import functools
import time
from loguru import logger


def log_function(level="DEBUG", log_args=True, log_result=True):
    """Decorator for logging function calls."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"

            # Create entry log message
            entry_msg = f"Calling {func_name}"
            if log_args and (args or kwargs):
                safe_kwargs = {
                    k: v if not k.lower() in ('password', 'token', 'secret', 'key') else '***'
                    for k, v in kwargs.items()
                }
                if args and kwargs:
                    entry_msg += f" with args: {args} and kwargs: {safe_kwargs}"
                elif args:
                    entry_msg += f" with args: {args}"
                elif kwargs:
                    entry_msg += f" with kwargs: {safe_kwargs}"

            # Log entry with correct source location
            logger.opt(depth=1).log(level, entry_msg)

            # Measure execution time
            start_time = time.time()

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Log exit with timing information
                duration = time.time() - start_time
                exit_msg = f"Completed {func_name} in {duration:.3f}s"

                # Include result in log if requested
                if log_result and result is not None:
                    # Truncate long results
                    result_str = str(result)
                    if len(result_str) > 500:
                        result_str = result_str[:500] + "... [truncated]"
                    exit_msg += f" with result: {result_str}"

                logger.opt(depth=1).log(level, exit_msg)
                return result

            except Exception as e:
                # Log exception with timing information
                duration = time.time() - start_time
                logger.opt(depth=1).exception(
                    f"Exception in {func_name} after {duration:.3f}s: {str(e)}"
                )
                raise

        return wrapper

    return decorator
