"""
logs/logs.py
Centralised logging configuration for BankSec-TIP — ELK branch.

Usage:
    from logs.logs import get_logger
    logger = get_logger(__name__)
    logger.info("Syncing to Elasticsearch...")
"""

import logging
import os

LOG_DIR  = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "app.log")

_FMT      = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a named logger with both file and console handlers.
    Safe to call multiple times with the same name.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
