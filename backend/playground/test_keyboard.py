from pynput.keyboard import Controller, Key
import time
import cv2
import numpy as np
import time
from playsound import playsound

class OBSVirtualCamSource:
    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        self.width = 480
        self.height = 320

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        # return cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        return frame

    def release(self):
        self.cap.release()

def bgr_to_hex(bgr):
    return '#{:02x}{:02x}{:02x}'.format(*bgr[::-1])

# --- Config ---
inspect_x, inspect_y = 127, 132
zoom_size = 7
scale_factor = 8
crosshair_color = (0, 255, 0)  # neon green
line_len = 5
font = cv2.FONT_HERSHEY_SIMPLEX

source = OBSVirtualCamSource()

# Warm-up
for _ in range(5):
    source.read_frame()
    time.sleep(0.05)

frame = source.read_frame()
cv2.imshow("OBS Virtual Cam Preview", frame)
cv2.waitKey(1)
time.sleep(0.2)

keyboard = Controller()

def restart_game():
    keyboard.press(Key.cmd)
    keyboard.press('r')
    time.sleep(0.05)
    keyboard.release(Key.cmd)
    keyboard.release('r')

def fast_forward(arg: bool):
    if arg == True:
        keyboard.press(Key.tab)
    else:
        keyboard.release(Key.tab)

def btn_a():
    keyboard.press('x')
    time.sleep(0.05)
    keyboard.release('x')

def btn_down():
    keyboard.press(Key.down)
    time.sleep(0.05)
    keyboard.release(Key.down)

def btn_start():
    keyboard.press(Key.enter)
    time.sleep(0.05)
    keyboard.release(Key.enter)

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
    btn_a()
    time.sleep(0.1)

def handle_screen_analysis():
    # print('here 1')
    frame = source.read_frame()
    # if frame is None:
    #     print("No frame received.")
    #     continue

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

    # print('here 2')
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

    # print('here 3')
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
    # print('here 4')
    # Stack PIP
    pip_combined = np.vstack((zoom_display, overlay))
    h, w = pip_combined.shape[:2]
    frame[0:h, 0:w] = pip_combined
    # print('here 5')

    # print(f"Pixel ({inspect_x},{inspect_y}): BGR={bgr.tolist()}  HEX={hex_color}", end='\r')

    # print('here 6')

    cv2.imshow("OBS Virtual Cam Preview", frame)
    cv2.waitKey(1)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    # print('here 7')
    return hex_color

i = 5
for i in range(5):
    print(f'starting in {i}')
    i -= 1
    time.sleep(1)

attempt_count = 1

ret_color = 'starting_val'
while True:
    print(f"Attempt count: {attempt_count}", end='\r')
    fast_forward(True)
    restart_game()
    proceed_through_intro()
    pick_up_pokeball()
    decline_naming()
    open_pokemon_summary()
    time.sleep(0.8)
    ret_color = handle_screen_analysis()

    if ret_color =='#F8FFFF' or ret_color == '#F0EEF8':
        print('Virtual camera is out of sync, catching back up...')
    elif ret_color != '#D13B4C':
        print(f'found after {attempt_count} attempts with ret_color {ret_color}')
        playsound('item_found_sfx.mp3')
        break;

    attempt_count += 1

while True:
    i = i + 1
    i = i - 1