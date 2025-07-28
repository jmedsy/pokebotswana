#!/usr/bin/env python3
"""
Demo: Searching specific directories in Google Drive
"""

import os
import sys

# Add tools directory to path so we can import save_manager
sys.path.append('tools')
from save_manager import GoogleDriveSaveManager

def demo_directory_search():
    """Demonstrate searching specific Google Drive directories"""
    
    # Initialize with correct credentials path
    save_manager = GoogleDriveSaveManager(
        credentials_file='tools/save_manager/credentials.json',
        token_file='tools/save_manager/token.pickle'
    )
    
    if not save_manager.authenticate():
        print("❌ Authentication failed!")
        return
    
    print("🎯 **DIRECTORY-SPECIFIC SEARCH DEMO**\n")
    
    # Method 1: Search by folder name
    print("1️⃣ **Search in 'pokebotswana' folder:**")
    files = save_manager.search_files_in_folder(
        folder_name="pokebotswana",
        file_types=['.sav', '.py', '.dat']
    )
    print(f"Found {len(files)} files in pokebotswana folder\n")
    
    print("="*60 + "\n")
    
    # Method 2: Search in 'old saves' folder
    print("2️⃣ **Search in 'old saves' folder:**")
    files = save_manager.search_files_in_folder(
        folder_name="old saves",
        file_types=['.sav', '.dat', '.srm']
    )
    print(f"Found {len(files)} save files in old saves folder\n")
    
    print("="*60 + "\n")
    
    # Method 3: Search in 'emerald' folder
    print("3️⃣ **Search in 'emerald' folder:**")
    files = save_manager.search_files_in_folder(
        folder_name="emerald",
        file_types=['.sav', '.dat']
    )
    print(f"Found {len(files)} files in emerald folder\n")
    
    print("="*60 + "\n")
    
    # Method 4: List folders to find what directories you have
    print("4️⃣ **Available Pokemon/Game-related folders:**")
    folders = save_manager.list_folders(show_ids=False)
    
    pokemon_keywords = ['pokemon', 'emerald', 'fire', 'red', 'save', 'rom', 'gb', 'gba']
    relevant_folders = []
    
    for folder in folders:
        name_lower = folder['name'].lower()
        if any(keyword in name_lower for keyword in pokemon_keywords):
            relevant_folders.append(folder['name'])
    
    if relevant_folders:
        print(f"\n🎮 **Found {len(relevant_folders)} game-related folders:**")
        for folder_name in relevant_folders:
            print(f"  📂 {folder_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Method 5: Search using direct folder ID (if you know it)
    print("5️⃣ **Example: Search using direct folder ID:**")
    print("# If you know the folder ID, you can search directly:")
    print("# files = save_manager.search_files_in_folder(")
    print("#     folder_id='1NhYJ_NsG5QtMhr3-BTxRo4PyfywplCFi',  # pokebotswana folder")
    print("#     file_types=['.sav']")
    print("# )")


if __name__ == "__main__":
    demo_directory_search() 