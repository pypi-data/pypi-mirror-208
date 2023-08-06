from time import sleep
from typing import Callable, Generator, Generic, Iterable, Optional, TypeVar

RequestType = TypeVar("RequestType")
ResponseType = TypeVar("ResponseType")


class RequestResponseStream(Generic[RequestType, ResponseType]):
    """A helper class for wrapping Stream-Stream gRPCs."""

    def __init__(
        self,
        stream_endpoint: Callable[
            [Iterable[RequestType]], Generator[ResponseType, None, None]
        ],
        check_interval_secs: float = 0.1,
    ):
        """Initialize the :class:`RequestResponseStream`.

        :param stream_endpoint: The endpoint the :class:`RequestResponseStream` should wrap.
        :param check_interval_secs: The time interval in seconds, for checking whether
        the current request is sent, or the :class:`RequestResponseStream` is closed.
        """
        self._check_interval = check_interval_secs
        self._request: Optional[RequestType] = None
        self._closed: bool = False
        self._response_iterator = stream_endpoint(self)

    def _await_request_sent(self):
        while self._request is not None:
            sleep(self._check_interval)

    def send(self, request: RequestType) -> ResponseType:
        """Sends a request after waiting for the previous request to have been sent, if
        there is one.

        :param request: The request to send.
        :return: The response.
        """
        self._await_request_sent()
        self._request = request
        return next(self._response_iterator)

    def close(self) -> None:
        """Close the :class:`RequestResponseStream` blocking until any outstanding
        request has been delivered.
        """
        self._await_request_sent()
        self._request = None
        self._closed = True

    def __iter__(self) -> "RequestResponseStream[RequestType, ResponseType]":
        return self

    def __next__(self) -> RequestType:
        while not self._closed and self._request is None:
            sleep(self._check_interval)

        if self._closed:
            raise StopIteration()
        else:
            request = self._request
            self._request = None
            return request  # type: ignore[return-value]
