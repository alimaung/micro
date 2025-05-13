"""
API endpoints for external systems (SMA Software and External PC).
These endpoints provide status information and control capabilities.
"""

import json
import random
import time
import datetime
import subprocess
import os
import platform
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Mock data for development/testing
SMA_CONNECTED = True
EXTERNAL_PC_CONNECTED = True

@csrf_exempt
@login_required
def sma_status(request):
    """
    API endpoint to get SMA Software status.
    
    Returns:
        JSON response with SMA Software status information
    """
    try:
        # In a real implementation, this would check the actual SMA software status
        # For now, return mock data
        
        # Randomly determine if SMA is connected (for simulation)
        # In production, this would be based on actual connection status
        global SMA_CONNECTED
        if random.random() < 0.05:  # 5% chance to toggle status for simulation
            SMA_CONNECTED = not SMA_CONNECTED
            
        if SMA_CONNECTED:
            # Generate realistic mock data
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            film_number = f"{random.randint(1, 9999):04d}"
            current_film = f"F-{random.randint(1, 20)}-{film_number}"
            
            total_pages = random.randint(100, 1000)
            processed_pages = random.randint(0, total_pages)
            pages_processed = f"{processed_pages}/{total_pages}"
            
            eta_hours = random.randint(0, 23)
            eta_minutes = random.randint(0, 59)
            eta_seconds = random.randint(0, 59)
            eta = f"{eta_hours:02d}:{eta_minutes:02d}:{eta_seconds:02d}"
            
            return JsonResponse({
                'status': 'running',
                'uptime': uptime,
                'current_film': current_film,
                'pages_processed': pages_processed,
                'eta': eta
            })
        else:
            return JsonResponse({
                'status': 'stopped',
                'uptime': '00:00:00',
                'current_film': 'None',
                'pages_processed': '0/0',
                'eta': '00:00:00'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
def sma_reconnect(request):
    """
    API endpoint to reconnect to SMA Software.
    
    Returns:
        JSON response with reconnection result
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
        
    try:
        # In a real implementation, this would attempt to reconnect to the SMA software
        # For now, simulate with a delay and success
        time.sleep(1)  # Simulate processing time
        
        global SMA_CONNECTED
        SMA_CONNECTED = True
        
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully reconnected to SMA Software'
        })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
def external_pc_status(request):
    """
    API endpoint to get External PC status.
    
    Args:
        ip_address: IP address of the external PC (POST parameter)
    
    Returns:
        JSON response with External PC status information
    """
    try:
        # Get IP address from request
        if request.method == 'POST':
            data = json.loads(request.body)
            ip_address = data.get('ip_address', '192.168.1.96')  # Default to configured IP if not provided
        else:
            ip_address = '192.168.1.96'  # Default IP
        
        # Check if PC is reachable with ping
        is_connected = ping_host(ip_address)
        
        # Update global state
        global EXTERNAL_PC_CONNECTED
        EXTERNAL_PC_CONNECTED = is_connected
            
        if EXTERNAL_PC_CONNECTED:
            # Generate realistic mock data
            days = random.randint(0, 9)
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            uptime = f"{days}d {hours}h {minutes}m"
            
            # Random resource usage percentages
            cpu_usage = random.randint(10, 95)
            memory_usage = random.randint(20, 90)
            disk_usage = random.randint(30, 85)
            network_usage = random.randint(5, 70)
            ping_time = random.randint(1, 20)  # 1-20ms
            
            return JsonResponse({
                'status': 'connected',
                'hostname': 'MICRO-PC01',
                'ip_address': ip_address,
                'uptime': uptime,
                'os': 'Windows 10 Pro',
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'network_usage': network_usage,
                'ping_time': ping_time
            })
        else:
            return JsonResponse({
                'status': 'disconnected',
                'hostname': 'MICRO-PC01',
                'ip_address': ip_address,
                'uptime': '0d 0h 0m',
                'os': 'Windows 10 Pro',
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'network_usage': 0,
                'ping_time': 0
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
def external_pc_ping(request):
    """
    API endpoint to ping the external PC.
    
    Args:
        ip_address: IP address of the external PC (POST parameter)
    
    Returns:
        JSON response with ping result
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
        
    try:
        # Get IP address from request
        data = json.loads(request.body)
        ip_address = data.get('ip_address', '192.168.1.96')  # Default to configured IP if not provided
        
        # Ping the host and measure response time
        start_time = time.time()
        is_reachable = ping_host(ip_address)
        end_time = time.time()
        
        # Update global state
        global EXTERNAL_PC_CONNECTED
        
        if is_reachable:
            # Calculate ping time in milliseconds
            ping_time = int((end_time - start_time) * 1000)
            
            EXTERNAL_PC_CONNECTED = True
            
            return JsonResponse({
                'success': True,
                'ping_time': ping_time,
                'message': f'Host {ip_address} is reachable'
            })
        else:
            EXTERNAL_PC_CONNECTED = False
            
            return JsonResponse({
                'success': False,
                'ping_time': 0,
                'message': f'Host {ip_address} is unreachable'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
def external_pc_rdp(request):
    """
    API endpoint to initiate an RDP connection to the external PC.
    
    Args:
        ip_address: IP address of the external PC (POST parameter)
    
    Returns:
        JSON response with RDP connection result
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)
        
    try:
        # Get IP address from request
        data = json.loads(request.body)
        ip_address = data.get('ip_address', '192.168.1.96')  # Default to configured IP if not provided
        
        # Check if PC is reachable before trying to connect
        if not ping_host(ip_address):
            return JsonResponse({
                'success': False,
                'message': f'Host {ip_address} is unreachable'
            })
        
        # Launch RDP client based on OS
        current_os = platform.system()
        
        if current_os == 'Windows':
            # Use mstsc.exe on Windows
            subprocess.Popen(['mstsc.exe', f'/v:{ip_address}'])
            success = True
            message = f'RDP connection to {ip_address} initiated'
        elif current_os == 'Darwin':
            # Use Microsoft Remote Desktop on macOS if available
            try:
                subprocess.Popen(['open', '-a', 'Microsoft Remote Desktop', f'rdp://{ip_address}'])
                success = True
                message = f'RDP connection to {ip_address} initiated'
            except:
                success = False
                message = 'Microsoft Remote Desktop not found on this Mac'
        elif current_os == 'Linux':
            # Use rdesktop or similar on Linux if available
            try:
                subprocess.Popen(['rdesktop', ip_address])
                success = True
                message = f'RDP connection to {ip_address} initiated'
            except:
                try:
                    subprocess.Popen(['xfreerdp', f'/v:{ip_address}'])
                    success = True
                    message = f'RDP connection to {ip_address} initiated'
                except:
                    success = False
                    message = 'No RDP client found on this Linux system'
        else:
            success = False
            message = f'Unsupported operating system: {current_os}'
        
        return JsonResponse({
            'success': success,
            'message': message
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

def ping_host(host):
    """
    Ping a host to check if it's reachable.
    
    Args:
        host: Hostname or IP address to ping
        
    Returns:
        bool: True if host is reachable, False otherwise
    """
    # Determine the correct ping command based on OS
    current_os = platform.system().lower()
    
    if current_os == 'windows':
        ping_cmd = ['ping', '-n', '1', '-w', '1000', host]
    else:  # Unix-like systems (Linux, macOS)
        ping_cmd = ['ping', '-c', '1', '-W', '1', host]
    
    try:
        # Run the ping command and capture output
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        
        # Check if ping was successful (return code 0)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False 