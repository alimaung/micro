"""
Motor Control CLI Tool

Command-line tool for controlling individual motor functions of the Trinamic controller.
Use flags to test specific functions.

Usage:
  python motor_control_cli.py --port COM3 --move 1000
  python motor_control_cli.py --port COM3 --stop
  python motor_control_cli.py --port COM3 --set-current 50
  python motor_control_cli.py --port COM3 --apply-config
  python motor_control_cli.py --port COM3 --motor 0 --home (only works for shutter motor)
"""

import sys
import time
import os
import argparse

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.motor_control import MotorControl
from src.config_manager import ConfigManager
from src.logger import logger, LogLevel


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Control Trinamic motor functions')
    
    # Connection parameters
    parser.add_argument('--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baudrate (default: 9600)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Motor selection
    parser.add_argument('--motor', type=int, default=1, help='Motor number (0=shutter, 1=film)')
    
    # Configuration commands
    config_group = parser.add_argument_group('Configuration Commands')
    config_group.add_argument('--config-file', help='Path to configuration file (default: find automatically)')
    config_group.add_argument('--apply-config', action='store_true', help='Apply configuration from INI file to motors')
    config_group.add_argument('--show-config', action='store_true', help='Show current configuration')
    
    # Movement commands
    move_group = parser.add_argument_group('Movement Commands')
    move_group.add_argument('--move', type=int, metavar='STEPS', help='Move motor specified number of steps')
    move_group.add_argument('--direction', type=int, choices=[-1, 1], default=1, 
                          help='Movement direction (1=forward, -1=backward)')
    move_group.add_argument('--stop', action='store_true', help='Stop the motor')
    move_group.add_argument('--home', action='store_true', 
                          help='Move shutter motor (0) to home position - only valid for motor 0')
    move_group.add_argument('--wait', action='store_true', 
                          help='Wait for motor to stop after movement command')
    
    # Motor parameters
    param_group = parser.add_argument_group('Motor Parameters')
    param_group.add_argument('--set-resolution', type=int, metavar='RES', 
                           help='Set motor resolution (1, 2, 4, 8, 16)')
    param_group.add_argument('--set-speed', type=int, metavar='SPEED', 
                           help='Set target speed')
    param_group.add_argument('--set-current', type=int, metavar='CURRENT', 
                           help='Set maximum current (0-100)')
    param_group.add_argument('--set-standby-current', type=int, metavar='CURRENT', 
                           help='Set standby current (0-100)')
    param_group.add_argument('--set-acceleration', type=int, metavar='ACCEL', 
                           help='Set acceleration (0-100)')
    
    # Status commands
    status_group = parser.add_argument_group('Status Commands')
    status_group.add_argument('--is-running', action='store_true', 
                            help='Check if motor is running')
    status_group.add_argument('--reset', action='store_true', 
                            help='Reset the controller')
    
    args = parser.parse_args()
    
    # Set logger level based on debug flag
    logger.min_level = LogLevel.DEBUG if args.debug else LogLevel.INFO
    
    # Log script startup
    logger.info("SCRIPT", f"Motor Control CLI starting on port {args.port}")
    
    # Create and connect to controller
    controller = TrinamicController(port=args.port, baudrate=args.baudrate)
    
    try:
        logger.info("SCRIPT", f"Connecting to Trinamic controller on {args.port}...")
        controller.connect()
        logger.info("SCRIPT", "Connection established")
        
        # Create motor control interface
        motor = MotorControl(controller)
        
        # Create configuration manager
        config_manager = ConfigManager(args.config_file)
        
        # Process commands
        motor_num = args.motor
        logger.info("MOTOR", f"Using motor {motor_num} (0=shutter, 1=film)")
        
        # Configuration commands
        if args.show_config:
            logger.info("CONFIG", "Current configuration:")
            
            if motor_num == 0:  # Shutter motor
                config = config_manager.get_shutter_config()
                logger.info("CONFIG", "Shutter motor (0) configuration:")
                for key, value in config.items():
                    logger.info("CONFIG", f"  {key}: {value}")
            else:  # Film motor
                config = config_manager.get_film_config()
                logger.info("CONFIG", "Film motor (1) configuration:")
                for key, value in config.items():
                    logger.info("CONFIG", f"  {key}: {value}")
                    
            system_config = config_manager.get_system_config()
            logger.info("CONFIG", "System configuration:")
            for key, value in system_config.items():
                logger.info("CONFIG", f"  {key}: {value}")
                
        if args.apply_config:
            logger.info("CONFIG", "Applying configuration from INI file...")
            try:
                config_manager.apply_motor_config(motor)
                logger.info("CONFIG", "Configuration applied successfully")
            except Exception as e:
                logger.error("CONFIG", f"Error applying configuration: {e}")
        
        # Motor parameters
        if args.set_resolution is not None:
            logger.info("MOTOR", f"Setting motor {motor_num} resolution to {args.set_resolution}...")
            result = motor.set_motor_resolution(motor_num, args.set_resolution)
            logger.info("MOTOR", f"Resolution set command result: {result}")
            
        if args.set_speed is not None:
            logger.info("MOTOR", f"Setting motor {motor_num} speed to {args.set_speed}...")
            result = motor.set_target_speed(motor_num, args.set_speed)
            logger.info("MOTOR", f"Speed set command result: {result}")
            
        if args.set_current is not None:
            logger.info("MOTOR", f"Setting motor {motor_num} current to {args.set_current}...")
            result = motor.set_max_current(motor_num, args.set_current)
            logger.info("MOTOR", f"Current set command result: {result}")
            
        if args.set_standby_current is not None:
            logger.info("MOTOR", f"Setting motor {motor_num} standby current to {args.set_standby_current}...")
            result = motor.set_standby_current(motor_num, args.set_standby_current)
            logger.info("MOTOR", f"Standby current set command result: {result}")
            
        if args.set_acceleration is not None:
            logger.info("MOTOR", f"Setting motor {motor_num} acceleration to {args.set_acceleration}...")
            result = motor.set_max_acceleration(motor_num, args.set_acceleration)
            logger.info("MOTOR", f"Acceleration set command result: {result}")
            
        # Movement commands
        if args.move is not None:
            steps = args.move
            direction = args.direction
            logger.info("MOTOR", f"Moving motor {motor_num} {steps} steps {'forward' if direction > 0 else 'backward'}...")
            result = motor.move_motor(motor_num, steps * direction)
            logger.info("MOTOR", f"Move command result: {result}")
            
            if args.wait:
                logger.info("MOTOR", "Waiting for motor to stop...")
                i = 0
                while motor.is_motor_running(motor_num):
                    if i % 4 == 0:  # Don't spam too many log messages
                        logger.debug("MOTOR", "Motor still running...")
                    i += 1
                    time.sleep(0.5)
                logger.info("MOTOR", "Motor stopped")
                
        if args.stop:
            logger.info("MOTOR", f"Stopping motor {motor_num}...")
            result = motor.stop_motor(motor_num)
            logger.info("MOTOR", f"Stop command result: {result}")
            
        if args.home:
            # Check if the right motor is selected for home command
            if motor_num != 0:
                logger.error("MOTOR", "Home position is only available for the shutter motor (motor 0)")
                logger.info("MOTOR", "Please use --motor 0 with the --home command")
            else:
                logger.info("MOTOR", "Moving shutter motor to home position...")
                try:
                    result = motor.move_to_home_position(0)  # Always use 0 for shutter motor
                    logger.info("MOTOR", f"Home command result: {result}")
                except Exception as e:
                    logger.error("MOTOR", f"Error moving to home position: {e}")
            
        # Status commands
        if args.is_running:
            logger.info("MOTOR", f"Checking if motor {motor_num} is running...")
            try:
                status = motor.is_motor_running(motor_num)
                logger.info("MOTOR", f"Motor {motor_num} status: {'Running' if status else 'Stopped'}")
            except Exception as e:
                logger.error("MOTOR", f"Error checking motor status: {e}")
            
        if args.reset:
            logger.info("CONTROLLER", "Resetting controller...")
            try:
                result = motor.reset_controller()
                logger.info("CONTROLLER", f"Reset command result: {result}")
            except Exception as e:
                logger.error("CONTROLLER", f"Error resetting controller: {e}")
            
        # If no specific command was given, show help
        if not any([args.move is not None, args.stop, args.home, 
                   args.set_resolution is not None, args.set_speed is not None,
                   args.set_current is not None, args.set_standby_current is not None,
                   args.set_acceleration is not None, args.is_running, args.reset,
                   args.show_config, args.apply_config]):
            parser.print_help()
            
    except Exception as e:
        logger.error("SCRIPT", f"Unhandled error: {e}")
        # Emergency stop in case of error
        try:
            logger.warn("MOTOR", f"Emergency stop of motor {args.motor}")
            motor.stop_motor(args.motor)
        except:
            pass
            
    finally:
        # Always close the serial connection
        logger.info("SCRIPT", "Closing connection and exiting")
        controller.disconnect()


if __name__ == "__main__":
    main() 