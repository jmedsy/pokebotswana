import pygame
import time
from pkbt.config import SUCCESS_AUDIO

def play_success(blocking=False):
    pygame.mixer.init()
    pygame.mixer.music.load(SUCCESS_AUDIO)
    pygame.mixer.music.play()
    if blocking:
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

if __name__ == "__main__":
    play_success()