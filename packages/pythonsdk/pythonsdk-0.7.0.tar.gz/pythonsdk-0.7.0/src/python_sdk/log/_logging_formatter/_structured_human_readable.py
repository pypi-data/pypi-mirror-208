import copy
import datetime
import io
import logging
import traceback
import types
import typing

import python_sdk


class StructuredHumanReadable:
    TYPE: str = "STRUCTURED_HUMAN_READABLE"

    include_current_log_filename: bool
    include_function_name: bool
    include_line_number: bool
    include_module_name: bool
    include_module_path: bool
    include_process_id: bool
    include_process_name: bool
    include_thread_id: bool
    include_thread_name: bool
    include_python_sdk_version: bool

    def __init__(
        self,
        include_current_log_filename: bool,
        include_function_name: bool,
        include_line_number: bool,
        include_module_name: bool,
        include_module_path: bool,
        include_process_id: bool,
        include_process_name: bool,
        include_thread_id: bool,
        include_thread_name: bool,
        include_python_sdk_version: bool,
    ) -> None:
        super().__init__()

        self.include_current_log_filename = include_current_log_filename
        self.include_function_name = include_function_name
        self.include_line_number = include_line_number
        self.include_module_name = include_module_name
        self.include_module_path = include_module_path
        self.include_process_id = include_process_id
        self.include_process_name = include_process_name
        self.include_thread_id = include_thread_id
        self.include_thread_name = include_thread_name
        self.include_python_sdk_version = include_python_sdk_version

    def pre_format(self, record: logging.LogRecord) -> dict[str, typing.Any]:
        timestamp = datetime.datetime.fromtimestamp(record.created).replace(tzinfo=datetime.timezone.utc)

        message = record.msg
        if record.args:
            message = record.msg % record.args
        message, embedded_context = self._yank_embedded_context_from_message(message=message)

        setattr(record, "context", getattr(record, "context", {}) | embedded_context)

        data = {"log_level": record.levelname, "message": message, "timestamp": timestamp}
        if self.include_current_log_filename:
            data["filename"] = record.filename
        if self.include_function_name:
            data["function_name"] = record.funcName
        if self.include_line_number:
            data["line_number"] = record.lineno
        if self.include_module_name:
            data["module_name"] = record.module
        if self.include_module_path:
            data["module_path"] = record.pathname
        if self.include_process_id:
            data["process_id"] = record.process
        if self.include_process_name:
            data["process_name"] = record.processName
        if self.include_thread_id:
            data["thread_id"] = record.thread
        if self.include_thread_name:
            data["thread_name"] = record.threadName
        if self.include_python_sdk_version:
            data["python_sdk_version"] = python_sdk.__version__

        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            record.exc_text = self.format_exception(record.exc_info)
        if record.exc_text:
            data["exception"] = record.exc_text
        if record.stack_info:
            data["stack_info"] = record.stack_info

        context = getattr(record, "context", {})
        for key in context:
            if key in data:
                logging.warning(f"Attempted to overwrite log attribute: {key}. Log attributes cannot be overwritten.")
            else:
                data[key] = context[key]

        return data

    def format(self, record: logging.LogRecord) -> str:
        data = self.pre_format(record=record)
        padding = max(60 - len(data["message"]), 0)
        text = f"{data['timestamp']} [{data['log_level']}\t] {data['message']} {' ' * padding}"
        for key, val in data.items():
            if key not in ["timestamp", "log_level", "message"]:
                text += f" {key}={val}"
        return text

    # taken from logging.Formatter.formatException
    def format_exception(
        self, ei: tuple[type[BaseException], BaseException, types.TracebackType | None] | tuple[None, None, None]
    ) -> str:
        """
        Format and return the specified exception information as a string.

        This default implementation just uses
        traceback.print_exception()
        """
        sio = io.StringIO()
        tb = ei[2]
        # See issues #9427, #1553375. Commented out for now.
        # if getattr(self, 'fullstack', False):
        #    traceback.print_stack(tb.tb_frame.f_back, file=sio)
        traceback.print_exception(ei[0], ei[1], tb, None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == "\n":
            s = s[:-1]
        return s

    def _yank_embedded_context_from_message(self, message: str) -> tuple[str, dict[str, typing.Any]]:
        # Given a logged message:
        #
        # ```py
        # user_id: int = 123
        # user_name: str = "test"
        # logging.info(f"User logged in. {user_id=} {user_name=}")
        # ```
        #
        # The resulting message will be:
        # User logged in. user_id=123 user_name='test'

        embedded_context: dict[str, typing.Any] = {}

        if "=" not in message:
            return message, embedded_context

        tokenized_message = message.split()
        for word in reversed(copy.copy(tokenized_message)):
            if "=" not in word:
                # In a message such as: "A User with the name='Tom' connected from ip='127.0.0.1'"
                # We will only yank "ip=127.0.0.1", else we risk the message not making sense.
                # To save ourselves the time processing the rest of the message, after we encounter a word
                # without the context token "=", we break.
                break

            context_key, context_value = word.split("=")
            embedded_context[context_key] = context_value.strip("'")
            tokenized_message.pop(-1)

        new_message = " ".join(tokenized_message)
        return new_message, embedded_context
