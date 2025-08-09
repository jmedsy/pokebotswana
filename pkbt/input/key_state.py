from typing import Dict
from pkbt.input.key_type import KeyType, KEY_TYPES

KEY_STATE_CTRL_CHAR = "\x01"

class KeyState:
    _key_states: Dict[str, bool] = {}

    def __init__(self):
        self.clear()

    def clear(self):
        for k in KEY_TYPES:
            self._key_states[k] = False

    def set_key(self, key_type: KeyType, is_held: bool):
        self._key_states[key_type] = is_held

    def serialize_bitmask(self) -> str:
        # Build bitmask on client side
        keys = 0
        for i, key_type in enumerate(KEY_TYPES):
            if self._key_states[key_type]:
                keys |= (1 << i)
            bitmask_str = f"{KEY_STATE_CTRL_CHAR}{keys}\n"
        return bitmask_str