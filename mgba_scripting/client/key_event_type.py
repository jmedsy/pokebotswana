from enum import Enum, auto

class KeyEventType(Enum):
    PUSH = auto()
    HOLD = auto()
    RELEASE = auto()