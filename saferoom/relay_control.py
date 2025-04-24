#!/usr/bin/env python3
"""
ESP32 Relay Controller - Python Client
This script controls relays connected to an ESP32 via serial commands
"""

import serial
import time
import argparse
import os
import atexit

# Global controller instance for persistent connection
_controller = None

class RelayController:
    """Controls relays connected to an ESP32 via serial communication"""
    
    def __init__(self, port, baudrate=115200, timeout=1, reset_delay=0.0):
        """Initialize the serial connection to the ESP32"""
        conn_start = time.time()
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        conn_time = (time.time() - conn_start) * 1000
        
        if reset_delay > 0:
            time.sleep(reset_delay)  # Wait for ESP32 to reset after serial connection
        
        self.flush_input()
    
    def flush_input(self):
        """Clear any pending input"""
        self.ser.reset_input_buffer()
    
    def send_command(self, command):
        """Send a command to the ESP32 and return the response"""
        self.flush_input()
        start_time = time.time()
        self.ser.write(f"{command}\n".encode())
        time.sleep(0.05)  # Reduced wait time
        
        # Read the response
        response = ""
        while self.ser.in_waiting > 0:
            response += self.ser.readline().decode('utf-8')
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return response.strip()
    
    def relay_on(self, relay_num):
        """Turn on a specific relay"""
        return self.send_command(f"ON:{relay_num}")
    
    def relay_off(self, relay_num):
        """Turn off a specific relay"""
        return self.send_command(f"OFF:{relay_num}")
    
    def pulse_relay(self, relay_num):
        """Send a pulse to a specific relay"""
        return self.send_command(f"PULSE:{relay_num}")
    
    def get_status(self):
        """Get the status of all relays"""
        return self.send_command("STATUS")
    
    def close(self):
        """Close the serial connection"""
        self.ser.close()

def get_controller(port, reset_delay=0.0):
    """Get or create a global controller instance"""
    global _controller
    if _controller is None:
        _controller = RelayController(port, reset_delay=reset_delay)
        # Register cleanup function
        atexit.register(lambda: _controller.close() if _controller is not None else None)
    return _controller

def run_command(args):
    """Execute the command based on arguments"""
    # Use global controller if persistent, otherwise create new one
    if args.persistent:
        controller = get_controller(args.port, reset_delay=args.reset_delay)
    else:
        controller = RelayController(args.port, reset_delay=args.reset_delay)
    
    try:
        # Execute the requested command
        if args.command == 'on':
            result = controller.relay_on(args.relay)
        elif args.command == 'off':
            result = controller.relay_off(args.relay)
        elif args.command == 'pulse':
            result = controller.pulse_relay(args.relay)
        elif args.command == 'status':
            result = controller.get_status()
        
        print(result)
        
    except serial.SerialException as e:
        print(f"Error: {e}")
        return 1
    finally:
        if not args.persistent and 'controller' in locals():
            controller.close()
    
    return 0

if __name__ == "__main__":
    # Start timing the execution
    script_start_time = time.time()
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Control ESP32 Relays via Serial')
    parser.add_argument('--port', required=True, help='Serial port (e.g., /dev/ttyUSB0 or COM3)')
    parser.add_argument('--command', choices=['on', 'off', 'pulse', 'status'], 
                        required=True, help='Command to send')
    parser.add_argument('--relay', type=int, choices=range(1, 9), 
                        help='Relay number (1-8, required for on/off/pulse commands)')
    parser.add_argument('--reset-delay', type=float, default=0.0,
                        help='Delay in seconds to wait for ESP32 to reset (default: 0.0)')
    parser.add_argument('--persistent', action='store_true',
                        help='Use persistent connection (faster for multiple commands)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.command in ['on', 'off', 'pulse'] and args.relay is None:
        parser.error(f"--relay is required for the {args.command} command")
    
    # Run the command
    exit_code = run_command(args)
    
    # Calculate and display total execution time
    script_end_time = time.time()
    total_time = (script_end_time - script_start_time) * 1000  # Convert to milliseconds
    print(f"\nTotal execution time: {total_time:.2f} ms")
    
    exit(exit_code)

# Examples of usage:
# To turn on relay 1:
#   python serial_relay_control.py --port COM7 --command on --relay 1
#
# To turn off relay 2:
#   python serial_relay_control.py --port COM7 --command off --relay 2
#
# For faster operation (keeps connection open between runs):
#   python serial_relay_control.py --port COM7 --command status --persistent