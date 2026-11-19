import atexit
import copy
import json
import logging
import os
import queue
import socket
import urllib.request
from logging.handlers import QueueHandler, QueueListener

DEFAULT_LOKI_URL = "http://2.27.44.99:3100"
PUSH_PATH = "/loki/api/v1/push"


def loki_push_url() -> str:
    url = os.getenv("LOKI_URL", DEFAULT_LOKI_URL).rstrip("/")
    if url.endswith(PUSH_PATH):
        return url
    return f"{url}{PUSH_PATH}"


class LokiEmitHandler(logging.Handler):
    """Отправляет одну запись в Loki. Ошибка доставки не роняет приложение."""

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url
        self.labels = {
            "app": "server-time",
            "host": socket.gethostname(),
        }
        self._last_ts = 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [[self._timestamp(record), self.format(record)]],
                    }
                ]
            }
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            request = urllib.request.Request(
                self.url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=2) as response:
                response.read()
        except Exception:
            return

    def _timestamp(self, record: logging.LogRecord) -> str:
        timestamp = int(record.created * 1_000_000_000)
        if timestamp <= self._last_ts:
            timestamp = self._last_ts + 1
        self._last_ts = timestamp
        return str(timestamp)


class LokiQueueHandler(QueueHandler):
    """Кладёт логи в очередь, чтобы запрос к Loki не задерживал приложение."""

    def __init__(self) -> None:
        log_queue: queue.Queue[logging.LogRecord] = queue.Queue(maxsize=10_000)
        super().__init__(log_queue)
        self._emitter = LokiEmitHandler(loki_push_url())
        self._listener = QueueListener(log_queue, self._emitter)
        self._listener.start()
        self._stopped = False
        atexit.register(self._shutdown)

    def setFormatter(self, fmt: logging.Formatter) -> None:
        self._emitter.setFormatter(fmt)

    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        return copy.copy(record)

    def enqueue(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            return

    def _shutdown(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._listener.stop()

    def close(self) -> None:
        try:
            self._shutdown()
        finally:
            super().close()


LOG_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "loki": {
            "()": LokiQueueHandler,
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console", "loki"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["console", "loki"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "loki"],
        "level": "INFO",
    },
}
