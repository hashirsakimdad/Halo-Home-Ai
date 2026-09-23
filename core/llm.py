"""Ollama LLM wrapper — all agent LLM calls go through this module."""

from __future__ import annotations

import json
import logging
from collections import deque

import httpx

from config.settings import (
    HOLOHOME_SYSTEM_PROMPT,
    HOME_CONTEXT_FILE,
    OFFLINE_FALLBACK_RESPONSE,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)

logger = logging.getLogger(__name__)

DEFAULT_MAX_HISTORY = 20


def load_home_context() -> str:
    """Load home context JSON for injection into the system prompt."""
    if not HOME_CONTEXT_FILE.exists():
        return "{}"
    try:
        return HOME_CONTEXT_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read home context: %s", exc)
        return "{}"


class ConversationHistory:
    """Rolling buffer of chat messages for multi-turn context."""

    def __init__(self, max_turns: int = DEFAULT_MAX_HISTORY):
        self._max = max_turns * 2
        self._messages: deque[dict[str, str]] = deque(maxlen=self._max)

    def add_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self._messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)


class LLMClient:
    """Async client for local Ollama chat completions."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
    ):
        """Initialize Ollama connection settings."""
        self.model = model or OLLAMA_MODEL
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout or OLLAMA_TIMEOUT

    async def chat(
        self,
        prompt: str,
        system: str | None = None,
        history: ConversationHistory | None = None,
    ) -> str:
        """Send a chat request to Ollama and return the assistant reply."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history.get_messages())
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False},
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
            logger.error("Ollama chat failed: %s", exc)
            return OFFLINE_FALLBACK_RESPONSE

    async def holohome_chat(
        self,
        prompt: str,
        extra_system: str | None = None,
        history: ConversationHistory | None = None,
    ) -> str:
        """Chat using the standard HoloHome system prompt with home context."""
        home_context = load_home_context()
        system = HOLOHOME_SYSTEM_PROMPT.format(home_context=home_context)
        if extra_system:
            system = f"{system}\n\n{extra_system}"
        return await self.chat(prompt, system=system, history=history)

    async def is_available(self) -> bool:
        """Return True if Ollama responds to a health check."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
