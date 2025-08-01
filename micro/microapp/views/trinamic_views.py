"""
Trinamic control views for the microapp.
These views handle interaction with the Trinamic machine controller.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ..services.trinamic_service import get_trinamic_service

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def trinamic_connect(request):
    """Connect to the Trinamic controller."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            port = data.get('port', 'COM3')
            baudrate = data.get('baudrate', 9600)
            address = data.get('address', 1)
            
            service = get_trinamic_service(port, baudrate, address)
            result = service.connect()
            
            return JsonResponse({
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_connect: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Connection error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def trinamic_disconnect(request):
    """Disconnect from the Trinamic controller."""
    if request.method == 'POST':
        try:
            service = get_trinamic_service()
            result = service.disconnect()
            
            return JsonResponse({
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_disconnect: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Disconnect error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def trinamic_status(request):
    """Get Trinamic controller status."""
    if request.method == 'GET':
        try:
            service = get_trinamic_service()
            
            if service.is_connected():
                result = service.get_system_status()
            else:
                result = {
                    'success': False,
                    'message': 'Not connected',
                    'connection': service.get_connection_status()
                }
            
            return JsonResponse({
                'status': 'success',
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_status: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Status error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def trinamic_io_control(request):
    """Control I/O operations (vacuum, LED, magnet)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            action = data.get('action')
            device = data.get('device')
            
            service = get_trinamic_service()
            
            if not service.is_connected():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not connected to controller'
                })
            
            result = None
            
            # Handle vacuum operations
            if device == 'vacuum':
                if action == 'on':
                    result = service.vacuum_on()
                elif action == 'off':
                    result = service.vacuum_off()
                elif action == 'status':
                    result = service.is_vacuum_ok()
            
            # Handle LED operations
            elif device == 'led':
                if action == 'on':
                    result = service.led_on()
                elif action == 'off':
                    result = service.led_off()
            
            # Handle magnet operations
            elif device == 'magnet':
                if action == 'on':
                    result = service.magnet_on()
                elif action == 'off':
                    result = service.magnet_off()
            
            # Handle sensor readings
            elif device == 'light_sensor' and action == 'read':
                result = service.get_light_sensor()
            
            elif device == 'zero_point' and action == 'check':
                result = service.is_at_zero_point()
                
            elif device == 'machine_state' and action == 'get':
                result = service.get_machine_state()
            
            if result is None:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Invalid action {action} for device {device}'
                })
            
            return JsonResponse({
                'status': 'success' if result.get('success', False) else 'error',
                'message': result.get('message', 'Operation completed'),
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_io_control: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'I/O control error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def trinamic_motor_control(request):
    """Control motor operations."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            action = data.get('action')
            motor = data.get('motor', 0)
            
            service = get_trinamic_service()
            
            if not service.is_connected():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not connected to controller'
                })
            
            result = None
            
            if action == 'move':
                steps = data.get('steps', 100)
                direction = data.get('direction', 1)
                result = service.move_motor(motor, steps, direction)
                
            elif action == 'stop':
                result = service.stop_motor(motor)
                
            elif action == 'home':
                result = service.move_to_home_position(motor)
                
            elif action == 'status':
                result = service.is_motor_running(motor)
                
            elif action == 'set_speed':
                speed = data.get('speed', 100)
                result = service.set_motor_speed(motor, speed)
                
            elif action == 'set_current':
                current = data.get('current', 200)
                result = service.set_motor_current(motor, current)
                
            elif action == 'set_standby_current':
                standby_current = data.get('standby_current', 10)
                result = service.set_motor_standby_current(motor, standby_current)
                
            elif action == 'set_acceleration':
                acceleration = data.get('acceleration', 500)
                result = service.set_motor_acceleration(motor, acceleration)
                
            elif action == 'set_resolution':
                resolution = data.get('resolution', 2)
                result = service.set_motor_resolution(motor, resolution)
            
            if result is None:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Invalid motor action: {action}'
                })
            
            return JsonResponse({
                'status': 'success' if result.get('success', False) else 'error',
                'message': result.get('message', 'Motor operation completed'),
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_motor_control: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Motor control error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def trinamic_system_status(request):
    """Get comprehensive system status."""
    if request.method == 'GET':
        try:
            service = get_trinamic_service()
            result = service.get_system_status()
            
            return JsonResponse({
                'status': 'success' if result.get('success', False) else 'error',
                'message': result.get('message', 'Status retrieved'),
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_system_status: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'System status error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def trinamic_emergency_stop(request):
    """Emergency stop all motors."""
    if request.method == 'POST':
        try:
            service = get_trinamic_service()
            
            if not service.is_connected():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not connected to controller'
                })
            
            # Stop both motors (0 and 1)
            results = []
            for motor in [0, 1]:
                result = service.stop_motor(motor)
                results.append(f"Motor {motor}: {'stopped' if result.get('success') else 'failed'}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Emergency stop executed',
                'data': {
                    'results': results,
                    'success': True
                }
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_emergency_stop: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Emergency stop error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required  
def trinamic_configure(request):
    """Configure Trinamic controller parameters."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            
            service = get_trinamic_service()
            
            if not service.is_connected():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Not connected to controller'
                })
            
            # Configure motors based on provided parameters
            motor_configs = data.get('motors', {})
            results = {}
            
            for motor_str, config in motor_configs.items():
                motor = int(motor_str)
                motor_results = {}
                
                if 'speed' in config:
                    result = service.set_motor_speed(motor, config['speed'])
                    motor_results['speed'] = result
                
                if 'current' in config:
                    result = service.set_motor_current(motor, config['current'])
                    motor_results['current'] = result
                    
                if 'acceleration' in config:
                    result = service.set_motor_acceleration(motor, config['acceleration'])
                    motor_results['acceleration'] = result
                    
                if 'resolution' in config:
                    result = service.set_motor_resolution(motor, config['resolution'])
                    motor_results['resolution'] = result
                
                results[f'motor_{motor}'] = motor_results
            
            return JsonResponse({
                'status': 'success',
                'message': 'Configuration applied',
                'data': {
                    'results': results,
                    'success': True
                }
            })
            
        except Exception as e:
            logger.error(f"Error in trinamic_configure: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Configuration error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 