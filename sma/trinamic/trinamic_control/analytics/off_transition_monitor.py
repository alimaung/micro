#!/usr/bin/env python
"""
Power OFF Transition Analyzer

This script specifically analyzes the transition from ON to OFF state,
monitoring the gradual voltage decrease until manually stopped.
"""

import sys
import time
import os
import statistics
import datetime
from collections import deque

# For keyboard input on Windows
import msvcrt

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.logger import LogLevel, logger

# Constants
SAMPLE_INTERVAL = 0.1  # Seconds between samples
INITIAL_SAMPLE_TIME = 5  # Seconds to sample ON state
TRANSITION_THRESHOLD_PERCENT = 5  # Percent drop to detect transition start

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class OffTransitionMonitor:
    def __init__(self, port='COM3'):
        # Disable logging
        logger.min_level = LogLevel.ERROR
        
        # Initialize controller
        print(f"Connecting to controller on port {port}...")
        self.controller = TrinamicController(port=port)
        self.controller.connect()
        
        # Store voltage readings
        self.readings = []
        self.start_time = None
        self.on_median = None
        self.min_voltage = float('inf')
        self.max_voltage = 0
        self.transition_detected_at = None
        
    def get_voltage(self):
        """Get the current voltage reading"""
        try:
            voltage = self.controller.send_command(15, 8, 1, 0)
            self.min_voltage = min(self.min_voltage, voltage)
            self.max_voltage = max(self.max_voltage, voltage)
            return voltage
        except Exception as e:
            print(f"Error reading voltage: {e}")
            return 0
    
    def sample_on_state(self):
        """Sample the ON state to establish baseline"""
        print(f"\n{Colors.BOLD}Sampling ON state for {INITIAL_SAMPLE_TIME} seconds...{Colors.RESET}")
        print("Please ensure the device is fully powered ON and the lid is CLOSED.")
        print("\nTime     | Voltage  | Status")
        print("---------+----------+------------")
        
        voltages = []
        start = time.time()
        
        while time.time() - start < INITIAL_SAMPLE_TIME:
            voltage = self.get_voltage()
            voltages.append(voltage)
            elapsed = time.time() - start
            
            print(f"{elapsed:7.2f}s | {voltage:8} | Sampling ON")
            time.sleep(SAMPLE_INTERVAL)
        
        # Calculate median
        self.on_median = statistics.median(voltages)
        self.on_std_dev = statistics.stdev(voltages) if len(voltages) > 1 else 0
        
        print(f"\n{Colors.BOLD}ON state sampling complete:{Colors.RESET}")
        print(f"Median voltage: {self.on_median:.0f}")
        print(f"Standard deviation: {self.on_std_dev:.1f}")
    
    def monitor_transition(self):
        """Monitor the transition from ON to OFF until manually stopped"""
        transition_threshold = self.on_median * (1 - TRANSITION_THRESHOLD_PERCENT/100)
        
        print(f"\n{Colors.BOLD}Ready to monitor OFF transition{Colors.RESET}")
        print(f"Transition will be detected when voltage drops below {transition_threshold:.0f}")
        print("Press Enter to begin shutdown, then press 'p' at any time to stop monitoring...")
        input("\nPress Enter when ready to turn device OFF...")
        
        self.start_time = time.time()
        print("\nTimestamp            | Elapsed  | Voltage  | Status")
        print("---------------------+----------+----------+------------------")
        
        # Set up counters
        reading_count = 0
        transition_detected = False
        last_status_update = time.time()
        status_update_interval = 1.0  # Status message update interval in seconds
        
        try:
            while True:
                voltage = self.get_voltage()
                now = time.time()
                elapsed = now - self.start_time
                reading_count += 1
                
                # Record the reading
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                self.readings.append((timestamp, elapsed, voltage))
                
                # Check for transition detection
                if not transition_detected and voltage < transition_threshold:
                    transition_detected = True
                    self.transition_detected_at = elapsed
                    status = f"{Colors.YELLOW}Transition detected!{Colors.RESET}"
                    print(f"{timestamp} | {elapsed:8.2f} | {voltage:8} | {status}")
                elif now - last_status_update >= status_update_interval:
                    # Determine voltage color and status
                    if voltage > self.on_median * 0.9:
                        color = Colors.GREEN
                        status = "ON"
                    elif voltage > self.on_median * 0.2:
                        color = Colors.YELLOW
                        status = "Decreasing"
                    else:
                        color = Colors.RED
                        status = "LOW"
                    
                    print(f"{timestamp} | {elapsed:8.2f} | {color}{voltage:8}{Colors.RESET} | {status}")
                    last_status_update = now
                
                # Check for keyboard input (Windows method)
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'p':
                        print("\nMonitoring manually stopped.")
                        break
                
                time.sleep(SAMPLE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped with Ctrl+C")
        finally:
            print(f"\nRecorded {len(self.readings)} voltage readings over {elapsed:.2f} seconds")
    
    def save_results(self):
        """Save the collected data to a file"""
        if not self.readings:
            print("No data to save.")
            return
            
        filename = f"off_transition_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w') as f:
            f.write("=== Power OFF Transition Analysis ===\n\n")
            f.write(f"ON State Median Voltage: {self.on_median:.0f}\n")
            f.write(f"ON State Standard Deviation: {self.on_std_dev:.1f}\n")
            f.write(f"Voltage Range: {self.min_voltage} to {self.max_voltage}\n")
            
            if self.transition_detected_at:
                f.write(f"Transition detected at: {self.transition_detected_at:.2f} seconds\n")
            
            f.write("\nRaw Data:\n")
            f.write("Timestamp,Elapsed,Voltage\n")
            
            for timestamp, elapsed, voltage in self.readings:
                f.write(f"{timestamp},{elapsed:.2f},{voltage}\n")
        
        print(f"\nSaved results to {filename}")
    
    def run(self):
        """Run the complete monitoring sequence"""
        print(f"\n{Colors.BOLD}=== Power OFF Transition Analyzer ==={Colors.RESET}\n")
        
        try:
            # Step 1: Sample ON state
            self.sample_on_state()
            
            # Step 2: Monitor transition
            self.monitor_transition()
            
            # Step 3: Save results
            self.save_results()
            
        except Exception as e:
            print(f"\nError during analysis: {e}")
        finally:
            if hasattr(self, 'controller') and self.controller:
                print("\nDisconnecting controller...")
                self.controller.disconnect()


def main():
    port = 'COM3'  # Default port
    
    # Get port from command line argument if provided
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    monitor = OffTransitionMonitor(port=port)
    monitor.run()


if __name__ == "__main__":
    main() 