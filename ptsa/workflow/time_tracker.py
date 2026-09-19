from __future__ import annotations

import datetime
import threading
import time


class TimeTracker:
    """Print a message periodically without blocking the caller."""

    def __init__(self, interval_second: float = 1.0, timezone: object | None = None) -> None:
        if interval_second <= 0:
            raise ValueError("interval_second must be greater than zero")

        self.interval_second = interval_second
        self.timezone = timezone or datetime.datetime.now().astimezone().tzinfo
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_time: float | None = None
        self._start_epoch: float | None = None
        self._title = "Time tracker"

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, title: str = "Time tracker") -> None:
        if self.is_running:
            return

        self._stop_event.clear()
        self._start_time = time.monotonic()
        self._start_epoch = time.time()
        self._title = title
        self._thread = threading.Thread(target=self._run, args=(title,), name="time-tracker", daemon=True)
        self._thread.start()
        print(f"{title} | started at {self._format_epoch(self._start_epoch)}", flush=True)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join()
        if self._start_time is not None:
            running_for = time.monotonic() - self._start_time
            print(f"{self._title} | stopped after {self._format_duration(running_for)}", flush=True)
        self._thread = None
        self._start_time = None
        self._start_epoch = None

    def _format_duration(self, duration_second: float) -> str:
        if duration_second < 60:
            value, unit = duration_second, "second"
        elif duration_second < 60 * 60:
            value, unit = duration_second / 60, "minute"
        elif duration_second < 24 * 60 * 60:
            value, unit = duration_second / (60 * 60), "hour"
        else:
            value, unit = duration_second / (24 * 60 * 60), "day"

        if value != 1:
            unit += "s"
        return f"{value:.2f} {unit}"

    def _format_epoch(self, epoch: float | None) -> str:
        if epoch is None:
            return "unknown"
        return datetime.datetime.fromtimestamp(epoch, tz=self.timezone).strftime("%Y-%m-%d %H:%M:%S%z")

    def _run(self, title: str) -> None:
        while not self._stop_event.wait(self.interval_second):
            running_for = time.monotonic() - self._start_time
            print(f"{title} | elapsed for {self._format_duration(running_for)} since {self._format_epoch(self._start_epoch)}", flush=True)
