"""Education agent — tutoring and explanations."""

import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EducationAgent(BaseAgent):
    """Provides tutoring, explanations, and learning support."""

    def __init__(self):
        """Initialize education agent."""
        super().__init__("EducationAgent")

    EDUCATION_SYSTEM = (
        "You are HoloHome's education tutor. Explain concepts clearly and adapt "
        "to the user's level. Use examples. Support Urdu and English."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle education and tutoring requests."""
        system = context.get("system_prompt", self.EDUCATION_SYSTEM)
        prior = await self.recall("education")
        prompt = task
        if prior:
            prompt = f"Previous learning context:\n{prior}\n\nUser question: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system)
        await self.remember("education", f"Q: {task} A: {response}")
        return response
