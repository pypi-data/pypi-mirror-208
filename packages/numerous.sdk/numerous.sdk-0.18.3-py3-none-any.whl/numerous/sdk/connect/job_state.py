"""Contains the implementation of the JobState class, for managing job execution state."""

import json
from typing import Any, Optional, Union

from numerous.client_common.grpc_retry import grpc_retry_unary
from spm_pb2 import ScenarioCustomMetaData
from spm_pb2_grpc import SPMStub

from numerous.sdk.connect.job_utils import JobIdentifier


class JobState:
    """JobState enables jobs to store state remotely, and cache it locally. This is useful for keeping track of values
    across hibernations, or if an error has restarted the job.
    """

    def __init__(
        self,
        spm_client: SPMStub,
        identity: JobIdentifier,
        execution_id: str,
    ) -> None:
        """Initializes the JobState.

        :param spm_client:
        :param identity: The identitiers for the job and related objects.
        """
        self._spm_client = spm_client
        self._identity = identity
        self._execution_id = execution_id
        self._state = self._load()

    def get(self, key: str, default: Optional[Any] = None) -> Union[Any, Any]:
        """Get the state value keyed by :paramref:`key` from the :class:`JobState`.

        :param key: The key to look up in the state.
        :param default: A default value to return if the key does not exist.
        :return: The state value at the :paramref:`key` if it exists, otherwise the
            :paramref:`default`, or `None` if no default is specified.
        """
        return self._state.get(key, default)

    def set(self, key: str, value: Any, commit: bool = True) -> None:
        """Set the state value keyed by :paramref:`key` to the value :paramref:`value`
        in the :class:`JobState`, and optionally commit the state to the server.

        If :paramref:`commit` is `True` the new state resulting from setting the value,
        will be comitted to the server.

        :param key: The key to set in the state.
        :param value: The value to set.
        :param commit: Whether or not to commit the resulting state to the server.
        """
        self._state[key] = value

        if commit:
            self._commit()

    def unset(self, key: str, commit: bool = True) -> None:
        """Unset the state value keyed by :paramref:`key` in the :class:`JobState`, and
        optionally commit the state to the server.

        If :paramref:`commit` is `True` the new state resulting from unsetting the
        value, will be comitted to the server.

        :param key: The key to unset in the state.
        :param commit: Whether or not to commit the resulting state to the server.
        """
        if key in self._state:
            del self._state[key]

        if commit:
            self._commit()

    @grpc_retry_unary()
    def _load(self) -> dict[str, Any]:
        try:
            state = json.loads(
                self._spm_client.GetScenarioCustomMetaData(
                    ScenarioCustomMetaData(
                        project=self._identity.project_id,
                        scenario=self._identity.scenario_id,
                        execution=self._execution_id,
                        key=f"{self._identity.job_id}.state",
                    )
                ).meta
            )
        except json.decoder.JSONDecodeError:
            state = {}

        if isinstance(state, dict):
            return state
        else:
            return {}

    @grpc_retry_unary()
    def _commit(self) -> None:
        self._spm_client.SetScenarioCustomMetaData(
            ScenarioCustomMetaData(
                project=self._identity.project_id,
                scenario=self._identity.scenario_id,
                execution=self._execution_id,
                key=f"{self._identity.job_id}.state",
                meta=json.dumps(self._state),
            )
        )
