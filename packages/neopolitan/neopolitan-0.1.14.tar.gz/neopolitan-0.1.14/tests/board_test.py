"""Board test"""

from neopolitan.board_functions.board import Board

def test_board_scroll():
    """Test that scrolling the data works correctly"""

    initial_data = [1,0,1,0,1,0]
    scroll_once_with_wrap_height_1 = [0,1,0,1,0,1]
    then_scroll_once_without_wrap_height_1 = [1,0,1,0,1]
    board = Board(6)
    board.set_data(initial_data)
    board.scroll(height=1)
    assert board.data == scroll_once_with_wrap_height_1,  \
        'Scrolled data did not match expected'
    board.scroll(wrap=False, height=1, pad=False)
    assert board.data == then_scroll_once_without_wrap_height_1, \
        'Scrolled data did not match expected'
    