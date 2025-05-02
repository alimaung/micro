"""
Machine control and status views for the microapp.
These views handle interaction with the Trinamic machine controller.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import serial.tools.list_ports
from ..machine_test import check_machine_power, MachineController

def list_com_ports():
    """List available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

@csrf_exempt
def check_port(request):
    """
    API endpoint to check if a COM port is available and get its details.
    
    Args:
        port: The COM port to check (POST parameter)
    
    Returns:
        JSON response with port details or error
    """
    if request.method == 'POST':
        port = request.POST.get('port', '')
        
        # Get the list of available COM ports
        available_ports = list_com_ports()
        
        # Check if requested port is available
        port_info = next((p for p in serial.tools.list_ports.comports() if p.device == port), None)
        
        if port_info:
            # Port is available, extract detailed information
            device_info = {
                'port': port_info.device,
                'description': port_info.description,
                'vendor_id': f"0x{port_info.vid:04X}" if port_info.vid else "N/A",
                'product_id': f"0x{port_info.pid:04X}" if port_info.pid else "N/A",
                'manufacturer': port_info.manufacturer or "N/A",
                'product': port_info.product or "N/A",
                'serial_number': port_info.serial_number or "N/A"
            }
            
            return JsonResponse({
                'status': 'success',
                'message': f'Port {port} is available',
                'port': port,
                'device_info': device_info
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Port {port} is not available'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def check_machine_state(request):
    """
    API endpoint to check if the machine is actually powered on.
    
    Args:
        port: The COM port to use (POST parameter, defaults to COM3)
    
    Returns:
        JSON response with machine power state
    """
    if request.method == 'POST':
        port = request.POST.get('port', 'COM3')  # Default to COM3
        
        try:
            # Use the machine_test module to check power state
            is_on = check_machine_power(port)
            
            return JsonResponse({
                'status': 'success',
                'is_on': is_on,
                'message': f'Machine is {"ON" if is_on else "OFF"}'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error checking machine power: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

def get_machine_stats(request):
    """
    API endpoint to get detailed machine statistics using TMCL commands.
    
    Args:
        port: The COM port to use (POST parameter, defaults to COM3)
    
    Returns:
        JSON response with detailed machine statistics
    """
    if request.method == 'POST':
        port = request.POST.get('port', 'COM3')
        
        try:
            controller = MachineController(port)
            
            if not controller.connect():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to connect to machine on {port}'
                })
            
            # Gather machine stats using various TMCL commands
            stats = {}
            
            try:
                # Get voltage (GIO 8, 1)
                voltage = controller.send_bin_command(1, 15, 1, 8, 0)
                if voltage > 1000:  # If value seems unreasonably large
                    # Try just using the last byte as per our investigation
                    voltage_value = voltage & 0xFF  # Last byte only
                else:
                    voltage_value = voltage
                
                # Convert to proper voltage (1/10V units)
                stats['voltage'] = voltage_value / 10.0
                
                # Get temperature (GIO 9, 1)
                temperature = controller.send_bin_command(1, 15, 1, 9, 0)
                stats['temperature'] = temperature
                
                # For each motor (0, 1, 2), get:
                for motor in range(3):
                    # 1. Velocity (GAP 3)
                    speed = controller.send_bin_command(1, 6, motor, 3, 0)
                    # Convert to positive RPM value for display
                    stats[f'motor{motor}_speed'] = abs(speed)
                    
                    # 2. Position (GAP 1)
                    position = controller.send_bin_command(1, 6, motor, 1, 0)
                    stats[f'motor{motor}_position'] = position
                    
                    # 3. Current (GAP 150)
                    current = controller.send_bin_command(1, 6, motor, 150, 0)
                    stats[f'motor{motor}_current'] = current
                    
                    # 4. Motor state
                    if speed == 0:
                        stats[f'motor{motor}_state'] = 'stopped'
                    elif speed > 0:
                        stats[f'motor{motor}_state'] = 'running-cw'
                    else:
                        stats[f'motor{motor}_state'] = 'running-ccw'
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error collecting machine stats: {str(e)}'
                })
            finally:
                controller.close()
            
            return JsonResponse({
                'status': 'success',
                'data': stats
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error connecting to machine: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }) 