"""
Configuration Manager

Loads configuration from INI files and applies settings to the controller.
"""

import os
import configparser
from .logger import logger
from .motor_control import MotorControl

class ConfigManager:
    """
    Configuration manager for Trinamic controllers
    """
    
    # Motor number constants
    MOTOR_SHUTTER = 0  # Verschluss motor
    MOTOR_FILM = 1     # Film motor
    
    def __init__(self, config_path=None, verbose=True):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the config file. If None, will look in standard locations.
            verbose: Whether to log detailed information. Set to False for JSON output.
        """
        self.config = configparser.ConfigParser()
        self.verbose = verbose
        
        # Find config file if not specified
        if config_path is None:
            # Try to find config in standard locations
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'config', 'trinamic.ini'),
                os.path.join(os.path.dirname(__file__), '..', 'trinamic.ini'),
                'trinamic.ini'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        # Load config from file
        if config_path and os.path.exists(config_path):
            if self.verbose:
                logger.info("CONFIG", f"Loading configuration from: {config_path}")
            self.config.read(config_path)
            self.config_path = config_path
        else:
            if self.verbose:
                logger.warn("CONFIG", "No configuration file found, using defaults")
            self.config_path = None
            
            # Set default values
            self.config['VERSCHLUSS'] = {
                'BESCHLEUNIGUNG': '500',
                'FAHRSTROM': '80',
                'HALTESTROM': '10',
                'MIKROSTEPS': '2',
                'ReferenceSpeed1': '50',
                'ReferenceSpeed2': '10'
            }
            
            self.config['FILM'] = {
                'BESCHLEUNIGUNG': '600',
                'FAHRSTROM': '120',
                'HALTESTROM': '10',
                'MIKROSTEPS': '2'
            }
            
            self.config['SYSTEM'] = {
                'FILM_SPEED': '4000',
                'STEPS_PER_ROTATION': '1600',
                'STEPS_PER_MM_16MM': '139',
                'STEPS_PER_MM_35MM': '140'
            }
    
    def get_shutter_config(self):
        """Get configuration values for shutter motor"""
        section = self.config['VERSCHLUSS']
        return {
            'acceleration': int(section.get('BESCHLEUNIGUNG', 500)),
            'drive_current': int(section.get('FAHRSTROM', 80)),
            'hold_current': int(section.get('HALTESTROM', 10)),
            'microsteps': int(section.get('MIKROSTEPS', 2)),
            'ref_speed1': int(section.get('ReferenceSpeed1', 50)),
            'ref_speed2': int(section.get('ReferenceSpeed2', 10))
        }
    
    def get_film_config(self):
        """Get configuration values for film motor"""
        section = self.config['FILM']
        return {
            'acceleration': int(section.get('BESCHLEUNIGUNG', 600)),
            'drive_current': int(section.get('FAHRSTROM', 120)),
            'hold_current': int(section.get('HALTESTROM', 10)),
            'microsteps': int(section.get('MIKROSTEPS', 2))
        }
    
    def get_system_config(self):
        """Get system configuration values"""
        # Check if SYSTEM section exists
        if 'SYSTEM' not in self.config:
            if self.verbose:
                logger.warn("CONFIG", "No SYSTEM section found in config, using defaults")
            return {
                'film_speed': 4000,
                'steps_per_rotation': 1600,
                'steps_per_mm_16mm': 139,
                'steps_per_mm_35mm': 140
            }
            
        # If section exists, get values from it
        section = self.config['SYSTEM']
        return {
            'film_speed': int(section.get('FILM_SPEED', 4000)),
            'steps_per_rotation': int(section.get('STEPS_PER_ROTATION', 1600)),
            'steps_per_mm_16mm': int(section.get('STEPS_PER_MM_16MM', 139)),
            'steps_per_mm_35mm': int(section.get('STEPS_PER_MM_35MM', 140))
        }
    
    def apply_motor_config(self, motor_control):
        """
        Apply the configuration to the motors
        
        Args:
            motor_control: MotorControl instance
        """
        if not isinstance(motor_control, MotorControl):
            raise TypeError("motor_control must be an instance of MotorControl")
        
        # Apply shutter motor configuration
        if self.verbose:
            logger.info("CONFIG", "Applying shutter motor configuration...")
        shutter_config = self.get_shutter_config()
        motor_control.set_motor_resolution(self.MOTOR_SHUTTER, shutter_config['microsteps'])
        motor_control.set_max_acceleration(self.MOTOR_SHUTTER, shutter_config['acceleration'])
        motor_control.set_max_current(self.MOTOR_SHUTTER, shutter_config['drive_current'])
        motor_control.set_standby_current(self.MOTOR_SHUTTER, shutter_config['hold_current'])
        motor_control.set_reference_speeds(
            self.MOTOR_SHUTTER, 
            shutter_config['ref_speed1'], 
            shutter_config['ref_speed2']
        )
        
        # Apply film motor configuration
        if self.verbose:
            logger.info("CONFIG", "Applying film motor configuration...")
        film_config = self.get_film_config()
        motor_control.set_motor_resolution(self.MOTOR_FILM, film_config['microsteps'])
        motor_control.set_max_acceleration(self.MOTOR_FILM, film_config['acceleration'])
        motor_control.set_max_current(self.MOTOR_FILM, film_config['drive_current'])
        motor_control.set_standby_current(self.MOTOR_FILM, film_config['hold_current'])
        # Note: Film motor doesn't get reference speeds in the original VB.NET code
        
        if self.verbose:
            logger.info("CONFIG", "Motor configuration applied successfully")
        return True
        
    def save_config(self, path=None):
        """
        Save the current configuration to a file
        
        Args:
            path: Path to save to. If None, uses the original path.
        """
        save_path = path or self.config_path
        if not save_path:
            save_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'trinamic.ini')
            
        if self.verbose:
            logger.info("CONFIG", f"Saving configuration to: {save_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as config_file:
            self.config.write(config_file)
        
        return save_path 
    
    def to_dict(self):
        """
        Convert configuration to a dictionary suitable for JSON serialization
        
        Returns:
            dict: Configuration as a dictionary
        """
        return {
            'shutter': self.get_shutter_config(),
            'film': self.get_film_config(),
            'system': self.get_system_config()
        } 