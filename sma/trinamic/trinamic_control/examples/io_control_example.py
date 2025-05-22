"""
I/O Control Example

Demonstrates how to use the Trinamic controller to control I/O functions
"""

import sys
import time
import os

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.io_control import IOControl


def main():
    # Create and connect to controller
    controller = TrinamicController(port='COM3', baudrate=9600)
    
    try:
        print("Connecting to Trinamic controller...")
        controller.connect()
        
        # Create I/O control interface
        io = IOControl(controller)
        
        # Check system status
        print("Checking system status...")
        print(f"Lid closed: {io.is_lid_closed()}")
        print(f"At zero point: {io.is_at_zero_point()}")
        print(f"Supply voltage OK: {io.is_supply_voltage_ok()}")
        print(f"Light sensor value: {io.get_light_sensor()}")
        
        # Control LED
        print("Turning LED on...")
        io.led_on()
        time.sleep(2)
        
        print("Turning LED off...")
        io.led_off()
        time.sleep(1)
        
        # Control vacuum if available
        print("Turning vacuum on...")
        io.vacuum_on()
        time.sleep(2)
        
        print("Checking vacuum status...")
        print(f"Vacuum OK: {io.is_vacuum_ok()}")
        time.sleep(1)
        
        print("Turning vacuum off...")
        io.vacuum_off()
        time.sleep(1)
        
        # Control magnet if available
        print("Turning magnet on...")
        io.magnet_on()
        time.sleep(2)
        
        print("Turning magnet off...")
        io.magnet_off()
        
    except Exception as e:
        print(f"Error: {e}")
            
    finally:
        # Always close the serial connection
        controller.disconnect()
        print("Connection closed")


if __name__ == "__main__":
    main() 