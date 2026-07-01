# HoloHome AI

A 24/7 holographic AI home assistant inspired by Psycho-Pass. Runs **100% locally** on free, open-source tools — no paid API dependencies.

## Architecture

```
Voice/Gesture → Wake Word → Whisper STT → LangGraph Orchestrator → Specialist Agents → TTS → Display
                                              ↓
                                         ChromaDB Memory
```

**Specialist agents:** Voice, Home (IoT), Education, Schedule, Interior, Security

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Llama 3.2-1B via Ollama |
| Agents | LangGraph |
| STT | OpenAI Whisper (local) |
| TTS | pyttsx3 |
| Wake word | Vosk |
| Memory | ChromaDB |
| API | FastAPI |
| IoT | Home Assistant + MQTT |

## Quick Start

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) with `llama3.2:1b` pulled
- Microphone (for voice mode)

```bash
ollama pull llama3.2:1b
```

### 2. Install

```bash
cd "HaloHome AI"
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
```

### 3. Wake word model (voice mode)

Download the [Vosk small English model](https://alphacephei.com/vosk/models) and extract to:

```
data/vosk-model-small-en-us-0.15/
```

### 4. Run

```bash
# Text mode (no mic needed — good for first test)
python main.py --mode text

# Voice mode with wake word "hey holo"
python main.py --mode voice

# Voice without wake word (listens immediately)
python main.py --mode voice --no-wake-word

# FastAPI server (includes /health)
python main.py --mode api
```

## Project Structure

```
├── core/           # LLM, memory, orchestrator, wake word
├── agents/         # 6 specialist agents + base class
├── display/        # Hologram + avatar (Phase 4)
├── api/            # FastAPI server
├── config/         # Central settings (.env)
├── data/           # Home context, ChromaDB, Vosk model
├── tests/
└── main.py         # Entry point
```

## Development Phases

- **Phase 1 — Voice MVP** ✅ scaffolded
- **Phase 2 — Agents + Memory** ✅ scaffolded
- **Phase 3 — 24/7 Production** — API + health check ready; add systemd service
- **Phase 4 — Hologram Display** — stubs in `display/`

## 24/7 Production (Linux)

Create a systemd unit at `/etc/systemd/system/holohome.service`:

```ini
[Unit]
Description=HoloHome AI Assistant
After=network.target ollama.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/holohome
ExecStart=/home/pi/holohome/.venv/bin/python main.py --mode api
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**UPS recommended** for uninterrupted 24/7 operation.

## Health Check

```bash
curl http://localhost:8000/health
```

## Tests

```bash
pytest tests/ -v
```

## License

MIT
