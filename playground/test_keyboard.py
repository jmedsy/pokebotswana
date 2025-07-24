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
import threading

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

latest_frame = None
frame_lock = threading.Lock()

def frame_grabber():
    global latest_frame
    while True:
        frame = VC.read_frame()
        with frame_lock:
            latest_frame = frame

def get_latest_frame():
    with frame_lock:
        return latest_frame.copy() if latest_frame is not None else None

def send_key_to_all_players(key):
    num_rows = 3
    num_cols = 4
    for col in range(1, num_cols + 1):
        player_title = f"Player {col}"
        result = subprocess.run(['xdotool', 'search', '--name', player_title], capture_output=True, text=True)
        window_ids = result.stdout.strip().split('\n')
        for row in range(num_rows):
            if len(window_ids) > row and window_ids[row]:
                wid = window_ids[row]
                subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
                time.sleep(0.1)
                subprocess.run(['xdotool', 'keydown', key])
                time.sleep(0.05)
                subprocess.run(['xdotool', 'keyup', key])


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
    num_players = 4  # Increase this if you add more players/windows
    for i in range(1, num_players + 1):
        player_title = f"Player {i}"
        send_p_to_window(player_title)

def fast_forward(arg: bool):
    # Always focus Player 1 window before sending Tab
    send_p_to_window('Player 1')  # This will focus Player 1, but we don't want to send 'p', so split the logic
    # Instead, just focus Player 1 window:
    result = subprocess.run(['xdotool', 'search', '--name', 'Player 1'], capture_output=True, text=True)
    window_ids = result.stdout.strip().split('\n')
    for wid in window_ids:
        if wid:
            subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
            break  # Only focus the first matching window
    # Now send Tab keydown/keyup
    if arg:
        send_key_to_all_players('Tab')
    else:
        send_key_to_all_players('Tab')
    time.sleep(0.05)

def fast_forward_once():
    send_key_to_all_players('Tab')
    time.sleep(0.05)

def btn_a():
    send_key_to_all_players('x')
    time.sleep(0.05)

def btn_down():
    send_key_to_all_players('Down')
    time.sleep(0.05)

def btn_up():
    send_key_to_all_players('Up')
    time.sleep(0.05)

def btn_start():
    send_key_to_all_players('Return')
    # send_key_to_all_players('Return', action='keydown')
    # time.sleep(0.05)
    # send_key_to_all_players('Return', action='keyup')
    time.sleep(0.05)

def proceed_through_intro():
    i = 1
    for i in range(4):
        print(i)
        i = i + 1
        time.sleep(0.2)
        btn_a()

def step_foward():
    btn_up()
    time.sleep(0.5)

def pick_up_pokeball():
    for i in range(4):
        time.sleep(0.2)
        btn_a()
    time.sleep(0.5)

def decline_naming():
    btn_down()
    time.sleep(0.1)
    for i in range(3):
        btn_a()
        time.sleep(0.2)
    time.sleep(0.3)

def open_pokemon_summary():
    btn_start()
    time.sleep(0.5)
    btn_a()
    time.sleep(0.5)
    btn_a()
    time.sleep(0.5)
    btn_a()
    time.sleep(0.5)

