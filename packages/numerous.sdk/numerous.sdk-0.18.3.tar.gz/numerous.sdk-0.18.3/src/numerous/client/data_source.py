import enum
import threading
from datetime import datetime
from queue import Empty, Queue
from time import time
from typing import Any, Dict, List, Optional

from .common import Interp, interp1d, log


class DataSourceEmptyDataset(Exception):
    pass


class DataSourceHibernating(Exception):
    pass


class DataSourceCompleted(Exception):
    pass


class DataSourceStreamClosed(Exception):
    pass


class DataSourceStreamStarting(Exception):
    pass


class SourceStatus(enum.Enum):
    EMPTY_DATASET = 0
    HIBERNATING = 1
    COMPLETED = 2
    STREAM_CLOSED = 3
    OK = 4
    NO_DATA = 5
    STREAM_STARTING = 6


class StaticSource:
    def __init__(
        self, row_data, t0=0, t_end=None, dt=3600, generate_index=True  # noqa: F841
    ):
        self.row = row_data
        self.source_type = "static"
        self.t = float("inf")
        self.t0 = t0
        self.subscribe = False
        self.generate_index = generate_index

    def get_at_time(self, t):
        self.t = t
        self.row["_index"] = t
        self.row["_index_relative"] = t - self.t0
        return self.row


