"""Thin wrappers around Win32 window operations for Python (Windows only)."""

import time
from dataclasses import dataclass

try:
    import win32gui, win32con, win32process, win32api
except ImportError as e:
    raise RuntimeError(
        "pywin32 is required on Windows. Install with: pip install pywin32"
    ) from e

# --- Internal ---

def _top_window_from_pid(pid: int, timeout: float = 10.0) -> int:
    """Return the top-level window handle for a given PID, waiting up to timeout."""
    deadline = time.time() + timeout

    while time.time() < deadline:
        found: list[int] = []

        def cb(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid == pid and win32gui.GetWindow(hwnd, win32con.GW_OWNER) == 0:
                title = win32gui.GetWindowText(hwnd)
                # Only include windows that start with "mGBA"
                if title.startswith("mGBA"):
                    found.append(hwnd)

        win32gui.EnumWindows(cb, None)

        if found:
            return found[0]
        time.sleep(0.05)

    raise TimeoutError(f"No top-level window found for PID {pid}")

# --- Public API ---

def get_rect(hwnd: int) -> tuple[int, int, int, int]:
    """Return (x, y, width, height) for the given window handle."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return left, top, right - left, bottom - top

def get_size(hwnd: int) -> tuple[int, int]:
    """Return (width, height) for the given window handle."""
    _, _, w, h = get_rect(hwnd)
    return w, h

def get_width(hwnd: int) -> int:
    """Return the width of the given window handle."""
    return get_size(hwnd)[0]

def get_height(hwnd: int) -> int:
    """Return the height of the given window handle."""
    return get_size(hwnd)[1]

def get_position(hwnd: int) -> tuple[int, int]:
    """Return (x, y) position (top-left corner) of the given window handle."""
    left, top, _, _ = get_rect(hwnd)
    return left, top

def move(hwnd: int, x: int, y: int) -> None:
    """Move the window to (x, y) without resizing."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd, None, x, y, 0, 0,
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )

def move_resize(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    """Move and resize the window."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd, None, x, y, w, h,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
    )

def get_primary_screen_size() -> tuple[int, int]:
    """Width, height of the primary display in pixels."""
    w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return w, h

def get_primary_screen_width() -> int:
    return get_primary_screen_size()[0]

def get_primary_screen_height() -> int:
    return get_primary_screen_size()[1]

def minimize_windows_starting_with(prefix: str) -> None:
    """Minimize all visible windows that start with the given prefix."""
    def cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if title.startswith(prefix):
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    
    win32gui.EnumWindows(cb, None)

def arrange_in_grid(windows: list["Window"], num_cols: int, num_rows: int) -> None:
    """Arrange the given windows in a grid of the given size."""
    for i, w in enumerate(windows):
        col = i % num_cols
        row = i // num_cols
        w.move(col * w.width(), row * w.height())

def arrange_windows_auto_grid(windows: list["Window"], max_width: int) -> None:
    """Arrange windows left to right, top to bottom, wrapping when they don't fit."""
    if not windows:
        return
    
    current_x = 0
    current_y = 0
    row_height = 0
    
    for w in windows:
        # Check if this window fits on the current row
        if current_x + w.width() > max_width and current_x > 0:
            # Move to next row
            current_x = 0
            current_y += row_height
            row_height = 0
        
        # Position the window
        w.move(current_x, current_y)
        
        # Update position for next window
        current_x += w.width()
        row_height = max(row_height, w.height())

@dataclass(frozen=True)
class Window:
    hwnd: int

    @classmethod
    def from_pid(cls, pid: int, timeout: float = 10.0) -> "Window":
        return cls(_top_window_from_pid(pid, timeout))

    def rect(self) -> tuple[int, int, int, int]:
        return get_rect(self.hwnd)

    def size(self) -> tuple[int, int]:
        return get_size(self.hwnd)

    def width(self) -> int:
        return get_width(self.hwnd)

    def height(self) -> int:
        return get_height(self.hwnd)

    def position(self) -> tuple[int, int]:
        return get_position(self.hwnd)

    def move(self, x: int, y: int) -> None:
        move(self.hwnd, x, y)

    def move_resize(self, x: int, y: int, w: int, h: int) -> None:
        move_resize(self.hwnd, x, y, w, h)
