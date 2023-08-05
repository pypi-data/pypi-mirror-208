import queue
import time
from multiprocessing import Process, Queue
from threading import Timer
from typing import Any, Generic, Iterable, List, TypeVar

from .pipes.generic import GenericPipe

S = TypeVar("S")


class Dispatcher(Process, Generic[S]):
    def __init__(self, queue: "Queue[S]"):
        super().__init__()
        self._source = queue
        self.subscribers: "List[Queue[S]]" = []
        self._subscribers_mask: List[int] = []
        self._death_counter: List[int] = []
        self._timeout = 0.1

        Timer(0.015, self.start).start()

    def dispatch_to(self, recipients: "List[Queue[S]]", count: int = 1):
        for recipient in recipients:
            self.subscribers.append(recipient)
            self._subscribers_mask.append(count)

    def _dispatch(self, args: Iterable[S]):
        for s in self.subscribers:
            for arg in args:
                while True:
                    try:
                        s.put(arg, timeout=self._timeout)
                        break
                    except Exception as e:
                        if e.__class__.__name__ == "Full":
                            continue
                        break

    def _kill(self, packet: Any) -> bool:
        _, death_count = packet
        self._death_counter.append(death_count)
        if len(self._death_counter) != death_count:
            return False
        for s in self.subscribers:
            while not s.empty():
                time.sleep(0.01)
        self._source.close()
        for i, s in enumerate(self.subscribers):
            num_children = self._subscribers_mask[i]
            for _ in range(num_children):
                s.put(GenericPipe.get_kill_word(num_children), timeout=self._timeout)
        return True

    def run(self):
        while True:
            try:
                packet = self._source.get(timeout=0.1)
                if GenericPipe.is_death_packet(packet):
                    if self._kill(packet):
                        return
                    else:
                        continue
            except queue.Empty:
                continue
            except Exception as e:
                print("Error", e)
                return
            self._dispatch([packet])
