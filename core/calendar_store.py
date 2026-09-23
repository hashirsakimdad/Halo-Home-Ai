"""Persistent calendar store — JSON-backed event storage for ScheduleAgent."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from config.settings import DATA_DIR

logger = logging.getLogger(__name__)

CALENDAR_FILE = DATA_DIR / "calendar.json"

EVENT_EXTRACTION_PROMPT = (
    "You are a date/time parser. Extract structured event data from the user request.\n"
    "Current time: {now}\n\n"
    "Return JSON with these fields (omit optional ones if not mentioned):\n"
    '{{"title": "<short title>", "start": "<ISO 8601 datetime>", '
    '"description": "<details or empty string>", "remind_minutes_before": <int or 0>}}\n\n'
    "If the request is NOT about creating/scheduling an event (e.g. listing events, "
    'asking about schedule), return: {{"action": "query"}}\n\n'
    "Examples:\n"
    '- "remind me to call mom tomorrow at 3pm" (now: 2025-01-15T10:00:00) -> '
    '{{"title": "Call mom", "start": "2025-01-16T15:00:00", "description": "", "remind_minutes_before": 15}}\n'
    '- "schedule dentist appointment friday at 2:30" (now: 2025-01-13T10:00:00) -> '
    '{{"title": "Dentist appointment", "start": "2025-01-17T14:30:00", "description": "", "remind_minutes_before": 30}}\n'
    '- "what do I have today?" -> {{"action": "query"}}\n\n'
    "User request: {task}\n\nJSON:"
)


class CalendarStore:
    """Simple JSON-file calendar for storing and querying events."""

    def __init__(self, path: Path | None = None):
        self._path = path or CALENDAR_FILE
        self._events: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load calendar: %s", exc)
            return []

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._events, indent=2, default=str), encoding="utf-8"
        )

    def add_event(
        self,
        title: str,
        start: str,
        description: str = "",
        remind_minutes_before: int = 0,
    ) -> dict:
        event = {
            "id": uuid.uuid4().hex[:8],
            "title": title,
            "start": start,
            "description": description,
            "remind_minutes_before": remind_minutes_before,
            "created_at": datetime.now().isoformat(),
        }
        self._events.append(event)
        self._save()
        return event

    def remove_event(self, event_id: str) -> bool:
        before = len(self._events)
        self._events = [e for e in self._events if e["id"] != event_id]
        if len(self._events) < before:
            self._save()
            return True
        return False

    def list_upcoming(self, limit: int = 10) -> list[dict]:
        now = datetime.now().isoformat()
        upcoming = [e for e in self._events if e.get("start", "") >= now]
        upcoming.sort(key=lambda e: e.get("start", ""))
        return upcoming[:limit]

    def list_all(self) -> list[dict]:
        return list(self._events)

    def get_due_reminders(self) -> list[dict]:
        now = datetime.now()
        due = []
        for event in self._events:
            try:
                start = datetime.fromisoformat(event["start"])
                mins = event.get("remind_minutes_before", 0)
                if mins > 0:
                    from datetime import timedelta

                    remind_at = start - timedelta(minutes=mins)
                    if remind_at <= now < start:
                        due.append(event)
            except (ValueError, KeyError):
                continue
        return due
