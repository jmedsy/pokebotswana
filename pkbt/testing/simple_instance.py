import subprocess
import tomllib
from pathlib import Path
import time
import win32gui, win32con, win32process

"""Import mGBA path from config"""
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
with Path (CONFIG_PATH).open("rb") as f:
    config = tomllib.load(f)
    mgba_path = config["paths"]["mgba_dev"]
    input_display_script = config["paths"]["scripts"]["input_display"]
    pokemon_red_rom = config["paths"]["roms"]["pokemon_red"]

if __name__ == "__main__":
    p1 = subprocess.Popen([
        mgba_path,
        "--script",
        input_display_script,
        pokemon_red_rom])