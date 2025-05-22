"""
File system operation views for the microapp.
These views handle browsing, creating, and managing files and folders.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import subprocess
import win32api
import win32con

def _folder_is_hidden(p):
    """
    Check if a folder is hidden or system in Windows.
    
    Args:
        p: Path to check
        
    Returns:
        True if the folder is hidden or system, False otherwise
    """
    try:
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    except:
        return False

@csrf_exempt
def create_folder(request):
    """
    API endpoint to create a new folder at the specified path.
    
    Args:
        path: The parent directory path (JSON parameter)
        folderName: The name of the folder to create (JSON parameter)
        
    Returns:
        JSON response with success or error
    """
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
    """
    API endpoint to open a folder browser dialog on the server.
    
    Returns:
        JSON response with the selected folder path
    """
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
    """
    API endpoint to list all available drives in the system.
    
    Returns:
        JSON response with a list of available drives and their names
    """
    if request.method == 'GET':
        try:
            # Get available drives by checking from A to Z
            drives = []
            drive_names = {}
            
            # Use the simple method that works reliably
            for drive_letter in range(65, 91):  # A to Z
                drive = f"{chr(drive_letter)}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
                    # Try to get volume name using ctypes
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
                        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
                        serial_number = ctypes.c_ulong(0)
                        max_component_length = ctypes.c_ulong(0)
                        file_system_flags = ctypes.c_ulong(0)
                        
                        rc = kernel32.GetVolumeInformationW(
                            ctypes.c_wchar_p(drive),
                            volumeNameBuffer,
                            ctypes.sizeof(volumeNameBuffer),
                            ctypes.byref(serial_number),
                            ctypes.byref(max_component_length),
                            ctypes.byref(file_system_flags),
                            fileSystemNameBuffer,
                            ctypes.sizeof(fileSystemNameBuffer)
                        )
                        
                        if rc:
                            drive_names[drive] = volumeNameBuffer.value
                    except Exception:
                        # If we can't get the volume name, just leave it empty
                        drive_names[drive] = ""
            
            # For microfilm-transfer (green), we need to detect it by volume name
            # since its drive letter can change (USB drive)
            for drive, name in list(drive_names.items()):
                # Check if any drive's volume name contains "microfilm-transfer"
                if name and "microfilm-transit" in name.lower():
                    drive_names[drive] = "microfilm-transit"
                # Also check for variations in volume names for other drives
                elif name and "microfilm-archive" in name.lower():
                    drive_names[drive] = "microfilm-archive"
                elif name and "microfilm-engineering" in name.lower():
                    drive_names[drive] = "microfilm-engineering"
            
            return JsonResponse({
                'drives': drives,
                'driveNames': drive_names
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def list_drive_contents(request):
    """
    API endpoint to list the contents of a directory.
    
    Args:
        path: The directory path to list (GET parameter)
        scan_subdirectories: Whether to scan subdirectories (GET parameter, default: false)
        
    Returns:
        JSON response with the directory contents
    """
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
    """
    API endpoint to get file statistics from a folder including file count, total size, and file list.
    
    Args:
        path: The directory path to analyze (GET parameter)
        
    Returns:
        JSON response with file statistics
    """
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

def reveal_in_explorer(request):
    """
    API endpoint to open Windows Explorer and select a file.
    
    Args:
        path: The file path to reveal in Explorer (POST parameter)
        
    Returns:
        JSON response with success or error
    """
    if request.method == 'POST':
        path = request.POST.get('path')
        if path:
            subprocess.Popen(['explorer', '/select,', path])
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({
        'error': 'Invalid request method or missing path'
    }, status=400) 