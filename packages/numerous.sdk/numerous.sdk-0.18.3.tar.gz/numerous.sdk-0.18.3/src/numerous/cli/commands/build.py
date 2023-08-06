import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..auth import AuthenticationError, login
from ..build_manager_client import BuildError, get_build_manager_client
from ..repository import NumerousRepository
from ..utils import bold, cyan, green, red


@dataclass
class BuildArgs:
    commit: Optional[str] = None
    launch: bool = False
    tags: Optional[list[str]] = None
    timeout: Optional[float] = None


def command_build(path: Optional[Path], args: BuildArgs):
    path = Path.cwd() if path is None else path
    try:
        repo = NumerousRepository(path).load()
    except Exception:
        print(red(f"Cannot build: {bold(path)} does not exist."))
        sys.exit(1)

    if repo.commit is None and args.commit is None:
        print(red("Cannot build: No commit checked out or specified."))
        sys.exit(1)

    if repo.remote is None:
        print(red("Cannot build: No remote is configured for the repository."))
        print(
            f"Use the command {bold('numerous config --remote <REMOTE_URL>')} to configure a remote for the "
            "repository."
        )
        sys.exit(1)

    if repo.scenario is None:
        print(red("Cannot build: A scenario must be checked out."))
        sys.exit(1)

    if repo.snapshot is None or repo.commit is None:
        print(red("Cannot build: No push has been made to the remote."))
        sys.exit(1)

    try:
        id_token = login(repo)
    except AuthenticationError:
        print(red("Cannot build: Login failed."))
        sys.exit(1)

    with get_build_manager_client(repo.remote.api_url, id_token) as build_manager:
        build_id = build_manager.launch_build(
            repo.remote.name,
            args.commit or repo.commit,
            args.launch,
            args.tags or [],
            args.timeout,
        )

        print(cyan(f"Build {bold(build_id)} enqueued. Awaiting remote builder..."))
        try:
            for message in build_manager.stream_build_logs(
                build_id, repo.scenario.id, repo.scenario.project_id
            ):
                print(cyan("[Remote builder]"), message)
        except BuildError:
            print(red("Build failed: An error occured during the build."))
            sys.exit(1)

        build_info = build_manager.get_build_info(repo.remote.name, build_id)

        print(cyan("Updating job image reference..."))
        build_manager.update_job_image_reference(
            repo.remote.name,
            repo.scenario.project_id,
            repo.scenario.id,
            repo.remote.job_id,
            build_info["tags"][0],
            repo.commit,
            build_id,
        )
    print(green(f"Success: Build {bold(build_id)} complete"))
