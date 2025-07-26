# 🎮 Pokemon RetroArch Automation Usage Guide

## Quick Start

### 1. Prerequisites
- RetroArch installed (`sudo apt install retroarch`)
- mGBA core installed (`sudo apt install libretro-mgba`)
- Python dependencies: `pip install flask requests`
- Pokemon ROM file (`.gba` format)

### 2. Launch the Dashboard

**Option A: With ROM file specified**
```bash
cd automation/retroarch
python dashboard_server.py /path/to/your/pokemon_rom.gba
```

**Option B: Auto-detect ROM (place ROM as `pokemon.gba` in the directory)**
```bash
cd automation/retroarch
python dashboard_server.py
```

### 3. Open the Web Dashboard
Navigate to: **http://localhost:5001**

## 🎯 How It Works

### The Dashboard Will:
- **Start 12 RetroArch instances** automatically when you click "Start All Instances"
- **Run each instance headless** (no GUI windows)
- **Enable fast-forward** on all instances for faster automation
- **Take screenshots** when requested
- **Monitor all instances** in real-time

### Each Instance:
- Runs on ports **55356-55367** (API control)
- Uses virtual displays **:100-:111** (headless mode)
- Saves screenshots to `screenshots/` directory
- Can be controlled individually via the dashboard

## 🕹️ Dashboard Controls

### Global Controls:
- **🚀 Start All Instances**: Launch all 12 RetroArch instances
- **⏹️ Stop All Instances**: Shut down all running instances
- **🔄 Refresh**: Update the dashboard data

### Per-Instance Controls:
- **🔄 Reset**: Reset the game to the beginning
- **⚡ Fast Forward**: Toggle fast-forward mode
- **📷 Screenshot**: Capture current screen

## 🔧 Manual Control (Alternative)

If you prefer manual control, you can also:

### Start Single Instance:
```bash
# Start RetroArch on port 55356
retroarch --config /etc/retroarch.cfg \
  -L /usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so \
  your_pokemon_rom.gba \
  --appendconfig <(echo "network_cmd_enable = true; network_cmd_port = 55356; fastforward_ratio = 0.0")
```

### Control via Python:
```python
from retroarch_api import RetroArchAPI

api = RetroArchAPI(port=55356)
api.fast_forward()  # Speed up
api.reset_game()    # Reset for new attempt
api.screenshot()    # Capture screen
```

### Control via Command Line:
```bash
# Send commands directly via UDP
echo -n "FAST_FORWARD" | nc -u -w1 127.0.0.1 55356
echo -n "RESET" | nc -u -w1 127.0.0.1 55356
```

## 📊 Automation Workflow

### Pokemon Shiny Hunting Example:
1. **Start instances** via dashboard
2. **Enable fast-forward** on all instances  
3. **Let automation run** (each instance hunts independently)
4. **Monitor screenshots** for shiny Pokemon
5. **Reset games** when encounters finish

### Live Video Streaming (Optional):
```bash
# Start video monitor for live streams
python video_monitor.py
# Open http://localhost:5002 for live video feeds
```

## 🛠️ Troubleshooting

### Common Issues:

**"No ROM file specified"**
- Place your Pokemon ROM as `pokemon.gba` in the `automation/retroarch/` directory
- Or specify the full path: `python dashboard_server.py /path/to/rom.gba`

**"Failed to start instance"**
- Check if RetroArch is installed: `which retroarch`
- Check if mGBA core exists: `ls /usr/lib/x86_64-linux-gnu/libretro/mgba_libretro.so`
- Ensure ROM file is valid `.gba` format

**Instances not responding**
- Check if ports 55356-55367 are free: `netstat -tulpn | grep 5535`
- Try stopping and restarting the dashboard

**No screenshots appearing**
- Screenshots are saved to `automation/retroarch/screenshots/`
- Make sure RetroArch has write permissions to this directory

## 🎉 You're Ready!

The system is designed to be **fully automated**. Just:
1. Start the dashboard server
2. Click "Start All Instances" 
3. Watch your Pokemon automation run across 12 instances simultaneously!

Your dashboard will show real-time status, screenshot counts, and let you control each instance individually. 