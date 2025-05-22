#!/usr/bin/env python
import subprocess
import time

def run_command(command, description=None):
    """Run a command and print its description"""
    if description:
        print(f"\n=== {description} ===")
    print(f"Executing: {command}")
    
    # Run the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    return result.stdout

def check_vacuum_status():
    """Check vacuum status and return True if OK"""
    result = subprocess.run(
        "python io_control_cli.py --check-vacuum",
        shell=True, capture_output=True, text=True
    )
    print("\033[31m" + result.stdout + "\033[0m")
    return "vacuum status: ok" in result.stdout.lower()

def simulate_exposure(num_frames=10):
    print(f"\n==== STARTING EXPOSURE SIMULATION FOR {num_frames} FRAMES ====\n")
    
    # Home the shutter at start (once only)
    # Note: --home command already has built-in waiting, so no --wait needed
    run_command(
        "python motor_control_cli.py --port COM3 --motor 0 --direction 1 --home",
        "INITIALIZING: Homing shutter"
    )
    
    # Activate vacuum once at the beginning and keep it on
    run_command(
        "python io_control_cli.py --vacuum-on", 
        "Activating vacuum (stays on for entire process)"
    )
    
    # Add pause after opening vacuum to let it establish
    pause_seconds = 2
    print(f"\n=== Pausing for {pause_seconds} seconds to let vacuum establish ===")
    time.sleep(pause_seconds)
    
    # Expose each frame
    for frame in range(1, num_frames + 1):
        print(f"\n==== PROCESSING FRAME {frame}/{num_frames} ====")
        
        # Activate magnet for this frame
        run_command(
            "python io_control_cli.py --magnet-on", 
            "Activating magnet"
        )
        
        # Verify vacuum status and retry if needed
        vacuum_retries = 3
        vacuum_ok = False
        for retry in range(vacuum_retries):
            if check_vacuum_status():
                vacuum_ok = True
                print("Vacuum check passed, proceeding with exposure")
                break
            else:
                print(f"Vacuum check failed (attempt {retry+1}/{vacuum_retries})")
                time.sleep(0.5)
        
        if not vacuum_ok:
            print("WARNING: Could not establish proper vacuum, but continuing for demo purposes")
        
        # Pause before first shutter operation
        if frame == 1:
            pause_seconds = 1
            print(f"\n=== Pausing for {pause_seconds} seconds before first shutter operation ===")
            time.sleep(pause_seconds)
        
        # Operate shutter for exposure - include --wait flag
        run_command(
            "python motor_control_cli.py --port COM3 --motor 0 --set-resolution 4 --set-speed 640 --set-current 80 --move 3200 --direction 1 --set-standby-current 10 --wait",
            f"EXPOSING frame {frame}"
        )
        
        # Turn off magnet after exposure (vacuum stays on)
        run_command(
            "python io_control_cli.py --magnet-off",
            "Deactivating magnet (vacuum remains on)"
        )
        time.sleep(0.5)
        
        # Advance film (except after last frame) - include --wait flag
        if frame < num_frames:
            run_command(
                "python motor_control_cli.py --port COM3 --motor 1 --set-resolution 4 --set-speed 540 --set-current 120 --move 2796 --direction 1 --set-standby-current 10 --set-acceleration 600 --wait",
                "Advancing film to next position"
            )
    
    # Turn off vacuum at the very end
    run_command(
        "python io_control_cli.py --vacuum-off",
        "Deactivating vacuum at end of session"
    )
    
    print("\n==== EXPOSURE SIMULATION COMPLETE ====")

if __name__ == "__main__":
    simulate_exposure(3)