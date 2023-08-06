import json
from pathlib import Path, PurePosixPath
from typing import Optional
from urllib.parse import urlparse

from numerous.cli.utils import exclude_paths, hash_directory, walk


class RepositoryRemote:
    def __init__(
        self,
        url: Optional[str] = None,
        api_url: Optional[str] = None,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        if name is not None and api_url is not None and job_id is not None:
            self.name = name
            self.api_url = api_url
            self.job_id = job_id
        elif url is not None:
            parsed_url = urlparse(url)
            _, self.job_id, self.name = PurePosixPath(parsed_url.path).parts
            self.api_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            raise ValueError(
                "RepositoryRemote must be supplied 'url' or 'api_url', 'job_id' and 'name'."
            )

    def __str__(self):
        return f"{self.api_url}/{self.job_id}/{self.name}"


class ProjectScenario:
    def __init__(
        self,
        project_scenario: Optional[str] = None,
        project_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
    ):
        if project_scenario:
            self.project_id, self.id = project_scenario.split(":")
        elif project_id is not None and scenario_id is not None:
            self.project_id = project_id
            self.id = scenario_id
        else:
            raise ValueError(
                "ProjectScenario must be supplied 'project_scenario' or 'project_id' and 'scenario_id"
            )

    def __str__(self):
        return f"{self.project_id}:{self.id}"


class NumerousRepository:
    FILE_NAME = ".numerous.repository.json"

    def __init__(self, path: Optional[Path] = None):
        self.path: Path = path or Path.cwd()
        self.organization: Optional[str] = None
        self.user: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.remote: Optional[RepositoryRemote] = None
        self.scenario: Optional[ProjectScenario] = None
        self.commit: Optional[str] = None
        self.snapshot: Optional[str] = None

    def save(self) -> "NumerousRepository":
        with (self.path / NumerousRepository.FILE_NAME).open("w") as fp:
            json.dump(
                {
                    "scenario": None if self.scenario is None else str(self.scenario),
                    "commit": self.commit,
                    "snapshot": self.snapshot,
                    "refresh_token": self.refresh_token,
                    "remote": None if self.remote is None else str(self.remote),
                    "organization": self.organization,
                    "user": self.user,
                },
                fp,
            )
            return self

    def load(self) -> "NumerousRepository":
        with (self.path / NumerousRepository.FILE_NAME).open("r") as fp:
            config = json.load(fp)
            self.remote = (
                None
                if config["remote"] is None
                else RepositoryRemote(url=config["remote"])
            )
            self.user = config["user"]
            self.organization = config["organization"]
            self.scenario = (
                None
                if config["scenario"] is None
                else ProjectScenario(config["scenario"])
            )
            self.commit = config["commit"]
            self.snapshot = config["snapshot"]
            self.refresh_token = config.get("refresh_token")
            return self

    def is_dirty(self) -> bool:
        return hash_directory(self.path) != self.snapshot

    def walk(self):
        exclude_file = self.path / ".exclude"
        exclude_patterns = (
            exclude_file.open("r").readlines() if exclude_file.exists() else []
        )
        yield from exclude_paths(self.path, walk(self.path), exclude_patterns)
