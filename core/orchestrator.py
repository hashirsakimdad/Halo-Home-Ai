"""LangGraph orchestrator — routes user intent to specialist agents."""

import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.education_agent import EducationAgent
from agents.home_agent import HomeAgent
from agents.interior_agent import InteriorAgent
from agents.schedule_agent import ScheduleAgent
from agents.security_agent import SecurityAgent
from agents.voice_agent import VoiceAgent
from core.llm import LLMClient, load_home_context
from config.settings import HOLOHOME_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    """State passed between LangGraph nodes."""

    task: str
    context: dict
    agent_name: str
    response: str


ROUTING_PROMPT = """Classify this user request into exactly ONE agent category.
Reply with ONLY the agent name, nothing else.

Agents:
- voice: general conversation, greetings, unclear intent
- home: lights, switches, thermostat, IoT, smart home
- education: learning, tutoring, homework, explanations
- schedule: calendar, reminders, tasks, appointments
- interior: design, decor, furniture, room layout
- security: cameras, alarms, locks, safety alerts

User request: {task}

Agent:"""


class Orchestrator:
    """Routes tasks to specialist agents via LangGraph."""

    AGENT_MAP = {
        "voice": VoiceAgent,
        "home": HomeAgent,
        "education": EducationAgent,
        "schedule": ScheduleAgent,
        "interior": InteriorAgent,
        "security": SecurityAgent,
    }

    KEYWORD_ROUTES = {
        "home": ("light", "turn on", "turn off", "switch", "thermostat", "mqtt", "device"),
        "education": ("teach", "explain", "learn", "homework", "study", "tutor"),
        "schedule": ("schedule", "calendar", "remind", "reminder", "appointment", "task"),
        "interior": ("design", "decor", "furniture", "layout", "room", "interior"),
        "security": ("camera", "alarm", "security", "lock", "motion", "alert"),
    }

    def __init__(self):
        """Initialize agents and compile the routing graph."""
        self.llm = LLMClient()
        self._agents = {name: cls() for name, cls in self.AGENT_MAP.items()}
        self._graph = self._build_graph()

    def _route_by_keywords(self, task: str) -> str | None:
        """Fast keyword-based routing before LLM classification."""
        lower = task.lower()
        for agent, keywords in self.KEYWORD_ROUTES.items():
            if any(kw in lower for kw in keywords):
                return agent
        return None

    async def _classify_node(self, state: OrchestratorState) -> OrchestratorState:
        """Determine which specialist agent should handle the task."""
        task = state["task"]
        agent_name = self._route_by_keywords(task)
        if not agent_name:
            prompt = ROUTING_PROMPT.format(task=task)
            raw = await self.llm.chat(prompt)
            candidate = raw.strip().lower().split()[0] if raw.strip() else "voice"
            agent_name = candidate if candidate in self.AGENT_MAP else "voice"
        logger.info("Routing to %s agent", agent_name)
        return {**state, "agent_name": agent_name}

    async def _execute_node(self, state: OrchestratorState) -> OrchestratorState:
        """Run the selected specialist agent."""
        agent_name = state["agent_name"]
        agent = self._agents[agent_name]
        context = dict(state.get("context") or {})
        home_context = load_home_context()
        context.setdefault(
            "system_prompt",
            HOLOHOME_SYSTEM_PROMPT.format(home_context=home_context),
        )
        try:
            response = await agent.run(state["task"], context)
        except Exception as exc:
            logger.error("Agent %s failed: %s", agent_name, exc)
            response = "Something went wrong. Please try again."
        return {**state, "response": response}

    def _build_graph(self):
        """Build and compile the LangGraph routing pipeline."""
        graph = StateGraph(OrchestratorState)
        graph.add_node("classify", self._classify_node)
        graph.add_node("execute", self._execute_node)
        graph.set_entry_point("classify")
        # classify → execute → END
        graph.add_edge("classify", "execute")
        graph.add_edge("execute", END)
        return graph.compile()

    async def run(self, task: str, context: dict | None = None) -> str:
        """Route a user task to the appropriate agent and return the response."""
        initial: OrchestratorState = {
            "task": task,
            "context": context or {},
            "agent_name": "",
            "response": "",
        }
        result = await self._graph.ainvoke(initial)
        return result["response"]
