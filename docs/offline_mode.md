# Offline Mode

If Ollama is unavailable, `core/llm.py` returns a configured fallback string instead of crashing.

Configure:

- `.env` → `OFFLINE_FALLBACK_RESPONSE`

