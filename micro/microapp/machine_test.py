#!/usr/bin/env python3
"""
Machine Power Test - Detects if the machine is actually powered on
Based on comtest.py but streamlined for integration with Django
"""

import serial
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MachineController:
    """Controls and tests the machine connection and power state"""
    
    def __init__(self, port='COM3', baudrate=38400, timeout=1):
        """Initialize the serial connection to the machine"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
    
    def connect(self):
        """Establish a connection to the machine"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            logging.info(f"Connected to machine on {self.port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            logging.error(f"Failed to connect to machine on {self.port}: {e}")
            return False
    
    def close(self):
        """Close the serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Serial connection to machine closed.")
    
    def is_power_on(self):
        """Check if the machine is actually powered on by querying voltage"""
        try:
            if not self.ser or not self.ser.is_open:
                if not self.connect():
                    return False
            
            # Values for voltage check command
            target = 1
            inst = 15
            motor = 1
            type1 = 8
            value = 0
            
            # Create and send the command
            voltage = self.send_bin_command(target, inst, motor, type1, value)
            logging.info(f"Machine voltage value: {voltage}")
            
            # Determine power state based on voltage threshold
            is_on = voltage > 10000
            logging.info(f"Machine power is {'ON' if is_on else 'OFF'}")
            
            return is_on
            
        except Exception as e:
            logging.error(f"Error checking machine power: {e}")
            return False
        finally:
            self.close()
    
    def send_bin_command(self, target, inst, motor, type1, value):
        """Send a binary command to the Trinamic controller and get the response"""
        # Create command packet
        array = bytearray(10)  # 10 bytes (0-9)
        
        # Fill the command packet
        array[1] = target & 0xFF
        array[2] = inst & 0xFF
        array[3] = type1 & 0xFF
        array[4] = motor & 0xFF
        
        # Break value into bytes
        array[5] = (value & 0xFF000000) >> 24
        array[6] = (value & 0x00FF0000) >> 16
        array[7] = (value & 0x0000FF00) >> 8
        array[8] = (value & 0x000000FF)
        
        # Calculate checksum
        checksum = 0
        for i in range(1, 9):
            checksum += array[i]
        
        array[9] = checksum & 0xFF
        
        # Print the command bytes being sent
        sent_bytes = []
        for i in range(1, 10):
            sent_bytes.append(f"0x{array[i]:02x}")
        logging.info(f"Sending 9 bytes: {sent_bytes}")
        
        # Send the command bytes
        for i in range(1, 10):
            self.ser.write(bytes([array[i]]))
        
        # Wait for response
        time.sleep(0.2)
        
        # Read response
        result = 0
        response = bytearray()
        
        if self.ser.in_waiting > 0:
            response = self.ser.read(self.ser.in_waiting)
            
            # Print the received bytes
            received_bytes = []
            for byte in response:
                received_bytes.append(f"0x{byte:02x}")
            logging.info(f"Received {len(response)} bytes: {received_bytes}")
            
            # Print status code interpretation if we have enough bytes
            if len(response) >= 3:
                status_code = response[2]
                status_meaning = "Unknown"
                if status_code == 100:
                    status_meaning = "Success"
                elif status_code == 1:
                    status_meaning = "Wrong checksum"
                elif status_code == 2:
                    status_meaning = "Invalid command"
                elif status_code == 3:
                    status_meaning = "Wrong type"
                elif status_code == 4:
                    status_meaning = "Invalid value"
                elif status_code == 5:
                    status_meaning = "Configuration EEPROM locked"
                elif status_code == 6:
                    status_meaning = "Command not available"
                logging.info(f"Status code: {status_code} ({status_meaning})")
            
            # Calculate voltage from bytes 7-8 if we have enough bytes
            if len(response) >= 9:
                result = (response[7] * 256 + response[8])
                logging.info(f"Calculated from bytes 7,8: 0x{response[7]:02x}*256 + 0x{response[8]:02x} = {result}")
                
                # Try interpreting voltage in different ways
                if result > 1000:  # If value seems too large
                    alt_voltage = response[8]  # Try just the last byte
                    logging.info(f"Alternative voltage (last byte only): {alt_voltage/10.0}V")
        
        return result

def check_machine_power(port='COM3'):
    """Utility function to check if machine is powered on"""
    controller = MachineController(port)
    is_on = controller.is_power_on()
    return is_on

if __name__ == "__main__":
    is_on = check_machine_power()
    print(f"Machine is {'ON' if is_on else 'OFF'}") 