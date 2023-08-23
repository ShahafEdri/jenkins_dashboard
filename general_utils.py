# add timeit decorator

import time
import functools
from log import logger
import argparse


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

def validate_pickle_file_name(value):
    if not value.endswith('.pickle'):
        raise argparse.ArgumentTypeError("File name must end with '.pickle'")
    return value
