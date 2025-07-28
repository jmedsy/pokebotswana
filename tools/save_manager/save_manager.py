#!/usr/bin/env python3
"""
Google Drive Save File Manager
Downloads Pokemon save files from specific directories in Google Drive
"""

POKEBOTSWANA_FOLDER_ID = '1NhYJ_NsG5QtMhr3-BTxRo4PyfywplCFi'

import io
import os
import pickle
import time
from typing import List, Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError

# Google Drive API scopes (added write access for uploads)
SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDriveSaveManager:
    """Manages downloading save files from specific Google Drive directories"""
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        creds = None
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"Credentials file {self.credentials_file} not found!")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building service: {e}")
            return False
    
    def find_folder_by_name(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """
        Find a folder by name and return its ID
        
        Args:
            folder_name: Name of the folder to find
            parent_id: ID of parent folder to search in (None for root)
            
        Returns:
            Folder ID if found, None otherwise
        """
        if not self.service:
            return None
            
        try:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                print(f"✅ Found folder '{folder_name}': {folders[0]['id']}")
                return folders[0]['id']
            else:
                print(f"❌ Folder '{folder_name}' not found")
                return None
                
        except HttpError as error:
            print(f'Error finding folder: {error}')
            return None
    
    def list_folders(self, parent_id: str = None, show_ids: bool = True) -> List[Dict[str, Any]]:
        """
        List folders in Google Drive
        
        Args:
            parent_id: Parent folder ID (None for root)
            show_ids: Whether to print folder IDs
            
        Returns:
            List of folder metadata dictionaries
        """
        if not self.service:
            return []
        
        try:
            query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, modifiedTime)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                print(f'📁 Found {len(folders)} folders:')
                for folder in folders:
                    if show_ids:
                        print(f"  📂 {folder['name']} (ID: {folder['id']})")
                    else:
                        print(f"  📂 {folder['name']}")
            else:
                print("No folders found")
            
            return folders
            
        except HttpError as error:
            print(f'Error listing folders: {error}')
            return []
    
    def search_files_in_folder(self, folder_name: str = None, folder_id: str = None, 
                              file_types: List[str] = None, query: str = None, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Search for files in a specific folder
        
        Args:
            folder_name: Name of folder to search in (will find ID automatically)
            folder_id: Direct folder ID to search in
            file_types: List of file extensions to filter by
            query: Additional search query
            
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            print("Not authenticated. Call authenticate() first.")
            return []
        
        # Get folder ID if folder name provided
        target_folder_id = folder_id
        if folder_name and not folder_id:
            target_folder_id = self.find_folder_by_name(folder_name)
            if not target_folder_id:
                return []
        
        try:
            # Build search query
            search_query = ["trashed=false"]
            
            if target_folder_id:
                search_query.append(f"'{target_folder_id}' in parents")
                print(f"🔍 Searching in folder ID: {target_folder_id}")
            else:
                print("🔍 Searching in root directory")
            
            if query:
                search_query.append(query)
            
            if file_types:
                type_queries = []
                for ext in file_types:
                    type_queries.append(f"name contains '{ext}'")
                search_query.append(f"({' or '.join(type_queries)})")
            
            q = " and ".join(search_query)
            
            # Execute search
            results = self.service.files().list(
                q=q,
                pageSize=100,
                fields="files(id, name, size, modifiedTime, mimeType)"
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                if verbose:
                    print('No files found in specified directory.')
                return []
            
            if verbose:
                print(f'📄 Found {len(items)} files:')
                for item in items:
                    size = int(item.get('size', 0)) if item.get('size') else 0
                    print(f"  📄 {item['name']} ({size} bytes)")
            
            return items
            
        except HttpError as error:
            print(f'An error occurred during search: {error}')
            return []
    
    def download_file(self, file_id: str, destination: str) -> bool:
        """Download a file from Google Drive"""
        if not self.service:
            return False
        
        try:
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata['name']
            
            print(f"⬇️ Downloading {file_name}...")
            
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Progress: {int(status.progress() * 100)}%")
            
            with open(destination, 'wb') as f:
                f.write(fh.getvalue())
            
            # Preserve original modification time from Google Drive
            if 'modifiedTime' in file_metadata:
                from save_helpers import parse_google_drive_timestamp
                
                original_time = parse_google_drive_timestamp(file_metadata['modifiedTime'])
                timestamp = original_time.timestamp()
                os.utime(destination, (timestamp, timestamp))
                print(f"🕐 Preserved original timestamp: {original_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"✅ Downloaded {file_name}")
            return True
            
        except Exception as e:
            print(f'❌ Download failed: {e}')
            return False
    
    def download_folder_contents(self, folder_id: str, local_directory: str, 
                                file_types: List[str] = None, create_subdirs: bool = True) -> bool:
        """
        Download all contents of a Google Drive folder to a local directory
        
        Args:
            folder_id: Google Drive folder ID to download from
            local_directory: Local directory path to download files to
            file_types: Optional list of file extensions to filter (e.g., ['.gba', '.zip'])
            create_subdirs: Whether to create subdirectories for subfolders
            
        Returns:
            True if at least one file was downloaded successfully
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        print(f"📁 Downloading contents of folder ID: {folder_id}")
        print(f"📂 To local directory: {local_directory}")
        
        # Create the local directory if it doesn't exist
        os.makedirs(local_directory, exist_ok=True)
        
        try:
            # Search for all files in the specified folder
            search_query = [f"'{folder_id}' in parents", "trashed=false"]
            
            # Add file type filter if specified
            if file_types:
                type_queries = []
                for ext in file_types:
                    type_queries.append(f"name contains '{ext}'")
                search_query.append(f"({' or '.join(type_queries)})")
            
            q = " and ".join(search_query)
            
            # Get all files and folders in the directory
            results = self.service.files().list(
                q=q,
                pageSize=1000,  # Get up to 1000 items
                fields="files(id, name, size, mimeType, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                print("📄 No files found in the specified folder.")
                return False
            
            files_downloaded = 0
            folders_found = 0
            
            for item in items:
                item_name = item['name']
                item_id = item['id']
                item_type = item.get('mimeType', '')
                
                # Check if it's a folder
                if item_type == 'application/vnd.google-apps.folder':
                    folders_found += 1
                    if create_subdirs:
                        subfolder_path = os.path.join(local_directory, item_name)
                        print(f"📁 Found subfolder: {item_name}")
                        # Recursively download subfolder contents
                        self.download_folder_contents(item_id, subfolder_path, file_types, create_subdirs)
                    else:
                        print(f"📁 Skipping subfolder: {item_name} (create_subdirs=False)")
                else:
                    # It's a file - download it
                    file_path = os.path.join(local_directory, item_name)
                    
                    # Skip if file already exists
                    if os.path.exists(file_path):
                        print(f"⏭️  Skipping {item_name} (already exists)")
                        continue
                    
                    if self.download_file(item_id, file_path):
                        files_downloaded += 1
            
            print(f"\n✅ Download Summary:")
            print(f"   📄 Files downloaded: {files_downloaded}")
            print(f"   📁 Subfolders found: {folders_found}")
            print(f"   📂 Downloaded to: {local_directory}")
            
            return files_downloaded > 0
            
        except Exception as e:
            print(f"❌ Error downloading folder contents: {e}")
            return False
    
    def upload_file(self, local_file_path: str, folder_id: str, file_name: str = None) -> str:
        """
        Upload a file to Google Drive
        
        Args:
            local_file_path: Path to the local file to upload
            folder_id: Google Drive folder ID to upload to
            file_name: Name for the file on Google Drive (defaults to local filename)
            
        Returns:
            File ID of uploaded file if successful, None otherwise
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        if not os.path.exists(local_file_path):
            print(f"❌ Local file not found: {local_file_path}")
            return None
        
        try:
            # Use local filename if no custom name provided
            if not file_name:
                file_name = os.path.basename(local_file_path)
            
            print(f"⬆️ Uploading {file_name} to Google Drive...")
            
            # File metadata
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Create media upload object
            media = MediaFileUpload(local_file_path, resumable=True)
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            print(f"✅ Uploaded successfully! File ID: {file_id}")
            return file_id
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None
    
    def move_file_to_folder(self, file_id: str, target_folder_id: str, new_name: str = None) -> bool:
        """
        Move a file to a different folder (for backup purposes)
        
        Args:
            file_id: ID of the file to move
            target_folder_id: ID of the destination folder
            new_name: Optional new name for the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        try:
            # Get current file metadata
            file_metadata = self.service.files().get(fileId=file_id, fields='parents,name').execute()
            previous_parents = ",".join(file_metadata.get('parents'))
            current_name = file_metadata.get('name')
            
            # Prepare update data
            update_data = {}
            
            # Add new name if provided
            if new_name:
                update_data['name'] = new_name
                print(f"📦 Moving and renaming '{current_name}' to '{new_name}'...")
            else:
                print(f"📦 Moving '{current_name}' to backup folder...")
            
            # Move file to new folder
            updated_file = self.service.files().update(
                fileId=file_id,
                addParents=target_folder_id,
                removeParents=previous_parents,
                body=update_data,
                fields='id,name'
            ).execute()
            
            print(f"✅ File moved successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to move file: {e}")
            return False
    
    def find_file_in_folder(self, folder_id: str, file_name: str) -> dict:
        """
        Find a specific file by name in a folder
        
        Args:
            folder_id: Google Drive folder ID to search in
            file_name: Exact name of the file to find
            
        Returns:
            File metadata dict if found, None otherwise
        """
        if not self.service:
            return None
        
        try:
            query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]  # Return first match
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error searching for file: {e}")
            return None


def demo_folder_search():
    """Demo of searching specific folders"""
    save_manager = GoogleDriveSaveManager()
    
    if not save_manager.authenticate():
        return
    
    print("=== FOLDER SEARCH DEMO ===\n")
    
    # Method 1: Search by folder name
    print("1️⃣ Searching in 'pokebotswana' folder:")
    files = save_manager.search_files_in_folder(
        folder_name="pokebotswana",
        file_types=['.sav', '.py']
    )
    
    print("\n" + "="*50 + "\n")
    
    # Method 2: Search in 'old saves' folder
    print("2️⃣ Searching in 'old saves' folder:")
    files = save_manager.search_files_in_folder(
        folder_name="old saves",
        file_types=['.sav', '.dat']
    )
    
    print("\n" + "="*50 + "\n")
    
    # Method 3: List all folders to find Pokemon-related ones
    print("3️⃣ Finding Pokemon-related folders:")
    folders = save_manager.list_folders()
    
    pokemon_folders = []
    for folder in folders:
        name_lower = folder['name'].lower()
        if any(keyword in name_lower for keyword in ['pokemon', 'emerald', 'fire', 'save', 'rom']):
            pokemon_folders.append(folder)
    
    if pokemon_folders:
        print(f"\n🎮 Found {len(pokemon_folders)} Pokemon-related folders:")
        for folder in pokemon_folders:
            print(f"  📂 {folder['name']}")


if __name__ == "__main__":
    # demo_folder_search()
    save_manager = GoogleDriveSaveManager()
    if save_manager.authenticate():
        print(save_manager.find_folder_by_name("saves"))