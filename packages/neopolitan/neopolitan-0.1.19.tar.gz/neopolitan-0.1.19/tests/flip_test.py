"""Tests whether the 'flip' functionality is implemented correctly"""

# pylint: disable=import-error
from neopolitan.display.hardware_board_display import HardwareBoardDisplay

# pylint: disable=pointless-string-statement
"""
0 0 0 -> 0 1 0
1 1 1    1 0 1
"""

def test_flip():
    """Test that the flip functions as expected"""
    # todo: more data tests

    initial_data = [0,1,0,1,0,1]
    expected_data = [0,1,1,0,0,1]
    height = 2

    assert HardwareBoardDisplay.flip(initial_data, height=height) == expected_data, \
        'Flipped data does not match expected'
