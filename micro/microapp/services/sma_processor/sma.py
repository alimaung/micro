#!/usr/bin/env python3
"""
SMA (film scanning) automation system - Main Entry Point

This is the main entry point for the SMA automation system. It replaces the
original monolithic sma.py file with a modular architecture.

The original 2100+ line file has been refactored into the following modules:
- sma_controller.py: Main orchestrator
- sma_config.py: Configuration management  
- ui_automation.py: UI automation core
- sma_workflow.py: SMA application workflow
- progress_monitor.py: Progress tracking system
- advanced_finish.py: Advanced warning system
- post_processing.py: End-of-process handling
- sma_exceptions.py: Custom exception classes
- sma_utils.py: Utility functions and helpers

Usage:
    python sma.py <folder_path> <template> [--filmnumber <number>] [--recovery]
    
    Examples:
        python sma.py "Y:\\Data\\Film001" 16
        python sma.py "Y:\\Data\\Film002" 35 --filmnumber "CUSTOM_NAME" 
        python sma.py "Y:\\Data\\Film003" 16 --recovery
"""

import sys
import os

# Add the sma package to Python path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the SMA automation system."""
    try:
        # Import the main controller from the sma package
        from sma import SMAController, main as sma_main
        
        # Run the automation system
        success = sma_main()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except ImportError as e:
        print(f"Error importing SMA modules: {e}")
        print("Please ensure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error in SMA automation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 