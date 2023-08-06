"""Test groups"""

from neopolitan.writing.letters_8 import  \
    DEFINED_UPPERCASE, DEFINED_LOWERCASE, DEFINED_SYMBOLS, DEFINED_NUMBERS
from neopolitan.writing.groups_8 import  \
    uppercase, lowercase, symbols, numbers


def test_all_letters_used():
    """Tests that all defined symbols are put into a group"""
    len_groups = len(uppercase) + len(lowercase) + len(symbols) + len(numbers)
    len_letters = DEFINED_UPPERCASE + DEFINED_LOWERCASE + DEFINED_SYMBOLS + DEFINED_NUMBERS
    assert len_groups == len_letters, 'The number of symbols defined should be the same either way'
    