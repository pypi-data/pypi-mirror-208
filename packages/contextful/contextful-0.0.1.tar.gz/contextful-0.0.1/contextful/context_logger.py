import inspect
import logging
from types import FrameType

from .log_context import LogContext


class ContextLogger(logging.Logger):
    def __init__(self, name: str = None, level: int = logging.INFO):
        super().__init__(name, level)

    def _get_frame_log_context(self, frame: FrameType, log_level: int) -> LogContext | None:
        log_context = log_context = next(
            (
                value
                for value in frame.f_locals.values()
                if isinstance(value, LogContext) and value.level >= log_level
            ),
            None
        )
        return log_context

    def _get_context_data(self, log_data: dict | None, log_level: int = logging.CRITICAL) -> dict:
        context_data = {}
        frames = [frame_info.frame for frame_info in inspect.stack()]

        for frame in frames:
            log_context = self._get_frame_log_context(frame, log_level)
            if log_context:
                context_data = {**log_context.data, **context_data}

        data = {**context_data, **(log_data or {})}
        return data

    def _log(self, level: int, msg: object, *args, extra: dict | None = None, **kwargs) -> None:
        context_data = self._get_context_data(extra, level)
        context_wrapper = {'context': context_data}
        msg = f'{msg}'
        return super()._log(level, msg, *args, extra=context_wrapper, **kwargs)

    def __context(self, extra: dict, level: int = logging.NOTSET, frame_trace_count: int = 2) -> LogContext:
        frames = [frame_info.frame for frame_info in inspect.stack()]
        caller_frame_locals = frames[frame_trace_count].f_locals
        context = LogContext(extra, caller_frame_locals, level or self.level)

        return context

    def context(self, extra: dict) -> LogContext:
        return self.__context(extra, self.level)

    def debug_context(self, extra: dict) -> LogContext:
        return self.__context(extra, logging.DEBUG)

    def info_context(self, extra: dict) -> LogContext:
        return self.__context(extra, logging.INFO)

    def warning_context(self, extra: dict) -> LogContext:
        return self.__context(extra, logging.WARNING)

    def error_context(self, extra: dict) -> LogContext:
        return self.__context(extra, logging.ERROR)

    def critical_context(self, extra: dict) -> LogContext:
        return self.__context(extra, logging.CRITICAL)