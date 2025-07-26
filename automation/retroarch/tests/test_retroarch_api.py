import subprocess
import time
import os

class RetroArchAPI:
    def __init__(self, port=55355):
        self.port = port
        self.process = None
        
    def start_retroarch(self, rom_path=None, core_path=None):
        '''Start RetroArch with network commands enabled'''
        
        # Create config file to enable network commands
        config_content = f'''
network_cmd_enable = true
network_cmd_port = {self.port}
stdin_cmd_enable = true
fastforward_ratio = 5.0
notification_show_fast_forward = true
rewind_enable = true
'''
        
        config_path = '/tmp/retroarch_api.cfg'
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Build command
        cmd = [
            'retroarch',
            '--config', '/etc/retroarch.cfg',
            '--appendconfig', config_path
        ]
        
        # Add core if specified
        if core_path:
            cmd.extend(['-L', core_path])
        else:
            cmd.extend(['-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so'])
            
        # Add ROM if specified
        if rom_path:
            cmd.append(rom_path)
        
        print(f'Starting RetroArch on port {self.port}...')
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for startup
        
    def send_command(self, command):
        '''Send command to RetroArch via UDP network API'''
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.sendto(command.encode(), ('127.0.0.1', self.port))
            sock.close()
            return True
        except:
            return False
            
    def stop(self):
        '''Stop RetroArch'''
        if self.process:
            try:
                self.send_command('QUIT')
                time.sleep(2)
                if self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except:
                if self.process.poll() is None:
                    self.process.terminate()

def test_api_basic():
    '''Test basic RetroArch API functionality without ROM'''
    
    print('=== Testing RetroArch API (No ROM) ===\n')
    
    api = RetroArchAPI()
    
    try:
        # Start RetroArch without ROM
        print('1. Starting RetroArch without ROM...')
        api.start_retroarch()
        
        # Test basic commands that work without ROM
        print('\n2. Testing basic commands...')
        
        commands = [
            'FAST_FORWARD_HOLD',
            'FAST_FORWARD',
            'PAUSE',
            'TOGGLE_FULLSCREEN',
            'MENU_TOGGLE',
            'QUIT'
        ]
        
        results = []
        for cmd in commands:
            print(f'\nTesting: {cmd}')
            success = api.send_command(cmd)
            results.append((cmd, success))
            time.sleep(1)
            
        # Print results
        print('\n=== Results ===')
        for cmd, success in results:
            status = '✅ PASS' if success else '❌ FAIL'
            print(f'{status}: {cmd}')
            
        working_commands = [cmd for cmd, success in results if success]
        
        if working_commands:
            print(f'\n🎉 {len(working_commands)} commands working!')
        else:
            print('\n❌ No commands working')
            
    except Exception as e:
        print(f'Error during test: {e}')
        
    finally:
        print('\n3. Stopping RetroArch...')
        api.stop()

def test_api_with_rom():
    '''Test RetroArch API functionality with ROM loaded'''
    
    print('\n=== Testing RetroArch API (With ROM) ===\n')
    
    api = RetroArchAPI()
    rom_path = '/home/josh/roms/pokemon_fire_red.gba'
    
    if not os.path.exists(rom_path):
        print(f'❌ ROM not found: {rom_path}')
        print('Skipping ROM-based tests')
        return
    
    try:
        # Start RetroArch with ROM
        print('1. Starting RetroArch with Pokemon Fire Red...')
        api.start_retroarch(rom_path)
        
        # Test commands that work with ROM loaded
        print('\n2. Testing commands with ROM loaded...')
        
        commands = [
            'FAST_FORWARD_HOLD',
            'PAUSE',
            'RESET',
            'STATE_SAVE_SLOT 0',
            'STATE_LOAD_SLOT 0',
            'MENU_TOGGLE',
            'FAST_FORWARD',
            'QUIT'
        ]
        
        results = []
        for cmd in commands:
            print(f'\nTesting: {cmd}')
            success = api.send_command(cmd)
            results.append((cmd, success))
            time.sleep(2)  # Give more time between commands with ROM
            
        # Print results
        print('\n=== Results ===')
        for cmd, success in results:
            status = '✅ PASS' if success else '❌ FAIL'
            print(f'{status}: {cmd}')
            
        working_commands = [cmd for cmd, success in results if success]
        
        if working_commands:
            print(f'\n🎉 {len(working_commands)} ROM commands working!')
        else:
            print('\n❌ No ROM commands working')
            
    except Exception as e:
        print(f'Error during ROM test: {e}')
        
    finally:
        print('\n3. Stopping RetroArch...')
        api.stop()

def main():
    '''Run all API tests'''
    print('=== RetroArch API Test Suite ===\n')
    
    # Test basic functionality
    test_api_basic()
    
    time.sleep(2)  # Brief pause between tests
    
    # Test with ROM
    test_api_with_rom()
    
    print('\n=== All Tests Complete ===')

if __name__ == '__main__':
    main() 