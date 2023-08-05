from multiprocessing import Queue
from multiprocessing.managers import BaseManager
from typing import Any, Callable, Dict, List, Optional, TypeVar

from .generic import GenericPipe

R = TypeVar("R")
S = TypeVar("S")


class ClassInstancePipe(GenericPipe[R, S]):
    def __init__(
        self,
        source: "Queue[R]",
        constructor_class: Any,
        use_method: Callable[[Any, R], S],
        target: "Queue[S]",
        close_method: Optional[Callable[[Any], Any]] = None,
        args_class: List[Any] = [],
        kwargs_class: Dict[str, Any] = {},
    ):
        BaseManager.register(constructor_class.__name__, constructor_class)
        self._constructor_class = constructor_class
        self._use_method = use_method
        self._close_method = close_method
        self._args_class = args_class
        self._kwargs_class = kwargs_class
        self._source = source
        self._target = target
        super().__init__(self._source, self._target)

    def start(self) -> None:
        self._instance = self._constructor_class(
            *self._args_class, **self._kwargs_class
        )
        self._task = getattr(self._instance, self._use_method.__name__)
        if self._close_method is not None:
            self._close_method = getattr(self._instance, self._close_method.__name__)
        else:
            self._close_method = None
        return super().start()

    def _perform_task(self, data: R) -> S:
        return self._task(data)

    def _kill(self, data: Any, error: bool = False):
        if self._close_method is not None:
            self._close_method()  # type: ignore
        super()._kill(data)
