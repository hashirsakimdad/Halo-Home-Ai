"""Base agent class — all specialist agents inherit from this."""

import logging
from abc import ABC, abstractmethod

from core.llm import LLMClient
from core.memory import MemoryClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base for HoloHome specialist agents."""

    def __init__(self, name: str):
        """Initialize agent with shared LLM and memory clients."""
        self.name = name
        self.llm = LLMClient()
        self.memory = MemoryClient()
        logger.info("%s agent initialized", self.name)

    @abstractmethod
    async def run(self, task: str, context: dict) -> str:
        """Execute the agent's primary task."""
        pass

    async def remember(self, key: str, value: str) -> None:
        """Save information to shared memory."""
        await self.memory.store(key, value)

    async def recall(self, query: str) -> str:
        """Retrieve relevant information from memory."""
        return await self.memory.search(query)
