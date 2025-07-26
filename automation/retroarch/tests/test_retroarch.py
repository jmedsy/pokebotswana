import subprocess
import time

def test_retroarch():
    '''Test basic RetroArch functionality'''
    
    print('Testing RetroArch installation...')
    
    # Test if RetroArch is available
    try:
        result = subprocess.run(['retroarch', '--version'], 
                              capture_output=True, text=True)
        print(f'RetroArch version: {result.stdout.strip()}')
    except FileNotFoundError:
        print('Error: RetroArch not found')
        return False
        
    # Test if mGBA core is available
    mgba_core = '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so'
    if os.path.exists(mgba_core):
        print(f'mGBA core found: {mgba_core}')
    else:
        print('Error: mGBA core not found')
        return False
        
    # Test basic command line
    try:
        result = subprocess.run(['retroarch', '--help'], 
                              capture_output=True, text=True)
        print('RetroArch command line working')
    except Exception as e:
        print(f'Error testing RetroArch: {e}')
        return False
        
    print('RetroArch setup looks good!')
    return True

if __name__ == '__main__':
    import os
    test_retroarch() 