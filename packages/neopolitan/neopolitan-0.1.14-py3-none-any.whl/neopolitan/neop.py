"""Main application function"""

# pylint: disable=fixme
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=import-outside-toplevel
# pylint: disable=logging-fstring-interpolation

import getopt
import sys
import time

from neopolitan.board_functions.board import Board
# from board_functions.colors import OFF, ON
from neopolitan.board_functions.board_data import default_board_data
from neopolitan.writing.data_transformation import str_to_data
from neopolitan.os_detection import on_pi
from neopolitan.log import init_logger, get_logger # why tf is this erroring?
# pylint: disable=wildcard-import
from neopolitan.const import *


def main(events=None, initialize_logger=False):
    """Make a very simple display"""

    if initialize_logger:
        init_logger()
    logger = get_logger()

    board_data = process_arguments()

    width = WIDTH
    height = HEIGHT
    size = width*height
    board = None
    display = None
    board_display = None

    # todo: make better
    if board_data.graphical:
        from neopolitan.display.graphical_display import GraphicalDisplay
        board = Board(size)
        display = GraphicalDisplay(board=board)
    else:
        from neopolitan.display.hardware_display import HardwareDisplay
        display = HardwareDisplay(WIDTH*HEIGHT)
        board_display = display.board_display
        board = board_display.board

    board.set_data(str_to_data(board_data.message))

    while not display.should_exit:
        # process events
        # todo: make better
        while events and not events.empty():
            event = events.get()
            logger.info(f'event: {event}')
            event_list = event.split()
            first = event_list[0]
            if first == 'exit':
                return
            if first == 'say':
                logger.info(f'say: {event}')
                # todo: better handling: this is unintuitive
                message = ' '
                for word in event_list[1:]:
                    message += word + ' '
                logger.info(message)
                board.set_data(str_to_data(message))
                logger.info(f'set message: {message}')
            else: # try board data events
                board_data = process_board_data_events(board_data, event_list)
            # todo: error handling
        display.loop()
        if board_data.scroll_speed:
            board.scroll(wrap=board_data.should_wrap)

        time.sleep(board_data.scroll_wait)

    del display

def process_arguments():
    """Process the command line arguments and return them as a BoardData object"""
    logger = get_logger()
    board_data = default_board_data

    argument_list = sys.argv[1:]
    options = 'm:g:s:w:'
    long_options = ['message=', 'graphical=', 'scroll=', 'wrap=']
    try:
        # args, vals
        args = getopt.getopt(argument_list, options, long_options)
        if len(args[0]) > 0:
            for arg, val in args[0]:
                if arg in ('-m', '--message'):
                    board_data.message = val
                elif arg in ('-g', '--graphical'):
                    if val == 'True':
                        board_data.graphical = True
                    elif val == 'False':
                        board_data.graphical = False
                    else:
                        logger.warning(f'Could not parse "graphical" argument: {val}')
                elif arg in ('-s', 'scroll'):
                    if val in ('slow', 'medium', 'fast'):
                        board_data.scroll_speed = val
                        if val == 'slow':
                            board_data.scroll_wait = SCROLL_FAST
                        elif val == 'medium':
                            board_data.scroll_wait = SCROLL_MED
                        else: # fast
                            board_data.scroll_wait = SCROLL_SLOW
                    else:
                        logger.warning(f'Invalid scroll speed: {val}')
                elif arg in ('-w', 'wrap'):
                    if val == 'True':
                        board_data.should_wrap = True
                    elif val == 'False':
                        board_data.should_wrap = False
                    else:
                        logger.warning(f'Could not parse "wrap" argument: {val}')
        # --- Verify OS for graphical/hardware
        if on_pi() and board_data.graphical:
            logger.warning('This code cannot be run in graphical' \
                            ' mode on a Raspberry Pi, setting graphical to False')
            board_data.graphical = False
        if not on_pi() and not board_data.graphical:
            logger.warning('This code cannot be run in hardware mode when not run'\
            ' on a Raspberry Pi, setting graphical to True')
            board_data.graphical = True
        # --- Done verifying
        logger.info(f'message set to: {board_data.message}')
        logger.info(f'graphical set to: {board_data.graphical}')
        logger.info(f'scroll speed set to: {board_data.scroll_speed} ({board_data.scroll_wait})')
        logger.info(f'wrap set to: {board_data.should_wrap}')

    except getopt.error as err:
        logger.error(f'getopt error: {err}')

    return board_data

def process_board_data_events(board_data, event_list):
    """Manipulate board data according to events"""

    logger = get_logger()

    first = event_list[0]
    if first == 'speed':
        try:
            speed = event_list[1]
        # pylint: disable=broad-except
        except Exception as err:
            # todo: better explanation
            logger.warning('No second value provided, %s', err)
        if speed == 'slow':
            board_data.scroll_slow()
            logger.info('set speed: slow')
        elif speed == 'medium':
            board_data.scroll_medium()
            logger.info('set speed: medium')
        elif speed == 'fast':
            board_data.scroll_fast()
            logger.info('set speed: fast')
        else:
            try:
                speed = float(speed)
                board_data.set_scroll_wait(speed)
                logger.info(f'set speed: {speed}')
            except ValueError:
                logger.warning(f'Cannot parse speed: {speed}')
    elif first == 'wrap':
        try:
            wrap = event_list[1]
        # pylint: disable=broad-except
        except Exception as err:
            # todo: better explanation
            logger.warning('No second value provided, %s', err)
        if wrap in ('True', '1'):
            board_data.should_wrap = True
            logger.info('set wrap: True')
        elif wrap in ('False', '0'):
            board_data.should_wrap = False
            logger.info('set wrap: False')
        else:
            logger.warning('Cannot parse wrap: %s', wrap)

    return board_data

if __name__ == '__main__': # todo: is this still true when running from the thread?
    main(initialize_logger=True) # try False maybe? for testing
