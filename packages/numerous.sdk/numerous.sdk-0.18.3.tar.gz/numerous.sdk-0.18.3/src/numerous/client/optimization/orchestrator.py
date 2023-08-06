import logging
import threading
from abc import ABC, abstractmethod
from time import sleep
from typing import Any, Dict, List, Tuple

from ..numerous_client import NumerousClient, ScenarioStatus
from .configuration import ScenarioSetting

log = logging.getLogger(__name__)


class OptimizationIteration:
    def __init__(
        self,
        scenario_id: str,
        execution_id: str,
        scenario_settings: List[ScenarioSetting],
    ):
        self.scenario_id = scenario_id
        self.execution_id = execution_id
        self.scenario_settings = scenario_settings

    def __str__(self):
        settings = [
            f'{s["type"]}: {s["id"]}={s["value"]}' for s in self.scenario_settings
        ]
        return f'Iteration[{self.scenario_id}][{", ".join(settings)}]'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "scenario_id": self.scenario_id,
            "scenario_settings": self.scenario_settings,
        }

    @classmethod
    def from_dict(cls, iteration: Dict[str, Any]) -> "OptimizationIteration":
        return cls(
            iteration["scenario_id"],
            iteration["execution_id"],
            iteration["scenario_settings"],
        )


class BaseOptimizationOrchestrator(ABC):
    def __init__(self, client: NumerousClient, parallelism: int):
        self.client = client
        self.target_job_id = self.client.optimization_config.target_job_id
        self.target_scenario_id = self.client.optimization_config.target_scenario_id
        self.aggregator_config = self.client.optimization_config.aggregator_config
        self.goal_function_config = self.client.optimization_config.goal_function_config
        self.goal_function_inputs = self.client.optimization_config.goal_function_inputs
        self.settings = self.client.optimization_config.settings
        self.parallelism = parallelism
        self.clean_wait_time = 1
        self.previous_ongoing_iterations = 0
        self.previous_iteration_status: Dict[str, ScenarioStatus] = {}
        log.info("Initializing orchestrator with parallelism %s", self.parallelism)

        # load state
        self.aggregated: List[Tuple[OptimizationIteration, float]] = [
            (OptimizationIteration.from_dict(agg["iteration"]), agg["value"])
            for agg in client.state.get("aggregated", [])
        ]
        self.completed: List[OptimizationIteration] = [
            OptimizationIteration.from_dict(completed)
            for completed in client.state.get("completed", [])
        ]
        self.ongoing: List[OptimizationIteration] = [
            OptimizationIteration.from_dict(ongoing)
            for ongoing in client.state.get("ongoing", [])
        ]
        self.failed: List[OptimizationIteration] = [
            OptimizationIteration.from_dict(failed)
            for failed in client.state.get("failed", [])
        ]
        if self.aggregated or self.completed or self.ongoing or self.failed:
            log.info(
                "Loaded %s aggregated, %s completed, %s ongoing, and %s failed iterations",
                len(self.aggregated),
                len(self.completed),
                len(self.ongoing),
                len(self.failed),
            )

    def _aggregate(self):
        for iteration in list(
            self.completed
        ):  # Create a copy, to prevent deleting from iterated collection
            aggregate = self.aggregate(iteration)
            self.client.set_optimization_iteration_score(
                iteration.scenario_id, aggregate
            )
            log.info("Aggregated %s to %f", iteration.scenario_id, aggregate)
            self.aggregated.append((iteration, aggregate))
            self.completed.remove(iteration)
        self.client.state.set(
            "aggregated",
            [
                {"value": value, "iteration": iteration.to_dict()}
                for iteration, value in self.aggregated
            ],
        )

    def _clean(self):
        finished = []
        failed = []

        if len(self.ongoing) != self.previous_ongoing_iterations:
            log.info("Awaiting finished iterations (%s ongoing)", len(self.ongoing))
            self.previous_ongoing_iterations = len(self.ongoing)

        for iteration in self.ongoing:
            doc, _ = self.client.get_scenario_document(scenario=iteration.scenario_id)
            status = (
                doc.get("jobs", {})
                .get(self.target_job_id, {})
                .get("status", {})
                .get("status", {})
            )

            if status != self.previous_iteration_status.get(iteration.scenario_id):
                log.debug(
                    "Iteration %s now %s", iteration.scenario_id, ScenarioStatus(status)
                )
                self.previous_iteration_status[iteration.scenario_id] = status
            if status == ScenarioStatus.FINISHED:
                finished.append(iteration)
            if status == ScenarioStatus.FAILED:
                failed.append(iteration)

        for iteration in finished:
            self.ongoing.remove(iteration)
            self.completed.append(iteration)
        for iteration in failed:
            self.ongoing.remove(iteration)
            self.failed.append(iteration)

        self.client.state.set(
            "ongoing", [ongoing.to_dict() for ongoing in self.ongoing]
        )
        self.client.state.set("failed", [failed.to_dict() for failed in self.failed])
        self.client.state.set(
            "completed", [completed.to_dict() for completed in self.completed]
        )

    def _launcher(self):
        log.info("Launching %s iterations...", len(self.iteration_configs))
        while self.iteration_configs:
            while not self._can_launch():
                sleep(0.1)
            self._launch(self.iteration_configs.pop())
        log.info("Launcher finished")

    def _launch(self, settings: List[ScenarioSetting]):
        scenario_id, execution_id = self.client.start_iteration_scenario(
            self.target_scenario_id, self.target_job_id, settings
        )
        iteration = OptimizationIteration(scenario_id, execution_id, settings)
        self.ongoing.append(iteration)
        self.client.state.set(
            "ongoing", [ongoing.to_dict() for ongoing in self.ongoing]
        )
        log.info("Started %s", iteration)
        self._running_progress()

    def _can_launch(self):
        return len(self.ongoing) < self.parallelism

    def _running_progress(self):
        finished = len(self.aggregated) + len(self.completed) + len(self.failed)
        total = finished + len(self.iteration_configs) + len(self.ongoing)
        progress = 100 * float(finished) / float(total)
        self.client.set_scenario_progress(
            "Running iterations", ScenarioStatus.RUNNING, progress, force=True
        )

    def _goal_function_progress(self):
        self.client.set_scenario_progress(
            "Searching for optimal iteration", ScenarioStatus.RUNNING, force=True
        )

    @abstractmethod
    def aggregate(self, iteration: OptimizationIteration) -> float:
        pass

    @abstractmethod
    def get_iteration_configs(self) -> List[List[ScenarioSetting]]:
        pass

    @abstractmethod
    def goal_function(self, current: float, best: float) -> float:  # noqa: F841
        pass

    def run(self, poll_timeout: float = 1.0) -> Tuple[OptimizationIteration, Any]:
        self.client.set_scenario_progress(
            "Initializing optimization", ScenarioStatus.INITIALZING, force=True
        )
        iteration_configs = self.client.state.get("settings", None)
        self.iteration_configs = (
            self.get_iteration_configs()
            if iteration_configs is None
            else iteration_configs
        )
        self.client.state.set("settings", self.iteration_configs)
        self._running_progress()
        launcher_thread = threading.Thread(name="Launcher", target=self._launcher)
        launcher_thread.start()
        while self.ongoing or launcher_thread.is_alive():
            self._clean()
            if self.completed:
                self._aggregate()
            else:
                sleep(poll_timeout)

        log.info(
            "Iteration and aggregation done (%s aggregates, %s failed), finding optimal scenario...",
            len(self.aggregated),
            len(self.failed),
        )
        candidate_iteration = None
        candidate_aggregate = None
        for iteration, aggregate in self.aggregated:
            self._goal_function_progress()
            if (
                candidate_iteration is None
                or self.goal_function(aggregate, candidate_aggregate) == aggregate
            ):
                candidate_iteration = iteration
                candidate_aggregate = aggregate

        self.client.state.unset("aggregated")
        self.client.state.unset("ongoing")
        self.client.state.unset("completed")
        self.client.state.unset("failed")
        self.client.state.unset("settings")

        if self.failed:
            raise RuntimeError(
                f"Optimization errors! {len(self.failed)} iterations failed"
            )
        elif candidate_iteration is None or candidate_aggregate is None:
            raise RuntimeError("Optimization did not find an optimal solution")
        else:
            log.info(
                "Optimization finished: Iteration=%s, Aggregate=%f",
                candidate_iteration,
                candidate_aggregate,
            )
            self.client.set_optimization_result(
                candidate_iteration.scenario_id,
                candidate_aggregate,
                candidate_iteration.scenario_settings,
            )
            return candidate_iteration, candidate_aggregate
