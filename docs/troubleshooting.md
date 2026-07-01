# Troubleshooting

## Ollama not running

- Start: `ollama serve`
- Verify: `curl http://localhost:11434/api/tags`

## ChromaDB issues

- Ensure `CHROMA_PERSIST_DIR` points to a writable folder (default `data/chroma_db`)

## Voice mode not working

- Install voice deps when ready:
  - `pip install openai-whisper sounddevice scipy numpy pyttsx3 pygame`

