#!/usr/bin/env python
"""
Motor Initialization Script

This script initializes the Trinamic motors with the correct configuration from the INI file.
Run this at system startup to ensure the motors are configured properly.
"""

import sys
import os
import argparse
import time

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.motor_control import MotorControl
from src.config_manager import ConfigManager
from src.logger import logger, LogLevel


def initialize_motors(port, baudrate, debug=False, check_running=True):
    """
    Initialize the motors with configuration from INI file
    
    Args:
        port: Serial port to use
        baudrate: Baud rate for serial communication
        debug: Enable debug logging
        check_running: Check if motors are running before initialization
    
    Returns:
        True if successful, False otherwise
    """
    # Set logger level
    logger.min_level = LogLevel.DEBUG if debug else LogLevel.INFO
    
    logger.info("INIT", f"Initializing Trinamic motors on port {port}...")
    
    # Create controller instance
    controller = TrinamicController(port=port, baudrate=baudrate)
    
    try:
        # Connect to controller
        controller.connect()
        logger.info("INIT", "Connection established")
        
        # Create motor control interface
        motor_control = MotorControl(controller)
        
        # Create configuration manager
        config_manager = ConfigManager()
        
        # Check if motors are running
        if check_running:
            shutter_running = motor_control.is_motor_running(ConfigManager.MOTOR_SHUTTER)
            film_running = motor_control.is_motor_running(ConfigManager.MOTOR_FILM)
            
            if shutter_running:
                logger.warn("INIT", "Shutter motor is currently running!")
                stop_response = input("Do you want to stop the shutter motor before initializing? (y/n): ")
                if stop_response.lower() == 'y':
                    motor_control.stop_motor(ConfigManager.MOTOR_SHUTTER)
                    logger.info("INIT", "Shutter motor stopped")
                    time.sleep(0.5)
                else:
                    logger.warn("INIT", "Continuing with initialization while shutter motor is running")
            
            if film_running:
                logger.warn("INIT", "Film motor is currently running!")
                stop_response = input("Do you want to stop the film motor before initializing? (y/n): ")
                if stop_response.lower() == 'y':
                    motor_control.stop_motor(ConfigManager.MOTOR_FILM)
                    logger.info("INIT", "Film motor stopped")
                    time.sleep(0.5)
                else:
                    logger.warn("INIT", "Continuing with initialization while film motor is running")
        
        # Apply configuration
        logger.info("INIT", "Applying motor configuration from INI file...")
        config_manager.apply_motor_config(motor_control)
        
        # Print summary
        logger.info("INIT", "Motor initialization complete")
        logger.info("INIT", "Shutter motor settings:")
        shutter_config = config_manager.get_shutter_config()
        for key, value in shutter_config.items():
            logger.info("INIT", f"  {key}: {value}")
        
        logger.info("INIT", "Film motor settings:")
        film_config = config_manager.get_film_config()
        for key, value in film_config.items():
            logger.info("INIT", f"  {key}: {value}")
        
        return True
    
    except Exception as e:
        logger.error("INIT", f"Error during initialization: {e}")
        return False
    
    finally:
        # Always disconnect
        controller.disconnect()
        logger.info("INIT", "Controller disconnected")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Initialize Trinamic motors')
    
    parser.add_argument('--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baudrate (default: 9600)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--force', action='store_true', 
                      help='Force initialization without checking if motors are running')
    
    args = parser.parse_args()
    
    # Run initialization
    success = initialize_motors(
        port=args.port,
        baudrate=args.baudrate,
        debug=args.debug,
        check_running=not args.force
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 