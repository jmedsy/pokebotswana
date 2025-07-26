#!/usr/bin/env python3
"""
Live Video Streaming Monitor for Headless RetroArch

Streams video from virtual displays in real-time instead of slow screenshots.
"""

import subprocess
import time
import os
from flask import Flask, Response, render_template, jsonify
import signal
import sys

app = Flask(__name__)

class VideoStreamer:
    def __init__(self, instance_id, display_num):
        self.instance_id = instance_id
        self.display_num = display_num
        self.display = f":{display_num}"
        self.streaming = False
        self.ffmpeg_process = None
        
    def start_stream(self, port):
        """Start FFmpeg stream from virtual display"""
        if self.streaming:
            return True
            
        # FFmpeg command to capture X11 display and stream as MJPEG
        cmd = [
            'ffmpeg',
            '-f', 'x11grab',
            '-video_size', '800x600',
            '-framerate', '30',
            '-i', self.display,
            '-f', 'mjpeg',
            '-q:v', '5',  # Quality (1=best, 31=worst)
            '-'  # Output to stdout
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0
            )
            self.streaming = True
            print(f"✅ Started video stream for instance {self.instance_id} (display {self.display})")
            return True
        except Exception as e:
            print(f"❌ Failed to start stream for instance {self.instance_id}: {e}")
            return False
    
    def get_frame(self):
        """Get next video frame"""
        if not self.streaming or not self.ffmpeg_process:
            return None
            
        try:
            # Read JPEG frame from FFmpeg
            # Look for JPEG header (FF D8)
            buffer = b''
            while True:
                chunk = self.ffmpeg_process.stdout.read(1024)
                if not chunk:
                    break
                    
                buffer += chunk
                
                # Look for JPEG start marker
                start = buffer.find(b'\xff\xd8')
                if start != -1:
                    # Look for JPEG end marker
                    end = buffer.find(b'\xff\xd9', start + 2)
                    if end != -1:
                        # Found complete JPEG frame
                        frame = buffer[start:end + 2]
                        buffer = buffer[end + 2:]
                        return frame
                        
                # Keep buffer size reasonable
                if len(buffer) > 100000:  # 100KB max buffer
                    buffer = buffer[-50000:]  # Keep last 50KB
                    
        except Exception as e:
            print(f"Frame read error for instance {self.instance_id}: {e}")
            
        return None
    
    def stop_stream(self):
        """Stop video stream"""
        self.streaming = False
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except:
                self.ffmpeg_process.kill()
            self.ffmpeg_process = None
        print(f"⏹️  Stopped stream for instance {self.instance_id}")

class VideoMonitor:
    def __init__(self, num_instances=12, display_base=99):
        self.num_instances = num_instances
        self.display_base = display_base
        self.streamers = {}
        
        # Create streamers for each instance
        for i in range(1, num_instances + 1):
            display_num = display_base + i
            self.streamers[i] = VideoStreamer(i, display_num)
    
    def start_all_streams(self):
        """Start video streams for all instances"""
        print(f"🎥 Starting video streams for {self.num_instances} instances...")
        
        for instance_id, streamer in self.streamers.items():
            streamer.start_stream(8000 + instance_id)
            time.sleep(0.5)  # Stagger starts
    
    def stop_all_streams(self):
        """Stop all video streams"""
        print("🛑 Stopping all video streams...")
        for streamer in self.streamers.values():
            streamer.stop_stream()
    
    def get_streamer(self, instance_id):
        """Get streamer for specific instance"""
        return self.streamers.get(instance_id)

# Global video monitor
video_monitor = VideoMonitor()

def generate_video_feed(instance_id):
    """Generate video feed for specific instance"""
    streamer = video_monitor.get_streamer(instance_id)
    if not streamer:
        return
        
    if not streamer.streaming:
        streamer.start_stream(8000 + instance_id)
        time.sleep(1)  # Give it time to start
    
    while streamer.streaming:
        frame = streamer.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.033)  # ~30 FPS

@app.route('/')
def dashboard():
    """Main video dashboard"""
    return render_template('video_dashboard.html', num_instances=video_monitor.num_instances)

