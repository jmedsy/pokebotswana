# Automation Tools

This directory contains automation tools for GBA emulation and shiny hunting.

## Structure

```
automation/
├── retroarch/          # RetroArch automation scripts
│   ├── tests/         # Test and debugging scripts
│   └── ...            # Main automation scripts
├── shared/            # Shared utilities and helpers
└── README.md          # This file
```

## RetroArch Automation

### Files
- `retroarch_automation.py` - Main automation script for multiple RetroArch instances
- `dashboard.py` - Monitoring options menu
- `status_monitor.py` - Status logging functionality
- `monitor_screenshots.py` - Screenshot monitoring
- `tests/` - Test and debugging scripts

### Usage

1. **Test RetroArch setup:**
   ```bash
   python automation/retroarch/tests/test_retroarch.py
   ```

2. **Test RetroArch API:**
   ```bash
   python automation/retroarch/tests/test_retroarch_api.py
   ```

3. **Run automation:**
   ```bash
   python automation/retroarch/retroarch_automation.py
   ```

### Configuration

Update the following in the automation scripts:
- `ROM_PATH` - Path to your GBA ROM file
- `NUM_INSTANCES` - Number of RetroArch instances to run

## Requirements

- RetroArch installed
- mGBA core installed
- Python requests library: `pip install requests` 