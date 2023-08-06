import json
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, List, Optional

import grpc
import spm_pb2
from spm_pb2_grpc import BuildManagerStub, SPMStub

from .auth import IdTokenAuth
from .utils import StubClient

log = logging.getLogger(__name__)


class SnapshotAlreadyExistsError(Exception):
    pass


class BuildError(Exception):
    pass


class SnapshotError(Exception):
    pass


class HistoryUpdate:
    def __init__(self, update: spm_pb2.HistoryUpdate):
        self.commit_id: str = update.id
        self.snapshot_id: str = update.snapshot_id
        self.scenario_id: str = update.scenario_id
        self.project_id: str = update.project_id
        self.comment: str = update.comment
        self.timestamp: float = update.timestamp
        self.user_full_name: str = update.user.full_name
        self.user_email: str = update.user.email


class BuildManagerClient:
    def __init__(self, stub: BuildManagerStub, spm_stub: SPMStub):
        self._stub: BuildManagerStub = stub
        self._spm_stub = spm_stub

    def launch_build(
        self,
        repository: str,
        commit_id: str,
        launch_after_build: bool,
        tags: List[str],
        timeout: Optional[float],
    ):
        request = spm_pb2.BuildRequest(
            repository=repository,
            commit_id=commit_id,
            launch_after_build=launch_after_build,
            tags=tags,
            timeout=timeout,
        )
        response = self._stub.LaunchBuild(request)
        return response.build_id

    def get_build_info(self, repository: str, build_id: str) -> Any:
        request = spm_pb2.BuildInfoRequest(repository=repository, build_id=build_id)
        response = self._stub.GetBuildInfo(request)
        return json.loads(response.info)

    def update_job_image_reference(
        self,
        repository: str,
        project_id: str,
        scenario_id: str,
        job_id: str,
        path: str,
        commit_id: str,
        build_id: str,
    ):
        request = spm_pb2.JobImageReferenceUpdate(
            project=project_id,
            scenario=scenario_id,
            job=job_id,
            name=repository,
            path=path,
            repository=repository,
            commit_id=commit_id,
            internal=True,
            build=build_id,
        )
        self._stub.UpdateJobImageReference(request)

    def get_scenario_history(
        self, repository: str, scenario_id: str
    ) -> List[HistoryUpdate]:
        request = spm_pb2.HistoryRequest(repository=repository, scenario_id=scenario_id)
        response = self._stub.GetHistory(request)
        return [HistoryUpdate(update) for update in response.updates]

    def get_history_update(
        self, repository: str, commit_id: str
    ) -> Optional[HistoryUpdate]:
        request = spm_pb2.HistoryRequest(
            repository=repository, history_update_ids=[commit_id]
        )
        response = self._stub.GetHistory(request)
        return HistoryUpdate(response.updates[0]) if len(response.updates) > 0 else None

    def create_history_update(
        self,
        repository: str,
        project_id: str,
        scenario_id: str,
        snapshot_id: str,
        parent_commit_id: Optional[str],
        comment: str,
        timestamp: float,
    ) -> str:
        request = spm_pb2.HistoryUpdate(
            repository=repository,
            project_id=project_id,
            scenario_id=scenario_id,
            snapshot_id=snapshot_id,
            parent_commit_id=parent_commit_id,
            comment=comment,
            timestamp=datetime.utcnow().timestamp(),
        )
        response = self._stub.CreateHistoryUpdate(request)
        return str(response.commit_id)

    def get_download_url(
        self, repository: str, project_id: str, scenario_id: str, snapshot_id: str
    ) -> str:
        request = spm_pb2.PullRequest(
            repository=repository,
            snapshot_id=snapshot_id,
            project_id=project_id,
            scenario_id=scenario_id,
        )
        response = self._stub.PullSnapshot(request)
        return str(response.archive_url.url)

    def create_snapshot_get_upload_url(
        self, repository: str, snapshot_id: str, file_structure: Any
    ) -> str:
        request = spm_pb2.Snapshot(
            snapshot_id=snapshot_id,
            repository=repository,
            file_structure=file_structure,
            only_get_uploads=False,
        )

        try:
            response = self._stub.CreateSnapshot(request)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise SnapshotAlreadyExistsError()
            else:
                raise SnapshotError()

        return str(response.upload_url)

    def stream_build_logs(
        self, build_id: str, scenario_id: str, project_id: str
    ) -> Iterator[str]:
        request = spm_pb2.Subscription(
            channel_patterns=[build_id], project_id=project_id, scenario=scenario_id
        )
        for update in self._spm_stub.SubscribeForUpdates(request):
            if update.message == ":BUILD_DONE:":
                break
            elif update.message == ":ERROR:":
                raise BuildError()
            else:
                yield update.message


@contextmanager
def get_build_manager_client(
    api_url: str, id_token: str
) -> Iterator[BuildManagerClient]:
    with StubClient(api_url, SPMStub, IdTokenAuth(id_token)) as spm_stub:
        with StubClient(api_url, BuildManagerStub, IdTokenAuth(id_token)) as stub:
            yield BuildManagerClient(stub, spm_stub)
