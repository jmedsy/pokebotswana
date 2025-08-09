import subprocess
import tomllib
from pathlib import Path
import time
import win32gui, win32con, win32process

"""Import mGBA path from config"""
with Path ("../../config.toml").open("rb") as f:
    config = tomllib.load(f)
    mgba_path = config["paths"]["mgba_dev"]
    pokemon_red_rom = config["paths"]["pokemon_red_rom"]

def top_window_from_pid(pid, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = []
        def cb(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd): return
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid == pid:
                # Skip tool/child windows
                if win32gui.GetWindow(hwnd, win32con.GW_OWNER) == 0:
                    result.append(hwnd)
        win32gui.EnumWindows(cb, None)
        if result: return result[0]
        time.sleep(0.05)
    raise TimeoutError("No top-level window for pid")

def move_and_resize(hwnd, x, y, w, h):
    # Ensure it's not minimized/hidden
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(hwnd, None, x, y, w, h,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)

def move_only(hwnd, x, y):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # un-minimize if needed
    win32gui.SetWindowPos(
        hwnd, None, x, y, 0, 0,
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )

def get_window_rect(hwnd):
    """Return (x, y, width, height) for the given window handle."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return left, top, right - left, bottom - top

def get_window_size(hwnd):
    """Return (width, height) of the given window handle."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return right - left, bottom - top # Width, Height

def get_window_width(hwnd):
    return get_window_size(hwnd)[0]

def get_window_height(hwnd):
    return get_window_size(hwnd)[1]

if __name__ == "__main__":

    # Launch two independent instances
    p1 = subprocess.Popen([mgba_path, pokemon_red_rom])
    p2 = subprocess.Popen([mgba_path, pokemon_red_rom])

    # Wait for their main windows to exist, then position
    h1 = top_window_from_pid(p1.pid)
    h2 = top_window_from_pid(p2.pid)

    # Example layout: left and right halves of a 1920x1080 screen
    move_only(h1, 0, 0)
    move_only(h2, 960, 0)

    # for _ in range(1):
    #     proc = subprocess.Popen([exe, pokemon_red_rom])

"""
If you wanted to do something non-blocking you would do the following (Windows)

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

if __name__ == "__main__":
    proc = subprocess.Popen([exe],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True)
    time.sleep(3)
    proc.terminate()
"""