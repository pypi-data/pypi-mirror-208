"""Contains the implementation of the job client."""

import json
import os
import signal
import sys
import threading
from enum import Enum
from types import FrameType, TracebackType
from typing import Any, Callable, Optional

import grpc
import spm_pb2
from spm_pb2 import RefreshRequest, Token
from spm_pb2_grpc import SPMStub, TokenManagerStub

from numerous.sdk.connect.auth import AccessTokenAuthMetadataPlugin
from numerous.sdk.connect.command_handler import CommandHandler
from numerous.sdk.connect.config import Config
from numerous.sdk.connect.file_manager import FileManager
from numerous.sdk.connect.job_state import JobState
from numerous.sdk.connect.job_utils import JobIdentifier
from numerous.sdk.connect.reader import Reader
from numerous.sdk.connect.subscription import Subscription
from numerous.sdk.connect.writer import Writer
from numerous.sdk.models.scenario import Scenario
from numerous.sdk.models.time_setup import TimeSetup


class JobStatus(str, Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    FINISHED = "finished"
    ERROR = "error"
    FAILED = "failed"


def _clamp(value: float, minimum: float, maximum: float):
    """Clamps the given value, between the given minimum and maximum values.

    :param minimum: The result will never be lower than the minimum.
    :param maximum: The result will never be higher than the maximum.
    """
    return min(max(minimum, value), maximum)


class JobClient:
    """The JobClient is the recommended way to connect to the numerous platform."""

    def __init__(
        self,
        channel: grpc.Channel,
        identity: JobIdentifier,
        execution_id: str,
        config: Optional[Config] = None,
    ):
        """Initialize the job client with a gRPC channel. The channel must be
        configured with credentials.

        :param channel: A gRPC channel configured with required authorization.
        :param identity: Contains identity information for the job object and related objects.
        """
        self._config = Config() if config is None else config
        self._channel = channel
        self._spm_client = SPMStub(self._channel)
        self._identity = identity
        self._execution_id = execution_id
        self._file_manager = FileManager(
            self._spm_client, self._identity.project_id, self._identity.scenario_id
        )
        self._status: JobStatus = JobStatus.INITIALIZING
        self._progress: float = 0.0
        self._message: str = ""
        self._job_state: Optional[JobState] = None
        self._scenario_document: Optional[dict[str, Any]] = None
        self._reader: Optional[Reader] = None
        self._writer: Optional[Writer] = None
        self._terminate_callback: Optional[Callable] = None
        self._setup_sigterm_handling()
        self._command_handler = self._create_command_handler()

    def _setup_sigterm_handling(self):
        def _sigterm_handler(signalnum: int, frame: Optional[FrameType]):  # noqa: F841
            if self._terminate_callback:
                thread = threading.Thread(target=self._terminate_callback, daemon=True)
                thread.start()
                thread.join(timeout=self._config.terminate_handler_timeout)
            sys.exit(1)

        signal.signal(signal.SIGTERM, _sigterm_handler)

    def _create_command_handler(self) -> CommandHandler:
        subscription = Subscription(
            self._identity.project_id,
            self._identity.scenario_id,
            self._spm_client,
            ".".join(
                (
                    "COMMAND",
                    self._identity.project_id,
                    self._identity.scenario_id,
                    self._identity.job_id,
                )
            ),
        )
        return CommandHandler(subscription)

    def __enter__(self) -> "JobClient":
        """Return itself upon entering the context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],  # noqa: F841
        exc_value: Optional[BaseException],  # noqa: F841
        traceback: Optional[TracebackType],  # noqa: F841
    ) -> Optional[bool]:
        """Closes the gRPC channel upon exiting the context manager."""
        self.close()
        return None

    @staticmethod
    def channel_options(config: Config) -> list[tuple[str, Any]]:
        """Returns the default gRPC channel options."""
        return [
            ("grpc.max_message_length", config.grpc_max_message_size),
            ("grpc.max_send_message_length", config.grpc_max_message_size),
            ("grpc.max_receive_message_length", config.grpc_max_message_size),
        ]

    @staticmethod
    def create(
        hostname: str,
        port: str,
        refresh_token: str,
        identity: JobIdentifier,
        execution_id: str,
        config: Config,
    ) -> "JobClient":
        """Create a JobClient from connection parameters.

        :param hostname: Hostname of the numerous server
        :param port: gRPC port of the numerous server
        :param refresh_token: Refresh token for the execution.
        :param identity: Contains identity information for the job object and related objects.
        """
        with grpc.secure_channel(
            f"{hostname}:{port}",
            grpc.ssl_channel_credentials(),
            JobClient.channel_options(config),
        ) as unauthorized_channel:
            token_manager = TokenManagerStub(unauthorized_channel)
            access_token = token_manager.GetAccessToken(
                RefreshRequest(refresh_token=Token(val=refresh_token))
            )

        authorized_channel = grpc.secure_channel(
            f"{hostname}:{port}",
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(),
                grpc.metadata_call_credentials(
                    AccessTokenAuthMetadataPlugin(access_token.val)
                ),
            ),
            JobClient.channel_options(config),
        )

        return JobClient(authorized_channel, identity, execution_id, config)

    @staticmethod
    def from_environment() -> "JobClient":
        """Create a JobClient from environment variables.

        Uses the following environment variables:
         - `NUMEROUS_API_SERVER`
         - `NUMEROUS_API_PORT`
         - `NUMEROUS_API_REFRESH_TOKEN`
         - `NUMEROUS_PROJECT`
         - `NUMEROUS_SCENARIO`
         - `JOB_ID`
         - `NUMEROUS_EXECUTION_ID`
        """
        return JobClient.create(
            os.environ["NUMEROUS_API_SERVER"],
            os.environ["NUMEROUS_API_PORT"],
            os.environ["NUMEROUS_API_REFRESH_TOKEN"],
            JobIdentifier(
                os.environ["NUMEROUS_PROJECT"],
                os.environ["NUMEROUS_SCENARIO"],
                os.environ["JOB_ID"],
            ),
            os.environ["NUMEROUS_EXECUTION_ID"],
            config=Config.from_environment(),
        )

    @staticmethod
    def from_legacy_client(client: Any) -> "JobClient":
        """Create a JobClient from a legacy :class:`~numerous.client.numerous_client.NumerousClient`.

        Reuses the channel of the legacy client, and connects to the same job.
        """
        from numerous.client import NumerousClient

        if not isinstance(client, NumerousClient):
            raise TypeError(
                f"'client' argument must be of type NumerousClient, was {type(client).__name__}"
            )
        else:
            return JobClient(
                client.channel,
                JobIdentifier(client._project, client._scenario, client._job_id),
                client._execution_id,
                Config.from_environment(),
            )

    def close(self) -> None:
        """Close the JobClient.

        Closes the JobClient's connection to the numerous platform, immediately
        terminating any active communication.

        This method is idempotent.
        """
        self._channel.close()

    @property
    def file_manager(self) -> FileManager:
        """Access the file manager of the job."""
        return self._file_manager

    @property
    def state(self) -> JobState:
        """The job state, which can be persisted across hibernations.

        It is a lazy property, that will load any remote state on access.
        """
        if self._job_state is None:
            self._job_state = JobState(
                self._spm_client, self._identity, self._execution_id
            )
        return self._job_state

    @property
    def scenario(self) -> Scenario:
        """The associated :class:`Scenario` configuration, with jobs, components,
        parameters and input variables.

        It is a lazy property, that will load the scenario data on access.
        """
        return Scenario.from_document(self._get_scenario_document())

    @property
    def time_setup(self) -> TimeSetup:
        """The associated time setup of the job, which contains start and end times
        of the simulation, and the duration.
        """
        return TimeSetup.from_document(
            self._get_scenario_document()["jobs"][self._identity.job_id]
        )

    def _get_scenario_document(self) -> dict[str, Any]:
        if self._scenario_document is None:
            response = self._spm_client.GetScenario(
                spm_pb2.Scenario(
                    project=self._identity.project_id,
                    scenario=self._identity.scenario_id,
                )
            )
            self._scenario_document = json.loads(response.scenario_document)
        return self._scenario_document

    @property
    def status(self) -> JobStatus:
        """Status of the job, reported to the platform.

        Getting the status returns a locally cached value.
        """
        return self._status

    @status.setter
    def status(self, value: JobStatus) -> None:
        self._status = value
        self._set_scenario_progress()

    @property
    def message(self) -> str:
        """Status message of the job, reported to the platform. Is truncated to at most 32 characters upon setting.

        Getting the status message returns a locally cached value.
        """
        return self._message

    @message.setter
    def message(self, value: str):
        self._message = value[: self._config.max_status_message_length]
        self._set_scenario_progress()

    @property
    def progress(self) -> float:
        """Progress of the job, reported to the platform. Is clamped between 0.0 and 100.0 upon setting.

        Getting the progress returns a locally cached value.
        """
        return self._progress

    @progress.setter
    def progress(self, value: float):
        self._progress = _clamp(value, 0.0, 100.0)
        self._set_scenario_progress()

    def _set_scenario_progress(self):
        self._spm_client.SetScenarioProgress(
            spm_pb2.ScenarioProgress(
                project=self._identity.project_id,
                scenario=self._identity.scenario_id,
                job_id=self._identity.job_id,
                status=self._status.value,
                progress=self._progress,
                message=self._message,
            )
        )

    @property
    def reader(self) -> Reader:
        """Data reader for the job."""
        if self._reader is None:
            self._reader = Reader(
                self._spm_client,
                self._identity,
                self._execution_id,
            )
        return self._reader

    @property
    def writer(self) -> Writer:
        """Data writer for the job."""
        if self._writer is None:
            self._writer = Writer(
                self._spm_client,
                self._identity,
                self._execution_id,
                self._config.grpc_max_message_size,
                flush_margin_bytes=self._config.grpc_max_message_size // 8,
            )
        return self._writer

    def set_terminate_callback(self, callback: Callable) -> None:
        self._terminate_callback = callback
