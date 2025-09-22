import os
import argparse

# dir tree structure:
#
# X: 
# └── PROJECT1/                 (folder)
#     └── PDF/                  (subfolder)
#         └── DOCUMENT1.pdf
#         └── DOCUMENT2.pdf
#         └── DOCUMENT3.pdf
#         └── ...
#     └── COM.xlsx
# └── ...

# Parse command line arguments
parser = argparse.ArgumentParser(description="List project folders and subfolders")
parser.add_argument("-f", "--folders", action="store_true", help="Print only project folders")
parser.add_argument("-s", "--subfolders", action="store_true", help="Print only subfolders")
parser.add_argument("-e", "--export", type=str, help="Export to text file (specify filename)")
args = parser.parse_args()

root_folder_path = "X:/"

# Get all project folders in the root folder (excluding system folders)
exclude_folders = {".management", "archive.ico", "autorun.inf", "$RECYCLE.BIN", "System Volume Information"}
project_folders = [f for f in os.listdir(root_folder_path) 
                  if f not in exclude_folders and os.path.isdir(os.path.join(root_folder_path, f))]

total_subfolders = 0
output_lines = []

# For each project folder
for project_folder in project_folders:
    project_path = os.path.join(root_folder_path, project_folder)
    
    try:
        # Get all subfolders within this project (ignore folders starting with .)
        subfolders = [f for f in os.listdir(project_path) 
                     if os.path.isdir(os.path.join(project_path, f)) and not f.startswith('.')]
        
        # Determine what to output based on flags
        if args.folders and not args.subfolders:
            # Only print project folders
            line = f"\033[92m{project_folder}\033[0m"
            print(line)
            output_lines.append(project_folder)
        elif args.subfolders and not args.folders:
            # Only print subfolders
            for subfolder in subfolders:
                line = f"\033[91m{subfolder}\033[0m"
                print(line)
                output_lines.append(subfolder)
        else:
            # Default: print both (project folder - subfolder1, subfolder2)
            if subfolders:
                subfolder_list = ", ".join(subfolders)
                line = f"\033[92m{project_folder}\033[0m - \033[91m{subfolder_list}\033[0m"
                print(line)
                output_lines.append(f"{project_folder} - {subfolder_list}")
            else:
                line = f"\033[92m{project_folder}\033[0m - \033[91mno subfolders\033[0m"
                print(line)
                output_lines.append(f"{project_folder} - no subfolders")
        
        total_subfolders += len(subfolders)
    
    except PermissionError:
        if args.folders and not args.subfolders:
            line = f"\033[92m{project_folder}\033[0m"
            print(line)
            output_lines.append(project_folder)
        elif not (args.subfolders and not args.folders):
            line = f"\033[92m{project_folder}\033[0m - \033[91mPermission denied\033[0m"
            print(line)
            output_lines.append(f"{project_folder} - Permission denied")

# Print summary
print(f"Total project folders: {len(project_folders)}")
print(f"Total subfolders: {total_subfolders}")

# Export to file if requested
if args.export:
    with open(args.export, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')
        f.write(f"Total project folders: {len(project_folders)}\n")
        f.write(f"Total subfolders: {total_subfolders}\n")
    print(f"Output exported to: {args.export}")
