"""
I/O Control CLI Tool

Command-line tool for controlling individual I/O functions of the Trinamic controller.
Use flags to test specific functions.

Usage:
  python io_control_cli.py --port COM3 --led-on
  python io_control_cli.py --port COM3 --vacuum-off
  python io_control_cli.py --port COM3 --check-status
  python io_control_cli.py --port COM3 --check-machine-state
  python io_control_cli.py --port COM3 --check-vacuum --debug
  python io_control_cli.py --port COM3 --check-vacuum --json
"""

import sys
import time
import os
import argparse
import json

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
    parser.add_argument('--debug', action='store_true', help='Enable debug logging and verbose output')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
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
    
    # Log script startup (only if debugging)
    if args.debug and not args.json:
        logger.info("SCRIPT", f"IO Control CLI starting on port {args.port}")
    
    # Create and connect to controller - enable verbose mode only when debugging
    controller = TrinamicController(port=args.port, baudrate=args.baudrate, verbose=args.debug and not args.json)
    
    try:
        if args.debug and not args.json:
            logger.info("SCRIPT", f"Connecting to Trinamic controller on {args.port}...")
        controller.connect()
        if args.debug and not args.json:
            logger.info("SCRIPT", "Connection established")
        
        # Create I/O control interface
        io = IOControl(controller)
        
        # Process commands
        
        # LED control
        if args.led_on:
            if args.debug and not args.json:
                logger.info("LED", "Turning LED on...")
            result = io.led_on()
            if args.debug and not args.json:
                logger.info("LED", f"LED on command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "led_on",
                    "message": "LED turned on" if result else "Failed to turn on LED"
                }))
            else:
                if result:
                    print("LED turned on")
                else:
                    print("Failed to turn on LED")
            
        if args.led_off:
            if args.debug and not args.json:
                logger.info("LED", "Turning LED off...")
            result = io.led_off()
            if args.debug and not args.json:
                logger.info("LED", f"LED off command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "led_off",
                    "message": "LED turned off" if result else "Failed to turn off LED"
                }))
            else:
                if result:
                    print("LED turned off")
                else:
                    print("Failed to turn off LED")
            
        # Vacuum control
        if args.vacuum_on:
            if args.debug and not args.json:
                logger.info("VACUUM", "Turning vacuum on...")
            result = io.vacuum_on()
            if args.debug and not args.json:
                logger.info("VACUUM", f"Vacuum on command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "vacuum_on",
                    "message": "Vacuum turned on" if result else "Failed to turn on vacuum"
                }))
            else:
                if result:
                    print("Vacuum turned on")
                else:
                    print("Failed to turn on vacuum")
            
        if args.vacuum_off:
            if args.debug and not args.json:
                logger.info("VACUUM", "Turning vacuum off...")
            result = io.vacuum_off()
            if args.debug and not args.json:
                logger.info("VACUUM", f"Vacuum off command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "vacuum_off",
                    "message": "Vacuum turned off" if result else "Failed to turn off vacuum"
                }))
            else:
                if result:
                    print("Vacuum turned off")
                else:
                    print("Failed to turn off vacuum")
            
        if args.check_vacuum:
            if args.debug and not args.json:
                logger.info("VACUUM", "Checking vacuum status...")
            try:
                status = io.is_vacuum_ok()
                if args.debug and not args.json:
                    logger.info("VACUUM", f"Vacuum status: {'OK' if status else 'Not OK'}")
                elif args.json:
                    print(json.dumps({
                        "success": True,
                        "action": "check_vacuum",
                        "vacuum_ok": status,
                        "vacuum_status": "OK" if status else "Not OK"
                    }))
                else:
                    print(f"Vacuum status: {'OK' if status else 'Not OK'}")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("VACUUM", f"Error checking vacuum status: {e}")
                elif args.json:
                    print(json.dumps({
                        "success": False,
                        "action": "check_vacuum",
                        "error": str(e)
                    }))
                else:
                    print(f"Error checking vacuum status: {e}")
            
        # Magnet control
        if args.magnet_on:
            if args.debug and not args.json:
                logger.info("MAGNET", "Turning magnet on...")
            result = io.magnet_on()
            if args.debug and not args.json:
                logger.info("MAGNET", f"Magnet on command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "magnet_on",
                    "message": "Magnet turned on" if result else "Failed to turn on magnet"
                }))
            else:
                if result:
                    print("Magnet turned on")
                else:
                    print("Failed to turn on magnet")
            
        if args.magnet_off:
            if args.debug and not args.json:
                logger.info("MAGNET", "Turning magnet off...")
            result = io.magnet_off()
            if args.debug and not args.json:
                logger.info("MAGNET", f"Magnet off command result: {result}")
            elif args.json:
                print(json.dumps({
                    "success": result,
                    "action": "magnet_off",
                    "message": "Magnet turned off" if result else "Failed to turn off magnet"
                }))
            else:
                if result:
                    print("Magnet turned off")
                else:
                    print("Failed to turn off magnet")
            
        # Status checks
        if args.check_status or args.check_lid:
            if args.debug and not args.json:
                logger.info("STATUS", "Checking lid status (based on supply voltage)...")
            try:
                status = io.is_supply_voltage_ok()
                # Direct supply voltage check for lid status
                if args.debug and not args.json:
                    logger.info("STATUS", f"Lid status: {'Closed' if status else 'Open'}")
                elif args.json and args.check_lid:
                    print(json.dumps({
                        "success": True,
                        "action": "check_lid",
                        "lid_closed": status,
                        "lid_status": "Closed" if status else "Open"
                    }))
                elif not args.json:
                    print(f"Lid status: {'Closed' if status else 'Open'}")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("STATUS", f"Error checking lid status: {e}")
                elif args.json and args.check_lid:
                    print(json.dumps({
                        "success": False,
                        "action": "check_lid",
                        "error": str(e)
                    }))
                elif not args.json:
                    print(f"Error checking lid status: {e}")
            
        if args.check_status or args.check_zero_point:
            if args.debug and not args.json:
                logger.info("STATUS", "Checking zero point status...")
            try:
                status = io.is_at_zero_point()
                if args.debug and not args.json:
                    logger.info("STATUS", f"Zero point status: {'At zero point' if status else 'Not at zero point'}")
                elif args.json and args.check_zero_point:
                    print(json.dumps({
                        "success": True,
                        "action": "check_zero_point",
                        "at_zero_point": status,
                        "zero_point_status": "At zero point" if status else "Not at zero point"
                    }))
                elif not args.json:
                    print(f"Zero point status: {'At zero point' if status else 'Not at zero point'}")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("STATUS", f"Error checking zero point status: {e}")
                elif args.json and args.check_zero_point:
                    print(json.dumps({
                        "success": False,
                        "action": "check_zero_point",
                        "error": str(e)
                    }))
                elif not args.json:
                    print(f"Error checking zero point status: {e}")
            
        if args.check_status or args.check_voltage:
            if args.debug and not args.json:
                logger.info("STATUS", "Checking supply voltage...")
            try:
                status = io.is_supply_voltage_ok()
                # Get the raw voltage value for more detailed information
                raw_voltage = controller.send_command(15, 8, 1, 0)
                if args.debug and not args.json:
                    logger.info("STATUS", f"Supply voltage: {raw_voltage} ({'OK (Lid closed)' if status else 'Low (Lid open)'})")
                elif args.json and args.check_voltage:
                    print(json.dumps({
                        "success": True,
                        "action": "check_voltage",
                        "voltage": raw_voltage,
                        "voltage_ok": status,
                        "voltage_status": "OK (Lid closed)" if status else "Low (Lid open)"
                    }))
                elif not args.json:
                    print(f"Supply voltage: {raw_voltage} ({'OK (Lid closed)' if status else 'Low (Lid open)'})")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("STATUS", f"Error checking supply voltage: {e}")
                elif args.json and args.check_voltage:
                    print(json.dumps({
                        "success": False,
                        "action": "check_voltage",
                        "error": str(e)
                    }))
                elif not args.json:
                    print(f"Error checking supply voltage: {e}")
        
        if args.check_status or args.check_machine_state:
            if args.debug and not args.json:
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
                
                if args.debug and not args.json:
                    logger.info("STATUS", f"Machine state: {state} - {state_desc}")
                    logger.info("STATUS", f"Raw voltage: {raw_voltage}")
                elif args.json and args.check_machine_state:
                    print(json.dumps({
                        "success": True,
                        "action": "check_machine_state",
                        "machine_state": str(state),
                        "state_description": state_desc,
                        "raw_voltage": raw_voltage
                    }))
                elif not args.json:
                    print(f"Machine state: {state} - {state_desc}")
                    print(f"Raw voltage: {raw_voltage}")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("STATUS", f"Error determining machine state: {e}")
                elif args.json and args.check_machine_state:
                    print(json.dumps({
                        "success": False,
                        "action": "check_machine_state",
                        "error": str(e)
                    }))
                elif not args.json:
                    print(f"Error determining machine state: {e}")
            
        if args.check_status or args.light_sensor:
            if args.debug and not args.json:
                logger.info("SENSOR", "Reading light sensor...")
            try:
                value = io.get_light_sensor()
                if args.debug and not args.json:
                    logger.info("SENSOR", f"Light sensor value: {value}")
                elif args.json and args.light_sensor:
                    print(json.dumps({
                        "success": True,
                        "action": "light_sensor",
                        "light_sensor_value": value
                    }))
                elif not args.json:
                    print(f"Light sensor value: {value}")
            except Exception as e:
                if args.debug and not args.json:
                    logger.error("SENSOR", f"Error reading light sensor: {e}")
                elif args.json and args.light_sensor:
                    print(json.dumps({
                        "success": False,
                        "action": "light_sensor",
                        "error": str(e)
                    }))
                elif not args.json:
                    print(f"Error reading light sensor: {e}")
            
        # If no specific command was given, show help
        if not any([args.led_on, args.led_off, args.vacuum_on, args.vacuum_off, 
                   args.check_vacuum, args.magnet_on, args.magnet_off, 
                   args.check_status, args.check_lid, args.check_zero_point, 
                   args.check_voltage, args.light_sensor, args.check_machine_state]):
            parser.print_help()
            
    except Exception as e:
        if args.debug and not args.json:
            logger.error("SCRIPT", f"Unhandled error: {e}")
        elif args.json:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
        else:
            print(f"Error: {e}")
            
    finally:
        # Always close the serial connection
        if args.debug and not args.json:
            logger.info("SCRIPT", "Closing connection and exiting")
        controller.disconnect()


if __name__ == "__main__":
    main() 