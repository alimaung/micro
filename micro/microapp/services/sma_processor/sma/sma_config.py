"""
Configuration Management Module for SMA (film scanning) automation system.

This module handles all configuration-related operations including command line
argument parsing, configuration file management, and system path setup.
"""

import configparser
import argparse
import os
from .sma_exceptions import SMAConfigurationError, SMAFileError, SMAINIError, SMATemplateError

class SMAConfig:
    """Configuration manager for SMA automation system."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config = {}
        self.template_map = {
            '16': "16mm.TPL",
            '35': "35mm.TPL"
        }
        
    def parse_arguments(self, args=None):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='File Converter Automation Script')
        parser.add_argument('folder_path', help='Path to the folder to process')
        parser.add_argument('template', choices=['16', '35'], 
                          help='Template to use: 16 for Portrait - 16mm.TPL, 35 for Landscape - 35mm.TPL')
        parser.add_argument('--filmnumber', help='Custom film number to use (default: folder name)')
        parser.add_argument('--recovery', action='store_true', 
                          help='Attempt to recover and continue an existing scanning session')
        
        if args is None:
            return parser.parse_args()
        else:
            return parser.parse_args(args)
    
    def load_configuration(self, args):
        """Load configuration parameters from arguments."""
        try:
            # Create configuration dictionary
            self.config = {
                'template_name': self.template_map[args.template],
                'ini_file_path': r"Y:\SMA\file-converter-64\docufileuc.ini",
                'folder_path': args.folder_path,
                'app_path': r"Y:\SMA\file-converter-64\file-sma.exe",
                'templates_dir': r"Y:\SMA\file-converter-64\TEMPLATES",
                'custom_filmnumber': args.filmnumber,
                'recovery_mode': args.recovery
            }
            
            # Validate paths exist
            self._validate_paths()
            
            return self.config
            
        except Exception as e:
            raise SMAConfigurationError(
                message=f"Failed to load configuration: {str(e)}",
                details={'args': vars(args)}
            )
    
    def _validate_paths(self):
        """Validate that required paths exist."""
        required_paths = [
            ('app_path', 'SMA application'),
            ('templates_dir', 'Templates directory'),
            ('folder_path', 'Source folder')
        ]
        
        missing_paths = []
        for path_key, description in required_paths:
            if path_key in self.config:
                path = self.config[path_key]
                if not os.path.exists(path):
                    missing_paths.append(f"{description}: {path}")
        
        if missing_paths:
            raise SMAConfigurationError(
                message="Required paths do not exist",
                details={'missing_paths': missing_paths}
            )
    
    def create_log_directory(self, folder_path, logger):
        """Create filmlogs directory in the parent folder of the selected folder."""
        try:
            # Get parent of parent folder
            parent_folder = os.path.dirname(os.path.dirname(folder_path))
            filmlogs_dir = os.path.join(parent_folder, ".filmlogs")
            
            # Create the filmlogs directory if it doesn't exist
            if not os.path.exists(filmlogs_dir):
                os.makedirs(filmlogs_dir)
                logger.info(f"Created filmlogs directory: {filmlogs_dir}")
            else:
                logger.info(f"Using existing filmlogs directory: {filmlogs_dir}")
            
            return filmlogs_dir, parent_folder
            
        except Exception as e:
            raise SMAFileError(
                file_path=folder_path,
                operation="create_log_directory",
                message=f"Failed to create log directory: {str(e)}"
            )
    
    def update_template_file(self, template_path, log_dir, template_name, logger):
        """Edit TPL file with the log file path."""
        try:
            # Read the TPL file
            with open(template_path, 'r', encoding='cp1252') as tpl_file:
                tpl_lines = tpl_file.readlines()
            
            # Replace the LOGFILEPATH
            updated_lines = []
            
            for line in tpl_lines:
                if line.startswith('LOGFILEPATH='):
                    updated_lines.append(f'LOGFILEPATH={log_dir}\n')
                else:
                    updated_lines.append(line)
            
            # Write the updated content back to the file
            with open(template_path, 'w', encoding='cp1252') as tpl_file:
                tpl_file.writelines(updated_lines)
            
            logger.info(f"Updated LOGFILEPATH in {template_name} to {log_dir}")
            return True
            
        except Exception as e:
            raise SMATemplateError(
                template_name=template_name,
                message=f"Error updating TPL file: {str(e)}",
                details={'template_path': template_path, 'log_dir': log_dir}
            )
    
    def update_ini_file(self, ini_path, folder_path, logger):
        """Update INI file with folder path."""
        try:
            # Create a ConfigParser object
            config = configparser.ConfigParser()
            
            # Open the INI file with UTF-16 encoding
            with open(ini_path, 'r', encoding='utf-16') as configfile:
                config.read_file(configfile)
            
            # Modify the PFAD entry under the SYSTEM section
            config.set('SYSTEM', 'PFAD', folder_path)
            
            # Save the changes back to the INI file
            with open(ini_path, 'w', encoding='utf-16') as configfile:
                config.write(configfile)
            
            logger.info(f"PFAD updated to: {folder_path}")
            return True
            
        except Exception as e:
            raise SMAINIError(
                ini_path=ini_path,
                message=f"Error updating INI file: {str(e)}",
                details={'folder_path': folder_path}
            )
    
    def get_template_path(self, template_name):
        """Get the full path to a template file."""
        if 'templates_dir' not in self.config:
            raise SMAConfigurationError(
                config_item='templates_dir',
                message="Templates directory not configured"
            )
        
        template_path = os.path.join(self.config['templates_dir'], template_name)
        
        if not os.path.exists(template_path):
            raise SMATemplateError(
                template_name=template_name,
                message=f"Template file not found: {template_path}"
            )
        
        return template_path
    
    def get_film_number(self, folder_path, custom_filmnumber=None):
        """Determine the film number to use."""
        if custom_filmnumber:
            return custom_filmnumber
        else:
            # Extract the folder name from the selected folder path
            return os.path.basename(folder_path)
    
    def get_config_value(self, key, default=None):
        """Get a configuration value by key."""
        return self.config.get(key, default)
    
    def set_config_value(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
    
    def get_all_config(self):
        """Get all configuration values."""
        return self.config.copy()
    
    def validate_template_choice(self, template_choice):
        """Validate that the template choice is valid."""
        if template_choice not in self.template_map:
            raise SMAConfigurationError(
                config_item='template',
                message=f"Invalid template choice: {template_choice}. Must be one of: {list(self.template_map.keys())}"
            )
        return self.template_map[template_choice]

# Convenience functions for backward compatibility
def parse_arguments():
    """Parse command line arguments."""
    config_manager = SMAConfig()
    return config_manager.parse_arguments()

def load_configuration(args):
    """Load configuration parameters."""
    config_manager = SMAConfig()
    return config_manager.load_configuration(args)

def create_log_directory(folder_path, logger):
    """Create filmlogs directory in the parent folder of the selected folder."""
    config_manager = SMAConfig()
    return config_manager.create_log_directory(folder_path, logger)

def update_template_file(template_path, log_dir, template_name, logger):
    """Edit TPL file with the log file path."""
    config_manager = SMAConfig()
    return config_manager.update_template_file(template_path, log_dir, template_name, logger)

def update_ini_file(ini_path, folder_path, logger):
    """Update INI file with folder path."""
    config_manager = SMAConfig()
    return config_manager.update_ini_file(ini_path, folder_path, logger) 