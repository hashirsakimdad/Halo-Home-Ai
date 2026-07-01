"""Central configuration for HoloHome AI — all values loaded from environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# LLM (Ollama)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "30"))

# Memory (ChromaDB)
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db"))
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "holohome_memory")

# Voice
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
TTS_ENGINE: str = os.getenv("TTS_ENGINE", "pyttsx3")  # pyttsx3 | coqui
TTS_RATE: int = int(os.getenv("TTS_RATE", "150"))
TTS_VOLUME: float = float(os.getenv("TTS_VOLUME", "1.0"))

# Wake word
WAKE_WORD: str = os.getenv("WAKE_WORD", "hey holo")
WAKE_WORD_ENGINE: str = os.getenv("WAKE_WORD_ENGINE", "vosk")  # vosk | porcupine
PORCUPINE_ACCESS_KEY: str = os.getenv("PORCUPINE_ACCESS_KEY", "")
VOSK_MODEL_PATH: str = os.getenv("VOSK_MODEL_PATH", str(DATA_DIR / "vosk-model-small-en-us-0.15"))

# Home Assistant / MQTT
HOME_ASSISTANT_URL: str = os.getenv("HOME_ASSISTANT_URL", "http://localhost:8123")
HOME_ASSISTANT_TOKEN: str = os.getenv("HOME_ASSISTANT_TOKEN", "")
MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

# API server
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# Display
DISPLAY_WIDTH: int = int(os.getenv("DISPLAY_WIDTH", "800"))
DISPLAY_HEIGHT: int = int(os.getenv("DISPLAY_HEIGHT", "600"))
DISPLAY_FPS: int = int(os.getenv("DISPLAY_FPS", "30"))

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", str(LOG_DIR / "holohome.log"))

# Home context file
HOME_CONTEXT_FILE: Path = DATA_DIR / "home_context.json"

# Offline fallback response when Ollama is unavailable
OFFLINE_FALLBACK_RESPONSE: str = os.getenv(
    "OFFLINE_FALLBACK_RESPONSE",
    "I'm temporarily offline. Please check that Ollama is running.",
)

# HoloHome system prompt template
HOLOHOME_SYSTEM_PROMPT: str = """You are HoloHome, an intelligent holographic AI assistant living in the user's home.
You know everything about their home, schedule, and preferences.
You are helpful, concise, and proactive.
You respond in the same language the user speaks to you.
You can control home devices, manage schedules, help with education, and suggest improvements.
Always respond in 1-3 sentences unless more detail is specifically requested.
Current home context: {home_context}"""
