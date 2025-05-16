"""
Logger module for Trinamic Control

Provides consistent, colored logging functionality across the application
"""

import time
import sys
from enum import Enum

class LogLevel(Enum):
    DEBUG = (0, '\033[36m')  # Cyan
    INFO = (1, '\033[32m')   # Green
    WARN = (2, '\033[33m')   # Yellow
    ERROR = (3, '\033[31m')  # Red
    COMMAND = (4, '\033[35m') # Purple
    RESPONSE = (5, '\033[34m') # Blue

class Logger:
    def __init__(self, min_level=LogLevel.DEBUG):
        self.min_level = min_level
        self.reset_color = '\033[0m'
        
    def log(self, level, group, message, data=None):
        if level.value[0] < self.min_level.value[0]:
            return
            
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        color = level.value[1]
        
        # Format message
        log_line = f"{color}{timestamp} [{level.name:^7}] {group:>8} :{self.reset_color} {message}"
        print(log_line)
        
        # Print data in formatted way if provided
        if data is not None:
            if isinstance(data, bytes) or isinstance(data, list):
                hex_data = ' '.join([f"{b:02X}" for b in data])
                print(f"{color}{'':15} {'':^9} {'':>8} | {self.reset_color} HEX: {hex_data}")
                decimal_data = ' '.join([f"{b:3d}" for b in data])
                print(f"{color}{'':15} {'':^9} {'':>8} | {self.reset_color} DEC: {decimal_data}")
            elif isinstance(data, dict):
                for key, value in data.items():
                    print(f"{color}{'':15} {'':^9} {'':>8} | {self.reset_color} {key}: {value}")
            else:
                print(f"{color}{'':15} {'':^9} {'':>8} | {self.reset_color} {data}")
    
    def debug(self, group, message, data=None):
        self.log(LogLevel.DEBUG, group, message, data)
        
    def info(self, group, message, data=None):
        self.log(LogLevel.INFO, group, message, data)
        
    def warn(self, group, message, data=None):
        self.log(LogLevel.WARN, group, message, data)
        
    def error(self, group, message, data=None):
        self.log(LogLevel.ERROR, group, message, data)
        
    def command(self, group, message, data=None):
        self.log(LogLevel.COMMAND, group, message, data)
        
    def response(self, group, message, data=None):
        self.log(LogLevel.RESPONSE, group, message, data)

# Create a global logger instance
logger = Logger() 