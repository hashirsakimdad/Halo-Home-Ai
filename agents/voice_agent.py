"""Voice agent — Whisper STT and pyttsx3/Coqui TTS pipeline."""

import asyncio
import logging
import tempfile
from pathlib import Path

from agents.base_agent import BaseAgent
from config.settings import TTS_RATE, TTS_VOLUME, WHISPER_MODEL

logger = logging.getLogger(__name__)


class VoiceAgent(BaseAgent):
    """Handles speech-to-text and text-to-speech for HoloHome."""

    VOICE_SYSTEM = (
        "You are HoloHome's voice interface. Rephrase responses for natural spoken delivery. "
        "Keep answers brief and conversational."
    )

    def __init__(self):
        """Load Whisper and TTS engines."""
        super().__init__("VoiceAgent")
        self._whisper_model = None
        self._tts_engine = None

    def _load_whisper(self):
        """Lazy-load Whisper model on first use."""
        if self._whisper_model is None:
            import whisper

            logger.info("Loading Whisper model: %s", WHISPER_MODEL)
            self._whisper_model = whisper.load_model(WHISPER_MODEL)

    def _load_tts(self):
        """Lazy-load pyttsx3 engine on first use."""
        if self._tts_engine is None:
            import pyttsx3

            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", TTS_RATE)
            self._tts_engine.setProperty("volume", TTS_VOLUME)

    async def listen(self, duration: float = 5.0, sample_rate: int = 16000) -> str:
        """Record from microphone and transcribe with Whisper."""
        try:
            import sounddevice as sd
            import soundfile as sf

            self._load_whisper()
            audio = await asyncio.to_thread(
                sd.rec,
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            await asyncio.to_thread(sd.wait)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            await asyncio.to_thread(sf.write, str(tmp_path), audio, sample_rate)

            try:
                result = await asyncio.to_thread(
                    self._whisper_model.transcribe, str(tmp_path)
                )
                text = result.get("text", "").strip()
                logger.info("Transcribed: %s", text)
                return text
            finally:
                tmp_path.unlink(missing_ok=True)
        except Exception as exc:
            logger.error("Listen failed: %s", exc)
            return ""

    async def speak(self, text: str) -> None:
        """Speak text aloud using pyttsx3."""
        if not text:
            return
        try:
            self._load_tts()
            await asyncio.to_thread(self._tts_engine.say, text)
            await asyncio.to_thread(self._tts_engine.runAndWait)
            logger.debug("Spoke response (%d chars)", len(text))
        except Exception as exc:
            logger.error("TTS failed: %s", exc)

    async def run(self, task: str, context: dict) -> str:
        """Process a voice-related request or general conversation."""
        system = context.get("system_prompt", self.VOICE_SYSTEM)
        return await self.llm.holohome_chat(task, extra_system=system)
