import subprocess
import time
import os
import signal
import sys
from multiprocessing import Process, Event
import json
import requests

# Configuration
NUM_INSTANCES = 12
ROM_PATH = '/home/josh/roms/pokemon_fire_red.gba'  # Update this path as needed
MGBA_CORE = '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so'

class RetroArchController:
    def __init__(self, instance_id, port_base=55355):
        self.instance_id = instance_id
        self.port = port_base + instance_id
        self.process = None
        self.api_url = f'http://localhost:{self.port}'
        
    def start(self):
        '''Start RetroArch instance with mGBA core'''
        cmd = [
            'retroarch',
            '-L', MGBA_CORE,
            ROM_PATH,
            '--netplay-mode', 'server',
            '--netplay-port', str(self.port),
            '--no-gui',
            '--log-level', '0'
        ]
        
        print(f'Starting RetroArch instance {self.instance_id} on port {self.port}')
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Wait for startup
        
    def stop(self):
        '''Stop RetroArch instance'''
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            
    def send_command(self, command):
        '''Send command to RetroArch via HTTP API'''
        try:
            response = requests.post(f'{self.api_url}/retroarch', json=command)
            return response.json()
        except:
            return None
            
    def press_button(self, button, duration=0.1):
        '''Press a button for specified duration'''
        self.send_command({
            'command': 'SET_INPUT',
            'button': button,
            'state': True
        })
        time.sleep(duration)
        self.send_command({
            'command': 'SET_INPUT', 
            'button': button,
            'state': False
        })
        
    def restart_game(self):
        '''Restart the game'''
        self.send_command({'command': 'RESET'})
        time.sleep(1)
        
    def set_speed(self, speed):
        '''Set emulator speed (1 = normal, 2 = 2x, etc)'''
        self.send_command({
            'command': 'SET_SPEED',
            'speed': speed
        })

def automation_process(instance_id, stop_event):
    '''Process that handles automation for a specific RetroArch instance'''
    controller = RetroArchController(instance_id)
    
    try:
        controller.start()
        controller.set_speed(1000)  # Run at 1000x speed
        
        attempt_count = 0
        while not stop_event.is_set():
            attempt_count += 1
            
            # Restart game
            controller.restart_game()
            
            # Proceed through intro (6 A presses)
            for _ in range(6):
                controller.press_button('A', 0.05)
                
            # Step forward
            controller.press_button('Up', 0.5)
            
            # Start encounter (3 A presses)
            for _ in range(3):
                controller.press_button('A', 0.05)
                
            # Wait for encounter
            time.sleep(0.8)
            
            # Check for shiny (this would need to be implemented)
            # For now, just continue
            
            if attempt_count % 100 == 0:
                print(f'Instance {instance_id}: {attempt_count} attempts')
                
    except Exception as e:
        print(f'Error in RetroArch instance {instance_id}: {e}')
    finally:
        controller.stop()

def main():
    '''Main function to coordinate multiple RetroArch instances'''
    print('Starting RetroArch automation...')
    
    # Check if ROM exists
    if not os.path.exists(ROM_PATH):
        print(f'Error: ROM file not found at {ROM_PATH}')
        print('Please update ROM_PATH in the script')
        return
        
    # Create shared stop event
    stop_event = Event()
    
    # Create processes for each RetroArch instance
    processes = []
    for i in range(NUM_INSTANCES):
        proc = Process(target=automation_process, args=(i + 1, stop_event))
        processes.append(proc)
        
    # Start all processes
    for proc in processes:
        proc.start()
        time.sleep(1)  # Stagger starts
        
    # Wait for completion or interruption
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
            
            # Check if any process has died
            for proc in processes:
                if not proc.is_alive():
                    print(f'Process {proc.name} died unexpectedly')
                    stop_event.set()
                    break
                    
    except KeyboardInterrupt:
        print('\nReceived interrupt signal, shutting down...')
        stop_event.set()
        
    # Clean up
    print('Cleaning up processes...')
    for proc in processes:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
            if proc.is_alive():
                proc.kill()
                
    print('Shutdown complete')

if __name__ == '__main__':
    main() 