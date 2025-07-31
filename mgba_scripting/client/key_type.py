from enum import Enum, auto

class KeyType(Enum):
    A = auto()
    B = auto()
    L = auto()
    R = auto()
    START = auto()
    SELECT = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

KEY_TYPES = [
    KeyType.A,
    KeyType.B,
    KeyType.L,
    KeyType.R,
    KeyType.START,
    KeyType.SELECT,
    KeyType.UP,
    KeyType.DOWN,
    KeyType.LEFT,
    KeyType.RIGHT
]