#!/usr/bin/env python3

#  Derived from https://wiki.python.org/moin/PythonDecoratorLibrary#Retry

#
#
# retry.py
#
# Decorator for retrying a function call depending on what
# exceptions were raised.
#
import logging
import time
from functools import wraps
from typing import Callable
from typing import List
from typing import Optional


def retry(
    exceptions: List, tries: int = 4, delay: int = 3, backoff: int = 2, logger: logging.Logger = None, reset: Optional[Callable] = None
) -> callable:
    """
    Retry calling the decorated function using an exponential backoff.

    @retry((MyRetryableErrorClass,))
    def thing:
        ...
    Note: store in a tuple to avoid:
    "catching classes that do not inherit from BaseException is not allowed"

    :param logger: Logger to use. If None, do nothing.
    :param backoff: Backoff multiplier (e.g. value of 2 will double the delay each retry).
    :param delay: Initial delay between retries in seconds.
    :param tries: Number of times to try (not retry) before giving up.
    :param exceptions: The exception to check. may be a tuple of exceptions to check.
    :param reset: A callable to call before sleeping between retries
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if logger:
                        msg = f"{e}, Retrying in {mdelay} seconds..."
                        logger.warning(msg)
                    if reset:
                        reset()
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry
