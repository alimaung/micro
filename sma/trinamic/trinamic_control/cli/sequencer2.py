#!/usr/bin/env python
"""
Sequence Test 2 - Simplified exposure sequence simulator

This script provides a cleaner implementation of the exposure sequence
simulation, starting with just basic homing operation.
"""

import subprocess
import time
import sys
import os
import signal
import json
import re

# Constants
PORT = "COM3"
SHUTTER_MOTOR = 0
FILM_MOTOR = 1

# ANSI Colors for better output formatting
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def run_command_fast(command, description=None):
    """
    Run a command without waiting for completion (for operations like magnet, vacuum)
    
    Args:
        command (str): The command to execute
        description (str, optional): A description of what the command does
        
    Returns:
        dict: Parsed JSON response from the command
    """
    # Add JSON flag if not present
    if not "--json" in command:
        command += " --json"
        
    try:
        if description:
            print(f"{Colors.BLUE}=== {description} ==={Colors.RESET}")
        
        print(f"Executing (fast): {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Process result
        if result.returncode != 0:
            print(f"{Colors.RED}Command failed with return code {result.returncode}{Colors.RESET}")
            if result.stderr:
                print(f"{Colors.RED}Error: {result.stderr}{Colors.RESET}")
            return {"success": False, "error": f"Return code {result.returncode}"}
        
        # Extract JSON from output (may have log messages or multiple JSON objects)
        stdout = result.stdout
        
        # Try to parse the last complete JSON object in the output
        try:
            # Find all complete JSON objects in the output
            json_objects = []
            pos = 0
            while pos < len(stdout):
                start_idx = stdout.find('{', pos)
                if start_idx == -1:
                    break
                    
                # Find the matching closing brace
                level = 0
                end_idx = -1
                for i in range(start_idx, len(stdout)):
                    if stdout[i] == '{':
                        level += 1
                    elif stdout[i] == '}':
                        level -= 1
                    if level == 0:
                        end_idx = i + 1
                        break
                
                if end_idx != -1:
                    try:
                        json_str = stdout[start_idx:end_idx]
                        json_obj = json.loads(json_str)
                        json_objects.append(json_obj)
                        pos = end_idx
                    except json.JSONDecodeError:
                        # If not valid JSON, move to next potential object
                        pos = start_idx + 1
                else:
                    # If no closing brace, move to next position
                    pos = start_idx + 1
            
            # Use the last JSON object as the result
            if json_objects:
                data = json_objects[-1]  # Get the last (most recent) JSON object
                
                # Print status based on success
                if data.get("success", False):
                    print(f"{Colors.GREEN}✓ Success{Colors.RESET}")
                else:
                    print(f"{Colors.RED}✗ Failed: {data.get('error', 'Unknown error')}{Colors.RESET}")
                    
                return data
            else:
                print(f"{Colors.RED}No JSON found in response{Colors.RESET}")
                print(f"Raw output: {stdout}")
                return {"success": False, "error": "No JSON found in response"}
                
        except Exception as e:
            print(f"{Colors.RED}Failed to parse JSON response: {str(e)}{Colors.RESET}")
            print(f"Raw output: {stdout}")
            return {"success": False, "error": f"JSON parse error: {str(e)}"}
            
    except Exception as e:
        print(f"{Colors.RED}Exception: {str(e)}{Colors.RESET}")
        return {"success": False, "error": str(e)}

def run_command_with_wait(command, description=None):
    """
    Run a command and wait for completion (for operations like home, film advance, shutter)
    Uses Popen to better control execution and ensure waiting works properly
    
    Args:
        command (str): The command to execute
        description (str, optional): A description of what the command does
        
    Returns:
        dict: Parsed JSON response from the command
    """
    # Add JSON flag if not present
    if not "--json" in command:
        command += " --json"
    
    # Add --wait flag to motor movement commands if not present
    if ("--move" in command or "--home" in command) and not "--wait" in command:
        command += " --wait"
        
    try:
        if description:
            print(f"{Colors.BLUE}=== {description} ==={Colors.RESET}")
        
        print(f"Executing (with wait): {command}")
        
        # Use Popen to have more control over execution
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for completion and capture output
        stdout, stderr = process.communicate()
        
        # Process result
        if process.returncode != 0:
            print(f"{Colors.RED}Command failed with return code {process.returncode}{Colors.RESET}")
            if stderr:
                print(f"{Colors.RED}Error: {stderr}{Colors.RESET}")
            return {"success": False, "error": f"Return code {process.returncode}"}
        
        # Extract JSON from output (may have log messages or multiple JSON objects)
        # Try to parse the last complete JSON object in the output
        try:
            # Find all complete JSON objects in the output
            json_objects = []
            pos = 0
            while pos < len(stdout):
                start_idx = stdout.find('{', pos)
                if start_idx == -1:
                    break
                    
                # Find the matching closing brace
                level = 0
                end_idx = -1
                for i in range(start_idx, len(stdout)):
                    if stdout[i] == '{':
                        level += 1
                    elif stdout[i] == '}':
                        level -= 1
                    if level == 0:
                        end_idx = i + 1
                        break
                
                if end_idx != -1:
                    try:
                        json_str = stdout[start_idx:end_idx]
                        json_obj = json.loads(json_str)
                        json_objects.append(json_obj)
                        pos = end_idx
                    except json.JSONDecodeError:
                        # If not valid JSON, move to next potential object
                        pos = start_idx + 1
                else:
                    # If no closing brace, move to next position
                    pos = start_idx + 1
            
            # Use the last JSON object as the result
            if json_objects:
                data = json_objects[-1]  # Get the last (most recent) JSON object
                
                # Print status based on success
                if data.get("success", False):
                    print(f"{Colors.GREEN}✓ Success{Colors.RESET}")
                else:
                    print(f"{Colors.RED}✗ Failed: {data.get('error', 'Unknown error')}{Colors.RESET}")
                    
                return data
            else:
                print(f"{Colors.RED}No JSON found in response{Colors.RESET}")
                print(f"Raw output: {stdout}")
                return {"success": False, "error": "No JSON found in response"}
                
        except Exception as e:
            print(f"{Colors.RED}Failed to parse JSON response: {str(e)}{Colors.RESET}")
            print(f"Raw output: {stdout}")
            return {"success": False, "error": f"JSON parse error: {str(e)}"}
            
    except Exception as e:
        print(f"{Colors.RED}Exception: {str(e)}{Colors.RESET}")
        return {"success": False, "error": str(e)}

def home_shutter():
    """
    Home the shutter motor using JSON output (with waiting)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== HOMING SHUTTER ===={Colors.RESET}")
    
    response = run_command_with_wait(
        f"python motor_control_cli.py --port {PORT} --motor {SHUTTER_MOTOR} --home",
        "Moving shutter to home position"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Shutter successfully moved to home position{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to home shutter: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def activate_vacuum():
    """
    Activate vacuum (fast operation)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== ACTIVATING VACUUM ===={Colors.RESET}")
    
    response = run_command_fast(
        "python io_control_cli.py --vacuum-on",
        "Turning vacuum on"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Vacuum activated successfully{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to activate vacuum: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def activate_magnet():
    """
    Activate magnet (fast operation)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== ACTIVATING MAGNET ===={Colors.RESET}")
    
    response = run_command_fast(
        "python io_control_cli.py --magnet-on",
        "Turning magnet on"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Magnet activated successfully{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to activate magnet: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def deactivate_magnet():
    """
    Deactivate magnet (fast operation)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== RELEASING MAGNET ===={Colors.RESET}")
    
    response = run_command_fast(
        "python io_control_cli.py --magnet-off",
        "Turning magnet off"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Magnet released successfully{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to release magnet: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def check_vacuum():
    """
    Check vacuum status (wait operation)
    
    Returns:
        bool: True if vacuum is OK, False otherwise
    """
    print(f"\n{Colors.BLUE}==== CHECKING VACUUM STATUS ===={Colors.RESET}")
    
    response = run_command_with_wait(
        "python io_control_cli.py --check-vacuum",
        "Checking vacuum status"
    )
    
    vacuum_ok = response.get("vacuum_ok", False)
    status = response.get("vacuum_status", "Unknown")
    
    if vacuum_ok:
        print(f"{Colors.GREEN}✓ Vacuum status: {status}{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Vacuum status: {status}{Colors.RESET}")
        
    return vacuum_ok

def operate_shutter():
    """
    Operate shutter for exposure (wait operation)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== OPERATING SHUTTER ===={Colors.RESET}")
    
    response = run_command_with_wait(
        f"python motor_control_cli.py --port {PORT} --motor {SHUTTER_MOTOR} "
        f"--set-resolution 4 --set-speed 640 --set-current 80 --move 3200 "
        f"--direction 1 --set-standby-current 10",
        "Moving shutter for exposure"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Shutter operation successful{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to operate shutter: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def advance_film():
    """
    Advance film to next position (wait operation)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.BLUE}==== ADVANCING FILM ===={Colors.RESET}")
    
    response = run_command_with_wait(
        f"python motor_control_cli.py --port {PORT} --motor {FILM_MOTOR} "
        f"--set-resolution 4 --set-speed 540 --set-current 120 --move 2796 "
        f"--direction 1 --set-standby-current 10 --set-acceleration 600",
        "Moving film to next position"
    )
    
    if response.get("success", False):
        print(f"{Colors.GREEN}✓ Film advanced successfully{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed to advance film: {response.get('error', 'Unknown error')}{Colors.RESET}")
        return False

def get_user_number():
    """
    Prompt the user to enter an 8-digit number
    
    Returns:
        str: The 8-digit number entered by the user
    """
    print(f"\n{Colors.BLUE}==== USER INPUT REQUIRED ===={Colors.RESET}")
    
    while True:
        input_str = input(f"{Colors.YELLOW}Please enter an 8-digit number: {Colors.RESET}")
        
        # Validate input
        if re.match(r'^\d{8}$', input_str):
            print(f"{Colors.GREEN}✓ Valid number entered: {input_str}{Colors.RESET}")
            return input_str
        else:
            print(f"{Colors.RED}✗ Please enter exactly 8 digits{Colors.RESET}")

def exposure_sequence(num_frames=3):
    """
    Run a complete exposure sequence for multiple frames
    
    Args:
        num_frames: Number of frames to expose
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.GREEN}===== STARTING EXPOSURE SEQUENCE FOR {num_frames} FRAMES ====={Colors.RESET}")
    
    success = True
    
    for frame in range(1, num_frames + 1):
        print(f"\n{Colors.GREEN}==== PROCESSING FRAME {frame}/{num_frames} ===={Colors.RESET}")
        
        # Step 1: Operate shutter for exposure
        if not operate_shutter():
            print(f"{Colors.RED}✗ Failed during shutter operation for frame {frame}{Colors.RESET}")
            success = False
            break
        
        # Step 2: Release magnet
        print(f"{Colors.BLUE}Releasing magnet...{Colors.RESET}")
        if not deactivate_magnet():
            print(f"{Colors.RED}✗ Failed during magnet release for frame {frame}{Colors.RESET}")
            success = False
            break
        
        # Step 3: Advance film (waits until complete)
        print(f"{Colors.BLUE}Now advancing film...{Colors.RESET}")
        if not advance_film():
            print(f"{Colors.RED}✗ Failed during film advance for frame {frame}{Colors.RESET}")
            success = False
            break
        
        # Step 4: Re-engage magnet after film has completely stopped
        if not activate_magnet():
            print(f"{Colors.RED}✗ Failed during magnet re-engagement for frame {frame}{Colors.RESET}")
            success = False
            break
        
        # Short pause between frames
        #if frame < num_frames:
        #    pause_time = 0.5
        #    print(f"\n{Colors.BLUE}Pausing {pause_time}s before next frame...{Colors.RESET}")
        #    time.sleep(pause_time)
    
    return success

def handle_exit(signal, frame):
    """Handle script termination gracefully"""
    print(f"\n\n{Colors.YELLOW}Terminating sequence test...{Colors.RESET}")
    try:
        # Stop any running motors
        print(f"{Colors.YELLOW}Emergency stop for motors...{Colors.RESET}")
        run_command_fast(f"python motor_control_cli.py --port {PORT} --motor {SHUTTER_MOTOR} --stop",
                    "Emergency shutter stop")
        run_command_fast(f"python motor_control_cli.py --port {PORT} --motor {FILM_MOTOR} --stop",
                    "Emergency film stop")
                
        # Turn off vacuum and magnet
        run_command_fast("python io_control_cli.py --vacuum-off", 
                    "Emergency vacuum off")
        run_command_fast("python io_control_cli.py --magnet-off", 
                    "Emergency magnet off")
    except Exception as e:
        print(f"{Colors.RED}Error during cleanup: {e}{Colors.RESET}")
    
    print(f"{Colors.GREEN}Cleanup complete. Exiting.{Colors.RESET}")
    sys.exit(0)

def main():
    """Main function"""
    print(f"\n{Colors.GREEN}===== SEQUENCE TEST 2 ====={Colors.RESET}")
    print(f"{Colors.GREEN}Version 1.4 - Properly Sequenced Operations{Colors.RESET}\n")
    
    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    try:
        # Home the shutter
        if not home_shutter():
            print(f"\n{Colors.RED}===== TEST FAILED: HOMING ERROR ====={Colors.RESET}")
            return
            
        # Get user input
        #user_number = get_user_number()
        #print(f"{Colors.BLUE}Using number: {user_number}{Colors.RESET}")
        
        # Activate vacuum
        if not activate_vacuum():
            print(f"\n{Colors.RED}===== TEST FAILED: VACUUM ACTIVATION ERROR ====={Colors.RESET}")
            return
            
        # Activate magnet
        if not activate_magnet():
            print(f"\n{Colors.RED}===== TEST FAILED: MAGNET ACTIVATION ERROR ====={Colors.RESET}")
            # Turn off vacuum before exit
            run_command_fast("python io_control_cli.py --vacuum-off", "Emergency vacuum off")
            return
            
        # Wait for vacuum to establish
        wait_time = 3
        print(f"\n{Colors.BLUE}=== Waiting {wait_time} seconds for vacuum to establish ==={Colors.RESET}")
        time.sleep(wait_time)
        
        # Check vacuum status
        vacuum_ok = check_vacuum()
        
        if not vacuum_ok:
            print(f"\n{Colors.RED}===== TEST FAILED: VACUUM NOT ESTABLISHED ====={Colors.RESET}")
            # Turn off vacuum and magnet before exit
            run_command_fast("python io_control_cli.py --vacuum-off", "Turning vacuum off")
            run_command_fast("python io_control_cli.py --magnet-off", "Turning magnet off")
            return
        
        # Begin exposure sequence - 5 frames by default
        frames = 5
        sequence_success = exposure_sequence(frames)
        
        if sequence_success:
            print(f"\n{Colors.GREEN}===== EXPOSURE SEQUENCE COMPLETED SUCCESSFULLY ====={Colors.RESET}")
        else:
            print(f"\n{Colors.RED}===== EXPOSURE SEQUENCE FAILED ====={Colors.RESET}")
        
        # Turn off vacuum and magnet before exit
        run_command_fast("python io_control_cli.py --vacuum-off", "Turning vacuum off")
        run_command_fast("python io_control_cli.py --magnet-off", "Turning magnet off")
            
    except Exception as e:
        print(f"{Colors.RED}ERROR: {str(e)}{Colors.RESET}")
        # Ensure cleanup on error
        try:
            run_command_fast("python io_control_cli.py --vacuum-off", "Emergency vacuum off")
            run_command_fast("python io_control_cli.py --magnet-off", "Emergency magnet off")
        except:
            pass
    
if __name__ == "__main__":
    main()