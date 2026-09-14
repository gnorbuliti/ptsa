import asyncio
import sqlite3
import time
from collections.abc import Awaitable, Callable
from typing import Any


class TrackedTask[T]:
    def __init__(self, stageCAT: T):
        self.stage_cat: T = stageCAT
        self.is_finished: bool = False
        self.start_time: float = time.perf_counter()
        self.end_time: float = float("nan")

    def finished(self):
        self.is_finished = True
        self.end_time = time.perf_counter()


class TaskAlreadyExistsError(Exception):
    def __init__(self, stage_cat: str) -> None:
        self.stage_cat = stage_cat
        super().__init__(f"Task {stage_cat} already exists.")


class ApplicationModulePackage[T]:
    def __init__(self, task_flow: dict[T, list[T]], task_conditions: dict[T, list[T]]):
        self.task_flow: dict[T, list[T]] = task_flow
        self.task_conditions: dict[T, list[T]] = task_conditions
        self.task_tracker: dict[T, TrackedTask] = {}
        self.tasks: list[asyncio.Task[T]] = []

    def task_add(self, stageCAT: T, task: Callable[..., Awaitable[Any]], *args: Any):
        if stageCAT in self.task_tracker:
            raise TaskAlreadyExistsError(stageCAT)

        self.task_tracker[stageCAT] = TrackedTask(stageCAT)

        async def wrapper() -> T:
            await asyncio.create_task(task(*args))
            return stageCAT

        self.tasks.append(asyncio.create_task(wrapper()))

    async def task_next(self) -> set[T] | None:
        if not self.tasks:
            return None

        output: set[T] = set()
        done, _ = await asyncio.wait(self.tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            self.tasks.remove(task)
            result: T = task.result()

            found_state: TrackedTask[T] | None = self.task_tracker.get(result)
            if not found_state or found_state.is_finished:
                continue
            found_state.finished()

            task_next: list[T] | None = self.task_flow.get(result)
            if not task_next:
                continue

            for nextCAT in task_next:
                task_conditions: list[T] | None = self.task_conditions.get(nextCAT)
                if task_conditions:
                    found_states: list[bool] = []
                    for task_condition in task_conditions:
                        found_state: TrackedTask[T] | None = self.task_tracker.get(task_condition)
                        found_states.append(found_state and found_state.is_finished)
                    if len(found_states) > 0 and all(found_states):
                        output.add(nextCAT)
                else:
                    output.add(nextCAT)

        return output

    @staticmethod
    def task_read_database_table(database_path: str, table_name: str) -> list[Any]:
        connection: sqlite3.Connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        connection.close()
        return rows
