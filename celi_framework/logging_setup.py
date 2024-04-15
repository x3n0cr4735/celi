import json
import logging
import logging.config
from pathlib import Path


def setup_logging():
    with open(Path(__file__).parent / "logging_config.json", "r") as f:
        log_config = json.load(f)
    logging.config.dictConfig(log_config)


# ANSI escape codes for colors
COLORS = {
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "brown": "\033[0;33m",
    "cyan": "\033[96m",
    "red": "\033[91m",
    "white": "\033[97m",
    "grey": "\033[37m",
    "orange": "\033[38;5;202m",  # ANSI code for orange
    "purple": "\033[95m",
    "light_green": "\033[92m",
    "dark_grey": "\033[90m",
    "end": "\033[0m",
}


def colorize(message, color):
    """
    Applies ANSI color codes to a given message string.

    Args:
        message (str): The message to colorize.
        color (str): The name of the color to apply. Must be a key in the COLORS dictionary.

    Returns:
        str: The colorized message string.
    """
    return f"{COLORS.get(color, '')}{message}{COLORS['end']}"


class ColorizingStreamHandler(logging.StreamHandler):
    """
    A logging stream handler that colorizes log messages based on a 'color' attribute in the log record.

    This handler extends the logging.StreamHandler class, adding functionality to colorize log messages
    for console output and integrate MongoDB logging through the MongoDBUtilitySingleton class.
    """

    def format(self, record):
        """
        Formats a log record with ANSI color codes if a 'color' attribute is present.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message, colorized if applicable.
        """
        original_message = super(ColorizingStreamHandler, self).format(record)
        if hasattr(record, "color") and record.color in COLORS:
            return colorize(original_message, record.color)
        elif record.levelno == logging.ERROR:
            return colorize(original_message, "red")
        elif record.levelno == logging.WARNING:
            return colorize(original_message, "yellow")
        else:
            return original_message
