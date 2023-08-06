from .numerous_admin_client import NumerousAdminClient, open_admin_client
from .numerous_client import (
    DataSourcesReader,
    DataStreamTimeoutBreakStatus,
    NumerousClient,
    ScenarioStatus,
    open_client,
)


def _setup_runtime():
    import signal
    import sys

    import urllib3

    from numerous.client.common import log

    urllib3.disable_warnings()

    def handle_term(_signum, _frame):
        log.warning("Terminated")
        sys.exit()

    signal.signal(signal.SIGINT, handle_term)
    signal.signal(signal.SIGTERM, handle_term)


_setup_runtime()


__all__ = (
    "DataSourcesReader",
    "NumerousClient",
    "open_client",
    "NumerousAdminClient",
    "open_admin_client",
    "ScenarioStatus",
    "DataStreamTimeoutBreakStatus",
)
