import json
import logging
import logging.handlers
import math
import os
import signal
import threading
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from itertools import islice
from queue import Queue
from time import sleep, time
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid4

import grpc
import health_pb2_grpc
import requests
import spm_pb2
import spm_pb2_grpc
from numerous.client_common.grpc_retry import grpc_retry_stream, grpc_retry_unary
from numerous.client_common.request_response_stream import RequestResponseStream

from . import config
from .common import (
    JobStatus,
    RepeatedFunction,
    RestorableIterator,
    initialize_grpc_channel,
    log,
    parse_api_url,
)
from .data_source import (
    DataSourceCompleted,
    DataSourceEmptyDataset,
    DataSourceHibernating,
    DataSourceStreamStarting,
    DynamicSource,
    InputManager,
    StaticSource,
)
from .numerous_buffered_writer import NumerousBufferedWriter
from .numerous_log_handler import NumerousLogHandler
from .optimization.configuration import OptimizationConfiguration, ScenarioSetting

try:
    import pandas as pd
except ModuleNotFoundError:
    pass


retry = grpc_retry_unary(
    max_attempts=config.GRPC_RETRY_ATTEMPTS, start_delay=config.GRPC_RETRY_DELAY
)
retry_stream = grpc_retry_stream(
    max_attempts=config.GRPC_RETRY_ATTEMPTS, start_delay=config.GRPC_RETRY_DELAY
)


def to_indexed_data_list(
    data_gen: Iterable[spm_pb2.DataList],
) -> Iterator[spm_pb2.IndexedDataList]:
    writer_id = str(uuid4())
    for i, item in enumerate(data_gen):
        yield spm_pb2.IndexedDataList(id=i, data_list=item, writer_id=writer_id)


class ScenarioStatus(str, Enum):
    FINISHED = "finished"
    FAILED = "failed"
    WAITING = "Waiting"
    REQUESTED = "requested"
    RUNNING = "running"
    INITIALZING = "initializing"
    MODEL_INITIALIZING = "Model Initializing"
    ENVIRONMENT_INITIALIZING = "Environment Initializing"
    EQUATIONS_ASSEMBLY = "Equations Assembly"
    HIBERNATING = "hibernating"


class ScenarioState:
    def __init__(
        self,
        spm_stub: spm_pb2_grpc.SPMStub,
        project_id: str,
        scenario_id: str,
        execution_id: str,
    ):
        self.spm_stub = spm_stub
        self.scenario_id = scenario_id
        self.project_id = project_id
        self.execution_id = execution_id
        self._state: Dict[str, Any] = self._get_scenario_custom_metadata(
            project_id, scenario_id, execution_id
        )

    @retry
    def _get_scenario_custom_metadata(
        self, project_id: str, scenario_id: str, execution_id: str
    ):
        request = spm_pb2.ScenarioCustomMetaData(
            scenario=scenario_id,
            project=project_id,
            execution=execution_id,
            key="state",
        )
        return json.loads(self.spm_stub.GetScenarioCustomMetaData(request).meta)

    def set(
        self, key_or_state: Union[str, Dict[str, Any]], value: Optional[Any] = None
    ) -> None:
        if isinstance(key_or_state, str):
            self._state[key_or_state] = value
        else:
            for key in key_or_state:
                self._state[key] = key_or_state[key]

    def unset(self, key: str) -> None:
        if key in self._state:
            del self._state[key]

    def get(self, key: str, default: Any) -> Any:
        return self._state.get(key, default)

    @retry
    def commit(self) -> None:
        scenario_custom_metadata = spm_pb2.ScenarioCustomMetaData(
            scenario=self.scenario_id,
            project=self.project_id,
            execution=self.execution_id,
            key="state",
            meta=json.dumps(self._state),
        )
        self.spm_stub.SetScenarioCustomMetaData(scenario_custom_metadata)


class JobParameters:
    def __init__(
        self,
        spm_stub: spm_pb2_grpc.SPMStub,
        project_id: str,
        scenario_id: str,
        job_id: str,
    ):
        scenario_data = spm_stub.GetScenario(
            spm_pb2.Scenario(project=project_id, scenario=scenario_id)
        )
        job_info = json.loads(scenario_data.scenario_document)["jobs"][job_id]
        self._params: Dict[str, Any] = {}
        for param in job_info["image"].get("parameters", {}):
            self._params[param["id"]] = param["value"]

    def get(self, key: str, default: Any):
        return self._params.get(key, default)


class RunSettings:
    def __init__(
        self,
        spm_stub: spm_pb2_grpc.SPMStub,
        project_id: str,
        scenario_id: str,
        job_id: str,
    ):
        scenario_data = spm_stub.GetScenario(
            spm_pb2.Scenario(project=project_id, scenario=scenario_id)
        )
        job_info = json.loads(scenario_data.scenario_document)["jobs"][job_id]
        self.start = datetime.fromisoformat(job_info["runSettings"]["startDate"])
        self.end = datetime.fromisoformat(job_info["runSettings"]["endDate"])
        self.duration = self.end - self.start


class DataSourcesReader:
    def __init__(
        self,
        client,
        scenario_data: Dict,
        start_time: float,
        t0: float,
        te: float,
        dt: float,
        tag_prefix: str,
        tag_separator: str,
        timeout: float,
    ):
        self._client = client
        self._inputs_params = {
            "scenario_data": scenario_data,
            "t0": t0,
            "te": te,
            "dt": dt,
            "tag_prefix": tag_prefix,
            "tag_separator": tag_separator,
            "timeout": timeout,
        }
        self._reader: InputManager = self._client.get_inputs(**self._inputs_params)
        self._t0 = t0
        self._start_time = start_time
        self._retry_delay: float = 1.0
        self._retry_timeout: float = 10.0
        self._stream_starting_timeout: float = 120

    def read(self, t: float):
        empty_since = None
        stream_starting_since = None
        data = None
        while data is None:
            try:
                if (
                    self._client.hibernate_event.is_set()
                    or self._client.terminate_event.is_set()
                ):
                    log.debug("Hibernate event or terminate event is set")
                    return None

                data = self._reader.get_at_time(t)
                if data is None:
                    sleep(self._retry_delay)
                    continue
                return data
            except DataSourceHibernating:
                log.debug(
                    "Data source hibernating, t0 = %f, start_time = %f",
                    self._t0,
                    self._start_time,
                )
                if self._t0 > self._start_time:
                    self._reader = self._client.get_inputs(**self._inputs_params)
                    sleep(self._retry_delay)
                    continue
                else:
                    self._client.hibernate()
                    return None
            except DataSourceCompleted:
                log.debug("Data source completed")
                return None
            except DataSourceEmptyDataset:
                if empty_since is None:
                    empty_since = time()
                empty_duration = time() - empty_since
                if empty_duration > self._retry_timeout:
                    log.warning("Empty dataset for %s. Stopping", empty_duration)
                    return None
                self._reader = self._client.get_inputs(**self._inputs_params)
                sleep(self._retry_delay)
            except DataSourceStreamStarting:
                if stream_starting_since is None:
                    stream_starting_since = time()
                stream_starting_duration = time() - stream_starting_since
                if stream_starting_duration > self._stream_starting_timeout:
                    log.warning("Stream not started after %s", stream_starting_duration)
                    return None
                sleep(self._retry_delay)
        return None

    def set_retry_delay(self, value: float):
        self._retry_delay = value

    def set_retry_timeout(self, value: float):
        self._retry_timeout = value


