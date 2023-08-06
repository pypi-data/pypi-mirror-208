from dataclasses import dataclass
from typing import Any

from .component import Component, get_components_from_scenario_document
from .job import Job


@dataclass
class Scenario:
    id: str
    name: str
    components: dict[str, Component]
    jobs: list[Job]

    @staticmethod
    def from_document(data: dict[str, Any]) -> "Scenario":
        return Scenario(
            id=data["id"],
            name=data.get("scenarioName", ""),
            components=get_components_from_scenario_document(data),
            jobs=[
                Job.from_document(job_id, job_data)
                for job_id, job_data in data.get("jobs", {}).items()
            ],
        )
