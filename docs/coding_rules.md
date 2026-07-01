# Coding Rules (Project)

- Every function has a docstring
- Agents inherit from `BaseAgent` (no standalone agent functions)
- Config via `config/settings.py` + `.env`
- Async for I/O, logging over print
- LLM calls only via `core/llm.py`
- Memory only via `core/memory.py`

