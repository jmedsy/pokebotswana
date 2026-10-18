#!/usr/bin/env python3
"""
Pull Pokemon Pearl Version save file from Google Drive
Downloads specific Pearl save and backs up existing files
"""

import os
import shutil
from datetime import datetime
from save_manager import GoogleDriveSaveManager
from save_helpers import show_file_comparison

# Configuration
PEARL_FOLDER_ID = '1mg-XzjiEcZPw-IOGIDfTgzY-uwabf4Pz'
PEARL_SAVE_NAME = 'Pokemon - Pearl Version (USA) (Rev 5).sav'
LOCAL_ROMS_DIR = '../../roms'

def backup_existing_file(file_path: str) -> str:
    """
    Create a backup of existing file with timestamp in roms/old/ directory
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file created
    """
    if not os.path.exists(file_path):
        return None
    
    # Create backup directory (roms/old/)
    backup_dir = os.path.join(os.path.dirname(file_path), 'old')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    backup_name = f"{base_name}_backup_{timestamp}.sav"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Copy the existing file to backup
    shutil.copy2(file_path, backup_path)
    print(f"📦 Backed up existing save to: old/{backup_name}")
    
    return backup_path

def find_pearl_save(save_manager: GoogleDriveSaveManager) -> dict:
    """
    Find the Pokemon Pearl save file in the specified folder
    
    Args:
        save_manager: Authenticated GoogleDriveSaveManager instance
        
    Returns:
        File metadata dict if found, None otherwise
    """
    print(f"🔍 Searching for '{PEARL_SAVE_NAME}' in folder...")
    
    # Search for files in the Pearl folder
    files = save_manager.search_files_in_folder(
        folder_id=PEARL_FOLDER_ID,
        file_types=['.sav']  # Only look for save files
    )
    
    # Look for the exact filename
    for file_info in files:
        if file_info['name'] == PEARL_SAVE_NAME:
            print(f"✅ Found Pearl save file: {file_info['name']}")
            return file_info
    
    print(f"❌ '{PEARL_SAVE_NAME}' not found in the specified folder")
    return None

def pull_pearl_save():
    """Main function to pull Pearl save file from Google Drive"""
    
    print("⚪ **POKEMON PEARL VERSION SAVE PULLER**\n")
    
    # Initialize save manager
    save_manager = GoogleDriveSaveManager(
        credentials_file='credentials.json',
        token_file='token.pickle'
    )
    
    if not save_manager.authenticate():
        print("❌ Authentication failed!")
        return False
    
    # Find the Pearl save file
    pearl_file = find_pearl_save(save_manager)
    if not pearl_file:
        return False
    
    # Create local directory path
    local_save_path = os.path.join(LOCAL_ROMS_DIR, PEARL_SAVE_NAME)
    local_save_path = os.path.normpath(local_save_path)  # Clean up the path
    
    print(f"📂 Target location: {local_save_path}")
    
    # Modification time safety check - compare when saves were last modified
    if os.path.exists(local_save_path):
        print(f"\n🕐 Checking save modification times for safety...")
        if not show_file_comparison(local_save_path, pearl_file, "pull"):
            print(f"🛑 Operation cancelled by user")
            return False
    
    # Check if file already exists and backup if needed
    backup_created = None
    if os.path.exists(local_save_path):
        print(f"⚠️  File already exists at {local_save_path}")
        backup_created = backup_existing_file(local_save_path)
        if backup_created:
            print(f"✅ Backup created successfully")
        else:
            print(f"❌ Failed to create backup")
            return False
    
    # Download the new save file
    print(f"\n⬇️ Downloading new Pearl save file...")
    success = save_manager.download_file(
        file_id=pearl_file['id'],
        destination=local_save_path
    )
    
    if success:
        print(f"\n🎉 **PEARL SAVE PULLED SUCCESSFULLY!**")
        print(f"📄 Downloaded: {PEARL_SAVE_NAME}")
        print(f"📂 Location: {local_save_path}")
        if backup_created:
            print(f"📦 Backup: old/{os.path.basename(backup_created)}")
        
        # Show file info
        if os.path.exists(local_save_path):
            size = os.path.getsize(local_save_path)
            size_kb = size / 1024
            print(f"📊 File size: {size_kb:.1f} KB")
        
        return True
    else:
        print(f"❌ Failed to download Pearl save file")
        # If download failed and we created a backup, we might want to restore it
        if backup_created and os.path.exists(backup_created):
            print(f"💾 Restoring backup...")
            shutil.move(backup_created, local_save_path)
            print(f"✅ Original file restored")
        return False

def list_save_backups():
    """List recent Pearl backup save files in the roms/old directory"""
    
    roms_dir = os.path.normpath(LOCAL_ROMS_DIR)
    backup_dir = os.path.join(roms_dir, 'old')
    
    if not os.path.exists(backup_dir):
        print(f"\n📦 No backup directory found (roms/old/)")
        return
    
    backup_files = []
    for file in os.listdir(backup_dir):
        if 'pearl' in file.lower() and 'backup_' in file and file.endswith('.sav'):
            backup_files.append(file)
    
    if backup_files:
        backup_files.sort(reverse=True)  # Newest first
        total_count = len(backup_files)
        recent_count = min(3, total_count)  # Show max 3 recent backups
        
        print(f"\n📦 **PEARL LOCAL BACKUPS:** {total_count} total, showing {recent_count} most recent:")
        
        for backup in backup_files[:recent_count]:
            backup_path = os.path.join(backup_dir, backup)
            mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
            print(f"  📄 {backup} - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n📦 No Pearl backup save files found in roms/old/")

if __name__ == "__main__":
    # Pull the Pearl save
    success = pull_pearl_save()
    
    # Show available backups
    print("\n" + "="*60)
    list_save_backups()
    
    if success:
        print(f"\n✅ Pearl save is ready for use!")
    else:
        print(f"\n❌ Failed to pull Pearl save")
