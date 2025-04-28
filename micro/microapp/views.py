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
import os
import win32api, win32con
import subprocess
import sys
import shutil
import uuid
import threading
import time
from collections import defaultdict

# Dictionary to store transfer jobs and their progress
transfer_jobs = {}

# Template views
def home(request):
    return render(request, 'microapp/home.html')

def transfer(request):
    return render(request, 'microapp/transfer/transfer_main.html')

def register(request):
    return render(request, 'microapp/register/register.html')

def film(request):
    return render(request, 'microapp/film.html')

def control(request):
    return render(request, 'microapp/control/control.html')

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

# Inactive views
def oldcontrol(request):
    return render(request, 'microapp/control_old.html')

def oldregister(request):
    return render(request, 'microapp/register_old.html')

def oldtransfer(request):
    return render(request, 'microapp/transfer_old.html')

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

def _folder_is_hidden(p):
    """Check if a folder is hidden or system in Windows."""
    try:
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    except:
        return False

@csrf_exempt
def create_folder(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            path = data.get('path')
            folder_name = data.get('folderName')
            
            # Validate inputs
            if not path or not folder_name:
                return JsonResponse({
                    'error': 'Path and folder name are required'
                }, status=400)
                
            # Create the full path
            new_folder_path = os.path.join(path, folder_name)
            
            # Check if folder already exists
            if os.path.exists(new_folder_path):
                return JsonResponse({
                    'error': f'Folder "{folder_name}" already exists'
                }, status=400)
                
            # Create the folder
            os.makedirs(new_folder_path, exist_ok=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Folder "{folder_name}" created successfully'
            })
            
        except PermissionError:
            return JsonResponse({
                'error': 'Permission denied when creating folder'
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def browse_local_folders(request):
    if request.method == 'GET':
        try:
            powershell_command = '''
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "Select Folder"
            $dialog.UseDescriptionForTitle = $true
            $dialog.ShowNewFolderButton = $true
            $dialog.SelectedPath = "Y:"
            if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $dialog.SelectedPath
            }
            '''
            result = subprocess.run(['powershell', '-Command', powershell_command], 
                                    capture_output=True, text=True)
            folder_path = result.stdout.strip()
            return JsonResponse({'path': folder_path if folder_path else ''})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def list_drives(request):
    """List all available drives in the system"""
    if request.method == 'GET':
        try:
            # Get available drives by checking from A to Z
            drives = []
            for drive_letter in range(65, 91):  # A to Z
                drive = f"{chr(drive_letter)}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
            
            return JsonResponse({
                'drives': drives
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)



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

def list_drive_contents(request):
    if request.method == 'GET':
        try:
            # Get the requested path or default to Y: drive
            path = request.GET.get('path', 'Y:\\')
            
            # Check if we should scan subdirectories
            scan_subdirectories = request.GET.get('scan_subdirectories', 'false').lower() == 'true'
            
            # Ensure the path exists and is a directory
            if not os.path.exists(path) or not os.path.isdir(path):
                return JsonResponse({
                    'error': f'Path does not exist or is not a directory: {path}'
                }, status=404)
            
            # Always fetch folders for navigation
            folders = [f for f in os.listdir(path) 
                      if os.path.isdir(os.path.join(path, f)) 
                      and not _folder_is_hidden(os.path.join(path, f))
                      and not f.startswith('.')]
                      
            # Sort folders alphabetically
            folders.sort()
            
            # Always fetch files 
            files = [f for f in os.listdir(path) 
                    if os.path.isfile(os.path.join(path, f))
                    and not _folder_is_hidden(os.path.join(path, f))
                    and not f.startswith('.')]
                    
            # Sort files alphabetically
            files.sort()
            
            response_data = {
                'currentPath': path,
                'folders': folders,
                'files': files
            }
            
            # If we should scan subdirectories, add them to the response
            if scan_subdirectories:
                # Prepare a structure to hold data about all subdirectories
                full_structure = {'root': {'folders': folders, 'files': files}}
                
                # Scan only first-level subdirectories to avoid too much data
                # In a real implementation, you might want to limit the depth or number of subdirectories
                for folder in folders:
                    subfolder_path = os.path.join(path, folder)
                    try:
                        # Get subfolders
                        subfolders = [sf for sf in os.listdir(subfolder_path) 
                                     if os.path.isdir(os.path.join(subfolder_path, sf)) 
                                     and not _folder_is_hidden(os.path.join(subfolder_path, sf))
                                     and not sf.startswith('.')]
                        
                        # Get files in subfolder
                        subfiles = [f for f in os.listdir(subfolder_path) 
                                   if os.path.isfile(os.path.join(subfolder_path, f))
                                   and not _folder_is_hidden(os.path.join(subfolder_path, f))
                                   and not f.startswith('.')]
                        
                        # Add to structure
                        full_structure[folder] = {
                            'folders': subfolders,
                            'files': subfiles
                        }
                    except (PermissionError, FileNotFoundError):
                        # Skip folders we can't access
                        continue
                
                # Add the full structure to the response
                response_data['fullStructure'] = full_structure
            
            return JsonResponse(response_data)
            
        except PermissionError:
            return JsonResponse({
                'error': 'Permission denied accessing path'
            }, status=403)
        except FileNotFoundError:
            return JsonResponse({
                'error': 'Path not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def get_file_statistics(request):
    """Get file statistics from a folder including file count, total size, and file list."""
    if request.method == 'GET':
        try:
            # Get the requested path
            path = request.GET.get('path')
            
            # Ensure the path exists and is a directory
            if not os.path.exists(path) or not os.path.isdir(path):
                return JsonResponse({
                    'error': f'Path does not exist or is not a directory: {path}'
                }, status=404)
            
            # Get files in the folder, including subdirectories
            files = []
            file_count = 0
            total_size = 0
            
            # Walk through the directory tree
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.startswith('.') or _folder_is_hidden(os.path.join(root, filename)):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                    
                    # Include all files with their relative paths
                    rel_path = os.path.relpath(root, path)
                    if rel_path == '.':
                        rel_path = ''  # Root directory
                    
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'path': file_path,
                        'relPath': rel_path
                    })
            
            return JsonResponse({
                'fileCount': file_count,
                'totalSize': total_size,
                'files': files
            })
            
        except PermissionError:
            return JsonResponse({
                'error': 'Permission denied accessing path'
            }, status=403)
        except FileNotFoundError:
            return JsonResponse({
                'error': 'Path not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

@csrf_exempt
def transfer_files(request):
    """API endpoint to handle file transfers from source to destination."""
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            source_path = data.get('sourcePath')
            destination_path = data.get('destinationPath')
            files = data.get('files', [])
            
            # Validate inputs
            if not source_path or not destination_path:
                return JsonResponse({
                    'error': 'Source and destination paths are required'
                }, status=400)
                
            if not files or not isinstance(files, list):
                return JsonResponse({
                    'error': 'File list is required and must be an array'
                }, status=400)
                
            # Create a unique ID for this transfer job
            transfer_id = str(uuid.uuid4())
            
            # Initialize transfer job status
            transfer_jobs[transfer_id] = {
                'status': 'pending',
                'errors': [],
                'filesTransferred': 0,
                'totalFiles': len(files),
                'bytesTransferred': 0,
                'currentFile': '',
                'fileProgress': 0,
                'files': files,
                'sourcePath': source_path,
                'destinationPath': destination_path,
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the transfer
            transfer_thread = threading.Thread(
                target=process_file_transfer, 
                args=(transfer_id, source_path, destination_path, files)
            )
            transfer_thread.daemon = True
            transfer_thread.start()
            
            return JsonResponse({
                'id': transfer_id,
                'status': 'started'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def transfer_progress(request):
    """API endpoint to get progress of a file transfer job."""
    if request.method == 'GET':
        try:
            transfer_id = request.GET.get('id')
            
            if not transfer_id or transfer_id not in transfer_jobs:
                return JsonResponse({
                    'error': 'Invalid or unknown transfer ID'
                }, status=404)
                
            # Get the transfer job status
            job_status = transfer_jobs[transfer_id]
            
            # Clean up completed jobs after some time
            if job_status['status'] in ['completed', 'error', 'cancelled']:
                # If the job has been in a final state for more than 5 minutes, clean it up
                if time.time() - job_status['lastUpdateTime'] > 300:
                    # Before deleting, return the status one last time
                    status_copy = job_status.copy()
                    del transfer_jobs[transfer_id]
                    return JsonResponse(status_copy)
            
            return JsonResponse(job_status)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def process_file_transfer(transfer_id, source_path, destination_path, files):
    """Background process to transfer files from source to destination."""
    job = transfer_jobs[transfer_id]
    job['status'] = 'in-progress'
    
    try:
        # Ensure destination directory exists
        if not os.path.exists(destination_path):
            os.makedirs(destination_path, exist_ok=True)
        
        files_transferred = 0
        bytes_transferred = 0
        
        # Process each file
        for file_info in files:
            file_name = file_info.get('name')
            file_size = file_info.get('size', 0)
            file_path = file_info.get('path')
            rel_path = file_info.get('relPath', '')
            
            # Skip files with missing information
            if not file_name or not file_path:
                job['errors'].append(f"Missing file information for {file_name or 'unknown file'}")
                continue
            
            # Update job status to show current file
            job['currentFile'] = file_name
            job['fileProgress'] = 0
            
            # Check if source file exists
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                job['errors'].append(f"Source file not found: {file_path}")
                continue
            
            # Calculate destination path, preserving directory structure
            dest_dir = destination_path
            if rel_path:
                dest_dir = os.path.join(destination_path, rel_path)
                # Create subdirectories if they don't exist
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
            
            dest_file_path = os.path.join(dest_dir, file_name)
            
            try:
                # Perform the file copy
                shutil.copy2(file_path, dest_file_path)
                
                # Update progress
                files_transferred += 1
                bytes_transferred += file_size
                job['filesTransferred'] = files_transferred
                job['bytesTransferred'] = bytes_transferred
                job['fileProgress'] = 1.0  # 100% for this file
                job['lastUpdateTime'] = time.time()
                
            except Exception as e:
                job['errors'].append(f"Error copying {file_path}: {str(e)}")
        
        # Mark job as completed when done
        job['status'] = 'completed' if len(job['errors']) == 0 else 'completed_with_errors'
        job['lastUpdateTime'] = time.time()
        
    except Exception as e:
        # Mark job as error if there's an exception
        job['status'] = 'error'
        job['errors'].append(f"Transfer failed: {str(e)}")
        job['lastUpdateTime'] = time.time()
    
    return True









