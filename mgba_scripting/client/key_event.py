from enum import Enum, auto
from key_event_type import KeyEventType
from key_type import KeyType

PUSH_TIME = 0.05 # Default key push time

class KeyEvent:
    event_type: KeyEventType
    push_time: float
    key_type: KeyType

    def __init__(self, event_type: KeyEventType, key_type: KeyType, push_time: float = PUSH_TIME) -> None:
        self.event_type = event_type
        self.key_type = key_type
        self.push_time = push_time