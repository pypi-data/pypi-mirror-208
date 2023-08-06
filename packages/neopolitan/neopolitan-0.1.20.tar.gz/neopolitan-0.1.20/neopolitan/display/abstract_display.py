"""
Handles initialization of the framework
that will allow LEDs to be displayed

This means initializing the pygame or neopixel libraries
"""

from abc import ABC, abstractmethod

class Display(ABC):
    """Wrapper code for initializing a display framework"""
    def __init__(self):
        self.should_exit = False # todo??

    @abstractmethod
    def draw(self):
        """Initiate the drawing of the board data"""

    @abstractmethod
    def loop(self):
        """Execution loop; used for drawing"""
