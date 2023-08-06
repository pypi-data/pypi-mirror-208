import sys
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import List

from prettytable import PrettyTable

from ..auth import AuthenticationError, login
from ..build_manager_client import HistoryUpdate, get_build_manager_client
from ..repository import NumerousRepository
from ..utils import bold, cyan, green, red, yellow


def print_updates_table(repo: NumerousRepository, updates: List[HistoryUpdate]):
    table = PrettyTable()
    table.field_names = ["Timestamp", "Scenario", "Comment", "Commit ID", "Current"]
    for update in updates:
        table.add_row(
            [
                datetime.fromtimestamp(update.timestamp),
                update.scenario_id,
                update.comment,
                update.commit_id,
                f"{green('*')} {red('dirty') if repo.is_dirty() else ''}"
                if repo.commit == update.commit_id
                else "",
            ]
        )
    print(table)


def print_updates_git(repo: NumerousRepository, updates: List[HistoryUpdate]):
    for update in updates:
        state = (
            f" {green('current')}{red(' dirty') if repo.is_dirty() else ''}"
            if repo.commit == update.commit_id
            else ""
        )
        print(
            f"{yellow(f'commit {update.commit_id}')} {yellow('(')}"
            f"{cyan(update.project_id + ':' + update.scenario_id)}{yellow(')')}{state}"
        )
        update_time = datetime.fromtimestamp(update.timestamp)
        print(f"Author: {update.user_full_name} <{update.user_email}>")
        print(f'Date:   {update_time.strftime("%a %b %d %H:%M:%S %Y %z")}')
        print()
        for line in update.comment.splitlines():
            print("    " + line)
        print()


def command_log(log: Logger, path: Path, display_mode: str):
    path = path or Path.cwd()

    try:
        repo = NumerousRepository(path).load()
    except Exception as excp:
        log.debug(f"Exception {type(excp)} {excp}")
        print(red(f"Cannot get logs: {bold(str(path))} is not a repository."))
        sys.exit(1)

    if repo.remote is None:
        print(red("Cannot get logs: No remote is configured for the repository."))
        print(
            f"Use the command {bold('numerous config --remote <REMOTE_URL>')} to configure a remote for the "
            "repository."
        )
        sys.exit(1)

    if repo.scenario is None:
        print(red("Cannot get logs: A scenario must be checked out."))
        print(f"Check out a scenario with {bold('numerous checkout <SCENARIO ID>')}")
        print(
            f"Push to a scenario with {bold('numerous push -c <COMMENT> <SCENARIO ID>')}"
        )
        sys.exit(1)

    try:
        id_token = login(repo)
    except AuthenticationError:
        print(red("Cannot get logs: Login failed."))
        sys.exit(1)

    with get_build_manager_client(repo.remote.api_url, id_token) as build_manager:
        updates = build_manager.get_scenario_history(repo.remote.name, repo.scenario.id)

    if not updates:
        print(f"No history exists for remote {bold(repo.remote)}")

    if display_mode == "table":
        print_updates_table(repo, updates)
    else:
        print_updates_git(repo, updates)
