"""
Logging configuration for RFP Agent.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import config


def setup_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Set up a logger with console and optional file output.

    Args:
        name: Logger name
        log_file: Optional path to log file

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level))

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.log_level))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, config.log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default logger
logger = setup_logger("dux_rfp_agent")
