import sys
from logging import Logger
from pathlib import Path

from ..auth import AuthenticationError, login
from ..repository import NumerousRepository
from ..utils import bold, green, red


def command_login(log: Logger, path: Path):
    path = path or Path.cwd()

    try:
        repo = NumerousRepository(path).load()
    except Exception as excp:
        log.debug(f"Exception {type(excp)} {excp}")
        print(red(f"Cannot login: {bold(str(path))} is not a repository."))
        sys.exit(1)

    if repo.remote is None:
        print(red("Cannot login: No remote is configured for the repository."))
        print(
            f"Use the command {bold('numerous config --remote <REMOTE_URL>')} to configure a remote for the "
            "repository."
        )
        sys.exit(1)

    if repo.scenario is None:
        print(red("Cannot re-login: A scenario must be checked out."))
        print(f"Check out a scenario with {bold('numerous checkout <SCENARIO ID>')}")
        sys.exit(1)

    try:
        repo.refresh_token = None
        login(repo)
        print(green("Login succeeded."))
    except AuthenticationError:
        print(red("Login failed."))
        sys.exit(1)
