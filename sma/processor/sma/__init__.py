"""
SMA (film scanning) automation system package.

This package provides a modular automation system for SMA film scanning operations.

Main Components:
- SMAController: Main orchestrator for the automation process
- SMAConfig: Configuration management
- UI automation functions for SMA application interaction
- Progress monitoring with advanced finish warnings
- Post-processing and cleanup operations

Usage:
    from sma import SMAController
    
    controller = SMAController()
    success = controller.run()
"""

# Main controller for easy access
from .sma_controller import SMAController, main

# Configuration management
from .sma_config import SMAConfig

# Exception classes
from .sma_exceptions import (
    SMAException, SMAProcessNotFoundError, SMAWindowNotFoundError,
    SMAControlNotFoundError, SMAButtonClickError, SMATimeoutError,
    SMAConfigurationError, SMAFileError, SMATemplateError, SMAINIError,
    SMARecoveryError, SMAProgressMonitorError, SMAAdvancedFinishError,
    SMANotificationError, SMADependencyError
)

# Utility functions that might be needed externally
from .sma_utils import (
    setup_logging, log_system_info, PerformanceTimer,
    calculate_eta, format_progress_percent
)

# Progress monitoring
from .progress_monitor import ProgressMonitor, monitor_progress

# Post-processing
from .post_processing import PostProcessingManager, check_log_file

# Advanced finish system
from .advanced_finish import (
    AdvancedFinishManager, create_advanced_finish_manager,
    get_availability_status, check_dependencies
)

# Version information
__version__ = "2.0.0"
__author__ = "SMA Automation Team"
__description__ = "Modular SMA film scanning automation system"

# Package metadata
__all__ = [
    # Main classes
    'SMAController',
    'SMAConfig',
    'ProgressMonitor',
    'PostProcessingManager',
    'AdvancedFinishManager',
    
    # Main entry point
    'main',
    
    # Exception classes
    'SMAException',
    'SMAProcessNotFoundError',
    'SMAWindowNotFoundError',
    'SMAControlNotFoundError',
    'SMAButtonClickError',
    'SMATimeoutError',
    'SMAConfigurationError',
    'SMAFileError',
    'SMATemplateError',
    'SMAINIError',
    'SMARecoveryError',
    'SMAProgressMonitorError',
    'SMAAdvancedFinishError',
    'SMANotificationError',
    'SMADependencyError',
    
    # Utility functions
    'setup_logging',
    'log_system_info',
    'PerformanceTimer',
    'calculate_eta',
    'format_progress_percent',
    
    # Convenience functions
    'monitor_progress',
    'check_log_file',
    'create_advanced_finish_manager',
    'get_availability_status',
    'check_dependencies',
]

# Package information
def get_package_info():
    """Get package information."""
    return {
        'name': 'sma',
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'modules': [
            'sma_controller',
            'sma_config', 
            'ui_automation',
            'sma_workflow',
            'progress_monitor',
            'advanced_finish',
            'post_processing',
            'sma_exceptions',
            'sma_utils'
        ]
    } 