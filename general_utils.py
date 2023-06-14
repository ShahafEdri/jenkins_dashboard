# add timeit decorator

import time
import functools
from log import logger


def timeit(func):
    """
    A decorator to time a function
    :param func: function to time
    :return: None
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()

        logger.info(f"{func.__name__} took {end - start} seconds")
        return res

    return wrapper