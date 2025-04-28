import os
import win32api, win32con

def folder_is_hidden(p):
    """Check if a folder is hidden or system in Windows."""
    try:
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    except:
        return False

def listdir(drive_path):
    """List all non-hidden directories in the specified path."""
    folders = []
    for f in os.listdir(drive_path):
        full_path = os.path.join(drive_path, f)
        if os.path.isdir(full_path) and not folder_is_hidden(full_path):
            folders.append(f)
    return folders

if __name__ == "__main__":
    try:
        folders = listdir("Y:")
        print("Found folders:", len(folders))
        for folder in folders:
            print(f"  - {folder}")
    except Exception as e:
        print(f"Error listing directory: {e}")
