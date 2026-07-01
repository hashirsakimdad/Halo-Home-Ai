"""Central logging configuration for HoloHome AI."""

import logging
import sys
from logging.handlers import RotatingFileHandler

from config.settings import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """Configure root logger with console and rotating file handlers."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    if not root.handlers:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        root.addHandler(console)

        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