def handle_screen_analysis(display=True):
    frame = get_latest_frame()
    if frame is None:
        return []
    zoom_displays = []
    spots = []
    num_rows = 3
    num_cols = 4
    y_offset_correction = 2  # Tune this value as needed
    for row in range(num_rows):
        for col in range(num_cols):
            x = inspect_x + col * 480
            y = inspect_y + row * 320 - y_offset_correction
            if x < frame.shape[1] and y < frame.shape[0]:
                bgr = frame[y, x].copy()
                hex_color = bgr_to_hex(bgr).upper()
                spots.append({'x': x, 'y': y, 'bgr': bgr, 'hex': hex_color})

                # Draw crosshair on full frame
                for dx in range(-line_len, line_len + 1):
                    if dx == 0: continue
                    xx = x + dx
                    if 0 <= xx < frame.shape[1]:
                        frame[y, xx] = crosshair_color
                for dy in range(-line_len, line_len + 1):
                    if dy == 0: continue
                    yy = y + dy
                    if 0 <= yy < frame.shape[0]:
                        frame[yy, x] = crosshair_color

                # Zoom view for this spot
                x0, x1 = max(x - zoom_size, 0), min(x + zoom_size + 1, frame.shape[1])
                y0, y1 = max(y - zoom_size, 0), min(y + zoom_size + 1, frame.shape[0])
                zoom_region = frame[y0:y1, x0:x1]
                zoom_display = cv2.resize(zoom_region, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)

                # Crosshair in zoom view (no center dot)
                center = (zoom_display.shape[1] // 2, zoom_display.shape[0] // 2)
                for dx in range(-line_len, line_len + 1):
                    if dx == 0: continue
                    xx = center[0] + dx
                    if 0 <= xx < zoom_display.shape[1]:
                        zoom_display[center[1], xx] = crosshair_color
                for dy in range(-line_len, line_len + 1):
                    if dy == 0: continue
                    yy = center[1] + dy
                    if 0 <= yy < zoom_display.shape[0]:
                        zoom_display[yy, center[0]] = crosshair_color

                # Overlay with hex + swatch
                pip_h, pip_w = zoom_display.shape[:2]
                overlay_height = 28
                overlay = np.zeros((overlay_height, pip_w, 3), dtype=np.uint8)
                swatch_width = 40
                overlay[:, :swatch_width] = bgr
                text_x = swatch_width + 10
                text_y = 20
                cv2.putText(overlay, hex_color, (text_x, text_y), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                # Stack zoom and overlay for this spot
                pip_combined = np.vstack((zoom_display, overlay))
                zoom_displays.append({'pip': pip_combined, 'row': row, 'col': col})

    # Place each PIP overlay above its corresponding player in the grid
    if display and zoom_displays:
        pip_h, pip_w = zoom_displays[0]['pip'].shape[:2]
        for item in zoom_displays:
            row = item['row']
            col = item['col']
            x_offset = col * 480
            y_offset = row * pip_h
            pip_combined = item['pip']
            if x_offset + pip_w <= frame.shape[1] and y_offset + pip_h <= frame.shape[0]:
                frame[y_offset:y_offset+pip_h, x_offset:x_offset+pip_w] = pip_combined
        cv2.imshow("OBS Virtual Cam Preview", frame)
        cv2.waitKey(1)

    # Return all hex colors for further logic
    return [spot['hex'] for spot in spots]

i = 5
for i in range(5):
    print(f'starting in {i}')
    i -= 1
    time.sleep(1)

attempt_count = 0
non_shiny_color = ''
taboo_colors = []
if platform.system() == 'Darwin':
    taboo_colors = ['#F8FFFF', '#F0EEF8', '#F0EFF6']
    non_shiny_color = '#D13B4C'
else:
    taboo_colors = []
    non_shiny_color = '#D23B4C'

ret_color = 'starting_val'
# fast_forward_once()
def focus_player_1():
    result = subprocess.run(['xdotool', 'search', '--name', 'Player 1'], capture_output=True, text=True)
    window_ids = result.stdout.strip().split('\n')
    for wid in window_ids:
        if wid: 
            subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
            break

def prime_all_windows_with_x():
    num_players = 4  # Or however many you have
    for i in range(1, num_players + 1):
        player_title = f"Player {i}"
        result = subprocess.run(['xdotool', 'search', '--name', player_title], capture_output=True, text=True)
        window_ids = result.stdout.strip().split('\n')
        for wid in window_ids:
            if wid:
                subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
                subprocess.run(['xdotool', 'key', 'x'])
                break  # Only focus the first matching window

def automation_loop():
    attempt_count = 1
    ret_colors = ['starting_val']
    while True:
        print(f'Attempt count: {attempt_count}', end='\r')
        restart_game()
        focus_player_1()
        proceed_through_intro()
        pick_up_pokeball()
        decline_naming()
        open_pokemon_summary()
        time.sleep(0.8)
        # Only analyze colors, do not update the OpenCV window here
        ret_colors = handle_screen_analysis(display=False)

        if SHINY_HEX in ret_colors:
            print(f'found after {attempt_count} attempts with ret_color(s) {ret_colors}')
            playsound('playground/item_found_sfx.mp3')
            break

        attempt_count += 4

def live_preview():
    while True:
        handle_screen_analysis(display=True)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1/60)

if __name__ == "__main__":
    grabber_thread = threading.Thread(target=frame_grabber, daemon=True)
    grabber_thread.start()
    automation_thread = threading.Thread(target=automation_loop, daemon=True)
    automation_thread.start()
    live_preview()  # This runs in the main thread