"""Functions for detecting the operating machine"""

import platform

def on_pi():
    """Is this code being run on a 32 bit Raspberry Pi?"""
    return (platform.machine()).strip() == 'armv7l'

def test():
    pass
