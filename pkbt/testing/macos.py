if __name__ == "__main__":
    from pkbt.mgba_connection import MGBAConnection
    from pkbt.emulator import EmulatorProc
    from pkbt.config import POKEMON_RED_ROM, SERVER_SCRIPT, MGBA_DEV, INPUT_DISPLAY_SCRIPT
    from pkbt.orchestrator import Orchestrator
    from pkbt.state_manager import initialize_state_manager
    import time
    from pkbt.input.key_event import KeyEvent, KeyEventType
    from pkbt.input.key_type import KeyType

    emu = EmulatorProc(MGBA_DEV, POKEMON_RED_ROM, [SERVER_SCRIPT, INPUT_DISPLAY_SCRIPT])
    client = MGBAConnection('localhost', 8888)
    orch = Orchestrator(emu, client)
    
    initialize_state_manager()
    orch.emu.start()
    time.sleep(5) # Wait for the emulator to start
    orch.client.connect()

    def task(e, c):
        for _ in range(0, 10):
            c.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)

    orch.perform_task(task)