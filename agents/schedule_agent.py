"""Schedule agent — calendar, reminders, and task management."""

import logging
from datetime import datetime

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ScheduleAgent(BaseAgent):
    """Manages calendar events, reminders, and daily tasks."""

    def __init__(self):
        """Initialize schedule agent."""
        super().__init__("ScheduleAgent")

    SCHEDULE_SYSTEM = (
        "You are HoloHome's schedule manager. Help with calendars, reminders, and tasks. "
        "Be precise with dates and times. Confirm actions clearly."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle scheduling requests and retrieve stored reminders."""
        system = context.get("system_prompt", self.SCHEDULE_SYSTEM)
        now = datetime.now().isoformat()
        stored = await self.recall("schedule")

        prompt = f"Current time: {now}\n"
        if stored:
            prompt += f"Stored schedule data:\n{stored}\n\n"
        prompt += f"User request: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system)
        await self.remember("schedule", f"[{now}] {task} -> {response}")
        return response
