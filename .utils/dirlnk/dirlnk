import os, shutil
from pathlib import Path

root_path = r"E:\.transfer"

dirs = os.listdir(root_path)

for item in dirs:
    if item.endswith(".lnk"):
        print(f"\033[92m{item}\033[0m")
        item_filepath = os.path.join(root_path, item)
        print(item_filepath)
        
        filename = Path(item).stem.strip("- Shortcut").strip()
        print(f"\033[93m{filename}\033[0m")

        folder = os.path.join(root_path, filename)
        print(folder)

        os.mkdir(folder)
        shutil.move(item_filepath, folder)