@app.route('/video_feed/<int:instance_id>')
def video_feed(instance_id):
    """Video feed endpoint for specific instance"""
    if 1 <= instance_id <= video_monitor.num_instances:
        return Response(
            generate_video_feed(instance_id),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    return "Invalid instance ID", 404

@app.route('/api/video_status')
def video_status():
    """Get status of all video streams"""
    status = {}
    for instance_id, streamer in video_monitor.streamers.items():
        status[instance_id] = {
            'streaming': streamer.streaming,
            'display': streamer.display
        }
    return jsonify(status)

@app.route('/api/start_stream/<int:instance_id>')
def start_stream(instance_id):
    """Start stream for specific instance"""
    streamer = video_monitor.get_streamer(instance_id)
    if streamer and not streamer.streaming:
        success = streamer.start_stream(8000 + instance_id)
        return jsonify({'success': success})
    return jsonify({'success': False, 'error': 'Invalid instance or already streaming'})

@app.route('/api/stop_stream/<int:instance_id>')
def stop_stream(instance_id):
    """Stop stream for specific instance"""
    streamer = video_monitor.get_streamer(instance_id)
    if streamer and streamer.streaming:
        streamer.stop_stream()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid instance or not streaming'})

def create_templates():
    """Create templates directory and video dashboard"""
    os.makedirs('templates', exist_ok=True)
    
    dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎥 RetroArch Live Video Monitor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #fff;
            margin: 0;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        
        .btn:hover { background: #45a049; }
        .btn.danger { background: #f44336; }
        
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .video-card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #4CAF50;
        }
        
        .video-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .video-container {
            position: relative;
            background: #000;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .video-stream {
            width: 100%;
            height: auto;
            max-height: 300px;
            object-fit: contain;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            background: #333;
            color: #888;
        }
        
        .stream-controls {
            margin-top: 10px;
            text-align: center;
        }
        
        .status {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            text-transform: uppercase;
        }
        
        .status.streaming { background: #4CAF50; }
        .status.stopped { background: #f44336; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎥 RetroArch Live Video Monitor</h1>
        <p>Real-time video streams from all headless instances</p>
    </div>
    
    <div class="controls">
        <button class="btn" onclick="startAllStreams()">▶️ Start All Streams</button>
        <button class="btn danger" onclick="stopAllStreams()">⏹️ Stop All Streams</button>
        <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
    </div>
    
    <div class="video-grid" id="videoGrid">
        <!-- Video feeds will be populated by JavaScript -->
    </div>

    <script>
        function createVideoCard(instanceId) {
            return `
                <div class="video-card" id="card-${instanceId}">
                    <div class="video-header">
                        <h3>Instance ${instanceId}</h3>
                        <span class="status stopped" id="status-${instanceId}">Stopped</span>
                    </div>
                    <div class="video-container">
                        <img class="video-stream" 
                             id="stream-${instanceId}"
                             src="/video_feed/${instanceId}" 
                             style="display: none;"
                             onload="this.style.display='block'; document.getElementById('loading-${instanceId}').style.display='none'"
                             onerror="this.style.display='none'; document.getElementById('loading-${instanceId}').style.display='flex'">
                        <div class="loading" id="loading-${instanceId}">Loading video stream...</div>
                    </div>
                    <div class="stream-controls">
                        <button class="btn" onclick="startStream(${instanceId})">▶️ Start</button>
                        <button class="btn danger" onclick="stopStream(${instanceId})">⏹️ Stop</button>
                    </div>
                </div>
            `;
        }
        
        function initializeGrid() {
            const grid = document.getElementById('videoGrid');
            let html = '';
            for (let i = 1; i <= {{ num_instances }}; i++) {
                html += createVideoCard(i);
            }
            grid.innerHTML = html;
        }
        
        function startStream(instanceId) {
            fetch(`/api/start_stream/${instanceId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(`status-${instanceId}`).textContent = 'Streaming';
                        document.getElementById(`status-${instanceId}`).className = 'status streaming';
                        // Refresh the image source to start the stream
                        const img = document.getElementById(`stream-${instanceId}`);
                        img.src = img.src + '?t=' + new Date().getTime();
                    }
                });
        }
        
        function stopStream(instanceId) {
            fetch(`/api/stop_stream/${instanceId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(`status-${instanceId}`).textContent = 'Stopped';
                        document.getElementById(`status-${instanceId}`).className = 'status stopped';
                    }
                });
        }
        
        function startAllStreams() {
            for (let i = 1; i <= {{ num_instances }}; i++) {
                startStream(i);
            }
        }
        
        function stopAllStreams() {
            for (let i = 1; i <= {{ num_instances }}; i++) {
                stopStream(i);
            }
        }
        
        function refreshStatus() {
            fetch('/api/video_status')
                .then(response => response.json())
                .then(data => {
                    Object.keys(data).forEach(instanceId => {
                        const status = data[instanceId];
                        const statusEl = document.getElementById(`status-${instanceId}`);
                        if (statusEl) {
                            statusEl.textContent = status.streaming ? 'Streaming' : 'Stopped';
                            statusEl.className = `status ${status.streaming ? 'streaming' : 'stopped'}`;
                        }
                    });
                });
        }
        
        // Initialize the grid and refresh status periodically
        initializeGrid();
        refreshStatus();
        setInterval(refreshStatus, 5000); // Refresh every 5 seconds
    </script>
</body>
</html>
    '''
    
    with open('templates/video_dashboard.html', 'w') as f:
        f.write(dashboard_html)

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print('\n🛑 Shutting down video monitor...')
    video_monitor.stop_all_streams()
    sys.exit(0)

def check_dependencies():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found. Install with:")
    print("sudo apt update && sudo apt install ffmpeg")
    return False

def main():
    """Start the video monitoring server"""
    print('🎥 Starting Live Video Monitor for RetroArch')
    print('=' * 50)
    
    if not check_dependencies():
        return
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    create_templates()
    
    print('🎬 Video dashboard ready')
    print('🔗 Open http://localhost:5002 to watch live streams')
    print('📺 Real-time video from all headless instances')
    print('⏹️  Press Ctrl+C to stop')
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main() 