"""
UI Automation Core Module for SMA (film scanning) automation system.

This module contains the most critical and brittle parts of the SMA automation:
- Window and control finding with pywinauto
- Button clicking and control interaction
- Process management and application lifecycle
- Session recovery and connection management

CRITICAL: This module requires exact timing and behavior preservation.
Any changes to timing or interaction sequences could break the automation.
"""

import time
import sys
from pywinauto import Application
from .sma_exceptions import (
    SMAProcessNotFoundError, SMAWindowNotFoundError, SMAControlNotFoundError,
    SMAButtonClickError, SMATimeoutError, SMARecoveryError
)

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
        
        raise SMAWindowNotFoundError(
            window_title=title or title_re or class_name,
            message=error_msg
        )
    
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
        
        raise SMAControlNotFoundError(
            control_name=title or auto_id or class_name or str(control_id),
            message=error_msg
        )
    
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
        raise SMATimeoutError(
            operation=f"wait_for_window({title})",
            timeout_duration=timeout,
            message=error_msg
        )
    
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
        
        raise SMAButtonClickError(
            button_name=button.window_text() if hasattr(button, 'window_text') else "unknown",
            message=f"Failed to click button: {str(e)}"
        )

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

def cleanup_and_exit(app, logger):
    """Clean up and close application."""
    try:
        logger.info("Cleaning up and closing the application...")
        
        # Ensure mouse lock is released if active (import dynamically)
        try:
            import pathlib
            import importlib.util
            lock_mouse_spec = importlib.util.spec_from_file_location(
                "lock_mouse", 
                pathlib.Path(__file__).parent.parent / "lock_mouse.py"
            )
            if lock_mouse_spec:
                lock_mouse = importlib.util.module_from_spec(lock_mouse_spec)
                lock_mouse_spec.loader.exec_module(lock_mouse)
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

# Utility functions for safe control access
def safe_get_window_text(control, default=""):
    """Safely get window text from a control."""
    try:
        return control.window_text()
    except Exception:
        return default

def safe_get_control_id(control, default=None):
    """Safely get control ID."""
    try:
        return control.control_id()
    except Exception:
        return default

def safe_control_exists(control):
    """Safely check if control exists."""
    try:
        return control.exists()
    except Exception:
        return False

def safe_control_enabled(control):
    """Safely check if control is enabled."""
    try:
        return control.is_enabled()
    except Exception:
        return False

def safe_control_visible(control):
    """Safely check if control is visible."""
    try:
        return control.is_visible()
    except Exception:
        return False

def enumerate_window_children(window, logger=None):
    """Enumerate all children of a window for debugging."""
    try:
        children = window.children()
        if logger:
            logger.info(f"Window has {len(children)} children:")
            for i, child in enumerate(children):
                try:
                    text = child.window_text()
                    class_name = child.class_name()
                    control_id = safe_get_control_id(child)
                    logger.info(f"  Child {i}: '{text}' (class: {class_name}, id: {control_id})")
                except Exception as e:
                    logger.info(f"  Child {i}: [Error getting info: {e}]")
        return children
    except Exception as e:
        if logger:
            logger.error(f"Error enumerating children: {e}")
        return []

def wait_for_condition(condition_func, timeout=30, check_interval=0.5, logger=None):
    """Wait for a condition to become true."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception as e:
            if logger:
                logger.debug(f"Condition check failed: {e}")
        time.sleep(check_interval)
    
    if logger:
        logger.warning(f"Condition not met within {timeout} seconds")
    return False

def retry_ui_operation(operation_func, max_retries=3, delay=1, logger=None):
    """Retry a UI operation multiple times."""
    for attempt in range(max_retries):
        try:
            return operation_func()
        except Exception as e:
            if attempt == max_retries - 1:
                if logger:
                    logger.error(f"UI operation failed after {max_retries} attempts: {e}")
                raise
            if logger:
                logger.warning(f"UI operation attempt {attempt + 1} failed: {e}, retrying...")
            time.sleep(delay)
    return None 