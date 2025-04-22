import os
import shutil

path = r"L:\microfilm+\micro\testing\RRD017-2024_OU_GROSS"
db = r"L:\microfilm+\micro\film_allocation.sqlite3"

# List of subfolders to check and delete if they exist
subfolders = ['.data', '.logs', '.output', '.temp']

for subfolder in subfolders:
    subfolder_path = os.path.join(path, subfolder)
    if os.path.exists(subfolder_path) and os.path.isdir(subfolder_path):
        shutil.rmtree(subfolder_path)
        print(f"\033[31mDeleted: {subfolder_path}\033[0m")

# Remove the database file
os.remove(db)

