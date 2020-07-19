'''
	This script is to create a logger object and return it to the script that called it.
    Author: Donovan Torgerson
    Email: Donovan@Torgersonlabs.com
'''
import logging

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s %(lineno)d')

def get_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
