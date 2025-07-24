import time
import cv2
import numpy as np
import time
from playsound import playsound
import platform
from backend.logic.virtual_camera import VC, bgr_to_hex
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
SHINY_HEX = os.getenv('SHINY_HEX')

# --- Config ---
inspect_x, inspect_y = 211, 80
zoom_size = 7
scale_factor = 8
crosshair_color = (0, 255, 0)  # neon green
line_len = 5
font = cv2.FONT_HERSHEY_SIMPLEX

# Warm-up
VC.warm_up()

frame = VC.read_frame()
cv2.imshow('OBS Virtual Cam Preview', frame)
cv2.waitKey(10)
time.sleep(0.2)

def send_key_to_all_mgba(key, action='key'):
    subprocess.run([
        'xdotool', 'search', '--name', 'mGBA', action, '--window', '%@', key
    ])

def send_ctrl_r_to_all_mgba():
    for cmd in [
        ['xdotool', 'search', '--name', 'mGBA', 'keydown', '--window', '%@', 'ctrl'],
        ['xdotool', 'search', '--name', 'mGBA', 'key', '--window', '%@', 'r'],
        ['xdotool', 'search', '--name', 'mGBA', 'keyup', '--window', '%@', 'ctrl'],
    ]:
        print("Running:", " ".join(cmd))
        subprocess.run(cmd)

def send_p_to_window(window_title_substring):
    # Find all windows matching the substring
    result = subprocess.run(['xdotool', 'search', '--name', window_title_substring], capture_output=True, text=True)
    window_ids = result.stdout.strip().split('\n')
    for wid in window_ids:
        if wid:
            subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
            subprocess.run(['xdotool', 'key', 'p'])

def restart_game():
    send_p_to_window('Player 1')

def fast_forward(arg: bool):
    # Tab key down/up
    if arg:
        send_key_to_all_mgba('Tab', action='keydown')
    else:
        send_key_to_all_mgba('Tab', action='keyup')
    time.sleep(0.05)

def btn_a():
    send_key_to_all_mgba('x')
    time.sleep(0.05)

def btn_down():
    send_key_to_all_mgba('Down')
    time.sleep(0.05)

def btn_start():
    send_key_to_all_mgba('Return', action='keydown')
    time.sleep(0.05)
    send_key_to_all_mgba('Return', action='keyup')
    time.sleep(0.05)

def proceed_through_intro():
    for i in range(4):
        time.sleep(0.2)
        btn_a()

def pick_up_pokeball():
    for i in range(4):
        time.sleep(0.2)
        btn_a()
    time.sleep(0.2)

def decline_naming():
    btn_down()
    time.sleep(0.1)
    for i in range(3):
        btn_a()
        time.sleep(0.2)

def open_pokemon_summary():
    btn_start()
    time.sleep(0.1)
    btn_a()
    time.sleep(0.1)
    btn_a()
    time.sleep(0.1)

def handle_screen_analysis():
    frame = VC.read_frame()

    bgr = frame[inspect_y, inspect_x].copy()
    hex_color = bgr_to_hex(bgr).upper()

    # Draw crosshair on full frame
    for dx in range(-line_len, line_len + 1):
        if dx == 0: continue
        x = inspect_x + dx
        if 0 <= x < frame.shape[1]:
            frame[inspect_y, x] = crosshair_color
    for dy in range(-line_len, line_len + 1):
        if dy == 0: continue
        y = inspect_y + dy
        if 0 <= y < frame.shape[0]:
            frame[y, inspect_x] = crosshair_color

    # Zoom view
    x0, x1 = max(inspect_x - zoom_size, 0), min(inspect_x + zoom_size + 1, frame.shape[1])
    y0, y1 = max(inspect_y - zoom_size, 0), min(inspect_y + zoom_size + 1, frame.shape[0])
    zoom_region = frame[y0:y1, x0:x1]
    zoom_display = cv2.resize(zoom_region, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)

    # Crosshair in zoom view (no center dot)
    center = (zoom_display.shape[1] // 2, zoom_display.shape[0] // 2)
    for dx in range(-line_len, line_len + 1):
        if dx == 0: continue
        x = center[0] + dx
        if 0 <= x < zoom_display.shape[1]:
            zoom_display[center[1], x] = crosshair_color
    for dy in range(-line_len, line_len + 1):
        if dy == 0: continue
        y = center[1] + dy
        if 0 <= y < zoom_display.shape[0]:
            zoom_display[y, center[0]] = crosshair_color

    # Overlay with hex + swatch
    pip_h, pip_w = zoom_display.shape[:2]
    overlay_height = 28
    overlay = np.zeros((overlay_height, pip_w, 3), dtype=np.uint8)

    # Swatch block
    swatch_width = 40
    overlay[:, :swatch_width] = bgr

    # Small hex text
    text_x = swatch_width + 10
    text_y = 20
    cv2.putText(overlay, hex_color, (text_x, text_y), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Stack PIP
    pip_combined = np.vstack((zoom_display, overlay))
    h, w = pip_combined.shape[:2]
    frame[0:h, 0:w] = pip_combined

    cv2.imshow("OBS Virtual Cam Preview", frame)
    cv2.waitKey(1)

    return hex_color

i = 5
for i in range(5):
    print(f'starting in {i}')
    i -= 1
    time.sleep(1)

attempt_count = 1
non_shiny_color = ''
taboo_colors = []
if platform.system() == 'Darwin':
    taboo_colors = ['#F8FFFF', '#F0EEF8', '#F0EFF6']
    non_shiny_color = '#D13B4C'
else:
    taboo_colors = []
    non_shiny_color = '#D23B4C'

ret_color = 'starting_val'
while True:
    print(f'Attempt count: {attempt_count}', end='\r')
    fast_forward(True)
    restart_game()
    proceed_through_intro()
    pick_up_pokeball()
    decline_naming()
    open_pokemon_summary()
    time.sleep(0.8)
    ret_color = handle_screen_analysis()

    if ret_color == SHINY_HEX:
        print(f'found after {attempt_count} attempts with ret_color {ret_color}')
        playsound('playground/item_found_sfx.mp3')
        break;

    attempt_count += 1

while True:
    i = i + 1
    i = i - 1