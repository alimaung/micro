"""
Basic Movement Example

Demonstrates how to use the Trinamic controller to move motors
"""

import sys
import time
import os

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.motor_control import MotorControl


def main():
    # Create and connect to controller
    controller = TrinamicController(port='COM3', baudrate=9600)
    
    try:
        print("Connecting to Trinamic controller...")
        controller.connect()
        
        # Create motor control interface
        motor = MotorControl(controller)
        
        # Configure motor 1 (film motor)
        film_motor = 1
        print("Configuring film motor...")
        motor.set_motor_resolution(film_motor, 4)  # 1/4 microstepping
        motor.set_max_current(film_motor, 50)      # 50% current
        motor.set_standby_current(film_motor, 10)  # 10% standby current
        motor.set_max_acceleration(film_motor, 50) # 50% acceleration
        
        # Move motor
        print("Moving film motor 1000 steps forward...")
        motor.move_motor(film_motor, 1000)
        
        # Wait for motor to stop
        while motor.is_motor_running(film_motor):
            print("Motor is running...")
            time.sleep(0.5)
            
        print("Motor stopped")
        
        # Wait a moment
        time.sleep(2)
        
        # Move motor back
        print("Moving film motor 1000 steps backward...")
        motor.move_motor(film_motor, -1000)
        
        # Wait for motor to stop
        while motor.is_motor_running(film_motor):
            print("Motor is running...")
            time.sleep(0.5)
            
        print("Motor stopped")
        
    except Exception as e:
        print(f"Error: {e}")
        # Emergency stop in case of error
        try:
            motor.stop_motor(film_motor)
        except:
            pass
            
    finally:
        # Always close the serial connection
        controller.disconnect()
        print("Connection closed")


if __name__ == "__main__":
    main() 