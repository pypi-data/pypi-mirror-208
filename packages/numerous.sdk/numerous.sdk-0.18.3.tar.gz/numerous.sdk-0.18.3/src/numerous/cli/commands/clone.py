import io
import sys
from logging import Logger
from pathlib import Path

import requests

from ..auth import AuthenticationError, login
from ..build_manager_client import get_build_manager_client
from ..repository import NumerousRepository, ProjectScenario, RepositoryRemote
from ..utils import (
    bold,
    cyan,
    extract_gzipped_tarball,
    green,
    print_repository_help_message,
    red,
)


def cleanup(path: Path):
    (path / NumerousRepository.FILE_NAME).unlink(True)
    (path / ".exclude").unlink(True)
    path.rmdir()


def command_clone(
    log: Logger, scenario: ProjectScenario, path: Path, remote: RepositoryRemote
) -> None:
    path = path or (Path.cwd() / remote.name)

    if path.exists():
        print(red(f"Cannot clone: {bold(path)} already exists"))
        sys.exit(1)

    repo = NumerousRepository(path)
    repo.remote = remote
    repo.scenario = scenario
    path.mkdir()

    try:
        try:
            id_token = login(repo)
        except AuthenticationError:
            print(red("Cannot clone: Login failed."))
            cleanup(path)
            sys.exit(1)

        with get_build_manager_client(repo.remote.api_url, id_token) as build_manager:
            updates = build_manager.get_scenario_history(repo.remote.name, scenario.id)

            if not updates:
                print(red("Cannot clone: No commit found"))
                sys.exit(1)

            update = updates[0]
            repo.snapshot = update.snapshot_id
            repo.scenario = scenario

            print(
                cyan(
                    f"Downloading snapshot {bold(repo.snapshot)} into {bold(path.absolute())}"
                )
            )
            url = build_manager.get_download_url(
                repo.remote.name,
                repo.scenario.project_id,
                repo.scenario.id,
                repo.snapshot,
            )
            response = requests.get(url, allow_redirects=True)
            extract_gzipped_tarball(io.BytesIO(response.content), path)

            repo.commit = update.commit_id
            repo.save()
            abs_path = path.absolute()
            print(
                green(
                    f"Repository {bold(repo.remote.name)} was cloned into {bold(abs_path)}"
                )
            )
            print_repository_help_message(abs_path)
    except BaseException:
        path.rmdir()
        print(red("Cannot clone: An error occured."))
        sys.exit(1)
    repo.save()
