#!/usr/local/bin/python3

import logging
import time
import socket

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
            FORMAT = '%(asctime)s %(clientip)-15s %(hostname)-8s %(message)s'
            logging.basicConfig(format=FORMAT)
            ## getting the hostname by socket.gethostname() method
            hostname = socket.gethostname() 
            ip_address = socket.gethostbyname(hostname) 
            d = {'clientip': ip_adress, 'hostname': hostname}
            logger.info(f"func.__name__ took {elapsed_time} seconds to execute!")
            return result
        return wrapper
    return decorator
