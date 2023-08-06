import io
import sys
from logging import Logger
from pathlib import Path
from typing import Optional

import requests

from ..auth import AuthenticationError, login
from ..build_manager_client import get_build_manager_client
from ..repository import NumerousRepository, ProjectScenario
from ..utils import (
    bold,
    cyan,
    extract_gzipped_tarball,
    green,
    hash_directory,
    red,
    yellow,
)


def command_checkout(
    log: Logger,
    path: Path,
    scenario: Optional[ProjectScenario],
    commit_id: Optional[str],
):
    path = Path.cwd() if path is None else path
    if not path.exists():
        print(red(f"Cannot checkout: {bold(path)} does not exist"))
        sys.exit(1)

    repo = NumerousRepository(path)
    try:
        repo.load()
    except Exception:
        print(red(f"Cannot checkout: {path} is not a repository."))
        sys.exit(1)

    if repo.remote is None:
        print(red("Cannot checkout: No remote is configured for the repository."))
        print(
            f"Use the command {bold('numerous config --remote <REMOTE_URL>')} to configure a remote for the "
            "repository."
        )
        sys.exit(1)

    try:
        id_token = login(repo)
    except AuthenticationError:
        print(red("Cannot checkout: Login failed."))
        sys.exit(1)

    with get_build_manager_client(repo.remote.api_url, id_token) as build_manager:
        if commit_id is None:
            if scenario is not None:
                scenario_id = scenario.id
            elif repo.scenario is not None:
                scenario_id = repo.scenario.id
            else:
                print(red("Cannot checkout: No scenario specified."))
            updates = build_manager.get_scenario_history(repo.remote.name, scenario_id)
            update = updates[0] if updates else None
        else:
            update = build_manager.get_history_update(repo.remote.name, commit_id)

        if update is None:
            if scenario:
                repo.scenario = scenario
                repo.save()
                print(green(f"Checked out fresh scenario {bold(scenario)}"))
                return
            else:
                print(red("Cannot checkout: no commit found"))
                sys.exit(1)

        snapshot = hash_directory(path)
        choice = input(
            yellow("There are changes since the last commit. Continue? (y/n) ")
        )  # nosec
        if snapshot != repo.snapshot and choice.strip().lower() != "y":
            print(red("Aborted checkout"))
            sys.exit(1)

        print(
            cyan(f"Downloading snapshot {bold(update.snapshot_id)} into {bold(path)}")
        )
        url = build_manager.get_download_url(
            repo.remote.name, update.project_id, update.scenario_id, update.snapshot_id
        )
        response = requests.get(url, allow_redirects=True)
        extract_gzipped_tarball(io.BytesIO(response.content), path)

        repo.snapshot = update.snapshot_id
        repo.commit = update.commit_id
        repo.scenario = ProjectScenario(
            scenario_id=update.scenario_id, project_id=update.project_id
        )
        repo.save()

        print(
            green(
                f"Checkout complete => Scenario {bold(repo.scenario)}, commit {bold(repo.commit)}"
            )
        )
