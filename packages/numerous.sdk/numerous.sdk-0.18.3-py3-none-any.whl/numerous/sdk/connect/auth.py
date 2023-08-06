"""Authorization and authentication related functionality."""

import grpc


class AccessTokenAuthMetadataPlugin(grpc.AuthMetadataPlugin):
    """Implements access-token based authorization for a gRPC channel."""

    def __init__(self, access_token: str):
        self._access_token = access_token

    def __call__(
        self,
        context: grpc.AuthMetadataContext,  # noqa: F841
        callback: grpc.AuthMetadataPluginCallback,
    ):
        callback([("token", self._access_token)], None)

    def __eq__(self, other):
        if isinstance(other, AccessTokenAuthMetadataPlugin):
            return other._access_token == self._access_token
        else:
            return False
