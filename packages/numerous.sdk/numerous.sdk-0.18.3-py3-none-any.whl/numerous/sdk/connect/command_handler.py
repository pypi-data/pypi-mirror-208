import signal
import threading

from numerous.sdk.connect.subscription import Subscription


class CommandHandler:
    def __init__(self, subscription: Subscription):
        self._subscription = subscription
        self._thread = threading.Thread(target=self._handler, daemon=True)
        self._thread.start()

    def _handler(self):
        for message in self._subscription:
            command = message.message["command"]
            if command == "terminate":
                signal.raise_signal(signal.SIGTERM)
                return
