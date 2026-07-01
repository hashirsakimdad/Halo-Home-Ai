"""3D avatar animation synced to voice — Phase 4 stub."""

import logging

logger = logging.getLogger(__name__)


class AvatarAnimator:
    """Animates a holographic avatar in sync with TTS speech output."""

    def __init__(self):
        """Initialize avatar animator state."""
        self._speaking = False
        self._frame = 0

    def start_speaking(self) -> None:
        """Begin mouth/movement animation during speech."""
        self._speaking = True
        logger.debug("Avatar speaking animation started")

    def stop_speaking(self) -> None:
        """Stop avatar animation and return to idle."""
        self._speaking = False
        self._frame = 0
        logger.debug("Avatar returned to idle")

    def update(self) -> dict:
        """Advance animation frame and return current avatar state."""
        if self._speaking:
            self._frame = (self._frame + 1) % 30
        return {"speaking": self._speaking, "frame": self._frame, "expression": "neutral"}
