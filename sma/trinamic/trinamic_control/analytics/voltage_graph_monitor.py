#!/usr/bin/env python
"""
Live Supply Voltage Graph Monitor

This script continuously monitors the supply voltage and displays it as a live
scrolling graph, making it easy to visualize voltage changes when the lid is opened or closed.
"""

import sys
import time
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.logger import LogLevel, logger

# Define constants
MAX_POINTS = 500  # Maximum number of points to display
UPDATE_INTERVAL = 100  # Update interval in milliseconds (100ms)
SUPPLY_VOLTAGE_THRESHOLD = 10000  # Threshold for lid open/closed detection

class VoltageMonitor:
    def __init__(self, port='COM3'):
        # Disable logging
        logger.min_level = LogLevel.ERROR
        
        # Initialize data structures
        self.times = deque(maxlen=MAX_POINTS)
        self.voltages = deque(maxlen=MAX_POINTS)
        self.start_time = None
        
        # Setup controller
        self.controller = TrinamicController(port=port)
        self.controller.connect()
        
        # Setup the figure and axis
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_title('Live Supply Voltage Monitor')
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Voltage')
        self.ax.grid(True)
        
        # Add a horizontal line for the threshold
        self.threshold_line = self.ax.axhline(y=SUPPLY_VOLTAGE_THRESHOLD, color='r', linestyle='--', alpha=0.7)
        self.ax.text(0.02, SUPPLY_VOLTAGE_THRESHOLD * 1.02, 'Lid Open/Closed Threshold', 
                    color='r', alpha=0.7, transform=plt.gca().get_yaxis_transform())
        
        # Initialize the plot line
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5)
        
        # Add status text display
        self.status_text = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes,
                                      fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', 
                                      facecolor='white', alpha=0.8))
        
        # Set y-axis limits with some padding
        self.ax.set_ylim(0, 70000)
        self.fig.tight_layout()
    
    def init_animation(self):
        """Initialize the animation"""
        self.line.set_data([], [])
        self.start_time = time.time()
        return self.line, self.status_text, self.threshold_line
    
    def update_animation(self, frame):
        """Update the animation frame"""
        # Get voltage reading
        voltage = self.controller.send_command(15, 8, 1, 0)
        current_time = time.time() - self.start_time
        
        # Add the new data
        self.times.append(current_time)
        self.voltages.append(voltage)
        
        # Determine lid status
        lid_status = "CLOSED" if voltage > SUPPLY_VOLTAGE_THRESHOLD else "OPEN"
        status_color = "green" if lid_status == "CLOSED" else "red"
        
        # Update the line data
        self.line.set_data(list(self.times), list(self.voltages))
        
        # Adjust x-axis limits to show only the most recent data
        if len(self.times) > 0:
            x_min = max(0, current_time - 30)  # Show last 30 seconds
            x_max = current_time + 0.5  # Add a small buffer on the right
            self.ax.set_xlim(x_min, x_max)
        
        # Update status text
        status_text = f"Lid: {lid_status} | Current Voltage: {voltage}"
        self.status_text.set_text(status_text)
        self.status_text.set_color(status_color)
        
        return self.line, self.status_text, self.threshold_line
    
    def run(self):
        """Run the animation"""
        ani = animation.FuncAnimation(
            self.fig, 
            self.update_animation, 
            init_func=self.init_animation,
            interval=UPDATE_INTERVAL, 
            blit=True
        )
        plt.show()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.disconnect()


def main():
    port = 'COM3'  # Default port
    
    # Get port from command line argument if provided
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print(f"Starting Voltage Graph Monitor on port {port}")
    print("Close the graph window to exit")
    
    monitor = None
    try:
        monitor = VoltageMonitor(port=port)
        monitor.run()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if monitor:
            monitor.cleanup()


if __name__ == "__main__":
    main() 