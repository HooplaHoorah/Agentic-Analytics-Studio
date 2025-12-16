"""Simple logging helper.

This module provides a `get_logger` function that returns a module‑level
logger configured with a basic formatter. It avoids adding duplicate
handlers if called multiple times.
"""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with standard settings.

    Args:
        name: Typically `__name__` of the calling module.

    Returns:
        A `logging.Logger` instance with a stream handler attached.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Configure the handler only once
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger