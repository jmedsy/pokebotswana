from typing import Dict
from key_type import KeyType, KEY_TYPES

class KeyState:
    _key_states: Dict[str, bool] = {}

    def __init__(self):
        self.reset()

    def reset(self):
        for k in KEY_TYPES:
            self._key_states[k] = False

    def set_key(self, key_type: KeyType, is_held: bool):
        self._key_states[key_type] = is_held

    def serialize(self) -> str:
        string_repr = ""
        for k in KEY_TYPES:
            string_repr += '1' if self._key_states[k] else '0'
        return string_repr