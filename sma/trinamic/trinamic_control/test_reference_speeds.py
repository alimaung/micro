#!/usr/bin/env python3
"""
Test Reference Speeds Implementation

This script demonstrates the new reference speed functionality and shows
how to configure the Trinamic controller to match the SMA application exactly.
"""

import sys
import os
import time

# Add parent directory to path so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from distance_calculator import DistanceCalculator


def generate_sma_equivalent_commands():
    """Generate commands that exactly match the SMA application configuration"""
    
    print("=" * 80)
    print("SMA APPLICATION EQUIVALENT COMMANDS")
    print("=" * 80)
    print()
    
    # Create calculator with SMA values
    calc = DistanceCalculator(139.0, 140.0)  # SMA SCHRITTEPROMM values
    
    print("1. SHUTTER MOTOR (Motor 0) - Full SMA Configuration:")
    print("   - Uses reference speeds (50, 10)")
    print("   - Drive current: 80A")
    print("   - Hold current: 10A")
    print("   - Acceleration: 500")
    print("   - Resolution: 2 (half step)")
    print()
    
    # Calculate steps for 5mm movement (typical shutter movement)
    shutter_steps = calc.calculate_steps_for_distance(5.0, 2, 0)  # 5mm, resolution 2, motor 0
    
    print("   Example: Move shutter 5mm")
    print(f"   python cli/motor_control_cli.py --port COM3 --motor 0 \\")
    print(f"     --set-resolution 2 --set-speed 2000 --set-current 80 \\")
    print(f"     --set-standby-current 10 --set-acceleration 500 \\")
    print(f"     --set-reference-speeds 50 10 --move {shutter_steps} --direction 1")
    print()
    
    print("2. FILM MOTOR (Motor 1) - SMA Configuration:")
    print("   - NO reference speeds (as per VB.NET code)")
    print("   - Drive current: 120A")
    print("   - Hold current: 10A")
    print("   - Acceleration: 600")
    print("   - Resolution: 2 (half step)")
    print("   - Steps per mm: 139 (SCHRITTEPROMM_0)")
    print()
    
    # Calculate steps for 10mm movement
    film_steps = calc.calculate_steps_for_distance(10.0, 2, 1)  # 10mm, resolution 2, motor 1
    
    print("   Example: Move film 10mm")
    print(f"   python cli/motor_control_cli.py --port COM3 --motor 1 \\")
    print(f"     --set-resolution 2 --set-speed 2000 --set-current 120 \\")
    print(f"     --set-standby-current 10 --set-acceleration 600 \\")
    print(f"     --move {film_steps} --direction 1")
    print()
    
    print("3. CONFIGURATION-ONLY COMMANDS (Set once, then just move):")
    print("   This is more efficient, like the SMA application startup")
    print()
    print("   # Configure shutter motor once:")
    print("   python cli/motor_control_cli.py --port COM3 --motor 0 \\")
    print("     --set-resolution 2 --set-current 80 --set-standby-current 10 \\")
    print("     --set-acceleration 500 --set-reference-speeds 50 10")
    print()
    print("   # Configure film motor once:")
    print("   python cli/motor_control_cli.py --port COM3 --motor 1 \\")
    print("     --set-resolution 2 --set-current 120 --set-standby-current 10 \\")
    print("     --set-acceleration 600")
    print()
    print("   # Then just move (faster subsequent commands):")
    print(f"   python cli/motor_control_cli.py --port COM3 --motor 1 --set-speed 2000 --move {film_steps}")
    print()


def show_reference_speed_explanation():
    """Explain what reference speeds do and why they're important"""
    
    print("=" * 80)
    print("REFERENCE SPEEDS EXPLANATION")
    print("=" * 80)
    print()
    
    print("Reference speeds control the acceleration/deceleration curves of Trinamic motors.")
    print("They define how smoothly the motor accelerates from standstill to target speed.")
    print()
    
    print("VB.NET Code Analysis:")
    print("- SetRefSpeedsTrinamic(motor, speed1, speed2)")
    print("- Sends TMCL commands: TYPE=194 (speed1), TYPE=195 (speed2)")
    print("- Only applied to SHUTTER motor (motor 0), NOT film motor (motor 1)")
    print("- Values from trinamic.ini: ReferenceSpeed1=50, ReferenceSpeed2=10")
    print()
    
    print("Effects of Reference Speeds:")
    print("✓ Smoother acceleration/deceleration")
    print("✓ Reduced vibration and noise")
    print("✓ More precise positioning")
    print("✓ Less mechanical stress on the system")
    print("✗ Without them: jerky movements, potential overshooting")
    print()
    
    print("CLI Implementation:")
    print("- --set-reference-speeds 50 10     (set both at once)")
    print("- --set-reference-speed1 50        (set first speed only)")
    print("- --set-reference-speed2 10        (set second speed only)")
    print()


def show_distance_calculation_comparison():
    """Show the difference between different calculation methods"""
    
    print("=" * 80)
    print("DISTANCE CALCULATION COMPARISON")
    print("=" * 80)
    print()
    
    # Original Python defaults
    calc_original = DistanceCalculator(139.8, 140)
    
    # SMA application values
    calc_sma = DistanceCalculator(139.0, 140)
    
    distance = 10.0
    
    print(f"For {distance}mm movement:")
    print()
    
    print("Original Python Calculator (steps_per_mm=139.8):")
    for res in [1, 2, 4, 8]:
        steps = calc_original.calculate_steps_for_distance(distance, res, 1)
        print(f"  Resolution {res}: {steps} steps")
    print()
    
    print("SMA Application Calculator (steps_per_mm=139.0):")
    for res in [1, 2, 4, 8]:
        steps = calc_sma.calculate_steps_for_distance(distance, res, 1)
        sma_highlight = " ← SMA uses this" if res == 2 else ""
        print(f"  Resolution {res}: {steps} steps{sma_highlight}")
    print()
    
    print("Your Original Command vs SMA Equivalent:")
    original_steps = calc_original.calculate_steps_for_distance(distance, 4, 1)
    sma_steps = calc_sma.calculate_steps_for_distance(distance, 2, 1)
    
    print(f"Your original:    {original_steps} steps (resolution 4, 139.8 steps/mm)")
    print(f"SMA equivalent:   {sma_steps} steps (resolution 2, 139.0 steps/mm)")
    print(f"Difference:       {abs(original_steps - sma_steps)} steps ({abs(original_steps - sma_steps) / max(original_steps, sma_steps) * 100:.1f}%)")
    print()


def main():
    """Main demonstration function"""
    
    print("TRINAMIC REFERENCE SPEEDS IMPLEMENTATION")
    print("Analysis and Commands for SMA Application Compatibility")
    print("=" * 80)
    print()
    
    show_reference_speed_explanation()
    print()
    
    show_distance_calculation_comparison()
    print()
    
    generate_sma_equivalent_commands()
    
    print("=" * 80)
    print("QUICK REFERENCE")
    print("=" * 80)
    print()
    print("Key Differences Found:")
    print("1. ❌ Resolution: You used 4, SMA uses 2")
    print("2. ❌ Steps/mm: You used 139.8, SMA uses 139.0")
    print("3. ❌ Reference speeds: You didn't set them, SMA sets them for shutter motor")
    print()
    print("For EXACT SMA matching:")
    print("python distance_calculator.py --distance 10 --sma-config --generate-command")
    print()
    print("To test reference speeds:")
    print("python cli/motor_control_cli.py --port COM3 --motor 0 --set-reference-speeds 50 10 --debug")
    print()


if __name__ == "__main__":
    main() 