"""
Logging configuration for SpiderMail
"""

import os
import sys
from pathlib import Path
from loguru import logger

from ..config.settings import settings


def setup_logger():
    """Setup application logging"""
    # Remove default logger
    logger.remove()

    # Ensure log directory exists
    log_file_path = Path(settings.logging.file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Add console handler
    logger.add(
        sys.stdout,
        level=settings.logging.level,
        format=settings.logging.format,
        colorize=True
    )

    # Add file handler
    logger.add(
        settings.logging.file_path,
        level=settings.logging.level,
        format=settings.logging.format,
        rotation=settings.logging.max_file_size,
        retention=settings.logging.backup_count,
        compression="zip",
        encoding="utf-8"
    )

    # Add error file handler
    error_log_path = log_file_path.parent / "error.log"
    logger.add(
        str(error_log_path),
        level="ERROR",
        format=settings.logging.format,
        rotation=settings.logging.max_file_size,
        retention=settings.logging.backup_count,
        compression="zip",
        encoding="utf-8"
    )

    logger.info(f"Logger initialized: {settings.logging.level}")
    return logger


# Initialize logger
setup_logger()