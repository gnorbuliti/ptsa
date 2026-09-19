from __future__ import annotations

from datetime import UTC, datetime

from ptsa.workflow.time_tracker import TimeTracker


def test_default_timezone_uses_system_timezone() -> None:
    tracker = TimeTracker(interval_second=1)

    expected = datetime.now().astimezone().tzinfo
    assert tracker.timezone == expected


def test_explicit_timezone_is_preserved() -> None:

    tracker = TimeTracker(interval_second=1, timezone=UTC)

    assert tracker.timezone == UTC


def test_duration_uses_seconds_below_one_minute() -> None:
    tracker = TimeTracker()

    assert tracker._format_duration(12.345) == "12.35 seconds"


def test_duration_uses_minutes_below_one_hour() -> None:
    tracker = TimeTracker()

    assert tracker._format_duration(120) == "2.00 minutes"


def test_duration_uses_hours_below_one_day() -> None:
    tracker = TimeTracker()

    assert tracker._format_duration(7200) == "2.00 hours"


def test_duration_uses_days_from_one_day() -> None:
    tracker = TimeTracker()

    assert tracker._format_duration(172800) == "2.00 days"