class DynamicSource:
    def __init__(
        self,
        client: Any,
        scenario,
        execution,
        spec,
        t0=0,
        te=0,
        timeout=None,
        source_type=None,
        interpolation_method=Interp.zero,
    ):
        self.timeout = timeout
        self.t0 = t0
        if te is None:
            te = 0
        self.te = te
        self.meta = client.get_timeseries_meta_data(
            scenario=scenario, execution=execution
        )
        self.closed = client.get_dataset_closed(scenario=scenario, execution=execution)
        self.name = scenario
        self.spec = spec
        self.spec["offset"] = self.spec["offset"] if "offset" in self.spec else 0

        # The offset set in spec is the full offset from 0 - not relative from meta.offset
        offset = self.spec["offset"]
        self.offset = offset
        self.execution = execution
        self.client = client

        # start time in original absolute time/input base time
        start = t0 - offset
        end = max(te - offset, 0)

        # If the data set is open, we will try to listen for data as its being generated if t end not reached.
        # This is stored in the state, to enable consistent behaviour across hibernation resumes
        subscribe = client.state.get(f"_{scenario}_{execution}_source_subscribe", None)
        if subscribe is None:
            subscribe = not self.closed
            client.state.set(f"_{scenario}_{execution}_source_subscribe", subscribe)
        self.subscribe = subscribe

        stats = client.get_timeseries_stats(None, scenario, execution)
        if stats.min + offset > t0:
            raise Exception(
                f"dynamic input scenario {scenario} with tags {[t.name for t in self.meta.tags]} "
                f"is offset to the future {stats.min + offset}>{t0}"
            )

        self.start = start
        self.end = end

        log.info("Scenario: %s", scenario)
        log.info("Scenario data is closed: %s", self.closed)
        log.info("Offset in spec: %s", datetime.fromtimestamp(spec["offset"]))
        log.info("Offset in meta: %s", datetime.fromtimestamp(self.meta.offset))
        log.info(
            "Data stats: %s",
            client.get_timeseries_stats(
                project=None, scenario=scenario, execution=execution
            ),
        )
        log.info("Combined offset: %s", datetime.fromtimestamp(offset))
        log.info("t0: %s", datetime.fromtimestamp(t0))
        log.info("te: %s", datetime.fromtimestamp(te))
        log.info("start: %s (%s)", datetime.fromtimestamp(start), start)
        log.info("end: %s (%s)", datetime.fromtimestamp(end), end)

        tags = set([s["tag"] for s in spec["tags"].values()])
        self.tags = tags

        self.generator = client.read_data_as_row(
            scenario=scenario,
            tags=tags,
            execution=execution,
            start=start,
            end=end,
            subscribe=self.subscribe,
            index_by_time=True,
        )
        self.source_type = source_type
        self.row_queue: Queue = Queue(100)
        self.t = -1
        self._rows_read = 0  # Keep a counter of rows read - if nothing is read we don't want to requery.
        self.row_buffer = RowBuffer(
            tags=[s for s in spec["tags"].keys()],
            offset=offset,
            method=interpolation_method,
        )
        # Keep the last/presumably max ix read on record - if in continuous mode this needs to be  added to the requery
        # as an offset.
        self.max_ix_read = 0
        self.last_get: Optional[float] = None
        self.status = SourceStatus.STREAM_STARTING

        def _next():
            complete = False
            lastdt = 0
            lastrow_index = None
            status = SourceStatus.STREAM_CLOSED

            while not complete:
                for row_ in self.generator:
                    if row_ == "HIBERNATE":
                        status = SourceStatus.HIBERNATING
                        break
                    elif row_ == "STOP":
                        status = SourceStatus.COMPLETED
                        break

                    self._rows_read += 1
                    self.row_queue.put(row_)
                    if lastrow_index is None:
                        lastrow_index = row_["_index"]
                    lastdt = row_["_index"] - lastrow_index
                    lastrow_index = row_["_index"]
                    self.max_ix_read = row_["_index"]

                log.debug(
                    "%s: All data read: %s of %d to %d, read n rows: %d",
                    scenario,
                    self.t - offset,
                    start,
                    end,
                    self._rows_read,
                )

                if self._rows_read <= 0:
                    # If nothing was returned the data source is empty and no use to requery.
                    log.debug(f"No data in {scenario}!")
                    self.row_queue.put("EMPTY")
                    return
                elif self.subscribe:
                    if status == SourceStatus.STREAM_CLOSED:
                        log.debug(
                            f"Subscribed data source {scenario} is active and not flagged hibernating, "
                            f"but is not streaming"
                        )
                        self.row_queue.put("CLOSED")
                    elif status == SourceStatus.COMPLETED:
                        log.debug(
                            f"Subscribed data source {scenario} has closed and stopped generating data"
                        )
                        self.row_queue.put("STOP")
                    elif status == SourceStatus.HIBERNATING:
                        log.debug(f"Subscribed data source {scenario} is hibernating")
                        self.row_queue.put("HIBERNATE")
                    return
                else:
                    # mode is continuous requry data and shift its _index to extend the current data
                    log.debug("Requerying data for " + scenario)
                    # TODO: Assess if we need to keep the query in memory instead of requery.
                    # Requery could lead to inconsistency perhaps? Data changed since last query?
                    self.generator = client.read_data_as_row(
                        tags=tags,
                        scenario=scenario,
                        execution=execution,
                        start=self.start,
                        end=self.end,
                        # We should never subscribe on requery
                        subscribe=False,
                        # Make sure to offset requeried _index so we extend the data. Shift by one estimated timestep
                        offset=self.max_ix_read + lastdt - self.start,
                    )

                if self.end > 0:
                    complete = self.max_ix_read >= self.end

            self.row_queue.put("STOP")

        threading.Thread(target=_next, daemon=True).start()

    def __next__(self):
        if self.status not in (SourceStatus.OK, SourceStatus.STREAM_STARTING):
            return self.status

        if self.last_get is None:
            self.last_get = time()
        try:
            row_ = self.row_queue.get(block=True, timeout=1)
            self.last_get = time()
        except Empty:
            row_ = None
            if self.timeout is not None and time() - self.last_get > self.timeout:
                log.debug("timeout")
                raise TimeoutError("Timed out!")

        if row_ == "STOP":
            log.debug("source consumed and no longer active")
            self.status = SourceStatus.COMPLETED
            return self.status
        elif row_ == "EMPTY":
            self.status = SourceStatus.EMPTY_DATASET
            log.debug("Source empty")
            return self.status
        elif row_ == "HIBERNATE":
            self.status = SourceStatus.HIBERNATING
            log.debug("Source is hibernating")
            return self.status
        elif row_ == "CLOSED":
            self.status = SourceStatus.STREAM_CLOSED
            log.debug("Source unexpectedly closed")
            return self.status
        elif row_ is None:
            if self.status != SourceStatus.STREAM_STARTING:
                self.status = SourceStatus.NO_DATA
            return self.status

        row = {}
        for tag, s in self.spec["tags"].items():
            try:
                row[tag] = row_[s["tag"]] * s["scale"] + s["offset"]
            except Exception:
                log.debug(str(row_))
                raise
        # substract meta.offset since read_as_row returns the data in input base time
        row["_index"] = row_["_index"] + self.offset
        row["_index_relative"] = row_["_index"] - self.t0
        row["_datetime_utc"] = datetime.utcfromtimestamp(row["_index"])
        self.t = row["_index"]
        self.row_buffer.add(row)
        return SourceStatus.OK

    # Get at simulation time
    def get_at_time(self, t):
        while self.t <= t or not self.row_buffer.full:
            status = self.__next__()
            if status != SourceStatus.OK:
                break

        if t > self.row_buffer.tmax():
            if self.status == SourceStatus.EMPTY_DATASET:
                raise DataSourceEmptyDataset(f"Data Source for {self.name} is empty.")
            elif self.status == SourceStatus.HIBERNATING:
                raise DataSourceHibernating(
                    f"Data Source for {self.name} is hibernating."
                )
            elif self.status == SourceStatus.COMPLETED:
                raise DataSourceCompleted(
                    f"Data Source for {self.name} has been consumed and is no longer active."
                )
            elif self.status == SourceStatus.STREAM_CLOSED:
                raise DataSourceStreamClosed(
                    f"Data Source for {self.name} closed it's stream unexpectedly."
                )
            elif self.status == SourceStatus.NO_DATA:
                return None
            elif self.status == SourceStatus.STREAM_STARTING:
                raise DataSourceStreamStarting(
                    f"Data Source for {self.name} is starting"
                )
            else:
                raise NotImplementedError(f"unhandled exception for {self.status}")
        else:
            return self.row_buffer.get(t)


