"""
Utility Functions and Helpers Module for SMA (film scanning) automation system.

This module contains shared utilities, constants, and helper functions
used throughout the SMA automation system.
"""

import time
import enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from .logger import get_logger, LogLevel
import os
import subprocess
from .sma_exceptions import SMAException


# Constants
class SMAConstants:
    """Constants used throughout the SMA system."""
    
    # Default timeouts (seconds)
    DEFAULT_WINDOW_TIMEOUT = 30
    DEFAULT_CONTROL_TIMEOUT = 30
    DEFAULT_BUTTON_TIMEOUT = 30
    TRANSPORT_TIMEOUT = 300  # 5 minutes
    
    # Progress monitoring
    MIN_LOG_INTERVAL = 1.0  # Minimum seconds between progress logs
    NOTIFICATION_INTERVAL_PERCENT = 2  # Send notifications every 2%
    
    # Advanced finish system thresholds (frames remaining)
    OVERLAY_START_FRAMES = 20
    MOUSE_LOCK_FRAMES = 10
    MOUSE_RELEASE_FRAMES = 7
    FOREGROUND_FRAMES = 5
    
    # Overlay settings
    OVERLAY_TARGET_OPACITY = 0.75  # 75%
    OVERLAY_FADE_DURATION = 5.0  # 5 seconds
    
    # Mouse lock settings
    MOUSE_LOCK_CHECK_INTERVAL = 0.05  # 50ms
    MOUSE_POSITION_TOLERANCE = 5  # pixels
    
    # PREP notification modes
    PREP_TIME_THRESHOLD = 180  # 3 minutes in seconds
    PREP_PERCENTAGE_THRESHOLD = 90.0  # 90%
    
    # Template mappings
    TEMPLATE_MAP = {
        '16': "16mm.TPL",
        '35': "35mm.TPL"
    }
    
    # Default file paths
    DEFAULT_INI_PATH = r"Y:\SMA\file-converter-64\docufileuc.ini"
    DEFAULT_APP_PATH = r"Y:\SMA\file-converter-64\file-sma.exe"
    DEFAULT_TEMPLATES_DIR = r"Y:\SMA\file-converter-64\TEMPLATES"


class SMAStates(enum.Enum):
    """Enumeration of SMA process states."""
    INITIALIZING = "initializing"
    CONFIGURING = "configuring"
    STARTING_APP = "starting_app"
    HANDLING_MAIN_SCREEN = "handling_main_screen"
    SELECTING_DATA_SOURCE = "selecting_data_source"
    STARTING_FILM = "starting_film"
    INSERTING_FILM = "inserting_film"
    ENTERING_FILM_NUMBER = "entering_film_number"
    MONITORING_PROGRESS = "monitoring_progress"
    HANDLING_END_PROMPTS = "handling_end_prompts"
    WAITING_TRANSPORT = "waiting_transport"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    ERROR = "error"


class NotificationTypes(enum.Enum):
    """Enumeration of notification types."""
    PREP1 = "PREP1"
    PREP2 = "PREP2"
    PREP3 = "PREP3"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AdvancedFinishStages(enum.Enum):
    """Enumeration of advanced finish system stages."""
    IDLE = "idle"
    OVERLAY_ACTIVE = "overlay_active"
    MOUSE_LOCKED = "mouse_locked"
    MOUSE_RELEASED = "mouse_released"
    FOREGROUND_BROUGHT = "foreground_brought"
    CLEANUP = "cleanup"


# Utility Functions

