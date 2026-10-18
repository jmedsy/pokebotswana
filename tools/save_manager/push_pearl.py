#!/usr/bin/env python3
"""
Push Pokemon Pearl Version save file to Google Drive
Uploads local Pearl save and backs up existing files on Google Drive
"""

import os
from datetime import datetime
from save_manager import GoogleDriveSaveManager
from save_helpers import show_file_comparison

# Configuration
PEARL_FOLDER_ID = '1mg-XzjiEcZPw-IOGIDfTgzY-uwabf4Pz'  # Target folder for save
BACKUP_FOLDER_ID = '1JmwSAAe-4oIpP-PrL-iaq3IJHnenwy-k'    # Backup folder for overwritten files
PEARL_SAVE_NAME = 'Pokemon - Pearl Version (USA) (Rev 5).sav'
LOCAL_ROMS_DIR = '../../roms'

def create_backup_name(original_name: str) -> str:
    """
    Create a timestamped backup filename
    
    Args:
        original_name: Original filename
        
    Returns:
        Backup filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(original_name)[0]
    return f"{base_name}_backup_{timestamp}.sav"

def backup_existing_drive_file(save_manager: GoogleDriveSaveManager, file_info: dict) -> bool:
    """
    Backup existing file on Google Drive to backup folder
    
    Args:
        save_manager: Authenticated GoogleDriveSaveManager instance
        file_info: File metadata dict from Google Drive
        
    Returns:
        True if backup successful, False otherwise
    """
    try:
        backup_name = create_backup_name(file_info['name'])
        
        print(f"📦 Backing up existing Google Drive file to: {backup_name}")
        
        success = save_manager.move_file_to_folder(
            file_id=file_info['id'],
            target_folder_id=BACKUP_FOLDER_ID,
            new_name=backup_name
        )
        
        if success:
            print(f"✅ Backup created on Google Drive")
            return True
        else:
            print(f"❌ Failed to backup existing file")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def push_pearl_save():
    """Main function to push Pearl save file to Google Drive"""
    
    print("⚪ **POKEMON PEARL VERSION SAVE PUSHER**\n")
    
    # Initialize save manager
    save_manager = GoogleDriveSaveManager(
        credentials_file='credentials.json',
        token_file='token.pickle'
    )
    
    if not save_manager.authenticate():
        print("❌ Authentication failed!")
        return False
    
    # Check if local save file exists
    local_save_path = os.path.join(LOCAL_ROMS_DIR, PEARL_SAVE_NAME)
    local_save_path = os.path.normpath(local_save_path)
    
    if not os.path.exists(local_save_path):
        print(f"❌ Local Pearl save file not found: {local_save_path}")
        print(f"💡 Run pull_pearl.py first to get a save file")
        return False
    
    print(f"✅ Found local save file: {local_save_path}")
    
    # Get file info
    file_size = os.path.getsize(local_save_path)
    file_size_kb = file_size / 1024
    print(f"📊 File size: {file_size_kb:.1f} KB")
    
    # Check if file already exists on Google Drive
    print(f"\n🔍 Checking if file exists on Google Drive...")
    existing_file = save_manager.find_file_in_folder(PEARL_FOLDER_ID, PEARL_SAVE_NAME)
    
    if existing_file:
        print(f"⚠️  File already exists on Google Drive:")
        print(f"📄 Name: {existing_file['name']}")
        print(f"📊 Size: {int(existing_file.get('size', 0)) / 1024:.1f} KB")
        print(f"📅 Modified: {existing_file.get('modifiedTime', 'Unknown')}")
        
        # Modification time safety check - compare when saves were last modified
        print(f"\n🕐 Checking save modification times for safety...")
        if not show_file_comparison(local_save_path, existing_file, "push"):
            print(f"🛑 Operation cancelled by user")
            return False
        
        # Backup the existing file
        print(f"\n📦 Creating backup of existing Google Drive file...")
        backup_success = backup_existing_drive_file(save_manager, existing_file)
        
        if not backup_success:
            print(f"❌ Cannot proceed without backing up existing file")
            return False
    else:
        print(f"✅ No existing file found - proceeding with upload")
    
    # Upload the new file
    print(f"\n⬆️ Uploading local save file to Google Drive...")
    uploaded_file_id = save_manager.upload_file(
        local_file_path=local_save_path,
        folder_id=PEARL_FOLDER_ID,
        file_name=PEARL_SAVE_NAME
    )
    
    if uploaded_file_id:
        print(f"\n🎉 **PEARL SAVE PUSHED SUCCESSFULLY!**")
        print(f"📄 Uploaded: {PEARL_SAVE_NAME}")
        print(f"📂 To folder: {PEARL_FOLDER_ID}")
        print(f"🆔 File ID: {uploaded_file_id}")
        
        if existing_file:
            print(f"📦 Previous version backed up to backup folder")
        
        return True
    else:
        print(f"❌ Failed to upload Pearl save file")
        return False

def list_drive_backups(save_manager: GoogleDriveSaveManager):
    """List recent Pearl backup files in the Google Drive backup folder"""
    
    try:
        # Search for backup files in the backup folder
        backup_files = save_manager.search_files_in_folder(
            folder_id=BACKUP_FOLDER_ID,
            file_types=['.sav']
        )
        
        if backup_files:
            pearl_backups = [f for f in backup_files if 'pearl' in f['name'].lower() and 'backup_' in f['name']]
            
            if pearl_backups:
                total_count = len(pearl_backups)
                recent_count = min(3, total_count)  # Show max 3 recent backups
                
                # Sort by name (which includes timestamp)
                pearl_backups.sort(key=lambda x: x['name'], reverse=True)
                
                print(f"\n📦 **GOOGLE DRIVE BACKUPS:** {total_count} total, showing {recent_count} most recent:")
                
                for backup in pearl_backups[:recent_count]:
                    print(f"  📄 {backup['name']}")
            else:
                print(f"\n📦 **GOOGLE DRIVE BACKUPS:** No Pearl backup files found")
        else:
            print(f"\n📦 **GOOGLE DRIVE BACKUPS:** No backup files found in backup folder")
            
    except Exception as e:
        print(f"\n📦 **GOOGLE DRIVE BACKUPS:** Error listing backups: {e}")

if __name__ == "__main__":
    # Push the Pearl save
    success = push_pearl_save()
    
    if success:
        # Show backup files after successful push
        save_manager = GoogleDriveSaveManager(
            credentials_file='credentials.json',
            token_file='token.pickle'
        )
        if save_manager.authenticate():
            list_drive_backups(save_manager)
        
        print(f"\n✅ Pearl save is now on Google Drive!")
    else:
        print(f"\n❌ Failed to push Pearl save")