class FIFO:
    def __init__(self, buffer_len: int = 2):
        self.buffer: Dict[str, List[float]] = {}
        self.buffer_len = buffer_len

    def _init_buffer(self, row):
        self.buffer = {tag: [0.0] * self.buffer_len for tag in row.keys()}

    def __len__(self):
        return len(self.buffer)

    def add(self, row):
        if len(self.buffer) == 0:
            self._init_buffer(row)

        for tag, val in row.items():
            self.buffer[tag].pop(0)
            self.buffer[tag].append(val)


class RowBuffer:
    def __init__(self, tags=None, offset=None, method=Interp.zero):
        self.tags = tags
        self.tags.append("_index")
        self.offset = offset
        self.method = method
        self.full = False
        self._rows = 0
        if method == Interp.zero:
            self.buffer_len = 2
        elif method == Interp.linear:
            self.buffer_len = 2
        else:
            raise NotImplementedError
        self._buffer = FIFO(self.buffer_len)

    def add(self, row):
        row_tags = {tag: row.get(tag) for tag in self.tags}
        self._buffer.add(row_tags)

        if self.full:
            return

        self._rows += 1
        if self._rows >= self.buffer_len:
            self.full = True

    def tmax(self):
        if "_index" in self._buffer.buffer:
            return max(self._buffer.buffer["_index"])
        else:
            return -1

    def get(self, t):
        tags = self.tags
        irow = {}
        if self.method == Interp.zero:
            for tag in tags[:-1]:
                ifun = interp1d(
                    self._buffer.buffer["_index"], self._buffer.buffer[tag], kind="zero"
                )
                irow.update({tag: ifun(t)[0]})
        elif self.method == Interp.linear:
            for tag in tags[:-1]:
                ifun = interp1d(
                    self._buffer.buffer["_index"],
                    self._buffer.buffer[tag],
                    kind="linear",
                )
                irow.update({tag: ifun(t)[0]})
        else:
            raise NotImplementedError("Unknown interpolation type")
        return irow


class InputManager:
    def __init__(self, sources, t, t0):
        self.sources = sources
        self.t = t
        self.t0 = t0

    def get_at_time(self, t):
        row = {}
        for source in self.sources:
            try:
                part_row = source.get_at_time(t)
                if part_row is None:
                    return None

            except TimeoutError as e:
                if source.subscribe:
                    return None
                else:
                    raise e
            row.update(part_row)
        # return simulation time
        row.update({"_index": t})
        return row
