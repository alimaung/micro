"""
File transfer views for the microapp.
These views handle file transfer operations between locations.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import time
import uuid
import shutil
import threading

# Dictionary to store transfer jobs and their progress
transfer_jobs = {}

@csrf_exempt
def transfer_files(request):
    """
    API endpoint to handle file transfers from source to destination.
    
    Args:
        sourcePath: The source directory path (JSON parameter)
        destinationPath: The destination directory path (JSON parameter)
        files: List of files to transfer (JSON parameter)
        
    Returns:
        JSON response with transfer job ID and status
    """
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
    """
    API endpoint to get progress of a file transfer job.
    
    Args:
        id: The transfer job ID (GET parameter)
        
    Returns:
        JSON response with the transfer job status
    """
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
    """
    Background process to transfer files from source to destination.
    
    Args:
        transfer_id: The unique ID for this transfer job
        source_path: The source directory path
        destination_path: The destination directory path
        files: List of files to transfer
        
    Returns:
        True when complete
    """
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