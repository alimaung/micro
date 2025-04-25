from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .relay_control import RelayController
from .machine_test import check_machine_power, MachineController
import serial.tools.list_ports
import json
import time

# Create your views here.
def home(request):
    return render(request, 'microapp/home.html')

def register(request):
    return render(request, 'microapp/register/register.html')

def oldregister(request):
    return render(request, 'microapp/register_old.html')

def film(request):
    return render(request, 'microapp/film.html')

def list_com_ports():
    """List available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def control(request):
    relays = range(1, 9)  # Create a range of relay numbers
    com_ports = list_com_ports()  # Get available COM ports
    return render(request, 'microapp/control.html', {'relays': relays, 'com_ports': com_ports})

def handoff(request):
    return render(request, 'microapp/handoff.html')

def explore(request):
    return render(request, 'microapp/explore.html')

def report(request):
    return render(request, 'microapp/report.html')

def settings(request):
    return render(request, 'microapp/settings.html')

def login(request):
    return render(request, 'microapp/login.html')

def language(request):
    return render(request, 'microapp/language.html')

@csrf_exempt
def control_relay(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        com_port = request.POST.get('com_port', 'COM18')  # Default to COM18

        print(f"Received request to perform action: {action} on {com_port}")

        # Special case for ping action (latency measurement)
        if action == 'ping':
            # This is just a latency test, no need to actually do anything
            # The round-trip time is calculated on the client side
            return JsonResponse({'status': 'success', 'message': 'pong'})

        try:
            controller = RelayController(com_port)
            result = None
            
            if action == 'light':
                result = controller.set_light_mode()
                response = {
                    'status': 'success',
                    'message': 'Light mode activated',
                    'mode': 'light',
                    'relay_states': controller.relay_states
                }
            elif action == 'dark':
                result = controller.set_dark_mode()
                response = {
                    'status': 'success', 
                    'message': 'Dark mode activated',
                    'mode': 'dark',
                    'relay_states': controller.relay_states
                }
            elif action == 'machine_on':
                result = controller.machine_on()
                response = {
                    'status': 'success',
                    'message': 'Machine turned on',
                    'machine_state': True,
                    'relay_states': controller.relay_states
                }
            elif action == 'machine_off':
                result = controller.machine_off()
                response = {
                    'status': 'success',
                    'message': 'Machine turned off',
                    'machine_state': False,
                    'relay_states': controller.relay_states
                }
            elif action in ['on', 'off']:
                relay_number = request.POST.get('relay')
                if action == 'on':
                    result = controller.relay_on(relay_number)
                    state = True
                else:
                    result = controller.relay_off(relay_number)
                    state = False
                    
                response = {
                    'status': 'success',
                    'message': f"Relay {relay_number} turned {action.upper()}",
                    'relay': relay_number,
                    'state': state,
                    'relay_states': controller.relay_states
                }
            else:
                controller.close()
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})

            controller.close()
            return JsonResponse(response)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_relay_status(request):
    """Get the current status of all relays"""
    if request.method == 'POST':
        com_port = request.POST.get('com_port', 'COM7')  # Default to COM18
        
        try:
            controller = RelayController(com_port)
            
            # Get all relay states
            controller.get_relay_status()  # This updates internal state
            
            # Get current mode
            current_mode = controller.get_current_mode()
            
            response = {
                'status': 'success',
                'relay_states': controller.relay_states,
                'current_mode': current_mode
            }
            
            controller.close()
            return JsonResponse(response)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error getting relay status: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })
    
@csrf_exempt
def get_system_stats(request):
    """Get the ESP32 system statistics"""
    if request.method == 'POST':
        com_port = request.POST.get('com_port', 'COM18')  # Default to COM18
        
        try:
            controller = RelayController(com_port)
            
            # Get all system stats
            stats = controller.get_system_stats()
            
            response = {
                'status': 'success',
                'system_stats': stats
            }
            
            controller.close()
            return JsonResponse(response)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error getting system stats: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })
    
@csrf_exempt
def get_all_states(request):
    """Get all relay states and system stats in one call"""
    if request.method == 'POST':
        com_port = request.POST.get('com_port', 'COM7')  # Default to COM18
        
        try:
            controller = RelayController(com_port)
            
            # Update all states
            all_states = controller.update_all_states()
            
            response = {
                'status': 'success',
                'data': all_states
            }
            
            controller.close()
            return JsonResponse(response)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error getting all states: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

# Function to check if a COM port is available
@csrf_exempt
def check_port(request):
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
    """Check if the machine is actually powered on"""
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
    """Get detailed machine statistics using TMCL commands"""
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
