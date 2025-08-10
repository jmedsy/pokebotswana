import subprocess
from tkinter import W
import tomllib
from pathlib import Path
from pkbt.input.key_type import KeyType
from pkbt.windowing import Window, get_primary_screen_width
from pkbt.client.mgba_connection import MGBAConnection
import time
from pkbt.image_processing import save_with_crosshair, pixel_rgb, pixel_hex
import threading
from pkbt.input.key_event import KeyEvent
from pkbt.input.key_event_type import KeyEventType

"""Import mGBA path from config"""
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
with Path (CONFIG_PATH).open("rb") as f:
    config = tomllib.load(f)
    mgba_path = config["paths"]["mgba_dev"]
    input_display_script = config["paths"]["scripts"]["input_display"]
    server_script = config["paths"]["scripts"]["server"]
    pokemon_red_rom = config["paths"]["roms"]["pokemon_red"]
    pokemon_sapphire_rom = config["paths"]["roms"]["pokemon_sapphire"]
    pokemon_emerald_rom = config["paths"]["roms"]["pokemon_emerald"]
    STATE_MANAGER = config["paths"]["state_manager"]
    TEMP = config["paths"]["temp"]


def initialize_state_manager():
    """Ensure the temp directory and state_manager file exist and contain an empty array"""
    # Create temp directory if it doesn't exist
    temp_dir = Path(TEMP)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure the state_manager file exists and contains an empty array
    if not Path(STATE_MANAGER).exists():
        Path(STATE_MANAGER).touch()
    with open(STATE_MANAGER, "w", encoding="utf-8") as f:
        f.write("[]")


def start_processes(numInstances: int) -> list[subprocess.Popen]:
    """Start mGBA processes and return a list of processes"""
    # Keep track of new instance positions
    posX = 0
    posY = 0

    processes = []

    for _ in range(numInstances):

        # Start mGBA process
        p = subprocess.Popen([
            mgba_path,
            "--script",
            server_script,
            pokemon_emerald_rom])

        # Get window
        w = Window.from_pid(p.pid)

        # Place window in next sequential position
        if posX + w.width() > get_primary_screen_width():
            posX = 0
            posY += w.height()
        w.move(posX, posY)

        # Update position for future windows
        posX += w.width()

        # Add process to list
        processes.append(p)

    return processes


def start_clients(processes: list[subprocess.Popen]) -> list[MGBAConnection]:
    """Start MGBA connections and return a list of connections"""
    clients = []
    for proc in processes:
        port = 8888 + processes.index(proc)
        client = MGBAConnection('localhost', port)
        client.connect()
        clients.append(client)

    return clients

import random

def wait_random_short():
    """Wait for a random time between 0 and 0.1 seconds."""
    time.sleep(random.uniform(0, 1))

def wait_random_long():
    """Wait for a random time between 0 and 0.1 seconds."""
    time.sleep(random.uniform(1, 2))


total_count = 0
acceptable_mistakes=  ['#395200', '#d6d6bd']

def client_thread_fn(idx, process: subprocess.Popen, client: MGBAConnection):
    global total_count

    try:
        crosshair_x = 40
        crosshair_y = 53
        blueish_hex = '#4a84d6'
        found = False
        while not found:
            client.reset_game()
            time.sleep(1)

            # Proceed through the title screen
            time.sleep(4.5)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(2)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(2)
            wait_random_short()

            # Continue up to naming prompts
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(5)
            wait_random_short()

            # Decline naming
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)

            # Open menu >> Pokemon
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.START))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(2)

            # Move to Beldum and open
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)
            client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(1)

            client.save_screenshot_to_file(f"{idx}foo.png")
            time.sleep(2.5)
            total_count += 1
            print(f"Total count: {total_count}")
            if blueish_hex != pixel_hex(f"{TEMP}/{idx}foo.png", crosshair_x, crosshair_y) and pixel_hex(f"{TEMP}/{idx}foo.png", crosshair_x, crosshair_y) not in acceptable_mistakes:
                print(f"Found on {idx} with color {pixel_hex(f"{TEMP}/{idx}foo.png", crosshair_x, crosshair_y)}")
                found = True

        # for i in range(30):
        #     client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        #     time.sleep(0.5)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.START))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.UP))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.UP))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        # time.sleep(1)
        # client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
    except Exception as e:
        print(f"[Client {idx}] Exception: {e}")


if __name__ == "__main__":
    
    initialize_state_manager()
    processes = start_processes(8)
    clients = start_clients(processes)

    # Gives me time to set fast forward manually
    time.sleep(2)

    crosshair_x = 40
    crosshair_y = 53

    threads = []
    for idx, (process, client) in enumerate(zip(processes, clients)):
        t = threading.Thread(target=client_thread_fn, args=(idx, process, client), daemon=True)
        t.start()
        threads.append(t)

    # Optionally, join threads if you want the main program to wait for them
    for t in threads:
        t.join()

    # time.sleep(15)


    # clients[0].save_screenshot_to_file("foo.png")

    # clients[0].reset_game()
    # time.sleep(1)
    # clients[1].reset_game()

    # crosshair_x = 40
    # crosshair_y = 53

    # save_with_crosshair(f"{TEMP}/foo.png", f"{TEMP}/foo_with_crosshair.png", crosshair_x, crosshair_y)
    # print(pixel_rgb(f"{TEMP}/foo.png", crosshair_x , crosshair_y))
    # print(pixel_hex(f"{TEMP}/foo.png", crosshair_x, crosshair_y))

    # time.sleep(2)