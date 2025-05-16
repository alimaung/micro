"""
Motor Control Module

Functions for controlling motor movement, speed, and parameters
"""

from .trinamic_controller import TrinamicController
from .logger import logger
import time


class MotorControl:
    """
    Motor control functions for Trinamic controllers
    """
    
    def __init__(self, controller):
        """Initialize with a controller instance"""
        self.controller = controller
        # Store current resolution for each motor
        self.motor_resolution = {0: 2, 1: 2}  # Default to 2 (half step)
        logger.debug("MOTOR", "Motor Control initialized")
        
    def set_motor_resolution(self, motor, resolution):
        """Set the microstepping resolution of the motor"""
        logger.debug("MOTOR", f"Setting motor {motor} resolution to {resolution} (CMD=5, TYPE=140, MOTOR={motor}, VALUE={resolution})")
        # Store the resolution for speed scaling
        self.motor_resolution[motor] = resolution
        return self.controller.send_command(5, 140, motor, resolution)
    
    def set_target_speed(self, motor, speed):
        """Set the target speed of the motor with automatic resolution scaling"""
        # Use the resolution-aware speed scaling
        return self.set_speed_with_resolution_scaling(motor, speed)
    
    def set_speed_with_resolution_scaling(self, motor, speed):
        """
        Set the target speed with scaling adjustment based on the motor resolution
        This replicates the behavior of SetMaximumSpeedTrinamic in the VB.NET code
        """
        resolution = self.motor_resolution.get(motor, 2)  # Default to 2 if not set
        adjusted_speed = speed
        
        # Apply scaling based on motor and resolution
        if motor == 1:  # Film motor
            if resolution == 1:  # Full step
                adjusted_speed = round(speed / 4)
                logger.debug("MOTOR", f"Film motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
            elif resolution == 2:  # Half step
                adjusted_speed = round(speed / 2)
                logger.debug("MOTOR", f"Film motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
            elif resolution == 8:  # 1/8 step
                adjusted_speed = speed * 2
                logger.debug("MOTOR", f"Film motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
        else:  # Shutter motor (motor 0)
            if resolution == 4:  # 1/4 step
                adjusted_speed = round(speed / 2)
                logger.debug("MOTOR", f"Shutter motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
            elif resolution == 2:  # Half step
                adjusted_speed = round(speed / 4)
                logger.debug("MOTOR", f"Shutter motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
            elif resolution == 1:  # Full step
                adjusted_speed = round(speed / 8)
                logger.debug("MOTOR", f"Shutter motor: Adjusting speed from {speed} to {adjusted_speed} (resolution={resolution})")
                
        logger.debug("MOTOR", f"Setting motor {motor} target speed to {adjusted_speed} (original={speed}, resolution={resolution}) (CMD=5, TYPE=4, MOTOR={motor}, VALUE={adjusted_speed})")
        return self.controller.send_command(5, 4, motor, adjusted_speed)
    
    def set_max_current(self, motor, current):
        """Set the maximum current for the motor"""
        logger.debug("MOTOR", f"Setting motor {motor} max current to {current} (CMD=5, TYPE=6, MOTOR={motor}, VALUE={current})")
        return self.controller.send_command(5, 6, motor, current)
    
    def set_standby_current(self, motor, current):
        """Set the standby current for the motor"""
        logger.debug("MOTOR", f"Setting motor {motor} standby current to {current} (CMD=5, TYPE=7, MOTOR={motor}, VALUE={current})")
        return self.controller.send_command(5, 7, motor, current)
    
    def set_max_acceleration(self, motor, acceleration):
        """Set the maximum acceleration for the motor"""
        logger.debug("MOTOR", f"Setting motor {motor} acceleration to {acceleration} (CMD=5, TYPE=5, MOTOR={motor}, VALUE={acceleration})")
        return self.controller.send_command(5, 5, motor, acceleration)
    
    def set_reference_speeds(self, motor, speed1, speed2):
        """Set reference speeds for the motor"""
        logger.debug("MOTOR", f"Setting motor {motor} reference speed 1 to {speed1} (CMD=5, TYPE=194, MOTOR={motor}, VALUE={speed1})")
        result1 = self.controller.send_command(5, 194, motor, speed1)
        logger.debug("MOTOR", f"Setting motor {motor} reference speed 2 to {speed2} (CMD=5, TYPE=195, MOTOR={motor}, VALUE={speed2})")
        result2 = self.controller.send_command(5, 195, motor, speed2)
        return result1 and result2
    
    def move_motor(self, motor, steps, direction=1):
        """Move the motor a specific number of steps in the given direction"""
        if direction < 0:
            steps = -steps
        logger.debug("MOTOR", f"Moving motor {motor} {abs(steps)} steps {'backward' if steps < 0 else 'forward'} (CMD=4, TYPE=1, MOTOR={motor}, VALUE={steps})")
        return self.controller.send_command(4, 1, motor, steps)
    
    def stop_motor(self, motor):
        """Stop the specified motor"""
        logger.debug("MOTOR", f"Stopping motor {motor} (CMD=3, TYPE=0, MOTOR={motor}, VALUE=0)")
        return self.controller.send_command(3, 0, motor, 0)
    
    def is_motor_running(self, motor):
        """Check if the motor is currently running"""
        logger.debug("MOTOR", f"Checking if motor {motor} is running (CMD=6, TYPE=3, MOTOR={motor}, VALUE=0)")
        result = self.controller.send_command(6, 3, motor, 0)
        is_running = result != 0
        logger.debug("MOTOR", f"Motor {motor} running status: {is_running} (result={result})")
        return is_running
    
    def reset_controller(self):
        """Reset the controller"""
        logger.debug("MOTOR", "Resetting controller (CMD=255, TYPE=0, MOTOR=0, VALUE=1234)")
        return self.controller.send_command(255, 0, 0, 1234, True)
    
    def move_to_home_position(self, motor):
        """Move the motor to its home position"""
        logger.debug("MOTOR", f"Starting home move for motor {motor} (CMD=13, TYPE=0, MOTOR={motor}, VALUE=0)")
        self.controller.send_command(13, 0, motor, 0)
        start_time = time.time()
        logger.debug("MOTOR", "Waiting for home position...")
        
        while time.time() - start_time <= 2:
            logger.debug("MOTOR", f"Checking home position (CMD=13, TYPE=2, MOTOR={motor}, VALUE=0)")
            result = self.controller.send_command(13, 2, motor, 0)
            logger.debug("MOTOR", f"Home position check result: {result}")
            if result == 0:
                logger.debug("MOTOR", "Home position reached")
                break
            time.sleep(0.5)
            
        logger.debug("MOTOR", f"Home move completed (timeout={time.time() - start_time > 2})")
        return True 