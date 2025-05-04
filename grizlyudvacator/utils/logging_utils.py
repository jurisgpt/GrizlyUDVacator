import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .date_utils import generate_timestamp
from .path_utils import get_output_dir


def setup_logger(
    name: str,
    log_file: str | None = None,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Setup a logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format_str)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log_file is provided
    if log_file:
        log_path = get_output_dir() / f"{log_file}_{generate_timestamp()}.log"
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """Get or create a logger with the given name."""
    return setup_logger(name, log_file)


def log_exception(e: Exception, logger: logging.Logger) -> None:
    """Log an exception with full traceback."""
    logger.error(f"Exception occurred: {str(e)}", exc_info=True)


def log_warning(message: str, logger: logging.Logger) -> None:
    """Log a warning message."""
    logger.warning(message)
