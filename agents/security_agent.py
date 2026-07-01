"""Security agent — camera monitoring and alerts."""

import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Monitors cameras and handles security-related alerts."""

    def __init__(self):
        """Initialize security agent."""
        super().__init__("SecurityAgent")

    SECURITY_SYSTEM = (
        "You are HoloHome's security monitor. Handle alerts, camera status, and "
        "security questions. Be calm and actionable in responses."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle security monitoring and alert requests."""
        system = context.get("system_prompt", self.SECURITY_SYSTEM)
        history = await self.recall("security")
        prompt = task
        if history:
            prompt = f"Recent security events:\n{history}\n\nUser request: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system)
        await self.remember("security", f"{task} -> {response}")
        return response
