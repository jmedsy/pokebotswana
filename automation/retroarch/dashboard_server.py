#!/usr/bin/env python3
"""
RetroArch Dashboard Server

Flask server that manages multiple RetroArch instances and serves the monitoring dashboard.
"""

import os
import subprocess
import time
import signal
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, send_from_directory
from retroarch_api import MultiInstanceAPI
import threading
import glob

app = Flask(__name__, template_folder='templates')

class RetroArchManager:
    def __init__(self, num_instances=12, rom_path=None):
        self.num_instances = num_instances
        self.rom_path = rom_path
        self.processes = {}
        self.api = MultiInstanceAPI(num_instances, port_base=55355)
        self.start_time = datetime.now()
        self.screenshot_dir = os.path.abspath(os.path.join(os.getcwd(), 'screenshots'))
        
        # Ensure screenshot directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Create subdirectories for each instance
        for i in range(1, num_instances + 1):
            instance_dir = os.path.join(self.screenshot_dir, f'instance_{i}')
            os.makedirs(instance_dir, exist_ok=True)
        
    def start_instance(self, instance_id, display_num=None):
        """Start a single RetroArch instance"""
        if instance_id in self.processes:
            print(f"Instance {instance_id} already running")
            return False
            
        if not self.rom_path or not os.path.exists(self.rom_path):
            print(f"❌ ROM file not found: {self.rom_path}")
            return False
            
        port = 55355 + instance_id
        display = f":{99 + instance_id}" if display_num is None else f":{display_num}"
        instance_screenshot_dir = os.path.join(self.screenshot_dir, f'instance_{instance_id}')
        
        # Create config for this instance
        config_content = f"""
network_cmd_enable = true
network_cmd_port = {port}
fastforward_ratio = 0.0
pause_nonactive = false
screenshot_directory = "{instance_screenshot_dir}"
notification_show_fast_forward = true
video_driver = "null"
audio_driver = "null"
input_driver = "null"
menu_driver = "null"
video_vsync = false
video_threaded = false
audio_enable = false
video_gpu_screenshot = false
"""
        
        config_file = f"/tmp/retroarch_instance_{instance_id}.cfg"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Start RetroArch with null drivers for headless operation
        cmd = [
            'retroarch',
            '--config', config_file,
            '-L', '/usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so',
            self.rom_path,
            '--verbose'
        ]
        
        # Add virtual display if specified
        env = os.environ.copy()
        if display_num:
            env['DISPLAY'] = display
        
        # Create log file for this instance
        log_file = f"/tmp/retroarch_instance_{instance_id}.log"
        
        try:
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT
                )
            
            self.processes[instance_id] = {
                'process': process,
                'port': port,
                'config_file': config_file,
                'log_file': log_file,
                'start_time': datetime.now(),
                'screenshot_count': 0
            }
            
            print(f"✅ Started RetroArch instance {instance_id} on port {port}")
            
            # Give it a moment to start, then enable fast forward
            time.sleep(2)
            self.api.get_instance(instance_id).fast_forward()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start instance {instance_id}: {e}")
            return False
    
    def stop_instance(self, instance_id):
        """Stop a single RetroArch instance"""
        if instance_id not in self.processes:
            return False
            
        # Try to quit gracefully first
        api_instance = self.api.get_instance(instance_id)
        api_instance.quit()
        time.sleep(1)
        api_instance.quit()  # Send twice as per documentation
        
        time.sleep(2)
        
        # Force kill if still running
        process_info = self.processes[instance_id]
        process = process_info['process']
        
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Clean up config and log files
        if os.path.exists(process_info['config_file']):
            os.remove(process_info['config_file'])
        if os.path.exists(process_info['log_file']):
            os.remove(process_info['log_file'])
        
        del self.processes[instance_id]
        print(f"⏹️  Stopped instance {instance_id}")
        return True
    
    def start_all_instances(self):
        """Start all instances"""
        print(f"🚀 Starting {self.num_instances} RetroArch instances...")
        
        for i in range(1, self.num_instances + 1):
            if self.start_instance(i, display_num=99 + i):
                time.sleep(1)  # Stagger starts
            else:
                print(f"❌ Failed to start instance {i}")
    
    def stop_all_instances(self):
        """Stop all instances"""
        print("🛑 Stopping all RetroArch instances...")
        
        instance_ids = list(self.processes.keys())
        for instance_id in instance_ids:
            self.stop_instance(instance_id)
    
    def get_status(self):
        """Get status of all instances"""
        now = datetime.now()
        runtime = str(now - self.start_time).split('.')[0]  # Remove microseconds
        
        # Count screenshots across all instance directories
        total_screenshots = 0
        for i in range(1, self.num_instances + 1):
            instance_dir = os.path.join(self.screenshot_dir, f'instance_{i}')
            if os.path.exists(instance_dir):
                total_screenshots += len(glob.glob(os.path.join(instance_dir, '*.png')))
        
        # Update screenshot counts for each instance
        for instance_id in self.processes:
            # Count PNG files in this instance's directory
            instance_dir = os.path.join(self.screenshot_dir, f'instance_{instance_id}')
            pattern = os.path.join(instance_dir, '*.png')
            self.processes[instance_id]['screenshot_count'] = len(glob.glob(pattern))
        
        instances = {}
        for instance_id, info in self.processes.items():
            # Check if process is still running
            is_running = info['process'].poll() is None
            
            # Find latest screenshot for this specific instance
            instance_dir = os.path.join(self.screenshot_dir, f'instance_{instance_id}')
            pattern = os.path.join(instance_dir, '*.png')
            screenshots = glob.glob(pattern)
            latest_screenshot = None
            if screenshots:
                latest_screenshot = max(screenshots, key=os.path.getctime)
                # Return relative path from screenshots directory for web serving
                latest_screenshot = f'instance_{instance_id}/{os.path.basename(latest_screenshot)}'
            
            instances[instance_id] = {
                'id': instance_id,
                'status': 'running' if is_running else 'stopped',
                'port': info['port'],
                'start_time': info['start_time'].strftime('%H:%M:%S'),
                'screenshot_count': info['screenshot_count'],
                'latest_screenshot': latest_screenshot,
                'last_update': now.strftime('%H:%M:%S')
            }
        
        summary = {
            'runtime': runtime,
            'total_instances': len(self.processes),
            'active_instances': sum(1 for i in instances.values() if i['status'] == 'running'),
            'total_screenshots': total_screenshots
        }
        
        return {
            'summary': summary,
            'instances': instances
        }

