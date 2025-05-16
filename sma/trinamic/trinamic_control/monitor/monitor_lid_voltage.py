#!/usr/bin/env python
"""
Simple Lid Status and Supply Voltage Monitor

This script continuously monitors the supply voltage and shows the actual lid status,
printing each numbered reading on a new line to track the gradual changes over time.
"""

import sys
import time
import os
import datetime

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.logger import LogLevel, logger

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def get_voltage_color(voltage):
    """Return color code based on voltage level"""
    if voltage > 50000:
        return Colors.GREEN
    elif voltage < 6000:
        return Colors.RED
    else:
        return Colors.YELLOW

def main():
    port = 'COM3'  # Default port, change if needed
    
    # Get port from command line argument if provided
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    # Completely disable all logging - set level higher than any defined log level
    logger.min_level = LogLevel.ERROR
    
    # Redirect stdout and stderr for the controller
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    null_stream = open(os.devnull, 'w')
    
    # Define voltage threshold for lid status
    SUPPLY_VOLTAGE_THRESHOLD = 10000
    
    print(f"{Colors.BOLD}Supply Voltage and Lid Status Monitor{Colors.RESET}")
    print(f"Port: {port} | Polling every 100ms | Lid threshold: {SUPPLY_VOLTAGE_THRESHOLD} | Press Ctrl+C to exit")
    print("-" * 80)
    
    # Create controller instance
    controller = TrinamicController(port=port)
    
    try:
        # Connect to controller
        controller.connect()
        
        # Main monitoring loop
        count = 1
        while True:
            # Temporarily redirect all output
            sys.stdout = null_stream
            sys.stderr = null_stream
            
            # Get raw values directly
            voltage = controller.send_command(15, 8, 1, 0)
            
            # Restore output for our display
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # Determine lid status based on voltage
            lid_status = "CLOSED" if voltage > SUPPLY_VOLTAGE_THRESHOLD else "OPEN"
            
            # Get colors
            voltage_color = get_voltage_color(voltage)
            lid_color = Colors.GREEN if lid_status == "CLOSED" else Colors.RED
            
            # Print each reading on a new line with timestamp and counter
            timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{count:4d} | {timestamp} | Lid: {lid_color}{lid_status}{Colors.RESET} | Voltage: {voltage_color}{voltage}{Colors.RESET}")
            
            # Increment counter
            count += 1
            
            # Wait before checking again
            time.sleep(0.1)  # Poll every 100ms
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Restore output streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Close connection
        controller.disconnect()

if __name__ == "__main__":
    main() 