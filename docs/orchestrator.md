# Orchestrator (LangGraph)

Routing is handled by `core/orchestrator.py`.

## Routing strategy

1. **Keyword route** (fast): common phrases map directly to an agent
2. **LLM classify** (fallback): asks the LLM to output *only* the agent name
3. **Execute**: selected agent handles the task and returns response

## Why this design

- Keeps intent routing robust even on small local models
- Avoids crashes: agent execution is wrapped with error handling

