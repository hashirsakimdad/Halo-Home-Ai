"""Tests for orchestrator keyword routing."""

import pytest

from core.orchestrator import Orchestrator


@pytest.fixture
def orchestrator():
    """Create orchestrator with mocked agents for routing tests."""
    return Orchestrator()


def test_keyword_routes_home(orchestrator):
    """Home-related phrases route to home agent."""
    assert orchestrator._route_by_keywords("Turn on the living room light") == "home"


def test_keyword_routes_schedule(orchestrator):
    """Schedule phrases route to schedule agent."""
    assert orchestrator._route_by_keywords("Set a reminder for tomorrow") == "schedule"


def test_keyword_routes_none_for_generic(orchestrator):
    """Generic phrases fall through to LLM classification."""
    assert orchestrator._route_by_keywords("Hello there") is None
