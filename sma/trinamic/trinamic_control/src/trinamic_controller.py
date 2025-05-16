"""
Trinamic Controller Module

Main class for controlling Trinamic stepper motor controllers
"""

import serial
import time
import configparser
import os

# Import the logger
from .logger import logger


class TrinamicController:
    """
    Main controller class for Trinamic motor controllers
    """
    
    def __init__(self, port='COM3', baudrate=9600, address=1):
        """Initialize the controller with serial connection parameters"""
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.ser = None
        logger.debug("INIT", f"Initialized controller with port={port}, baudrate={baudrate}, address={address}")
        
    def connect(self):
        """Establish connection to the controller"""
        logger.info("CONNECT", f"Opening serial port {self.port}")
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        is_open = self.ser.is_open
        logger.info("CONNECT", f"Connection {'successful' if is_open else 'failed'}")
        return is_open
        
    def disconnect(self):
        """Close the serial connection"""
        if self.ser and self.ser.is_open:
            logger.info("CONNECT", f"Closing serial port {self.port}")
            self.ser.close()
            logger.debug("CONNECT", "Connection closed")
            
    def calculate_checksum(self, data):
        """Calculate checksum for TMCL command"""
        checksum = 0
        for byte in data:
            checksum += byte
        return checksum & 0xFF
        
    def send_command(self, command, type_number, motor, value, no_answer=False):
        """Send a TMCL command to the controller"""
        # Log command information
        cmd_info = {
            "Command": command,
            "Type": type_number,
            "Motor": motor,
            "Value": value,
            "No Answer": no_answer
        }
        logger.command("TMCL", f"Sending command: CMD={command}, TYPE={type_number}, MOTOR={motor}, VALUE={value}", cmd_info)
        
        # Construct command
        data = [
            self.address,
            command,
            type_number,
            motor,
            (value >> 24) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF
        ]
        
        checksum = self.calculate_checksum(data)
        data.append(checksum)
        
        logger.debug("SERIAL", "Sending raw data", data)
        self.ser.write(bytes(data))
        
        if no_answer:
            logger.debug("SERIAL", "Not waiting for response (no_answer=True)")
            return 0
        
        # Read response
        response = self.ser.read(9)
        logger.response("TMCL", f"Received response ({len(response)} bytes)", list(response))
        
        if len(response) == 9:
            # Extract value from response
            value = (response[5] << 24) | (response[6] << 16) | (response[7] << 8) | response[8]
            status_code = response[2] 
            status_info = "Success" if status_code == 100 else f"Error code: {status_code}"
            logger.response("TMCL", f"Response status: {status_info}, value: {value}")
            return value
        else:
            logger.error("TMCL", f"Invalid response length: {len(response)}, expected 9 bytes")
        
        return 0 