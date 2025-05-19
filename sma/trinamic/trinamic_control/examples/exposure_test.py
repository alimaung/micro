#!/usr/bin/env python
"""
Exposure Test Script

This script emulates the basic motion sequence for microfilm exposures without actually 
taking images. It reads parameters from the configuration files and controls the motors
accordingly.
"""

import os
import sys
import time
import configparser
from pathlib import Path

# Adjust import paths
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent.parent  # /y:/micro/sma
sys.path.append(str(project_root))

# Import trinamic control modules directly from absolute path
from trinamic.trinamic_control.src.trinamic_controller import TrinamicController
from trinamic.trinamic_control.src.motor_control import MotorControl
from trinamic.trinamic_control.src.logger import logger

# Constants
SHUTTER_MOTOR = 0
FILM_MOTOR = 1
CONFIG_PATH = os.path.join(project_root, "sma_source", "config")

class ExposureSimulator:
    """Simulates the exposure process based on configuration settings"""
    
    def __init__(self, config_path=CONFIG_PATH, simulation_mode=True):
        """Initialize the simulator with configuration"""
        self.config_path = config_path
        self.simulation_mode = simulation_mode
        self.trinamic_config = None
        self.job_config = None
        
        # Controller and motor control will be initialized after loading config
        self.controller = None
        self.motor_control = None
        
        # Load configurations
        self.load_configs()
        
        # Initialize controller and motor control
        if not simulation_mode:
            self.initialize_controller()
        
    def load_configs(self):
        """Load configuration from Trinamic.ini and job.tpl"""
        # Load Trinamic.ini
        self.trinamic_config = configparser.ConfigParser()
        trinamic_ini_path = os.path.join(self.config_path, "Trinamic.ini")
        print(f"Looking for Trinamic.ini at: {trinamic_ini_path}")
        if os.path.exists(trinamic_ini_path):
            self.trinamic_config.read(trinamic_ini_path)
            print(f"Loaded Trinamic configuration from {trinamic_ini_path}")
        else:
            print(f"Warning: Trinamic.ini not found at {trinamic_ini_path}")
            
        # Load job.tpl
        self.job_config = configparser.ConfigParser()
        job_tpl_path = os.path.join(self.config_path, "job.tpl")
        print(f"Looking for job.tpl at: {job_tpl_path}")
        if os.path.exists(job_tpl_path):
            # job.tpl has custom format, trying to handle it
            self.job_config.read(job_tpl_path)
            print(f"Loaded job template from {job_tpl_path}")
        else:
            print(f"Warning: job.tpl not found at {job_tpl_path}")
    
    def initialize_controller(self, port="COM3"):
        """Initialize the Trinamic controller and motor control"""
        self.controller = TrinamicController(port=port)
        success = self.controller.connect()
        
        if success:
            self.motor_control = MotorControl(self.controller)
            # Initialize motors with configuration
            self.configure_motors()
            return True
        else:
            print("Failed to connect to controller")
            return False
    
    def configure_motors(self):
        """Configure motors based on Trinamic.ini settings"""
        # Configure shutter motor
        if "VERSCHLUSS" in self.trinamic_config:
            shutter_config = self.trinamic_config["VERSCHLUSS"]
            
            # Set microstepping resolution
            micro_steps = int(shutter_config.get("MIKROSTEPS", 2))
            self.motor_control.set_motor_resolution(SHUTTER_MOTOR, micro_steps)
            
            # Set current
            fahrstrom = int(shutter_config.get("Fahrstrom", 80))
            haltestrom = int(shutter_config.get("Haltestrom", 10))
            self.motor_control.set_max_current(SHUTTER_MOTOR, fahrstrom)
            self.motor_control.set_standby_current(SHUTTER_MOTOR, haltestrom)
            
            # Set acceleration
            beschleunigung = int(shutter_config.get("Beschleunigung", 500))
            self.motor_control.set_max_acceleration(SHUTTER_MOTOR, beschleunigung)
            
            # Set reference speeds
            ref_speed1 = int(shutter_config.get("ReferenceSpeed1", 50))
            ref_speed2 = int(shutter_config.get("ReferenceSpeed2", 10))
            self.motor_control.set_reference_speeds(SHUTTER_MOTOR, ref_speed1, ref_speed2)
        
        # Configure film motor
        if "FILM" in self.trinamic_config:
            film_config = self.trinamic_config["FILM"]
            
            # Set microstepping resolution
            micro_steps = int(film_config.get("MIKROSTEPS", 2))
            self.motor_control.set_motor_resolution(FILM_MOTOR, micro_steps)
            
            # Set current
            fahrstrom = int(film_config.get("Fahrstrom", 120))
            haltestrom = int(film_config.get("Haltestrom", 10))
            self.motor_control.set_max_current(FILM_MOTOR, fahrstrom)
            self.motor_control.set_standby_current(FILM_MOTOR, haltestrom)
            
            # Set acceleration
            beschleunigung = int(film_config.get("Beschleunigung", 600))
            self.motor_control.set_max_acceleration(FILM_MOTOR, beschleunigung)
    
    def get_job_settings(self):
        """Extract needed settings from job configuration"""
        settings = {}
        
        if "TEMPLATE" in self.job_config:
            job_template = self.job_config["TEMPLATE"]
            
            # Get exposure settings
            settings["shutter_speed"] = int(job_template.get("VerschlussGeschw", 160))
            settings["exposure"] = int(job_template.get("BELICHTUNG", 1))
            settings["additional_exposure"] = float(job_template.get("ZusatzBelichtung", 0))
            
            # Get film advancement setting (StepsImageToImage if available, or use default)
            settings["steps_per_frame"] = int(job_template.get("StepsImageToImage", 1000))
        
        return settings
    
    def simulate_vacuum_on(self):
        """Simulate turning vacuum on and waiting for vacuum to stabilize"""
        print("Turning vacuum on...")
        time.sleep(0.5)  # Simulate time for vacuum to turn on
        print("Vacuum stable")
        return True
    
    def simulate_vacuum_off(self):
        """Simulate turning vacuum off"""
        print("Releasing vacuum...")
        time.sleep(0.2)  # Simulate time for vacuum to release
        print("Vacuum released")
        return True
    
    def execute_shutter_movement(self, exposure_time, shutter_speed):
        """Execute the shutter movement for exposure"""
        print(f"Opening shutter at speed {shutter_speed}...")
        
        if not self.simulation_mode and self.motor_control:
            # Move shutter motor for exposure
            steps = self.get_job_settings().get("exposure", 1)
            self.motor_control.set_target_speed(SHUTTER_MOTOR, shutter_speed)
            self.motor_control.move_motor(SHUTTER_MOTOR, steps)
            
            # Wait for shutter movement to complete
            while self.motor_control.is_motor_running(SHUTTER_MOTOR):
                time.sleep(0.05)
        else:
            # Simulate shutter movement time
            time.sleep(0.5)
        
        # For two-part exposure with additional delay in between
        additional_exposure = self.get_job_settings().get("additional_exposure", 0)
        if additional_exposure > 0:
            print(f"Additional exposure delay: {additional_exposure} seconds")
            time.sleep(additional_exposure)
            
            if not self.simulation_mode and self.motor_control:
                # Second part of exposure
                self.motor_control.move_motor(SHUTTER_MOTOR, steps)
                while self.motor_control.is_motor_running(SHUTTER_MOTOR):
                    time.sleep(0.05)
            else:
                # Simulate second exposure movement
                time.sleep(0.5)
        
        print("Shutter cycle complete")
    
    def advance_film(self):
        """Advance the film to the next frame"""
        steps = self.get_job_settings().get("steps_per_frame", 1000)
        print(f"Advancing film by {steps} steps...")
        
        if not self.simulation_mode and self.motor_control:
            # Set film speed based on job configuration
            film_speed = 500  # Default value, should be extracted from job_config
            self.motor_control.set_target_speed(FILM_MOTOR, film_speed)
            
            # Move film motor
            self.motor_control.move_motor(FILM_MOTOR, steps)
            
            # Wait for film movement to complete
            while self.motor_control.is_motor_running(FILM_MOTOR):
                time.sleep(0.05)
        else:
            # Simulate film advancement time based on steps
            time.sleep(steps / 2000)  # Rough simulation
        
        print("Film advanced to next frame")
    
    def execute_exposure_sequence(self, num_documents=10):
        """Execute a complete exposure sequence for multiple documents"""
        print(f"\nStarting exposure sequence for {num_documents} documents\n")
        
        # Get settings from job configuration
        settings = self.get_job_settings()
        shutter_speed = settings.get("shutter_speed", 160)
        
        # Execute exposure sequence for each document
        for doc_num in range(1, num_documents + 1):
            print(f"\n--- Document {doc_num}/{num_documents} ---")
            
            # 1. Apply vacuum
            self.simulate_vacuum_on()
            
            # 2. Execute shutter movement (exposure)
            self.execute_shutter_movement(settings.get("exposure", 1), shutter_speed)
            
            # 3. Release vacuum
            self.simulate_vacuum_off()
            
            # 4. Advance film to next frame
            self.advance_film()
            
            # Slight pause between documents
            time.sleep(0.2)
        
        print("\nExposure sequence completed for all documents")
    
    def cleanup(self):
        """Clean up resources and disconnect"""
        if not self.simulation_mode and self.controller:
            self.controller.disconnect()
            print("Controller disconnected")


def main():
    """Main function to demonstrate exposure simulation"""
    # Create simulator in simulation mode (no hardware connection)
    simulator = ExposureSimulator(simulation_mode=False)  # Set to False to use real hardware
    
    # Print loaded configuration details
    print("\nConfiguration Summary:")
    
    # Trinamic.ini summary
    if simulator.trinamic_config:
        print("\nShutter Motor Settings:")
        if "VERSCHLUSS" in simulator.trinamic_config:
            for key, value in simulator.trinamic_config["VERSCHLUSS"].items():
                print(f"  {key} = {value}")
        
        print("\nFilm Motor Settings:")
        if "FILM" in simulator.trinamic_config:
            for key, value in simulator.trinamic_config["FILM"].items():
                print(f"  {key} = {value}")
    
    # Job settings summary
    settings = simulator.get_job_settings()
    print("\nJob Settings:")
    for key, value in settings.items():
        print(f"  {key} = {value}")
    
    # Execute exposure sequence for 10 documents
    simulator.execute_exposure_sequence(10)
    
    # Clean up
    simulator.cleanup()


if __name__ == "__main__":
    main()
