"""Tests various ways that board data is manipulated"""

from neopolitan.board_functions.board_data import default_board_data
from neopolitan.neop import process_board_data_events
from neopolitan.const import SCROLL_FAST

def test_board_data_event_processing():
    """Verify that processing events into board data object handles as expected"""

    # todo: more events

    board_data = default_board_data
    assert board_data is not None, 'Board data needs to be defined first'

    board_data = process_board_data_events(board_data, ['speed', 'fast'])
    assert board_data.scroll_speed == 'fast'\
        and board_data.scroll_wait == SCROLL_FAST,\
        'Scroll wait speed should be set to fast'

    board_data = process_board_data_events(board_data, ['speed', '0.7'])
    assert board_data.scroll_speed == 'user-defined'\
        and board_data.scroll_wait == 0.7,\
        'Scroll wait speed should be set to 0.7'

    board_data = process_board_data_events(board_data, ['speed', 'banana'])
    assert board_data.scroll_speed == 'user-defined'\
        and board_data.scroll_wait == 0.7,\
        'Scroll wait speed should not have changed'
