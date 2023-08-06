import logging
import os
from datetime import datetime
from enum import Enum
from time import sleep, time
from typing import Any, Optional

from numerous.client import ScenarioStatus
from numerous.client.data_source import (
    DataSourceCompleted,
    DataSourceEmptyDataset,
    DataSourceHibernating,
    DataSourceStreamClosed,
    DataSourceStreamStarting,
)

from .errors import SimulationError, tb_str
from .system import NumerousSystem

LOG_LEVEL = os.getenv("LOG_LEVEL", logging.DEBUG)


class ExitCode(Enum):
    def __new__(cls, *args, **kwds):  # noqa: F841
        value = args[0]
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, _, description, scenariostatus):
        self.description = description
        self.scenariostatus = scenariostatus

    COMPLETED = 10, "Scenario completed", ScenarioStatus.FINISHED
    SOURCE_COMPLETED = 11, "Scenario source completed", ScenarioStatus.FINISHED
    TERMINATED = 20, "Scenario terminated", ScenarioStatus.FINISHED
    HIBERNATING = 30, "Scenario hibernating", ScenarioStatus.HIBERNATING
    SOURCE_HIBERNATING = 31, "Scenario source hibernating", ScenarioStatus.HIBERNATING
    SOURCE_CLOSED = -20, "Scenario source closed", ScenarioStatus.FINISHED
    TIMEOUT = -30, "Data could not be retrieved before timeout", ScenarioStatus.FAILED
    ERROR = -100, "An error occured. See logs.", ScenarioStatus.FAILED
    SOURCE_EMPTY = -110, "Scenario source empty", ScenarioStatus.FINISHED
    SYSTEM_NOT_INITIALIZED = (
        -120,
        "System could not be initialized",
        ScenarioStatus.FAILED,
    )


class NumerousBaseJob:
    def __init__(self):
        self.system = None
        self.input = None
        self.app = None
        self.logger = logging.getLogger("numerous-base-job")
        self.init = True
        self.last_print = {}
        self._t0 = None
        self._exit_code = None
        self._t = None
        self._details = ""
        # Wrapper to allow specialized instanciation of components
        self.wrapper = None

    def read_data(self, t):
        if self.app.client.terminate_event.is_set():
            raise TerminateJob
        if self.app.client.hibernate_event.is_set():
            raise HibernateJob

        while True:
            try:
                data = self.input.get_at_time(t)
            except DataSourceStreamStarting:
                self.app.client.set_scenario_progress(
                    "waiting for input stream to start", ScenarioStatus.INITIALZING, 0.0
                )
                sleep(0.1)
                continue
            except Exception:
                raise

            self.system.update_inputs(data)

            return data

    def _post_init(self):  # This is called before _run_job from the app.loop method
        timeout = 120
        t, states = self._load_states()
        dt = self.app.client.params.get("dt_simulation", 60)

        # Allow dt parameter to be a time value from front-end
        if isinstance(dt, dict):
            dt = dt["value"]

        t_stop = self.app.end_time if not self.app.subscribe else 0
        self._t0 = t

        self.input = self.app.client.get_inputs(
            self.app.scenario, t0=t, te=t_stop, dt=dt, tag_prefix="", timeout=timeout
        )

        self.system = NumerousSystem(
            self.app.client,
            self.app.scenario,
            self.app.files,
            self.app.start_time,
            t_stop,
            self.app.model_folder,
            self,
            states,
            t,
            dt,
            self.input,
            wrapper=self.wrapper,
        )

    def serialize_states(self, t: float) -> Optional[Any]:
        """
        A method called when saving states.
        Returns: states, which must be JSON serializable, to be saved.
        """
        return {}

    def _save_states(self, t, cause, details):
        if self.init:
            self.logger.info("model not initialized, could not save states")
            return

        model_states = self.serialize_states(t)
        states = {"t": t, "states": model_states, "cause": cause, "details": details}

        self.app.client.state.set("states", states)

        self.logger.debug(f"states saved: reason {cause} ({details})")

    def _load_states(self):
        t = self.app.start_time
        states = self.app.client.state.get("states", {})

        t = states.get("t", t)

        if states:
            self.logger.debug("states loaded")
        return t, states

    def _print_update(self, t, ix, update_interval=5):
        if self.last_print.get(ix) is None:
            self.last_print.update({ix: t})
            return True

        if t - self.last_print[ix] >= update_interval:
            self.last_print.update({ix: t})
            return True
        else:
            return False

    def _start(self, app) -> ExitCode:
        self.app = app
        exit_code = ExitCode.COMPLETED
        try:
            self._post_init()
            exit_code = self.run_job()
            if not exit_code:
                exit_code = ExitCode.COMPLETED
        except Exception as e:
            self.logger.error(f"An error occurred {tb_str(e)}")
            exit_code = ExitCode.ERROR
        finally:
            self.logger.info(f"job ended with status {exit_code}")
            self._exit_code = exit_code
            self._save_states(self._t, exit_code.description, self._details)
            self.post_run(exit_code)
            return exit_code

    def run_job(self) -> ExitCode:
        # Overwrite this method to create the simplest job
        raise NotImplementedError

    def post_run(self, exit_code: ExitCode):
        pass


