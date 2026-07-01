"""Pepper's Ghost hologram renderer — Phase 4 stub."""

import logging

import pygame

from config.settings import DISPLAY_FPS, DISPLAY_HEIGHT, DISPLAY_WIDTH

logger = logging.getLogger(__name__)

# Pepper's Ghost requires black background for transparency illusion
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 200, 255)


class HologramDisplay:
    """Renders holographic output on a pygame window."""

    def __init__(self, width: int | None = None, height: int | None = None):
        """Initialize pygame display with black background."""
        self.width = width or DISPLAY_WIDTH
        self.height = height or DISPLAY_HEIGHT
        self._screen = None
        self._clock = None
        self._running = False

    def start(self) -> None:
        """Open the hologram display window."""
        pygame.init()
        self._screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("HoloHome")
        self._clock = pygame.time.Clock()
        self._running = True
        logger.info("Hologram display started %dx%d", self.width, self.height)

    def render_text(self, text: str) -> None:
        """Draw response text on the hologram screen."""
        if not self._screen:
            return
        self._screen.fill(BG_COLOR)
        font = pygame.font.SysFont("arial", 28)
        surface = font.render(text[:120], True, TEXT_COLOR)
        rect = surface.get_rect(center=(self.width // 2, self.height // 2))
        self._screen.blit(surface, rect)
        pygame.display.flip()

    def tick(self) -> bool:
        """Process events and return False if window was closed."""
        if not self._running:
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return False
        if self._clock:
            self._clock.tick(DISPLAY_FPS)
        return True

    def stop(self) -> None:
        """Shut down pygame."""
        if self._running:
            pygame.quit()
            self._running = False
            logger.info("Hologram display stopped")
