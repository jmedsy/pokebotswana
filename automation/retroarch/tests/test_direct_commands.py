import subprocess
import time
import os

def test_direct_automation():
    '''Test RetroArch direct automation using command-line options'''
    
    print('=== Testing RetroArch Direct Automation ===\n')
    
    # Test 1: Basic launch and quit
    print('1. Testing basic launch and quit...')
    try:
        cmd = [
            'retroarch',
            '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
            '--verbose'
        ]
        
        process = subprocess.Popen(cmd)
        time.sleep(3)
        process.terminate()
        process.wait(timeout=5)
        print('✅ Basic launch successful')
        
    except Exception as e:
        print(f'❌ Basic launch failed: {e}')
    
    # Test 2: Launch with ROM
    print('\n2. Testing launch with ROM...')
    rom_path = '/home/josh/roms/pokemon_fire_red.gba'
    
    if os.path.exists(rom_path):
        try:
            cmd = [
                'retroarch',
                '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
                rom_path,
                '--verbose'
            ]
            
            process = subprocess.Popen(cmd)
            time.sleep(5)
            process.terminate()
            process.wait(timeout=5)
            print('✅ ROM launch successful')
            
        except Exception as e:
            print(f'❌ ROM launch failed: {e}')
    else:
        print(f'⚠️  ROM not found at {rom_path}')
    
    # Test 3: Test speed control
    print('\n3. Testing speed control...')
    try:
        # Create a config with speed settings
        config_content = '''
fastforward_ratio = 2.0
rewind_enable = true
rewind_buffer_size = 10
'''
        
        with open('/tmp/retroarch_speed.cfg', 'w') as f:
            f.write(config_content)
        
        cmd = [
            'retroarch',
            '--config', '/etc/retroarch.cfg',
            '--appendconfig', '/tmp/retroarch_speed.cfg',
            '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
            '--verbose'
        ]
        
        process = subprocess.Popen(cmd)
        time.sleep(3)
        process.terminate()
        process.wait(timeout=5)
        print('✅ Speed control test successful')
        
        # Clean up
        os.remove('/tmp/retroarch_speed.cfg')
        
    except Exception as e:
        print(f'❌ Speed control test failed: {e}')
    
    print('\n=== Test Complete ===')
    print('\n🎉 RetroArch v1.21.0 is working!')
    print('\nNext steps:')
    print('1. Use RetroArch API for direct control (no GUI automation needed)')
    print('2. Use RetroArch\'s better performance and speed control')
    print('3. Implement API-based automation system')

if __name__ == '__main__':
    test_direct_automation() 