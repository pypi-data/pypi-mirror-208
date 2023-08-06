import logging
from pathlib import Path
from typing import Optional, Union

from numerous.client import NumerousClient

from .auth import get_refresh_token
from .job import start_local_job
from .repository import NumerousRepository


def get_client(
    path: Optional[Path] = None,
    clear_data: Optional[bool] = None,
    no_log: bool = False,
    log_level: Union[str, int] = logging.ERROR,
) -> NumerousClient:
    path = path or Path.cwd()
    repo = NumerousRepository(path).load()
    execution_id = start_local_job(repo)
    refresh_token = get_refresh_token(repo, execution_id)

    if repo.remote is None or repo.scenario is None:
        raise RuntimeError(
            "Repository not configured correctly, try checking out a scenario or re-initializing."
        )

    return NumerousClient(
        url=repo.remote.api_url,
        project=repo.scenario.project_id,
        scenario=repo.scenario.id,
        job_id=repo.remote.job_id,
        refresh_token=refresh_token,
        execution_id=execution_id,
        clear_data=clear_data,
        log_level=log_level,
        no_log=no_log,
    )
