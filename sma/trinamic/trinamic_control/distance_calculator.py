"""
Distance Calculator for Trinamic Motor Control

Calculates motor steps required to move a specific distance in millimeters,
accounting for microstepping resolution scaling as done in the original VB.NET code.
"""

import math
import argparse


class DistanceCalculator:
    """
    Calculator for converting distance to motor steps with resolution scaling
    """
    
    def __init__(self, steps_per_mm_16mm=139.8, steps_per_mm_35mm=140):
        """
        Initialize with steps per mm for different film formats
        
        Args:
            steps_per_mm_16mm: Steps per millimeter for 16mm film (default: 139.8)
            steps_per_mm_35mm: Steps per millimeter for 35mm film (default: 140)
        """
        self.steps_per_mm_16mm = steps_per_mm_16mm
        self.steps_per_mm_35mm = steps_per_mm_35mm
    
    def calculate_steps_for_distance(self, distance_mm, resolution, motor=1, film_format="16mm"):
        """
        Calculate the number of steps needed to move a specific distance
        
        Args:
            distance_mm: Distance to move in millimeters
            resolution: Microstepping resolution (1, 2, 4, 8)
            motor: Motor number (0=shutter, 1=film) - affects resolution scaling
            film_format: Film format ("16mm" or "35mm")
            
        Returns:
            int: Number of steps to send to motor controller
        """
        # Get base steps per mm based on film format
        if film_format == "35mm":
            steps_per_mm = self.steps_per_mm_35mm
        else:
            steps_per_mm = self.steps_per_mm_16mm
            
        # Calculate base steps needed
        base_steps = distance_mm * steps_per_mm
        
        # Apply resolution scaling (reverse of what happens in VB.NET code)
        # The VB.NET code divides steps before sending, so we need to multiply here
        if motor == 1:  # Film motor
            if resolution == 1:  # Full step
                scaled_steps = base_steps * 8
            elif resolution == 2:  # Half step
                scaled_steps = base_steps * 4
            elif resolution == 4:  # Quarter step
                scaled_steps = base_steps * 2
            elif resolution == 8:  # Eighth step
                scaled_steps = base_steps  # No scaling for 1/8 step
            else:
                scaled_steps = base_steps
        else:  # Shutter motor (motor 0) - different scaling pattern
            if resolution == 1:  # Full step
                scaled_steps = base_steps * 8
            elif resolution == 2:  # Half step
                scaled_steps = base_steps * 4
            elif resolution == 4:  # Quarter step
                scaled_steps = base_steps * 2
            elif resolution == 8:  # Eighth step
                scaled_steps = base_steps
            else:
                scaled_steps = base_steps
                
        return round(scaled_steps)
    
    def calculate_actual_distance(self, steps, resolution, motor=1, film_format="16mm"):
        """
        Calculate the actual distance that will be traveled for a given number of steps
        
        Args:
            steps: Number of steps sent to motor controller
            resolution: Microstepping resolution (1, 2, 4, 8)
            motor: Motor number (0=shutter, 1=film)
            film_format: Film format ("16mm" or "35mm")
            
        Returns:
            float: Actual distance in millimeters
        """
        # Get base steps per mm
        if film_format == "35mm":
            steps_per_mm = self.steps_per_mm_35mm
        else:
            steps_per_mm = self.steps_per_mm_16mm
            
        # Apply resolution scaling (what happens in VB.NET code)
        if motor == 1:  # Film motor
            if resolution == 1:  # Full step
                actual_steps = steps / 8
            elif resolution == 2:  # Half step
                actual_steps = steps / 4
            elif resolution == 4:  # Quarter step
                actual_steps = steps / 2
            elif resolution == 8:  # Eighth step
                actual_steps = steps  # No scaling
            else:
                actual_steps = steps
        else:  # Shutter motor
            if resolution == 1:  # Full step
                actual_steps = steps / 8
            elif resolution == 2:  # Half step
                actual_steps = steps / 4
            elif resolution == 4:  # Quarter step
                actual_steps = steps / 2
            elif resolution == 8:  # Eighth step
                actual_steps = steps
            else:
                actual_steps = steps
                
        return actual_steps / steps_per_mm


