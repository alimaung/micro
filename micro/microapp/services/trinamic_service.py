"""
Trinamic Service - Django service layer for Trinamic machine control.

This service provides the Django integration layer for the Trinamic controller,
handling motor control, I/O operations, and machine state management.
"""

import logging
import sys
import os
import time
import threading
from typing import Dict, Any, Optional
from django.conf import settings

# Add the trinamic control modules to the path
trinamic_path = os.path.join(settings.BASE_DIR, '..', 'sma', 'trinamic', 'trinamic_control')
if trinamic_path not in sys.path:
    sys.path.append(trinamic_path)

try:
    from src.trinamic_controller import TrinamicController
    from src.io_control import IOControl, MachineState
    from src.motor_control import MotorControl
except ImportError as e:
    logging.error(f"Failed to import Trinamic modules: {e}")
    TrinamicController = None
    IOControl = None
    MotorControl = None
    MachineState = None

logger = logging.getLogger(__name__)

class TrinamicService:
    """Service for managing Trinamic machine operations."""
    
    def __init__(self, port='COM3', baudrate=9600, address=1):
        """
        Initialize the Trinamic service.
        
        Args:
            port (str): Serial port for the Trinamic controller
            baudrate (int): Baud rate for communication
            address (int): Controller address
        """
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.controller = None
        self.io_control = None
        self.motor_control = None
        self._connected = False
        self._last_activity = None
        self._timeout_seconds = 30
        self._cleanup_timer = None
        self._lock = threading.Lock()
        
        if not TrinamicController:
            logger.error("Trinamic modules not available - controller will not function")
    
    def _update_activity(self):
        """Update the last activity timestamp and reset timeout timer."""
        with self._lock:
            self._last_activity = time.time()
            
            # Cancel existing cleanup timer
            if self._cleanup_timer:
                self._cleanup_timer.cancel()
            
            # Start new cleanup timer
            if self._connected:
                self._cleanup_timer = threading.Timer(self._timeout_seconds, self._timeout_disconnect)
                self._cleanup_timer.start()
    
    def _timeout_disconnect(self):
        """Disconnect due to inactivity timeout."""
        logger.info(f"Trinamic connection timed out after {self._timeout_seconds} seconds of inactivity")
        self.disconnect()
    
    def connect(self) -> Dict[str, Any]:
        """
        Connect to the Trinamic controller.
        
        Returns:
            Dict with success status and message
        """
        try:
            if not TrinamicController:
                return {
                    'success': False,
                    'message': 'Trinamic modules not available'
                }
            
            # If already connected, just update activity
            if self._connected and self.controller:
                self._update_activity()
                return {
                    'success': True,
                    'message': f'Already connected to {self.port}',
                    'port': self.port
                }
            
            # Create new connection
            self.controller = TrinamicController(
                port=self.port,
                baudrate=self.baudrate,
                address=self.address,
                verbose=True
            )
            
            if self.controller.connect():
                self.io_control = IOControl(self.controller)
                self.motor_control = MotorControl(self.controller)
                self._connected = True
                self._update_activity()
                
                logger.info(f"Connected to Trinamic controller on {self.port}")
                return {
                    'success': True,
                    'message': f'Connected to {self.port}',
                    'port': self.port
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to connect to {self.port}'
                }
                
        except Exception as e:
            logger.error(f"Error connecting to Trinamic controller: {e}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """
        Disconnect from the Trinamic controller.
        
        Returns:
            Dict with success status and message
        """
        try:
            with self._lock:
                # Cancel cleanup timer
                if self._cleanup_timer:
                    self._cleanup_timer.cancel()
                    self._cleanup_timer = None
                
                # Disconnect controller
                if self.controller:
                    self.controller.disconnect()
                    self.controller = None
                    self.io_control = None
                    self.motor_control = None
                    self._connected = False
                    self._last_activity = None
                    
                    logger.info("Disconnected from Trinamic controller")
                    return {
                        'success': True,
                        'message': 'Disconnected successfully'
                    }
                else:
                    return {
                        'success': True,
                        'message': 'Already disconnected'
                    }
                    
        except Exception as e:
            logger.error(f"Error disconnecting from Trinamic controller: {e}")
            return {
                'success': False,
                'message': f'Disconnect error: {str(e)}'
            }
    
    def is_connected(self) -> bool:
        """Check if connected to the controller."""
        return self._connected and self.controller is not None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get the current connection status."""
        with self._lock:
            time_since_activity = None
            if self._last_activity:
                time_since_activity = time.time() - self._last_activity
                
            return {
                'connected': self.is_connected(),
                'port': self.port if self.is_connected() else None,
                'baudrate': self.baudrate if self.is_connected() else None,
                'timeout_seconds': self._timeout_seconds,
                'time_since_activity': time_since_activity
            }
    
    # === I/O Control Methods ===
    
    def vacuum_on(self) -> Dict[str, Any]:
        """Turn on the vacuum."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.vacuum_on_json()
        except Exception as e:
            logger.error(f"Error turning on vacuum: {e}")
            return {'success': False, 'message': str(e)}
    
    def vacuum_off(self) -> Dict[str, Any]:
        """Turn off the vacuum."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.vacuum_off_json()
        except Exception as e:
            logger.error(f"Error turning off vacuum: {e}")
            return {'success': False, 'message': str(e)}
    
    def is_vacuum_ok(self) -> Dict[str, Any]:
        """Check vacuum status."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.is_vacuum_ok_json()
        except Exception as e:
            logger.error(f"Error checking vacuum status: {e}")
            return {'success': False, 'message': str(e)}
    
    def led_on(self) -> Dict[str, Any]:
        """Turn on the LED."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.io_control.led_on()
            return {
                'success': True if result else False,
                'led': 'on',
                'result': result
            }
        except Exception as e:
            logger.error(f"Error turning on LED: {e}")
            return {'success': False, 'message': str(e)}
    
    def led_off(self) -> Dict[str, Any]:
        """Turn off the LED."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.io_control.led_off()
            return {
                'success': True if result else False,
                'led': 'off',
                'result': result
            }
        except Exception as e:
            logger.error(f"Error turning off LED: {e}")
            return {'success': False, 'message': str(e)}
    
    def magnet_on(self) -> Dict[str, Any]:
        """Turn on the magnet."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.magnet_on_json()
        except Exception as e:
            logger.error(f"Error turning on magnet: {e}")
            return {'success': False, 'message': str(e)}
    
    def magnet_off(self) -> Dict[str, Any]:
        """Turn off the magnet."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.magnet_off_json()
        except Exception as e:
            logger.error(f"Error turning off magnet: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_machine_state(self) -> Dict[str, Any]:
        """Get the current machine state."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.io_control.get_machine_state_json()
        except Exception as e:
            logger.error(f"Error getting machine state: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_light_sensor(self) -> Dict[str, Any]:
        """Get light sensor reading."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            value = self.io_control.get_light_sensor()
            return {
                'success': True,
                'light_sensor_value': value
            }
        except Exception as e:
            logger.error(f"Error reading light sensor: {e}")
            return {'success': False, 'message': str(e)}
    
    def is_at_zero_point(self) -> Dict[str, Any]:
        """Check if at zero point."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            at_zero = self.io_control.is_at_zero_point()
            return {
                'success': True,
                'at_zero_point': at_zero
            }
        except Exception as e:
            logger.error(f"Error checking zero point: {e}")
            return {'success': False, 'message': str(e)}
    
    # === Motor Control Methods ===
    
    def move_motor(self, motor: int, steps: int, direction: int = 1) -> Dict[str, Any]:
        """Move a motor by the specified number of steps."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.motor_control.move_motor_json(motor, steps, direction)
        except Exception as e:
            logger.error(f"Error moving motor {motor}: {e}")
            return {'success': False, 'message': str(e)}
    
    def stop_motor(self, motor: int) -> Dict[str, Any]:
        """Stop the specified motor."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.motor_control.stop_motor_json(motor)
        except Exception as e:
            logger.error(f"Error stopping motor {motor}: {e}")
            return {'success': False, 'message': str(e)}
    
    def is_motor_running(self, motor: int) -> Dict[str, Any]:
        """Check if a motor is running."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.motor_control.is_motor_running_json(motor)
        except Exception as e:
            logger.error(f"Error checking motor {motor} status: {e}")
            return {'success': False, 'message': str(e)}
    
    def move_to_home_position(self, motor: int) -> Dict[str, Any]:
        """Move motor to home position."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            return self.motor_control.move_to_home_position_json(motor)
        except Exception as e:
            logger.error(f"Error homing motor {motor}: {e}")
            return {'success': False, 'message': str(e)}
    
    def set_motor_speed(self, motor: int, speed: int) -> Dict[str, Any]:
        """Set motor speed."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.motor_control.set_target_speed(motor, speed)
            return {
                'success': True if result else False,
                'motor': motor,
                'speed': speed,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error setting motor {motor} speed: {e}")
            return {'success': False, 'message': str(e)}
    
    def set_motor_current(self, motor: int, current: int) -> Dict[str, Any]:
        """Set motor current."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.motor_control.set_max_current(motor, current)
            return {
                'success': True if result else False,
                'motor': motor,
                'current': current,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error setting motor {motor} current: {e}")
            return {'success': False, 'message': str(e)}
    
    def set_motor_standby_current(self, motor: int, standby_current: int) -> Dict[str, Any]:
        """Set motor standby current."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.motor_control.set_standby_current(motor, standby_current)
            return {
                'success': True if result else False,
                'motor': motor,
                'standby_current': standby_current,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error setting motor {motor} standby current: {e}")
            return {'success': False, 'message': str(e)}
    
    def set_motor_acceleration(self, motor: int, acceleration: int) -> Dict[str, Any]:
        """Set motor acceleration."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.motor_control.set_max_acceleration(motor, acceleration)
            return {
                'success': True if result else False,
                'motor': motor,
                'acceleration': acceleration,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error setting motor {motor} acceleration: {e}")
            return {'success': False, 'message': str(e)}
    
    def set_motor_resolution(self, motor: int, resolution: int) -> Dict[str, Any]:
        """Set motor microstepping resolution."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            result = self.motor_control.set_motor_resolution(motor, resolution)
            return {
                'success': True if result else False,
                'motor': motor,
                'resolution': resolution,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error setting motor {motor} resolution: {e}")
            return {'success': False, 'message': str(e)}
    
    # === Convenience Methods ===
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        if not self.is_connected():
            return {'success': False, 'message': 'Not connected to controller'}
        
        self._update_activity()
        try:
            # Get machine state
            machine_state = self.get_machine_state()
            
            # Get vacuum status
            vacuum_status = self.is_vacuum_ok()
            
            # Get zero point status
            zero_point = self.is_at_zero_point()
            
            # Get light sensor
            light_sensor = self.get_light_sensor()
            
            # Check motor status for motors 0 and 1
            motor_statuses = {}
            for motor in [0, 1]:
                motor_statuses[f'motor_{motor}'] = self.is_motor_running(motor)
            
            return {
                'success': True,
                'machine_state': machine_state,
                'vacuum_status': vacuum_status,
                'zero_point': zero_point,
                'light_sensor': light_sensor,
                'motor_statuses': motor_statuses,
                'connection': self.get_connection_status()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'success': False, 'message': str(e)}

# Global service instance
_trinamic_service = None

def get_trinamic_service(port='COM3', baudrate=9600, address=1) -> TrinamicService:
    """Get or create a global Trinamic service instance."""
    global _trinamic_service
    
    if _trinamic_service is None:
        _trinamic_service = TrinamicService(port, baudrate, address)
    
    return _trinamic_service 