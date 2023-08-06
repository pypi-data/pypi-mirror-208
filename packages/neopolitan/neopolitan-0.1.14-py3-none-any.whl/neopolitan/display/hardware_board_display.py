"""Interacts with the LED board"""

import logging
from neopolitan.display.abstract_board_display import BoardDisplay
from neopolitan.const import WIDTH, HEIGHT

class HardwareBoardDisplay(BoardDisplay):
    """Draws board data"""

    def __init__(self, board, pixels, size=WIDTH*HEIGHT):
        # pylint: disable=line-too-long
        # pylint: disable=consider-using-f-string
        super().__init__(board)
        assert pixels, 'Neopixel library not initialized'
        self.pixels = pixels
        self.size = size # todo: organization
        assert board.size == self.size, \
            'board size ({0} does not meet given size ({1})'.format(board.size, size)

    def draw_board(self):
        """Sets all the LEDs in accordance with the current data"""
        assert self.board, 'No board assigned'

        flipped_data = HardwareBoardDisplay.flip(self.board.data, HEIGHT)

        for i in range(self.size):
            if i >= len(self.board.data):
                logging.warning('index %s outside of data array bounds', i)
                return
            self.pixels[i] = flipped_data[i]

    # pylint: disable=no-self-argument
    def flip(data, height=HEIGHT, start_at_first=False):
        """
        Handles flipping alternate 'rows' so that data appears as expected;
        returns the flipped data
        """

        # Every other 'column', starting with the second,
        # should be flipped such that it appears 'upside down',
        # so that when the board displays it actually appears right side up.
        assert len(data) % height == 0, \
            'Data length does not fill its last column' # todo: doesn't need to tho

        flipped_data = []
        idx = 0
        # pylint: disable=unsubscriptable-object
        while idx < len(data):
            col = data[idx:idx+height]
            if start_at_first:
                col = reversed(col)
            start_at_first = not start_at_first

            flipped_data += col
            idx += height

        return flipped_data

    # TODO: SET DATA TO MATCH!!
    def fill(self, color):
        """Fill all the pixels a given color"""
        # self.pixels.fill(color)
        self.board.fill(color)

    def fill_red(self):
        """Fill all the pixels red"""
        self.fill((255,0,0))
    def fill_green(self):
        """Fill all the pixels green"""
        self.fill((0,255,0))
    def fill_blue(self):
        """Fill all the pixels blue"""
        self.fill((0,0,255))
    def fill_white(self):
        """Fill all the pixels white"""
        self.fill((255,255,255))
    def fill_blank(self):
        """Turn all the pixels off"""
        # todo: unecessary
        self.fill((0,0,0))
