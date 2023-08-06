#!/usr/local/bin/python3

import logging
import time

"""
This module prints the time taken by a function where it is decorated
"""

def ttaken(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            func(*args, **kwargs) 
            logger.info(f"func.__name__ took {elapsed_time} seconds to execute!")
            return result
        return wrapper
    return decorator

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__) 
    ttaken(logger)

if __name__ == "__main__":
    main()
