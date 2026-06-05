"""
logs/logs.py
Centralised logging configuration for BankSec-TIP.
Import get_logger() in any module to get a consistent logger.

Usage:
    from logs.logs import get_logger
    logger = get_logger(__name__)
    logger.info("Feed ingestion started")
    logger.warning("Duplicate IOC skipped")
    logger.error("MongoDB connection failed")
"""

import logging
import os

LOG_DIR  = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "app.log")

_FMT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a named logger with both file and console handlers.
    Handlers are added only once, so calling get_logger() multiple
    times with the same name is safe.
    """
    logger = logging.getLogger(name)

    if logger.handlers:          # already configured — return as-is
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    # File handler — persistent log at logs/app.log
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler — visible in terminal
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
