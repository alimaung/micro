#!/usr/bin/env python
"""
OFF Transition Data Analyzer

Analyzes the recorded voltage transition data to understand the decay pattern.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

def analyze_transition_file(filename):
    """Analyze a transition data file and visualize the results"""
    print(f"Analyzing file: {filename}")
    
    # Extract metadata from the beginning of the file
    metadata = {}
    with open(filename, 'r') as f:
        # Skip the header line
        f.readline()
        f.readline()
        
        # Read metadata
        for _ in range(10):  # Read up to 10 lines for metadata
            line = f.readline().strip()
            if line == "" or "Raw Data:" in line:
                break
            
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
    
    print("\nMetadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Read the CSV data
    # Skip rows until we find the CSV header
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    start_line = 0
    for i, line in enumerate(lines):
        if "Timestamp,Elapsed,Voltage" in line:
            start_line = i + 1
            break
    
    # Convert data to pandas DataFrame
    data = []
    for line in lines[start_line:]:
        try:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                timestamp, elapsed, voltage = parts
                data.append({
                    'timestamp': timestamp,
                    'elapsed': float(elapsed),
                    'voltage': int(voltage)
                })
        except (ValueError, IndexError):
            continue
    
    df = pd.DataFrame(data)
    
    # Basic statistics
    stats = {
        'Total samples': len(df),
        'Duration (s)': df['elapsed'].max() - df['elapsed'].min(),
        'Initial voltage': df['voltage'].iloc[0],
        'Final voltage': df['voltage'].iloc[-1],
        'Max voltage': df['voltage'].max(),
        'Min voltage': df['voltage'].min(),
        'Voltage drop': df['voltage'].iloc[0] - df['voltage'].iloc[-1]
    }
    
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Find key transition points
    voltage_threshold = 0.1 * (df['voltage'].max() - df['voltage'].min()) + df['voltage'].min()
    
    # Find the time when voltage dropped to 90%, 50%, 10% of the initial range
    initial_voltage = df['voltage'].iloc[0]
    final_voltage = df['voltage'].iloc[-1]
    voltage_range = initial_voltage - final_voltage
    
    thresholds = {
        '90% of initial': initial_voltage - 0.1 * voltage_range,
        '50% of initial': initial_voltage - 0.5 * voltage_range,
        '10% of initial': initial_voltage - 0.9 * voltage_range
    }
    
    transition_times = {}
    for name, threshold in thresholds.items():
        try:
            # Find first time voltage drops below threshold
            idx = df[df['voltage'] < threshold].index[0]
            transition_times[name] = df.iloc[idx]['elapsed']
        except IndexError:
            transition_times[name] = None
    
    print("\nKey Transition Points:")
    for name, elapsed in transition_times.items():
        if elapsed is not None:
            print(f"  Time to {name}: {elapsed:.2f} seconds")
        else:
            print(f"  Time to {name}: Not reached")
    
    # Calculate decay rate (V/s) during the main transition period
    try:
        start_idx = df[df['voltage'] < thresholds['90% of initial']].index[0]
        try:
            end_idx = df[df['voltage'] < thresholds['10% of initial']].index[0]
        except IndexError:
            end_idx = len(df) - 1
        
        if start_idx < end_idx:
            start_voltage = df.iloc[start_idx]['voltage']
            end_voltage = df.iloc[end_idx]['voltage']
            start_time = df.iloc[start_idx]['elapsed']
            end_time = df.iloc[end_idx]['elapsed']
            
            decay_rate = (start_voltage - end_voltage) / (end_time - start_time)
            print(f"\nMain decay rate: {decay_rate:.2f} V/s")
    except IndexError:
        print("\nCouldn't calculate decay rate")
    
    # Plot the voltage over time
    plt.figure(figsize=(12, 8))
    
    # Main plot - full resolution
    plt.subplot(2, 1, 1)
    plt.plot(df['elapsed'], df['voltage'], 'b-', alpha=0.5, label='Raw')
    
    # Add smoothed line
    try:
        # Apply Savitzky-Golay filter for smoothing
        if len(df) > 10:
            window_size = min(15, len(df) // 2 * 2 - 1)  # Must be odd
            if window_size > 2:
                smoothed = savgol_filter(df['voltage'], window_size, 2)
                plt.plot(df['elapsed'], smoothed, 'r-', linewidth=2, label='Smoothed')
    except Exception as e:
        print(f"Couldn't apply smoothing: {e}")
    
    # Add horizontal lines for thresholds
    for name, threshold in thresholds.items():
        plt.axhline(y=threshold, color='g', linestyle='--', alpha=0.7)
        
    # Add vertical lines for transition times
    for name, elapsed in transition_times.items():
        if elapsed is not None:
            plt.axvline(x=elapsed, color='r', linestyle='--', alpha=0.7)
            plt.text(elapsed, df['voltage'].max() * 0.9, name, 
                     rotation=90, verticalalignment='top')
    
    plt.title('Voltage Transition Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Voltage')
    plt.grid(True)
    plt.legend()
    
    # Second subplot - log scale to highlight transitions
    plt.subplot(2, 1, 2)
    plt.semilogy(df['elapsed'], df['voltage'], 'g-', linewidth=2)
    plt.title('Voltage Transition (Log Scale)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Voltage (log)')
    plt.grid(True)
    
    plt.tight_layout()
    output_filename = os.path.splitext(filename)[0] + '_analysis.png'
    plt.savefig(output_filename)
    print(f"\nSaved analysis plot to {output_filename}")
    
    # Show the plot
    plt.show()


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Find the latest transition file
        data_dir = os.path.dirname(os.path.abspath(__file__))
        files = [f for f in os.listdir(data_dir) if f.startswith('off_transition_') and f.endswith('.txt')]
        
        if not files:
            print("No transition data files found!")
            return
        
        # Sort by modification time (latest first)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(data_dir, f)), reverse=True)
        filename = os.path.join(data_dir, files[0])
        print(f"Using most recent file: {filename}")
    
    analyze_transition_file(filename)


if __name__ == "__main__":
    main() 