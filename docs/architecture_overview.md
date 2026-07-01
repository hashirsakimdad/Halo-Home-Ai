# Architecture Overview

HoloHome AI is a **local-only**, modular assistant:

- **Wake word**: lightweight always-on listener (Vosk)
- **STT**: Whisper (local)
- **Router**: LangGraph orchestrator routes intent to specialist agents
- **Specialists**: voice, home, education, schedule, interior, security
- **Memory**: ChromaDB shared vector memory
- **API**: FastAPI server (`/health`, `/chat`)

All LLM calls go through `core/llm.py`, and all memory reads/writes go through `core/memory.py`.

