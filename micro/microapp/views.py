from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .relay_control import RelayController
from .machine_test import check_machine_power, MachineController

import serial.tools.list_ports
import websocket
import json

# Template views
def home(request):
    return render(request, 'microapp/home.html')

def register(request):
    return render(request, 'microapp/register/register.html')

def oldregister(request):
    return render(request, 'microapp/register_old.html')

def film(request):
    return render(request, 'microapp/film.html')

def control(request):
    return render(request, 'microapp/control/control.html')

def oldcontrol(request):
    return render(request, 'microapp/control_old.html')

def handoff(request):
    return render(request, 'microapp/handoff.html')

def explore(request):
    return render(request, 'microapp/explore.html')

def report(request):
    return render(request, 'microapp/report.html')

def settings_view(request):
    return render(request, 'microapp/settings.html')

def login(request):
    return render(request, 'microapp/login.html')

def language(request):
    return render(request, 'microapp/language.html')


# Utility functions
def list_com_ports():
    """List available COM ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

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

def send_esp32_ws_command(command, esp32_host='192.168.1.101', port=81, timeout=3):
    ws = websocket.create_connection(f"ws://{esp32_host}:{port}", timeout=timeout)
    ws.send(json.dumps(command))
    result = ws.recv()
    ws.close()
    return json.loads(result)


# Machine check views (TMCL)
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


# Internationalization (I18N)
def toggle_language(request):
    """
    Rotate through settings.LANGUAGES, store selection in
    session + cookie, then redirect back to the same page.
    """
    # Where to go after switching:
    next_url = request.GET.get('next') or request.META.get("HTTP_REFERER", "/")

    current_lang = translation.get_language()
    lang_codes   = [code for code, _ in settings.LANGUAGES]

    try:
        new_lang = lang_codes[(lang_codes.index(current_lang) + 1) % len(lang_codes)]
    except ValueError:          # current language not in list
        new_lang = lang_codes[0]

    translation.activate(new_lang)

    if hasattr(request, "session"):
        request.session['django_language'] = new_lang   # literal key

    response = HttpResponseRedirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, new_lang)
    return response


# WebSocket Relay control views (ESP32)
@csrf_exempt
def control_relay(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        relay_number = request.POST.get('relay')
        try:
            if action in ['on', 'off']:
                if not relay_number:
                    return JsonResponse({'status': 'error', 'message': 'Missing relay number'})
                state = True if action == 'on' else False
                cmd = {"action": "set", "relay": int(relay_number), "state": state}
                resp = send_esp32_ws_command(cmd)
                return JsonResponse({'status': 'success', 'response': resp})
            elif action == 'pulse':
                if not relay_number:
                    return JsonResponse({'status': 'error', 'message': 'Missing relay number'})
                cmd = {"action": "pulse", "relay": int(relay_number)}
                resp = send_esp32_ws_command(cmd)
                return JsonResponse({'status': 'success', 'response': resp})
            elif action == 'ping':
                resp = send_esp32_ws_command({"action": "ping"})
                return JsonResponse({'status': 'success', 'response': resp})
            elif action in ['dark', 'light']:
                # --- NEW LOGIC: handle dark/light as relay sequences ---
                responses = []
                # Always pulse relay 1
                responses.append(send_esp32_ws_command({"action": "pulse", "relay": 1}))
                relay_states = {}
                if action == 'dark':
                    # Relays 2,3,4 ON
                    for r in [2, 3, 4]:
                        resp = send_esp32_ws_command({"action": "set", "relay": r, "state": True})
                        responses.append(resp)
                        relay_states[r] = True
                else:  # light
                    # Relays 2,3,4 OFF
                    for r in [2, 3, 4]:
                        resp = send_esp32_ws_command({"action": "set", "relay": r, "state": False})
                        responses.append(resp)
                        relay_states[r] = False
                # Return the new mode and relay states
                return JsonResponse({'status': 'success', 'mode': action, 'relay_states': relay_states, 'responses': responses})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_relay_status(request):
    if request.method == 'GET':
        try:
            resp = send_esp32_ws_command({"action": "status"})
            return JsonResponse({'status': 'success', 'relay_states': resp.get('states', [])})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_system_stats(request):
    if request.method == 'GET':
        try:
            resp = send_esp32_ws_command({"action": "system"})
            return JsonResponse({'status': 'success', 'system_stats': resp})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_all_states(request):
    if request.method == 'GET':
        try:
            relay_resp = send_esp32_ws_command({"action": "status"})
            system_resp = send_esp32_ws_command({"action": "system"})
            return JsonResponse({
                'status': 'success',
                'data': {
                    'relay_states': relay_resp.get('states', []),
                    'system_stats': system_resp
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def esp32_config(request):
    if request.method == 'POST':
        params = {}
        # Acceptable config keys
        allowed_keys = ['wifi_mode', 'ssid', 'password', 'pulse_duration', 'relay_pins', 'ota_url']
        for key in allowed_keys:
            value = request.POST.get(key)
            if value is not None:
                if key == 'pulse_duration':
                    try:
                        params[key] = int(value)
                    except ValueError:
                        return JsonResponse({'status': 'error', 'message': 'Invalid pulse_duration'})
                elif key == 'relay_pins':
                    # Expect a comma-separated list of ints
                    try:
                        pins = [int(x) for x in value.split(',')]
                        if len(pins) != 8:
                            return JsonResponse({'status': 'error', 'message': 'relay_pins must have 8 values'})
                        params[key] = pins
                    except Exception:
                        return JsonResponse({'status': 'error', 'message': 'Invalid relay_pins'})
                else:
                    params[key] = value
        if not params:
            return JsonResponse({'status': 'error', 'message': 'No valid config parameters provided'})
        try:
            resp = send_esp32_ws_command({"action": "config", "params": params})
            return JsonResponse({'status': 'success', 'response': resp})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})











