import contextlib
import logging
import logging.handlers
import multiprocessing

from python_sdk.log._config import LogConfig


class RotatingFile(logging.handlers.QueueHandler):
    TYPE: str = "ROTATING_FILE"

    def __init__(self) -> None:
        # For this to support multiprocessing, logs will flow:
        # processes -> queue -> queue-handler -> queue-listener.

        # Create the queue where logs will be stored.
        self.queue: multiprocessing.Queue[logging.LogRecord] = multiprocessing.Queue(-1)

        # Initialize self, the QueueHandler, which places logs into the queue
        super().__init__(queue=self.queue)

        # Create the rotating file where the logs will be stored.
        self.rotating_file = logging.handlers.RotatingFileHandler(
            filename=LogConfig.DESTINATION_ROTATING_FILE_PATH,
            mode="a",
            maxBytes=LogConfig.DESTINATION_ROTATING_FILE_MAX_SIZE_BYTES,
            backupCount=LogConfig.DESTINATION_ROTATING_FILE_MAX_NUMBER_OF_FILES,
            encoding="utf-8",
            delay=False,
            errors=None,
        )

        # Initialize a QueueListener, which will take logs from the queue, and pass them onto the RotatingFileHandler.
        self.queue_listener = logging.handlers.QueueListener(self.queue, self.rotating_file, respect_handler_level=True)
        self.queue_listener.start()

    def setFormatter(self, fmt: logging.Formatter | None) -> None:
        return self.rotating_file.setFormatter(fmt=fmt)

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self.queue_listener.stop()
        with contextlib.suppress(Exception):
            self.queue.close()
