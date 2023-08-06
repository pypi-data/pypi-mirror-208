"""Takes letters as defined and transforms them into usable data"""

# pylint: disable=fixme
# Todo: location?
# todo
from math import floor
import logging
from neopolitan.writing.groups_8 import uppercase, lowercase, symbols, numbers
from neopolitan.board_functions.colors import ON, OFF

def character_to_symbol(char):
    """Gets the symbol for the character"""
    ascii_val = ord(char)
    # todo: make everything like for symbols?
    if char == ' ':
        # todo
        return 'space'
    if 97 <= ascii_val < 123:
        return lowercase[ascii_val-97]
    if 65 <= ascii_val < 91:
        return uppercase[ascii_val-65]
    if 48 <= ascii_val < 58:
        return numbers[ascii_val-48]
    if char in symbols:
        return symbols[char]
    logging.warning('Cannot find char: %s', char)
    return []

def frame_length(sym):
    """Returns the highest multiple of 8 above the largest index in the symbol array.
    This makes it so the frame has the correct length, since it should 'fill' all columns it uses"""
    if sym == 'space':
        return 8*2
    sym_len = len(sym)
    last_idx = sym_len-1
    last_col = sym[last_idx]
    len_last_col = len(last_col)
    last_col_idx = len_last_col-1
    last_val = last_col[last_col_idx]
    # round up to next multiple of 8
    ret = -1
    if last_val % 8 == 0:
        ret = last_val
    else:
        ret = 8 * (floor(last_val / 8.0)+1)
    return ret

# Todo: dictionary: idx=color instead?
def symbol_to_array(sym, color=(255,255,255), off=None):
    """Takes a defined symbol and returns an array where the symbol
        is defined by indices of 'color' and 'off' values are None"""
    frame = [off for i in range(frame_length(sym))]
    if sym == 'space':
        # todo
        return frame
    for col in sym:
        for val in col:
            frame[val] = color
    return frame

def str_to_data(msg, color=ON, add_space=4):
    """Converts a string into usable display data"""

    data = []
    line = [OFF for i in range(8)] # todo: height?
    for char in msg:
        arr = symbol_to_array(character_to_symbol(char), color=color, off=OFF)
        data = data + arr + line
    data += line*add_space
    return data
