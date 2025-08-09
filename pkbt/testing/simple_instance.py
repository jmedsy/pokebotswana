import subprocess
from tkinter import W
import tomllib
from pathlib import Path
from pkbt.windows.windowing import Window, get_primary_screen_width

"""Import mGBA path from config"""
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
with Path (CONFIG_PATH).open("rb") as f:
    config = tomllib.load(f)
    mgba_path = config["paths"]["mgba_dev"]
    input_display_script = config["paths"]["scripts"]["input_display"]
    pokemon_red_rom = config["paths"]["roms"]["pokemon_red"]

if __name__ == "__main__":
    posX = 0
    posY = 0
    for i in range(30):
        p1 = subprocess.Popen([
            mgba_path,
            "--script",
            input_display_script,
            pokemon_red_rom])
        w1 = Window.from_pid(p1.pid)
        if posX + w1.width() > get_primary_screen_width():
            posX = 0
            posY += w1.height()
        w1.move(posX, posY)
        posX += w1.width()