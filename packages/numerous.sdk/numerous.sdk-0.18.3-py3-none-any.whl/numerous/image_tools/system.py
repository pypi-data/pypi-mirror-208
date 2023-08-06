import copy
import importlib
import logging
import os
import sys
from pathlib import Path
from time import sleep
from typing import Any, Iterable, Optional

import networkx as nx

from numerous.client import NumerousClient, ScenarioStatus
from numerous.client.data_source import DataSourceStreamStarting
from numerous.image_tools.errors import tb_str

logger = logging.getLogger("sim-setup")


class Component:
    def __init__(
        self,
        component_id: str,
        container_id: str,
        name: str,
        folder: str,
        path: str,
        handle: str,
        constants: dict,
        parameters: dict,
        import_flag: bool = False,
        item_class: Optional[str] = None,
    ):
        self._folder = Path(folder) if folder else None
        self._path = Path(path) if path else None
        self._handle = handle
        self.constants = constants
        self.parameters = parameters
        self._constructor = None
        self._entrypoint = None
        self.item = None
        self.item_class = item_class
        self.name = name
        self.component_id = component_id
        self.container_id = container_id
        self._import = import_flag
        self.inputs: dict[str, dict] = {}
        self.model: Any = None
        self.components: dict[str, Component] = {}

    def _initialize(self, system, wrapper=None):
        if not self._import:
            return

        if wrapper:
            item = wrapper(self, self.name, system)
        else:
            item = self._entrypoint(self.name, system)

        self.item = item
        return item

    def _dynamicimport(self):
        if not self._import:
            return
        _entrypoint = getattr(
            importlib.import_module(self._path.as_posix()), self._handle
        )
        self._entrypoint = _entrypoint

    def _add_subcomponent(self, component):
        self.components.update({component.name: component})


class Project:
    def __init__(self, project: dict):
        self._project = project
        self.parameters = self._format_parameters()
        self.description = project.get("description")
        self._id = project.get("id")

    def _format_parameters(self):
        project_parameters = self._project.get("parameters")
        if not project_parameters:
            return {}

        return {
            project_parameter["id"]: project_parameter["value"]
            for project_parameter in project_parameters
        }


def unroll_components(
    components: Iterable[Component],
    graph: nx.DiGraph,
    references: list[str],
    container_references: dict[str, str],
) -> list[Component]:
    unrolled_components = []
    for component in components:
        unrolled_components.extend(
            unroll_components(
                component.components.values(),
                graph,
                references,
                container_references,
            )
        )

        graph.add_node(component.component_id, component=component)
        references.append(component.component_id)
        if component.container_id:
            container_references[component.container_id] = component.component_id

        unrolled_components.append(component)
    return unrolled_components


def sort_components(components: list[Component]) -> list[Component]:
    graph = nx.DiGraph()
    references: list[str] = []
    container_references: dict[str, str] = {}
    unrolled_components: list[Component] = unroll_components(
        components, graph, references, container_references
    )

    for component in unrolled_components:
        for param_name, param in component.constants.items():
            if isinstance(param, dict) and "ref" in param:
                ref = param["ref"]
                if ref in container_references:
                    ref = container_references[ref]
                    param["ref"] = ref
                if ref in references:
                    graph.add_edge(ref, component.component_id)
                else:
                    print(
                        f"Warning: {ref} is not defined. Referenced from {component.component_id}"
                    )

    components_ = nx.get_node_attributes(graph, "component")
    components_top_sorted = [components_[n] for n in nx.topological_sort(graph)]
    return components_top_sorted


