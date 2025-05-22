#!/usr/bin/env python
"""
Supply Voltage State Analyzer

This script guides the user through different device states (ON, LID OPEN, OFF)
and analyzes the voltage patterns to determine characteristic voltage ranges for each state.
"""

import sys
import time
import os
import statistics
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.trinamic_controller import TrinamicController
from src.logger import LogLevel, logger

# Constants for analysis
SAMPLE_TIME = 5  # Seconds to sample each state
SAMPLE_INTERVAL = 0.1  # Seconds between samples
STABILITY_THRESHOLD = 200  # Voltage variation considered stable

class VoltageStateAnalyzer:
    def __init__(self, port='COM3'):
        # Disable logging
        logger.min_level = LogLevel.ERROR
        
        # Initialize controller
        self.controller = TrinamicController(port=port)
        self.controller.connect()
        
        # Store results for each state
        self.results = {
            'ON': {'voltages': [], 'median': None, 'std_dev': None},
            'LID_OPEN': {'voltages': [], 'median': None, 'std_dev': None},
            'OFF': {'voltages': [], 'median': None, 'std_dev': None}
        }
        
        # For live monitoring
        self.voltages = []
        self.times = []
        self.start_time = time.time()
    
    def get_voltage(self):
        """Get the current voltage reading"""
        try:
            return self.controller.send_command(15, 8, 1, 0)
        except Exception as e:
            print(f"Error reading voltage: {e}")
            return 0
    
    def monitor_until_stable(self, description="current", timeout=30, required_stable_time=2):
        """Monitor voltage until it stabilizes"""
        print(f"\nMonitoring {description} state until voltage stabilizes...")
        print("Time    | Voltage  | Status")
        print("--------+----------+------------------")
        
        start = time.time()
        stable_start = None
        recent_voltages = deque(maxlen=int(required_stable_time / SAMPLE_INTERVAL))
        
        while True:
            voltage = self.get_voltage()
            elapsed = time.time() - start
            
            # Add to our recording
            self.voltages.append(voltage)
            self.times.append(time.time() - self.start_time)
            
            # Add to stability check window
            recent_voltages.append(voltage)
            
            # Calculate standard deviation of recent readings if we have enough
            is_stable = False
            stability_message = "Waiting for stability"
            
            if len(recent_voltages) >= 3:  # Need at least a few readings
                std_dev = statistics.stdev(recent_voltages)
                
                if std_dev < STABILITY_THRESHOLD:
                    if stable_start is None:
                        stable_start = time.time()
                    
                    stable_time = time.time() - stable_start
                    stability_message = f"Stable for {stable_time:.1f}s (std={std_dev:.1f})"
                    
                    # If stable for required time, we're done
                    if stable_time >= required_stable_time:
                        is_stable = True
                else:
                    # Reset stable timer if we saw variance
                    stable_start = None
                    stability_message = f"Unstable (std={std_dev:.1f})"
            
            # Print status update
            print(f"{elapsed:06.2f}s | {voltage:8} | {stability_message}")
            
            # Check if we're done
            if is_stable:
                print(f"\nVoltage has stabilized around {statistics.median(recent_voltages)}")
                return recent_voltages
            
            # Check timeout
            if elapsed > timeout:
                print(f"\nTimeout reached after {timeout}s. Using current values.")
                return recent_voltages
            
            time.sleep(SAMPLE_INTERVAL)
    
    def sample_state(self, state_name, description):
        """Sample voltage readings for a specific state"""
        input(f"\nPress Enter when the device is in {description} state...")
        
        print(f"\nSampling {description} state for {SAMPLE_TIME} seconds...")
        print("Time    | Voltage  | Status")
        print("--------+----------+------------------")
        
        # First monitor until stable
        stable_voltages = self.monitor_until_stable(description)
        
        # Now collect samples for the specified time
        start_time = time.time()
        voltages = []
        
        while time.time() - start_time < SAMPLE_TIME:
            voltage = self.get_voltage()
            voltages.append(voltage)
            elapsed = time.time() - start_time
            
            # Add to our recording
            self.voltages.append(voltage)
            self.times.append(time.time() - self.start_time)
            
            print(f"{elapsed:06.2f}s | {voltage:8} | Recording")
            time.sleep(SAMPLE_INTERVAL)
        
        # Calculate statistics
        self.results[state_name]['voltages'] = voltages
        self.results[state_name]['median'] = statistics.median(voltages)
        self.results[state_name]['std_dev'] = statistics.stdev(voltages) if len(voltages) > 1 else 0
        
        print(f"\n{description} state sampled - Median voltage: {self.results[state_name]['median']}")
    
    def analyze_transition(self, from_state, to_state, description):
        """Analyze the transition between two states"""
        input(f"\nPress Enter to begin transition from {from_state} to {to_state}...")
        
        print(f"\nMonitoring transition from {from_state} to {to_state}...")
        print("Please perform the action when ready.")
        
        # First, get a few baseline readings of the current state
        baselines = []
        for _ in range(5):
            baselines.append(self.get_voltage())
            time.sleep(SAMPLE_INTERVAL)
        
        baseline = statistics.median(baselines)
        print(f"Baseline voltage: {baseline}")
        
        # Monitor the transition
        self.monitor_until_stable(f"transition to {to_state}", timeout=60)
    
    def plot_results(self):
        """Plot the full voltage trace and state information"""
        plt.figure(figsize=(12, 8))
        
        # Plot the full voltage trace
        plt.subplot(2, 1, 1)
        plt.plot(self.times, self.voltages, 'b-', linewidth=1.5)
        plt.title('Voltage Over Time Across All States')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Voltage')
        plt.grid(True)
        
        # Mark the approximate state transitions with vertical lines
        # Note: This is a simplification as we don't track exact transition points
        
        # Plot the state distribution histogram
        plt.subplot(2, 1, 2)
        
        # Combine all voltage readings to determine overall distribution
        all_voltages = []
        for state, data in self.results.items():
            if data['voltages']:
                all_voltages.extend(data['voltages'])
        
        if all_voltages:
            plt.hist(all_voltages, bins=50, alpha=0.7)
            plt.title('Voltage Distribution')
            plt.xlabel('Voltage')
            plt.ylabel('Frequency')
            plt.grid(True)
            
            # Add vertical lines for each state's median
            for state, data in self.results.items():
                if data['median'] is not None:
                    plt.axvline(x=data['median'], color='r' if state == 'OFF' else 'g' if state == 'ON' else 'y', 
                               linestyle='--', label=f"{state} Median: {data['median']:.0f}")
            
            plt.legend()
        
        plt.tight_layout()
        plt.savefig('voltage_state_analysis.png')
        print("\nSaved analysis plot to voltage_state_analysis.png")
        plt.show()
    
    def calculate_thresholds(self):
        """Calculate optimal threshold values to distinguish between states"""
        thresholds = {}
        
        # Check if we have enough data
        if (self.results['ON']['median'] is not None and 
            self.results['LID_OPEN']['median'] is not None):
            # Threshold between ON and LID_OPEN
            thresholds['ON_LID_OPEN'] = (self.results['ON']['median'] + self.results['LID_OPEN']['median']) / 2
        
        if (self.results['LID_OPEN']['median'] is not None and 
            self.results['OFF']['median'] is not None):
            # Threshold between LID_OPEN and OFF
            thresholds['LID_OPEN_OFF'] = (self.results['LID_OPEN']['median'] + self.results['OFF']['median']) / 2
        
        return thresholds
    
    def run_analysis(self):
        """Run the complete analysis flow"""
        print("\n=== Supply Voltage State Analyzer ===\n")
        print("This script will guide you through analyzing different states of the device.")
        print("It will help determine voltage thresholds for ON, LID OPEN, and OFF states.")
        
        try:
            # Step 1: Power ON state
            print("\n--- Step 1: Device Powered ON ---")
            print("Make sure the device is powered ON with the lid CLOSED.")
            self.sample_state('ON', "powered ON with lid CLOSED")
            
            # Step 2: LID OPEN state
            print("\n--- Step 2: LID OPEN Transition ---")
            print("Next, we'll analyze what happens when you open the lid.")
            self.analyze_transition("ON", "LID OPEN", "opening the lid")
            self.sample_state('LID_OPEN', "powered ON with lid OPEN")
            
            # Step 3: Power OFF state
            print("\n--- Step 3: Power OFF Transition ---")
            print("Finally, we'll analyze what happens when you turn the device OFF.")
            self.analyze_transition("LID OPEN", "OFF", "powering OFF")
            self.sample_state('OFF', "powered OFF")
            
            # Calculate thresholds
            thresholds = self.calculate_thresholds()
            
            # Show results
            print("\n=== Analysis Results ===\n")
            
            print("State Voltage Characteristics:")
            for state, data in self.results.items():
                if data['median'] is not None:
                    print(f"{state+':':<10} Median = {data['median']:.0f}, StdDev = {data['std_dev']:.1f}")
            
            print("\nRecommended Threshold Values:")
            if 'ON_LID_OPEN' in thresholds:
                print(f"ON vs LID_OPEN: {thresholds['ON_LID_OPEN']:.0f}")
            if 'LID_OPEN_OFF' in thresholds:
                print(f"LID_OPEN vs OFF: {thresholds['LID_OPEN_OFF']:.0f}")
            
            # Save and show the plot
            self.plot_results()
            
            # Save results to file
            self.save_results()
            
        except KeyboardInterrupt:
            print("\nAnalysis interrupted!")
        except Exception as e:
            print(f"\nError during analysis: {e}")
        finally:
            if hasattr(self, 'controller') and self.controller:
                print("\nDisconnecting controller...")
                self.controller.disconnect()
    
    def save_results(self):
        """Save the analysis results to a text file"""
        with open('voltage_state_analysis.txt', 'w') as f:
            f.write("=== Supply Voltage State Analysis Results ===\n\n")
            
            f.write("State Voltage Characteristics:\n")
            for state, data in self.results.items():
                if data['median'] is not None:
                    f.write(f"{state+':':<10} Median = {data['median']:.0f}, StdDev = {data['std_dev']:.1f}\n")
            
            thresholds = self.calculate_thresholds()
            f.write("\nRecommended Threshold Values:\n")
            if 'ON_LID_OPEN' in thresholds:
                f.write(f"ON vs LID_OPEN: {thresholds['ON_LID_OPEN']:.0f}\n")
            if 'LID_OPEN_OFF' in thresholds:
                f.write(f"LID_OPEN vs OFF: {thresholds['LID_OPEN_OFF']:.0f}\n")
            
            f.write("\nRaw Data:\n")
            for state, data in self.results.items():
                if data['voltages']:
                    f.write(f"{state} voltages: {', '.join(map(str, data['voltages']))}\n")
        
        print("Saved analysis results to voltage_state_analysis.txt")


def main():
    port = 'COM3'  # Default port
    
    # Get port from command line argument if provided
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    analyzer = VoltageStateAnalyzer(port=port)
    analyzer.run_analysis()


if __name__ == "__main__":
    main() 