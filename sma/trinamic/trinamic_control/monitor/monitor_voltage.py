#!/usr/bin/env python
"""
Supply Voltage Monitor

This script continuously monitors the supply voltage from the Trinamic controller
and displays only the current voltage value, making it easier to observe changes
when opening/closing the lid.
"""

import sys
import time
import os
import subprocess
import re

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def clear_line():
    """Clear the current line in the terminal"""
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

def main():
    # Add directory to path to ensure we can find the IO control CLI
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Regular expression to extract voltage value
    voltage_pattern = re.compile(r'Supply voltage raw result: (\d+)')
    
    print(f"{Colors.BOLD}Supply Voltage Monitor{Colors.RESET}")
    print("Press Ctrl+C to exit")
    print("-" * 60)
    
    try:
        while True:
            # Run the IO control CLI with voltage check
            cmd = [sys.executable, os.path.join(script_dir, 'io_control_cli.py'), '--debug', '--check-voltage']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Extract the voltage value from the output
            match = voltage_pattern.search(result.stdout)
            if match:
                voltage = int(match.group(1))
                
                # Determine color based on voltage level
                if voltage > 50000:
                    color = Colors.GREEN
                    status = "CLOSED"
                elif voltage < 6000:
                    color = Colors.RED
                    status = "OPEN"
                else:
                    color = Colors.YELLOW
                    status = "TRANSITION"
                
                # Print voltage with timestamp and clear the line for the next update
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                clear_line()
                sys.stdout.write(f"{timestamp} - Voltage: {color}{voltage}{Colors.RESET} - Lid: {color}{status}{Colors.RESET}")
                sys.stdout.flush()
            
            # Wait before checking again (adjust as needed)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

if __name__ == "__main__":
    main() 