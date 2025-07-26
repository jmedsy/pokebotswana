import subprocess
import time
import os
from datetime import datetime

class ScreenshotMonitor:
    def __init__(self, port=55355, output_dir='screenshots'):
        self.port = port
        self.output_dir = output_dir
        self.screenshot_count = 0
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def take_screenshot(self, description=''):
        '''Take a screenshot and save it with timestamp'''
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.screenshot_count += 1
        
        filename = f'{timestamp}_{self.screenshot_count:04d}_{description}.png'
        filepath = os.path.join(self.output_dir, filename)
        
        # Take screenshot via RetroArch API
        cmd = ['retroarch', '--command', f'SCREENSHOT;localhost;{self.port}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f'📸 Screenshot saved: {filename}')
            return filepath
        else:
            print(f'❌ Screenshot failed: {result.stderr}')
            return None
            
    def monitor_loop(self, interval=5):
        '''Continuous monitoring loop'''
        print(f'📸 Starting screenshot monitoring every {interval} seconds...')
        print(f'📁 Screenshots saved to: {os.path.abspath(self.output_dir)}')
        
        try:
            while True:
                self.take_screenshot('monitor')
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print('\n🛑 Monitoring stopped')

def test_screenshot_monitoring():
    '''Test screenshot monitoring'''
    print('=== Screenshot Monitoring Test ===\n')
    
    # Start RetroArch first
    print('1. Starting RetroArch...')
    config_content = '''
network_cmd_enable = true
network_cmd_port = 55355
stdin_cmd_enable = true
'''
    
    config_path = '/tmp/monitor_test.cfg'
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    rom_path = '/home/josh/roms/pokemon_fire_red.gba'
    
    if not os.path.exists(rom_path):
        print(f'❌ ROM not found: {rom_path}')
        return
    
    cmd = [
        'retroarch',
        '--config', '/etc/retroarch.cfg',
        '--appendconfig', config_path,
        '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
        rom_path
    ]
    
    process = subprocess.Popen(cmd)
    time.sleep(5)
    
    # Test screenshot monitoring
    print('\n2. Testing screenshot monitoring...')
    monitor = ScreenshotMonitor()
    
    # Take a few test screenshots
    for i in range(3):
        monitor.take_screenshot(f'test_{i+1}')
        time.sleep(2)
    
    # Clean up
    process.terminate()
    process.wait(timeout=5)
    os.remove(config_path)
    
    print('\n✅ Screenshot monitoring test complete!')

if __name__ == '__main__':
    test_screenshot_monitoring() 