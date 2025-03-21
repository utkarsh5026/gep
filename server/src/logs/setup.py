import sys
import os
from pathlib import Path
from loguru import logger


def configure_logging(verbose_level=0, components=None, log_file=None):
    """Configure Loguru with appropriate settings based on verbosity."""
    logger.remove()
    levels = {
        0: "WARNING",  # Default
        1: "INFO",  # -v
        2: "DEBUG",  # -vv
        3: "TRACE"  # -vvv
    }
    level = levels.get(min(verbose_level, 3), "DEBUG")
    format_str = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{"
                  "name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

    logger.add(
        sys.stderr,
        format=format_str,
        level=level,
        colorize=True,
        enqueue=True
    )

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_path,
            format=format_str,
            level=level,
            rotation="10 MB",
            compression="zip",
            enqueue=True
        )

    # If component filtering is enabled
    if components:
        original_add = logger.add

        def filtered_add(sink, **kwargs):
            # Create component filter
            def component_filter(record):
                # Always show warnings and above
                if record["level"].no >= logger.level("WARNING").no:
                    return True

                # Check if this record's module matches any enabled component
                module_parts = record["name"].split(".")
                return any(c == module_parts[0] for c in components)

            # Add the filter to kwargs
            kwargs["filter"] = component_filter
            return original_add(sink, **kwargs)

        # Replace the add method
        logger.add = filtered_add

    return logger
