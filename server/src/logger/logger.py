import logging
import sys
from typing import Optional
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        # Save original levelname
        orig_levelname = record.levelname
        # Add color to the levelname
        record.levelname = f"{self.COLORS.get(record.levelname, '')}{
            record.levelname}{Style.RESET_ALL}"
        # Add timestamp
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Format the message
        result = super().format(record)
        # Restore original levelname
        record.levelname = orig_levelname
        return result


def setup_logger(name: str = "app", level: Optional[str] = "INFO") -> logging.Logger:
    """
    Set up and return a colored logger instance

    Args:
        name (str): Name of the logger
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = ColoredFormatter(
        '%(timestamp)s | %(levelname)-8s | %(name)s | %(message)s'
    )

    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
