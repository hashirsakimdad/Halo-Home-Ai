"""Always-on wake word detection — runs independently of LLM."""

import asyncio
import json
import logging
import queue
import threading
from pathlib import Path

from config.settings import VOSK_MODEL_PATH, WAKE_WORD

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Listens for the wake phrase using Vosk (free, offline)."""

    def __init__(self, wake_word: str | None = None, model_path: str | None = None):
        """Configure wake word and Vosk model path."""
        self.wake_word = (wake_word or WAKE_WORD).lower()
        self.model_path = Path(model_path or VOSK_MODEL_PATH)
        self._running = False
        self._thread: threading.Thread | None = None
        self._detected = asyncio.Event()
        self._audio_queue: queue.Queue = queue.Queue()

    @property
    def detected(self) -> asyncio.Event:
        """Event set when wake word is heard."""
        return self._detected

    def _listen_loop(self) -> None:
        """Background thread: capture audio and check for wake word."""
        try:
            import pyaudio
            from vosk import KaldiRecognizer, Model, SetLogLevel

            SetLogLevel(-1)
            if not self.model_path.exists():
                logger.error("Vosk model not found at %s", self.model_path)
                return

            model = Model(str(self.model_path))
            recognizer = KaldiRecognizer(model, 16000)

            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000,
            )
            stream.start_stream()
            logger.info("Wake word listener active — say '%s'", self.wake_word)

            while self._running:
                data = stream.read(4000, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()
                    if self.wake_word in text:
                        logger.info("Wake word detected: %s", text)
                        self._detected.set()
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get("partial", "").lower()
                    if self.wake_word in partial_text:
                        logger.info("Wake word detected (partial): %s", partial_text)
                        self._detected.set()

            stream.stop_stream()
            stream.close()
            pa.terminate()
        except ImportError as exc:
            logger.error("Wake word dependencies missing: %s", exc)
        except Exception as exc:
            logger.error("Wake word listener error: %s", exc)

    def start(self) -> None:
        """Start wake word detection in a background thread."""
        if self._running:
            return
        self._running = True
        self._detected.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop wake word detection."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    async def wait_for_wake(self) -> None:
        """Block until wake word is detected, then reset the event."""
        self._detected.clear()
        await self._detected.wait()
        self._detected.clear()