class NumerousSystem:
    def __init__(
        self,
        nc: NumerousClient = None,
        scenario=None,
        files=None,
        start_time=None,
        end_time=None,
        model_folder=None,
        numerous_job=None,
        states=None,
        t=None,
        dt=None,
        input=None,
        wrapper=None,
        load_model=True,
    ):
        self.references: dict[str, str] = {}
        self.nc = nc
        self.scenario = scenario
        self.files = files
        self.start_time = start_time
        self.end_time = end_time
        self._initialized = False
        self.logger = logging.getLogger("NumerousSystem")
        self._model_folder = model_folder
        self._has_model = False
        self.wrapper = wrapper
        self.numerous_job = numerous_job
        self.states = states
        self.dt = dt
        self.input = input

        # Initialize other system variables
        self.top_level_components = self._format_job_spec(self.scenario)
        self.unrolled_components = sort_components(self.top_level_components)
        for component in self.unrolled_components:
            if component._import:
                self._has_model = True
                break
        self.components = {
            component.name: component for component in self.unrolled_components
        }

        if load_model:
            self.load_model(t)

    def load_model(self, t):
        self.nc.set_scenario_progress(
            "Environment Initializing",
            ScenarioStatus.ENVIRONMENT_INITIALIZING,
            0.0,
            clean=True,
        )
        # Download needed files
        self._download_custom_files()
        self._dynamic_import_components()

        self.parameters = {}
        self.project = Project(project=self.nc.get_project_document())

        for par in self.scenario.get("parameters", []):
            if "id" in par and "value" in par:
                self.parameters.update({par.get("id"): par.get("value")})

        if self._has_model:
            while True:
                try:
                    data = self.input.get_at_time(t)
                    self.update_inputs(data)
                    self.instantiate_model()
                    self.nc.set_scenario_progress(
                        "model initialized", ScenarioStatus.INITIALZING, 0.0
                    )
                    break

                except DataSourceStreamStarting:
                    self.nc.set_scenario_progress(
                        "waiting for input stream to start",
                        ScenarioStatus.INITIALZING,
                        0.0,
                    )
                    sleep(0.1)
                    continue
                except Exception as e:
                    self.logger.error(f"could not initialize model {tb_str(e)}")
                    raise

        self.logger.debug("completed setup")

    def _add_path_topdown(self, top):
        if top in sys.path:
            return
        for root, _, __ in os.walk(top, topdown=True):
            sys.path.append(root)

    def _download_custom_files(self):
        # Check if there are any custom files and download them if so
        datasets = self.scenario.get("datasets", [])
        if len(datasets) > 0:
            self.nc.get_download_files(datasets)

    def instantiate_model(self):
        self.numerous_job.system = self

        for component in self.unrolled_components:
            for constant in component.constants.keys():
                val = component.constants[constant]
                # Handle references
                if isinstance(val, dict) and "ref" in val:
                    if val["ref"] in self.references:
                        ref_val = self.references[val["ref"]]
                    else:
                        ref_val = None
                        self.logger.warning(
                            f"{val['ref']} not found for {component.name} with {constant}. "
                            f"Available references are {self.references.keys()}"
                        )

                    component.constants[constant] = ref_val

            component.model = component._initialize(self, self.wrapper)

            # Add newly create component model to references to be passed in for subsequent ref values

            self.references[component.component_id] = component.model
            if component.container_id:
                self.references[component.container_id] = component.model

    def _dynamic_import_components(self):
        for component in self.unrolled_components:
            self._add_path_topdown(component._folder)
            component._dynamicimport()

    def update_inputs(self, data):
        if data is None:
            return
        component_data = copy.deepcopy(data)
        component_data.pop("_index")
        component_data.pop("_index_relative")
        self.input_data = component_data

        for input_tag, value in component_data.items():
            try:
                component_name = input_tag.split(".")[0]
                subcomponents = input_tag.split(".")[1:]
            except IndexError:
                logger.error(
                    f"input {input_tag} could not be split into component and subcomponent"
                )
                raise

            if component_name in self.components:
                self.components[component_name].inputs.update(
                    {".".join(subcomponents): value}
                )

    def _format_job_spec(self, scenario):
        simcomponents = scenario["simComponents"]
        component_list = []
        components = {}

        for simcomponent in simcomponents:
            if simcomponent.get("disabled", False) or simcomponent.get(
                "isSubcomponent"
            ):
                continue
            component = self._add_components_recursive(simcomponents, simcomponent)
            components.update({simcomponent["name"]: component})
            component_list.append(component)

        # Return list of components

        return component_list

    def _find_subcomponents(self, subcomps, simcomponents):
        subcomponents = []
        for subcomp in subcomps:
            for component in simcomponents:
                if component.get("uuid") == subcomp.get("uuid"):
                    subcomponents.append(component)
        return subcomponents

    def _add_components_recursive(self, simcomponents, simcomponent, level=0):
        component = self._add_component(simcomponent)

        subcomps = simcomponent.get("subcomponents")
        if subcomps:
            subcomponents_list = self._find_subcomponents(subcomps, simcomponents)
            for subcomponent in subcomponents_list:
                if subcomponent.get("disabled", False):
                    continue
                subcomponent = self._add_components_recursive(
                    simcomponents, subcomponent, level=level + 1
                )
                component._add_subcomponent(subcomponent)
        return component

    def _add_component(self, simcomponent):
        handle = None
        has_model = False
        folder = "."
        path = "."

        # Get values for helper variables
        item_class = simcomponent["item_class"]
        items = []
        if item_class:
            items = item_class.split(".")
        component_name = simcomponent["name"]
        component_id = simcomponent["uuid"]
        container_id = (
            simcomponent["containerID"] if "containerID" in simcomponent else None
        )

        if item_class and len(items) > 1:
            has_model = True

            model_file_name = items[-2]
            handle = items[-1]

            if len(items) > 2:
                model_name = items[0]

                folder = f"{self._model_folder}/{model_name}"
                path = f"{self._model_folder}.{model_name}.{model_file_name}"
            else:
                folder = f"{self._model_folder}"
                path = f"{self._model_folder}.{model_file_name}"
        else:
            self.logger.warning(
                f"Skipping adding model for {component_name} as it does not obey requirements: "
                f"item_class is not None and must be formatted as x.y/x.y.z "
                f"(item_class: {item_class})"
            )

        component_constants = {}
        if simcomponent["parameters"]:
            for d in simcomponent["parameters"]:
                if d["type"] == "file":
                    component_constants[d["id"]] = d["value"]["name"]
                elif d["type"] == "reference":
                    component_constants[d["id"]] = {"ref": d["value"]}
                else:
                    component_constants[d["id"]] = d["value"]

        # Format parameters ('inputVariables' in frontend)
        component_parameters = (
            {
                d["id"]: f'{simcomponent["name"]}.{d["id"]}'
                for d in simcomponent["inputVariables"]
            }
            if simcomponent["inputVariables"]
            else {}
        )

        # Make a complete dict with formatted specifications

        if self._model_folder == ".":
            path = path.lstrip(".")

        component = Component(
            component_id=component_id,
            container_id=container_id,
            name=component_name,
            folder=folder,
            path=path,
            handle=handle,
            constants=component_constants,
            parameters=component_parameters,
            import_flag=has_model and self._model_folder is not None,
            item_class=item_class,
        )

        return component
