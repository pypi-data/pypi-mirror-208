"""Functions for detecting the operating machine"""

import platform
from neopolitan.log import get_logger

def on_pi():
    """Is this code being run on a 32 bit Raspberry Pi?"""
    yes = (platform.machine()).strip() == 'armv7l'
    get_logger().info('On Pi: %s', yes)
    get_logger().info('Machine: %s', platform.machine())
    return yes
