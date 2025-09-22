"""
Centralized logging module for the Pagify application.

This module provides consistent, colorful logging functionality across all modules
with module-level and severity distinction in log messages.
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

class LogModule(Enum):
    """Available logging modules"""
    MAIN = "MAIN"           # Main application information
    PROJECT = "PROJECT"     # Project-related information
    DOCUMENT = "DOCUMENT"   # Document-related information
    ALLOCATION = "ALLOCATION" # Allocation decisions
    FILM = "FILM"           # Film roll operations
    DATABASE = "DATABASE"   # Database operations
    REFERENCE = "REFERENCE" # Reference-related information
    EXPORT = "EXPORT"       # Export operations
    DISTRIBUTION = "DISTRIBUTION"  # Add this new module

class LogLevel(Enum):
    """Severity log levels"""
    DEBUG = 10      # Detailed debugging information
    INFO = 20       # General information
    SUCCESS = 30    # Successful operations
    WARNING = 40    # Warnings
    ERROR = 50      # Errors
    CRITICAL = 60   # Critical failures

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

class FilmLogger:
    """
    A logger class for film processing operations with module and severity level distinction.
    """
    
    def __init__(self, name, log_level=LogLevel.INFO.value, log_to_file=True, parent_folder=None, silent=False):
        """
        Initialize the FilmLogger.
        
        Args:
            name: Name of the logger
            log_level: Logging level (default: LogLevel.INFO.value)
            log_to_file: Whether to log to a file (default: True)
            parent_folder: Parent folder path for log files (default: None)
            silent: Whether to suppress section headers and other visual output (default: False)
        """
        self.name = name
        self.silent = silent
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
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        self.handlers.append(console_handler)
        
        # Set up file logging if enabled and parent_folder is provided
        if log_to_file and parent_folder:
            self.save_log_file()
        
        # Set up the module styles
        self.module_styles = {
            LogModule.MAIN.value: {"color": ColorCode.BRIGHT_BLUE},
            LogModule.PROJECT.value: {"color": ColorCode.BLUE},
            LogModule.DOCUMENT.value: {"color": ColorCode.CYAN},
            LogModule.ALLOCATION.value: {"color": ColorCode.MAGENTA},
            LogModule.FILM.value: {"color": ColorCode.BRIGHT_MAGENTA},
            LogModule.DATABASE.value: {"color": ColorCode.GREEN},
            LogModule.REFERENCE.value: {"color": ColorCode.YELLOW},
            LogModule.EXPORT.value: {"color": ColorCode.BRIGHT_CYAN},
            LogModule.DISTRIBUTION.value: {"color": ColorCode.BRIGHT_GREEN},
        }
        
        # Set up the severity level styles with background colors
        self.level_styles = {
            LogLevel.DEBUG.value: {"bg_color": ColorCode.BG_ORANGE, "text": "DEBUG"},
            LogLevel.INFO.value: {"bg_color": ColorCode.BG_BRIGHT_WHITE, "text": "INFO"},
            LogLevel.SUCCESS.value: {"bg_color": ColorCode.BG_GREEN, "text": "SUCCESS"},
            LogLevel.WARNING.value: {"bg_color": ColorCode.BG_YELLOW, "text": "WARNING"},
            LogLevel.ERROR.value: {"bg_color": ColorCode.BG_RED, "text": "ERROR"},
            LogLevel.CRITICAL.value: {"bg_color": ColorCode.BG_BRIGHT_RED, "text": "CRITICAL"},
        }
        
        # Initialize progress tracking data
        self._progress_data = None
        self._active_progress = None
    
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
    
    def _format_message(self, module, level, message, extras=None):
        """
        Format log message with timestamp, module, level, and extras
        
        Args:
            module: The module name (from LogModule)
            level: The severity level (from LogLevel)
            message: The log message
            extras: Optional dictionary of extra information
            
        Returns:
            Tuple of (console_message, file_message)
        """
        timestamp = datetime.now().strftime("%d-%m-%y %H:%M:%S.%f")[:-3]
        
        # Get module and level styles
        module_style = self.module_styles.get(module, self.module_styles[LogModule.MAIN.value])
        level_style = self.level_styles.get(level, self.level_styles[LogLevel.INFO.value])
        
        # Format the module and level indicators with centered text
        # Make all module and level text consistent width
        module_width = 10
        level_width = 8
        
        module_text = module.center(module_width)
        level_text = level_style['text'].center(level_width)
        
        # Format the module indicator with vertical bars and color
        module_indicator = f"{module_style['color']}| {module_text} |{ColorCode.RESET}"
        
        # Format the level indicator with centered text in background and vertical bars
        level_indicator = f"{level_style['bg_color']}{ColorCode.BLACK} {level_text} {ColorCode.RESET}"
        
        # Combine for console output (with colors)
        console_msg = f"{timestamp} {module_indicator} {level_indicator} {message}"
        
        # For file output - no colors, include file and line info
        # Get caller frame info for file and line information
        # Current frame -> FilmLogger method -> Caller
        frame = sys._getframe(3)  # Adjust this number if needed
        file_name = os.path.basename(frame.f_code.co_filename)
        line_no = frame.f_lineno
        file_msg = f"{timestamp} [{module:8s}] [{level_style['text']:8s}] [{file_name}:{line_no}] {message}"
        
        # Add extras if provided
        if extras:
            extra_str = " | " + " | ".join(f"{k}={v}" for k, v in extras.items())
            console_msg += extra_str
            file_msg += extra_str
        
        return console_msg, file_msg
    
    def _log(self, module, level, message, extras=None):
        """
        Internal logging method
        
        Args:
            module: The module name (from LogModule)
            level: The severity level (from LogLevel)
            message: The log message
            extras: Optional dictionary of extra information
        """
        if level < self.log_level:
            return
        
        console_msg, file_msg = self._format_message(module, level, message, extras)
        
        # Use tqdm.write for console output if available, otherwise use print
        if TQDM_AVAILABLE:
            # Write to console with tqdm.write
            tqdm.write(console_msg)
            
            # Write to file if file handler exists
            if hasattr(self, 'file_handler') and self.file_handler:
                print(file_msg, file=self.file_handler)
        else:
            # Fall back to original implementation if tqdm is not available
            # If we have an active progress bar, first clear the line
            has_progress = hasattr(self, '_progress_data') and self._progress_data and self._progress_data.get("active", False)
            if has_progress and hasattr(self.handlers[0], 'isatty') and self.handlers[0].isatty():
                # Get terminal width to clear the entire line properly
                terminal_width, _ = self._get_terminal_size()
                # Clear the line with carriage return and spaces
                print("\r" + " " * terminal_width + "\r", end='', file=self.handlers[0])
            
            for handler in self.handlers:
                if handler == self.file_handler if hasattr(self, 'file_handler') else False:
                    print(file_msg, file=handler)
                else:
                    print(console_msg, file=handler)
            
            # If we have an active progress bar, redraw it
            if has_progress and hasattr(self.handlers[0], 'isatty') and self.handlers[0].isatty():
                self._update_progress_bar(self._progress_data["current"])
    
    # Module-level logging methods
    
    # MAIN module methods
    def main_debug(self, message, **extras):
        """Log debug message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.DEBUG.value, message, extras)
    
    def main_info(self, message, **extras):
        """Log info message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.INFO.value, message, extras)
    
    def main_success(self, message, **extras):
        """Log success message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.SUCCESS.value, message, extras)
    
    def main_warning(self, message, **extras):
        """Log warning message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.WARNING.value, message, extras)
    
    def main_error(self, message, **extras):
        """Log error message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.ERROR.value, message, extras)
    
    def main_critical(self, message, **extras):
        """Log critical message from MAIN module"""
        self._log(LogModule.MAIN.value, LogLevel.CRITICAL.value, message, extras)
    
    # PROJECT module methods
    def project_debug(self, message, **extras):
        """Log debug message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.DEBUG.value, message, extras)
    
    def project_info(self, message, **extras):
        """Log info message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.INFO.value, message, extras)
    
    def project_success(self, message, **extras):
        """Log success message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.SUCCESS.value, message, extras)
    
    def project_warning(self, message, **extras):
        """Log warning message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.WARNING.value, message, extras)
    
    def project_error(self, message, **extras):
        """Log error message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.ERROR.value, message, extras)
    
    def project_critical(self, message, **extras):
        """Log critical message from PROJECT module"""
        self._log(LogModule.PROJECT.value, LogLevel.CRITICAL.value, message, extras)
    
    # DOCUMENT module methods
    def document_debug(self, message, **extras):
        """Log debug message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.DEBUG.value, message, extras)
    
    def document_info(self, message, **extras):
        """Log info message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.INFO.value, message, extras)
    
    def document_success(self, message, **extras):
        """Log success message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.SUCCESS.value, message, extras)
    
    def document_warning(self, message, **extras):
        """Log warning message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.WARNING.value, message, extras)
    
    def document_error(self, message, **extras):
        """Log error message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.ERROR.value, message, extras)
    
    def document_critical(self, message, **extras):
        """Log critical message from DOCUMENT module"""
        self._log(LogModule.DOCUMENT.value, LogLevel.CRITICAL.value, message, extras)
    
    # ALLOCATION module methods
    def allocation_debug(self, message, **extras):
        """Log debug message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.DEBUG.value, message, extras)
    
    def allocation_info(self, message, **extras):
        """Log info message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.INFO.value, message, extras)
    
    def allocation_success(self, message, **extras):
        """Log success message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.SUCCESS.value, message, extras)
    
    def allocation_warning(self, message, **extras):
        """Log warning message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.WARNING.value, message, extras)
    
    def allocation_error(self, message, **extras):
        """Log error message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.ERROR.value, message, extras)
    
    def allocation_critical(self, message, **extras):
        """Log critical message from ALLOCATION module"""
        self._log(LogModule.ALLOCATION.value, LogLevel.CRITICAL.value, message, extras)
    
    # FILM module methods
    def film_debug(self, message, **extras):
        """Log debug message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.DEBUG.value, message, extras)
    
    def film_info(self, message, **extras):
        """Log info message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.INFO.value, message, extras)
    
    def film_success(self, message, **extras):
        """Log success message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.SUCCESS.value, message, extras)
    
    def film_warning(self, message, **extras):
        """Log warning message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.WARNING.value, message, extras)
    
    def film_error(self, message, **extras):
        """Log error message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.ERROR.value, message, extras)
    
    def film_critical(self, message, **extras):
        """Log critical message from FILM module"""
        self._log(LogModule.FILM.value, LogLevel.CRITICAL.value, message, extras)
    
    # DATABASE module methods
    def database_debug(self, message, **extras):
        """Log debug message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.DEBUG.value, message, extras)
    
    def database_info(self, message, **extras):
        """Log info message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.INFO.value, message, extras)
    
    def database_success(self, message, **extras):
        """Log success message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.SUCCESS.value, message, extras)
    
    def database_warning(self, message, **extras):
        """Log warning message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.WARNING.value, message, extras)
    
    def database_error(self, message, **extras):
        """Log error message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.ERROR.value, message, extras)
    
    def database_critical(self, message, **extras):
        """Log critical message from DATABASE module"""
        self._log(LogModule.DATABASE.value, LogLevel.CRITICAL.value, message, extras)
    
    # REFERENCE module methods
    def reference_debug(self, message, **extras):
        """Log debug message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.DEBUG.value, message, extras)
    
    def reference_info(self, message, **extras):
        """Log info message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.INFO.value, message, extras)
    
    def reference_success(self, message, **extras):
        """Log success message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.SUCCESS.value, message, extras)
    
    def reference_warning(self, message, **extras):
        """Log warning message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.WARNING.value, message, extras)
    
    def reference_error(self, message, **extras):
        """Log error message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.ERROR.value, message, extras)
    
    def reference_critical(self, message, **extras):
        """Log critical message from REFERENCE module"""
        self._log(LogModule.REFERENCE.value, LogLevel.CRITICAL.value, message, extras)
    
    # EXPORT module methods
    def export_debug(self, message, **extras):
        """Log debug message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.DEBUG.value, message, extras)
    
    def export_info(self, message, **extras):
        """Log info message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.INFO.value, message, extras)
    
    def export_success(self, message, **extras):
        """Log success message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.SUCCESS.value, message, extras)
    
    def export_warning(self, message, **extras):
        """Log warning message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.WARNING.value, message, extras)
    
    def export_error(self, message, **extras):
        """Log error message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.ERROR.value, message, extras)
    
    def export_critical(self, message, **extras):
        """Log critical message from EXPORT module"""
        self._log(LogModule.EXPORT.value, LogLevel.CRITICAL.value, message, extras)
    
    # Progress tracking methods - maintained from original implementation
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
            if not hasattr(self, '_progress_data') or not self._progress_data or not self._progress_data.get("active", False):
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
            if not hasattr(self, '_progress_data') or not self._progress_data or not self._progress_data.get("active", False):
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
    
    def section(self, title, width=80):
        """Print a section header with optional width."""
        if not title or self.silent:
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
            if isinstance(handler, logging.StreamHandler):
                if hasattr(handler.stream, 'isatty') and handler.stream.isatty():
                    # With solid background color for terminal - using bright white for better visibility
                    handler.stream.write(f"\n{bg_color}{ColorCode.BRIGHT_WHITE}{ColorCode.BOLD}{title_padded}{ColorCode.RESET}\n")
                else:
                    # Plain text version for files
                    header = f"{'-' * 5} {title} {'-' * (width - 7 - len(title))}"
                    handler.stream.write(f"\n{header}\n")
                handler.stream.flush()
    
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
        logs_dir = r"C:\Users\user1\Desktop\microexcel\AnalysisResults\Logs"
            
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

    def subsection(self, title, width=80):
        """Print a subsection header with optional width."""
        if not title:
            return
        
        # Get terminal width if not specified
        if not width:
            terminal_width, _ = self._get_terminal_size()
            width = terminal_width
        
        # Format the subsection header
        header = f"\n{ColorCode.BRIGHT_CYAN}{title}{ColorCode.RESET}\n{ColorCode.DIM}{'-' * len(title)}{ColorCode.RESET}\n"
        
        # Print to each handler
        for handler in self.handlers:
            if handler == self.file_handler if hasattr(self, 'file_handler') else False:
                # Plain version for log file
                plain_header = f"\n{title}\n{'-' * len(title)}\n"
                print(plain_header, file=handler)
            else:
                # Colored version for console
                print(header, file=handler)

    def __enter__(self):
        """Support using logger as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up when exiting context."""
        self.close()
        
        # Log exception if one occurred
        if exc_type is not None:
            self.main_error(f"Exception occurred: {exc_val}")
            return False  # Let the exception propagate

    def distribution_debug(self, message):
        self._log(LogModule.DISTRIBUTION.value, LogLevel.DEBUG.value, message)

    def distribution_info(self, message):
        self._log(LogModule.DISTRIBUTION.value, LogLevel.INFO.value, message)

    def distribution_warning(self, message):
        self._log(LogModule.DISTRIBUTION.value, LogLevel.WARNING.value, message)
    
    def distribution_error(self, message):
        self._log(LogModule.DISTRIBUTION.value, LogLevel.ERROR.value, message)
    
    def distribution_success(self, message):
        self._log(LogModule.DISTRIBUTION.value, LogLevel.SUCCESS.value, message)

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
    """Context manager for progress tracking with the FilmLogger."""
    
    def __init__(self, logger, total, desc="", **kwargs):
        """
        Initialize the context manager.
        
        Args:
            logger: The FilmLogger instance
            total: Total number of items
            desc: Description for the progress bar
            **kwargs: Additional arguments for tqdm
        """
        self.logger = logger
        self.total = total
        self.desc = desc
        self.kwargs = kwargs
    
    def __enter__(self):
        """Start the progress tracking when entering the context."""
        if TQDM_AVAILABLE:
            self.progress_bar = self.logger.start_progress(
                total=self.total,
                prefix=self.desc,
                **self.kwargs
            )
            return self.progress_bar
        else:
            self.progress_data = self.logger.start_progress(
                total=self.total,
                prefix=self.desc
            )
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish the progress tracking when exiting the context."""
        self.logger.finish_progress()
        
    def update(self, n=1):
        """Update the progress by n steps."""
        self.logger.update_progress(increment=n)

def create_tqdm_instance(total, desc="", **kwargs):
    """
    Create a properly configured tqdm instance.
    
    Args:
        total: Total number of iterations
        desc: Description text
        **kwargs: Additional arguments for tqdm
        
    Returns:
        A configured tqdm instance
    """
    if not TQDM_AVAILABLE:
        return None
        
    from tqdm import tqdm
    
    # Apply consistent styling to all tqdm instances
    default_kwargs = {
        "total": total,
        "desc": desc,
        "ncols": 100,
        "unit": "it",
        "colour": "green",
        "leave": True,
        "dynamic_ncols": True
    }
    
    # Override defaults with any provided kwargs
    default_kwargs.update(kwargs)
    
    # Create and return the tqdm instance
    return tqdm(**default_kwargs)