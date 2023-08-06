"""All groups of symbols for height of 8"""

# pylint: disable=fixme
# ToDo: fix this
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from neopolitan.writing.letters_8 import *

uppercase = [
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    J,
    K,
    L,
    M,
    N,
    O,
    P,
    Q,
    R,
    S,
    T,
    U,
    V,
    W,
    X,
    Y,
    Z,
]

lowercase = [
    a,
    b,
    c,
    d,
    e,
    f,
    g,
    h,
    i,
    j,
    k,
    l,
    m,
    n,
    o,
    p,
    q,
    r,
    s,
    t,
    u,
    v,
    w,
    x,
    y,
    z,
]

symbols = {
    "$": DOLLAR,
    "%": PERCENT,
    "↑": UP,
    "↓": DOWN,
    "(": OPEN,
    ")": CLOSE,
    "-": MINUS,
    ".": PERIOD,
    ":": COLON,
    "=": EQUALS,
    "~": TILDE,
    "!": EXCLAMATION,
    "@": AT,
    "&": AMPERSAND,
    "*": ASTERISK,
    "?": QUESTION,
    "<": LESSTHAN,
    ">": GREATERTHAN,
    ";": SEMICOLON,
    "|": PIPE,
    "{": OPENCURLY,
    "}": CLOSECURLY,
    '"': DOUBLEQUOTE,
    "'": SINGLEQUOTE,
}

numbers = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]

def space(height=8):
    """Returns a space (empty column) of specified height"""
    return [[height-1]]
