"""Schedule agent — calendar, reminders, and task management."""

import json
import logging
from datetime import datetime

from agents.base_agent import BaseAgent
from core.calendar_store import EVENT_EXTRACTION_PROMPT, CalendarStore

logger = logging.getLogger(__name__)


class ScheduleAgent(BaseAgent):
    """Manages calendar events, reminders, and daily tasks."""

    def __init__(self):
        """Initialize schedule agent."""
        super().__init__("ScheduleAgent")
        self.calendar = CalendarStore()

    SCHEDULE_SYSTEM = (
        "You are HoloHome's schedule manager. Help with calendars, reminders, and tasks. "
        "Be precise with dates and times. Confirm actions clearly."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle scheduling requests: create events or answer calendar queries."""
        system = context.get("system_prompt", self.SCHEDULE_SYSTEM)
        now = datetime.now().isoformat()
        history = context.get("history")

        parsed = await self._extract_event(task, now)
        action_result = None

        if parsed.get("action") != "query" and parsed.get("title"):
            event = self.calendar.add_event(
                title=parsed["title"],
                start=parsed.get("start", now),
                description=parsed.get("description", ""),
                remind_minutes_before=parsed.get("remind_minutes_before", 0),
            )
            action_result = f"Event created: {event['title']} at {event['start']} (id: {event['id']})"

        upcoming = self.calendar.list_upcoming(limit=5)
        upcoming_text = self._format_events(upcoming) if upcoming else "No upcoming events."

        prompt = f"Current time: {now}\nUpcoming events:\n{upcoming_text}\n\n"
        if action_result:
            prompt += f"[Action result: {action_result}]\n\n"
        prompt += f"User request: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system, history=history)
        await self.remember("schedule", f"[{now}] {task} -> {response}")
        return response

    async def _extract_event(self, task: str, now: str) -> dict:
        try:
            raw = await self.llm.chat(EVENT_EXTRACTION_PROMPT.format(task=task, now=now))
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Event extraction failed: %s", exc)
        return {"action": "query"}

    @staticmethod
    def _format_events(events: list[dict]) -> str:
        lines = []
        for e in events:
            lines.append(f"- [{e['id']}] {e['title']} @ {e.get('start', '?')}")
            if e.get("description"):
                lines.append(f"  {e['description']}")
        return "\n".join(lines)
