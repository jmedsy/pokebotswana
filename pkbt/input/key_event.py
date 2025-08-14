from pkbt.input.key_event_type import KeyEventType
from pkbt.input.key_type import KeyType
from pkbt.config import DEFAULT_PUSH_TIME

class KeyEvent:
    def __init__(self, event_type: KeyEventType, key_type: KeyType, push_time: float = DEFAULT_PUSH_TIME) -> None:
        self.event_type = event_type
        self.key_type = key_type
        self.push_time = push_time