def get_current_timestamp() -> str:
    """
    Get current timestamp in a standard format.
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def calculate_progress_percentage(current: int, total: int) -> float:
    """
    Calculate progress percentage.
    
    Args:
        current: Current progress value
        total: Total value
        
    Returns:
        float: Progress percentage (0.0 to 100.0)
    """
    if total <= 0:
        return 0.0
    return min(100.0, max(0.0, (current / total) * 100.0))


def calculate_eta(start_time: float, first_count: int, current_count: int, 
                 total_count: int) -> Tuple[Optional[datetime], Optional[str], float]:
    """
    Calculate estimated time to completion.
    
    Args:
        start_time: Process start time (timestamp)
        first_count: Initial count when timing started
        current_count: Current count
        total_count: Total expected count
        
    Returns:
        Tuple[Optional[datetime], Optional[str], float]: 
            (eta_datetime, duration_string, rate_per_second)
    """
    try:
        elapsed_time = time.time() - start_time
        items_processed = current_count - first_count
        
        if elapsed_time > 0 and items_processed > 0:
            rate_per_second = items_processed / elapsed_time
            items_remaining = total_count - current_count
            
            if rate_per_second > 0:
                seconds_remaining = items_remaining / rate_per_second
                eta = datetime.now() + timedelta(seconds=seconds_remaining)
                duration_str = format_duration(seconds_remaining)
                
                return eta, duration_str, rate_per_second
        
        return None, None, 0.0
        
    except Exception:
        return None, None, 0.0


def safe_get_window_text(window) -> str:
    """
    Safely get window text with error handling.
    
    Args:
        window: Window object
        
    Returns:
        str: Window text or error description
    """
    try:
        return window.window_text()
    except Exception as e:
        return f"<Error getting text: {e}>"


def safe_get_control_text(control) -> str:
    """
    Safely get control text with error handling.
    
    Args:
        control: Control object
        
    Returns:
        str: Control text or error description
    """
    try:
        return control.window_text()
    except Exception as e:
        return f"<Error getting text: {e}>"


def is_valid_film_number(film_number: str) -> bool:
    """
    Validate film number format.
    
    Args:
        film_number: Film number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not film_number or not isinstance(film_number, str):
        return False
    
    # Remove whitespace
    film_number = film_number.strip()
    
    # Check if not empty after trimming
    if not film_number:
        return False
    
    # Basic validation - no control characters
    if any(ord(c) < 32 for c in film_number):
        return False
    
    return True


def sanitize_film_number(film_number: str) -> str:
    """
    Sanitize film number for safe use.
    
    Args:
        film_number: Film number to sanitize
        
    Returns:
        str: Sanitized film number
    """
    if not film_number:
        return ""
    
    # Remove whitespace and control characters
    sanitized = ''.join(c for c in film_number if ord(c) >= 32)
    return sanitized.strip()


class PerformanceTimerOld:
    """Simple performance timer for measuring operation durations (deprecated - use context manager version)."""
    
    def __init__(self, operation_name: str = "Operation"):
        """
        Initialize performance timer.
        
        Args:
            operation_name: Name of operation being timed
        """
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.logger = get_logger(name="PerformanceTimer", log_level=LogLevel.DEBUG.value)
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.logger.debug(f"Started timing: {self.operation_name}")
    
    def stop(self):
        """Stop the timer and log duration."""
        self.end_time = time.time()
        if self.start_time:
            duration = self.end_time - self.start_time
            self.logger.debug(f"Completed {self.operation_name} in {duration:.2f} seconds")
            return duration
        return 0.0
    
    def get_duration(self) -> float:
        """Get current duration (whether stopped or not)."""
        if self.start_time:
            end_time = self.end_time or time.time()
            return end_time - self.start_time
        return 0.0


