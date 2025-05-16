"""
I/O Control CLI Tool

Command-line tool for controlling individual I/O functions of the Trinamic controller.
Use flags to test specific functions.

Usage:
  python io_control_cli.py --port COM3 --led-on
  python io_control_cli.py --port COM3 --vacuum-off
  python io_control_cli.py --port COM3 --check-status
  python io_control_cli.py --port COM3 --check-machine-state
"""

import sys
import time
import os
import argparse

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.io_control import IOControl, MachineState
from src.logger import logger, LogLevel


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Control Trinamic I/O functions')
    
    # Connection parameters
    parser.add_argument('--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baudrate (default: 9600)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # LED control
    led_group = parser.add_argument_group('LED Control')
    led_group.add_argument('--led-on', action='store_true', help='Turn LED on') # GOOD
    led_group.add_argument('--led-off', action='store_true', help='Turn LED off') # GOOD
    
    # Vacuum control
    vacuum_group = parser.add_argument_group('Vacuum Control')
    vacuum_group.add_argument('--vacuum-on', action='store_true', help='Turn vacuum on') # GOOD
    vacuum_group.add_argument('--vacuum-off', action='store_true', help='Turn vacuum off') # GOOD
    vacuum_group.add_argument('--check-vacuum', action='store_true', help='Check vacuum status') # GOOD
    
    # Magnet control
    magnet_group = parser.add_argument_group('Magnet Control')
    magnet_group.add_argument('--magnet-on', action='store_true', help='Turn magnet on') # GOOD
    magnet_group.add_argument('--magnet-off', action='store_true', help='Turn magnet off') # GOOD
    
    # Status checks
    status_group = parser.add_argument_group('Status Checks')
    status_group.add_argument('--check-status', action='store_true', help='Check all status indicators')
    status_group.add_argument('--check-lid', action='store_true', help='Check if lid is closed (based on supply voltage)') # GOOD
    status_group.add_argument('--check-zero-point', action='store_true', help='Check if at zero point') # GOOD
    status_group.add_argument('--check-voltage', action='store_true', help='Check supply voltage and lid status') # GOOD
    status_group.add_argument('--light-sensor', action='store_true', help='Read light sensor value') # GOOD
    status_group.add_argument('--check-machine-state', action='store_true', help='Determine complete machine state (ON/LID_OPEN/OFF)') # GOOD
    
    args = parser.parse_args()
    
    # Set logger level based on debug flag
    logger.min_level = LogLevel.DEBUG if args.debug else LogLevel.INFO
    
    # Log script startup
    logger.info("SCRIPT", f"IO Control CLI starting on port {args.port}")
    
    # Create and connect to controller
    controller = TrinamicController(port=args.port, baudrate=args.baudrate)
    
    try:
        logger.info("SCRIPT", f"Connecting to Trinamic controller on {args.port}...")
        controller.connect()
        logger.info("SCRIPT", "Connection established")
        
        # Create I/O control interface
        io = IOControl(controller)
        
        # Process commands
        
        # LED control
        if args.led_on:
            logger.info("LED", "Turning LED on...")
            result = io.led_on()
            logger.info("LED", f"LED on command result: {result}")
            
        if args.led_off:
            logger.info("LED", "Turning LED off...")
            result = io.led_off()
            logger.info("LED", f"LED off command result: {result}")
            
        # Vacuum control
        if args.vacuum_on:
            logger.info("VACUUM", "Turning vacuum on...")
            result = io.vacuum_on()
            logger.info("VACUUM", f"Vacuum on command result: {result}")
            
        if args.vacuum_off:
            logger.info("VACUUM", "Turning vacuum off...")
            result = io.vacuum_off()
            logger.info("VACUUM", f"Vacuum off command result: {result}")
            
        if args.check_vacuum:
            logger.info("VACUUM", "Checking vacuum status...")
            try:
                status = io.is_vacuum_ok()
                logger.info("VACUUM", f"Vacuum status: {'OK' if status else 'Not OK'}")
            except Exception as e:
                logger.error("VACUUM", f"Error checking vacuum status: {e}")
            
        # Magnet control
        if args.magnet_on:
            logger.info("MAGNET", "Turning magnet on...")
            result = io.magnet_on()
            logger.info("MAGNET", f"Magnet on command result: {result}")
            
        if args.magnet_off:
            logger.info("MAGNET", "Turning magnet off...")
            result = io.magnet_off()
            logger.info("MAGNET", f"Magnet off command result: {result}")
            
        # Status checks
        if args.check_status or args.check_lid:
            logger.info("STATUS", "Checking lid status (based on supply voltage)...")
            try:
                status = io.is_supply_voltage_ok()
                # Direct supply voltage check for lid status
                logger.info("STATUS", f"Lid status: {'Closed' if status else 'Open'}")
            except Exception as e:
                logger.error("STATUS", f"Error checking lid status: {e}")
            
        if args.check_status or args.check_zero_point:
            logger.info("STATUS", "Checking zero point status...")
            try:
                status = io.is_at_zero_point()
                logger.info("STATUS", f"Zero point status: {'At zero point' if status else 'Not at zero point'}")
            except Exception as e:
                logger.error("STATUS", f"Error checking zero point status: {e}")
            
        if args.check_status or args.check_voltage:
            logger.info("STATUS", "Checking supply voltage...")
            try:
                status = io.is_supply_voltage_ok()
                # Get the raw voltage value for more detailed information
                raw_voltage = controller.send_command(15, 8, 1, 0)
                logger.info("STATUS", f"Supply voltage: {raw_voltage} ({'OK (Lid closed)' if status else 'Low (Lid open)'})")
            except Exception as e:
                logger.error("STATUS", f"Error checking supply voltage: {e}")
        
        if args.check_status or args.check_machine_state:
            logger.info("STATUS", "Determining complete machine state...")
            try:
                state = io.get_machine_state()
                raw_voltage = controller.send_command(15, 8, 1, 0)
                
                if state == MachineState.ON:
                    state_desc = "ON (Lid closed)"
                elif state == MachineState.LID_OPEN:
                    state_desc = "ON (Lid open)"
                elif state == MachineState.OFF:
                    state_desc = "OFF"
                else:
                    state_desc = "UNKNOWN"
                
                logger.info("STATUS", f"Machine state: {state} - {state_desc}")
                logger.info("STATUS", f"Raw voltage: {raw_voltage}")
            except Exception as e:
                logger.error("STATUS", f"Error determining machine state: {e}")
            
        if args.check_status or args.light_sensor:
            logger.info("SENSOR", "Reading light sensor...")
            try:
                value = io.get_light_sensor()
                logger.info("SENSOR", f"Light sensor value: {value}")
            except Exception as e:
                logger.error("SENSOR", f"Error reading light sensor: {e}")
            
        # If no specific command was given, show help
        if not any([args.led_on, args.led_off, args.vacuum_on, args.vacuum_off, 
                   args.check_vacuum, args.magnet_on, args.magnet_off, 
                   args.check_status, args.check_lid, args.check_zero_point, 
                   args.check_voltage, args.light_sensor, args.check_machine_state]):
            parser.print_help()
            
    except Exception as e:
        logger.error("SCRIPT", f"Unhandled error: {e}")
            
    finally:
        # Always close the serial connection
        logger.info("SCRIPT", "Closing connection and exiting")
        controller.disconnect()


if __name__ == "__main__":
    main() 