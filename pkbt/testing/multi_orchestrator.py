from pkbt.emulator import EmulatorProc
from pkbt.orchestrator import Orchestrator
from pkbt.mgba_connection import MGBAConnection
from pkbt.config import POKEMON_RED_ROM, SERVER_SCRIPT, MGBA_DEV
from pkbt.input.key_event import KeyEvent
from pkbt.input.key_event_type import KeyEventType
from pkbt.input.key_type import KeyType
from pkbt.state_manager import initialize_state_manager
import time
import threading
from typing import Callable
from pkbt.windowing import Window, arrange_in_grid


"""Tweak these for test"""
NUM_INSTANCES = 8
STARTING_PORT = 8888 # Leave me alone


def task(e, c):
    """The actions that will be performed by each orchestrator"""
    e.start()
    c.connect()
    for _ in range(6):
        c.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(1)


def run_orchestrator(idx: int, task_callback: Callable[[EmulatorProc, MGBAConnection], None]):
    """The function that will be called to run the orchestrator thread"""
    # Create an orchestrator for each instance
    orch = Orchestrator(
        EmulatorProc(MGBA_DEV, POKEMON_RED_ROM, [SERVER_SCRIPT]),
        MGBAConnection('localhost', STARTING_PORT + idx))

    # Perform the task
    orch.perform_task(task_callback)

    # Exit the orchestrator
    orch.exit()


"""Putting it all together and running it"""
initialize_state_manager()

# Create the orchestrators
orchestrators = []
for i in range(NUM_INSTANCES):
    orch = Orchestrator(
        EmulatorProc(MGBA_DEV, POKEMON_RED_ROM, [SERVER_SCRIPT]),
        MGBAConnection('localhost', STARTING_PORT + i))
    orchestrators.append(orch)

# Start the emulators
emu_pids: list[int] = []
for i in range(NUM_INSTANCES):
    pid = orchestrators[i].perform_task(lambda e, c: e.process.pid if e.start() else None)
    emu_pids.append(pid)

# Arrange the windows in a grid
print(emu_pids)
windows = [Window.from_pid(pid) for pid in emu_pids]
arrange_in_grid(windows, num_cols=4, num_rows=2)

"""
threads = []
for i in range(NUM_INSTANCES):
    t = threading.Thread(target=run_orchestrator, args=(i, task), daemon=True)
    t.start()
    threads.append(t)

# Without this, the main program will exit immediately, 
# causing daemon threads to be killed before they complete their tasks
for t in threads:
    t.join()
"""