class DataStreamTimeoutBreakStatus(Exception):
    def __init__(self, break_status):
        super(DataStreamTimeoutBreakStatus, self).__init__()
        self.break_status = break_status


class NumerousClient:
    _execution_id: str

    def __init__(
        self,
        job_id: Optional[str] = None,
        project: Optional[str] = None,
        scenario: Optional[str] = None,
        server: Optional[str] = None,
        port: Optional[int] = None,
        refresh_token: Optional[str] = None,
        clear_data: Optional[bool] = None,
        no_log: bool = False,
        instance_id: Optional[str] = None,
        secure: Optional[bool] = None,
        url: Optional[str] = None,
        log_level: Union[str, int] = logging.ERROR,
        execution_id: Optional[str] = None,
    ):
        if url:
            server, port, secure = parse_api_url(url)
        self._t = [0]
        self.job_states = JobStatus

        if project is None:
            project = config.NUMEROUS_PROJECT
        if project is None:
            raise TypeError("Missing project id.")
        self._project = project

        if scenario is None:
            scenario = config.NUMEROUS_SCENARIO
        if scenario is None:
            raise TypeError("Missing scenario id.")
        self._scenario = scenario

        if job_id is None:
            job_id = config.JOB_ID
        if job_id is None:
            raise TypeError("Missing job id.")
        self._job_id = job_id

        self._refresh_token = refresh_token or config.NUMEROUS_API_REFRESH_TOKEN
        if self._refresh_token is None:
            raise TypeError("Missing refresh token.")

        execution_id = execution_id or config.NUMEROUS_EXECUTION_ID
        if execution_id is None:
            raise TypeError("Missing execution id")
        self._execution_id = execution_id  # linters workaround

        self._access_token = None
        self._instance_id = instance_id or str(uuid4())
        self._complete = True
        self._hibernating = False
        self._error = False
        self.terminate_event = threading.Event()
        self.hibernate_event = threading.Event()
        self.writers: List[NumerousBufferedWriter] = []

        self._state: Optional[ScenarioState] = None  # Used by state property
        self._params: Optional[JobParameters] = None  # Used by params property
        self._writer: Optional[NumerousBufferedWriter] = None  # Used by writer property
        self._run_settings: Optional[
            RunSettings
        ] = None  # Used by run_settings property
        self._optimization_config: Optional[
            OptimizationConfiguration
        ] = None  # Used by optimization_config property

        self.channel, self._instance_id = initialize_grpc_channel(
            server=server,
            port=port,
            secure=secure,
            instance_id=self._instance_id,
            token_callback=self._get_current_token,
            refresh_token=self._refresh_token,
        )
        self._base_client = spm_pb2_grpc.SPMStub(self.channel)
        self._token_manager = spm_pb2_grpc.TokenManagerStub(self.channel)
        self._health = health_pb2_grpc.HealthStub(self.channel)
        self._job_manager = spm_pb2_grpc.JobManagerStub(self.channel)
        self._file_manager = spm_pb2_grpc.FileManagerStub(self.channel)

        self._cancel_streams: List[Callable[[], None]] = []

        # Refresh token every 9 minutes (?)
        self._access_token_refresher = RepeatedFunction(
            interval=9 * 60,
            function=self._refresh_access_token,
            run_initially=True,
            refresh_token=self._refresh_token,
            instance_id=self._instance_id,
            execution_id=self._execution_id,
            project_id=self._project,
            scenario_id=self._scenario,
            job_id=self._job_id,
        )
        self._access_token_refresher.start()

        self._terminated = False
        if not no_log:
            self._init_logger(log_level)

        self.last_progress: float = float("-inf")
        self.progress_debounce = 10

        self.last_state_set: float = float("-inf")
        self.state_debounce = 60

        clear_data = (
            clear_data if clear_data is not None else config.NUMEROUS_CLEAR_DATA
        )

        # If clearing data, the job was not resumed and vice versa
        self._was_resumed = not clear_data

        self._hibernate_callback = self._default_hibernation_callback
        self._hibernate_callback_args: Tuple[Tuple[Any, ...], Dict[str, Any]] = ((), {})

        if clear_data:
            self.clear_timeseries_data()

        self._listen = threading.Thread(target=self._command_listener)
        self._listen.start()

    @property
    def state(self) -> ScenarioState:
        if self._state is None:
            self._state = ScenarioState(
                self._base_client, self._project, self._scenario, self._execution_id
            )
        return self._state

    @property
    def params(self) -> JobParameters:
        if self._params is None:
            self._params = JobParameters(
                self._base_client, self._project, self._scenario, self._job_id
            )
        return self._params

    @property
    def writer(self) -> NumerousBufferedWriter:
        if self._writer is None:
            self._writer = self.new_writer(buffer_size=0)
        return self._writer

    @property
    def run_settings(self) -> RunSettings:
        if self._run_settings is None:
            self._run_settings = RunSettings(
                self._base_client, self._project, self._scenario, self._job_id
            )
        return self._run_settings

    @property
    def optimization_config(self) -> OptimizationConfiguration:
        if self._optimization_config is None:
            self._optimization_config = OptimizationConfiguration(
                self._base_client, self._project, self._scenario
            )
        return self._optimization_config

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.close()

    def noop(self):
        self._base_client.Noop(
            spm_pb2.NoopContent(scenario=self._scenario, content="nothing")
        )

    @retry
    def get_execution_state(self, execution_id):
        return self._job_manager.GetExecutionState(
            spm_pb2.ExecutionStateMessage(
                project_id=self._project, execution_id=execution_id
            )
        )

    def complete_execution(self):
        log.debug(
            "Completing job %s with execution %s. Hibernating: %s",
            self._job_id,
            self._execution_id,
            self._hibernating,
        )
        if not self._hibernating:
            log.debug("Triggering non-main jobs")
            self.publish_message(
                {
                    "event": "trigger_non_main",
                    "project": self._project,
                    "scenario": self._scenario,
                    "job": self._job_id,
                }
            )

        execution = spm_pb2.ExecutionMessage(
            project_id=self._project,
            scenario_id=self._scenario,
            job_id=self._job_id,
            execution_id=self._execution_id,
        )
        self._base_client.CompleteExecution(
            spm_pb2.CompleteExecutionMessage(
                execution=execution, hibernate=self._hibernating
            )
        )

    def _get_current_token(self):
        return self._access_token

    def _init_logger(self, log_level):
        log_queue: Queue = Queue(-1)
        numerous_logger = logging.handlers.QueueHandler(queue=log_queue)
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(numerous_logger)
        self.log_handler = NumerousLogHandler(self)
        self.log_listener = logging.handlers.QueueListener(log_queue, self.log_handler)  # type: ignore[arg-type]
        self.log_listener.start()
        self.logger = logger

    @retry
    def _refresh_access_token(
        self,
        refresh_token,
        instance_id,
        execution_id,
        project_id=None,
        scenario_id=None,
        job_id=None,
    ):
        refresh_request = spm_pb2.RefreshRequest(
            refresh_token=spm_pb2.Token(val=refresh_token),
            instance_id=instance_id,
            execution_id=execution_id,
            project_id=project_id,
            scenario_id=scenario_id,
            job_id=job_id,
        )
        token = self._token_manager.GetAccessToken(refresh_request)
        self._access_token = token.val

    def _command_listener(self):
        command_channel = ".".join(
            ["COMMAND", self._project, self._scenario, self._job_id]
        )
        for channel, message in self.subscribe_messages([command_channel]):
            log.debug("Channel %s received message: %s", channel, message)
            if "command" not in message:
                continue

            command = message["command"]
            if command == "terminate":
                log.warning("Received Termination Command")
                signal.raise_signal(signal.SIGTERM)
                self.terminate_event.set()
                break
            elif command == "hibernate":
                self.hibernate(message="Hibernating")
                break

    @retry
    def get_scenario_document(
        self, scenario: Optional[str] = None, project: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Iterable[spm_pb2.FileSignedUrl]]:
        if scenario is None:
            scenario = self._scenario
        if project is None:
            project = self._project

        scenario_data = self._base_client.GetScenario(
            spm_pb2.Scenario(project=project, scenario=scenario)
        )
        return json.loads(scenario_data.scenario_document), scenario_data.files

    def get_job(self, scenario_doc=None):
        if scenario_doc is None:
            scenario_doc, files = self.get_scenario_document()

        return scenario_doc["jobs"][self._job_id]

    @retry
    def get_group_document(self, group):
        group_data = self._base_client.GetGroup(
            spm_pb2.Group(project=self._project, group=group)
        )

        return json.loads(group_data.group_document)

    @retry
    def get_project_document(self):
        proj_data = self._base_client.GetProject(spm_pb2.Project(project=self._project))

        return json.loads(proj_data.project_document)

    def listen_scenario_document(self, scenario=None, project=None):
        if scenario is None:
            scenario = self._scenario
        if project is None:
            project = self._project

        for doc in self._base_client.ListenScenario(
            spm_pb2.Scenario(project=project, scenario=scenario)
        ):
            json_doc = doc.scenario_document

            yield json.loads(json_doc), doc.files

    def get_scenario(self, scenario=None, project=None, path="."):
        os.makedirs(path, exist_ok=True)

        log.debug("Get scenario")
        if scenario is None:
            scenario = self._scenario
        if project is None:
            project = self._project

        scenario_data, scenario_files = self.get_scenario_document(scenario, project)

        scenario_files = [
            {"name": f.name, "url": f.url, "path": f.path} for f in scenario_files
        ]

        model_data, model_files = self.get_model(
            scenario_data["systemID"], project_id=project, scenario_id=scenario
        )

        model_files = [
            {"name": f.name, "url": f.url, "path": f.path} for f in model_files
        ]

        file_paths_local = {}
        for f in scenario_files + model_files:
            f_path = path + "/" + f["name"]
            file_paths_local[f["name"]] = f_path
            r = requests.get(f["url"], allow_redirects=True)
            open(f_path, "wb").write(r.content)

        return scenario_data, model_data, file_paths_local

    @retry
    def get_model(self, model_id, project_id=None, scenario_id=None):
        if project_id is None:
            project_id = self._project

        model = self._base_client.GetModel(
            spm_pb2.Model(
                model_id=model_id, project_id=project_id, scenario_id=scenario_id
            )
        )

        return json.loads(model.model), model.files

    @retry
    def set_scenario_progress(
        self,
        message,
        status: ScenarioStatus,
        progress=None,
        clean=False,
        scenario=None,
        force=False,
        project=None,
        job=None,
    ):
        if status == ScenarioStatus.FAILED:
            self._error = True

        if scenario is None:
            scenario = self._scenario
        if project is None:
            project = self._project
        if job is None:
            job = self._job_id

        tic = time()
        if tic > (self.last_progress + self.progress_debounce) or force:
            self.last_progress = tic
            self._base_client.SetScenarioProgress(
                spm_pb2.ScenarioProgress(
                    project=project,
                    scenario=scenario,
                    job_id=job,
                    message=message,
                    status=status,
                    clean=clean,
                    progress=progress,
                )
            )

    def clear_scenario_results(self, scenario=None):
        if scenario is None:
            scenario = self._scenario

        self._base_client.ClearScenarioResults(
            spm_pb2.Scenario(project=self._project, scenario=scenario)
        )

    def set_scenario_results(
        self, names: list, values: list, units: list, scenario=None
    ):
        if scenario is None:
            scenario = self._scenario

        self._base_client.SetScenarioResults(
            spm_pb2.ScenarioResults(
                project=self._project,
                scenario=scenario,
                names=names,
                values=values,
                units=units,
            )
        )

    @retry
    def get_scenario_results(self, scenario=None):
        if scenario is None:
            scenario = self._scenario

        results = self._base_client.GetScenarioResults(
            spm_pb2.Scenario(project=self._project, scenario=scenario)
        )

        return results.names, results.values, results.units

    @retry
    def get_scenario_results_document(self, scenario=None, execution=None):
        if scenario is None:
            scenario = self._scenario

        results = self._base_client.GetScenarioResultDocument(
            spm_pb2.Scenario(
                project=self._project, scenario=scenario, execution=execution
            )
        )

        return json.loads(results.result)

    def set_scenario_results_document(
        self, results_dict, scenario=None, execution=None
    ):
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id

        self._base_client.SetScenarioResultDocument(
            spm_pb2.ScenarioResultsDocument(
                project=self._project,
                scenario=scenario,
                execution=execution,
                result=json.dumps(results_dict),
            )
        )

    def push_scenario_error(self, error, scenario=None):
        if scenario is None:
            scenario = self._scenario

        self._base_client.PushScenarioError(
            spm_pb2.ScenarioError(
                project=self._project,
                scenario=scenario,
                error=error,
                spm_job_id=self._job_id,
            )
        )

    @retry
    def push_scenario_logs(self, logs: List[Tuple[datetime, str]]):
        timestamps = [log_time.timestamp() for log_time, _ in logs]
        self._base_client.PushExecutionLogEntries(
            spm_pb2.LogEntries(
                scenario=self._scenario,
                project_id=self._project,
                execution_id=self._execution_id,
                log_entries=[entry for _, entry in logs],
                timestamps=timestamps,
            )
        )

    def get_download_files(
        self,
        files: list[str],
        local_path: str = "./tmp",
        scenario: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        os.makedirs(local_path, exist_ok=True)
        if scenario is None:
            scenario = self._scenario
        if project_id is None:
            project_id = self._project

        signed_urls = self._base_client.GetSignedURLs(
            spm_pb2.FilePaths(
                file_paths=[spm_pb2.FilePath(path=f"{scenario}/{fn}") for fn in files],
                scenario=scenario,
                project_id=project_id,
            )
        )

        files_out = {}
        for f in signed_urls.files:
            r = requests.get(f.url, allow_redirects=True)
            local_file_path = local_path + "/" + f.name
            open(local_file_path, "wb").write(r.content)
            files_out[f.name] = local_file_path
        return files_out

    def upload_file(
        self, local_file, file_id, file=None, scenario=None, content_type="text/html"
    ):
        if scenario is None:
            scenario = self._scenario
        if file is None:
            file = local_file.split("/")[-1]
        scenario_file_path = spm_pb2.ScenarioFilePath(
            project=self._project,
            scenario=scenario,
            path=file,
            file_id=file_id,
            content_type=content_type,
        )
        upload_url = self._base_client.GenerateScenarioUploadSignedURL(
            scenario_file_path
        )
        requests.post(
            upload_url.url,
            headers={"Content-Type": "multipart/related"},
            params={"name": file, "mimeType": content_type},
            data=open(local_file, "rb"),
        )

    def upload_file_path(self, remote_path: str, local_path: str):
        upload_urls = self._file_manager.GetUploadUrls(
            spm_pb2.FilePaths(project_id=self._project, paths=[remote_path])
        )

        # Validate url
        url = None
        for upload_url in upload_urls.urls:
            if upload_url.path == remote_path:
                url = upload_url.url

        if not url:
            raise RuntimeError(f"Could not upload to the remote path {remote_path}")

        with open(local_path, "rb") as upload_file:
            requests.post(
                url, headers={"Content-Type": "multipart/related"}, data=upload_file
            )

    def download_file_path(
        self, remote_path: str, local_path: str, overwrite: bool = False
    ) -> None:
        self.download_file_paths({remote_path: local_path}, overwrite)

    def download_file_paths(
        self, path_mapping: Mapping[str, str], overwrite: bool = False
    ) -> None:
        download_urls = self._file_manager.GetDownloadUrls(
            spm_pb2.FilePaths(project_id=self._project, paths=list(path_mapping))
        )

        for local_path in path_mapping.values():
            if not overwrite and os.path.exists(local_path):
                raise OSError(f"Cannot download onto existing file {local_path}")

        for download_url in download_urls.urls:
            if not download_url.url:
                raise RuntimeError(f"Could not download file at {download_url.path}")

        for download_url in download_urls.urls:
            url = download_url.url
            local_path = path_mapping[download_url.path]
            with requests.get(url, allow_redirects=True, stream=True) as response, open(
                local_path, "wb"
            ) as file:
                for chunk in response.iter_content(chunk_size=2**16):
                    file.write(chunk)

    @retry
    def get_timeseries_stats(
        self, project=None, scenario=None, execution=None, tag="_index"
    ):
        if project is None:
            project = self._project
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id
        log.debug("Get timeseries stats: tag=%s", tag)
        return self._base_client.GetScenarioDataStats(
            spm_pb2.ScenarioStatsRequest(
                project=project, scenario=scenario, execution=execution, tag=tag
            )
        )

    @retry
    def get_dataset_closed(self, project=None, scenario=None, execution=None):
        if project is None:
            project = self._project
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id

        return self._base_client.GetDataSetClosed(
            spm_pb2.Scenario(project=project, scenario=scenario, execution=execution)
        ).is_closed

    @retry
    def get_timeseries_meta_data(self, project=None, scenario=None, execution=None):
        if project is None:
            project = self._project
        if scenario is None:
            scenario = self._scenario

        return self._base_client.GetScenarioMetaData(
            spm_pb2.Scenario(project=project, scenario=scenario, execution=execution)
        )

    def set_timeseries_meta_data(
        self,
        tags: List[Dict[str, Any]],
        aliases: Optional[Dict[str, str]] = None,
        offset: int = 0,
        timezone: str = "UTC",
        epoch_type: str = "s",
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        project: Optional[str] = None,
    ):
        lifted_tags = [
            spm_pb2.Tag(
                name=tag["name"],
                displayName=tag.get("displayName", ""),
                unit=tag.get("unit", ""),
                description=tag.get("description", ""),
                type=tag.get("type", "double"),
                scaling=tag.get("scaling", 1),
                offset=tag.get("offset", 0),
            )
            for tag in tags
        ]
        lifted_aliases = (
            [spm_pb2.Alias(tag=k, aliases=v) for k, v in aliases.items()]
            if aliases is not None
            else []
        )
        if project is None:
            project = self._project
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id

        scenario_meta_data = spm_pb2.ScenarioMetaData(
            project=project,
            scenario=scenario,
            execution=execution,
            tags=lifted_tags,
            aliases=lifted_aliases,
            offset=offset,
            timezone=timezone,
            epoch_type=epoch_type,
        )
        return self._base_client.SetScenarioMetaData(scenario_meta_data)

    @retry
    def get_timeseries_custom_meta_data(
        self, scenario=None, project_id=None, execution=None, key=None
    ):
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id
        if project_id is None:
            project_id = self._project

        return self._base_client.GetScenarioCustomMetaData(
            spm_pb2.ScenarioCustomMetaData(
                scenario=scenario, project=project_id, execution=execution, key=key
            )
        ).meta

    def set_timeseries_custom_meta_data(
        self, meta: str, scenario=None, project_id=None, execution=None, key=None
    ):
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id
        if project_id is None:
            project_id = self._project
        scenario_custom_metadata = spm_pb2.ScenarioCustomMetaData(
            scenario=scenario,
            project=project_id,
            execution=execution,
            key=key,
            meta=meta,
        )
        return self._base_client.SetScenarioCustomMetaData(scenario_custom_metadata)

    def get_state(self, scenario=None, execution=None):
        try:
            state_json = self.get_timeseries_custom_meta_data(
                scenario=scenario, execution=execution, key="state"
            )
            return json.loads(state_json)
        except json.decoder.JSONDecodeError:
            return None

    def set_state(self, state, scenario=None, execution=None, force=False):
        tic = time()
        if tic > (self.last_state_set + self.state_debounce) or force:
            log.debug("State set.")
            self.last_state_set = tic
            return self.set_timeseries_custom_meta_data(
                meta=json.dumps(state),
                scenario=scenario,
                execution=execution,
                key="state",
            )

    def get_latest_main_execution(self, project=None, scenario=None):
        return self._base_client.GetLatestMainExecution(
            spm_pb2.Scenario(project=project, scenario=scenario)
        ).execution_id

    def open_data_stream(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        project: Optional[str] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        latest_execution: bool = False,
        subscribe: bool = False,
        index_by_time: bool = True,
    ):
        if tags is None:
            tags = []

        if project is None:
            project = self._project

        if scenario is None:
            scenario = self._scenario

        if latest_execution:
            execution = self.get_latest_main_execution(project, scenario)
        elif execution is None:
            execution = self._execution_id

        if isinstance(start, datetime):
            start = start.timestamp()
        if isinstance(end, datetime):
            end = end.timestamp()

        last_row = 0
        last_time = time()
        while True:
            row = last_row
            try:
                data_stream = self._base_client.ReadData(
                    spm_pb2.ReadScenario(
                        project=project,
                        scenario=scenario,
                        execution=execution,
                        tags=tags,
                        start=start,
                        end=end,
                        time_range=index_by_time,
                        listen=subscribe,
                    )
                )

                # TODO: Optimize reading restoration
                for data in islice(data_stream, last_row, None):
                    row += 1
                    last_time = time()
                    yield data
                break

            except grpc.RpcError as e:
                if time() - last_time >= config.GRPC_RETRY_TIMEOUT:
                    log.warning(
                        f"Exceeded read data stream retry timeout: {config.GRPC_RETRY_TIMEOUT}"
                    )
                    raise e
                last_row = row
                sleep(config.GRPC_RETRY_DELAY)

    def data_read_raw(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        project: Optional[str] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        index_by_time: bool = True,
    ):
        yield from self.open_data_stream(
            tags,
            start,
            end,
            project,
            scenario,
            execution,
            index_by_time=index_by_time,
        )

    def read_data(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        project: Optional[str] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        latest_execution: bool = False,
        subscribe: bool = False,
        index_by_time: bool = True,
    ):
        data_stream = self.open_data_stream(
            tags,
            start,
            end,
            project,
            scenario,
            execution,
            latest_execution,
            subscribe,
            index_by_time=index_by_time,
        )

        for data_list in data_stream:
            for data_block in data_list.data:
                yield data_block.tag, data_block.values

    def data_read_df(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        project: Optional[str] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        index_by_time: bool = True,
    ):
        data_generator = self.read_data(
            tags,
            start,
            end,
            project,
            scenario,
            execution,
            execution is None,
            index_by_time=index_by_time,
        )

        data = {}
        for tag, values in data_generator:
            if tag not in data:
                data[tag] = list(values)
            else:
                data[tag] += values

        if not data:
            return pd.DataFrame({})

        min_len = len(min(data.values(), key=len))
        return pd.DataFrame({k: v[:min_len] for k, v in data.items()})

    def read_data_stream(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        project: Optional[str] = None,
        index_by_time: bool = True,
    ):
        return self.read_data(
            tags, start, end, project, scenario, execution, index_by_time=index_by_time
        )

    def read_data_as_row(
        self,
        tags: Optional[List[str]] = None,
        start: Optional[Union[datetime, float]] = None,
        end: Optional[Union[datetime, float]] = None,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        project: Optional[str] = None,
        subscribe: bool = False,
        offset: int = 0,
        index_by_time: bool = True,
    ):
        data_stream = self.open_data_stream(
            tags,
            start,
            end,
            project,
            scenario,
            execution,
            subscribe=subscribe,
            index_by_time=index_by_time,
        )

        current_row = {}
        for b in data_stream:
            if b.stream_status == "HIBERNATE" or b.stream_status == "STOP":
                yield b.stream_status
                log.debug(f"stream is now status {b.stream_status}")
                return

            for d in b.data:
                if d.tag != "":
                    if d.tag not in current_row:
                        current_row[d.tag] = list(d.values)
                    else:
                        current_row[d.tag] += list(d.values)

            if b.row_complete or b.block_complete:
                len_index = len(current_row["_index"])

                wrong_len_tags = []
                for k in list(current_row.keys()):
                    if (len_cr := len(current_row[k])) != len_index:
                        wrong_len_tags.append((k, len_cr))

                if len(wrong_len_tags) > 0:
                    raise ValueError(
                        f"The following tags have a wrong number of data points returned (_index has {len_index}: "
                        + "\n".join(
                            [tag[0] + ": " + str(tag[1]) for tag in wrong_len_tags]
                        )
                    )

                for i in range(len_index):
                    r = {k: v[i] for k, v in current_row.items()}
                    r["_index"] += offset
                    yield r

                current_row = {}

        if len(list(current_row.keys())) > 0:
            for i, ix in enumerate(current_row["_index"]):
                r = {k: v[i] for k, v in current_row.items()}
                r["_index"] += offset
                yield r

        log.debug("Reading as row complete")

    def get_data_sources_reader(
        self,
        t0: float,
        te: float,
        scenario_data: Optional[Dict] = None,
        dt: float = 3600.0,
        tag_prefix: str = "Stub",
        tag_separator: str = ".",
        timeout: float = 10.0,
        start_time: Optional[float] = None,
    ) -> DataSourcesReader:
        if scenario_data is None:
            scenario_data, _ = self.get_scenario_document()
        if start_time is None:
            start_time = self.run_settings.start.timestamp()
        return DataSourcesReader(
            self,
            scenario_data,
            start_time,
            t0,
            te,
            dt,
            tag_prefix,
            tag_separator,
            timeout,
        )

    def clear_timeseries_data(self, scenario=None, execution=None):
        log.warning("Clearing data!")

        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id

        self._base_client.ClearData(
            spm_pb2.Scenario(scenario=scenario, execution=execution)
        )

    def data_write_df(self, df, scenario=None, execution=None, clear=True):
        if scenario is None:
            scenario = self._scenario
        if execution is None:
            execution = self._execution_id

        if clear:
            self.clear_timeseries_data(scenario=scenario, execution=execution)

        len_ix = len(df["_index"])
        i = 0
        data = []
        while i < len_ix:
            i_ = i + 10000
            data.append([{"tag": c, "values": df[c].values[i:i_]} for c in list(df)])
            i = i_

        def data_writer():
            size = 0
            b_size = len(df["_index"])

            blocks = []
            for r in data:
                for d in r:
                    size += b_size
                    blocks.append(spm_pb2.DataBlock(**d))
                    if size > 2e5:
                        yield spm_pb2.DataList(
                            scenario=scenario,
                            execution=execution,
                            data=blocks,
                            clear=False,
                            block_complete=False,
                            row_complete=False,
                        )
                        size = 0
                        blocks = []
                if size > 0:
                    yield spm_pb2.DataList(
                        scenario=scenario,
                        execution=execution,
                        data=blocks,
                        clear=False,
                        block_complete=True,
                        row_complete=False,
                    )

        self._base_client.WriteDataList(to_indexed_data_list(data_writer()))

    def _split(self, data, parts: int):
        """Keep numpy.array_split() logic."""
        length = len(data)

        size = length // parts + 1
        rest_start = (length % parts) * size
        for i in range(0, rest_start, size):
            yield data[i : i + size]

        size = length // parts
        if size:
            for i in range(rest_start, length, size):
                yield data[i : i + size]

    def _rows_to_blocks(self, rows) -> list[spm_pb2.DataBlock]:
        if len(rows) == 0:
            return []

        data = {k: [float(r[k]) for r in rows] for k in rows[0]}
        estimated_size = sum(len(json.dumps(value)) for value in data.values())
        maximum_block_size = 3.5e6  # allow some overhead
        estimated_chunks = int(math.ceil(estimated_size / maximum_block_size))
        blocks: list[spm_pb2.DataBlock] = [list() for _ in range(estimated_chunks)]

        # split data into chunks of equal size (except last chunk)
        for tag, values in data.items():
            for i, block_values in enumerate(self._split(values, estimated_chunks)):
                blocks[i].append(spm_pb2.DataBlock(tag=tag, values=block_values))

        return blocks

    def write_with_row_generator(
        self,
        data_generator,
        scenario: Optional[str] = None,
        clear=False,
        must_flush=None,
        execution=None,
    ):
        if must_flush is None:

            def must_flush(_n, _m):
                return True

        if scenario is None:
            scenario = self._scenario

        if execution is None:
            execution = self._execution_id

        def gen(clear):
            yield spm_pb2.DataList(
                scenario=scenario,
                execution=execution,
                data={},
                clear=clear,
                block_complete=False,
                row_complete=False,
            )
            rows = []
            for row in data_generator:
                if self.terminate_event.is_set():
                    break
                if row is not None:
                    rows.append(row)
                if len(rows) > 0 and must_flush(len(rows), len(row)):
                    blocks = self._rows_to_blocks(rows)
                    rows = []
                    for block in blocks:
                        yield spm_pb2.DataList(
                            scenario=scenario,
                            execution=execution,
                            data=block,
                            clear=clear,
                            block_complete=False,
                            row_complete=True,
                        )
                    clear = False

            # if len(rows)>0:
            blocks = self._rows_to_blocks(rows)

            for block in blocks:
                yield spm_pb2.DataList(
                    scenario=scenario,
                    execution=execution,
                    data=block,
                    clear=clear,
                    block_complete=True,
                    row_complete=True,
                )

        self._do_write_data_list(RestorableIterator(to_indexed_data_list(gen(clear))))

    @retry
    def _do_write_data_list(self, data: RestorableIterator):
        data.restore()
        for response in self._base_client.WriteDataList(data):
            # TODO: check response?
            data.item_handled()

    def new_writer(self, buffer_size=100, clear=False):
        if clear:
            self.clear_timeseries_data(self._scenario)

        _writer = NumerousBufferedWriter(
            self.write_with_row_generator,
            self.writer_closed,
            self._scenario,
            buffer_size,
        )
        self.writers.append(_writer)
        return _writer

    @retry
    def writer_closed(self, scenario):
        log.debug("Writer Closed")
        execution = self._execution_id
        self._base_client.CloseData(
            spm_pb2.DataCompleted(
                scenario=scenario,
                execution=execution,
                eta=-1,
                finalized=not self._hibernating,
            )
        )

    @contextmanager
    def open_writer(
        self,
        aliases: Optional[dict] = None,
        clear: bool = False,
        buffer_size: int = 24 * 7,
    ) -> Generator[NumerousBufferedWriter, None, None]:
        if clear:
            self.clear_timeseries_data(self._scenario)
        writer = NumerousBufferedWriter(
            self.write_with_row_generator,
            self.writer_closed,
            self._scenario,
            buffer_size,
        )
        self.writers.append(writer)
        try:
            yield writer
        finally:
            writer.close()

    def get_inputs(
        self,
        scenario_data: dict,
        t0: float = 0,
        te: float = 0,
        dt: float = 3600,
        tag_prefix="Stub",
        tag_separator: str = ".",
        timeout: int = 10,
    ):
        input_sources = {}
        static_data = {}
        input_source_types = {}
        only_static = True
        input_scenario_map_spec = {
            s["scenarioID"]: s for s in scenario_data["inputScenarios"]
        }

        # Mark subcomponents
        subcomponent_uuids = set()
        for component in scenario_data["simComponents"]:
            subcomponent_uuids.update(
                [c["uuid"] for c in component.get("subcomponents", ())]
            )
        for component in scenario_data["simComponents"]:
            component["isSubcomponent"] = component["uuid"] in subcomponent_uuids

        # Map input variables to datasources
        for component in scenario_data["simComponents"]:
            if (
                component["disabled"]
                or not component["isMainComponent"]
                and not component["isSubcomponent"]
            ):
                continue
            for inputVariable in component["inputVariables"]:
                tag = tag_separator.join(
                    filter(None, [tag_prefix, component["name"], inputVariable["id"]])
                )
                datasource_type = inputVariable["dataSourceType"]
                if datasource_type == "static":
                    static_data[tag] = inputVariable["value"]
                elif datasource_type in ["scenario", "control_machines"]:
                    datasource_id = inputVariable["dataSourceID"]
                    input_source_types[datasource_id] = datasource_type

                    only_static = False
                    if datasource_id not in input_sources:
                        input_sources[datasource_id] = input_scenario_map_spec[
                            datasource_id
                        ]
                        input_sources[datasource_id]["tags"] = {}
                    input_sources[datasource_id]["tags"][tag] = {
                        "tag": inputVariable["tagSource"]["tag"],
                        "scale": inputVariable["scaling"],
                        "offset": inputVariable["offset"],
                    }
                else:
                    raise ValueError(f"Unknown data source type: {datasource_type}")

        # First add the static source
        log.info("static only: %s", only_static)
        inputs: List[Union[StaticSource, DynamicSource]] = [
            StaticSource(static_data, t0=t0, dt=dt, generate_index=only_static)
        ]
        log.debug("input source types: %s", input_source_types)

        # Then add dynamic sources
        input_scenario_map = {
            s["scenarioID"]: s["executionID"] if "executionID" in s else None
            for s in scenario_data["inputScenarios"]
        }

        for input_source, spec in input_sources.items():
            log.debug(spec)
            log.debug(
                "Setting up input sources, scenario: %s, exe: %s",
                input_source,
                input_scenario_map[input_source],
            )
            inputs.append(
                DynamicSource(
                    client=self,
                    scenario=input_source,
                    execution=input_scenario_map[input_source],
                    spec=spec,
                    t0=t0,
                    te=te,
                    timeout=timeout,
                    source_type=input_source_types[input_source],
                )
            )

        return InputManager(inputs, self._t, t0)

    def publish_message(self, message, channel=None):
        if channel is None:
            channel = ".".join(["EVENT", self._project, self._scenario])
        self._base_client.PublishSubscriptionMessage(
            spm_pb2.SubscriptionMessage(channel=channel, message=json.dumps(message))
        )

    @retry_stream
    def subscribe_messages(self, channel_patterns):
        subscription = spm_pb2.Subscription(
            channel_patterns=channel_patterns,
            scenario=self._scenario,
            project_id=self._project,
        )
        message_generator = self._base_client.SubscribeForUpdates(subscription)
        self._cancel_streams.append(message_generator.cancel)
        try:
            for message in message_generator:
                yield message.channel, json.loads(message.message)
        except grpc._channel._MultiThreadedRendezvous:
            pass

    def start_iteration_scenario(
        self,
        target_scenario_id: str,
        target_job_id: str,
        override_settings: Iterable[ScenarioSetting],
    ):
        duplicate_request = spm_pb2.DuplicateScenarioRequest(
            scenario_id=target_scenario_id,
            project_id=self._project,
            execution_id=self._execution_id,
            create_child=True,
            override_settings=[
                spm_pb2.ScenarioSetting(
                    path=setting["path"], type=setting["type"], value=setting["value"]
                )
                for setting in override_settings
            ],
        )
        duplicated_scenario = self._base_client.DuplicateScenario(duplicate_request)
        start_request = spm_pb2.Job(
            project_id=duplicated_scenario.project,
            scenario_id=duplicated_scenario.scenario,
            job_id=target_job_id,
        )
        execution_id = self._job_manager.StartJob(start_request)
        return duplicated_scenario.scenario, execution_id.execution_id

    def set_optimization_iteration_score(
        self, iteration_scenario_id: str, score: float
    ):
        request = spm_pb2.SetOptimizationIterationScoreRequest(
            scenario_id=iteration_scenario_id, project_id=self._project, score=score
        )
        self._base_client.SetOptimizationIterationScore(request)

    def set_optimization_result(
        self, optimal_scenario_id: str, score: float, settings: List[ScenarioSetting]
    ):
        request = spm_pb2.SetOptimizationResultRequest(
            scenario_id=self._scenario,
            project_id=self._project,
            optimal_scenario_id=optimal_scenario_id,
            score=score,
            settings=[
                spm_pb2.ScenarioSetting(
                    path=s["path"], type=s["type"], value=s["value"]
                )
                for s in settings
            ],
        )
        self._base_client.SetOptimizationResult(request)

    def refresh_token(self, refresh_token):
        refreshed_token = self._token_manager.GetAccessToken(
            spm_pb2.Token(val=refresh_token)
        )
        return refreshed_token

    def was_resumed(self) -> bool:
        """Returns True if job was resumed and False otherwise"""
        return self._was_resumed

    @staticmethod
    def _default_hibernation_callback(*args, **kwargs) -> None:
        """Default function to be called when job is hibernated. Does it need functionality?"""
        print(
            f"Default Hibernation Callback with arguments. args: '{args}' kwargs: '{kwargs}'."
        )

    def set_hibernation_callback(self, func, *args, **kwargs) -> None:
        """
        Use this function to set a callback to be used when job is hibernated.
        :param func: function to be called
        """
        self._hibernate_callback = func
        self._hibernate_callback_args = (args, kwargs)

    def hibernate(self, message: str = "Hibernating") -> None:
        """
        Call this function to hibernate Client. This will enable client to reload its state
        after being restarted at a later point.
        """
        log.info("Client received hibernation signal.")
        self._hibernating = True
        self._complete = True
        self.set_scenario_progress(
            message=message, status=ScenarioStatus.HIBERNATING, force=True
        )
        self.hibernate_event.set()

    def close(self):
        log.debug("Client closing")
        # Close all writers
        for w in self.writers:
            w.close()

        # Close thread ofr refreshing token
        self._access_token_refresher.stop()

        # If job has been hibernated, call the set hibernate callback
        if self._hibernating:
            self._hibernate_callback(
                *self._hibernate_callback_args[0], **self._hibernate_callback_args[1]
            )

        if self._complete:
            if not self._hibernating:
                if not self._error:
                    self.set_scenario_progress(
                        message="Finished", status=ScenarioStatus.FINISHED, force=True
                    )
            self.complete_execution()

        if hasattr(self, "log_listener"):
            self.log_listener.stop()

        if hasattr(self, "log_handler"):
            self.log_handler.close()

        for cancel_func in self._cancel_streams:
            cancel_func()

        if self._state:
            self.state.commit()
        log.debug("Closing channel")
        self.channel.close()

    def set_data_stream_status(self, scenario, execution, status):
        self.set_timeseries_custom_meta_data(
            scenario=scenario,
            execution=execution,
            key="status",
            meta=json.dumps(status),
        )

    def get_data_stream_status(self, scenario, execution):
        return json.loads(
            self.get_timeseries_custom_meta_data(
                scenario=scenario, execution=execution, key="status"
            )
        )

    def open_write_data_stream(
        self,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
    ):
        if scenario is None:
            scenario = self._scenario

        if execution is None:
            execution = self._execution_id

        class _WriteDataStream(RequestResponseStream):
            def __init__(stream, client: NumerousClient):
                super(_WriteDataStream, stream).__init__(
                    client._base_client.WriteDataStream,
                )

            def write(
                stream,
                index: List[float],
                data: Dict[str, List[float]],
                overwrite: bool = False,
                update_stats: bool = False,
            ):
                response = stream.send(
                    spm_pb2.WriteDataStreamRequest(
                        scenario=scenario,
                        execution=execution,
                        overwrite=overwrite,
                        index=index,
                        data={
                            tag: spm_pb2.StreamData(values=values)
                            for tag, values in data.items()
                        },
                        update_stats=update_stats,
                    )
                )
                return response.index

        return _WriteDataStream(self)

    def open_read_data_stream(
        self,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
    ):
        if scenario is None:
            scenario = self._scenario

        if execution is None:
            execution = self._execution_id

        class _ReadDataStream(RequestResponseStream):
            def __init__(stream, client: NumerousClient):
                super(_ReadDataStream, stream).__init__(
                    client._base_client.ReadDataStream,
                )

            def read(
                stream,
                tags: List[str],
                start: Optional[float] = None,
                end: Optional[float] = None,
                length: Optional[int] = None,
                timeout_wait: float = 0.0,
                timeout_sleep_for: float = config.DATA_STREAM_DEFAULT_TIMEOUT_SLEEP_FOR,
                timeout_break_statuses: Optional[List[Any]] = None,
            ):
                deadline_time = time() + timeout_wait
                while True:
                    response = stream.send(
                        spm_pb2.ReadDataStreamRequest(
                            scenario=scenario,
                            execution=execution,
                            tags=tags,
                            start=start,
                            end=end,
                            length=length,
                        )
                    )

                    if response.index or time() >= deadline_time:
                        return response.index, {
                            tag: stream_data.values
                            for tag, stream_data in response.data.items()
                        }

                    if timeout_break_statuses:
                        status = self.get_data_stream_status(scenario, execution)
                        if status in timeout_break_statuses:
                            raise DataStreamTimeoutBreakStatus(status)

                    sleep(timeout_sleep_for)

        return _ReadDataStream(self)

    @dataclass
    class DataStreamStats:
        min: Optional[float]
        max: Optional[float]
        len: Optional[int]

    def get_data_stream_stats(
        self,
        scenario: Optional[str] = None,
        execution: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, DataStreamStats]:
        if scenario is None:
            scenario = self._scenario

        if execution is None:
            execution = self._execution_id

        request = spm_pb2.GetDataStreamStatsRequest(
            scenario=scenario, execution=execution, tags=tags
        )
        response: spm_pb2.GetDataStreamStatsResponse = (
            self._base_client.GetDataStreamStats(request)
        )
        return {
            tag: self.DataStreamStats(
                min=tag_stats.min, max=tag_stats.max, len=tag_stats.len
            )
            for tag, tag_stats in response.stats.items()
        }


@contextmanager
def open_client(
    job_id: Optional[str] = None,
    project: Optional[str] = None,
    scenario: Optional[str] = None,
    clear_data: Optional[bool] = None,
    no_log: bool = False,
    instance_id: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Generator[NumerousClient, None, None]:
    client = NumerousClient(
        job_id,
        project,
        scenario,
        clear_data=clear_data,
        no_log=no_log,
        instance_id=instance_id,
        refresh_token=refresh_token,
    )
    try:
        yield client
    except Exception as e:
        log.error(
            "Unhandled error occured in numerous client: %s\n%s",
            e,
            traceback.format_exc(),
        )
        client.push_scenario_error(error=traceback.format_exc())
        client.set_scenario_progress(
            f"Error: {type(e).__name__}", ScenarioStatus.FAILED, force=True
        )
    finally:
        log.info("Closing client")
        client.close()
