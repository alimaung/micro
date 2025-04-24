#!/usr/bin/env python3
"""
ESP32 Relay Controller - Python Client
This script controls relays connected to an ESP32 via serial commands
"""

import serial
import time
import logging
import json
import re

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
            # Initialize state tracking
            self.relay_states = {i: False for i in range(1, 9)}  # All relays start OFF
            self.system_stats = {
                "cpu": "0MHz",
                "temp": "0°C",
                "ram": "0KB",
                "uptime": "0d 0h 0m 0s",
                "voltage": "0V"
            }
            self.current_mode = "light"  # Default mode
            logging.info(f"Connected to {port} at {baudrate} baud.")
            
            # Get initial states
            self.update_all_states()
            
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {port}: {e}")
            raise

    def flush_input(self):
        """Clear any pending input"""
        self.ser.reset_input_buffer()

    def send_command(self, command, read_multiple_lines=False):
        """Send a command to the ESP32 and return the response(s)"""
        try:
            self.flush_input()
            self.ser.write(f"{command}\n".encode())
            
            if not read_multiple_lines:
                time.sleep(0.05)  # Short delay for simple commands
                response = self.ser.readline().decode('utf-8').strip()
                logging.info(f"Command '{command}' executed. Response: {response}")
                
                # Update relay state if command changed it
                if response.startswith("RELAY:") and ":" in response:
                    self._process_relay_response(response)
                    
                return response
            else:
                # For multi-line responses like STATUS
                time.sleep(0.1)  # Longer delay to ensure all data is received
                responses = []
                
                # Read until timeout or specific end marker
                start_marker_seen = False
                end_marker = None
                
                while self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    
                    # Check for start/end markers
                    if line == "RELAY_STATUS_BEGIN":
                        start_marker_seen = True
                        end_marker = "RELAY_STATUS_END"
                        continue
                    elif line == "SYSTEM_STATS_BEGIN":
                        start_marker_seen = True
                        end_marker = "SYSTEM_STATS_END"
                        continue
                    elif line == end_marker:
                        break
                    
                    if start_marker_seen:
                        responses.append(line)
                        
                        # Process relay status responses
                        if line.startswith("RELAY:"):
                            self._process_relay_response(line)
                        # Process system stat responses
                        elif ":" in line:
                            self._process_system_stat(line)
                
                logging.info(f"Command '{command}' executed. Got {len(responses)} responses.")
                return responses
                
        except Exception as e:
            logging.error(f"Error sending command '{command}': {e}")
            return None

    def _process_relay_response(self, response):
        """Process relay status response and update internal state"""
        try:
            parts = response.split(":")
            if len(parts) >= 3 and parts[0] == "RELAY":
                relay_num = int(parts[1])
                state = parts[2].upper() == "ON"
                self.relay_states[relay_num] = state
                
                # Update mode state for relays 2, 3, 4 (these control the dark/light mode)
                if relay_num in [2, 3, 4]:
                    # If relay 2, 3, and 4 are on, it's dark mode. Otherwise, it's light mode.
                    if all(self.relay_states.get(i, False) for i in [2, 3, 4]):
                        self.current_mode = "dark"
                    else:
                        self.current_mode = "light"
                
                logging.debug(f"Updated relay {relay_num} state to {state}")
        except Exception as e:
            logging.error(f"Error processing relay response {response}: {e}")

    def _process_system_stat(self, line):
        """Process system stat response and update internal state"""
        try:
            key, value = line.split(":", 1)
            if key == "CPU":
                self.system_stats["cpu"] = value
            elif key == "TEMP":
                self.system_stats["temp"] = value
            elif key == "RAM":
                self.system_stats["ram"] = value
            elif key == "UPTIME":
                self.system_stats["uptime"] = value
            elif key == "VOLTAGE":
                self.system_stats["voltage"] = value
        except Exception as e:
            logging.error(f"Error processing system stat {line}: {e}")

    def relay_on(self, relay_num):
        """Turn on a specific relay"""
        response = self.send_command(f"ON:{relay_num}")
        return response

    def relay_off(self, relay_num):
        """Turn off a specific relay"""
        response = self.send_command(f"OFF:{relay_num}")
        return response

    def pulse_relay(self, relay_num):
        """Send a pulse to a specific relay"""
        logging.info(f"Pulsing relay {relay_num}")
        response = self.send_command(f"PULSE:{relay_num}")
        return response

    def get_relay_status(self, relay_num=None):
        """Get the status of a specific relay or all relays"""
        if relay_num is not None:
            response = self.send_command(f"STATUS:RELAY:{relay_num}")
            return response
        else:
            responses = self.send_command("STATUS", read_multiple_lines=True)
            return responses
    
    def get_system_stats(self):
        """Get all system stats"""
        responses = self.send_command("STATUS:SYSTEM", read_multiple_lines=True)
        return self.system_stats

    def get_cpu_freq(self):
        """Get CPU frequency"""
        response = self.send_command("STATUS:CPU")
        if response and response.startswith("CPU:"):
            return response.split(":", 1)[1]
        return None

    def get_temperature(self):
        """Get CPU temperature"""
        response = self.send_command("STATUS:TEMP")
        if response and response.startswith("TEMP:"):
            return response.split(":", 1)[1]
        return None

    def get_free_ram(self):
        """Get free RAM"""
        response = self.send_command("STATUS:RAM")
        if response and response.startswith("RAM:"):
            return response.split(":", 1)[1]
        return None

    def get_uptime(self):
        """Get ESP32 uptime"""
        response = self.send_command("STATUS:UPTIME")
        if response and response.startswith("UPTIME:"):
            return response.split(":", 1)[1]
        return None

    def get_voltage(self):
        """Get voltage"""
        response = self.send_command("STATUS:VOLTAGE")
        if response and response.startswith("VOLTAGE:"):
            return response.split(":", 1)[1]
        return None

    def update_all_states(self):
        """Update all relay states and system stats"""
        # Get relay states
        self.send_command("STATUS", read_multiple_lines=True)
        # Get system stats
        self.send_command("STATUS:SYSTEM", read_multiple_lines=True)
        
        # Return combined state object
        return {
            "relay_states": self.relay_states,
            "system_stats": self.system_stats,
            "current_mode": self.current_mode
        }

    def get_current_mode(self):
        """Get current mode based on relay states"""
        return self.current_mode

    def set_light_mode(self):
        """Activate light mode by pulsing relay 1 and turning off relays 2, 3, 4"""
        logging.info("Activating light mode")
        
        # Turn off all the mode relays first
        self.relay_off(2)    # Turn off relay 2
        self.relay_off(3)    # Turn off relay 3
        self.relay_off(4)    # Turn off relay 4
        time.sleep(0.1)      # Short delay
        self.pulse_relay(1)  # Pulse relay 1 last
        
        # Update internal state
        self.relay_states[2] = False
        self.relay_states[3] = False
        self.relay_states[4] = False
        self.current_mode = "light"
        
        return "light"

    def set_dark_mode(self):
        """Activate dark mode by pulsing relay 1 and turning on relays 2, 3, 4"""
        logging.info("Activating dark mode")
        
        # Turn on all the mode relays first
        self.relay_on(2)     # Turn on relay 2
        self.relay_on(3)     # Turn on relay 3
        self.relay_on(4)     # Turn on relay 4
        time.sleep(0.1)      # Short delay
        self.pulse_relay(1)  # Pulse relay 1 last
        
        # Update internal state
        self.relay_states[2] = True
        self.relay_states[3] = True
        self.relay_states[4] = True
        self.current_mode = "dark"
        
        return "dark"

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