class StateTracker:
    """Track SMA process state and transitions."""
    
    def __init__(self):
        """Initialize state tracker."""
        self.current_state = SMAStates.INITIALIZING
        self.state_history = []
        self.state_start_time = time.time()
        self.logger = get_logger(name="StateTracker", log_level=LogLevel.DEBUG.value)
    
    def transition_to(self, new_state: SMAStates, details: str = ""):
        """
        Transition to a new state.
        
        Args:
            new_state: New state to transition to
            details: Optional details about the transition
        """
        old_state = self.current_state
        old_duration = time.time() - self.state_start_time
        
        # Record state history
        self.state_history.append({
            'state': old_state,
            'duration': old_duration,
            'timestamp': datetime.now()
        })
        
        # Update to new state
        self.current_state = new_state
        self.state_start_time = time.time()
        
        # Log transition
        log_msg = f"State transition: {old_state.value} -> {new_state.value} (was {old_duration:.1f}s)"
        if details:
            log_msg += f" - {details}"
        self.logger.info(log_msg)
    
    def get_current_state(self) -> SMAStates:
        """Get current state."""
        return self.current_state
    
    def get_state_duration(self) -> float:
        """Get duration in current state."""
        return time.time() - self.state_start_time
    
    def get_total_duration(self) -> float:
        """Get total process duration."""
        total = sum(entry['duration'] for entry in self.state_history)
        total += self.get_state_duration()  # Add current state duration
        return total
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of state transitions."""
        summary = {
            'current_state': self.current_state.value,
            'current_duration': self.get_state_duration(),
            'total_duration': self.get_total_duration(),
            'state_count': len(self.state_history) + 1,
            'history': [
                {
                    'state': entry['state'].value,
                    'duration': entry['duration'],
                    'timestamp': entry['timestamp'].isoformat()
                }
                for entry in self.state_history
            ]
        }
        return summary


def retry_operation_advanced(operation, max_retries: int = 3, delay: float = 1.0, 
                   logger: Optional[Any] = None):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        logger: Logger instance for debugging
        
    Returns:
        Result of the operation
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                if logger:
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                                 f"retrying in {wait_time:.1f}s: {e}")
                time.sleep(wait_time)
            else:
                if logger:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
    
    raise last_exception


# Logging helpers

def log_system_info_detailed(logger):
    """Log system information for debugging."""
    import platform
    import sys
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Machine: {platform.machine()}")
    logger.info(f"Processor: {platform.processor()}")


def log_dependency_status(logger):
    """Log status of optional dependencies."""
    dependencies = [
        ('tkinter', 'Red overlay functionality'),
        ('screeninfo', 'Multi-monitor detection'),
        ('pyautogui', 'Mouse control'),
        ('pywinauto', 'UI automation (required)'),
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            logger.info(f"✓ {module_name}: Available - {description}")
        except ImportError:
            logger.warning(f"✗ {module_name}: Not available - {description}")


# File and path utilities

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        bool: True if directory exists/was created, False otherwise
    """
    try:
        import os
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except Exception:
        return False


def safe_file_operation(operation, *args, **kwargs):
    """
    Safely perform a file operation with error handling.
    
    Args:
        operation: File operation function
        *args: Arguments for the operation
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Tuple[bool, Any, str]: (success, result, error_message)
    """
    try:
        result = operation(*args, **kwargs)
        return True, result, ""
    except Exception as e:
        return False, None, str(e) 


def calculate_eta_legacy(start_time, first_docs, current_docs, total_docs, logger):
    """Calculate estimated time to completion (legacy version for backward compatibility)."""
    try:
        # Call the main calculate_eta function with the correct signature
        eta, duration_str, rate = calculate_eta(start_time, first_docs, current_docs, total_docs)
        return eta, duration_str, rate
    except Exception as e:
        logger.error(f"Error calculating ETA: {e}")
        return None, None, 0


def setup_logging():
    """Configure and return a logger."""
    from .logger import get_logger, LogLevel
    return get_logger(name="FileConverter", log_level=LogLevel.DEBUG.value)


def open_log_file_folder(log_path):
    """Open the log file folder in Windows Explorer."""
    try:
        log_dir = os.path.dirname(log_path)
        subprocess.run(['explorer', log_dir])
        return True
    except Exception as e:
        print(f"Error opening log folder: {e}")
        return False


def format_progress_percent(verfilmt, total):
    """Format progress percentage for display."""
    if total > 0:
        return (verfilmt / total) * 100
    return 0.0


