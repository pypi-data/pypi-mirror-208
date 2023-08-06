from dataclasses import dataclass


@dataclass
class JobIdentifier:
    """An identifier for a job execution and its related objects"""

    project_id: str
    scenario_id: str
    job_id: str
