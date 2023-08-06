"""Functionality related to writing data series and the :class:`Writer`."""


import sys
from collections import defaultdict
from typing import Any, Callable, Generator, Iterable, Optional

import spm_pb2
import spm_pb2_grpc

from numerous.sdk.connect.job_utils import JobIdentifier
from numerous.sdk.connect.request_response_stream import RequestResponseStream

FLOAT_SIZE = sys.getsizeof(float())


class TagsNotAllowed(Exception):
    """An error raised when written tags are invalid according to the data series."""

    def __init__(self, tags: Iterable[str]):
        """Initialize the error.

        :param tags: The unallowed tags which triggered the error.
        """
        self.tags = tags

    def __eq__(self, __o: object) -> bool:  # pragma: no cover
        return isinstance(__o, TagsNotAllowed) and __o.tags == self.tags


def _default_tag(name: str):
    return spm_pb2.Tag(
        name=name,
        type="double",
        scaling=1,
        offset=0,
    )


class Writer:
    """The :class:`Writer` enables writing rows and series to the server.
    It manages a buffer, which is automatically flushed when it is full.
    """

    def __init__(
        self,
        spm_stub: spm_pb2_grpc.SPMStub,
        job_identity: JobIdentifier,
        execution_id: str,
        max_size_bytes: int,
        flush_margin_bytes: int,
    ):
        """Initialize the writer.

        :param spm_stub: The client.
        :param job_identity: The identity of the job, the :class:`Writer` is writing for.
        :param execution_id: The ID of the execution, the :class:`Writer` is writing for.
        :param max_size_bytes: The maximum buffer size of the :class:`Writer` in bytes.
        :param flush_margin_bytes: The margin that is subtracted the
        :paramref:`max_size_bytes` to determine if flushing should be performed.
        """
        self._spm_stub = spm_stub
        self._job_identity = job_identity
        self._execution_id = execution_id
        self._buffer_index: list[float] = []
        self._buffer: dict[str, list[float]] = defaultdict(list)
        self._max_size_bytes = max_size_bytes
        self._flush_margin_bytes = flush_margin_bytes
        self._size_bytes: int = 0
        write_data_stream: Callable[
            [Iterable[spm_pb2.WriteDataStreamRequest]],
            Generator[spm_pb2.WriteDataStreamResponse, None, None],
        ] = spm_stub.WriteDataStream
        self._stream = RequestResponseStream(write_data_stream)
        self._allowed_tags: Optional[set[str]] = None

    def _get_allowed_tags(self) -> Optional[set[str]]:
        if self._allowed_tags is not None:
            return self._allowed_tags

        metadata = self._spm_stub.GetScenarioMetaData(
            spm_pb2.Scenario(
                project=self._job_identity.project_id,
                scenario=self._job_identity.scenario_id,
                execution=self._execution_id,
            )
        )
        if metadata.tags:
            self._allowed_tags = {tag.name for tag in metadata.tags}
            return self._allowed_tags
        else:
            return None

    def _get_unallowed_tags(
        self, data: dict[str, Any], tags: Iterable[str]
    ) -> set[str]:
        return set(data.keys()).difference(tags)

    def _header_size(self, tags: Iterable[str]) -> int:
        if self._size_bytes == 0:
            return sum(sys.getsizeof(tag) for tag in tags)
        else:
            return 0

    def _list_size(self, data: list[float]) -> int:
        return FLOAT_SIZE * len(data)

    def _row_and_index_size(self, data: dict[str, float]) -> int:
        return FLOAT_SIZE + FLOAT_SIZE * len(data)

    def _series_size(self, index: list[float], data: dict[str, list[float]]) -> int:
        return self._list_size(index) + sum(
            (self._list_size(values) for values in data.values())
        )

    def _must_flush_before_adding(self, added_size_bytes: int) -> bool:
        return (
            added_size_bytes + self._size_bytes + self._flush_margin_bytes
            >= self._max_size_bytes
        )

    def _set_allowed_tags(self, data: dict[str, Any]) -> None:
        self._allowed_tags = set(data.keys())
        self._spm_stub.SetScenarioMetaData(
            spm_pb2.ScenarioMetaData(tags=[_default_tag(tag) for tag in data.keys()])
        )

    def _check_tags(self, data: dict[str, Any]):
        if (tags := self._get_allowed_tags()) is None:
            self._set_allowed_tags(data)
        elif unallowed_tags := self._get_unallowed_tags(data, tags):
            raise TagsNotAllowed(unallowed_tags)

    def row(self, index: float, data: dict[str, float], flush: bool = False) -> None:
        """Write a row of data into the data series.

        Each row written to the :class:`Writer` must have same keys as previously
        written series or rows.

        :param index: The index value, typically the UNIX timestamp.
        :param data: The row of data to write into the data stream.
        :param flush: If true, will flush the buffer of the writer upon writing.
        :raises TagsNotAllowed: If tags that have not been previously written, are
            written.
        """
        self._check_tags(data)

        size_bytes = self._header_size(data) + self._row_and_index_size(data)
        if self._must_flush_before_adding(size_bytes):
            self.flush()

        for tag, value in data.items():
            self._buffer[tag].append(value)
        self._buffer_index.append(index)
        self._size_bytes += size_bytes

        if flush:
            self.flush()

    def series(
        self, index: list[float], data: dict[str, list[float]], flush: bool = False
    ) -> None:
        """Write a series of data to the data stream.

        Each series written to the :class:`Writer` must have same keys as previously
        written series or rows.

        :param index: The index value, typically the UNIX timestamp.
        :param data: The data series to write. The keys are validated against
            previously written keys.
        :param flush: If true, will flush the buffer of the writer upon writing.
        :raises TagsNotAllowed: If tags that have not been previously written, are
            written.
        """
        self._check_tags(data)

        size_bytes = self._header_size(data) + self._series_size(index, data)
        if self._must_flush_before_adding(size_bytes):
            self.flush()

        for key, value in data.items():
            self._buffer[key].extend(value)
        self._buffer_index.extend(index)
        self._size_bytes += size_bytes

        if flush:
            self.flush()

    def flush(self) -> None:
        """Flushes the buffer of the writer."""
        self._stream.send(
            spm_pb2.WriteDataStreamRequest(
                scenario=self._job_identity.scenario_id,
                execution=self._execution_id,
                overwrite=False,
                index=self._buffer_index,
                data={
                    tag: spm_pb2.StreamData(values=values)
                    for tag, values in self._buffer.items()
                },
                update_stats=True,
            )
        )
        self._buffer_index.clear()
        self._buffer.clear()
        self._size_bytes = 0

    def close(self):
        """Close the :class:`Writer`, flushing the buffer."""
        self.flush()
        self._stream.close()
