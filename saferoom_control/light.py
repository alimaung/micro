#!/usr/bin/env python3
"""
Simplified Lighting Control Script
Usage: py light.py m light/dark
"""

import sys
import time
from serial_relay_control import get_controller

# Default configuration
DEFAULT_PORT = "COM7"
DEFAULT_RESET_DELAY = 0.0

def set_dark_mode(controller):
    """Set relays to dark mode configuration"""
    print("Setting DARK mode...")
    controller.pulse_relay(1)  # Pulse relay 1
    controller.relay_on(2)     # Turn on relay 2
    controller.relay_on(3)     # Turn on relay 3
    controller.relay_on(4)     # Turn on relay 4
    return "DARK mode activated"

def set_light_mode(controller):
    """Set relays to light mode configuration"""
    print("Setting LIGHT mode...")
    controller.pulse_relay(1)  # Pulse relay 1
    controller.relay_off(2)    # Turn off relay 2
    controller.relay_off(3)    # Turn off relay 3
    controller.relay_off(4)    # Turn off relay 4
    return "LIGHT mode activated"

def print_usage():
    """Print usage instructions"""
    print("Usage: py light.py m light/dark")
    print("       py light.py t [interval]  # Toggle mode with optional interval in seconds")
    sys.exit(1)

def main():
    # Get controller with persistent connection
    start_time = time.time()
    controller = get_controller(DEFAULT_PORT, reset_delay=DEFAULT_RESET_DELAY)
    
    # Parse simplified command line arguments
    if len(sys.argv) < 2:
        print_usage()
    
    cmd = sys.argv[1].lower()
    
    try:
        # Mode command (m light or m dark)
        if cmd == "m" and len(sys.argv) > 2:
            mode = sys.argv[2].lower()
            if mode == "light":
                result = set_light_mode(controller)
            elif mode == "dark":
                result = set_dark_mode(controller)
            else:
                print(f"Unknown mode: {mode}")
                print_usage()
            print(result)
            
        # Toggle command (t or t [interval])
        elif cmd == "t":
            interval = 5.0  # Default interval
            if len(sys.argv) > 2:
                try:
                    interval = float(sys.argv[2])
                except ValueError:
                    print("Invalid interval value. Using default 5.0 seconds.")
            
            print(f"Toggling between LIGHT and DARK modes every {interval} seconds.")
            print("Press Ctrl+C to exit.")
            current_mode = None
            
            while True:
                if current_mode != "light":
                    set_light_mode(controller)
                    current_mode = "light"
                else:
                    set_dark_mode(controller)
                    current_mode = "dark"
                
                time.sleep(interval)
        else:
            print_usage()
    
    except KeyboardInterrupt:
        print("\nExiting lighting control...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Don't close the controller - using persistent connection
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        print(f"Completed in {total_time:.2f} ms")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 