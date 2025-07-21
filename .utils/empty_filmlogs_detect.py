import os

root = r"X:/"

def find_empty_filmlogs(directory):
    """Recursively search for .filmlogs folders and check if they're empty"""
    try:
        # Get list of items in current directory
        items = os.listdir(directory)
        
        for item in items:
            item_path = os.path.join(directory, item)
            
            # Skip files and system/excluded folders
            if (not os.path.isdir(item_path) or 
                item in ["System Volume Information", "tiftopdf", ".management", "$RECYCLE.BIN"] or
                item.startswith("RRD9")):
                continue
            
            # Check if this is a .filmlogs folder
            if item == ".filmlogs":
                try:
                    # Check if the .filmlogs folder is empty
                    filmlogs_contents = os.listdir(item_path)
                    if len(filmlogs_contents) == 0:
                        print(f"\033[32m{directory}\033[0m")
                except PermissionError:
                    # Skip if we can't access the .filmlogs folder
                    pass
            else:
                # Recursively search subdirectories
                find_empty_filmlogs(item_path)
                
    except (PermissionError, OSError):
        # Skip directories we can't access
        pass

# Start the search
find_empty_filmlogs(root)