class TerminateJob(Exception):
    pass


class HibernateJob(Exception):
    pass


class NumerousSimulationJob(NumerousBaseJob):
    def __init__(self):
        super(NumerousSimulationJob, self).__init__()
        self.system: Optional[NumerousSystem] = None
        self.align_outputs_to_next_timestep = True
        self.logger = logging.getLogger("numerous-simulation-job")
        self.logger.setLevel(level=LOG_LEVEL)
        self._completed = 0
        self._t_last = None

    def write_output(self, t, output):
        if not output:
            raise SimulationError("Expected an output, but got None")

        if self.init:
            self.app.client.set_timeseries_meta_data(
                [{"name": tag} for tag in output.keys()], offset=self.app.start_time
            )
            self.init = False

        if not self.align_outputs_to_next_timestep:
            output.update({"_index": self._t - self.app.start_time})
        else:
            output.update({"_index": t - self.app.start_time})

        self.app.output.write_row(t, output)

    def read_input(self, t: float) -> Optional[tuple[dict, float]]:
        data = self.read_data(t)
        if not data:
            self.app.client.set_scenario_progress(
                f"waiting for data. Last update: " f"{datetime.fromtimestamp(t)}",
                ScenarioStatus.RUNNING if not self.init else ScenarioStatus.WAITING,
                self._completed,
            )
            if self._print_update(datetime.now().timestamp(), 0, 10):
                self.logger.info(f"no data. Simulation time: {t}. ")
                sleep(1)
            return self.read_input(t)

        if t == 0 and data["_index"] > 0:
            self.logger.warning(f'setting start time to {data["_index"]}')
            self._t = data["_index"]

        return None

    def initialize_simulation_system(self) -> Optional[dict]:
        """
        A method that is called once model is initialized (after the first data is read).
        Can return the initial output to be saved.
        """
        return None

    def step(self, t: float, dt: float) -> tuple[float, dict]:
        """
        A method that is called after each data read. Could be a step solver, or some other data manipulating function.
        Returns: tuple of next timestamp and outputs as a dict with tags to be saved

        """
        return t + dt, {"no_job_defined": None}

    def _handle_data_exception(self, e: Exception):
        if e.__class__ == DataSourceHibernating:
            if self.app.allow_hibernation:
                exit_code = ExitCode.SOURCE_HIBERNATING
                self.app.client.hibernate(message="hibernating")
            else:
                exit_code = ExitCode.COMPLETED
            return exit_code
        elif e.__class__ == DataSourceCompleted:
            return ExitCode.SOURCE_COMPLETED
        elif e.__class__ == DataSourceEmptyDataset:
            return ExitCode.SOURCE_EMPTY
        elif e.__class__ == DataSourceStreamClosed:
            return ExitCode.SOURCE_CLOSED
        elif e.__class__ == TimeoutError:
            return ExitCode.TIMEOUT
        elif e.__class__ == TerminateJob:
            return ExitCode.COMPLETED
        elif e.__class__ == HibernateJob:
            return ExitCode.HIBERNATING

    def run_job(self) -> ExitCode:
        if self.system is None:
            self.app.client.set_scenario_progress(
                "Could not load model",
                ScenarioStatus.FAILED,
                0.0,
                force=True,
            )
            return ExitCode.ERROR
        elif self.system.end_time is None:
            self.app.client.set_scenario_progress(
                "No end time set",
                ScenarioStatus.FAILED,
                0.0,
                force=True,
            )
            return ExitCode.ERROR

        # This is the classic pipelines approach - well suited for digital twins
        # Run simulation in a loop
        self.logger.debug("entering loop")
        details: dict[str, Any] | str = ""
        last_data = {}

        t = None
        exit_code = ExitCode.COMPLETED
        try:
            self.app.client.set_scenario_progress(
                "bootup", ScenarioStatus.INITIALZING, 0.0, force=True
            )
            self.app.terminate.wait(timeout=5)
            self.app.client.set_scenario_progress(
                "waiting for initial data", ScenarioStatus.INITIALZING, 0.0, force=True
            )
            t_stop = self.system.end_time
            self._t = self._t0

            # Increasingly longer spacing between log updates to 60 s
            last_logged = -1000.0
            dt_log_max = 60.0
            dt_log = 1.0

            while True:
                if t_stop > 0:
                    self._completed = (
                        1 - (t_stop - self._t) / (t_stop - self.app.start_time)
                    ) * 100
                    self.app.client.set_scenario_progress(
                        "running", ScenarioStatus.RUNNING, self._completed
                    )
                else:
                    self.app.client.set_scenario_progress(
                        f"Simulation time: {datetime.fromtimestamp(self._t)}",
                        ScenarioStatus.RUNNING,
                        0,
                    )

                if self.app.backup.is_set():
                    self._save_states(
                        t, "backup", f"scheduled checkpoint @ {datetime.now()}"
                    )
                    self.app.backup.clear()

                self.read_input(self._t)

                if self.init:
                    self.app.client.set_scenario_progress(
                        "building model",
                        ScenarioStatus.MODEL_INITIALIZING,
                        0,
                        force=True,
                    )
                    initial_output = self.initialize_simulation_system()
                    if initial_output:
                        if "_index" not in initial_output:
                            initial_output.update({"_index": 0})
                        self.write_output(self._t, initial_output)

                try:
                    tnew, output = self.step(self._t, self.system.dt)
                    self.write_output(tnew, output)
                except Exception as e:
                    details = tb_str(e)
                    raise SimulationError(details)

                # Advance time
                self._t = tnew

                if time() - last_logged > dt_log:
                    last_logged = time()
                    dt_log = min(dt_log_max, dt_log * 2)

                    self.logger.info(
                        f"Calculation step. Time is now {self._t}. completed: {self._completed}"
                    )

                last_data = {
                    component.name: component.inputs
                    for component in self.system.components.values()
                }

                if (self._t >= t_stop) and (t_stop > 0):
                    self.logger.warning("maximum time reached")
                    exit_code = ExitCode.COMPLETED
                    break

        except (
            TimeoutError,
            TerminateJob,
            HibernateJob,
            DataSourceHibernating,
            DataSourceCompleted,
            DataSourceEmptyDataset,
            DataSourceStreamClosed,
        ) as e:
            exit_code = self._handle_data_exception(e)
            details = tb_str(e)

        except Exception as e:
            self.logger.error(f"numerous_app crashed: {tb_str(e)}")
            self.logger.debug(f"previous data: {last_data}")
            data = {
                component.name: component.inputs
                for component in self.system.components.values()
            }
            self.logger.debug(f"data at crash: {data}")
            details = {
                "error message": tb_str(e),
                "previous_data": last_data,
                "data at crash": data,
            }
            exit_code = ExitCode.ERROR
        finally:
            self.logger.info("job terminated")
            self._details = details
            return exit_code
