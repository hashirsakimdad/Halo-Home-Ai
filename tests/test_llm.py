"""Tests for LLM client offline fallback behavior."""

import pytest

from core.llm import LLMClient
from config.settings import OFFLINE_FALLBACK_RESPONSE


@pytest.mark.asyncio
async def test_chat_returns_fallback_on_http_error():
    """LLM client should not crash when Ollama is unavailable."""
    client = LLMClient(base_url="http://invalid-host:9999", timeout=1)
    result = await client.chat("Hello")
    assert result == OFFLINE_FALLBACK_RESPONSE


@pytest.mark.asyncio
async def test_is_available_false_when_unreachable():
    """Health check returns False when Ollama is down."""
    client = LLMClient(base_url="http://invalid-host:9999", timeout=1)
    assert await client.is_available() is False
