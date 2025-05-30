"""
Custom exception classes for the SMA (film scanning) automation system.

This module defines specific exceptions that can occur during various stages
of the SMA scanning process, providing more granular error handling.
"""

class SMAException(Exception):
    """Base exception class for all SMA-related errors."""
    def __init__(self, message="SMA operation failed", details=None):
        super().__init__(message)
        self.details = details

class SMAProcessNotFoundError(SMAException):
    """Raised when SMA process cannot be found or connected to."""
    def __init__(self, message="SMA process not found or not accessible", details=None):
        super().__init__(message, details)

class SMAWindowNotFoundError(SMAException):
    """Raised when a required SMA window cannot be found."""
    def __init__(self, window_title=None, message=None, details=None):
        if message is None:
            message = f"SMA window not found: {window_title}" if window_title else "SMA window not found"
        super().__init__(message, details)
        self.window_title = window_title

class SMAControlNotFoundError(SMAException):
    """Raised when a required SMA control cannot be found."""
    def __init__(self, control_name=None, message=None, details=None):
        if message is None:
            message = f"SMA control not found: {control_name}" if control_name else "SMA control not found"
        super().__init__(message, details)
        self.control_name = control_name

class SMAButtonClickError(SMAException):
    """Raised when a button click operation fails."""
    def __init__(self, button_name=None, message=None, details=None):
        if message is None:
            message = f"Failed to click button: {button_name}" if button_name else "Button click failed"
        super().__init__(message, details)
        self.button_name = button_name

class SMATimeoutError(SMAException):
    """Raised when an operation times out."""
    def __init__(self, operation=None, timeout_duration=None, message=None, details=None):
        if message is None:
            msg_parts = ["Operation timed out"]
            if operation:
                msg_parts.append(f"({operation})")
            if timeout_duration:
                msg_parts.append(f"after {timeout_duration}s")
            message = " ".join(msg_parts)
        super().__init__(message, details)
        self.operation = operation
        self.timeout_duration = timeout_duration

class SMAConfigurationError(SMAException):
    """Raised when configuration is invalid or missing."""
    def __init__(self, config_item=None, message=None, details=None):
        if message is None:
            message = f"Configuration error: {config_item}" if config_item else "Configuration error"
        super().__init__(message, details)
        self.config_item = config_item

class SMAFileError(SMAException):
    """Raised when file operations fail."""
    def __init__(self, file_path=None, operation=None, message=None, details=None):
        if message is None:
            msg_parts = ["File operation failed"]
            if operation:
                msg_parts.append(f"({operation})")
            if file_path:
                msg_parts.append(f"for file: {file_path}")
            message = " ".join(msg_parts)
        super().__init__(message, details)
        self.file_path = file_path
        self.operation = operation

class SMATemplateError(SMAException):
    """Raised when template file operations fail."""
    def __init__(self, template_name=None, message=None, details=None):
        if message is None:
            message = f"Template error: {template_name}" if template_name else "Template error"
        super().__init__(message, details)
        self.template_name = template_name

class SMAINIError(SMAException):
    """Raised when INI file operations fail."""
    def __init__(self, ini_path=None, message=None, details=None):
        if message is None:
            message = f"INI file error: {ini_path}" if ini_path else "INI file error"
        super().__init__(message, details)
        self.ini_path = ini_path

class SMARecoveryError(SMAException):
    """Raised when session recovery fails."""
    def __init__(self, message="Session recovery failed", details=None):
        super().__init__(message, details)

class SMAProgressMonitorError(SMAException):
    """Raised when progress monitoring fails."""
    def __init__(self, message="Progress monitoring failed", details=None):
        super().__init__(message, details)

class SMAAdvancedFinishError(SMAException):
    """Raised when advanced finish features fail."""
    def __init__(self, feature=None, message=None, details=None):
        if message is None:
            message = f"Advanced finish error: {feature}" if feature else "Advanced finish error"
        super().__init__(message, details)
        self.feature = feature

class SMANotificationError(SMAException):
    """Raised when notification sending fails."""
    def __init__(self, notification_type=None, message=None, details=None):
        if message is None:
            message = f"Notification error: {notification_type}" if notification_type else "Notification error"
        super().__init__(message, details)
        self.notification_type = notification_type

class SMADependencyError(SMAException):
    """Raised when required dependencies are missing."""
    def __init__(self, dependency=None, message=None, details=None):
        if message is None:
            message = f"Missing dependency: {dependency}" if dependency else "Missing dependency"
        super().__init__(message, details)
        self.dependency = dependency

# Utility function for error context
def add_error_context(exception, context):
    """Add context information to an existing exception."""
    if hasattr(exception, 'details'):
        if exception.details is None:
            exception.details = {}
        if isinstance(exception.details, dict):
            exception.details.update(context)
    return exception

# Error logging helper
def log_exception(logger, exception, operation=None):
    """Log an exception with proper context."""
    if operation:
        logger.error(f"Error during {operation}: {exception}")
    else:
        logger.error(f"Error: {exception}")
    
    if hasattr(exception, 'details') and exception.details:
        logger.error(f"Exception details: {exception.details}")
    
    # Log the full traceback for debugging
    import traceback
    logger.error(traceback.format_exc()) 