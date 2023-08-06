import json
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

import health_pb2
import health_pb2_grpc
import spm_pb2
import spm_pb2_grpc

from . import config
from .common import RepeatedFunction, initialize_grpc_channel, parse_api_url


class NumerousAdminClient:
    def __init__(
        self,
        server: Optional[str] = None,
        port: Optional[int] = None,
        secure: Optional[bool] = None,
        refresh_token: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self._refresh_token = refresh_token or config.NUMEROUS_API_REFRESH_TOKEN
        if self._refresh_token is None:
            raise RuntimeError("Refresh token must be set.")
        if url:
            server, port, secure = parse_api_url(url)
        self.channel, self._instance_id = initialize_grpc_channel(
            server=server or config.NUMEROUS_API_SERVER,
            port=port or config.NUMEROUS_API_PORT,
            refresh_token=self._refresh_token,
            secure=secure if secure is not None else not config.FORCE_INSECURE,
            token_callback=self._get_access_token,
        )
        self._base_client = spm_pb2_grpc.SPMStub(self.channel)
        self._job_manager = spm_pb2_grpc.JobManagerStub(self.channel)
        self._build_manager = spm_pb2_grpc.BuildManagerStub(self.channel)
        self._token_manager = spm_pb2_grpc.TokenManagerStub(self.channel)
        self._health = health_pb2_grpc.HealthStub(self.channel)

        self._access_token = None
        self._terminated = False
        self._complete = False
        self._user = "test_user"  # TODO: replace or remove the hardcoded value
        self._organization = (
            "EnergyMachines"  # TODO: replace or remove the hardcoded value
        )
        self._access_token_refresher = RepeatedFunction(
            interval=9 * 60,
            function=self._refresh_access_token,
            run_initially=True,
            refresh_token=self._refresh_token,
        )
        self._access_token_refresher.start()

    def _refresh_access_token(self, refresh_token):
        token = self._token_manager.GetAccessToken(
            spm_pb2.RefreshRequest(refresh_token=spm_pb2.Token(val=refresh_token))
        )
        self._access_token = token.val

    def _get_access_token(self):
        return self._access_token

    def launch_job(self, project, scenario, job) -> str:
        return str(
            self._job_manager.StartJob(
                spm_pb2.Job(
                    project_id=project,
                    scenario_id=scenario,
                    job_id=job,
                    user_id=self._user,
                    organization_id=self._organization,
                )
            ).execution_id
        )

    def terminate_job(self, project, scenario, job):
        self._job_manager.TerminateJob(
            spm_pb2.Job(
                project_id=project,
                scenario_id=scenario,
                job_id=job,
                user_id=self._user,
                organization_id=self._organization,
            )
        )

    def reset_job(self, project, scenario, job):
        self._job_manager.ResetJob(
            spm_pb2.Job(
                project_id=project,
                scenario_id=scenario,
                job_id=job,
                user_id=self._user,
                organization_id=self._organization,
            )
        )

    def update_execution(self, update_):
        self._base_client.UpdateExecution(spm_pb2.Json(json=json.dumps(update_)))

    def get_execution_status(self, exe_id):
        return self._job_manager.GetExecutionStatus(
            spm_pb2.ExecutionId(execution_id=exe_id)
        ).json

    def clear_execution(self, scenario, execution):
        self._base_client.ClearExecutionMemory(
            spm_pb2.Scenario(scenario=scenario, execution=execution)
        )

    def remove_data_execution(self, scenario, execution):
        self._base_client.RemoveExecutionData(
            spm_pb2.Scenario(scenario=scenario, execution=execution)
        )

    def remove_execution(self, scenario, execution):
        self.remove_data_execution(scenario, execution)
        self.remove_execution_schedule(execution)

    def delete_execution(self, exe_id):
        self._job_manager.DeleteExecution(spm_pb2.ExecutionId(execution_id=exe_id))

    def update_job_by_backend(
        self, project, scenario, job, exe, message, status, log=None, complete=False
    ):
        self._base_client.SetScenarioProgress(
            spm_pb2.ScenarioProgress(
                project=project,
                scenario=scenario,
                job_id=job,
                message=message,
                status=status,
                progress=0,
            )
        )

        if log is not None:
            self._base_client.PushExecutionLogEntries(
                spm_pb2.LogEntries(
                    scenario=scenario,
                    execution_id=exe,
                    log_entries=[log],
                    timestamps=[datetime.utcnow().timestamp()],
                )
            )

        if complete:
            self._base_client.CompleteExecutionIgnoreInstance(
                spm_pb2.ExecutionMessage(
                    project_id=project,
                    scenario_id=scenario,
                    job_id=job,
                    execution_id=exe,
                )
            )

        return spm_pb2.Empty()

    def read_execution_logs(self, execution_id, project_id):
        for log_entry in self._base_client.ReadExecutionLogEntries(
            spm_pb2.ExecutionReadLogs(
                execution_id=execution_id, project_id=project_id, start=0, end=0
            )
        ):
            yield log_entry.log_entry, datetime.fromtimestamp(log_entry.timestamp)

    def hibernate_job(self, project_id, scenario_id, job_id, organization_id, user_id):
        self._job_manager.HibernateJob(
            spm_pb2.Job(
                project_id=project_id,
                scenario_id=scenario_id,
                job_id=job_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )

    def resume_job(self, project_id, scenario_id, job_id, organization_id, user_id):
        self._job_manager.ResumeJob(
            spm_pb2.Job(
                project_id=project_id,
                scenario_id=scenario_id,
                job_id=job_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )

    def add_job_schedule(
        self,
        project_id,
        scenario_id,
        job_id,
        organization_id,
        user_id,
        sleep_after,
        sleep_for,
        enable_scheduling,
    ):
        # TODO: check schedule attributes
        self._job_manager.AddJobSchedule(
            spm_pb2.JobSchedule(
                job=spm_pb2.Job(
                    project_id=project_id,
                    scenario_id=scenario_id,
                    job_id=job_id,
                    organization_id=organization_id,
                    user_id=user_id,
                ),
                schedule=spm_pb2.Schedule(
                    sleep_after=sleep_after,
                    sleep_for=sleep_for,
                    enable_scheduling=enable_scheduling,
                ),
            )
        )

    def update_job_schedule(
        self,
        project_id,
        scenario_id,
        job_id,
        organization_id,
        user_id,
        sleep_after,
        sleep_for,
        enable_scheduling,
    ):
        self._job_manager.AddJobSchedule(
            spm_pb2.JobSchedule(
                job=spm_pb2.Job(
                    project_id=project_id,
                    scenario_id=scenario_id,
                    job_id=job_id,
                    organization_id=organization_id,
                    user_id=user_id,
                ),
                schedule=spm_pb2.Schedule(
                    sleep_after=sleep_after,
                    sleep_for=sleep_for,
                    enable_scheduling=enable_scheduling,
                ),
            )
        )

    def remove_job_schedule(
        self, project_id, scenario_id, job_id, organization_id, user_id
    ):
        self._job_manager.RemoveJobSchedule(
            spm_pb2.Job(
                project_id=project_id,
                scenario_id=scenario_id,
                job_id=job_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )

    def get_job_schedule(
        self, project_id, scenario_id, job_id, organization_id, user_id
    ):
        return self._job_manager.GetJobSchedule(
            spm_pb2.Job(
                project_id=project_id,
                scenario_id=scenario_id,
                job_id=job_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )

    def add_execution_schedule(
        self, execution_id, sleep_after, sleep_for, enable_scheduling
    ):
        self._job_manager.AddExecutionSchedule(
            spm_pb2.ExecutionAndSchedule(
                execution=spm_pb2.ExecutionId(execution_id=execution_id),
                schedule=spm_pb2.Schedule(
                    sleep_after=sleep_after,
                    sleep_for=sleep_for,
                    enable_scheduling=enable_scheduling,
                ),
            )
        )

    def update_execution_schedule(
        self, execution_id, sleep_after, sleep_for, enable_scheduling
    ):
        self._job_manager.UpdateExecutionSchedule(
            spm_pb2.ExecutionAndSchedule(
                execution=spm_pb2.ExecutionId(execution_id=execution_id),
                schedule=spm_pb2.Schedule(
                    sleep_after=sleep_after,
                    sleep_for=sleep_for,
                    enable_scheduling=enable_scheduling,
                ),
            )
        )

    def remove_execution_schedule(self, execution_id):
        self._job_manager.RemoveExecutionSchedule(
            spm_pb2.ExecutionId(execution_id=execution_id)
        )

    def get_execution_schedule(self, execution_id):
        return self._job_manager.GetExecutionSchedule(
            spm_pb2.ExecutionId(execution_id=execution_id)
        )

    def generate_scenario_token(
        self,
        project,
        scenario,
        job,
        user_id,
        organization_id,
        agent,
        purpose,
        admin=False,
    ):
        token = self._token_manager.CreateRefreshToken(
            spm_pb2.TokenRequest(
                project_id=project,
                scenario_id=scenario,
                job_id=job,
                user_id=user_id,
                organization_id=organization_id,
                agent=agent,
                purpose=purpose,
                admin=admin,
            )
        ).val

        return token

    def enqueue_build(self, repository, commit_id, launch_after_build=False, tags=None):
        resp = self._build_manager.LaunchBuild(
            spm_pb2.BuildRequest(
                repository=repository,
                commit_id=commit_id,
                launch_after_build=launch_after_build,
                tags=tags,
            )
        )
        return resp.build_id

    def update_scenario_image(
        self,
        name,
        path,
        project,
        scenario,
        job,
        repository,
        commit,
        build,
        internal=True,
    ):
        self._build_manager.UpdateJobImageReference(
            spm_pb2.JobImageReferenceUpdate(
                project=project,
                scenario=scenario,
                job=job,
                name=name,
                path=path,
                repository=repository,
                commit_id=commit,
                internal=internal,
                build=build,
            )
        )

    def update_build(self, repository, build_id, **update):
        self._build_manager.UpdateBuild(
            spm_pb2.BuildUpdate(
                repository=repository, build_id=build_id, update=json.dumps(update)
            )
        )

    def get_build_info(self, repository, build_id):
        response = self._build_manager.GetBuildInfo(
            spm_pb2.BuildInfoRequest(repository=repository, build_id=build_id)
        )
        return json.loads(response.info)

    def push_scenario_logs_admin(self, logs, exe_id):
        timestamps = [log_entries[0].timestamp() for log_entries in logs]

        self._base_client.PushExecutionLogEntries(
            spm_pb2.LogEntries(
                scenario="",
                execution_id=exe_id,
                log_entries=[log_entries[1] for log_entries in logs],
                timestamps=timestamps,
            )
        )

    def delete_system(self, system):
        self._base_client.DeleteSystem(spm_pb2.SystemRequest(system=system))

    def delete_user(self, user):
        self._base_client.DeleteUser(spm_pb2.UserRequest(user=user))

    def complete_signup(self, invitationID, firstName, lastName, organization):
        self._base_client.CompleteUserSignup(
            spm_pb2.SignupData(
                invitationID=invitationID,
                firstName=firstName,
                lastName=lastName,
                organization=organization,
            )
        )

    def login_get_refresh(self, email, password):
        return self._token_manager.LoginGetRefreshToken(
            spm_pb2.LoginCredentials(
                email=email,
                password=password,
                token_request=spm_pb2.TokenRequest(
                    project_id="ssfsdf",
                    scenario_id="sdffd",
                    admin=True,
                    execution_id="sdsfd",
                    job_id="sfdsdf",
                    user_id="sfsdfsdfsdf",
                    organization_id="sdfsfd",
                    access_level=4,
                ),
            )
        )

    def check_health(self):
        response = self._health.Check(health_pb2.HealthCheckRequest(service=""))
        return response.status == health_pb2.HealthCheckResponse.ServingStatus.SERVING

    def close(self):
        self.channel.close()
        self._access_token_refresher.stop()


@contextmanager
def open_admin_client(
    server: Optional[str] = None,
    port: Optional[int] = None,
    secure: Optional[bool] = None,
    refresh_token: Optional[str] = None,
) -> Generator[NumerousAdminClient, None, None]:
    numerous_client_ = NumerousAdminClient(
        server=server, port=port, secure=secure, refresh_token=refresh_token
    )

    try:
        yield numerous_client_

    finally:
        numerous_client_.close()
