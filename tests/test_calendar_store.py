"""Tests for CalendarStore JSON-backed event storage."""

import json

import pytest

from core.calendar_store import CalendarStore


@pytest.fixture
def store(tmp_path):
    """Create a calendar store backed by a temp file."""
    return CalendarStore(path=tmp_path / "cal.json")


def test_add_event(store):
    event = store.add_event(title="Dentist", start="2025-06-15T14:00:00")
    assert event["title"] == "Dentist"
    assert event["start"] == "2025-06-15T14:00:00"
    assert "id" in event


def test_list_all(store):
    store.add_event(title="A", start="2025-01-01T10:00:00")
    store.add_event(title="B", start="2025-01-02T10:00:00")
    assert len(store.list_all()) == 2


def test_remove_event(store):
    event = store.add_event(title="Remove me", start="2025-01-01T10:00:00")
    assert store.remove_event(event["id"]) is True
    assert len(store.list_all()) == 0


def test_remove_nonexistent(store):
    assert store.remove_event("nope") is False


def test_list_upcoming_filters_past(store):
    store.add_event(title="Past", start="2000-01-01T00:00:00")
    store.add_event(title="Future", start="2099-12-31T23:59:59")
    upcoming = store.list_upcoming()
    assert len(upcoming) == 1
    assert upcoming[0]["title"] == "Future"


def test_list_upcoming_sorted(store):
    store.add_event(title="Later", start="2099-06-01T10:00:00")
    store.add_event(title="Sooner", start="2099-01-01T10:00:00")
    upcoming = store.list_upcoming()
    assert upcoming[0]["title"] == "Sooner"
    assert upcoming[1]["title"] == "Later"


def test_persistence(tmp_path):
    path = tmp_path / "cal.json"
    s1 = CalendarStore(path=path)
    s1.add_event(title="Persist", start="2099-01-01T10:00:00")

    s2 = CalendarStore(path=path)
    assert len(s2.list_all()) == 1
    assert s2.list_all()[0]["title"] == "Persist"


def test_add_event_with_reminder(store):
    event = store.add_event(
        title="Meeting", start="2099-06-01T09:00:00", remind_minutes_before=15
    )
    assert event["remind_minutes_before"] == 15


def test_corrupt_file_loads_empty(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    store = CalendarStore(path=path)
    assert store.list_all() == []