def main():
    """Command-line interface and example usage"""
    parser = argparse.ArgumentParser(description='Calculate motor steps for distance movement')
    parser.add_argument('--distance', '-d', type=float, help='Distance to move in millimeters')
    parser.add_argument('--resolution', '-r', type=int, choices=[1, 2, 4, 8], default=4, 
                       help='Microstepping resolution (default: 4)')
    parser.add_argument('--motor', '-m', type=int, choices=[0, 1], default=1,
                       help='Motor number: 0=shutter, 1=film (default: 1)')
    parser.add_argument('--film-format', '-f', choices=['16mm', '35mm'], default='16mm',
                       help='Film format (default: 16mm)')
    parser.add_argument('--steps', '-s', type=int, help='Calculate distance from steps (reverse calculation)')
    parser.add_argument('--generate-command', '-g', action='store_true',
                       help='Generate full motor_control_cli.py command')
    parser.add_argument('--sma-config', action='store_true',
                       help='Use SMA application configuration (SCHRITTEPROMM_0=139, resolution=2)')
    parser.add_argument('--steps-per-mm', type=float, help='Override steps per mm value')
    
    args = parser.parse_args()
    
    # Determine steps per mm value
    if args.sma_config:
        # Use SMA application values from docufile.ini
        steps_per_mm_16mm = 139.0  # SCHRITTEPROMM_0=139
        steps_per_mm_35mm = 140.0  # SCHRITTEPROMM_1=140
        default_resolution = 2     # FILM_AUFLOESUNG_0=2
        if args.resolution == 4:   # If user didn't specify, use SMA default
            args.resolution = default_resolution
            print(f"Using SMA configuration: steps_per_mm={steps_per_mm_16mm}, resolution={default_resolution}")
    elif args.steps_per_mm:
        steps_per_mm_16mm = args.steps_per_mm
        steps_per_mm_35mm = args.steps_per_mm
    else:
        # Use original Python defaults
        steps_per_mm_16mm = 139.8
        steps_per_mm_35mm = 140
    
    calc = DistanceCalculator(steps_per_mm_16mm, steps_per_mm_35mm)
    
    if args.steps:
        # Reverse calculation: steps to distance
        distance = calc.calculate_actual_distance(args.steps, args.resolution, args.motor, args.film_format)
        print(f"Steps {args.steps} with resolution {args.resolution} on motor {args.motor} = {distance:.3f}mm")
        return
    
    if args.distance:
        # Forward calculation: distance to steps
        steps = calc.calculate_steps_for_distance(args.distance, args.resolution, args.motor, args.film_format)
        actual_distance = calc.calculate_actual_distance(steps, args.resolution, args.motor, args.film_format)
        
        print(f"To move {args.distance}mm:")
        print(f"  Resolution: {args.resolution}")
        print(f"  Motor: {args.motor} ({'film' if args.motor == 1 else 'shutter'})")
        print(f"  Film format: {args.film_format}")
        print(f"  Steps per mm: {steps_per_mm_16mm if args.film_format == '16mm' else steps_per_mm_35mm}")
        print(f"  Steps needed: {steps}")
        print(f"  Actual distance: {actual_distance:.3f}mm")
        
        if args.generate_command:
            print(f"\nGenerated command (basic):")
            print(f"python motor_control_cli.py --port COM3 --motor {args.motor} --set-resolution {args.resolution} --set-speed 2000 --set-current 120 --move {steps} --direction 1 --set-standby-current 10 --set-acceleration 600")
            
            print(f"\nGenerated command (with reference speeds - matches SMA app):")
            if args.motor == 0:  # Shutter motor
                print(f"python motor_control_cli.py --port COM3 --motor {args.motor} --set-resolution {args.resolution} --set-speed 2000 --set-current 80 --move {steps} --direction 1 --set-standby-current 10 --set-acceleration 500 --set-reference-speeds 50 10")
            else:  # Film motor
                print(f"python motor_control_cli.py --port COM3 --motor {args.motor} --set-resolution {args.resolution} --set-speed 2000 --set-current 120 --move {steps} --direction 1 --set-standby-current 10 --set-acceleration 600")
                print(f"# Note: Film motor doesn't use reference speeds in the original VB.NET code")
        return
    
    # Default: show examples
    print("Distance Calculator for Trinamic Motors")
    print("=" * 50)
    
    # Example: Calculate steps for 10mm movement
    distance = 10.0  # mm
    resolution = 4
    motor = 1  # Film motor
    
    steps_needed = calc.calculate_steps_for_distance(distance, resolution, motor)
    actual_distance = calc.calculate_actual_distance(steps_needed, resolution, motor)
    
    print(f"To move {distance}mm with resolution {resolution} on motor {motor}:")
    print(f"  Steps to send: {steps_needed}")
    print(f"  Actual distance: {actual_distance:.3f}mm")
    print()
    
    # Test different resolutions
    print("Steps needed for 10mm at different resolutions (motor 1):")
    for res in [1, 2, 4, 8]:
        steps = calc.calculate_steps_for_distance(10.0, res, 1)
        actual = calc.calculate_actual_distance(steps, res, 1)
        print(f"  Resolution {res}: {steps} steps -> {actual:.3f}mm")
    
    print()
    print("Example commands:")
    steps_for_10mm = calc.calculate_steps_for_distance(10.0, 4, 1)
    print(f"python motor_control_cli.py --port COM3 --motor 1 --set-resolution 4 --set-speed 2000 --set-current 120 --move {steps_for_10mm} --direction 1 --set-standby-current 10 --set-acceleration 600")
    
    print(f"\nSMA Application equivalent (resolution 2, steps_per_mm=139):")
    calc_sma = DistanceCalculator(139, 140)
    steps_sma = calc_sma.calculate_steps_for_distance(10.0, 2, 1)
    print(f"python motor_control_cli.py --port COM3 --motor 1 --set-resolution 2 --set-speed 2000 --set-current 120 --move {steps_sma} --direction 1 --set-standby-current 10 --set-acceleration 600")
    
    print(f"\nUsage examples:")
    print(f"  python distance_calculator.py --distance 10 --resolution 4")
    print(f"  python distance_calculator.py --distance 10 --sma-config --generate-command")
    print(f"  python distance_calculator.py --distance 5 --resolution 2 --motor 0")
    print(f"  python distance_calculator.py --steps 2796 --resolution 4")
    print(f"  python distance_calculator.py --distance 10 --steps-per-mm 139")


if __name__ == "__main__":
    main() 