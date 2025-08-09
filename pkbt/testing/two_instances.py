import subprocess
from tkinter import W
import tomllib
from pathlib import Path
from pkbt.windows.windowing import Window, get_primary_screen_width
from pkbt.client.mgba_connection import MGBAConnection
import time
from pkbt.image_processing import save_with_crosshair, pixel_rgba, pixel_hex

"""Import mGBA path from config"""
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
with Path (CONFIG_PATH).open("rb") as f:
    config = tomllib.load(f)
    mgba_path = config["paths"]["mgba_dev"]
    input_display_script = config["paths"]["scripts"]["input_display"]
    server_script = config["paths"]["scripts"]["server"]
    pokemon_red_rom = config["paths"]["roms"]["pokemon_red"]
    STATE_MANAGER = config["paths"]["state_manager"]
    DATA = config["paths"]["data"]


def initialize_state_manager():
    """Ensure the state_manager file exists and contains an empty array"""
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
            pokemon_red_rom])

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


if __name__ == "__main__":

    initialize_state_manager()
    processes = start_processes(2)

    clients = start_clients(processes)

    time.sleep(5)

    clients[0].save_screenshot_to_file("foo.png")

    clients[0].reset_game()
    time.sleep(1)
    clients[1].reset_game()

    save_with_crosshair(f"{DATA}/foo.png", f"{DATA}/foo_with_crosshair.png", 100, 100)
    print(pixel_rgba(f"{DATA}/foo.png", 100, 100))
    print(pixel_hex(f"{DATA}/foo.png", 100, 100))