import configparser
import subprocess
import time
import sys
import argparse
import os
from logger import get_logger, LogLevel
from pywinauto import Application
from datetime import datetime, timedelta
import importlib.util
import pathlib
import threading

# Advanced finish features imports
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    print("Warning: tkinter not available. Red overlay will be disabled.")
    TKINTER_AVAILABLE = False

try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    print("Warning: screeninfo not available. Using fallback monitor detection.")
    SCREENINFO_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("Warning: pyautogui not available. Mouse control will be simulated.")
    PYAUTOGUI_AVAILABLE = False

# Import lock_mouse dynamically, handling the case when it might not be available
try:
    lock_mouse_spec = importlib.util.spec_from_file_location(
        "lock_mouse", 
        os.path.join(pathlib.Path(__file__).parent.absolute(), "lock_mouse.py")
    )
    lock_mouse = importlib.util.module_from_spec(lock_mouse_spec)
    lock_mouse_spec.loader.exec_module(lock_mouse)
    LOCK_MOUSE_AVAILABLE = True
except Exception as e:
    print(f"Warning: lock_mouse module not available: {e}")
    LOCK_MOUSE_AVAILABLE = False

# Import firebase_notif dynamically, handling the case when it might not be available
try:
    firebase_notif_spec = importlib.util.spec_from_file_location(
        "firebase_notif", 
        os.path.join(pathlib.Path(__file__).parent.absolute(), "firebase_notif.py")
    )
    firebase_notif = importlib.util.module_from_spec(firebase_notif_spec)
    firebase_notif_spec.loader.exec_module(firebase_notif)
    FIREBASE_NOTIF_AVAILABLE = True
except Exception as e:
    print(f"Warning: firebase_notif module not available: {e}")
    FIREBASE_NOTIF_AVAILABLE = False

class RedOverlay:
    """Creates a transparent red overlay on the specified monitor for finish warnings."""
    
    def __init__(self, monitor_info):
        self.monitor_info = monitor_info
        self.root = None
        self.is_visible = False
        self.current_opacity = 0.0
        self.warning_label = None
        self.frame_label = None
        self.start_time = None
        self.target_opacity = 0.75  # 75%
        self.fade_in_duration = 5.0  # 5 seconds to reach 75%
        
    def show(self, remaining_frames=0):
        """Show the red overlay."""
        if not self.is_visible and TKINTER_AVAILABLE:
            try:
                self.start_time = time.time()
                
                self.root = tk.Tk()
                self.root.overrideredirect(True)
                self.root.attributes('-topmost', True)
                self.root.configure(bg='red')
                
                # Set window to cover the entire left monitor
                geometry = f"{self.monitor_info['width']}x{self.monitor_info['height']}+{self.monitor_info['x']}+{self.monitor_info['y']}"
                self.root.geometry(geometry)
                
                # Warning text at the top - yellow, bold
                self.warning_label = tk.Label(
                    self.root, 
                    text="⚠️ SMA PROCESS FINISHING ⚠️\nPREPARE TO RELEASE MOUSE CONTROL\nSTAY READY FOR COMPLETION", 
                    bg='red', 
                    fg='yellow', 
                    font=('Arial', 28, 'bold'),
                    justify='center'
                )
                self.warning_label.place(relx=0.5, rely=0.15, anchor='center')
                
                # Frame count display - center, yellow, bold, huge
                self.frame_label = tk.Label(
                    self.root,
                    text=f"{remaining_frames}",
                    bg='red',
                    fg='yellow',
                    font=('Arial', 320, 'bold'),
                    justify='center'
                )
                self.frame_label.place(relx=0.5, rely=0.5, anchor='center')
                
                self.is_visible = True
                self.root.attributes('-alpha', 0.0)
                self.current_opacity = 0.0
                self.root.update()
                
            except Exception as e:
                print(f"Error showing red overlay: {e}")
    
    def update_opacity_smooth(self):
        """Update opacity smoothly based on elapsed time."""
        if not self.start_time or not self.root or not self.is_visible:
            return
            
        try:
            elapsed_time = time.time() - self.start_time
            
            if elapsed_time >= self.fade_in_duration:
                opacity = self.target_opacity  # Cap at 75%
            else:
                progress = elapsed_time / self.fade_in_duration
                opacity = progress * self.target_opacity
                
            # Update opacity if significantly changed
            if abs(opacity - self.current_opacity) > 0.01:
                self.current_opacity = opacity
                self.root.attributes('-alpha', self.current_opacity)
                
        except Exception as e:
            print(f"Error updating opacity: {e}")
                
    def update_frame_count(self, remaining_frames):
        """Update the frame count display."""
        if self.frame_label and self.is_visible:
            try:
                self.frame_label.config(text=f"{remaining_frames}")
            except Exception as e:
                print(f"Error updating frame count: {e}")
                
    def hide(self):
        """Hide the red overlay."""
        if self.root and self.is_visible:
            try:
                self.root.destroy()
                self.root = None
                self.warning_label = None
                self.frame_label = None
                self.is_visible = False
            except Exception as e:
                print(f"Error hiding red overlay: {e}")
            
    def update(self, remaining_frames=None):
        """Update the overlay (call this in main loop)."""
        if self.is_visible and self.root:
            try:
                self.update_opacity_smooth()
                if remaining_frames is not None:
                    self.update_frame_count(remaining_frames)
                self.root.update()
            except Exception as e:
                print(f"Error updating overlay: {e}")

class MouseLocker:
    """Locks mouse to a specific position on screen."""
    
    def __init__(self):
        self.is_locked = False
        self.lock_thread = None
        self.should_stop = False
        self.lock_position = None
        
    def lock_to_position(self, x, y):
        """Lock mouse to specific coordinates."""
        if self.is_locked or not PYAUTOGUI_AVAILABLE:
            return
            
        self.lock_position = (x, y)
        self.is_locked = True
        self.should_stop = False
        
        pyautogui.moveTo(x, y)
        self.lock_thread = threading.Thread(target=self._lock_loop, daemon=True)
        self.lock_thread.start()
        
    def release(self):
        """Release mouse lock."""
        if not self.is_locked:
            return
            
        self.should_stop = True
        self.is_locked = False
        
        if self.lock_thread and PYAUTOGUI_AVAILABLE:
            self.lock_thread.join(timeout=1)
        
    def _lock_loop(self):
        """Internal loop that keeps mouse locked to position."""
        while not self.should_stop and self.is_locked:
            try:
                if PYAUTOGUI_AVAILABLE:
                    current_pos = pyautogui.position()
                    if abs(current_pos.x - self.lock_position[0]) > 5 or abs(current_pos.y - self.lock_position[1]) > 5:
                        pyautogui.moveTo(self.lock_position[0], self.lock_position[1])
                time.sleep(0.05)  # Check every 50ms
            except Exception as e:
                print(f"Error in mouse lock loop: {e}")
                break

def get_monitor_info():
    """Get information about available monitors."""
    monitors = []
    
    if SCREENINFO_AVAILABLE:
        try:
            screen_monitors = get_monitors()
            for i, monitor in enumerate(screen_monitors):
                monitors.append({
                    'id': i + 1,
                    'x': monitor.x,
                    'y': monitor.y,
                    'width': monitor.width,
                    'height': monitor.height
                })
        except Exception as e:
            print(f"Error getting monitor info with screeninfo: {e}")
    
    # Fallback: Use tkinter to get primary monitor info
    if not monitors and TKINTER_AVAILABLE:
        try:
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            
            # Assume dual monitor setup with left monitor
            monitors = [
                {'id': 1, 'x': 0, 'y': 0, 'width': width, 'height': height},
                {'id': 2, 'x': -width, 'y': 0, 'width': width, 'height': height}  # Left monitor
            ]
        except Exception as e:
            print(f"Error with tkinter fallback: {e}")
    
    return monitors

