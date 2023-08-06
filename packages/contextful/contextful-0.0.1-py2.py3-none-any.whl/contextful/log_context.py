import logging
from types import TracebackType
from typing import Any, Awaitable, Coroutine, Type
from contextlib import AbstractAsyncContextManager, AbstractContextManager
import uuid


class LogContext(AbstractAsyncContextManager, AbstractContextManager):
    def __init__(self, data: dict, frame_locals: dict, level: int = logging.NOTSET, id_: str = None):
        self.id = id_ or str(uuid.uuid4())
        self.data = data
        self.level = level
        self._frame_locals = frame_locals

    async def __aenter__(self) -> Awaitable:
        self._frame_locals[self.id] = self
        return super().__aenter__()

    async def __aexit__(self, __exc_type: Type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> Coroutine[Any, Any, bool | None]:
        self._frame_locals.pop(self.id, None)
        return await super().__aexit__(__exc_type, __exc_value, __traceback)

    def __enter__(self):
        self._frame_locals[self.id] = self
        return super().__enter__()

    def __exit__(self, __exc_type: Type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        self._frame_locals.pop(self.id, None)
        return super().__exit__(__exc_type, __exc_value, __traceback)