def format_time_remaining(seconds_remaining):
    """Format remaining time as HH:MM:SS string."""
    if seconds_remaining is None or seconds_remaining < 0:
        return "N/A"
    
    hours = int(seconds_remaining // 3600)
    minutes = int((seconds_remaining % 3600) // 60)
    seconds = int(seconds_remaining % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_eta_time(eta):
    """Format ETA time for display."""
    if eta is None:
        return "N/A"
    return eta.strftime('%H:%M:%S')


def validate_frame_count(frames_text):
    """Validate and convert frame count text to integer."""
    try:
        if isinstance(frames_text, str) and frames_text.isdigit():
            return int(frames_text)
        elif isinstance(frames_text, int):
            return frames_text
        else:
            return None
    except (ValueError, TypeError):
        return None


def safe_get_window_text(control, default=""):
    """Safely get window text from a control, returning default if it fails."""
    try:
        return control.window_text()
    except Exception:
        return default


def safe_get_control_value(control, default=None):
    """Safely get value from a control, returning default if it fails."""
    try:
        return control.window_text()
    except Exception:
        return default


def is_numeric_string(text):
    """Check if a string represents a number."""
    try:
        if isinstance(text, str):
            return text.isdigit()
        return False
    except Exception:
        return False


def get_folder_name_from_path(folder_path):
    """Extract folder name from a full path."""
    try:
        return os.path.basename(folder_path)
    except Exception:
        return "unknown"


def check_file_exists(file_path):
    """Check if a file exists at the given path."""
    try:
        return os.path.exists(file_path) and os.path.isfile(file_path)
    except Exception:
        return False


def check_directory_exists(dir_path):
    """Check if a directory exists at the given path."""
    try:
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
    except Exception:
        return False


def create_directory_if_not_exists(dir_path):
    """Create a directory if it doesn't exist."""
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            return True
        return True
    except Exception:
        return False


def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception:
        return 0


def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    except Exception:
        return "Unknown"


def timestamp_string():
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def elapsed_time_string(start_time):
    """Get elapsed time since start_time as formatted string."""
    try:
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except Exception:
        return "00:00:00"


def rate_per_minute(docs_processed, elapsed_seconds):
    """Calculate processing rate per minute."""
    try:
        if elapsed_seconds > 0:
            rate_per_second = docs_processed / elapsed_seconds
            return rate_per_second * 60
        return 0
    except Exception:
        return 0


def remaining_time_in_seconds(total_docs, current_docs, rate_per_second):
    """Calculate remaining time in seconds based on current rate."""
    try:
        if rate_per_second > 0:
            docs_remaining = total_docs - current_docs
            return docs_remaining / rate_per_second
        return None
    except Exception:
        return None


def should_send_notification(current_percent, last_percent, interval=2):
    """Check if a notification should be sent based on percentage interval."""
    try:
        current_notification_percent = int(current_percent // interval) * interval
        last_notification_percent = int(last_percent // interval) * interval
        return current_notification_percent > last_notification_percent and current_notification_percent > 0
    except Exception:
        return False


def format_notification_message(progress_percent, remaining_frames, eta_str):
    """Format a progress notification message."""
    return f"{progress_percent:.1f}% complete, {remaining_frames} frames remaining, ETA: {eta_str}"


def safe_int_conversion(value, default=0):
    """Safely convert a value to integer."""
    try:
        if isinstance(value, str) and value.isdigit():
            return int(value)
        elif isinstance(value, (int, float)):
            return int(value)
        else:
            return default
    except (ValueError, TypeError):
        return default


def safe_float_conversion(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def clamp_value(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))


def wait_with_timeout(condition_func, timeout_seconds=30, check_interval=0.1):
    """Wait for a condition to be true with timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if condition_func():
            return True
        time.sleep(check_interval)
    return False


def retry_operation(operation_func, max_retries=3, delay_between_retries=1):
    """Retry an operation up to max_retries times."""
    for attempt in range(max_retries):
        try:
            return operation_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay_between_retries)
    return None


def log_system_info(logger):
    """Log basic system information."""
    try:
        import platform
        logger.info(f"System: {platform.system()} {platform.release()}")
        logger.info(f"Python: {platform.python_version()}")
        logger.info(f"Current working directory: {os.getcwd()}")
    except Exception as e:
        logger.warning(f"Could not log system info: {e}")


def normalize_path(path):
    """Normalize a file path for the current OS."""
    try:
        return os.path.normpath(path)
    except Exception:
        return path


def get_relative_path(path, base_path):
    """Get relative path from base_path."""
    try:
        return os.path.relpath(path, base_path)
    except Exception:
        return path


def ensure_path_exists(path):
    """Ensure all directories in the path exist."""
    try:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return True
    except Exception:
        return False


class PerformanceTimer:
    """Simple performance timer context manager."""
    
    def __init__(self, operation_name="Operation", logger=None):
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        if self.logger:
            self.logger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        if self.logger:
            if exc_type is None:
                self.logger.debug(f"Completed {self.operation_name} in {elapsed:.2f} seconds")
            else:
                self.logger.error(f"Failed {self.operation_name} after {elapsed:.2f} seconds")
    
    def elapsed(self):
        """Get elapsed time."""
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time


class LogContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context
        self.original_name = logger.name
    
    def __enter__(self):
        self.logger.name = f"{self.original_name}[{self.context}]"
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.name = self.original_name


def with_log_context(logger, context):
    """Create a log context manager."""
    return LogContext(logger, context) 