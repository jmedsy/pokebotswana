# Google Drive Save Manager Setup

This guide shows how to set up programmatic downloading from Google Drive for your Pokemon save files.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Drive API credentials:**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select existing one
   
   c. Enable the Google Drive API:
      - Go to "APIs & Services" > "Library"
      - Search for "Google Drive API"
      - Click "Enable"
   
   d. Create credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth 2.0 Client IDs"
      - Choose "Desktop application"
      - Download the JSON file and rename it to `credentials.json`
      - Place it in your project root directory

## Usage Examples

### Basic Usage

```python
from tools.save_manager import GoogleDriveSaveManager

# Initialize the manager
save_manager = GoogleDriveSaveManager()

# Download all Pokemon save files
save_manager.download_pokemon_saves('./saves')
```

### Advanced Usage

```python
# Search for specific files
save_manager.authenticate()
files = save_manager.search_files(
    query="name contains 'pokemon red'",
    file_types=['.sav', '.dat']
)

# Download a specific file by ID
save_manager.download_file('your-file-id-here', './saves/pokemon_red.sav')

# List folders to find your save directories
folders = save_manager.list_folders()
```

### Integration with Your Pokemon Bot

```python
import schedule
import time
from tools.save_manager import GoogleDriveSaveManager

def sync_saves():
    """Sync save files from Google Drive every hour"""
    save_manager = GoogleDriveSaveManager()
    save_manager.download_pokemon_saves('./saves')
    print("Save files synced!")

# Schedule automatic syncing
schedule.every().hour.do(sync_saves)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## File Types Supported

The save manager looks for these common Pokemon save file extensions:
- `.sav` - Standard save files
- `.dat` - Binary save data
- `.gbs` - Game Boy save files
- `.sgm` - Save game files
- `.sgs` - Save game state files

## Security Notes

- The `credentials.json` file contains sensitive information - never commit it to version control
- The `token.pickle` file will be created automatically after first authentication
- The script only requests read-only access to your Google Drive

## Troubleshooting

**"Credentials file not found"**
- Make sure you've downloaded `credentials.json` from Google Cloud Console
- Place it in the same directory as your Python script

**"Authentication failed"**
- Delete `token.pickle` and try again
- Make sure your Google Cloud project has the Drive API enabled

**"No files found"**
- Check your search query is correct
- Verify files aren't in the trash
- Make sure file names contain expected keywords 