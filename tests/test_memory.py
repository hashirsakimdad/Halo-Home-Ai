"""Tests for ChromaDB memory client."""

import pytest

from core.memory import MemoryClient


@pytest.fixture
def memory(tmp_path):
    """Create a temporary ChromaDB memory client."""
    return MemoryClient(persist_dir=str(tmp_path / "chroma"), collection_name="test")


@pytest.mark.asyncio
async def test_store_and_search(memory):
    await memory.store("greeting", "Hello, I am the user.")
    result = await memory.search("greeting")
    assert "Hello, I am the user." in result


@pytest.mark.asyncio
async def test_search_empty_returns_empty_string(memory):
    result = await memory.search("nonexistent topic")
    assert result == ""


@pytest.mark.asyncio
async def test_store_multiple_and_search(memory):
    await memory.store("food", "I like pizza.")
    await memory.store("food", "I also like pasta.")
    result = await memory.search("food preferences")
    assert "pizza" in result or "pasta" in result
