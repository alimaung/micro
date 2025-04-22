#!/usr/bin/env python3
"""
ESP32 Relay Controller - Python Client
This script controls relays connected to an ESP32 via serial commands
"""

import serial
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RelayController:
    """Controls relays connected to an ESP32 via serial communication"""
    
    def __init__(self, port, baudrate=115200, timeout=1, reset_delay=0.0):
        """Initialize the serial connection to the ESP32"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            if reset_delay > 0:
                time.sleep(reset_delay)  # Wait for ESP32 to reset after serial connection
            self.flush_input()
            logging.info(f"Connected to {port} at {baudrate} baud.")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {port}: {e}")
            raise

    def flush_input(self):
        """Clear any pending input"""
        self.ser.reset_input_buffer()

    def send_command(self, command):
        """Send a command to the ESP32 and return the response"""
        try:
            self.flush_input()
            self.ser.write(f"{command}\n".encode())
            time.sleep(0.05)  # Reduced wait time
            response = self.ser.readline().decode('utf-8').strip()
            logging.info(f"Command '{command}' executed. Response: {response}")
            return response
        except Exception as e:
            logging.error(f"Error sending command '{command}': {e}")
            return None

    def relay_on(self, relay_num):
        """Turn on a specific relay"""
        return self.send_command(f"ON:{relay_num}")

    def relay_off(self, relay_num):
        """Turn off a specific relay"""
        return self.send_command(f"OFF:{relay_num}")

    def pulse_relay(self, relay_num):
        """Send a pulse to a specific relay"""
        logging.info(f"Pulsing relay {relay_num}")
        self.send_command(f"PULSE:{relay_num}")

    def get_status(self):
        """Get the status of all relays"""
        return self.send_command("STATUS")

    def set_light_mode(self):
        """Activate light mode by pulsing relay 1 and turning off relays 2, 3, 4"""
        logging.info("Activating light mode")
        self.pulse_relay(1)  # Pulse relay 1
        self.relay_off(2)    # Turn off relay 2
        self.relay_off(3)    # Turn off relay 3
        self.relay_off(4)    # Turn off relay 4

    def set_dark_mode(self):
        """Activate dark mode by pulsing relay 1 and turning on relays 2, 3, 4"""
        logging.info("Activating dark mode")
        self.pulse_relay(1)  # Pulse relay 1
        self.relay_on(2)     # Turn on relay 2
        self.relay_on(3)     # Turn on relay 3
        self.relay_on(4)     # Turn on relay 4

    def machine_on(self):
        """Turn on the machine (relay 8)"""
        logging.info("Turning machine on")
        return self.relay_on(8)

    def machine_off(self):
        """Turn off the machine (relay 8)"""
        logging.info("Turning machine off")
        return self.relay_off(8)

    def close(self):
        """Close the serial connection"""
        self.ser.close()
        logging.info("Serial connection closed.")

def main():
    # This part remains unchanged, as it handles command-line arguments
    pass

if __name__ == "__main__":
    main()
