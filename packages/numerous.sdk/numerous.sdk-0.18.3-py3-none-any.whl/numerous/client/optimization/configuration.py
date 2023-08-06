import json
import logging
from typing import Any, Iterable, Optional, TypedDict

import spm_pb2
import spm_pb2_grpc

log = logging.getLogger(__name__)


class ScenarioSetting(TypedDict):
    path: list[str]
    type: str
    value: float
    id: str
    display_name: str


class OptimizationSetting:
    def __init__(self, path: list[str], setting_type: str, value: Any, raw: Any):
        self.path = path
        self.type = setting_type
        self.value = value
        self.raw = raw

    def scenario_setting(self, value: float) -> ScenarioSetting:
        return {
            "id": self.raw.get("id"),
            "display_name": self.raw.get("displayName"),
            "type": self.type,
            "value": value,
            "path": self.path,
        }


def extract_component(components: dict[str, Any], component: dict[str, Any]):
    value: dict[str, dict[str, Any]] = {"params": {}, "components": {}}
    for param in component.get("parameters", []):
        value["params"][param["id"]] = param.get("value")
    for subcomponent_ref in component.get("subcomponents", []):
        subcomponent = component.get(subcomponent_ref["uuid"], {})
        value["components"][subcomponent["name"]] = extract_component(
            components, subcomponent
        )
    return value


class OptimizationConfiguration:
    def __init__(
        self, spm_stub: spm_pb2_grpc.SPMStub, project_id: str, scenario_id: str
    ):
        scenario_response = spm_stub.GetScenario(
            spm_pb2.Scenario(project=project_id, scenario=scenario_id)
        )
        scenario = json.loads(scenario_response.scenario_document)

        if scenario.get("optimize", False):
            raise RuntimeError(
                f"Optimization was not enabled on scenario {scenario_id} in project {project_id}."
            )

        target_scenario = self._load_target_scenario_data_and_set_job_id(
            spm_stub, project_id, scenario
        )
        self.settings = list(self._parse_optimization_settings(target_scenario))
        components = self._components_by_uuid(scenario)
        self._parse_aggregator_configuration(components)
        self._parse_goal_function_configuration(components)

    def _load_target_scenario_data_and_set_job_id(
        self, spm_stub: spm_pb2_grpc.SPMStub, project_id: str, scenario: dict[str, Any]
    ) -> dict:
        self.target_scenario_id = scenario["optimizationTargetScenarioID"]
        target_scenario_request = spm_pb2.Scenario(
            project=project_id, scenario=self.target_scenario_id
        )
        target_scenario_response = spm_stub.GetScenario(target_scenario_request)
        target_scenario = json.loads(target_scenario_response.scenario_document)

        if not isinstance(target_scenario, dict):
            raise TypeError(f"Received invalid target scenario data: {target_scenario}")

        self.target_job_id = next(
            job_id
            for job_id, job in target_scenario["jobs"].items()
            if job.get("isMain", False)
        )
        return target_scenario

    def _parse_optimization_settings(
        self, target_scenario: dict[str, Any]
    ) -> Iterable[OptimizationSetting]:
        setting_paths = target_scenario.get("optimizationSettingsPaths", {})
        setting_paths.pop("__CONVERTED_FROM_MAP", None)  # Remove helper attribute
        settings_components = target_scenario.get(
            "optimizationSettingsSimComponents", {}
        )
        settings_components.pop("__CONVERTED_FROM_MAP", None)  # Remove helper attribute
        for settings_component_uuid, settings_components in settings_components.items():
            [
                settings_component
            ] = settings_components  # Assumption that exactly one component exists
            setting_path = setting_paths.get(settings_component_uuid)
            setting_type = settings_component_uuid.split("_")[
                -1
            ]  # param, value, offset, scale
            setting_value = extract_component(settings_components, settings_component)
            component: Optional[dict[str, Any]] = next(
                (
                    c
                    for c in target_scenario.get("simComponents", [])
                    if c["uuid"] == setting_path[-2]
                ),
                None,
            )
            if component is None:
                log.warning("Invalid component for optimization: %s", setting_path[-2])
                continue
            component_key = (
                "parameters" if setting_type == "param" else "inputVariables"
            )
            setting_raw = next(
                (
                    attr
                    for attr in component[component_key]
                    if attr["uuid"] == setting_path[-1]
                ),
                None,
            )
            setting_raw = self._add_setting_attrs_from_scenario(
                target_scenario,
                component_key,
                setting_path,
                setting_raw,
            )
            if None in (setting_path, setting_type, setting_value):
                log.warning(
                    "Invalid optimization setting component: %s", settings_component
                )
                continue
            yield OptimizationSetting(
                setting_path, setting_type, setting_value, setting_raw
            )

    def _parse_aggregator_configuration(self, components: dict[str, dict[str, Any]]):
        self.aggregator_config = None
        aggregator_component_uuid = next(
            (
                comp["uuid"]
                for comp in components.values()
                if comp["name"] == "aggregator"
            ),
            None,
        )
        if aggregator_component_uuid not in components:
            raise RuntimeError("Missing required aggregator component")

        aggregator_component = components.get(aggregator_component_uuid, {})
        self.aggregator_config = extract_component(components, aggregator_component)

    def _parse_goal_function_configuration(self, components: dict[str, dict[str, Any]]):
        self.goal_function_inputs = []
        self.goal_function_config = None
        goal_function_component_uuid = next(
            (
                comp["uuid"]
                for comp in components.values()
                if comp["name"] == "goal_function"
            ),
            None,
        )
        if goal_function_component_uuid not in components:
            raise RuntimeError("Missing required goal function component")

        goal_function_component = components.get(goal_function_component_uuid, {})
        self.goal_function_config = extract_component(
            components, goal_function_component
        )
        for input_variable in goal_function_component.get("inputVariables", []):
            if input_variable["dataSourceType"] != "scenario":
                log.warning(
                    "Invalid input variable for optimization: %s", input_variable
                )
                continue
            self.goal_function_inputs.append(
                {
                    "tag": input_variable["tagSource"]["tag"],
                    "scale": input_variable["scaling"],
                    "offset": input_variable["offset"],
                }
            )

    @staticmethod
    def _components_by_uuid(scenario: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return {comp["uuid"]: comp for comp in scenario.get("simComponents", [])}

    @staticmethod
    def _add_setting_attrs_from_scenario(
        scenario: dict, component_key: str, path: list[str], setting_raw: Optional[dict]
    ) -> Optional[dict[str, Any]]:
        attrs = ("id", "displayName")
        component: dict = next(
            (c for c in scenario.get("simComponents", []) if c["uuid"] == path[-2]), {}
        )
        setting: Optional[dict] = next(
            (s for s in component.get(component_key, []) if s["uuid"] == path[-1]), None
        )
        if setting is None:
            log.debug("Setting %s with key %s is not found", path, component_key)
        else:
            old_attrs = set() if setting_raw is None else setting_raw.keys()
            attrs_to_update = {
                attr: setting[attr]
                for attr in attrs
                if attr in setting and attr not in old_attrs
            }
            log.debug("Adding attrs %s of %s", attrs_to_update, setting_raw)
            if setting_raw is None:
                setting_raw = attrs_to_update if attrs_to_update else None
            else:
                setting_raw.update(**attrs_to_update)
        return setting_raw
