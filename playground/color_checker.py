import cv2
import numpy as np
import time

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

while True:
    frame = source.read_frame()
    if frame is None:
        print("No frame received.")
        continue

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

    print(f"Pixel ({inspect_x},{inspect_y}): BGR={bgr.tolist()}  HEX={hex_color}", end='\r')

    cv2.imshow("OBS Virtual Cam Preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

source.release()
cv2.destroyAllWindows()
