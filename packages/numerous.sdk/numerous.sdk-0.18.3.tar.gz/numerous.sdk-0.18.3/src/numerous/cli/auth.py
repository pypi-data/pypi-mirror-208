from getpass import getpass
from typing import Optional, Tuple

import grpc
from numerous.tokens import AccessLevel
from spm_pb2 import AuthenticateUserRequest, RefreshUserRequest, TokenRequest
from spm_pb2_grpc import TokenManagerStub

from .repository import NumerousRepository
from .utils import bold, get_token_manager, yellow


class AuthenticationError(Exception):
    pass


class IdTokenAuth(grpc.AuthMetadataPlugin):
    def __init__(self, id_token: str):
        self._id_token = id_token

    def __call__(
        self,
        _context: grpc.AuthMetadataContext,
        callback: grpc.AuthMetadataPluginCallback,
    ):
        callback([("authorization", self._id_token)], None)


def authenticate_user(
    token_manager: TokenManagerStub, email: str, password: str
) -> Tuple[str, str]:
    request = AuthenticateUserRequest(email=email, password=password)
    try:
        response = token_manager.AuthenticateUser(request)
        return response.id_token, response.refresh_token
    except grpc.RpcError:
        raise AuthenticationError()


def refresh_user(
    token_manager: TokenManagerStub, refresh_token: str
) -> Tuple[str, str, str]:
    request = RefreshUserRequest(refresh_token=refresh_token)
    try:
        response = token_manager.RefreshUser(request)
        return response.id_token, response.refresh_token, response.user_id
    except grpc.RpcError:
        raise AuthenticationError()


def get_refresh_token(repo: NumerousRepository, execution_id: str) -> str:
    if repo.remote is None:
        raise RuntimeError("Repository remote not defined")

    if repo.scenario is None:
        raise RuntimeError("Repository scenario is not defined")

    with get_token_manager(repo.remote.api_url) as token_manager:
        if repo.refresh_token is None:
            raise RuntimeError("Repository has no refresh token, use: numerous login")
        id_token, _, user_id = refresh_user(token_manager, repo.refresh_token)
        call_credentials = grpc.metadata_call_credentials(IdTokenAuth(id_token))
        request = TokenRequest(
            project_id=repo.scenario.project_id,
            scenario_id=repo.scenario.id,
            admin=False,
            execution_id=execution_id,
            job_id=repo.remote.job_id,
            access_level=AccessLevel.WRITE.value,
            user_id=user_id,
        )
        response, _ = token_manager.CreateRefreshToken.with_call(
            request, credentials=call_credentials
        )
        return str(response.val)


def get_id_token(api_url: str, refresh_token: str) -> str:
    with get_token_manager(api_url) as token_manager:
        return refresh_user(token_manager, refresh_token)[0]


def login(repo: NumerousRepository) -> str:
    if not repo.remote:
        raise AuthenticationError("No remote configured")

    id_token: Optional[str] = None

    with get_token_manager(repo.remote.api_url) as token_manager:
        if repo.refresh_token:
            try:
                id_token, refresh_token, user_id = refresh_user(
                    token_manager, repo.refresh_token
                )
                repo.user = user_id
            except AuthenticationError:
                pass

        if id_token is None:
            print(yellow(f"Login to {bold(repo.remote)}"))
            email = input("Email: ")  # nosec
            password = getpass("Password: ")
            id_token, refresh_token = authenticate_user(token_manager, email, password)

    repo.refresh_token = refresh_token
    repo.save()

    return id_token
