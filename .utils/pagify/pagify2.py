import os
import json
import tkinter as tk
from tkinter import filedialog

def select_base_directory():
    """Opens a dialog to select a directory starting at X:"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    directory = filedialog.askdirectory(initialdir="X:/", title="Select base directory")
    
    return directory

def scan_directory_structure(base_dir):
    """
    Scan the directory structure starting from base_dir
    Returns a hierarchical dictionary representing the folder structure
    Excludes folders starting with 'RRD9'
    """
    if not base_dir or not os.path.exists(base_dir):
        return {}
    
    result = {}
    
    # Get the top-level folders
    try:
        top_folders = [f for f in os.listdir(base_dir) 
                      if os.path.isdir(os.path.join(base_dir, f))]
    except PermissionError:
        print(f"Permission denied for {base_dir}")
        return {}
    
    for folder_name in top_folders:
        folder_path = os.path.join(base_dir, folder_name)
        
        # Skip folders starting with "RRD9"
        if folder_name.startswith("RRD9"):
            continue
        
        # For each top folder, get all subfolders
        subfolders = {}
        try:
            for root, dirs, _ in os.walk(folder_path):
                # Skip RRD9 folders at any level
                dirs[:] = [d for d in dirs if not d.startswith("RRD9")]
                
                # Calculate relative path from the top folder
                if root != folder_path:
                    rel_path = os.path.relpath(root, folder_path)
                    
                    # Build the nested dictionary structure
                    current = subfolders
                    path_parts = rel_path.split(os.sep)
                    
                    for i, part in enumerate(path_parts):
                        if part not in current:
                            current[part] = {}
                        current = current[part]
        except PermissionError:
            print(f"Permission denied for {folder_path}")
            continue
        
        result[folder_name] = subfolders
    
    return result

def main():
    # Step 1: Select the base directory (X: drive)
    base_dir = select_base_directory()
    if not base_dir:
        print("No directory selected. Using X:/ as default.")
        base_dir = "X:/"
    
    print(f"Scanning directory structure of {base_dir}...")
    
    # Step 2 & 3: Scan directory structure and exclude RRD9 folders
    directory_structure = scan_directory_structure(base_dir)
    
    # Step 4: Display as JSON
    json_output = json.dumps(directory_structure, indent=2)
    print(json_output)
    
    # Optional: Save to file for later use
    # Uncomment these lines to save the JSON to a file
    # with open("directory_structure.json", "w") as f:
    #     f.write(json_output)
    # print("Directory structure saved to directory_structure.json")

if __name__ == "__main__":
    main() 