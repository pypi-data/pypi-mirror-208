"""Module providing an easy way to setup a minimal logger."""
import logging
import os
import platform
import sys
from logging import handlers, StreamHandler
from pathlib import Path
from typing import Literal

if int(platform.python_version_tuple()[1]) >= 11:
    from enum import StrEnum
    from typing import Self
else:
    from enum import Enum

    from typing_extensions import Self
    StrEnum = (str, Enum)


class ConsoleColor(*StrEnum):
    """Simple shortcut to use colors in the console."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"
    ENDCOLOR = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class ColoredFormatter(logging.Formatter):
    """Formatter adding colors to levelname."""

    def color_format(self: Self, record: logging.LogRecord) -> str:
        """Add colors to the levelname of the record."""
        levelno = record.levelno
        if levelno == logging.ERROR:
            levelname_color = ConsoleColor.RED + record.levelname + ConsoleColor.ENDCOLOR
        elif levelno == logging.WARNING:
            levelname_color = ConsoleColor.ORANGE + record.levelname + ConsoleColor.ENDCOLOR
        elif levelno == logging.INFO:
            levelname_color = ConsoleColor.GREEN + record.levelname + ConsoleColor.ENDCOLOR
        elif levelno == logging.DEBUG:
            levelname_color = ConsoleColor.BLUE + record.levelname + ConsoleColor.ENDCOLOR
        else:
            levelname_color = record.levelname
        record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def create_logger(name: str,
                  *,
                  log_dir: Path | None = None,
                  stdout: bool = True,
                  verbose_level: Literal["debug", "info", "error"] = "info") -> logging.Logger:
    """Create a logger.

    Args:
        name: Name of the logger.
        log_dir: If not None, the logs will be saved to that folder.
        stdout: If True then outputs to stdout.
        verbose_level: Either debug, info, error.

    Returns:
        The logger instance.
    """
    if log_dir is None and not stdout:
        msg = f"Either `log_dir` must be a Path or stdout must be `True`, got {log_dir=} and {stdout=}."
        raise ValueError(msg)

    logger = logging.getLogger(name)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # Add a (rotating) file handler to the logging system
        file_log_handler = handlers.RotatingFileHandler(log_dir / (name + ".log"), maxBytes=500000, backupCount=2)
        file_log_handler.setFormatter(log_formatter)
        logger.addHandler(file_log_handler)

    if stdout:
        # Add handler to the logging system (default has none) : outputting in stdout
        terminal_log_handler = StreamHandler(sys.stdout)
        if os.name != "nt":
            # Fancy color for non windows console
            colored_log_formatter = ColoredFormatter("%(levelname)s - %(message)s")
            terminal_log_handler.setFormatter(colored_log_formatter)
        else:
            log_formatter = logging.Formatter("%(levelname)s - %(message)s")
            terminal_log_handler.setFormatter(log_formatter)
        logger.addHandler(terminal_log_handler)

    match verbose_level:
        case "debug":
            logger.setLevel(logging.DEBUG)
        case "info":
            logger.setLevel(logging.INFO)
        case "error":
            logger.setLevel(logging.ERROR)

    return logger
