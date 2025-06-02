"""
ESP32 relay control views for the microapp.
These views handle communication with the ESP32 relay controller via WebSockets.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import websocket

def send_esp32_ws_command(command, esp32_host='192.168.1.101', port=81, timeout=3):
    """
    Send a command to the ESP32 via WebSocket and return the response.
    
    Args:
        command: The command to send (dict)
        esp32_host: Host address of the ESP32 (default: 192.168.1.101)
        port: WebSocket port (default: 81)
        timeout: Connection timeout in seconds (default: 3)
        
    Returns:
        The JSON response from the ESP32
    """
    ws = websocket.create_connection(f"ws://{esp32_host}:{port}", timeout=timeout)
    ws.send(json.dumps(command))
    result = ws.recv()
    ws.close()
    return json.loads(result)

@csrf_exempt
def control_relay(request):
    """
    API endpoint to control relays connected to the ESP32.
    
    Handles turning relays on/off, pulsing relays, and setting the dark/light mode.
    """
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
                    # Relays 2,3,4 ON, relay 5 OFF (room light off in dark mode)
                    for r in [2, 3, 4]:
                        resp = send_esp32_ws_command({"action": "set", "relay": r, "state": True})
                        responses.append(resp)
                        relay_states[r] = True
                    # Turn OFF room light in dark mode
                    resp = send_esp32_ws_command({"action": "set", "relay": 5, "state": False})
                    responses.append(resp)
                    relay_states[5] = False
                else:  # light
                    # Relays 2,3,4 OFF, relay 5 ON (room light on in light mode)
                    for r in [2, 3, 4]:
                        resp = send_esp32_ws_command({"action": "set", "relay": r, "state": False})
                        responses.append(resp)
                        relay_states[r] = False
                    # Turn ON room light in light mode
                    resp = send_esp32_ws_command({"action": "set", "relay": 5, "state": True})
                    responses.append(resp)
                    relay_states[5] = True
                # Return the new mode and relay states
                return JsonResponse({'status': 'success', 'mode': action, 'relay_states': relay_states, 'responses': responses})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_relay_status(request):
    """API endpoint to get the status of all relays connected to the ESP32."""
    if request.method == 'GET':
        try:
            resp = send_esp32_ws_command({"action": "status"})
            return JsonResponse({'status': 'success', 'relay_states': resp.get('states', [])})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_system_stats(request):
    """API endpoint to get system statistics from the ESP32."""
    if request.method == 'GET':
        try:
            resp = send_esp32_ws_command({"action": "system"})
            return JsonResponse({'status': 'success', 'system_stats': resp})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_all_states(request):
    """API endpoint to get the status of all relays and system stats in one request."""
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
    """API endpoint to configure the ESP32 settings."""
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