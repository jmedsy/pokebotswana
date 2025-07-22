import cv2
import numpy as np
import pyautogui
from pynput import mouse

class OBSVirtualCamSource:
    def __init__(self):
        self.cap = cv2.VideoCapture(1)  # Try 0, 1, or 2 depending on device order
        self.width = 480
        self.height = 320

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)

    def release(self):
        self.cap.release()

def bgr_to_hex(bgr):
    b, g, r = bgr
    return f"#{r:02X}{g:02X}{b:02X}"

def on_move(x, y):
    try:
        x = int(x)
        y = int(y)
        img = pyautogui.screenshot(region=(x, y, 1, 1))
        rgb = np.array(img)[0, 0][:3]  # Only take R, G, B
        bgr = rgb[::-1]
        hex_code = bgr_to_hex(bgr)
        print(f"Mouse at ({x},{y}): HEX = {hex_code}")
    except Exception as e:
        print(f"Error: {e}")



# Initialize virtual camera source
source = OBSVirtualCamSource()

# Start mouse listener
listener = mouse.Listener(on_move=on_move)
listener.start()

# Live camera + mouse hex output loop
while True:
    frame = source.read_frame()
    if frame is None:
        print("No frame received.")
        continue

    cv2.imshow("OBS Virtual Cam Preview", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

source.release()
cv2.destroyAllWindows()
listener.stop()
