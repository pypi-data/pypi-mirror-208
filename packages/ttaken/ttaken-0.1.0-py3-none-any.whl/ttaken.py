import logging
import time

def ttaken(logger):
    """
    A decorator that logs the time taken by a function.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"func.__name__) took {elapsed_time..4f} seconds to execute!")
            return result
        return wrapper
    return decorator  
