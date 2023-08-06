"""Draws a board"""

import logging
import pygame
from neopolitan.display.abstract_board_display import BoardDisplay
from neopolitan.const import WIDTH, HEIGHT
# from board import Board

class GraphicalBoardDisplay(BoardDisplay):
    """Draws board data"""
    width = 0
    height = 0
    board = None

    def __init__(self, board, width=WIDTH, height=HEIGHT):
        # pylint: disable=line-too-long
        # pylint: disable=consider-using-f-string
        super().__init__(board)
        assert board.size == width * height, 'board size ({0} does not meet given dimensions {1}x{2}'.format(board.size, width, height)
        self.width = width
        self.height = height

    # pylint: disable=arguments-differ
    def draw_board(self, screen, space, size):
        """Draw all the 'lights' in the board"""
        assert self.board, 'No board assigned'

        for i in range(self.width * self.height):
            if i >= len(self.board.data):
                logging.warning('index %i outside of data array bounds', i)
                return
            color = self.board.data[i]
            row = self.get_row(i)
            col = self.get_col(i)

            if not self.board.data[i]:
                continue
            pos = (int(col * space + space/2), int(row * space + space/2))
            pygame.draw.circle(screen, color, pos, size)

    def get_row(self, idx):
        """Gets the row # from the index"""
        return idx % self.height
    def get_col(self, idx):
        """Gets the col # from the idx"""
        return idx // self.height
    