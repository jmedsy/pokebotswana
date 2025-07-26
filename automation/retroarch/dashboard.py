import subprocess
import time
import os
import threading
from datetime import datetime

def print_dashboard():
    '''Print monitoring options dashboard'''
    print('''
🎮 RETROARCH AUTOMATION MONITORING OPTIONS
==========================================

📸 Option 1: Screenshot Monitoring
   - Takes screenshots every X seconds
   - Saves to timestamped files
   - Good for reviewing what happened
   - Run: python3 monitor_screenshots.py

🎥 Option 2: (Removed - no longer using virtual camera)

📊 Option 3: Status Logging
   - Tracks resets, screenshots, events
   - Saves detailed logs
   - Shows statistics
   - Run: python3 status_monitor.py

🖥️  Option 4: RetroArch Window (Manual)
   - Just watch the RetroArch window directly
   - See everything in real-time
   - No additional tools needed

🔧 Option 5: Combined Approach
   - Use multiple monitoring methods
   - Screenshots + logging + occasional video
   - Best for debugging and verification

💡 RECOMMENDATIONS:
   - For debugging: Use video stream
   - For long runs: Use screenshot monitoring
   - For statistics: Use status logging
   - For verification: Use combined approach
''')

def test_all_monitoring():
    '''Test all monitoring options'''
    print('=== Testing All Monitoring Options ===\n')
    
    # Test 1: Screenshot monitoring
    print('1. Testing screenshot monitoring...')
    try:
        from monitor_screenshots import ScreenshotMonitor
        monitor = ScreenshotMonitor()
        monitor.take_screenshot('test')
        print('✅ Screenshot monitoring works')
    except Exception as e:
        print(f'❌ Screenshot monitoring failed: {e}')
    
    # Test 2: Status monitoring
    print('\n2. Testing status monitoring...')
    try:
        from status_monitor import StatusMonitor
        status = StatusMonitor()
        status.update_status('reset')
        status.update_status('screenshot')
        status.print_status()
        print('✅ Status monitoring works')
    except Exception as e:
        print(f'❌ Status monitoring failed: {e}')
    
    # Test 3: Video monitoring (just test import)
    print('\n3. Testing video monitoring...')
    try:
        from video_monitor import VideoMonitor
        print('✅ Video monitoring ready (run separately)')
    except Exception as e:
        print(f'❌ Video monitoring failed: {e}')
    
    print('\n🎉 All monitoring tests complete!')

if __name__ == '__main__':
    print_dashboard()
    
    response = input('\nWould you like to test all monitoring options? (y/n): ')
    if response.lower() == 'y':
        test_all_monitoring() 