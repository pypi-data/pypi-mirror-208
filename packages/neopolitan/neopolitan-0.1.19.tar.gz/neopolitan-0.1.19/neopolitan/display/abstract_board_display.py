"""
Handles taking board data and running the
necessary code to get LEDs to show up

This means running 'pygame.draw(...)' or 'pixels.turnOn(...)'
"""

from abc import ABC, abstractmethod

# pylint: disable=too-few-public-methods
class BoardDisplay(ABC):
    """Utilizes board data to turn on/off LEDs"""

    def __init__(self, board):
        # todo: error checking on board
        self.board = board

    @abstractmethod
    def draw_board(self):
        """Use board data to turn on/off individual LEDs"""
