#!/usr/bin/env python3
"""
RetroArch HTTP API for programmatic control

Clean HTTP interface for controlling RetroArch instances remotely.
"""

import requests
import socket
from datetime import datetime

class RetroArchAPI:
    def __init__(self, port=55355):
        self.port = port
        self.base_url = f'http://localhost:{port}'
        
    def send_command(self, command):
        """Send UDP command to RetroArch"""
        return self.send_udp_command(command)
    
    def send_udp_command(self, command):
        """Send UDP command to RetroArch (alternative method)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.sendto(command.encode(), ('127.0.0.1', self.port))
            sock.close()
            return {'status': 'sent'}
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}
    
    def reset_game(self):
        """Reset the game"""
        return self.send_command('RESET')
    
    def fast_forward(self):
        """Toggle fast forward"""
        return self.send_command('FAST_FORWARD')
    
    def pause_toggle(self):
        """Toggle pause"""
        return self.send_command('PAUSE_TOGGLE')
    
    def save_state(self, slot=0):
        """Save state to slot"""
        return self.send_command(f'SAVE_STATE_SLOT {slot}')
    
    def load_state(self, slot=0):
        """Load state from slot"""
        return self.send_command(f'LOAD_STATE_SLOT {slot}')
    
    def screenshot(self):
        """Take screenshot"""
        return self.send_command('SCREENSHOT')
    
    def quit(self):
        """Quit RetroArch"""
        return self.send_command('QUIT')

class MultiInstanceAPI:
    def __init__(self, num_instances=12, port_base=55355):
        self.num_instances = num_instances
        self.port_base = port_base
        self.instances = {}
        
        # Create API instances for each port
        for i in range(1, num_instances + 1):
            port = port_base + i
            self.instances[i] = RetroArchAPI(port)
    
    def get_instance(self, instance_id):
        """Get API for specific instance"""
        return self.instances.get(instance_id)
    
    def reset_all(self):
        """Reset all instances"""
        results = {}
        for instance_id, api in self.instances.items():
            results[instance_id] = api.reset_game()
        return results
    
    def fast_forward_all(self):
        """Enable fast forward on all instances"""
        results = {}
        for instance_id, api in self.instances.items():
            results[instance_id] = api.fast_forward()
        return results
    
    def screenshot_all(self):
        """Take screenshots of all instances"""
        results = {}
        for instance_id, api in self.instances.items():
            results[instance_id] = api.screenshot()
        return results
    
    def command_all(self, command):
        """Send command to all instances"""
        results = {}
        for instance_id, api in self.instances.items():
            results[instance_id] = api.send_command(command)
        return results

# Convenience functions
def quick_reset(instance_id=1, port_base=55355):
    """Quick reset for single instance"""
    api = RetroArchAPI(port_base + instance_id)
    return api.reset_game()

def quick_fast_forward(instance_id=1, port_base=55355):
    """Quick fast forward for single instance"""
    api = RetroArchAPI(port_base + instance_id)
    return api.fast_forward()

def quick_screenshot(instance_id=1, port_base=55355):
    """Quick screenshot for single instance"""
    api = RetroArchAPI(port_base + instance_id)
    return api.screenshot()

# Main usage example
if __name__ == '__main__':
    # Example usage
    print("🎮 RetroArch HTTP API Example")
    
    # Single instance control
    print("\n--- Single Instance ---")
    api = RetroArchAPI(55356)  # Instance 1
    print("Reset:", api.reset_game())
    print("Fast Forward:", api.fast_forward())
    
    # Multi-instance control
    print("\n--- Multi Instance ---")
    multi = MultiInstanceAPI(num_instances=3)
    print("Reset All:", multi.reset_all())
    print("Fast Forward All:", multi.fast_forward_all()) 