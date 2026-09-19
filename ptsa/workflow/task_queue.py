from __future__ import annotations

import multiprocessing
import os
from collections.abc import Callable


class Job[T, U]:
    def __init__(self, id: str, fn: Callable[[T], U], args: T, future: Future[U]):
        self.id: str = id
        self.fn: Callable[[T], U] = fn
        self.args: T = args
        self.future: Future[U] = future


class Future[U]:
    def __init__(self):
        self._queue = multiprocessing.Queue(maxsize=1)

    def result(self, timeout: float | None = None) -> U | BaseException:
        result = self._queue.get(timeout=timeout)
        return result["result"] if result["error"] is None else result["error"]

    def _set_result(self, result: U) -> None:
        self._queue.put({"result": result, "error": None})

    def _set_exception(self, error: BaseException) -> None:
        self._queue.put({"result": None, "error": error})


class WorkerPool[T, U]:
    def __init__(self, worker_count: int | None = None):
        if worker_count is None:
            worker_count = max(1, (os.cpu_count() or 1) - 1)
        elif worker_count < 1:
            raise ValueError("worker_count must be positive")

        self.worker_count = worker_count
        self.workers = multiprocessing.Pool(processes=worker_count)

    def submit(self, fn: Callable[[T], U], args: T) -> Future[U]:
        future: Future[U] = Future()
        self.workers.apply_async(fn, (args,), callback=future._set_result, error_callback=future._set_exception)
        return future

    def submit_chunks(self, fn: Callable[[T], U], args: list[T]) -> list[Future[list[U]]]:
        if not args:
            return []

        chunk_size = (len(args) + self.worker_count - 1) // self.worker_count
        futures: list[Future[list[U]]] = []
        for index in range(0, len(args), chunk_size):
            future: Future[list[U]] = Future()
            chunk = args[index : index + chunk_size]
            self.workers.apply_async(self.process_chunk, (fn, chunk), callback=future._set_result, error_callback=future._set_exception)
            futures.append(future)

        return futures

    @staticmethod
    def process_chunk(fn: Callable[[T], U], args: list[T]) -> list[U]:
        return [fn(i) for i in args]

    def shutdown(self):
        self.workers.close()
        self.workers.join()
