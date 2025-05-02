"""
Index Generation views for the microapp.
These views handle film index generation, processing, and management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json
import os
import time
import uuid
import threading
import xlwings as xw
from pathlib import Path
from datetime import datetime
from ..models import Project

# Dictionary to store index tasks and their progress
index_tasks = {}

@csrf_exempt
def initialize_index(request):
    """
    API endpoint to start index initialization for a project.
    
    Args:
        projectId: Project ID (JSON parameter)
        
    Returns:
        JSON response with task ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            
            # Validate inputs
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
            
            # Create a unique ID for this index task
            task_id = str(uuid.uuid4())
            
            # Initialize index task status
            index_tasks[task_id] = {
                'status': 'pending',
                'projectId': project_id,
                'progress': 0,
                'results': None,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the index initialization
            index_thread = threading.Thread(
                target=process_index_initialization, 
                args=(task_id, project_id)
            )
            index_thread.daemon = True
            index_thread.start()
            
            return JsonResponse({
                'taskId': task_id,
                'status': 'started',
                'message': 'Index initialization started successfully'
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

@csrf_exempt
def update_index(request):
    """
    API endpoint to update an index with film numbers.
    
    Args:
        projectId: Project ID (JSON parameter)
        filmNumbers: Dictionary mapping roll IDs to film numbers (JSON parameter)
        indexData: Initial index data (JSON parameter)
        
    Returns:
        JSON response with task ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            film_numbers = data.get('filmNumbers')
            index_data = data.get('indexData')
            
            # Validate inputs
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            if not film_numbers:
                return JsonResponse({
                    'error': 'Film numbers are required'
                }, status=400)
                
            if not index_data:
                return JsonResponse({
                    'error': 'Index data is required'
                }, status=400)
            
            # Create a unique ID for this index update task
            task_id = str(uuid.uuid4())
            
            # Initialize index update task status
            index_tasks[task_id] = {
                'status': 'pending',
                'projectId': project_id,
                'progress': 0,
                'results': None,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the index update
            index_thread = threading.Thread(
                target=process_index_update, 
                args=(task_id, project_id, index_data, film_numbers)
            )
            index_thread.daemon = True
            index_thread.start()
            
            return JsonResponse({
                'taskId': task_id,
                'status': 'started',
                'message': 'Index update started successfully'
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

def get_index_status(request):
    """
    API endpoint to get the status of an index task.
    
    Args:
        taskId: Task ID (GET parameter)
        
    Returns:
        JSON response with the task status
    """
    if request.method == 'GET':
        try:
            task_id = request.GET.get('taskId')
            
            if not task_id or task_id not in index_tasks:
                return JsonResponse({
                    'error': 'Invalid or unknown task ID'
                }, status=404)
                
            # Get the index task status
            task_status = index_tasks[task_id]
            
            # Clean up completed tasks after some time
            if task_status['status'] in ['completed', 'error', 'cancelled']:
                # If the task has been in a final state for more than 30 minutes, clean it up
                if time.time() - task_status['lastUpdateTime'] > 1800:
                    # Before deleting, return the status one last time
                    status_copy = task_status.copy()
                    del index_tasks[task_id]
                    return JsonResponse(status_copy)
            
            return JsonResponse(task_status)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def get_index_results(request):
    """
    API endpoint to get the full results of a completed index task.
    
    Args:
        projectId: Project ID (GET parameter)
        
    Returns:
        JSON response with index results
    """
    if request.method == 'GET':
        try:
            project_id = request.GET.get('projectId')
            
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            # Find the most recent completed index task for this project
            matching_tasks = [task for task_id, task in index_tasks.items() 
                             if task['projectId'] == project_id and task['status'] == 'completed']
            
            if not matching_tasks:
                return JsonResponse({
                    'error': 'No completed index task found for this project'
                }, status=404)
                
            # Sort by lastUpdateTime to get the most recent
            most_recent = sorted(matching_tasks, key=lambda x: x['lastUpdateTime'], reverse=True)[0]
            
            # Return the full results
            return JsonResponse({
                'status': 'success',
                'results': most_recent['results']
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def process_index_initialization(task_id, project_id):
    """
    Process index initialization in a background thread.
    
    Args:
        task_id: ID of the task
        project_id: ID of the project
    """
    task = index_tasks[task_id]
    
    try:
        # Update task status
        task['status'] = 'in-progress'
        task['progress'] = 10
        task['lastUpdateTime'] = time.time()
        
        # Get the project from the database
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            task['status'] = 'error'
            task['errors'].append(f'Project with ID {project_id} not found')
            task['lastUpdateTime'] = time.time()
            return
        
        # Get allocation results from previous tasks
        matching_allocation_tasks = []
        from .allocation_views import allocation_tasks
        for allocation_task_id, allocation_task in allocation_tasks.items():
            if allocation_task['projectId'] == project_id and allocation_task['status'] == 'completed':
                matching_allocation_tasks.append(allocation_task)
        
        if not matching_allocation_tasks:
            task['status'] = 'error'
            task['errors'].append('No completed allocation found for this project')
            task['lastUpdateTime'] = time.time()
            return
            
        # Get the most recent allocation
        most_recent_allocation = sorted(matching_allocation_tasks, key=lambda x: x['lastUpdateTime'], reverse=True)[0]
        allocation_results = most_recent_allocation.get('results', {})
        
        # Update task progress
        task['progress'] = 20
        task['lastUpdateTime'] = time.time()
        
        # Convert to Python data structure used by IndexService
        # Build a pseudo project object with film allocation that matches the original
        class PseudoProject:
            def __init__(self, project_db, allocation_data):
                self.archive_id = project_db.archive_id
                self.project_folder_name = project_db.project_folder_name
                self.comlist_path = project_db.comlist_path
                self.documents = []
                
                # Create film allocation
                self.film_allocation = PseudoFilmAllocation(allocation_data)
                
                # Extract documents
                if 'results' in allocation_data and 'documents' in allocation_data['results']:
                    for doc in allocation_data['results']['documents']:
                        self.documents.append(PseudoDocument(doc))
        
        class PseudoFilmAllocation:
            def __init__(self, allocation_data):
                # Extract data from the allocation results
                results = allocation_data.get('results', {})
                
                self.rolls_16mm = []
                rolls_16mm_data = results.get('rolls_16mm', [])
                for roll_data in rolls_16mm_data:
                    self.rolls_16mm.append(PseudoFilmRoll(roll_data))
        
        class PseudoFilmRoll:
            def __init__(self, roll_data):
                self.roll_id = roll_data.get('roll_id')
                self.document_segments = []
                
                for segment in roll_data.get('document_segments', []):
                    self.document_segments.append(PseudoDocumentSegment(segment))
        
        class PseudoDocumentSegment:
            def __init__(self, segment_data):
                self.doc_id = segment_data.get('doc_id')
                self.document_index = segment_data.get('document_index', 1)
                self.frame_range = segment_data.get('frame_range', [0, 0])
        
        class PseudoDocument:
            def __init__(self, doc_data):
                self.doc_id = doc_data.get('docId', '')
                self.com_id = None
        
        # Create the pseudo project
        pseudo_project = PseudoProject(project, most_recent_allocation)
        
        # Update task progress
        task['progress'] = 40
        task['lastUpdateTime'] = time.time()
        
        # Process COM list Excel file to extract document ID to COM ID mappings
        com_id_mappings = {}
        
        # Update task progress
        task['progress'] = 50
        task['lastUpdateTime'] = time.time()
        
        try:
            # Implement Excel file reading using xlwings
            if project.comlist_path and os.path.exists(project.comlist_path):
                wb = None
                try:
                    # Try to use already open workbook
                    wb = xw.books.active
                    if Path(wb.fullname).resolve() != Path(project.comlist_path).resolve():
                        wb = xw.Book(str(project.comlist_path))
                except Exception:
                    # Open the workbook directly
                    wb = xw.Book(str(project.comlist_path))
                
                # Get the first worksheet
                ws = wb.sheets[0]
                
                # Get data range with potential barcode and ComID values
                used_range = ws.used_range
                if used_range:
                    data = used_range.value
                    
                    # Skip header row if exists
                    start_row = 1 if isinstance(data[0][0], str) and not data[0][0].isdigit() else 0
                    
                    # Extract barcode and ComID pairs
                    for i in range(start_row, len(data)):
                        if i < len(data) and len(data[i]) >= 2:
                            barcode = str(data[i][0]) if data[i][0] is not None else None
                            com_id = data[i][1]
                            
                            # Convert ComID to integer if possible
                            if com_id is not None:
                                try:
                                    # Handle case where Excel returns a float
                                    if isinstance(com_id, float) and com_id.is_integer():
                                        com_id = int(com_id)
                                    else:
                                        com_id = int(com_id)
                                    
                                    if barcode and com_id:
                                        com_id_mappings[barcode] = com_id
                                except (ValueError, TypeError):
                                    pass
                
                # Close Excel if we opened it
                if wb:
                    wb.app.quit()
        except Exception as e:
            task['errors'].append(f'Error reading COM list Excel file: {str(e)}')
            # Continue anyway, using placeholder COM IDs
        
        # Update task progress
        task['progress'] = 70
        task['lastUpdateTime'] = time.time()
        
        # Process 16mm film rolls
        index_data = {
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "version": "1.0",
                "archive_id": project.archive_id,
                "project_name": project.project_folder_name
            },
            "index": []
        }
        
        # Iterate through 16mm film rolls
        for roll in pseudo_project.film_allocation.rolls_16mm:
            roll_id = roll.roll_id
            
            # Iterate through document segments in this roll
            for segment in roll.document_segments:
                doc_id = segment.doc_id
                
                # Get document index (position on this roll)
                doc_index = segment.document_index
                
                # Get frame range for this segment
                frame_range = segment.frame_range
                
                # Get COM ID from the mapping or use a placeholder
                com_id = com_id_mappings.get(doc_id, None)
                
                # If COM ID is not found, generate a placeholder
                if com_id is None:
                    # Use a placeholder COM ID (negative roll_id to avoid conflicts)
                    com_id = -roll_id
                
                # Update document COM ID if available
                for doc in pseudo_project.documents:
                    if doc.doc_id == doc_id and com_id is not None:
                        doc.com_id = com_id
                
                # Create initial index array with [roll_id, frameRange_start, frameRange_end]
                initial_index = [roll_id, frame_range[0], frame_range[1]]
                
                # Create index entry with document index
                index_entry = [
                    doc_id,                # Document ID
                    com_id,                # COM ID
                    initial_index,         # Initial index [roll_id, frameRange_start, frameRange_end]
                    None,                  # Final index (to be filled later)
                    doc_index              # Document index (position on roll)
                ]
                
                # Add to index
                index_data["index"].append(index_entry)
        
        # Update task progress
        task['progress'] = 90
        task['lastUpdateTime'] = time.time()
        
        # Update task status
        task['status'] = 'completed'
        task['progress'] = 100
        task['results'] = index_data
        task['lastUpdateTime'] = time.time()
        
    except Exception as e:
        # Log the error and update task status
        task['status'] = 'error'
        task['errors'].append(str(e))
        task['lastUpdateTime'] = time.time()

def process_index_update(task_id, project_id, index_data, film_numbers):
    """
    Process index update in a background thread.
    
    Args:
        task_id: ID of the task
        project_id: ID of the project
        index_data: Initial index data
        film_numbers: Dictionary mapping roll IDs to film numbers
    """
    task = index_tasks[task_id]
    
    try:
        # Update task status
        task['status'] = 'in-progress'
        task['progress'] = 10
        task['lastUpdateTime'] = time.time()
        
        # Get the project from the database
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            task['status'] = 'error'
            task['errors'].append(f'Project with ID {project_id} not found')
            task['lastUpdateTime'] = time.time()
            return
        
        # Update task progress
        task['progress'] = 30
        task['lastUpdateTime'] = time.time()
        
        # Validate film numbers
        if not isinstance(film_numbers, dict):
            task['status'] = 'error'
            task['errors'].append('Film numbers must be a dictionary')
            task['lastUpdateTime'] = time.time()
            return
        
        # Validate index data
        if not isinstance(index_data, dict) or 'index' not in index_data:
            task['status'] = 'error'
            task['errors'].append('Invalid index data format')
            task['lastUpdateTime'] = time.time()
            return
        
        # Update task progress
        task['progress'] = 50
        task['lastUpdateTime'] = time.time()
        
        # Process index update
        updated_count = 0
        missing_count = 0
        
        # Process each index entry
        for entry_idx, entry in enumerate(index_data["index"]):
            if len(entry) >= 4 and entry[2]:
                # Get roll_id and frame range from initial_index
                roll_id, frame_start, frame_end = entry[2]
                roll_id_str = str(roll_id)
                
                # Get document index (use 5th element if available, default to 1)
                doc_index = entry[4] if len(entry) >= 5 else 1
                
                # Find corresponding film_number in film_numbers
                if roll_id_str in film_numbers:
                    film_number = film_numbers[roll_id_str]
                    
                    # Update the final_index
                    if film_number:
                        # Use format: film_number-document_index(4 digits)-frame_start(5 digits)
                        entry[3] = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
                        updated_count += 1
                    else:
                        missing_count += 1
                else:
                    missing_count += 1
        
        # Update task progress
        task['progress'] = 80
        task['lastUpdateTime'] = time.time()
        
        # Update metadata
        index_data["metadata"]["update_date"] = datetime.now().isoformat()
        index_data["metadata"]["updated_count"] = updated_count
        index_data["metadata"]["missing_count"] = missing_count
        
        # Update task status
        task['status'] = 'completed'
        task['progress'] = 100
        task['results'] = index_data
        task['lastUpdateTime'] = time.time()
        
    except Exception as e:
        # Log the error and update task status
        task['status'] = 'error'
        task['errors'].append(str(e))
        task['lastUpdateTime'] = time.time()
