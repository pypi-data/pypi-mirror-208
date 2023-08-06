import os
import re
import time
import inspect
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Any])


def get_asctime() -> str:
    """Returns the current time in the same format as logging %(asctime)s


    Returns:
        str: current asctime
    """
    now = datetime.now()
    return now.strftime(f"%Y-%m-%d %H:%M:%S")


def logf(
    level: Optional[int] = logging.DEBUG,
    log_args: bool = True,
    log_return: bool = True,
    max_vlen: int = 1000,
    measure_time: bool = True
) -> Callable[[T], T]:
    """
    A decorator that logs the execution time, function name, arguments, keyword arguments,
    and return value of a function using a specified log level.

    Args:
        level (int, optional): The log level to use for logging. Defaults to logging.DEBUG.
        log_args (bool, optional): Should the function arguments be logged? Defaults to True.
        log_return (bool, optional): Should function return be logged? Defaults to True.
        max_vlen (int, optional): Maximum length of the logged arguments and return values. Defaults to 1000.
        measure_time (bool, optional): Should the function execution time be measured? Defaults to True.

    Returns:
        Callable[[T], T]: The wrapped function.
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Start the timer if required and execute the function.
            start_time = time.time() if measure_time else None

            # Log function arguments if required
            if log_args:
                arg_str = f"{func.__name__}() | {str(args)[:max_vlen]} {str(kwargs)[:max_vlen]}"
            else:
                arg_str = f"{func.__name__}()"

            logger.log(level, arg_str)

            # Execute the function
            result = func(*args, **kwargs)

            if measure_time:
                end_time = time.time()
                # Calculate the execution time and format the log message.
                exec_time = end_time - start_time
                exec_time_str = f"{exec_time:.5f}s"

            # Log the return value and execution time if required
            if log_return and measure_time:
                result_str = str(result)[:max_vlen]
                log_message = f"{func.__name__}() {exec_time_str} | {result_str}"
            elif log_return:
                result_str = str(result)[:max_vlen]
                log_message = f"{func.__name__}() | {result_str}"
            elif measure_time:
                log_message = f"{func.__name__}() {exec_time_str}"
            else:
                log_message = None

            if log_message is not None:
                # Log the message using the specified level.
                logger.log(level, log_message)

            return result
        return wrapper
    return decorator


@logf()
def valid_uuid(string):
    regex = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$')
    return bool(regex.match(string))