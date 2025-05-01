import os
import shutil
import curses
from tkinter import Tk
from tkinter.filedialog import askdirectory

def get_directory_info():
    import os
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\033[36mtool_dir: {tool_dir}\033[0m")

    root_dir = os.path.dirname(tool_dir)
    print(f"\033[33mroot_dir: {root_dir}\033[0m")

    target_dir = os.path.join(root_dir, "target")
    print(f"\033[34mtarget_dir: {target_dir}\033[0m")

    root_folders = [folder for folder in os.listdir(root_dir) 
                    if os.path.isdir(os.path.join(root_dir, folder)) 
                    and folder != os.path.basename(tool_dir)
                    and folder != os.path.basename(target_dir)]

    ou_folder = [folder for folder in root_folders if "Übergabe_aus_OU" in folder]
    dw_folder = [folder for folder in root_folders if "Übergabe_aus_DW" in folder]

    print(f"\033[32mou_folder: {ou_folder}\033[0m")

    ou_folders = [folder for folder in os.listdir(os.path.join(root_dir, ou_folder[0])) 
                 if os.path.isdir(os.path.join(root_dir, ou_folder[0], folder))]

    print(f"\033[32mou_folders: {ou_folders}\033[0m")

    print(f"\033[31mdw_folder: {dw_folder}\033[0m")

    dw_folders = [folder for folder in os.listdir(os.path.join(root_dir, dw_folder[0])) 
                 if os.path.isdir(os.path.join(root_dir, dw_folder[0], folder))]

    print(f"\033[31mdw_folders: {dw_folders}\033[0m")

    return {
        "ou_folder": ou_folder,
        "ou_folders": ou_folders,
        "dw_folder": dw_folder,
        "dw_folders": dw_folders,
        "target_dir": target_dir,
        "root_dir": root_dir
    }

def copy_folders_to_target(selected_folder, target_dir, folder_type):
    """Copy the selected folder to the target directory and rename the original folder."""
    directory_info = get_directory_info()
    root_dir = directory_info["root_dir"]  # This is the correct root directory

    # Determine the correct source path based on the folder type
    if folder_type == "OU":
        source_path = os.path.join(root_dir, "Übergabe_aus_OU", selected_folder)
    else:  # DW
        source_path = os.path.join(root_dir, "Übergabe_aus_DW", selected_folder)

    destination_path = os.path.join(target_dir, selected_folder)

    # Check if the source path exists
    if not os.path.exists(source_path):
        print(f"Source folder does not exist: {source_path}")
        return

    # Copy the folder
    shutil.copytree(source_path, destination_path)
    print(f"Copied {selected_folder} to {destination_path}")

    # Rename the original folder by adding a '.' prefix
    new_name = f".{selected_folder}"
    new_source_path = os.path.join(os.path.dirname(source_path), new_name)

    os.rename(source_path, new_source_path)
    print(f"Renamed original folder to: {new_name}")

def folder_dialog():
    """Open a folder dialog to choose the target directory."""
    Tk().withdraw()  # Prevents the root window from appearing
    return askdirectory(title="Select Target Directory")

def curses_ui(stdscr):
    """Curses UI for selecting folders."""
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()

    # Get directory info
    directory_info = get_directory_info()
    options = ["OU", "DW"]
    selected_option = 0

    # Main menu loop for selecting OU/DW
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select Folder Type (Use arrow keys to navigate, Enter to select):")
        for idx, option in enumerate(options):
            if idx == selected_option:
                stdscr.addstr(idx + 1, 0, f"> {option}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {option}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_option > 0:
            selected_option -= 1
        elif key == curses.KEY_DOWN and selected_option < len(options) - 1:
            selected_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            folder_type = options[selected_option]
            folders = directory_info[f"{folder_type.lower()}_folders"]
            break

    # Select subfolder to copy
    selected_subfolder = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Select {folder_type} Subfolder (Use arrow keys to navigate, Enter to select):")
        for idx, folder in enumerate(folders):
            if idx == selected_subfolder:
                stdscr.addstr(idx + 1, 0, f"> {folder}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {folder}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_subfolder > 0:
            selected_subfolder -= 1
        elif key == curses.KEY_DOWN and selected_subfolder < len(folders) - 1:
            selected_subfolder += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            break

    # Choose target directory from options
    target_options = ["Copy to Default Target Directory", "Choose Folder"]
    selected_target = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select Target Directory Option (Use arrow keys to navigate, Enter to select):")
        for idx, option in enumerate(target_options):
            if idx == selected_target:
                stdscr.addstr(idx + 1, 0, f"> {option}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 0, f"  {option}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_target > 0:
            selected_target -= 1
        elif key == curses.KEY_DOWN and selected_target < len(target_options) - 1:
            selected_target += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_target == 0:
                target_dir = directory_info["target_dir"]  # Use default target directory
            else:
                target_dir = folder_dialog()  # Open folder dialog
            break

    # Copy the selected subfolder
    copy_folders_to_target(folders[selected_subfolder], target_dir, folder_type)

if __name__ == "__main__":
    curses.wrapper(curses_ui)







