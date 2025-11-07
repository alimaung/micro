"""
Centralized logging module for the Pagify application.

This module provides consistent, colorful logging functionality across all modules
with file and line information included in log messages.
"""

import logging
import os
import sys
import time
import shutil
from typing import Optional, Union, Dict, Any, Tuple, List
import colorama
from datetime import datetime
from enum import Enum

# Try to import tqdm, with fallback if not available
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Initialize colorama for cross-platform colored terminal output
colorama.init()

# Color definitions for different log levels
COLORS = {
    'DEBUG': colorama.Fore.CYAN,
    'INFO': colorama.Fore.GREEN,
    'WARNING': colorama.Fore.YELLOW,
    'ERROR': colorama.Fore.RED,
    'CRITICAL': colorama.Style.BRIGHT + colorama.Fore.RED,
    'RESET': colorama.Style.RESET_ALL
}

class LogLevel(Enum):
    """Custom log levels for film processing pipeline"""
    DEBUG = 10      # Detailed debugging information
    INFO = 15       # General information
    MAIN = 20       # Main information
    SUCCESS = 25    # Successful operations
    PROJECT = 30    # Project-related information 
    DOCUMENT = 35   # Document-related information
    FILM = 40       # Film roll operations
    ALLOCATION = 45 # Allocation decisions
    WARNING = 50    # Warnings
    ERROR = 60      # Errors
    CRITICAL = 70   # Critical failures

class ColorCode:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_ORANGE = "\033[48;5;208m"
    
    # Bright background colors
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log messages with file and line information."""
    
    def format(self, record):
        # Get the original format
        format_orig = self._style._fmt
        
        # Add colors based on log level
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname_colored = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        else:
            record.levelname_colored = levelname
            
        # Add file and line information
        record.filepath = f"{os.path.basename(record.pathname)}:{record.lineno}"
        
        # Format the message
        result = super().format(record)
        
        # Restore the original format for next time
        self._style._fmt = format_orig
        
        return result

class TqdmLoggingHandler(logging.Handler):
    """Handler for logging that's compatible with tqdm progress bars."""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except ImportError:
            # If tqdm isn't available, fall back to print
            print(self.format(record))
        except Exception:
            self.handleError(record)

