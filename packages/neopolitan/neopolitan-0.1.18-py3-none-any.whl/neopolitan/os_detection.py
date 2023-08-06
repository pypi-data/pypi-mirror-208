"""Functions for detecting the operating machine"""

import platform
from neopolitan.log import get_logger

def on_pi():
    """Is this code being run on a 32 bit Raspberry Pi?"""  
    return (platform.machine()).strip() == 'armv7l'

def log_os():
    """Log whether this code is being run on a Pi"""
    get_logger().info('On Pi: %s', (platform.machine()).strip() == 'armv7l')
    get_logger().info(' Machine: %s', platform.machine())
