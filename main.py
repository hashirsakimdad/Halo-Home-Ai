"""HoloHome AI — 24/7 holographic home assistant entry point."""

import argparse
import asyncio
import logging
import sys

from core.logging_setup import setup_logging
from core.orchestrator import Orchestrator
from core.wake_word import WakeWordDetector
from agents.voice_agent import VoiceAgent
from core.llm import LLMClient

logger = logging.getLogger(__name__)


async def conversation_loop(
    use_wake_word: bool = True, use_display: bool = False
) -> None:
    """Run the Phase 1 voice MVP: wake word → listen → think → speak."""
    orchestrator = Orchestrator()
    voice = VoiceAgent()
    wake = WakeWordDetector() if use_wake_word else None
    display = None

    if use_display:
        from display.hologram import HologramDisplay

        display = HologramDisplay()
        display.start()
        display.render_text("HoloHome ready — say 'hey holo'")

    llm = LLMClient()
    if not await llm.is_available():
        logger.warning("Ollama not reachable — offline fallback responses will be used")

    if wake:
        wake.start()
        logger.info("Say '%s' to activate HoloHome", wake.wake_word)

    try:
        while True:
            if display and not display.tick():
                break

            if wake:
                await wake.wait_for_wake()
                await voice.speak("Yes?")
                if display:
                    display.render_text("Listening...")
            else:
                logger.info("Listening (no wake word mode)...")

            user_text = await voice.listen(duration=6.0)
            if not user_text:
                await voice.speak("I didn't catch that.")
                if display:
                    display.render_text("Didn't catch that.")
                continue

            if user_text.lower() in ("exit", "quit", "goodbye", "bye"):
                await voice.speak("Goodbye.")
                if display:
                    display.render_text("Goodbye.")
                break

            if display:
                display.render_text("Thinking...")

            response = await orchestrator.run(user_text)
            await voice.speak(response)
            if display:
                display.render_text(response)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if wake:
            wake.stop()
        if display:
            display.stop()


async def text_loop(use_display: bool = False) -> None:
    """Text-only conversation loop for testing without microphone."""
    orchestrator = Orchestrator()
    display = None

    if use_display:
        from display.hologram import HologramDisplay

        display = HologramDisplay()
        display.start()
        display.render_text("HoloHome text mode — type 'quit' to exit")

    print("HoloHome text mode — type 'quit' to exit.\n")

    try:
        while True:
            if display:
                display.tick()

            user_text = input("You: ").strip()
            if not user_text:
                continue
            if user_text.lower() in ("quit", "exit"):
                print("Goodbye.")
                if display:
                    display.render_text("Goodbye.")
                break

            if display:
                display.render_text("Thinking...")

            response = await orchestrator.run(user_text)
            print(f"HoloHome: {response}\n")
            if display:
                display.render_text(response)
    finally:
        if display:
            display.stop()


def main() -> None:
    """Parse CLI args and start the selected run mode."""
    setup_logging()

    parser = argparse.ArgumentParser(description="HoloHome AI assistant")
    parser.add_argument(
        "--mode",
        choices=["voice", "text", "api"],
        default="text",
        help="Run mode: voice (mic+TTS), text (keyboard), or api (FastAPI server)",
    )
    parser.add_argument(
        "--no-wake-word",
        action="store_true",
        help="Skip wake word detection and listen immediately",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Open Pepper's Ghost hologram display window",
    )
    args = parser.parse_args()

    if args.mode == "api":
        from api.server import run_server

        run_server()
        return

    if args.mode == "voice":
        asyncio.run(
            conversation_loop(
                use_wake_word=not args.no_wake_word, use_display=args.display
            )
        )
    else:
        asyncio.run(text_loop(use_display=args.display))


if __name__ == "__main__":
    main()
