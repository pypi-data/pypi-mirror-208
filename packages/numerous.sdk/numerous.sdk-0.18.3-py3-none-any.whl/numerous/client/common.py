import logging
import threading
from collections import deque
from enum import Enum
from time import time
from typing import Callable, Iterator, Optional, Union
from urllib.parse import urlparse

import grpc
from numerous.client_common.validation_interceptor import ValidationInterceptor

from . import config
from .config import GRPC_MAX_MESSAGE_SIZE

log = logging.getLogger("numerous.client")


class Interp(Enum):
    zero = 0
    linear = 1
    quadratic = 2


class JobStatus(Enum):
    ready = 0
    running = 1
    finished = 2
    request_termination = 3
    terminated = 4
    failed = 5
    requested = 6
    initializing = 7


class RepeatedFunction:
    def __init__(self, interval, function, run_initially=False, *args, **kwargs):
        self._timer: Optional[threading.Timer] = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time()

        if run_initially:
            self.function(*self.args, **self.kwargs)

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
        self.is_running = False


class RestorableIterator(Iterator):
    """
    Returns items not handled items again after restore.
    >>> restorable_iterator = RestorableIterator(iter(range(4)))
    >>> assert list(restorable_iterator) == [0, 1, 2, 3]
    >>> restorable_iterator.restore()
    >>> assert list(restorable_iterator) == [0, 1, 2, 3]
    >>> restorable_iterator.restore()
    >>> assert list(next(restorable_iterator) for i in range(3)) == [0, 1, 2]
    >>> restorable_iterator.item_handled()
    >>> restorable_iterator.item_handled()
    >>> restorable_iterator.restore()
    >>> assert list(restorable_iterator) == [2, 3]
    >>> restorable_iterator.item_handled()
    >>> restorable_iterator.restore()
    >>> assert list(restorable_iterator) == [3]
    >>> assert list(restorable_iterator) == []
    """

    def __init__(self, data: Iterator):
        self._not_handled: deque = deque()
        self._restored_data: deque = deque()
        self._data = data
        self._lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            next_item = (
                self._restored_data.popleft()
                if self._restored_data
                else next(self._data)
            )
            self._not_handled.append(next_item)
            return next_item

    def item_handled(self):
        with self._lock:
            self._not_handled.popleft()

    def restore(self):
        with self._lock:
            self._restored_data = self._not_handled + self._restored_data
            self._not_handled = deque()


def initialize_grpc_channel(
    refresh_token: str,
    token_callback: Callable[[], str],
    server: Optional[str] = None,
    port: Optional[int] = None,
    secure: Optional[bool] = None,
    instance_id: Optional[str] = None,
):
    secure_channel = secure if secure is not None else not config.FORCE_INSECURE
    if secure_channel is None:
        raise RuntimeError("Secure channel must be specified")
    server = server or config.NUMEROUS_API_SERVER
    if server is None:
        raise RuntimeError("Server must be specified")
    port = port or config.NUMEROUS_API_PORT
    if port is None:
        raise RuntimeError("Port must be specified")

    log.debug("Initializing gRPC channel %s:%s", server, port)

    options = [
        ("grpc.max_message_length", GRPC_MAX_MESSAGE_SIZE),
        ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_SIZE),
        ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_SIZE),
    ]

    if secure_channel:
        creds = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(f"{server}:{port}", creds, options)
    else:
        channel = grpc.insecure_channel(f"{server}:{port}", options)

    vi = ValidationInterceptor(
        token=refresh_token, token_callback=token_callback, instance=instance_id
    )
    channel = grpc.intercept_channel(channel, vi)
    return channel, vi.instance


def parse_api_url(url: str):
    parsed_url = urlparse(url)
    server = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    secure = parsed_url.scheme == "https"
    return server, port, secure


class InterpolationOutOfRangeError(Exception):
    def __init__(self, min_: float, max_: float, values: list[float]):
        oor_values = [value for value in values if value < min_ or value > max_]
        message = f"{oor_values} out of range [{min_}-{max_}]"
        super().__init__(message)


DataValue = Union[int, float]
DataList = list[DataValue]


def inrange(x: DataList):
    def outer(fun: Callable[[DataList], DataList]):
        def inner(x_data: Union[DataList, DataValue]) -> list[float]:
            if isinstance(x_data, (int, float)):
                x_data = [float(x_data)]
            if any(min(x) > x_elem or max(x) < x_elem for x_elem in x_data):
                raise InterpolationOutOfRangeError(min(x), max(x), x_data)
            return fun(x_data)

        return inner

    return outer


def interp_zero(
    x: DataList,
    y: DataList,
    x_data: DataList,
) -> DataList:
    return [y[_get_source_index(x, x_data_elem)] for x_data_elem in x_data]


def _get_source_index(
    x: DataList,
    x_data_elem: DataValue,
):
    return [i for i, x_source_elem in enumerate(x) if x_source_elem <= x_data_elem][-1]


def interp_linear_coefficients(
    x: DataList,
    y: DataList,
) -> tuple[float, float]:
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)

    ss_xy = sum((x_elem - x_mean) * (y_elem - y_mean) for x_elem, y_elem in zip(x, y))
    ss_xx = sum((x_elem - x_mean) ** 2 for x_elem in x)

    b1 = ss_xy / ss_xx
    b0 = y_mean - b1 * x_mean

    return b0, b1


def interp_linear(
    b0: float,
    b1: float,
    x_data: DataList,
) -> list:
    return [b1 * x_elem + b0 for x_elem in x_data]


def interp1d(
    x: DataList,
    y: DataList,
    kind: str = "zero",
) -> Callable[[Union[DataList, DataValue]], DataList]:
    if len(x) != len(y):
        raise ValueError("lengths of vectors must match")

    if kind == "zero":

        @inrange(x)
        def wrapper_zero(xi: DataList):
            return interp_zero(x, y, xi)

        return wrapper_zero
    elif kind == "linear":
        b0, b1 = interp_linear_coefficients(x, y)

        @inrange(x)
        def wrapper_linear(xi: list[Union[int, float]]):
            return interp_linear(b0, b1, xi)

        return wrapper_linear

    else:
        raise NotImplementedError(f"method {kind} not implemented")
