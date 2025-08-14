import subprocess
from typing import Callable
from pkbt.emulator import EmulatorProc
from pkbt.mgba_connection import MGBAConnection

class Orchestrator:

    def __init__(self, emu: EmulatorProc, client: MGBAConnection) -> None:
        self.emu = emu
        self.client = client

    def perform_task(self, task: Callable[[EmulatorProc, MGBAConnection], None]) -> None:
        task(self.emu, self.client)

    def exit(self) -> None:
        try:
            self.client.disconnect()
            self.emu.process.terminate()
        except Exception as e:
            print(f"Error exiting orchestrator: {e}")

if __name__ == "__main__":

    from pkbt.mgba_connection import MGBAConnection
    from pkbt.emulator import EmulatorProc
    from pkbt.config import POKEMON_RED_ROM, SERVER_SCRIPT, MGBA_DEV, INPUT_DISPLAY_SCRIPT
    import time
    from pkbt.input.key_event import KeyEvent
    from pkbt.input.key_event_type import KeyEventType
    from pkbt.input.key_type import KeyType
    from pkbt.state_manager import initialize_state_manager

    emu = EmulatorProc(MGBA_DEV, POKEMON_RED_ROM, [SERVER_SCRIPT, INPUT_DISPLAY_SCRIPT])
    client = MGBAConnection('localhost', 8888)
    orch = Orchestrator(emu, client)

    # This callback is a "task" that the orchestrator will perform
    # It will be called with the emulator and client as arguments
    def example(e, c):
        # Starting up
        initialize_state_manager()
        e.start()
        c.connect()

        # Main loop, this is where you tell it to do stuff
        for _ in range(3):
            c.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)

        # Cleanup
        orch.exit()

    # Finally, perform the task
    orch.perform_task(example)