import os
from dotenv import load_dotenv
import cv2
import time

# Load environment variables from .env file
load_dotenv()

CAMERA_INDEX = int(os.getenv('VC_DEVICE_IDX', 0))

class VirtualCamera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        ''' Instantiates a virtual camera object if not already instantiated. '''
        if not hasattr(self, 'cap'):
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            if not self.cap.isOpened():
                # Camera failed to open
                raise RuntimeError(f'Cannot open camera with index {CAMERA_INDEX}')
            self.width = 480
            self.height = 320

    def read_frame(self):
        for _ in range(3):  # Try up to 3 times
            ret, frame = self.cap.read()
            if ret:
                return frame
        # Failed to read frame after 3 attempts
        return None

    def release(self):
        self.cap.release()

    def warm_up(self):
        for _ in range(5):
            self.read_frame()
            time.sleep(0.05)


'''---------------------------------------------------------------- EXPORTS ----------------------------------------------------------------'''

''' Singleton instance of the virtual camera '''
VC = VirtualCamera.get_instance()

'''Utility Function'''
def bgr_to_hex(bgr):
    return '#{:02x}{:02x}{:02x}'.format(*bgr[::-1])

'''Utility Function'''
def warm_up():
    for _ in range(5):
        VirtualCamera.get_instance().read_frame()
        time.sleep(0.05)