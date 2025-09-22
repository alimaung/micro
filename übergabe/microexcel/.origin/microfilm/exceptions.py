"""
Custom exceptions for the microfilm processing system.

This module defines a hierarchy of custom exceptions used throughout the system
to provide structured error handling and reporting.
"""


class MicrofilmError(Exception):
    """Base exception for all microfilm related errors."""
    pass


class ProjectError(MicrofilmError):
    """Base exception for all project-related errors."""
    pass


class ProjectInitializationError(ProjectError):
    """Error raised during project initialization."""
    pass


class ProjectLoadError(ProjectError):
    """Error raised when loading a project fails."""
    pass


class ProjectExportError(ProjectError):
    """Error raised when exporting a project fails."""
    pass


class DirectoryError(MicrofilmError):
    """Error related to directory operations."""
    pass


class FileError(MicrofilmError):
    """Error related to file operations."""
    pass


class ValidationError(MicrofilmError):
    """Error raised during data validation."""
    pass


class ConfigurationError(MicrofilmError):
    """Error raised when configuration is invalid."""
    pass 