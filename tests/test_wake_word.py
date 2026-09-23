"""Tests for wake word detector configuration."""

from core.wake_word import WakeWordDetector


def test_default_wake_word():
    detector = WakeWordDetector()
    assert detector.wake_word == "hey holo"


def test_custom_wake_word():
    detector = WakeWordDetector(wake_word="ok holo")
    assert detector.wake_word == "ok holo"


def test_start_stop_without_model():
    """Starting without a Vosk model should not crash — it logs an error and returns."""
    detector = WakeWordDetector(model_path="/nonexistent/path")
    detector.start()
    detector.stop()


def test_detected_event_initially_unset():
    detector = WakeWordDetector()
    assert not detector.detected.is_set()
