import datetime
import logging
import os
import signal
from importlib.metadata import version
from threading import Event, Thread
from time import sleep
from typing import Optional

from numerous.cli.client import get_client
from numerous.client import NumerousClient
from numerous.client.numerous_client import ScenarioStatus

from .errors import tb_str
from .job import ExitCode, NumerousBaseJob

VERSION = version("numerous.sdk")
APPVERSION = os.getenv("APPVERSION", "?")

local = os.getenv("KUBERNETES_SERVICE_HOST", "") == ""


class NumerousApp:
    def __init__(
        self,
        numerous_job: NumerousBaseJob,
        appname="defaultnumerousApp",
        max_restarts=0,
        model_folder: Optional[str] = None,
        working_folder: Optional[str] = None,
        reset_job: bool = False,
    ):
        log_level = os.getenv("LOG_LEVEL", logging.root.level)

        self.appname = appname

        self.backup = Event()
        self.terminate = Event()
        self.scenario = None
        self.model_definition = None
        self.files = None
        self.job_spec = None
        self.solver_settings = None
        self.sim_job = None
        self.subscribe = False
        self.solver_settings = None
        self.logger = None
        self.allow_hibernation = False
        self.start_time = None
        self.end_time = None
        self.scenarioname = None
        self.max_restarts = max_restarts
        self.status = 0
        self.logger = logging.getLogger(self.appname)
        self.logger.setLevel(level=log_level)
        self.model_folder = model_folder
        self.numerous_job = numerous_job
        self.result = None
        self.working_folder = working_folder
        if local:
            self.client = get_client()
        else:
            self.client = NumerousClient()

        self.client.logger.setLevel(log_level)

        class __Output:
            def __init__(self, client: NumerousClient, buffer_size: int):
                self._output = client.new_writer(buffer_size=buffer_size)

            def write_row(self, t, row):
                self._output.write_row(row)

            def close(self):
                self._output.close()

        self.output = __Output(self.client, buffer_size=0)
        self.setup_scenario()

    def setup_scenario(self):
        self.client.set_scenario_progress(
            "initializing", ScenarioStatus.ENVIRONMENT_INITIALIZING, 0.0, force=True
        )

        self.scenario, self.model_definition, self.files = self.client.get_scenario()

        main_job = None
        main_job_id = None
        for job in self.scenario.get("jobs", {}).values():
            if job.get("isMain", True):
                main_job = job
                break
        org_job_id = self.client._job_id
        if main_job:
            main_job_id = main_job.get("id")
            self.client._job_id = main_job_id
        else:
            self.logger.warning("no main job found on scenario")

        self.client._run_settings = None
        # Prepare simulation setup

        self.start_time = self.client.run_settings.start.timestamp()
        self.end_time = self.client.run_settings.end.timestamp()
        subscribe = False
        if main_job_id:
            subscribe = (
                self.scenario["jobs"][main_job_id]
                .get("runSettings", {})
                .get("runMode", "duration")
                == "continuous"
            )
        self.subscribe = subscribe
        self.scenarioname = self.scenario["scenarioName"]
        self.allow_hibernation = self.client.params.get("allow_hibernation", False)
        self.logger.info(f"allow hibernation: {self.allow_hibernation}")
        self.logger.info(f"subscribe {self.subscribe}")
        self.client._job_id = org_job_id

    def loop(self):
        self.logger.info(
            f"starting numerous app for {self.appname} on scenario {self.scenarioname}"
        )
        thread = Thread(target=self.numerous_job._start, args=(self,), daemon=False)
        thread.start()
        starttime = datetime.datetime.now()
        last_checkpoint = starttime
        restarts = 0
        warned = False

        while not self.terminate.is_set():
            checkpoint_time = datetime.datetime.now()
            if (
                not thread.is_alive()
                and self.numerous_job._exit_code.value <= ExitCode.ERROR.value
            ):
                if not warned:
                    self.client.set_scenario_progress(
                        message=f"{self.numerous_job._exit_code.description}. Retrying after 5 mins "
                        f"({restarts + 1}/{self.max_restarts})",
                        status=ScenarioStatus.RUNNING,
                        force=True,
                    )
                    warned = True
                if (
                    datetime.datetime.now() - starttime
                    > datetime.timedelta(seconds=300)
                ) and restarts < self.max_restarts:
                    self.logger.error(f"{self.appname} is dead.. restarting")
                    self.status = 0
                    thread = Thread(
                        target=self.numerous_job._start, args=(self,), daemon=False
                    )
                    thread.start()
                    sleep(5)
                    restarts += 1
                    starttime = datetime.datetime.now()
                    warned = False

                elif restarts >= self.max_restarts:
                    self.logger.error(
                        f"{self.appname} is dead and reached max restarts"
                    )
                    break

            elif not thread.is_alive():
                self.logger.debug(f"thread has ended with code {self.status}")
                break

            if checkpoint(checkpoint_time, last_checkpoint):
                self.backup.set()
                last_checkpoint = checkpoint_time

            sleep(0.5)
        self.logger.debug(f"waiting for {self.appname} to shut down...")
        thread.join()
        self.logger.info(f"{self.appname} stopped")
        self.logger.info("Main thread stopped gracefully")

        return self.result

    def _run(self):
        """
        Runs the simulation job with the model located in model_folder_name. Handles all events.
        """
        log_level = os.getenv("LOG_LEVEL", logging.root.level)
        logger = logging.getLogger("numerous-image-tools")
        logger.setLevel(level=log_level)
        terminate = Event()

        def handler(sig, frame):
            logger.debug(f"main thread received {sig} {frame}")
            terminate.set()

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

        try:
            if self.numerous_job is None:
                raise KeyError("no simulation job specified")
            if self.appname is None:
                logger.warning("no appname specified")

            logger.info(
                f"Welcome to numerous image tools. Base version {VERSION} - app {self.appname}"
            )

            #  Create a temporary working folder, that can be used to place generated and downloaded files.
            os.makedirs(self.working_folder, exist_ok=True)

            self.terminate = terminate
            self.client.terminate_event = terminate
            self.loop()

            self.client.set_scenario_progress(
                self.numerous_job._exit_code.description,
                self.numerous_job._exit_code.scenariostatus,
                force=True,
            )

            logger.debug(f"setting state {self.numerous_job._exit_code}")
            self.client.state.set("_status", self.numerous_job._exit_code.name)

        except Exception as e:
            logger.error(f"unhandled exception: {tb_str(e)}")
            self.client.set_scenario_progress(
                "unhandled error", ScenarioStatus.FAILED, 0.0, force=True
            )
            logger.debug("setting state -2")
            self.client.state.set("_status", -2)
        finally:
            self.output.close()
            self.client.close()
            logger.info("application ended")
            return self.result


def checkpoint(tnow, tlast, interval=60):
    dt = datetime.timedelta(minutes=interval)
    if tnow - tlast > dt:
        return True
    else:
        return False


def run_job(
    numerous_job=None,
    appname=None,
    max_restarts=0,
    model_folder="models",
    working_folder="tmp",
    reset_job=None,
):
    """
    Instantiates the application and runs it inside the try/except
    """

    app = NumerousApp(
        appname=appname,
        max_restarts=max_restarts,
        numerous_job=numerous_job,
        model_folder=model_folder,
        working_folder=working_folder,
        reset_job=reset_job,
    )

    app._run()
