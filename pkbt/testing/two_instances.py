import subprocess
from tkinter import W
import tomllib
from pathlib import Path
from pkbt.windows.windowing import Window, get_primary_screen_width
import time

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


def initialize_state_manager():
    """Ensure the state_manager file exists and contains an empty array"""
    if not Path(STATE_MANAGER).exists():
        Path(STATE_MANAGER).touch()
    with open(STATE_MANAGER, "w", encoding="utf-8") as f:
        f.write("[]")


def start_processes(numInstances: int) -> list[subprocess.Popen]:

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

    return processes


if __name__ == "__main__":

    initialize_state_manager()
    processes = start_processes(2)

    print("hello")

    # posX = 0
    # posY = 0

    # for i in range(2):

    #     p1 = subprocess.Popen([
    #         mgba_path,
    #         "--script",
    #         server_script,
    #         pokemon_red_rom])

    #     w1 = Window.from_pid(p1.pid)

    #     if posX + w1.width() > get_primary_screen_width():
    #         posX = 0
    #         posY += w1.height()

    #     w1.move(posX, posY)
        
    #     posX += w1.width()