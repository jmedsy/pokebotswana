import time
import os
from datetime import datetime
import json

class StatusMonitor:
    def __init__(self, log_file='automation.log'):
        self.log_file = log_file
        self.start_time = datetime.now()
        self.reset_count = 0
        self.screenshot_count = 0
        self.last_shiny_check = None
        
    def log_event(self, event_type, message, data=None):
        '''Log an event with timestamp'''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message,
            'data': data or {}
        }
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        # Print to console
        print(f'[{timestamp}] {event_type.upper()}: {message}')
        
    def update_status(self, status_type, **kwargs):
        '''Update status and log it'''
        if status_type == 'reset':
            self.reset_count += 1
            self.log_event('reset', f'Game reset #{self.reset_count}')
            
        elif status_type == 'screenshot':
            self.screenshot_count += 1
            self.log_event('screenshot', f'Screenshot #{self.screenshot_count}')
            
        elif status_type == 'shiny_check':
            self.last_shiny_check = datetime.now()
            self.log_event('shiny_check', 'Checking for shiny Pokemon')
            
        elif status_type == 'shiny_found':
            self.log_event('shiny_found', '🎉 SHINY POKEMON FOUND! 🎉', kwargs)
            
        elif status_type == 'error':
            self.log_event('error', kwargs.get('message', 'Unknown error'), kwargs)
            
    def get_stats(self):
        '''Get current statistics'''
        runtime = datetime.now() - self.start_time
        hours = runtime.total_seconds() / 3600
        
        return {
            'runtime_hours': round(hours, 2),
            'resets': self.reset_count,
            'screenshots': self.screenshot_count,
            'resets_per_hour': round(self.reset_count / hours, 2) if hours > 0 else 0
        }
        
    def print_status(self):
        '''Print current status'''
        stats = self.get_stats()
        
        print('\n' + '='*50)
        print('🤖 AUTOMATION STATUS')
        print('='*50)
        print(f'⏱️  Runtime: {stats["runtime_hours"]} hours')
        print(f'🔄 Resets: {stats["resets"]}')
        print(f'📸 Screenshots: {stats["screenshots"]}')
        print(f'⚡ Resets/hour: {stats["resets_per_hour"]}')
        
        if self.last_shiny_check:
            time_since_check = datetime.now() - self.last_shiny_check
            print(f'🔍 Last shiny check: {time_since_check.seconds}s ago')
            
        print('='*50)

def test_status_monitoring():
    '''Test status monitoring'''
    print('=== Status Monitoring Test ===\n')
    
    monitor = StatusMonitor()
    
    # Simulate some events
    monitor.update_status('reset')
    time.sleep(1)
    
    monitor.update_status('screenshot')
    time.sleep(1)
    
    monitor.update_status('shiny_check')
    time.sleep(1)
    
    monitor.update_status('reset')
    time.sleep(1)
    
    # Print final status
    monitor.print_status()
    
    print(f'\n📄 Log saved to: {os.path.abspath(monitor.log_file)}')

if __name__ == '__main__':
    test_status_monitoring() 