from pkbt.config import TEMP_DIR, STATE_MANAGER

def initialize_state_manager():
    """Create runtime folder if it doesn't exist"""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    """Create/initialize state manager file"""
    if not STATE_MANAGER.exists():
        STATE_MANAGER.touch()
    with open(STATE_MANAGER, "w", encoding="utf-8") as f:
        f.write("[]")