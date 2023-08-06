import spm_pb2
import spm_pb2_grpc

from .auth import IdTokenAuth, get_id_token
from .repository import NumerousRepository
from .utils import StubClient


def start_local_job(repo: NumerousRepository) -> str:
    if repo.remote is None:
        raise RuntimeError("Repository remote is not configured, use: numerous config")

    if repo.scenario is None:
        raise RuntimeError(
            "Repository scenario is not checked out, use: numerous checkout"
        )

    if repo.refresh_token is None:
        raise RuntimeError("Repository has no refresh token, use: numerous login")

    request = spm_pb2.StartLocalJobRequest(
        project_id=repo.scenario.project_id,
        scenario_id=repo.scenario.id,
        job_id=repo.remote.job_id,
    )

    id_token = get_id_token(repo.remote.api_url, repo.refresh_token)

    with StubClient(
        repo.remote.api_url, spm_pb2_grpc.JobManagerStub, IdTokenAuth(id_token)
    ) as job_manager:
        return str(job_manager.StartLocalJob(request).execution_id)
