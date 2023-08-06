"""Initialize the package logger"""

import logging
import datetime
import os
import sys

def init_logger(prep='logs/'):
    """Set up the log file"""
    # todo: prep arg validation
    # make directory if it does not exist
    # todo: is this ok?
    if not os.path.exists(prep):
        os.makedirs(prep)
    # todo: is all this formatting really necessary for a log file?
    log_time = str(datetime.datetime.now())
    filename = f'{os.getcwd()}/{prep}neopolitan {log_time}.txt'
    if sys.version_info[1] > 7:
        logging.basicConfig(filename=filename, encoding='utf=8', level=logging.DEBUG)
    else:
        logging.basicConfig(filename=filename, level=logging.DEBUG)

def get_logger():
    """Get the package logger"""
    return logging.getLogger('neopolitan')