def get_left_monitor():
    """Get information about the left monitor (monitor 2)."""
    monitors = get_monitor_info()
    
    if len(monitors) >= 2:
        # Find the leftmost monitor (most negative x coordinate)
        left_monitor = min(monitors, key=lambda m: m['x'])
        return left_monitor
    elif len(monitors) == 1:
        return monitors[0]
    else:
        return None

def get_monitor_center(monitor_info):
    """Get the center point of a specific monitor."""
    if monitor_info:
        center_x = monitor_info['x'] + (monitor_info['width'] // 2)
        center_y = monitor_info['y'] + (monitor_info['height'] // 2)
        return center_x, center_y
    return None, None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='File Converter Automation Script')
    parser.add_argument('folder_path', help='Path to the folder to process')
    parser.add_argument('template', choices=['16', '35'], help='Template to use: 16 for Portrait - 16mm.TPL, 35 for Landscape - 35mm.TPL')
    parser.add_argument('--filmnumber', help='Custom film number to use (default: folder name)')
    parser.add_argument('--recovery', action='store_true', help='Attempt to recover and continue an existing scanning session')
    return parser.parse_args()

def setup_logging():
    """Configure and return a logger."""
    return get_logger(name="FileConverter", log_level=LogLevel.DEBUG.value)

def load_configuration(args):
    """Load configuration parameters."""
    # Map template choice to template name
    template_map = {
        '16': "16mm.TPL",
        '35': "35mm.TPL"
    }
    
    # Create configuration dictionary
    config = {
        'template_name': template_map[args.template],
        'ini_file_path': r"Y:\SMA\file-converter-64\docufileuc.ini",
        'folder_path': args.folder_path,
        'app_path': r"Y:\SMA\file-converter-64\file-sma.exe",
        'templates_dir': r"Y:\SMA\file-converter-64\TEMPLATES"
    }
    
    return config

def create_log_directory(folder_path, logger):
    """Create filmlogs directory in the parent folder of the selected folder."""
    # Get parent of parent folder
    parent_folder = os.path.dirname(os.path.dirname(folder_path))
    filmlogs_dir = os.path.join(parent_folder, ".filmlogs")
    
    # Create the filmlogs directory if it doesn't exist
    if not os.path.exists(filmlogs_dir):
        os.makedirs(filmlogs_dir)
        logger.info(f"Created filmlogs directory: {filmlogs_dir}")
    else:
        logger.info(f"Using existing filmlogs directory: {filmlogs_dir}")
    
    return filmlogs_dir, parent_folder

def update_template_file(template_path, log_dir, template_name, logger):
    """Edit TPL file with the log file path."""
    try:
        # Read the TPL file
        with open(template_path, 'r', encoding='cp1252') as tpl_file:
            tpl_lines = tpl_file.readlines()
        
        # Replace the LOGFILEPATH
        updated_lines = []
        
        for line in tpl_lines:
            if line.startswith('LOGFILEPATH='):
                updated_lines.append(f'LOGFILEPATH={log_dir}\n')
            else:
                updated_lines.append(line)
        
        # Write the updated content back to the file
        with open(template_path, 'w', encoding='cp1252') as tpl_file:
            tpl_file.writelines(updated_lines)
        
        logger.info(f"Updated LOGFILEPATH in {template_name} to {log_dir}")
        return True
    except Exception as e:
        logger.error(f"Error updating TPL file: {e}")
        # Print more detailed error information
        import traceback
        logger.error(traceback.format_exc())
        return False

def update_ini_file(ini_path, folder_path, logger):
    """Update INI file with folder path."""
    try:
        # Create a ConfigParser object
        config = configparser.ConfigParser()
        
        # Open the INI file with UTF-16 encoding
        with open(ini_path, 'r', encoding='utf-16') as configfile:
            config.read_file(configfile)
        
        # Modify the PFAD entry under the SYSTEM section
        config.set('SYSTEM', 'PFAD', folder_path)
        
        # Save the changes back to the INI file
        with open(ini_path, 'w', encoding='utf-16') as configfile:
            config.write(configfile)
        
        logger.info(f"PFAD updated to: {folder_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating INI file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_for_existing_session(app_path, logger):
    """Check if an existing SMA session is running with active scanning."""
    logger.info("Checking if SMA process is already running with active scanning...")
    try:
        # Try to connect to an existing SMA application
        existing_app = Application(backend="uia").connect(path=app_path)
        logger.info("Found existing SMA process")
        
        # Check if "Verfilmen der Dokumente" window is open
        try:
            verfilmen_window = existing_app.window(title="Verfilmen der Dokumente")
            if verfilmen_window.exists():
                logger.info("'Verfilmen der Dokumente' window is open. This appears to be an active scanning session.")
                return True, existing_app, verfilmen_window
        except Exception as e:
            logger.info("'Verfilmen der Dokumente' window is not open.")
        
        logger.info("No active scanning session found in the existing SMA process.")
        return False, existing_app, None
    
    except Exception as e:
        logger.info("No existing SMA process found.")
        return False, None, None

def recover_session(app, film_window, logger):
    """Recover an existing scanning session."""
    logger.info("Attempting to recover existing scanning session...")
    
    try:
        # Check if this is actually a Verfilmen der Dokumente window
        if film_window.window_text() != "Verfilmen der Dokumente":
            logger.warning("The window doesn't seem to be a 'Verfilmen der Dokumente' window. Cannot recover.")
            return False, None
        
        # Try to find the film number by looking at window information
        film_number = None
        try:
            # This is just a guess - we'd need to inspect actual window structure
            # to properly extract film number
            children = film_window.children()
            for child in children:
                try:
                    text = child.window_text()
                    if "Film" in text and ":" in text:
                        # This might contain the film number
                        parts = text.split(":")
                        if len(parts) > 1:
                            film_number = parts[1].strip()
                            logger.info(f"Recovered film number: {film_number}")
                            break
                except Exception as e:
                    pass
        except Exception as e:
            logger.warning(f"Could not recover film number: {e}")
        
        # Set focus on the window to ensure it's active
        film_window.set_focus()
        logger.info("Successfully recovered scanning session!")
        
        return True, film_number
    
    except Exception as e:
        logger.error(f"Error recovering session: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, None

def check_running_instance(app_path, logger, recovery_mode=False):
    """Check if SMA process is already running, kill if needed."""
    logger.info("Checking if SMA process is already running...")
    try:
        # Try to connect to an existing SMA application
        existing_app = Application(backend="uia").connect(path=app_path)
        logger.info("Found existing SMA process")
        
        # Check if recovery mode is enabled
        if recovery_mode:
            # Check if "Dokumente zu verfilmen" window is open
            try:
                verfilmen_window = existing_app.window(title="Verfilmen der Dokumente")
                if verfilmen_window.exists():
                    logger.info("'Verfilmen der Dokumente' window is open. Will attempt recovery.")
                    return False, existing_app, verfilmen_window
            except Exception as e:
                logger.info("'Verfilmen der Dokumente' window is not open. Cannot recover.")
        
        # If not in recovery mode or can't recover, kill the existing process
        logger.info("Killing existing SMA process and starting a new one...")
        existing_app.kill()
        time.sleep(2)  # Wait for the process to fully terminate
    
    except Exception as e:
        logger.info("No existing SMA process found. Starting a new one...")
    
    return True, None, None

def start_application(app_path, logger):
    """Start the application and get handle."""
    logger.info(f"Starting application: {app_path}")
    try:
        app = Application(backend="uia").start(app_path)
        logger.info("Application started")
        return app
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

def find_window(app, title=None, class_name=None, timeout=30, title_re=None, logger=None):
    """Find a window by title or class with timeout."""
    if logger:
        if title:
            logger.info(f"Looking for window with title '{title}'...")
        elif title_re:
            logger.info(f"Looking for window with title regex '{title_re}'...")
        elif class_name:
            logger.info(f"Looking for window with class '{class_name}'...")
    
    start_time = time.time()
    window = None
    
    while time.time() - start_time < timeout:
        try:
            if title:
                window = app.window(title=title)
            elif title_re:
                window = app.window(title_re=title_re)
            elif class_name:
                window = app.window(class_name=class_name)
            
            if window and window.exists():
                if logger:
                    logger.info(f"Window found")
                break
        except Exception as e:
            if logger:
                logger.error(f"Error finding window: {e}")
        
        # Wait a bit before checking again
        time.sleep(1)
    
    if window is None or not window.exists():
        error_msg = "Could not find window"
        if title:
            error_msg += f" with title '{title}'"
        elif title_re:
            error_msg += f" with title regex '{title_re}'"
        elif class_name:
            error_msg += f" with class '{class_name}'"
        error_msg += f" within timeout ({timeout}s)"
        
        if logger:
            logger.error(error_msg)
        
        raise Exception(error_msg)
    
    # Bring the window to front and set focus
    window.set_focus()
    if logger:
        logger.info("Window focus set")
    
    return window

def find_control(window, control_type=None, title=None, auto_id=None, class_name=None, 
                control_id=None, timeout=30, exact=True, logger=None):
    """Find a control in window with timeout."""
    if logger:
        logger.info(f"Looking for control {title or auto_id or class_name or control_id}...")
    
    start_time = time.time()
    control = None
    
    while time.time() - start_time < timeout:
        try:
            # Build criteria dictionary for child_window
            criteria = {}
            if title is not None:
                criteria['title'] = title
            if auto_id is not None:
                criteria['auto_id'] = auto_id
            if control_type is not None:
                criteria['control_type'] = control_type
            if class_name is not None:
                criteria['class_name'] = class_name
                
            # Find the control
            control = window.child_window(**criteria)
            
            # If we need to check by control_id, we need to iterate through children
            if control_id is not None and (control is None or not control.exists()):
                children = window.children()
                for child in children:
                    try:
                        if child.control_id() == control_id:
                            control = child
                            if logger:
                                logger.info(f"Control found by Control ID")
                            break
                    except Exception as e:
                        if logger:
                            logger.error(f"Error checking control ID: {e}")
            
            # Check if we found a valid control
            if control and control.exists():
                if logger:
                    logger.info("Control found")
                break
        except Exception as e:
            if logger:
                logger.error(f"Error finding control: {e}")
        
        # Wait a bit before checking again
        time.sleep(1)
    
    if control is None or not control.exists():
        error_msg = "Could not find control"
        if title:
            error_msg += f" with title '{title}'"
        if auto_id:
            error_msg += f" with auto_id '{auto_id}'"
        if control_type:
            error_msg += f" with control_type '{control_type}'"
        if class_name:
            error_msg += f" with class_name '{class_name}'"
        if control_id:
            error_msg += f" with control_id '{control_id}'"
        error_msg += f" within timeout ({timeout}s)"
        
        if logger:
            logger.error(error_msg)
        
        raise Exception(error_msg)
    
    return control

def wait_for_window(app, title, timeout=30, logger=None):
    """Wait for a window to appear."""
    if logger:
        logger.info(f"Waiting for window with title '{title}' to appear...")
    
    start_time = time.time()
    window = None
    
    while time.time() - start_time < timeout:
        # Get all windows
        all_windows = app.windows()
        
        # Find the window with the specified title
        for win in all_windows:
            try:
                win_title = win.window_text()
                if win_title == title:
                    window = win
                    if logger:
                        logger.info(f"Found window with title '{title}'")
                    break
            except Exception as e:
                if logger:
                    logger.error(f"Error getting window title: {e}")
        
        if window is not None:
            break
        
        # Wait a bit before checking again
        time.sleep(1)
    
    if window is None:
        error_msg = f"Could not find window with title '{title}' within {timeout} seconds"
        if logger:
            logger.error(error_msg)
        raise Exception(error_msg)
    
    # Check if the window is visible
    if window.is_visible():
        if logger:
            logger.info(f"Window is visible")
    else:
        if logger:
            logger.info(f"Window is not visible, waiting for it to become visible...")
        # Wait for the window to become visible (up to timeout seconds)
        visible_start_time = time.time()
        while not window.is_visible() and time.time() - visible_start_time < timeout:
            time.sleep(0.5)
        
        if window.is_visible():
            if logger:
                logger.info(f"Window is now visible")
        else:
            if logger:
                logger.warning(f"Window did not become visible within {timeout} seconds")
    
    # Bring the window to front and set focus
    window.set_focus()
    if logger:
        logger.info("Window focus set")
    
    return window

def click_button(button, logger=None):
    """Set focus and click a button."""
    if logger:
        logger.info(f"Clicking button: {button.window_text()}")
    
    try:
        # Check if the button is enabled
        if button.is_enabled():
            if logger:
                logger.info("Button is enabled")
        else:
            if logger:
                logger.info("Button is not enabled, waiting for it to become enabled...")
            # Wait for the button to become enabled (up to 30 seconds)
            start_time = time.time()
            timeout = 30
            while not button.is_enabled() and time.time() - start_time < timeout:
                time.sleep(0.5)
            
            if button.is_enabled():
                if logger:
                    logger.info("Button is now enabled")
            else:
                if logger:
                    logger.warning(f"Button did not become enabled within {timeout} seconds")
        
        # Set focus and click the button
        button.set_focus()
        button.type_keys('{ENTER}')
        
        if logger:
            logger.info(f"Clicked button")
        
        return True
    except Exception as e:
        if logger:
            logger.error(f"Error clicking button: {e}")
        
        raise Exception(f"Failed to click button: {e}")

def handle_main_screen(app, logger):
    """Handle the main application screen."""
    try:
        # Find the main window
        main_win = find_window(app, title_re="SMA 51.*", timeout=30, logger=logger)
        
        # Find the "Neue Verfilmung" static text control
        newfilm = find_control(
            main_win, 
            title="Neue Verfilmung", 
            auto_id="_Label_2", 
            control_type="Text", 
            timeout=30, 
            logger=logger
        )
        
        # Click on the "Neue Verfilmung" control
        newfilm.click_input()
        logger.info(f"Clicked on 'Neue Verfilmung' control")
        
        return True
    except Exception as e:
        logger.error(f"Error handling main screen: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_data_source_selection(app, template_name, logger):
    """Handle the data source selection dialog."""
    try:
        # Find "Datenquelle auswählen" window
        select_folder = find_window(
            app, 
            title="Datenquelle auswählen", 
            class_name="WindowsForms10.Window.8.app.0.141b42a_r6_ad1", 
            timeout=30, 
            logger=logger
        )
        
        # Select the template from the ComboBox
        try:
            # Find the ComboBox control
            template_combo = find_control(
                select_folder,
                auto_id="cmbTemplate", 
                control_type="ComboBox",
                timeout=30,
                logger=logger
            )
            
            # Select the item by text
            template_combo.select(template_name)
            logger.info(f"Selected template: {template_name}")
        except Exception as e:
            logger.error(f"Error selecting template: {e}")
            logger.info("Continuing anyway, as the default might be acceptable")
        
        # Find the "Neue Rolle beginnen" button
        newroll = find_control(
            select_folder, 
            title="Neue Rolle beginnen", 
            auto_id="cmdNewRoll", 
            control_type="Button", 
            timeout=30, 
            logger=logger
        )
        
        # Click on the "Neue Rolle beginnen" control
        click_button(newroll, logger)
        
        # Wait until the correct main window is visible again
        logger.info("Waiting for the main SMA window to reappear...")
        try:
            # Define the specific window class we're looking for
            main_window_class = "WindowsForms10.Window.8.app.0.141b42a_r6_ad1"
            
            # Wait for the window with the specific class to be visible
            main_win = find_window(app, class_name=main_window_class, timeout=30, logger=logger)
            
            return main_win
        except Exception as e:
            logger.error(f"Error waiting for main window to reappear: {e}")
            
            # Try to print diagnostic information
            try:
                logger.info("Available windows:")
                for i, window in enumerate(app.windows()):
                    try:
                        logger.info(f"Window {i+1}: {window.window_text()} ({window.class_name()})")
                    except:
                        logger.info(f"Window {i+1}: [Could not get window information]")
            except Exception as diag_error:
                logger.error(f"Error getting diagnostic information: {diag_error}")
            
            raise
    
    except Exception as e:
        logger.error(f"Error handling data source selection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_start(main_win, app, logger):
    """Handle the film start process."""
    try:
        # Find the "Verfilmen starten" button
        start_film = find_control(
            main_win,
            title="Verfilmen starten", 
            auto_id="cmdStart", 
            control_type="Button", 
            timeout=30, 
            logger=logger
        )
        
        # Click the "Verfilmen starten" button
        click_button(start_film, logger)
        
        # Wait for the "Film einlegen" window to appear
        film_window_title = "Verfilmen der Dokumente"
        film_window = wait_for_window(
            app=app, 
            title=film_window_title, 
            timeout=30, 
            logger=logger
        )
        
        return film_window
    
    except Exception as e:
        logger.error(f"Error starting film process: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_insert(film_window, logger):
    """Handle the film insert dialog."""
    try:
        # Wait for the "Film einlegen" child window to appear
        logger.info("Waiting for 'Film einlegen' child window to appear...")
        
        # Find the "Film einlegen" window
        film_einlegen_window = None
        timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                children = film_window.children()
                logger.info(f"Found {len(children)} child controls in the window")
                
                for child in children:
                    try:
                        if child.window_text() == "Film einlegen":
                            film_einlegen_window = child
                            logger.info(f"Found 'Film einlegen' child window")
                            break
                    except Exception as e:
                        logger.error(f"Error checking child window: {e}")
                
                if film_einlegen_window is not None:
                    break
                    
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding 'Film einlegen' window: {e}")
                time.sleep(1)
        
        if film_einlegen_window is None:
            raise Exception(f"Could not find 'Film einlegen' child window within {timeout} seconds")
        
        # Wait for the "Start" button to appear
        logger.info("Looking for 'Start' button...")
        start_button = None
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = film_einlegen_window.children()
                logger.info(f"Found {len(grandchildren)} grandchild controls in the 'Film einlegen' window")
                
                for grandchild in grandchildren:
                    try:
                        if grandchild.window_text() == "Start":
                            start_button = grandchild
                            logger.info(f"Found 'Start' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking grandchild control: {e}")
                
                if start_button is not None:
                    break
                    
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding 'Start' button: {e}")
                time.sleep(1)
        
        if start_button is None:
            raise Exception(f"Could not find 'Start' button within {timeout} seconds")
        
        # Click the "Start" button
        click_button(start_button, logger)
        
        return film_window
    
    except Exception as e:
        logger.error(f"Error handling film insert dialog: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_number_entry(app, folder_path, film_window, logger, custom_filmnumber=None):
    """Handle the film number entry dialog."""
    try:
        # Either use the custom film number or extract it from the folder name
        if custom_filmnumber:
            filmnumber = custom_filmnumber
            logger.info(f"Using provided custom film number: {filmnumber}")
        else:
            # Extract the folder name from the selected folder path
            filmnumber = os.path.basename(folder_path)
            logger.info(f"Using folder name as film number: {filmnumber}")
        
        # Wait for the "Filmnummer eingeben" window to appear
        logger.info("Waiting for 'Filmnummer eingeben' window to appear...")
        timeout = 30
        start_time = time.time()
        filmnummer_window = None
        
        while time.time() - start_time < timeout:
            try:
                # Get all windows
                all_windows = app.windows()
                
                # Find the window with the "Filmnummer eingeben" child
                for window in all_windows:
                    try:
                        children = window.children()
                        for child in children:
                            try:
                                if child.window_text() == "Filmnummer eingeben":
                                    filmnummer_window = child
                                    logger.info("'Filmnummer eingeben' window found")
                                    break
                            except Exception as e:
                                logger.error(f"Error checking child window: {e}")
                        
                        if filmnummer_window is not None:
                            break
                    except Exception as e:
                        logger.error(f"Error finding 'Filmnummer eingeben' window: {e}")
                
                if filmnummer_window is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking window: {e}")
                time.sleep(1)
        
        if filmnummer_window is None:
            raise Exception(f"Could not find 'Filmnummer eingeben' window within {timeout} seconds")
        
        # Find the text field in the "Filmnummer eingeben" window
        logger.info("Looking for text field in 'Filmnummer eingeben' window...")
        text_field = None
        
        try:
            # Get all child controls of the "Filmnummer eingeben" window
            grandchildren = filmnummer_window.children()
            logger.info(f"Found {len(grandchildren)} controls in 'Filmnummer eingeben' window")
            
            # Look for the text field with Control ID 6160962
            for control in grandchildren:
                try:
                    if control.control_id() == 6160962:
                        text_field = control
                        logger.info("Text field found by Control ID")
                        break
                except Exception as e:
                    logger.error(f"Error checking control: {e}")
            
            # If not found by Control ID, try by class name
            if text_field is None:
                for control in grandchildren:
                    try:
                        if control.class_name() == "WindowsForms10.EDIT.app.0.141b42a_r6_ad1":
                            text_field = control
                            logger.info("Text field found by class name")
                            break
                    except Exception as e:
                        logger.error(f"Error checking control: {e}")
        except Exception as e:
            logger.error(f"Error finding text field: {e}")
        
        if text_field is None:
            raise Exception("Could not find text field in 'Filmnummer eingeben' window")
        
        # Set focus on the text field
        text_field.set_focus()
        logger.info("Text field focus set")
        
        # Clear the existing text and enter the film number
        text_field.set_text(filmnumber)
        logger.info(f"Entered film number: {filmnumber}")
        
        # Find and click the OK button
        logger.info("Looking for OK button...")
        ok_button = None
        
        try:
            # Look for the OK button
            for control in grandchildren:
                try:
                    if control.window_text() == "OK":
                        ok_button = control
                        logger.info("OK button found")
                        break
                except Exception as e:
                    logger.error(f"Error checking control for OK button: {e}")
        except Exception as e:
            logger.error(f"Error finding OK button: {e}")
        
        if ok_button is None:
            raise Exception("Could not find OK button")
        
        # Click the OK button
        click_button(ok_button, logger)
        
        return filmnumber, film_window
    
    except Exception as e:
        logger.error(f"Error handling film number entry: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def find_progress_controls(film_window, logger):
    """Find progress monitoring controls."""
    try:
        logger.info("Finding static text controls for progress monitoring...")
        zu_verfilmen_control = None
        verfilmt_control = None
        
        try:
            # Get all child controls
            children = film_window.children()
            logger.info(f"Found {len(children)} children in film window")
            
            # Try to find the controls by examining the child controls
            # Based on experimentation, we know:
            # - Child 25 is "zu verfilmen" 
            # - Child 7 is "verfilmt"
            if len(children) >= 26 and len(children) >= 8:
                try:
                    zu_verfilmen_control = children[25]  # Index 25 for "zu verfilmen"
                    verfilmt_control = children[7]  # Index 7 for "verfilmt"
                    
                    logger.info(f"Found 'zu verfilmen' control at index 25: {zu_verfilmen_control.window_text()}")
                    logger.info(f"Found 'verfilmt' control at index 7: {verfilmt_control.window_text()}")
                except Exception as e:
                    logger.error(f"Error accessing controls at indices: {e}")
            
            # If we couldn't find the controls by index, try finding them by examining text
            if zu_verfilmen_control is None or verfilmt_control is None:
                logger.info("Couldn't find controls by index, trying to find by text...")
                
                for i, child in enumerate(children):
                    try:
                        text = child.window_text()
                        
                        # Check if this looks like a number (zu verfilmen or verfilmt count)
                        if text.isdigit():
                            logger.info(f"Found potential control at index {i}: '{text}'")
                            
                            if i > 0:
                                # Check the previous control to see if it has a label
                                prev_control = children[i-1]
                                prev_text = prev_control.window_text().lower()
                                
                                if "verfilmt" in prev_text and verfilmt_control is None:
                                    verfilmt_control = child
                                    logger.info(f"Found 'verfilmt' control by text inspection at index {i}")
                                elif "zu verfilmen" in prev_text and zu_verfilmen_control is None:
                                    zu_verfilmen_control = child
                                    logger.info(f"Found 'zu verfilmen' control by text inspection at index {i}")
                    except Exception as e:
                        logger.error(f"Error checking control at index {i}: {e}")
                
        except Exception as e:
            logger.error(f"Error finding static controls: {e}")
        
        if zu_verfilmen_control is None or verfilmt_control is None:
            logger.warning("Could not find required progress controls")
            if zu_verfilmen_control is None:
                logger.warning("'zu verfilmen' control not found")
            if verfilmt_control is None:
                logger.warning("'verfilmt' control not found")
        
        return zu_verfilmen_control, verfilmt_control
    
    except Exception as e:
        logger.error(f"Error finding progress controls: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None

def calculate_eta(start_time, first_docs, current_docs, total_docs, logger):
    """Calculate estimated time to completion."""
    try:
        elapsed_time = time.time() - start_time
        docs_processed = current_docs - first_docs
        
        if elapsed_time > 0 and docs_processed > 0:
            rate_per_second = docs_processed / elapsed_time
            docs_remaining = total_docs - current_docs
            
            if rate_per_second > 0:
                seconds_remaining = docs_remaining / rate_per_second
                eta = datetime.now() + timedelta(seconds=seconds_remaining)
                
                # Format remaining duration
                hours = int(seconds_remaining // 3600)
                minutes = int((seconds_remaining % 3600) // 60)
                seconds = int(seconds_remaining % 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                return eta, duration_str, rate_per_second
            else:
                return None, None, 0
        else:
            return None, None, 0
    except Exception as e:
        logger.error(f"Error calculating ETA: {e}")
        return None, None, 0

def monitor_progress(film_window, logger):
    """Monitor progress until completion."""
    try:
        # Find the progress monitoring controls
        zu_verfilmen_control, verfilmt_control = find_progress_controls(film_window, logger)
        
        if zu_verfilmen_control is None or verfilmt_control is None:
            logger.error("Could not find progress controls. Unable to monitor progress.")
            return True
        
        logger.info("Starting to monitor progress...")
        
        # Initialize variables
        prev_zu_verfilmen = None
        prev_verfilmt = None
        start_time = time.time()
        first_update_time = None
        first_verfilmt = None
        total_docs = 0
        last_log_time = 0
        min_log_interval = 1.0  # Minimum time between logs in seconds
        last_progress_value = 0  # Track the last progress value
        last_logged_verfilmt = None  # Track the last logged verfilmt value
        process_completed = False  # Flag to track if the process has completed
        progress_bar = None
        
        # Notification variables
        last_notification_percent = 0  # Track last notification percentage for 2% updates
        prep_mode = None  # 'time' or 'percentage' - tracks which PREP mode we're using
        prep_start_time = None  # When PREP mode was triggered
        prep_notifications_sent = {"PREP1": False, "PREP2": False, "PREP3": False}  # Track which PREP notifications sent
        foreground_brought = False  # Flag to track if we've brought the app to foreground at 95%
        
        # Advanced finish system variables
        left_monitor = get_left_monitor()
        monitor2_center = get_monitor_center(left_monitor) if left_monitor else (None, None)
        overlay = RedOverlay(left_monitor) if left_monitor else None
        mouse_locker = MouseLocker()
        overlay_active = False
        mouse_locked = False
        
        try:
            while not process_completed:
                # Get the current values
                try:
                    zu_verfilmen_value = zu_verfilmen_control.window_text() if zu_verfilmen_control is not None else "Not found"
                    verfilmt_value = verfilmt_control.window_text() if verfilmt_control is not None else "Not found"
                    
                    # Process values if they've changed
                    if zu_verfilmen_value != prev_zu_verfilmen or verfilmt_value != prev_verfilmt:
                        # Calculate progress
                        if zu_verfilmen_value.isdigit() and verfilmt_value.isdigit():
                            zu_verfilmen = int(zu_verfilmen_value)
                            verfilmt = int(verfilmt_value)
                            
                            # Check if process is complete
                            if total_docs > 0 and verfilmt >= total_docs and not process_completed:
                                process_completed = True
                                logger.info(f"Process completed: {verfilmt}/{total_docs} frames processed")
                                
                                # Send completion notification
                                if FIREBASE_NOTIF_AVAILABLE:
                                    try:
                                        firebase_notif.send_notification(
                                            "COMPLETED", 
                                            "Film processing completed successfully!", 
                                            "process"
                                        )
                                        logger.info("Sent completion notification")
                                    except Exception as e:
                                        logger.error(f"Error sending completion notification: {e}")
                                
                                break
                            
                            # Skip if we've already logged this exact verfilmt value
                            if verfilmt == last_logged_verfilmt:
                                # Update the previous values but don't log
                                prev_zu_verfilmen = zu_verfilmen_value
                                prev_verfilmt = verfilmt_value
                                time.sleep(0.1)
                                continue
                            
                            total = zu_verfilmen + verfilmt
                            
                            if total > 0:
                                progress_percent = (verfilmt / total) * 100
                                
                                # Initialize progress tracking on first update
                                if total_docs == 0:
                                    total_docs = total
                                    logger.info(f"Total frames to process: {total_docs}")
                                    
                                    # Initialize time prediction variables
                                    first_update_time = time.time()
                                    first_verfilmt = verfilmt
                                    last_progress_value = verfilmt
                                else:
                                    # Calculate and log ETA
                                    if first_update_time is not None and verfilmt != last_logged_verfilmt:
                                        eta, duration_str, rate = calculate_eta(
                                            first_update_time, first_verfilmt, verfilmt, total_docs, logger
                                        )
                                        
                                        # Calculate remaining time in seconds
                                        remaining_seconds = None
                                        if eta:
                                            remaining_seconds = (eta - datetime.now()).total_seconds()
                                        
                                        # Only log if enough time has passed since the last log
                                        current_time = time.time()
                                        if current_time - last_log_time >= min_log_interval:
                                            if eta and duration_str:
                                                logger.info(f"Progress: {progress_percent:.2f}% ({verfilmt}/{total_docs}) - ETA: {eta.strftime('%H:%M:%S')} - Remaining: {duration_str} - Rate: {rate:.2f} docs/sec")
                                            else:
                                                logger.info(f"Progress: {progress_percent:.2f}% ({verfilmt}/{total_docs})")
                                            
                                            last_log_time = current_time
                                            last_logged_verfilmt = verfilmt  # Update the last logged verfilmt value
                                            last_progress_value = verfilmt
                                            
                                            # Advanced finish warning system
                                            remaining_frames = total_docs - verfilmt
                                            
                                            # At 20 frames: Start red overlay
                                            if remaining_frames <= 20 and not overlay_active and overlay:
                                                try:
                                                    logger.info(f"🔴 {remaining_frames} frames remaining - starting red warning overlay")
                                                    overlay.show(remaining_frames=remaining_frames)
                                                    overlay_active = True
                                                except Exception as e:
                                                    logger.error(f"Error starting red overlay: {e}")
                                            
                                            # At 10 frames: Lock mouse to monitor 2 center
                                            elif remaining_frames <= 10 and not mouse_locked and monitor2_center[0] is not None:
                                                try:
                                                    logger.info(f"🖱️  {remaining_frames} frames remaining - locking mouse to monitor 2 center")
                                                    mouse_locker.lock_to_position(monitor2_center[0], monitor2_center[1])
                                                    mouse_locked = True
                                                except Exception as e:
                                                    logger.error(f"Error locking mouse: {e}")
                                            
                                            # At 7 frames: Release mouse lock
                                            elif remaining_frames <= 7 and mouse_locked:
                                                try:
                                                    logger.info(f"🖱️  {remaining_frames} frames remaining - releasing mouse lock")
                                                    mouse_locker.release()
                                                    mouse_locked = False
                                                except Exception as e:
                                                    logger.error(f"Error releasing mouse lock: {e}")
                                            
                                            # At 5 frames: Hide overlay and bring SMA to foreground  
                                            elif remaining_frames <= 5 and not foreground_brought:
                                                try:
                                                    logger.info(f"🖥️  {remaining_frames} frames remaining - hiding overlay and bringing SMA to foreground")
                                                    
                                                    # Hide overlay completely first
                                                    if overlay_active and overlay:
                                                        overlay.hide()
                                                        overlay_active = False
                                                        logger.info("✓ Overlay completely hidden")
                                                    
                                                    # Then bring SMA to foreground (Method 1)
                                                    film_window.set_focus()
                                                    
                                                    try:
                                                        film_window.restore()  # In case it's minimized
                                                        film_window.bring_to_top()  # Bring to top of Z-order
                                                    except Exception as e:
                                                        logger.warning(f"Could not fully bring window to front: {e}")
                                                    
                                                    foreground_brought = True
                                                    logger.info("✓ SMA application brought to foreground")
                                                except Exception as e:
                                                    logger.error(f"Error bringing application to foreground: {e}")
                                            
                                            # Update overlay if it's active
                                            if overlay_active and overlay:
                                                try:
                                                    overlay.update(remaining_frames=remaining_frames)
                                                except Exception as e:
                                                    logger.error(f"Error updating overlay: {e}")
                                            
                                            # Handle notifications if Firebase is available
                                            if FIREBASE_NOTIF_AVAILABLE:
                                                try:
                                                    # Check if we need to trigger PREP mode
                                                    prep_triggered = False
                                                    if prep_mode is None:
                                                        # Check for time trigger (remaining < 3 minutes = 180 seconds)
                                                        if remaining_seconds is not None and remaining_seconds <= 180:
                                                            prep_mode = 'time'
                                                            prep_start_time = current_time
                                                            prep_triggered = True
                                                            logger.info(f"PREP mode triggered by time: {remaining_seconds:.0f} seconds remaining")
                                                        # Check for percentage trigger (90%)
                                                        elif progress_percent >= 90.0:
                                                            prep_mode = 'percentage'
                                                            prep_start_time = current_time
                                                            prep_triggered = True
                                                            logger.info(f"PREP mode triggered by percentage: {progress_percent:.2f}%")
                                                    
                                                    # Handle PREP notifications based on mode
                                                    if prep_mode == 'time':
                                                        elapsed_prep_time = current_time - prep_start_time
                                                        
                                                        # PREP1: immediately (0m)
                                                        if not prep_notifications_sent["PREP1"]:
                                                            firebase_notif.send_notification(
                                                                "PREP1", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP1"] = True
                                                            logger.info("Sent PREP1 notification (time mode - immediate)")
                                                        
                                                        # PREP2: after 1 minute (60 seconds)
                                                        elif elapsed_prep_time >= 60 and not prep_notifications_sent["PREP2"]:
                                                            firebase_notif.send_notification(
                                                                "PREP2", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP2"] = True
                                                            logger.info("Sent PREP2 notification (time mode - after 1 minute)")
                                                        
                                                        # PREP3: after 2 minutes (120 seconds)
                                                        elif elapsed_prep_time >= 120 and not prep_notifications_sent["PREP3"]:
                                                            firebase_notif.send_notification(
                                                                "PREP3", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP3"] = True
                                                            logger.info("Sent PREP3 notification (time mode - after 2 minutes)")
                                                    
                                                    elif prep_mode == 'percentage':
                                                        # PREP1: immediately at 90%
                                                        if progress_percent >= 90.0 and not prep_notifications_sent["PREP1"]:
                                                            firebase_notif.send_notification(
                                                                "PREP1", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP1"] = True
                                                            logger.info(f"Sent PREP1 notification (percentage mode - {progress_percent:.2f}%)")
                                                        
                                                        # PREP2: at 93%
                                                        elif progress_percent >= 93.0 and not prep_notifications_sent["PREP2"]:
                                                            firebase_notif.send_notification(
                                                                "PREP2", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP2"] = True
                                                            logger.info(f"Sent PREP2 notification (percentage mode - {progress_percent:.2f}%)")
                                                        
                                                        # PREP3: at 96%
                                                        elif progress_percent >= 96.0 and not prep_notifications_sent["PREP3"]:
                                                            firebase_notif.send_notification(
                                                                "PREP3", 
                                                                "Process almost done, please prepare", 
                                                                "prep"
                                                            )
                                                            prep_notifications_sent["PREP3"] = True
                                                            logger.info(f"Sent PREP3 notification (percentage mode - {progress_percent:.2f}%)")
                                                    
                                                    # Send regular RUNNING notifications every 2% (continue even during PREP mode)
                                                    # RUNNING notifications use "process" message_id, PREP uses "prep" message_id
                                                    current_notification_percent = int(progress_percent // 2) * 2
                                                    if current_notification_percent > last_notification_percent and current_notification_percent > 0:
                                                        last_notification_percent = current_notification_percent
                                                        remaining_frames = total_docs - verfilmt
                                                        
                                                        eta_str = eta.strftime('%H:%M:%S') if eta else "N/A"
                                                        
                                                        message = f"{progress_percent:.1f}% complete, {remaining_frames} frames remaining, ETA: {eta_str}"
                                                        firebase_notif.send_notification(
                                                            "RUNNING", 
                                                            message, 
                                                            "process"
                                                        )
                                                        logger.info(f"Sent RUNNING notification at {current_notification_percent}%: {message}")
                                                
                                                except Exception as e:
                                                    logger.error(f"Error sending notification: {e}")
                        
                        # Update the previous values
                        prev_zu_verfilmen = zu_verfilmen_value
                        prev_verfilmt = verfilmt_value
                except Exception as e:
                    logger.error(f"Error getting control values: {e}")
                
                # If the process hasn't changed in some time, check if it's actually done
                if time.time() - last_log_time > 60 and last_logged_verfilmt is not None:
                    logger.warning("No progress for 60 seconds. Film process may be stalled or complete.")
                    break
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        except Exception as e:
            logger.error(f"Error during progress monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # Cleanup advanced finish components
            try:
                if overlay_active and overlay:
                    overlay.hide()
                    logger.info("✓ Cleaned up overlay")
                if mouse_locked:
                    mouse_locker.release()
                    logger.info("✓ Cleaned up mouse lock")
            except Exception as e:
                logger.error(f"Error cleaning up advanced finish components: {e}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error in monitor_progress: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def handle_endsymbole_prompt(film_window, app, logger):
    """Handle the Endsymbole prompt."""
    try:
        logger.info("Waiting for Endsymbole prompt...")
        timeout = 30
        start_time = time.time()
        ja_button = None
        sma_title_window = None
        
        # First find the SMA title window
        while time.time() - start_time < timeout:
            try:
                children = film_window.children()
                
                # Look for the SMA title window (usually contains version number)
                for child in children:
                    try:
                        child_text = child.window_text()
                        if "SMA 51" in child_text:
                            sma_title_window = child
                            logger.info(f"Found SMA title window: {child_text}")
                            break
                    except Exception as e:
                        logger.error(f"Error checking child window: {e}")
                
                if sma_title_window is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding SMA title window: {e}")
                time.sleep(1)
        
        if sma_title_window is None:
            logger.warning("Could not find SMA title window within timeout")
            # Try to continue with the film_window
            sma_title_window = film_window
        
        # Now look for the Endsymbole text and 'Ja' button
        start_time = time.time()  # Reset timer
        found_endsymbole_text = False
        endsymbole_text = ""
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = sma_title_window.children()
                
                # Search for Endsymbole text
                if not found_endsymbole_text:
                    for grandchild in grandchildren:
                        try:
                            if grandchild.class_name() == "WindowsForms10.STATIC.app.0.141b42a_r6_ad1":
                                grandchild_text = grandchild.window_text()
                                if "Endsymbole" in grandchild_text:
                                    found_endsymbole_text = True
                                    endsymbole_text = grandchild_text
                                    logger.info(f"Found 'Endsymbole' text: {grandchild_text}")
                                    break
                        except Exception as e:
                            logger.error(f"Error checking for Endsymbole text: {e}")
                
                # Look for the 'Ja' button
                for grandchild in grandchildren:
                    try:
                        if (grandchild.class_name() == "WindowsForms10.BUTTON.app.0.141b42a_r6_ad1" and 
                            grandchild.window_text() == "Ja"):
                            ja_button = grandchild
                            logger.info("Found 'Ja' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking for Ja button: {e}")
                
                if ja_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Endsymbole prompt: {e}")
                time.sleep(1)
        
        if ja_button is None:
            logger.warning("Could not find 'Ja' button for Endsymbole prompt within timeout")
            return False
        
        # Click the 'Ja' button
        click_button(ja_button, logger)
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Endsymbole prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def handle_nachspann_prompt(film_window, app, logger):
    """Handle the Nachspann prompt."""
    try:
        logger.info("Waiting for Nachspann prompt...")
        timeout = 30
        start_time = time.time()
        ja_button = None
        sma_title_window = None
        
        # First find the SMA title window
        while time.time() - start_time < timeout:
            try:
                children = film_window.children()
                
                # Look for the SMA title window (usually contains version number)
                for child in children:
                    try:
                        child_text = child.window_text()
                        if "SMA 51" in child_text:
                            sma_title_window = child
                            logger.info(f"Found SMA title window: {child_text}")
                            break
                    except Exception as e:
                        logger.error(f"Error checking child window: {e}")
                
                if sma_title_window is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding SMA title window: {e}")
                time.sleep(1)
        
        if sma_title_window is None:
            logger.warning("Could not find SMA title window within timeout")
            # Try to continue with the film_window
            sma_title_window = film_window
        
        # Now look for the Nachspann text and 'Ja' button
        start_time = time.time()  # Reset timer
        found_nachspann_text = False
        nachspann_text = ""
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = sma_title_window.children()
                
                # Search for Nachspann text
                if not found_nachspann_text:
                    for grandchild in grandchildren:
                        try:
                            if grandchild.class_name() == "WindowsForms10.STATIC.app.0.141b42a_r6_ad1":
                                grandchild_text = grandchild.window_text()
                                if "Soll ein Nachspann abgefahren werden?" in grandchild_text:
                                    found_nachspann_text = True
                                    nachspann_text = grandchild_text
                                    logger.info(f"Found 'Nachspann' text: {grandchild_text}")
                                    break
                        except Exception as e:
                            logger.error(f"Error checking for Nachspann text: {e}")
                
                # Look for the 'Ja' button
                for grandchild in grandchildren:
                    try:
                        if (grandchild.class_name() == "WindowsForms10.BUTTON.app.0.141b42a_r6_ad1" and 
                            grandchild.window_text() == "Ja"):
                            ja_button = grandchild
                            logger.info("Found 'Ja' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking for Ja button: {e}")
                
                if ja_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Nachspann prompt: {e}")
                time.sleep(1)
        
        if ja_button is None:
            logger.warning("Could not find 'Ja' button for Nachspann prompt within timeout")
            return False
        
        # Click the 'Ja' button
        click_button(ja_button, logger)
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Nachspann prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def wait_for_transport_start(film_window, app, logger):
    """Wait for film transport to start."""
    try:
        logger.info("Waiting for film transport to start...")
        transport_started = False
        transport_window = None
        transport_control = None
        timeout = 60  # 1 minute timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout and not transport_started:
            try:
                # Get all windows
                all_windows = app.windows()
                
                # Check all windows for the transport message
                for window in all_windows:
                    try:
                        # Check the window text
                        window_text = window.window_text()
                        
                        if "Film wird transportiert" in window_text:
                            transport_started = True
                            transport_window = window
                            logger.info(f"Transport started: Found in window '{window_text}'")
                            break
                        
                        # Check all child controls
                        children = window.children()
                        
                        for child in children:
                            try:
                                # Check the child text
                                child_text = child.window_text()
                                
                                if "Film wird transportiert" in child_text:
                                    transport_started = True
                                    transport_window = window
                                    transport_control = child
                                    logger.info(f"Transport started: Found in child '{child_text}'")
                                    break
                                
                                # Check grandchild controls
                                try:
                                    grandchildren = child.children()
                                    
                                    for grandchild in grandchildren:
                                        try:
                                            grandchild_text = grandchild.window_text()
                                            
                                            if "Film wird transportiert" in grandchild_text:
                                                transport_started = True
                                                transport_window = window
                                                transport_control = grandchild
                                                logger.info(f"Transport started: Found in grandchild '{grandchild_text}'")
                                                break
                                        except Exception as e:
                                            pass
                                except Exception as e:
                                    pass
                            except Exception as e:
                                pass
                    except Exception as e:
                        pass
                    
                    if transport_started:
                        break
                
                if transport_started:
                    break
                
                # Wait before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking transport start: {e}")
                time.sleep(1)
        
        if not transport_started:
            logger.warning("Timeout waiting for film transport to start")
            return None, None
        
        return transport_window, transport_control
    
    except Exception as e:
        logger.error(f"Error waiting for transport to start: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None

def wait_for_transport_completion(transport_window, transport_control, app, logger):
    """Wait for film transport to complete."""
    try:
        # Now wait for the "Film wird transportiert" message to disappear
        logger.info("Waiting for film transport to complete...")
        transport_complete = False
        timeout = 300  # 5 minutes timeout
        start_time = time.time()
        
        # If we found a specific control, we can focus on that
        if transport_control is not None:
            logger.info(f"Monitoring specific control for disappearance: '{transport_control.window_text()}'")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Check if the control is still accessible by trying to get its text
                    try:
                        current_text = transport_control.window_text()
                        if "Film wird transportiert" not in current_text:
                            transport_complete = True
                            logger.info(f"Film transport completed! Transport control text changed to: '{current_text}'")
                            break
                    except Exception as e:
                        # If we can't get the text, the control might be gone
                        transport_complete = True
                        logger.info("Film transport completed! Could not access transport control text.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error checking transport control: {e}")
                    time.sleep(1)
        # If we only found the window but not a specific control
        elif transport_window is not None:
            logger.info(f"Monitoring window for transport message disappearance: '{transport_window.window_text()}'")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Check if the window is still accessible by trying to get its text
                    try:
                        current_text = transport_window.window_text()
                        if "Film wird transportiert" not in current_text:
                            transport_complete = True
                            logger.info(f"Film transport completed! Transport window text changed to: '{current_text}'")
                            break
                    except Exception as e:
                        # If we can't get the text, the window might be gone
                        transport_complete = True
                        logger.info("Film transport completed! Could not access transport window text.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error checking transport window: {e}")
                    time.sleep(1)
        # Fallback to checking all windows if we couldn't identify a specific window or control
        else:
            logger.info("No specific transport window or control identified. Checking all windows for message disappearance.")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Get all windows
                    all_windows = app.windows()
                    
                    # Check if the "Film wird transportiert" message is still present
                    transport_message_found = False
                    
                    # Check all windows for the transport message
                    for window in all_windows:
                        try:
                            # Check the window text
                            window_text = window.window_text()
                            
                            if "Film wird transportiert" in window_text:
                                transport_message_found = True
                                logger.info(f"Transport message still present: Found in window '{window_text}'")
                                break
                            
                            # Check all child controls
                            children = window.children()
                            
                            for child in children:
                                try:
                                    # Check the child text
                                    child_text = child.window_text()
                                    
                                    if "Film wird transportiert" in child_text:
                                        transport_message_found = True
                                        logger.info(f"Transport message still present: Found in child '{child_text}'")
                                        break
                                    
                                    # Check grandchild controls
                                    try:
                                        grandchildren = child.children()
                                        
                                        for grandchild in grandchildren:
                                            try:
                                                grandchild_text = grandchild.window_text()
                                                
                                                if "Film wird transportiert" in grandchild_text:
                                                    transport_message_found = True
                                                    logger.info(f"Transport message still present: Found in grandchild '{grandchild_text}'")
                                                    break
                                            except Exception as e:
                                                pass
                                    except Exception as e:
                                        pass
                                except Exception as e:
                                    pass
                        except Exception as e:
                            pass
                        
                        if transport_message_found:
                            break
                    
                    # If the message is not found, transport is complete
                    if not transport_message_found:
                        transport_complete = True
                        logger.info("Film transport completed! No transport message found in any window.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Error checking transport status: {e}")
                    time.sleep(2)
        
        if not transport_complete:
            logger.warning("Timeout waiting for film transport to complete")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error waiting for transport completion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_log_file(parent_folder, film_number, logger):
    """Check if log file exists from the film application."""
    film_log_path = os.path.join(parent_folder, '.filmlogs', f"{film_number}.txt")
    
    if os.path.exists(film_log_path):
        logger.info(f"Film application log file exists: {film_log_path}")
        
        # Try to open the file to check its contents
        try:
            with open(film_log_path, 'r', encoding='cp1252') as log_file:
                contents = log_file.read()
                logger.info(f"Log file size: {len(contents)} bytes")
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
        
        return True, film_log_path
    else:
        logger.error(f"Film application log file does not exist: {film_log_path}")
        return False, film_log_path

def cleanup_and_exit(app, logger):
    """Clean up and close application."""
    try:
        logger.info("Cleaning up and closing the application...")
        
        # Ensure mouse lock is released if active
        if LOCK_MOUSE_AVAILABLE:
            try:
                logger.info("Ensuring mouse lock is released...")
                lock_mouse.stop_mouse_lock()
            except Exception as e:
                logger.error(f"Error releasing mouse lock during cleanup: {e}")
        
        time.sleep(5)  # Give some time before closing
        app.kill()
        logger.info("Application closed")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up: {e}")
        return False

def main(args=None):
    """Main function."""
    # Parse command line arguments if args not provided
    if args is None:
        args = parse_arguments()
    
    # Set up logging
    logger = setup_logging()
    
    # Start mouse lock at the beginning of the process if available
    if LOCK_MOUSE_AVAILABLE:
        logger.info("Activating mouse lock for the entire SMA process...")
        lock_mouse.start_mouse_lock()
    
    # Load configuration
    config = load_configuration(args)
    
    # Create log directory
    filmlogs_dir, parent_folder = create_log_directory(config['folder_path'], logger)
    
    # Update template file
    tpl_file_path = os.path.join(config['templates_dir'], config['template_name'])
    update_template_file(tpl_file_path, filmlogs_dir, config['template_name'], logger)
    
    # Update INI file
    update_ini_file(config['ini_file_path'], config['folder_path'], logger)
    
    app = None  # Initialize app variable
    film_window = None  # Initialize film_window variable
    filmnumber = None  # Initialize filmnumber variable
    
    # Recovery mode variables
    recovery_mode = args.recovery
    recovered = False
    
    try:
        # Check for running instance, with recovery mode if requested
        start_new, existing_app, existing_window = check_running_instance(config['app_path'], logger, recovery_mode)
        
        if start_new:
            # Normal flow - start from beginning
            logger.info("Starting new scanning session...")
            
            # Start application
            app = start_application(config['app_path'], logger)
            
            # Handle main screen
            handle_main_screen(app, logger)
            
            # Handle data source selection
            main_win = handle_data_source_selection(app, config['template_name'], logger)
            
            # Start the film process
            film_window = handle_film_start(main_win, app, logger)
            
            # Handle film insert
            film_window = handle_film_insert(film_window, logger)
            
            # Handle film number entry
            filmnumber, film_window = handle_film_number_entry(app, config['folder_path'], film_window, logger, args.filmnumber)
        else:
            # Recovery flow - continue from existing session
            logger.info("Attempting to recover existing scanning session...")
            app = existing_app
            film_window = existing_window
            
            # Try to recover the session
            recovered, recovered_filmnumber = recover_session(app, film_window, logger)
            
            if recovered:
                logger.info("Successfully recovered scanning session!")
                if recovered_filmnumber:
                    filmnumber = recovered_filmnumber
                elif args.filmnumber:
                    filmnumber = args.filmnumber
                    logger.info(f"Using provided film number for recovered session: {filmnumber}")
                else:
                    # If we couldn't recover the film number, use the folder name
                    filmnumber = os.path.basename(config['folder_path'])
                    logger.info(f"Using folder name as film number for recovered session: {filmnumber}")
            else:
                logger.error("Failed to recover session. Starting new session instead.")
                # Cleanup
                if app:
                    try:
                        app.kill()
                        time.sleep(2)
                    except:
                        pass
                
                # Start application
                app = start_application(config['app_path'], logger)
                
                # Handle main screen
                handle_main_screen(app, logger)
                
                # Handle data source selection
                main_win = handle_data_source_selection(app, config['template_name'], logger)
                
                # Start the film process
                film_window = handle_film_start(main_win, app, logger)
                
                # Handle film insert
                film_window = handle_film_insert(film_window, logger)
                
                # Handle film number entry
                filmnumber, film_window = handle_film_number_entry(app, config['folder_path'], film_window, logger, args.filmnumber)
        
        # From here on, the flow is the same for both normal and recovery mode
        
        # Monitor progress
        monitor_progress(film_window, logger)
        
        # Handle end symbols prompt
        handle_endsymbole_prompt(film_window, app, logger)
        
        # Handle nachspann prompt
        handle_nachspann_prompt(film_window, app, logger)
        
        # Wait for film transport to start
        transport_window, transport_control = wait_for_transport_start(film_window, app, logger)
        
        # Wait for film transport to complete
        wait_for_transport_completion(transport_window, transport_control, app, logger)
        
        # Check log file
        log_exists, log_path = check_log_file(parent_folder, filmnumber, logger)
        if log_exists:
            # Open the log file folder in explorer
            subprocess.run(['explorer', os.path.dirname(log_path)])
        
        # Clean up and close
        cleanup_and_exit(app, logger)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Try to close the application
        if app:
            try:
                app.kill()
                logger.info("Application closed due to error")
            except:
                pass
        
        # Ensure mouse lock is released in case of error
        if LOCK_MOUSE_AVAILABLE:
            try:
                logger.info("Releasing mouse lock due to error...")
                lock_mouse.stop_mouse_lock()
            except Exception as release_error:
                logger.error(f"Error releasing mouse lock: {release_error}")
        
        sys.exit(1)
    
    # Release mouse lock at the end of successful execution
    if LOCK_MOUSE_AVAILABLE:
        logger.info("Releasing mouse lock - SMA process completed successfully...")
        lock_mouse.stop_mouse_lock()
    
    logger.info("Script completed successfully")

if __name__ == "__main__":
    main(args=None) 