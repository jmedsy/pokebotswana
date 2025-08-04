from enum import Enum, auto

class KeyType(Enum):
    A = auto()
    B = auto()
    SELECT = auto()
    START = auto()
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()
    R = auto()
    L = auto()

"""Ensure order of keys matches that specified in server code"""
KEY_TYPES = [
    KeyType.A,
    KeyType.B,
    KeyType.SELECT,
    KeyType.START,
    KeyType.RIGHT,
    KeyType.LEFT,
    KeyType.UP,
    KeyType.DOWN,
    KeyType.R,
    KeyType.L
]