# Global manager instance
manager = None

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    if manager:
        return jsonify(manager.get_status())
    else:
        return jsonify({
            'summary': {
                'runtime': '00:00:00',
                'total_instances': 0,
                'active_instances': 0,
                'total_screenshots': 0
            },
            'instances': {}
        })

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve screenshot files (supports subdirectories)"""
    return send_from_directory(manager.screenshot_dir if manager else 'screenshots', filename)

@app.route('/api/start_all')
def start_all():
    """Start all RetroArch instances"""
    if manager and manager.rom_path:
        threading.Thread(target=manager.start_all_instances, daemon=True).start()
        return jsonify({'success': True, 'message': 'Starting all instances...'})
    else:
        return jsonify({'success': False, 'error': 'No ROM configured or manager not initialized'})

@app.route('/api/stop_all')
def stop_all():
    """Stop all RetroArch instances"""
    if manager:
        threading.Thread(target=manager.stop_all_instances, daemon=True).start()
        return jsonify({'success': True, 'message': 'Stopping all instances...'})
    else:
        return jsonify({'success': False, 'error': 'Manager not initialized'})

@app.route('/api/control/<int:instance_id>/<command>')
def control_instance(instance_id, command):
    """Send command to specific instance"""
    if not manager:
        return jsonify({'success': False, 'error': 'Manager not initialized'})
    
    api_instance = manager.api.get_instance(instance_id)
    if not api_instance:
        return jsonify({'success': False, 'error': 'Invalid instance ID'})
    
    if command == 'reset':
        result = api_instance.reset_game()
    elif command == 'fast_forward':
        result = api_instance.fast_forward()
    elif command == 'screenshot':
        result = api_instance.screenshot()
        # Update screenshot count
        if instance_id in manager.processes:
            manager.processes[instance_id]['screenshot_count'] += 1
    elif command == 'pause':
        result = api_instance.pause_toggle()
    else:
        return jsonify({'success': False, 'error': 'Unknown command'})
    
    return jsonify({'success': True, 'result': result})

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print('\n🛑 Shutting down RetroArch manager...')
    if manager:
        manager.stop_all_instances()
    sys.exit(0)

def main():
    """Main entry point"""
    global manager
    
    print('🎮 RetroArch Dashboard Server')
    print('=' * 50)
    
    # Get ROM path from command line or use default
    import sys
    if len(sys.argv) > 1:
        rom_path = sys.argv[1]
    else:
        # Look for common Pokemon ROM names
        rom_candidates = [
            'pokemon_emerald.gba',
            'pokemon_ruby.gba',
            'pokemon_sapphire.gba',
            'pokemon.gba'
        ]
        
        rom_path = None
        for candidate in rom_candidates:
            if os.path.exists(candidate):
                rom_path = candidate
                break
        
        if not rom_path:
            print("❌ No ROM file specified!")
            print("Usage: python dashboard_server.py [path_to_pokemon_rom.gba]")
            print("Or place a Pokemon ROM as 'pokemon.gba' in this directory")
            return
    
    if not os.path.exists(rom_path):
        print(f"❌ ROM file not found: {rom_path}")
        return
    
    print(f"🎮 Using ROM: {rom_path}")
    
    # Initialize manager
    manager = RetroArchManager(num_instances=12, rom_path=rom_path)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print('🎯 Dashboard server ready')
    print('🔗 Open http://localhost:5001 to view dashboard')
    print('📊 Use the web interface to start/stop instances')
    print('⏹️  Press Ctrl+C to stop')
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main() 