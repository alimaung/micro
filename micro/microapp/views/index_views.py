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
import openpyxl
import xlrd
from pathlib import Path
from datetime import datetime
from ..models import Project, Document

# Dictionary to store index tasks and their progress
index_tasks = {}

@csrf_exempt
def initialize_index(request):
    """
    API endpoint to start index initialization for a project.
    
    Args:
        projectId: Project ID (JSON parameter)
        allocationResults: Allocation results from frontend (JSON parameter)
        
    Returns:
        JSON response with task ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            allocation_results = data.get('allocationResults', {})
            
            print(f"DEBUG: Received initialize-index request for project {project_id}")
            print(f"DEBUG: Allocation results keys: {list(allocation_results.keys()) if allocation_results else 'None'}")
            
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
                args=(task_id, project_id, allocation_results)
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
            print(f"DEBUG: Error in initialize_index: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
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

def process_index_initialization(task_id, project_id, allocation_results=None):
    """
    Process index initialization in a background thread.
    
    Args:
        task_id: ID of the task
        project_id: ID of the project
        allocation_results: Allocation results from frontend
    """
    task = index_tasks[task_id]
    
    try:
        # Update task status
        task['status'] = 'in-progress'
        task['progress'] = 10
        task['lastUpdateTime'] = time.time()
        print(f"DEBUG: Index initialization started for task {task_id}, project {project_id}")
        
        # Get the project from the database
        try:
            project = Project.objects.get(id=project_id)
            print(f"DEBUG: Found project {project_id}: {project.archive_id}, comlist_path: {project.comlist_path}")
        except Project.DoesNotExist:
            task['status'] = 'error'
            task['errors'].append(f'Project with ID {project_id} not found')
            task['lastUpdateTime'] = time.time()
            print(f"DEBUG: Project {project_id} not found")
            return
        
        # Check if we have allocation results from the frontend
        if allocation_results:
            print(f"DEBUG: Using allocation results from frontend")
            most_recent_allocation = {'results': allocation_results, 'lastUpdateTime': time.time()}
        else:
            # Get allocation results from previous tasks
            print(f"DEBUG: No allocation results from frontend, checking backend tasks")
            matching_allocation_tasks = []
            from .allocation_views import allocation_tasks
            print(f"DEBUG: Looking for allocation tasks for project {project_id}")
            for allocation_task_id, allocation_task in allocation_tasks.items():
                if allocation_task['projectId'] == project_id and allocation_task['status'] == 'completed':
                    matching_allocation_tasks.append(allocation_task)
                    print(f"DEBUG: Found matching allocation task {allocation_task_id}")
            
            if not matching_allocation_tasks:
                print(f"DEBUG: No completed allocation found for project {project_id}")
                if allocation_results:
                    print(f"DEBUG: Using directly provided allocation results")
                    most_recent_allocation = {'results': allocation_results, 'lastUpdateTime': time.time()}
                else:
                    task['status'] = 'error'
                    task['errors'].append('No allocation results found. Please complete allocation first.')
                    task['lastUpdateTime'] = time.time()
                    return
            else:
                # Get the most recent allocation
                most_recent_allocation = sorted(matching_allocation_tasks, key=lambda x: x['lastUpdateTime'], reverse=True)[0]
                print(f"DEBUG: Using most recent allocation completed at {most_recent_allocation['lastUpdateTime']}")
        
        # Extract allocation results
        allocation_results = most_recent_allocation.get('results', {})
        print(f"DEBUG: Allocation results structure: {type(allocation_results)}")
        if isinstance(allocation_results, dict):
            print(f"DEBUG: Allocation results keys: {list(allocation_results.keys())}")
        
        # Update task progress
        task['progress'] = 20
        task['lastUpdateTime'] = time.time()
        
        # Convert to Python data structure used by IndexService
        print(f"DEBUG: Creating pseudo project objects")
        # Build a pseudo project object with film allocation that matches the original
        class PseudoProject:
            def __init__(self, project_db, allocation_data):
                self.archive_id = project_db.archive_id
                self.project_folder_name = project_db.project_folder_name
                self.comlist_path = project_db.comlist_path
                self.documents = []
                
                # Create film allocation
                print(f"DEBUG: Creating film allocation from allocation data")
                self.film_allocation = PseudoFilmAllocation(allocation_data)
                
                # Extract documents
                if 'results' in allocation_data and 'documents' in allocation_data['results']:
                    print(f"DEBUG: Found documents in allocation results")
                    for doc in allocation_data['results']['documents']:
                        self.documents.append(PseudoDocument(doc))
                else:
                    print(f"DEBUG: No documents found in allocation results")
                    print(f"DEBUG: allocation_data keys: {list(allocation_data.keys())}")
                    if 'results' in allocation_data:
                        print(f"DEBUG: allocation_data['results'] keys: {list(allocation_data['results'].keys())}")
        
        class PseudoFilmAllocation:
            def __init__(self, allocation_data):
                # Extract data from the allocation results
                results = allocation_data.get('results', {})
                
                self.rolls_16mm = []
                rolls_16mm_data = results.get('rolls_16mm', [])
                print(f"DEBUG: Found {len(rolls_16mm_data)} 16mm rolls in allocation results")
                for roll_data in rolls_16mm_data:
                    self.rolls_16mm.append(PseudoFilmRoll(roll_data))
        
        class PseudoFilmRoll:
            def __init__(self, roll_data):
                self.roll_id = roll_data.get('roll_id')
                self.document_segments = []
                
                segments = roll_data.get('document_segments', [])
                print(f"DEBUG: Roll {self.roll_id} has {len(segments)} document segments")
                for segment in segments:
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
        try:
            pseudo_project = PseudoProject(project, allocation_results)
            print(f"DEBUG: Created pseudo project with archive_id {pseudo_project.archive_id}")
        except Exception as e:
            print(f"DEBUG: Error creating pseudo project: {str(e)}")
            task['status'] = 'error'
            task['errors'].append(f'Error creating project structure: {str(e)}')
            task['lastUpdateTime'] = time.time()
            return
        
        # Update task progress
        task['progress'] = 40
        task['lastUpdateTime'] = time.time()
        
        # Process COM list Excel file to extract document ID to COM ID mappings
        com_id_mappings = {}
        
        # Update task progress
        task['progress'] = 50
        task['lastUpdateTime'] = time.time()
        
        try:
            # Implement Excel file reading using openpyxl/xlrd
            if project.comlist_path and os.path.exists(project.comlist_path):
                print(f"DEBUG: Reading COM list Excel file: {project.comlist_path}")
                
                # Determine file format
                file_extension = Path(project.comlist_path).suffix.lower()
                print(f"DEBUG: File format detected: {file_extension}")
                
                data = None
                
                if file_extension == '.xlsx':
                    # Use openpyxl for .xlsx files
                    try:
                        wb = openpyxl.load_workbook(project.comlist_path, read_only=True)
                        print(f"DEBUG: Opened .xlsx workbook with sheets: {wb.sheetnames}")
                        ws = wb.active
                        
                        # Get data from worksheet
                        data = list(ws.values)
                        wb.close()
                        
                    except Exception as e:
                        print(f"DEBUG: Error reading .xlsx file: {str(e)}")
                        raise
                        
                elif file_extension == '.xls':
                    # Use xlrd for .xls files
                    try:
                        wb = xlrd.open_workbook(project.comlist_path)
                        print(f"DEBUG: Opened .xls workbook with {wb.nsheets} sheets")
                        ws = wb.sheet_by_index(0)
                        
                        # Convert xlrd data to list format
                        data = []
                        for row_idx in range(ws.nrows):
                            row_data = []
                            for col_idx in range(ws.ncols):
                                cell_value = ws.cell_value(row_idx, col_idx)
                                # Convert xlrd cell types to Python types
                                if ws.cell_type(row_idx, col_idx) == xlrd.XL_CELL_EMPTY:
                                    cell_value = None
                                elif ws.cell_type(row_idx, col_idx) == xlrd.XL_CELL_NUMBER:
                                    # Check if it's actually an integer
                                    if cell_value == int(cell_value):
                                        cell_value = int(cell_value)
                                row_data.append(cell_value)
                            data.append(row_data)
                            
                    except Exception as e:
                        print(f"DEBUG: Error reading .xls file: {str(e)}")
                        raise
                        
                else:
                    raise Exception(f"Unsupported file format: {file_extension}")
                
                if data:
                    # Skip header row if exists
                    start_row = 1 if isinstance(data[0][0], str) and not data[0][0].isdigit() else 0
                    print(f"DEBUG: Processing data with {len(data)} rows, starting at row {start_row}")
                    
                    # Extract barcode and ComID pairs
                    for i in range(start_row, len(data)):
                        if i < len(data) and len(data[i]) >= 2:
                            barcode_raw = data[i][0]
                            com_id = data[i][1]
                            
                            # Keep the original barcode format AND create a normalized version
                            barcode_original = str(barcode_raw) if barcode_raw is not None else None
                            
                            # Also normalize to simple number format (for backward compatibility)
                            try:
                                if isinstance(barcode_raw, float) and barcode_raw.is_integer():
                                    # Convert float to integer (remove decimal)
                                    barcode_normalized = str(int(barcode_raw))
                                elif isinstance(barcode_raw, int):
                                    barcode_normalized = str(barcode_raw)
                                else:
                                    # Try to convert string to integer
                                    barcode_normalized = str(int(float(str(barcode_raw))))
                            except (ValueError, TypeError, AttributeError):
                                barcode_normalized = barcode_original
                            
                            print(f"DEBUG: Extracted barcode: {barcode_raw} -> original: {barcode_original}, normalized: {barcode_normalized}, com_id: {com_id}")
                            
                            # Convert ComID to integer if possible
                            if com_id is not None:
                                try:
                                    # Handle case where Excel returns a float
                                    if isinstance(com_id, float) and com_id.is_integer():
                                        com_id = int(com_id)
                                    else:
                                        com_id = int(com_id)
                                    
                                    # Store both formats in the mappings dictionary
                                    if barcode_original and com_id:
                                        com_id_mappings[barcode_original] = com_id
                                    if barcode_normalized and com_id:
                                        com_id_mappings[barcode_normalized] = com_id
                                except (ValueError, TypeError):
                                    pass
                
                print(f"DEBUG: Extracted {len(com_id_mappings)} COM ID mappings")
        except Exception as e:
            print(f"DEBUG: Error reading COM list Excel file: {str(e)}")
            task['errors'].append(f'Error reading COM list Excel file: {str(e)}')
            # Continue anyway, using placeholder COM IDs
        
        # Update task progress
        task['progress'] = 70
        task['lastUpdateTime'] = time.time()
        
        # Process 16mm film rolls
        print(f"DEBUG: Processing film rolls to build index")
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
            print(f"DEBUG: Processing roll {roll_id} with {len(roll.document_segments)} segments")
            
            # Iterate through document segments in this roll
            for segment in roll.document_segments:
                doc_id = segment.doc_id
                
                # Get document index (position on this roll)
                doc_index = segment.document_index
                
                # Get frame range for this segment
                frame_range = segment.frame_range
                
                # Create index entry with document index
                # Remove PDF extension (case-insensitive) to get the barcode for COM ID lookup
                doc_id_lower = doc_id.lower()
                if doc_id_lower.endswith('.pdf'):
                    doc_id_base = doc_id[:-4]  # Remove last 4 characters (.pdf or .PDF)
                else:
                    doc_id_base = doc_id
                
                # Get COM ID from the mapping or use a placeholder
                com_id = com_id_mappings.get(doc_id_base, None)

                # If not found, try alternative lookup methods
                if com_id is None:
                    # Try without leading zeros
                    try:
                        normalized_id = str(int(doc_id_base))
                        com_id = com_id_mappings.get(normalized_id, None)
                    except (ValueError, TypeError):
                        pass

                # If COM ID is still not found, generate a placeholder
                if com_id is None:
                    # Use a placeholder COM ID (negative roll_id to avoid conflicts)
                    com_id = -roll_id
                    print(f"DEBUG: No COM ID found for doc_id: {doc_id}, tried '{doc_id_base}', using placeholder: {com_id}")
                else:
                    print(f"DEBUG: Found COM ID: {com_id} for doc_id: {doc_id}")
                
                # Update document COM ID if available
                for doc in pseudo_project.documents:
                    if doc.doc_id == doc_id and com_id is not None:
                        doc.com_id = com_id
                
                # Also update the actual Document model in the database
                try:
                    db_document = Document.objects.filter(project=project, doc_id=doc_id_base).first()
                    if db_document and com_id is not None:
                        db_document.com_id = com_id
                        db_document.save()
                        print(f"DEBUG: Updated COM ID {com_id} for document {doc_id_base} in database")
                except Exception as e:
                    print(f"DEBUG: Error updating COM ID for document {doc_id_base}: {str(e)}")
                    # Don't fail the whole process for this error
                    pass
                
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
        print(f"DEBUG: Index built with {len(index_data['index'])} entries")
        print(f"DEBUG: Index data: {index_data}")
        task['progress'] = 90
        task['lastUpdateTime'] = time.time()
        
        # Update task status
        task['status'] = 'completed'
        task['progress'] = 100
        task['results'] = index_data
        task['lastUpdateTime'] = time.time()
        print(f"DEBUG: Index generation completed for task {task_id}")
        
    except Exception as e:
        # Log the error and update task status
        print(f"DEBUG: Error in index generation: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
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
