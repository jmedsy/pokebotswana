#!/usr/bin/env python3
"""
Helper functions for save file management
Handles timestamp comparisons and user confirmations
"""

import os
from datetime import datetime, timezone

def parse_google_drive_timestamp(timestamp_str: str) -> datetime:
    """
    Parse Google Drive timestamp string to local datetime object
    
    Args:
        timestamp_str: ISO format timestamp from Google Drive API (e.g., '2024-07-28T10:15:30.000Z')
        
    Returns:
        datetime object in local timezone
    """
    try:
        # Google Drive returns UTC timestamps with 'Z' suffix
        if timestamp_str.endswith('Z'):
            # Remove 'Z' and parse as UTC
            timestamp_str = timestamp_str[:-1]
            if '.' in timestamp_str:
                timestamp_str = timestamp_str.split('.')[0]
            
            # Parse as UTC then convert to local time (timezone-naive)
            utc_dt = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
            local_dt = utc_dt.astimezone()  # Convert to local timezone
            return local_dt.replace(tzinfo=None)  # Make timezone-naive for comparison
        else:
            # Fallback for timestamps without 'Z'
            if '.' in timestamp_str:
                timestamp_str = timestamp_str.split('.')[0]
            return datetime.fromisoformat(timestamp_str)
            
    except Exception as e:
        print(f"⚠️  Warning: Could not parse timestamp '{timestamp_str}': {e}")
        # Fallback to current time if parsing fails
        return datetime.now()

def get_local_file_timestamp(file_path: str) -> datetime:
    """
    Get the modification timestamp of a local file
    
    Args:
        file_path: Path to the local file
        
    Returns:
        datetime object of file modification time (timezone-naive, local time)
    """
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        # Return timezone-naive datetime in local time for consistency
        return datetime.fromtimestamp(timestamp)
    else:
        # Return epoch if file doesn't exist
        return datetime.fromtimestamp(0)

def format_timestamp(dt: datetime) -> str:
    """
    Format datetime for display
    
    Args:
        dt: datetime object
        
    Returns:
        Formatted string
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def confirm_overwrite_newer_file(operation: str, local_time: datetime, remote_time: datetime, 
                                local_name: str, remote_name: str) -> bool:
    """
    Ask user confirmation when trying to overwrite a more recently modified file
    
    Args:
        operation: "push" or "pull"
        local_time: Local file modification timestamp
        remote_time: Remote file modification timestamp  
        local_name: Local file description
        remote_name: Remote file description
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n⚠️  **MODIFICATION TIME WARNING**")
    print(f"📅 {local_name} last modified: {format_timestamp(local_time)}")
    print(f"📅 {remote_name} last modified: {format_timestamp(remote_time)}")
    
    if operation == "push":
        if remote_time > local_time:
            time_diff = remote_time - local_time
            print(f"\n🚨 **DANGER**: Google Drive save was modified {time_diff} MORE RECENTLY!")
            print(f"   Pushing will overwrite more recent progress on Google Drive.")
            
            response = input(f"\n❓ Are you sure you want to overwrite the more recently modified Google Drive save? (yes/no): ").strip().lower()
            return response in ['yes', 'y']
        else:
            print(f"\n✅ Local save was modified more recently - safe to push")
            return True
            
    elif operation == "pull":
        if local_time > remote_time:
            time_diff = local_time - remote_time
            print(f"\n🚨 **DANGER**: Your local save was modified {time_diff} MORE RECENTLY!")
            print(f"   Pulling will overwrite more recent local progress.")
            
            response = input(f"\n❓ Are you sure you want to overwrite your more recently modified local save? (yes/no): ").strip().lower()
            return response in ['yes', 'y']
        else:
            print(f"\n✅ Google Drive save was modified more recently - safe to pull")
            return True
    
    return True

def show_file_comparison(local_path: str, remote_file: dict, operation: str) -> bool:
    """
    Show save file modification time comparison and get user confirmation if needed
    
    Args:
        local_path: Path to local save file
        remote_file: Google Drive file metadata dict
        operation: "push" or "pull"
        
    Returns:
        True if operation should proceed, False if cancelled
    """
    local_time = get_local_file_timestamp(local_path)
    remote_time_str = remote_file.get('modifiedTime', '')
    remote_time = parse_google_drive_timestamp(remote_time_str) if remote_time_str else datetime.now()
    
    local_name = f"Local save ({os.path.basename(local_path)})"
    remote_name = f"Google Drive save ({remote_file['name']})"
    
    return confirm_overwrite_newer_file(operation, local_time, remote_time, local_name, remote_name) 