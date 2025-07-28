#!/usr/bin/env python3
"""
Download ROMs from Google Drive to local directory
"""

import os
from save_manager import GoogleDriveSaveManager

# Your ROMs folder ID
ROMS_FOLDER_ID = '1AJoT_XxY4W4YjmQDQJw8PLiJZ7ux314G'

def download_roms():
    """Download all ROMs from Google Drive to local roms directory"""
    
    # Initialize save manager with credentials in same directory
    save_manager = GoogleDriveSaveManager(
        credentials_file='credentials.json',
        token_file='token.pickle'
    )
    
    if not save_manager.authenticate():
        print("❌ Authentication failed!")
        return False
    
    print("🎮 **DOWNLOADING POKEMON ROMS**\n")
    
    # Create the roms directory path (relative to project root)
    local_roms_path = "../../roms"
    
    # Download all contents of the ROMs folder
    success = save_manager.download_folder_contents(
        folder_id=ROMS_FOLDER_ID,
        local_directory=local_roms_path,
        file_types=['.gba', '.gb', '.gbc', '.zip', '.7z', '.rar'],  # Common ROM formats
        create_subdirs=True  # Download subfolders too
    )
    
    if success:
        print("\n🎉 ROMs download completed!")
        
        # Show what was downloaded
        if os.path.exists(local_roms_path):
            print(f"\n📁 Contents of {local_roms_path}:")
            for root, dirs, files in os.walk(local_roms_path):
                level = root.replace(local_roms_path, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}📂 {os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    size_mb = size / (1024 * 1024)
                    print(f"{subindent}📄 {file} ({size_mb:.1f} MB)")
        
        return True
    else:
        print("❌ No ROMs were downloaded")
        return False

def download_specific_rom_types():
    """Download only specific ROM types (example)"""
    
    save_manager = GoogleDriveSaveManager(
        credentials_file='credentials.json',
        token_file='token.pickle'
    )
    
    if not save_manager.authenticate():
        return False
    
    print("🎮 **DOWNLOADING ONLY GBA ROMS**\n")
    
    # Download only GBA ROMs
    success = save_manager.download_folder_contents(
        folder_id=ROMS_FOLDER_ID,
        local_directory="../../roms/gba_only",
        file_types=['.gba'],  # Only GBA files
        create_subdirs=False  # Don't create subdirectories
    )
    
    return success


if __name__ == "__main__":
    # Option 1: Download all ROMs
    download_roms()
    
    # Option 2: Uncomment to download only specific types
    # download_specific_rom_types() 