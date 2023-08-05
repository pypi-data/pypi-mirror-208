__version__ = "1.1.1"

from multiprocessing import Process, Queue
from threading import Timer
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    cast,
)

from olympipe.dispatcher import Dispatcher
from olympipe.pipes.batch import BatchPipe
from olympipe.pipes.explode import ExplodePipe
from olympipe.pipes.filter import FilterPipe
from olympipe.pipes.generic import GenericPipe
from olympipe.pipes.instance import ClassInstancePipe
from olympipe.pipes.reduce import ReducePipe
from olympipe.pipes.task import TaskPipe
from olympipe.pipes.timebatch import TimeBatchPipe

R = TypeVar("R")
S = TypeVar("S")
T = TypeVar("T")


class Pipeline(Generic[R]):
    max_queue_size: int = 4
    """max_queue_size
    Change this value to alter the maximum number of item per pipeline element. Default
    Default is 4
    """

    @staticmethod
    def get_new_queue() -> "Queue[R]":
        return Queue(maxsize=Pipeline.max_queue_size)

    def __init__(
        self,
        datas: Optional[Iterable[R]] = None,
        links: Optional[List["Tuple[Pipeline[Any], Process, Queue[Any]]"]] = None,
    ):
        self._source: "Queue[R]" = Pipeline.get_new_queue()
        self._parents: List["Process"] = []
        self.dispatcher = Dispatcher(self._source)
        self._register(self.dispatcher)
        self._links: List["Tuple[Pipeline[Any], Process, Queue[Any]]"] = (
            [] if links is None else links
        )
        self._datas = datas

    def start(self):
        input_pipe = self._links[0][0] if len(self._links) > 0 else self
        if input_pipe._datas is not None:
            for data in input_pipe._datas:
                input_pipe._source.put(data)
        input_pipe._source.put(GenericPipe.get_kill_word())

    def _register(
        self, process: Process, output_pipe: Optional["Pipeline[Any]"] = None
    ):
        """_register
        This method will register a process as parent
        to know when it should stop
        """
        if output_pipe is not None:
            output_pipe._links = [*self._links, (self, process, output_pipe._source)]
        self._parents.append(process)

    def task(self, task: Callable[[R], S], count: int = 1) -> "Pipeline[S]":
        assert count >= 1
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[S]" = Pipeline(links=self._links)
        self.dispatcher.dispatch_to([target_queue], count)
        for _ in range(count):
            p = TaskPipe(target_queue, task, output_pipe._source)
            self._register(p, output_pipe)
        return output_pipe

    def class_task(
        self,
        class_constructor: Any,
        class_method: Callable[[Any, R], S],
        class_args: List[Any] = [],
        close_method: Optional[Callable[[Any], Any]] = None,
        class_kwargs: Dict[str, Any] = {},
        count: int = 1,
    ) -> "Pipeline[S]":
        assert count >= 1
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[S]" = Pipeline()
        self.dispatcher.dispatch_to([target_queue], count)
        for _ in range(count):
            p = ClassInstancePipe(
                target_queue,
                class_constructor,
                class_method,
                output_pipe._source,
                close_method,
                class_args,
                class_kwargs,
            )
            self._register(p, output_pipe)
        return output_pipe

    def explode(self, explode_function: Callable[[R], Iterable[S]]) -> "Pipeline[S]":
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[S]" = Pipeline()
        p = ExplodePipe(target_queue, explode_function, output_pipe._source)

        self._register(p, output_pipe)
        self.dispatcher.dispatch_to([target_queue])
        return output_pipe

    def batch(
        self, count: int = 2, keep_incomplete_batch: bool = True
    ) -> "Pipeline[Iterable[R]]":
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[Iterable[R]]" = Pipeline()
        p = BatchPipe(target_queue, output_pipe._source, count, keep_incomplete_batch)
        self.dispatcher.dispatch_to([target_queue])

        self._register(p, output_pipe)
        return output_pipe

    def temporal_batch(self, time_interval: float) -> "Pipeline[Iterable[R]]":
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[Iterable[R]]" = Pipeline()
        p = TimeBatchPipe(target_queue, output_pipe._source, time_interval)
        self.dispatcher.dispatch_to([target_queue])

        self._register(p, output_pipe)
        return output_pipe

    def filter(self, filter_function: Callable[[R], bool]) -> "Pipeline[R]":
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[R]" = Pipeline()
        p = FilterPipe(target_queue, filter_function, output_pipe._source)
        self.dispatcher.dispatch_to([target_queue])

        self._register(p, output_pipe)
        return output_pipe

    @staticmethod
    def print_return(data: S) -> S:
        print(f"debug_pipe {data}")
        return data

    def debug(self) -> "Pipeline[R]":
        return self.task(Pipeline.print_return)

    def kill(self) -> None:
        self.dispatcher.terminate()

    def _prepare_output_buffer(self) -> "Queue[R]":
        q: Queue[R] = Pipeline.get_new_queue()
        self.dispatcher.dispatch_to([q])
        return q

    def reduce(self, accumulator: T, reducer: Callable[[R, T], T]) -> "Pipeline[T]":
        target_queue: "Queue[R]" = Pipeline.get_new_queue()
        output_pipe: "Pipeline[T]" = Pipeline()

        p = ReducePipe(target_queue, output_pipe._source, accumulator, reducer)
        self._register(p, output_pipe)
        self.dispatcher.dispatch_to([target_queue])
        return output_pipe

    def build_dot_graph(self, debug_file: str):
        links: List[Tuple[str, str, str, str]] = []
        for t, u, v in self._links:
            tn = ""
            try:
                tn = cast(Any, u)._task.__name__
                tn = "Debug" if tn == "print_return" else tn
            except:
                pass
            frm = t._source.__repr__().split(" ")[-1][:-1]
            to = v.__repr__().split(" ")[-1][:-1]
            links.append((frm, to, u.__class__.__name__[:-4], tn))

        renamer: Dict[str, str] = {}
        count = 0
        for i, link in enumerate(links):
            frm, to, name, tn = link
            if frm not in renamer:
                renamer[frm] = str(count)
                count += 1
            frm = renamer[frm]
            if to not in renamer:
                renamer[to] = str(count)
                count += 1
            to = renamer[to]
            links[i] = (frm, to, name, tn)

        with open(debug_file, "w") as f:
            _ = f.write("digraph G {\n")
            for frm, to, name, tn in links:
                _ = f.write(f'"{frm}" -> "{to}" [label="{name} {tn}"]\n')
            _ = f.write("}\n")

    def wait_and_reduce(
        self,
        accumulator: T,
        reducer: Callable[[R, T], T],
        debug_graph: Optional[str] = None,
    ) -> "T":
        o = self.reduce(accumulator, reducer)
        if debug_graph is not None:
            o.build_dot_graph(debug_graph)
        [[res]] = Pipeline._wait_for_all_results([o])
        return res

    @staticmethod
    def _wait_for_all_completions(
        pipes: List["Pipeline[Any]"], timeout: Optional[int] = None
    ) -> None:
        output_queues: List[Queue[Any]] = [p._prepare_output_buffer() for p in pipes]
        Timer(0.015, pipes[0].start).start()

        for o in output_queues:
            while True:
                packet = o.get(timeout=timeout)
                if GenericPipe.is_death_packet(packet):
                    break

    @staticmethod
    def _wait_for_all_results(pipes: List["Pipeline[Any]"]) -> List[List[Any]]:
        output_queues: List[Optional[Queue[Any]]] = [
            p._prepare_output_buffer() for p in pipes
        ]
        Timer(0.015, pipes[0].start).start()

        outputs: List[List[Any]] = [[] for _ in pipes]

        while any(output_queues) > 0:
            for i in range(len(output_queues)):
                output_queue = output_queues[i]
                if output_queue is None:
                    continue
                try:
                    packet = output_queue.get(timeout=0.1)
                    if GenericPipe.is_death_packet(packet):
                        output_queues[i] = None
                    else:
                        outputs[i].append(packet)
                except Exception:
                    pass

        return outputs

    def wait_for_completion(
        self, other_pipes: List["Pipeline[Any]"] = [], debug_graph: Optional[str] = None
    ) -> None:
        """_summary_

        Args:
            other_pipes (List[&quot;Pipeline[Any]&quot;], optional): _description_. Defaults to [].
            debug_graph (Optional[str], optional): path to save the dot graph file. Defaults to None.

        Returns:
            _type_: _description_
        """
        if debug_graph is not None:
            self.build_dot_graph(debug_graph)
        return Pipeline._wait_for_all_completions([self, *other_pipes])

    def wait_for_results(
        self, other_pipes: List["Pipeline[Any]"] = [], debug_graph: Optional[str] = None
    ) -> List[List[R]]:
        """_summary_

        Args:
            other_pipes (List[&quot;Pipeline[Any]&quot;], optional): _description_. Defaults to [].
            debug_graph (Optional[str], optional): path to save the dot graph file. Defaults to None.

        Returns:
            List[List[R]]: _description_
        """
        if debug_graph is not None:
            self.build_dot_graph(debug_graph)
        return Pipeline._wait_for_all_results([self, *other_pipes])

    def wait_for_result(self, debug_graph: Optional[str] = None) -> List[R]:
        """
        Args:
            debug_graph (Optional[str], optional): path to save the dot graph file. Defaults to None.

        Returns:
            List[R]: _description_
        """
        if debug_graph is not None:
            self.build_dot_graph(debug_graph)
        [res] = Pipeline._wait_for_all_results([self])
        return res
