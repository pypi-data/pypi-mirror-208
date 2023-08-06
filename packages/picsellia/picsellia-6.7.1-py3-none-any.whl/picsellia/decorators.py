import logging
import os
import time
import warnings
from functools import wraps

from beartype.roar import (
    BeartypeCallHintPepParamException,
    BeartypeDecorHintPep585DeprecationWarning,
)

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)

logger = logging.getLogger("picsellia")

try:
    custom_logging = os.environ["PICSELLIA_SDK_CUSTOM_LOGGING"]
except KeyError:
    custom_logging = False


def exception_handler(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BeartypeCallHintPepParamException as e:
            message = str(e).split("@beartyped ")[1]
            raise TypeError(message) from e

    inner: func

    return inner


def retry(exceptions, total_tries=4, initial_wait=0.5, backoff_factor=2):
    """
    calling the decorated function applying an exponential backoff.
    Arguments:
        exceptions: Exception(s) that trigger a retry, can be a tuple
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
    """

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    _tries -= 1
                    if _tries == 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries

    return retry_decorator
