"""Interior agent — AR design and home improvement suggestions."""

import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class InteriorAgent(BaseAgent):
    """Suggests interior design, layout, and decor improvements."""

    def __init__(self):
        """Initialize interior agent."""
        super().__init__("InteriorAgent")

    INTERIOR_SYSTEM = (
        "You are HoloHome's interior design advisor. Suggest practical improvements "
        "for layout, color, lighting, and decor. Consider Pepper's Ghost display constraints."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle interior design and home improvement requests."""
        system = context.get("system_prompt", self.INTERIOR_SYSTEM)
        prefs = await self.recall("interior preferences")
        prompt = task
        if prefs:
            prompt = f"User preferences:\n{prefs}\n\nRequest: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system)
        await self.remember("interior", f"{task} -> {response}")
        return response
