from logging import config
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any


class QueueListenerHandler(QueueHandler):
    def __init__(
        self,
        handlers: list[Any],
        respect_handler_level: bool = False,
        queue: Queue[str] = Queue(-1),
    ):
        super().__init__(queue)
        self.handlers = self._resolve_handlers(handlers)
        self._listener: QueueListener = QueueListener(
            self.queue, *self.handlers, respect_handler_level=respect_handler_level
        )
        self._listener.start()

    def _resolve_handlers(self, handlers: list[Any]) -> list[Any]:
        return [handlers[i] for i in range(len(handlers))]


def setup_logging(logger_name: str, log_level: str):
    config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "standard": {
                    "format": (
                        "{asctime}.{msecs:0<3.0f} | {levelname: <8} | {name: <15} "
                        "| {filename}:{funcName}:{lineno} - {message}"
                    ),
                    "datefmt": "%y.%m.%d-%H:%M:%S",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                },
                "queue_listener": {
                    "class": f"{__name__}.QueueListenerHandler",
                    "handlers": ["cfg://handlers.console"],
                },
            },
            "root": {"handlers": ["queue_listener"], "level": "DEBUG"},
            "loggers": {
                logger_name: {"level": log_level, "propagate": True},
                "uvicorn": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": ["queue_listener"],
                },
            },
        }
    )