def setup_logger(name: Optional[str] = None, 
                log_level: int = logging.INFO, 
                log_file: Optional[str] = None,
                console: bool = True) -> logging.Logger:
    """
    Set up and return a logger with the specified configuration.
    
    Args:
        name: Logger name (usually __name__ from the calling module)
        log_level: Logging level (default: INFO)
        log_file: Optional file path to also log to a file
        console: Whether to include console output (default: True)
        
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name or 'pagify')
    
    # Only configure if it hasn't been set up or has no handlers
    if not logger.handlers:
        logger.setLevel(log_level)
        
        # Create console handler with custom formatter if enabled
        if console:
            console_handler = TqdmLoggingHandler()
            console_handler.setLevel(log_level)
            
            # Create formatter for console output with colored levelname
            console_formatter = ColoredFormatter(
                '%(asctime)s | %(levelname_colored)s | %(filepath)s | %(message)s',
                datefmt='%y%m%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # Create file handler if log_file is specified
        if log_file:
            try:
                # Create directory for log file if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                    
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(log_level)
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)d | %(message)s',
                    datefmt='%y%m%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                # If we can't create the file handler, at least log the error
                # to the console handler if it exists
                if console:
                    logger.error(f"Failed to create log file '{log_file}': {e}")
    
    return logger

def get_logger(name="FilmLogger", log_level=logging.INFO, log_to_file=True, parent_folder=None):
    """
    Creates and returns a FilmLogger instance with the specified settings.
    
    Args:
        name: Name of the logger
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to a file (default: True)
        parent_folder: Optional parent folder path for log files
        
    Returns:
        FilmLogger: Configured logger instance
    """
    logger = FilmLogger(name, log_level, log_to_file, parent_folder)
    return logger

class FilmLogger:
    """
    A logger class for film processing operations.
    """
    
    def __init__(self, name, log_level=logging.INFO, log_to_file=True, parent_folder=None):
        """
        Initialize the FilmLogger.
        
        Args:
            name: Name of the logger
            log_level: Logging level (default: logging.INFO)
            log_to_file: Whether to log to a file (default: True)
            parent_folder: Parent folder path for log files (default: None)
        """
        self.name = name
        self.log_level = log_level
        self.log_to_file = log_to_file
        self.parent_folder = parent_folder
        self.log_file = None
        self.handlers = []
        
        # Configure logging
        logging.basicConfig(level=log_level)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        self.handlers.append(console_handler.stream)  # Append the stream, not the handler
        
        # Set up file logging if enabled and parent_folder is provided
        if log_to_file and parent_folder:
            self.save_log_file()
        
        # Map log levels to styles - without emojis
        self.level_styles = {
            LogLevel.DEBUG.value: {"prefix": "DEBUG", "color": ColorCode.CYAN},
            LogLevel.MAIN.value: {"prefix": "MAIN", "color": ColorCode.BRIGHT_WHITE},
            LogLevel.INFO.value: {"prefix": "INFO", "color": ColorCode.GREEN},
            LogLevel.SUCCESS.value: {"prefix": "SUCCESS", "color": ColorCode.BRIGHT_GREEN},
            LogLevel.PROJECT.value: {"prefix": "PROJECT", "color": ColorCode.BLUE},
            LogLevel.DOCUMENT.value: {"prefix": "DOCUMENT", "color": ColorCode.BRIGHT_BLUE},
            LogLevel.FILM.value: {"prefix": "FILM", "color": ColorCode.MAGENTA},
            LogLevel.ALLOCATION.value: {"prefix": "ALLOCATION", "color": ColorCode.BRIGHT_MAGENTA},
            LogLevel.WARNING.value: {"prefix": "WARNING", "color": ColorCode.YELLOW},
            LogLevel.ERROR.value: {"prefix": "ERROR", "color": ColorCode.RED},
            LogLevel.CRITICAL.value: {"prefix": "CRITICAL", "color": ColorCode.BRIGHT_RED}
        }
    
    def _get_terminal_size(self) -> Tuple[int, int]:
        """
        Get the terminal size (width, height) in characters.
        Returns a default of (80, 24) if unable to determine.
        """
        try:
            # Try to get the terminal size using shutil
            columns, lines = shutil.get_terminal_size()
            return columns, lines
        except (AttributeError, OSError):
            # If that fails, try environment variables
            try:
                columns = int(os.environ.get('COLUMNS', 80))
                lines = int(os.environ.get('LINES', 24))
                return columns, lines
            except (ValueError, TypeError):
                # Return defaults if all else fails
                return 80, 24
    
    def _setup_handlers(self):
        """Set up console and file handlers"""
        # Clear existing handlers if any
        self.handlers = []
        
        # Always add console handler
        self.handlers.append(sys.stdout)
        
        # Add file handler if requested
        if self.log_to_file and self.log_file:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            # Open file for writing
            self.file_handler = open(self.log_file, 'a', encoding='utf-8')
            self.handlers.append(self.file_handler)
    
    def _format_message(self, level, message, extras=None):
        """Format log message with timestamp, level, and extras"""
        timestamp = datetime.now().strftime("%d-%m-%y %H:%M:%S.%f")[:-3]
        style = self.level_styles.get(level, self.level_styles[LogLevel.INFO.value])
        
        # Fixed width for the level indicator - 12 characters
        level_width = 12
        # Center the level text in the fixed width
        centered_prefix = style["prefix"].center(level_width)
        
        # Format level indicator with appropriate color
        level_indicator = f"{style['color']}{centered_prefix}{ColorCode.RESET}"
        
        # Combine all components
        base_msg = f"{timestamp} {level_indicator} {message}"
        
        # For file output - no colors, use brackets instead
        file_msg = f"{timestamp} [{centered_prefix}] {message}"
        
        # Add extras if provided
        if extras:
            extra_str = " | " + " | ".join(f"{k}={v}" for k, v in extras.items())
            base_msg += extra_str
            file_msg += extra_str
        
        return base_msg, file_msg
    
    def _log(self, level, message, extras=None):
        """Internal logging method"""
        if level < self.log_level:
            return
        
        base_msg, file_msg = self._format_message(level, message, extras)
        
        # Use tqdm.write for console output if available, otherwise use print
        if TQDM_AVAILABLE:
            # Write to console with tqdm.write
            tqdm.write(base_msg)
            
            # Write to file if file handler exists
            if hasattr(self, 'file_handler') and self.file_handler:
                print(file_msg, file=self.file_handler)
        else:
            # Fall back to original implementation if tqdm is not available
            # If we have an active progress bar, first clear the line
            has_progress = hasattr(self, '_progress_data') and self._progress_data.get("active", False)
            if has_progress and hasattr(self.handlers[0], 'isatty') and self.handlers[0].isatty():
                # Get terminal width to clear the entire line properly
                terminal_width, _ = self._get_terminal_size()
                # Clear the line with carriage return and spaces
                print("\r" + " " * terminal_width + "\r", end='', file=self.handlers[0])
            
            for handler in self.handlers:
                if handler == self.file_handler if hasattr(self, 'file_handler') else False:
                    print(file_msg, file=handler)
                else:
                    print(base_msg, file=handler)
            
            # If we have an active progress bar, redraw it
            if has_progress and hasattr(self.handlers[0], 'isatty') and self.handlers[0].isatty():
                self._update_progress_bar(self._progress_data["current"])
                
    def progress_iter(self, iterable, desc="", total=None, **kwargs):
        """
        Create a tqdm-wrapped iterator for direct use in loops.
        
        Args:
            iterable: The iterable to wrap with tqdm
            desc: Description to show in the progress bar
            total: Total number of items (if not provided, len(iterable) is used)
            **kwargs: Additional arguments to pass to tqdm
            
        Returns:
            A tqdm-wrapped iterator or the original iterable if tqdm is not available
        """
        if TQDM_AVAILABLE:
            if total is None:
                try:
                    total = len(iterable)
                except (TypeError, AttributeError):
                    total = None
                    
            # Create a tqdm instance for the iterable
            progress_bar = tqdm(
                iterable,
                desc=desc,
                total=total,
                dynamic_ncols=True,
                **kwargs
            )
            
            return progress_bar
        else:
            # If tqdm is not available, return the original iterable
            return iterable
    
    def debug(self, message, **extras):
        """Log debug message"""
        self._log(LogLevel.DEBUG.value, message, extras)
    
    def info(self, message, **extras):
        """Log info message"""
        self._log(LogLevel.INFO.value, message, extras)

    def main(self, message, **extras):
        """Log info message"""
        self._log(LogLevel.MAIN.value, message, extras)
    
    def success(self, message, **extras):
        """Log success message"""
        self._log(LogLevel.SUCCESS.value, message, extras)
    
    def project(self, message, **extras):
        """Log project-related message"""
        self._log(LogLevel.PROJECT.value, message, extras)
    
    def document(self, message, **extras):
        """Log document-related message"""
        self._log(LogLevel.DOCUMENT.value, message, extras)
    
    def film(self, message, **extras):
        """Log film-related message"""
        self._log(LogLevel.FILM.value, message, extras)
    
    def allocation(self, message, **extras):
        """Log allocation message"""
        self._log(LogLevel.ALLOCATION.value, message, extras)
    
    def warning(self, message, **extras):
        """Log warning message"""
        self._log(LogLevel.WARNING.value, message, extras)
    
    def error(self, message, **extras):
        """Log error message"""
        self._log(LogLevel.ERROR.value, message, extras)
    
    def critical(self, message, **extras):
        """Log critical message"""
        self._log(LogLevel.CRITICAL.value, message, extras)
    
    def start_progress(self, total, prefix="", suffix="", bar_length=None):
        """Start a new progress tracking session using tqdm if available."""
        if TQDM_AVAILABLE:
            # Create description from prefix and suffix
            desc = f"{prefix}" if prefix else ""
            if suffix:
                desc = f"{desc} ({suffix})" if desc else f"{suffix}"
                
            # Create the tqdm instance with consistent styling
            progress_bar = create_tqdm_instance(
                total=total,
                desc=desc.strip(),
                unit="it"
            )
            
            # Store the active progress bar
            self._active_progress = progress_bar
            return progress_bar
        else:
            # Fall back to original implementation if tqdm is not available
            # If bar_length is None, calculate based on terminal width
            if bar_length is None:
                terminal_width, _ = self._get_terminal_size()
                # Reserve space for prefix, suffix, percentage, and brackets
                reserved_space = len(prefix) + len(suffix) + 10  # 10 for percentage and decorations
                # Use a percentage of the terminal width (70%) for the bar
                bar_length = max(10, int((terminal_width - reserved_space) * 0.7))
            
            self._progress_data = {
                "total": total,
                "current": 0,
                "prefix": prefix,
                "suffix": suffix,
                "bar_length": bar_length,
                "active": True
            }
            # Draw the initial progress bar
            self._update_progress_bar(0)
            return self._progress_data
    
    def update_progress(self, current=None, increment=1):
        """Update the progress bar with new value"""
        if TQDM_AVAILABLE and hasattr(self, '_active_progress'):
            # Update the tqdm progress bar
            if current is not None:
                # Calculate the increment based on current position
                if hasattr(self._active_progress, 'n'):
                    increment = current - self._active_progress.n
                    if increment > 0:
                        self._active_progress.update(increment)
                    else:
                        # If we're going backwards, reset and update to current
                        self._active_progress.reset()
                        self._active_progress.update(current)
                else:
                    # Fallback if n attribute doesn't exist
                    self._active_progress.update(increment)
            else:
                # Update by the increment amount
                self._active_progress.update(increment)
                
            # Check if we're done
            if hasattr(self._active_progress, 'n') and hasattr(self._active_progress, 'total'):
                if self._active_progress.n >= self._active_progress.total:
                    self.finish_progress()
        else:
            # Fall back to original implementation
            if not hasattr(self, '_progress_data') or not self._progress_data["active"]:
                return
            
            # Update the current progress
            if current is not None:
                self._progress_data["current"] = current
            else:
                self._progress_data["current"] += increment
            
            # Ensure we don't exceed the total
            if self._progress_data["current"] > self._progress_data["total"]:
                self._progress_data["current"] = self._progress_data["total"]
            
            # Update the display
            self._update_progress_bar(self._progress_data["current"])
            
            # Check if we're done
            if self._progress_data["current"] >= self._progress_data["total"]:
                self.finish_progress()
    
    def finish_progress(self):
        """Complete the progress tracking and clean up"""
        if TQDM_AVAILABLE and hasattr(self, '_active_progress'):
            # Close the tqdm progress bar
            self._active_progress.close()
            # Remove the reference
            delattr(self, '_active_progress')
        else:
            # Fall back to original implementation
            if not hasattr(self, '_progress_data') or not self._progress_data["active"]:
                return
            
            # Ensure the progress shows 100%
            self._update_progress_bar(self._progress_data["total"])
            
            # Mark as inactive
            self._progress_data["active"] = False
            
            # Add a blank line for separation
            if hasattr(self.handlers[0], 'isatty') and self.handlers[0].isatty():
                print("", file=self.handlers[0])
                
    def _update_progress_bar(self, current):
        """Internal method to redraw the progress bar"""
        if not hasattr(self, '_progress_data') or not self._progress_data:
            return
            
        # Only display progress in terminals, not log files
        if not hasattr(self.handlers[0], 'isatty') or not self.handlers[0].isatty():
            return
            
        # Calculate the progress components
        total = self._progress_data["total"]
        prefix = self._progress_data["prefix"]
        suffix = self._progress_data["suffix"]
        bar_length = self._progress_data["bar_length"]
        
        # Avoid division by zero
        if total <= 0:
            percent = 100
        else:
            percent = min(100, (current / total) * 100)
        
        # Create the visual bar
        filled_length = int(bar_length * current // max(1, total))
        bar = ColorCode.BRIGHT_GREEN + '█' * filled_length + ColorCode.BRIGHT_BLACK + '█' * (bar_length - filled_length) + ColorCode.RESET
        
        # Format the progress line with bright white text
        progress_line = f"\r{ColorCode.BRIGHT_WHITE}{prefix} |{bar}| {percent:.1f}% {suffix}{ColorCode.RESET}"
        
        # Print the progress line, staying on the same line
        print(progress_line, end='', file=self.handlers[0])
    
    def progress(self, current, total, prefix="", suffix="", bar_length=None):
        """Legacy method for backward compatibility with single-update progress bars"""
        # If we don't have an active progress or it's for a different total,
        # start a new one
        if (not hasattr(self, '_progress_data') or 
            not self._progress_data["active"] or 
            self._progress_data["total"] != total or
            self._progress_data["prefix"] != prefix):
            
            self.start_progress(total, prefix, suffix, bar_length)
        
        # Update the progress
        self.update_progress(current)
    
    def section(self, title, width=80):
        """Print a section header with optional width."""
        if not title:
            return
        
        # Map section titles to appropriate background colors
        section_colors = {
            "INITIALIZING PROJECT": ColorCode.BG_GREEN,
            "PROCESSING DOCUMENTS": ColorCode.BG_CYAN,
            "IDENTIFYING OVERSIZED PAGES": ColorCode.BG_CYAN,
            "CALCULATING REFERENCE PAGES": ColorCode.BG_MAGENTA,
            "CALCULATING FILM ALLOCATION": ColorCode.BG_BLUE,
            "EXPORTING RESULTS": ColorCode.BG_GREEN,
            "16MM FILM ALLOCATION": ColorCode.BG_MAGENTA,
            "FILM ALLOCATION": ColorCode.BG_MAGENTA,
            "POSTPROCESSING DOCUMENTS": ColorCode.BG_BRIGHT_RED

        }
        
        # Get background color based on title, default to blue for unknown sections
        bg_color = ColorCode.BG_BLUE
        for section_key, color in section_colors.items():
            if section_key in title.upper():
                bg_color = color
                break
        
        # Create a section header with solid background
        title_padded = f" {title} ".center(width - 4)  # Pad with spaces for better appearance
        
        for handler in self.handlers:
            # Handlers now contain stream objects directly, not StreamHandler objects
            if hasattr(handler, 'isatty') and handler.isatty():
                # With solid background color for terminal - using bright white for better visibility
                handler.write(f"\n{bg_color}{ColorCode.BRIGHT_WHITE}{ColorCode.BOLD}{title_padded}{ColorCode.RESET}\n")
            else:
                # Plain text version for files
                header = f"{'-' * 5} {title} {'-' * (width - 7 - len(title))}"
                handler.write(f"\n{header}\n")
            handler.flush()
    
    def timer(self, operation_name):
        """Context manager for timing operations"""
        return TimerContext(self, operation_name)
    
    def close(self):
        """Close file handlers"""
        if hasattr(self, 'file_handler') and self.file_handler:
            self.file_handler.close()

    def save_log_file(self, log_file=None, archive_id=None):
        """
        Save log output to a file.
        
        Args:
            log_file: Optional path to the log file. If not provided, a default path will be used.
            archive_id: Optional archive ID to include in the log file name.
        """
        # Close any existing file handlers
        if hasattr(self, 'file_handler') and self.file_handler:
            self.file_handler.close()
            self.file_handler = None
            
        # Remove any existing file handlers from the logger
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
        
        # Determine the logs directory path
        if self.parent_folder:
            logs_dir = os.path.join(self.parent_folder, '.logs')
        else:
            logs_dir = os.path.join('.', '.logs')
            
        # Create logs directory if it doesn't exist
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        # Determine the log file path
        if log_file:
            self.log_file = log_file
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if archive_id and archive_id != "Unknown":
                # Extract just the archive ID part (e.g., "RRD017-2024" from "RRD017-2024_DW_FAIR")
                archive_id_parts = archive_id.split('_')
                archive_id_base = archive_id_parts[0] if archive_id_parts else archive_id
                self.log_file = os.path.join(logs_dir, f"{archive_id_base}_{timestamp}.log")
            else:
                self.log_file = os.path.join(logs_dir, f"{timestamp}.log")
            
        # Add file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Also set up the direct file handler for custom formatting
        self.file_handler = open(self.log_file, 'a', encoding='utf-8')
        
        # Log the file path
        self.logger.info(f"Log file saved to: {self.log_file}")

    def progress_context(self, total, desc="", **kwargs):
        """
        Context manager for progress tracking.
        
        Args:
            total: Total number of items
            desc: Description for the progress bar
            **kwargs: Additional arguments for tqdm
            
        Returns:
            A context manager that will automatically close the progress bar
        """
        return ProgressContext(self, total, desc, **kwargs)

class TimerContext:
    """Context manager for timing operations"""
    def __init__(self, logger, operation_name):
        self.logger = logger
        self.operation_name = operation_name
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            self.logger.error(f"Failed: {self.operation_name} ({duration:.2f}s)", error=str(exc_val))
        else:
            self.logger.success(f"Completed: {self.operation_name} ({duration:.2f}s)")
        
        return False  # Don't suppress exceptions

class ProgressContext:
    """Context manager for progress tracking with tqdm"""
    def __init__(self, logger, total, desc="", **kwargs):
        self.logger = logger
        self.total = total
        self.desc = desc
        self.kwargs = kwargs
        self.progress_bar = None
        
    def __enter__(self):
        self.progress_bar = self.logger.start_progress(
            total=self.total, 
            prefix=self.desc, 
            **self.kwargs
        )
        return self.progress_bar
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress_bar:
            self.logger.finish_progress()
        return False  # Don't suppress exceptions

# Utility function to create tqdm instances with consistent configuration
def create_tqdm_instance(total, desc="", unit="it", leave=True, position=0, **kwargs):
    """Create a configured tqdm instance with consistent styling."""
    if not TQDM_AVAILABLE:
        return None
        
    return tqdm(
        total=total,
        desc=desc,
        unit=unit,
        leave=leave,
        position=position,
        colour="green",
        dynamic_ncols=True,  # Adjust to terminal width
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        **kwargs
    )