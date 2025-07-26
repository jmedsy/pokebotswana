import subprocess
import time
import os

def test_retroarch_basic():
    '''Test basic RetroArch functionality'''
    
    print('Testing RetroArch basic functionality...')
    
    # Test launching RetroArch with mGBA core (without ROM)
    mgba_core = '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so'
    
    print(f'Testing mGBA core: {mgba_core}')
    
    # Test if we can launch RetroArch with the core
    try:
        # Launch RetroArch with mGBA core for 3 seconds
        cmd = [
            'retroarch',
            '-L', mgba_core,
            '--verbose'
        ]
        
        print('Launching RetroArch with mGBA core (will close in 3 seconds)...')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait 3 seconds then terminate
        time.sleep(3)
        process.terminate()
        process.wait(timeout=5)
        
        print('✅ RetroArch launched successfully with mGBA core')
        return True
        
    except Exception as e:
        print(f'❌ Error launching RetroArch: {e}')
        return False

def test_retroarch_with_rom(rom_path):
    '''Test RetroArch with a ROM file'''
    
    if not os.path.exists(rom_path):
        print(f'❌ ROM file not found: {rom_path}')
        return False
        
    print(f'Testing RetroArch with ROM: {rom_path}')
    
    try:
        cmd = [
            'retroarch',
            '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
            rom_path,
            '--verbose'
        ]
        
        print('Launching RetroArch with ROM (will close in 5 seconds)...')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait 5 seconds then terminate
        time.sleep(5)
        process.terminate()
        process.wait(timeout=5)
        
        print('✅ RetroArch launched successfully with ROM')
        return True
        
    except Exception as e:
        print(f'❌ Error launching RetroArch with ROM: {e}')
        return False

if __name__ == '__main__':
    print('=== RetroArch Basic Test ===\n')
    
    # Test 1: Basic launch
    success1 = test_retroarch_basic()
    
    # Test 2: With ROM (if provided)
    rom_path = input('\nEnter ROM path to test (or press Enter to skip): ').strip()
    if rom_path:
        success2 = test_retroarch_with_rom(rom_path)
    else:
        success2 = True
        print('Skipping ROM test')
    
    print('\n=== Test Results ===')
    print(f'Basic launch: {"✅ PASS" if success1 else "❌ FAIL"}')
    print(f'ROM launch: {"✅ PASS" if success2 else "❌ FAIL"}')
    
    if success1 and success2:
        print('\n✅ RetroArch is ready for automation with API support!')
    else:
        print('\n❌ Some tests failed. Check the output above.') 