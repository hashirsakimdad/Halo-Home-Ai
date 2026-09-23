"""Tests for specialist agents with mocked LLM and memory."""

from unittest.mock import AsyncMock, patch

import pytest

from agents.education_agent import EducationAgent
from agents.home_agent import HomeAgent
from agents.interior_agent import InteriorAgent
from agents.schedule_agent import ScheduleAgent
from agents.security_agent import SecurityAgent
from agents.voice_agent import VoiceAgent


@pytest.fixture
def mock_llm():
    """Patch LLMClient so agents don't need Ollama."""
    with patch("agents.base_agent.LLMClient") as cls:
        instance = cls.return_value
        instance.chat = AsyncMock(return_value="mocked response")
        instance.holohome_chat = AsyncMock(return_value="mocked response")
        yield instance


@pytest.fixture
def mock_memory():
    """Patch MemoryClient so agents don't need ChromaDB."""
    with patch("agents.base_agent.MemoryClient") as cls:
        instance = cls.return_value
        instance.store = AsyncMock()
        instance.search = AsyncMock(return_value="")
        yield instance


@pytest.mark.asyncio
async def test_voice_agent_run(mock_llm, mock_memory):
    agent = VoiceAgent()
    result = await agent.run("hello", {"system_prompt": "test"})
    assert result == "mocked response"
    mock_llm.holohome_chat.assert_called_once()


@pytest.mark.asyncio
async def test_education_agent_run(mock_llm, mock_memory):
    agent = EducationAgent()
    result = await agent.run("explain gravity", {"system_prompt": "test"})
    assert result == "mocked response"
    mock_memory.store.assert_called_once()


@pytest.mark.asyncio
async def test_schedule_agent_includes_time(mock_llm, mock_memory):
    agent = ScheduleAgent()
    await agent.run("set a reminder", {"system_prompt": "test"})
    call_args = mock_llm.holohome_chat.call_args[0][0]
    assert "Current time:" in call_args


@pytest.mark.asyncio
async def test_interior_agent_run(mock_llm, mock_memory):
    agent = InteriorAgent()
    result = await agent.run("suggest colors for living room", {})
    assert result == "mocked response"


@pytest.mark.asyncio
async def test_security_agent_run(mock_llm, mock_memory):
    agent = SecurityAgent()
    result = await agent.run("check cameras", {})
    assert result == "mocked response"


@pytest.mark.asyncio
async def test_home_agent_extracts_command(mock_llm, mock_memory):
    """HomeAgent should attempt to extract and execute a device command."""
    agent = HomeAgent()
    agent.llm.chat = AsyncMock(return_value='{"action": "none"}')
    agent.llm.holohome_chat = AsyncMock(return_value="Lights are off.")

    result = await agent.run("turn off the lights", {})
    assert result == "Lights are off."
    agent.llm.chat.assert_called_once()


@pytest.mark.asyncio
async def test_home_agent_calls_ha_service(mock_llm, mock_memory):
    """HomeAgent should call Home Assistant when a service command is extracted."""
    agent = HomeAgent()
    ha_json = '{"action": "ha_service", "domain": "light", "service": "turn_on", "entity_id": "light.living_room"}'
    agent.llm.chat = AsyncMock(return_value=ha_json)
    agent.llm.holohome_chat = AsyncMock(return_value="Turned on the lights.")
    agent.call_service = AsyncMock(return_value=True)

    result = await agent.run("turn on the lights", {})
    assert result == "Turned on the lights."
    agent.call_service.assert_called_once_with("light", "turn_on", "light.living_room")


@pytest.mark.asyncio
async def test_home_agent_publishes_mqtt(mock_llm, mock_memory):
    """HomeAgent should publish MQTT when an mqtt command is extracted."""
    agent = HomeAgent()
    mqtt_json = '{"action": "mqtt", "topic": "home/fan", "payload": "ON"}'
    agent.llm.chat = AsyncMock(return_value=mqtt_json)
    agent.llm.holohome_chat = AsyncMock(return_value="Fan is on.")
    agent.publish_mqtt = AsyncMock(return_value=True)

    result = await agent.run("turn on the fan via mqtt", {})
    assert result == "Fan is on."
    agent.publish_mqtt.assert_called_once_with("home/fan", "ON")
