"""Components are the basic building blocks of systems.

This module contains the definition of Components, and the implementation of
functionality to create them.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class SubComponentNotFound(Exception):
    """Raised when creating a :class:`Component` is configured with a subcomponent that
    does not exist.
    """

    component_uuid: str


@dataclass
class Component:
    """A component of a :class:`numerous.sdk.models.scenario.Scenario`, containing
    parameters, input variables, and any subcomponents."""

    uuid: str
    id: str
    type: str
    name: str
    item_class: list[str]
    is_enabled: bool
    is_main: bool
    components: dict[str, "Component"]
    """The subcomponents of this component."""

    @staticmethod
    def from_document(
        component: dict[str, Any], all_components: list[dict[str, Any]]
    ) -> "Component":
        return Component(
            uuid=component["uuid"],
            id=component["id"],
            type=component["type"],
            name=component["name"],
            is_enabled=not bool(component["disabled"]),
            is_main=bool(component["isMainComponent"]),
            components=_extract_subcomponents(component, all_components),
            item_class=component["item_class"].split("."),
        )


def _extract_subcomponents(
    component: dict[str, Any], all_components: list[dict[str, Any]]
):
    return {
        subcomponent_ref["name"]: _extract_subcomponent(
            subcomponent_ref["uuid"], all_components
        )
        for subcomponent_ref in component["subcomponents"]
    }


def _extract_subcomponent(
    subcomponent_uuid: str, all_components: list[dict[str, Any]]
) -> Component:
    subcomponent = next(
        (
            subcomponent
            for subcomponent in all_components
            if subcomponent.get("uuid") == subcomponent_uuid
        ),
        None,
    )

    if subcomponent is None:
        raise SubComponentNotFound(component_uuid=subcomponent_uuid)

    return Component.from_document(subcomponent, all_components)


def get_components_from_scenario_document(data: dict[str, Any]) -> dict[str, Component]:
    components = data.get("simComponents", [])
    subcomponent_uuids = _get_all_subcomponent_uuids(components)
    return {
        component["name"]: Component.from_document(component, components)
        for component in components
        if component["uuid"] not in subcomponent_uuids
    }


def _get_all_subcomponent_uuids(components: list[dict[str, Any]]) -> set[str]:
    all_subcomponent_uuids = set()

    for component in components:
        for subcomponent in component.get("subcomponents", []):
            all_subcomponent_uuids.add(subcomponent["uuid"])

    return all_subcomponent_uuids
