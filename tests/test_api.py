"""Tests for FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked orchestrator."""
    with patch("api.server.Orchestrator") as mock_orch_cls:
        mock_orch = mock_orch_cls.return_value
        mock_orch.run = AsyncMock(return_value="Test response")

        from api.server import app, _sessions

        _sessions.clear()

        with TestClient(app) as c:
            yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama" in data
    assert data["service"] == "holohome"


def test_chat_endpoint(client):
    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data


def test_chat_empty_message(client):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 200


def test_chat_session_tracking(client):
    """Multiple messages in the same session should share conversation history."""
    client.post("/chat", json={"message": "Hi", "session_id": "sess1"})
    client.post("/chat", json={"message": "How are you?", "session_id": "sess1"})
    from api.server import _sessions

    assert "sess1" in _sessions
    assert len(_sessions["sess1"]) == 4
