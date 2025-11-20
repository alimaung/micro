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
import re
from pathlib import Path
from datetime import datetime
from ..models import Project, Document

# Dictionary to store index tasks and their progress
index_tasks = {}

def validate_barcode(barcode: str) -> tuple[bool, str]:
    """
    Validate that barcode is exactly 16 digits.
    
    Args:
        barcode: Barcode string to validate
        
    Returns:
        Tuple of (is_valid, normalized_barcode)
    """
    if not barcode:
        return False, ""
    
    # Remove any whitespace and convert to string
    clean_barcode = str(barcode).strip()
    
    # Check if it's exactly 16 digits
    if re.match(r'^\d{16}$', clean_barcode):
        return True, clean_barcode
    
    # Try to extract 16 consecutive digits
    digits_only = re.sub(r'\D', '', clean_barcode)
    if len(digits_only) == 16:
        return True, digits_only
    
    return False, clean_barcode

def validate_com_id(com_id) -> tuple[bool, str]:
    """
    Validate that COM ID is exactly 8 digits.
    
    Args:
        com_id: COM ID to validate (can be string, int, float)
        
    Returns:
        Tuple of (is_valid, normalized_com_id)
    """
    if com_id is None:
        return False, ""
    
    # Handle different input types
    if isinstance(com_id, (int, float)):
        # Convert to integer if it's a whole number
        if isinstance(com_id, float) and com_id.is_integer():
            com_id = int(com_id)
        clean_com_id = str(com_id)
    else:
        clean_com_id = str(com_id).strip()
    
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', clean_com_id)
    
    # Check if it's exactly 8 digits
    if len(digits_only) == 8:
        return True, digits_only
    
    # Check if it's less than 8 digits and pad with leading zeros
    if len(digits_only) <= 8 and len(digits_only) > 0:
        padded_com_id = digits_only.zfill(8)
        return True, padded_com_id
    
    return False, clean_com_id

def normalize_document_id(doc_id: str) -> str:
    """
    Normalize document ID by removing .pdf extension and suffixes like _001, _002.
    
    This handles cases where additional documents are added after filming with suffixes.
    For example: 1422022600000227_001.PDF -> 1422022600000227
    
    Args:
        doc_id: Document ID to normalize
        
    Returns:
        Normalized document ID (base barcode without suffix)
    """
    if not doc_id:
        return ""
    
    # Convert to string and strip whitespace
    normalized = str(doc_id).strip()
    
    # Remove .pdf extension (case-insensitive)
    if normalized.lower().endswith('.pdf'):
        normalized = normalized[:-4]
    
    # Remove suffixes like _001, _002, _003, etc. (underscore + digits)
    # This allows documents added after filming to match their base barcode in COM list
    import re
    suffix_pattern = r'_\d{3,}$'  # Match underscore followed by 3+ digits at end
    normalized = re.sub(suffix_pattern, '', normalized)
    
    return normalized

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
                
                # Extract documents using the same nested structure handling
                documents_found = False
                
                # Try to find documents in the nested structure
                if 'documents' in allocation_data:
                    print(f"DEBUG: Found documents directly in allocation_data")
                    for doc in allocation_data['documents']:
                        self.documents.append(PseudoDocument(doc))
                    documents_found = True
                elif 'allocationResults' in allocation_data:
                    alloc_results = allocation_data['allocationResults']
                    if 'documents' in alloc_results:
                        print(f"DEBUG: Found documents in allocationResults")
                        for doc in alloc_results['documents']:
                            self.documents.append(PseudoDocument(doc))
                        documents_found = True
                    elif 'results' in alloc_results and 'documents' in alloc_results['results']:
                        print(f"DEBUG: Found documents in allocationResults.results")
                        for doc in alloc_results['results']['documents']:
                            self.documents.append(PseudoDocument(doc))
                        documents_found = True
                elif 'results' in allocation_data and 'documents' in allocation_data['results']:
                    print(f"DEBUG: Found documents in allocation_data.results")
                    for doc in allocation_data['results']['documents']:
                        self.documents.append(PseudoDocument(doc))
                    documents_found = True
                
                if not documents_found:
                    print(f"DEBUG: No documents found in allocation results")
                    print(f"DEBUG: allocation_data keys: {list(allocation_data.keys())}")
                    if 'results' in allocation_data:
                        print(f"DEBUG: allocation_data['results'] keys: {list(allocation_data['results'].keys())}")
                    if 'allocationResults' in allocation_data:
                        print(f"DEBUG: allocation_data['allocationResults'] keys: {list(allocation_data['allocationResults'].keys())}")
        
        class PseudoFilmAllocation:
            def __init__(self, allocation_data):
                # Handle different data structures: direct data, wrapped in allocationResults, or nested in allocationResults.results
                results = allocation_data
                if 'allocationResults' in allocation_data:
                    alloc_results = allocation_data['allocationResults']
                    if 'results' in alloc_results:
                        results = alloc_results['results']
                    else:
                        results = alloc_results
                
                # Additional check: if results still doesn't have rolls_16mm but has 'results' key, go deeper
                if 'rolls_16mm' not in results and 'results' in results:
                    print(f"DEBUG: Results doesn't have rolls_16mm directly, checking nested results")
                    results = results['results']
                
                print(f"DEBUG: Using allocation results structure with keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
                
                # Extract data from the allocation results
                results = results or {}
                
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
                    
                    # Extract barcode and ComID pairs with robust validation
                    for i in range(start_row, len(data)):
                        if i < len(data) and len(data[i]) >= 2:
                            barcode_raw = data[i][0]
                            com_id_raw = data[i][1]
                            
                            # Validate and normalize barcode (should be 16 digits)
                            barcode_valid, normalized_barcode = validate_barcode(barcode_raw)
                            if not barcode_valid:
                                # Fallback to original format for backward compatibility
                                normalized_barcode = normalize_document_id(str(barcode_raw)) if barcode_raw is not None else ""
                                print(f"DEBUG: Invalid barcode format in row {i}: '{barcode_raw}'. Expected 16 digits.")
                            
                            # Validate and normalize COM ID (should be 8 digits)
                            com_id_valid, normalized_com_id = validate_com_id(com_id_raw)
                            if not com_id_valid and com_id_raw is not None:
                                print(f"DEBUG: Invalid COM ID format in row {i}: '{com_id_raw}'. Expected 8 digits.")
                                continue  # Skip entries with invalid COM IDs
                            
                            print(f"DEBUG: Row {i} - barcode: {barcode_raw} -> {normalized_barcode} (valid: {barcode_valid}), com_id: {com_id_raw} -> {normalized_com_id} (valid: {com_id_valid})")
                            
                            # Store mappings using normalized values
                            if normalized_barcode and normalized_com_id:
                                com_id_mappings[normalized_barcode] = normalized_com_id
                                
                                # Also store original barcode format for backward compatibility
                                if barcode_raw is not None:
                                    original_barcode = str(barcode_raw).strip()
                                    if original_barcode != normalized_barcode:
                                        com_id_mappings[original_barcode] = normalized_com_id
                
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
                
                # Normalize document ID and validate it as barcode
                normalized_doc_id = normalize_document_id(doc_id)
                barcode_valid, validated_barcode = validate_barcode(normalized_doc_id)
                
                # Use validated barcode for COM ID lookup
                lookup_key = validated_barcode if barcode_valid else normalized_doc_id
                
                # Get COM ID from the mapping
                com_id = com_id_mappings.get(lookup_key, None)

                # If not found, try alternative lookup methods with original format
                if com_id is None:
                    # Try with original document ID (remove .pdf extension)
                    com_id = com_id_mappings.get(normalized_doc_id, None)
                    
                    # Try with numeric conversion for backward compatibility
                    if com_id is None:
                        try:
                            numeric_id = str(int(normalized_doc_id))
                            com_id = com_id_mappings.get(numeric_id, None)
                        except (ValueError, TypeError):
                            pass

                # Log validation results
                if not barcode_valid and normalized_doc_id:
                    print(f"DEBUG: Document ID '{doc_id}' is not a valid 16-digit barcode: '{normalized_doc_id}'")

                # If COM ID is still not found, generate a placeholder
                if com_id is None:
                    # Use a placeholder COM ID (negative roll_id to avoid conflicts)
                    com_id = f"PH{roll_id:06d}"  # Use string placeholder instead of negative number
                    print(f"DEBUG: No COM ID found for doc_id: {doc_id} (lookup_key: {lookup_key}), using placeholder: {com_id}")
                else:
                    print(f"DEBUG: Found COM ID: {com_id} for doc_id: {doc_id} (lookup_key: {lookup_key})")
                
                # Update document COM ID if available
                for doc in pseudo_project.documents:
                    if doc.doc_id == doc_id and com_id is not None:
                        doc.com_id = com_id
                
                # Also update the actual Document model in the database
                try:
                    # Use validated barcode or normalized doc_id for database lookup
                    lookup_doc_id = validated_barcode if barcode_valid else normalized_doc_id
                    db_document = Document.objects.filter(project=project, doc_id=lookup_doc_id).first()
                    
                    # Also try with original normalized doc_id if not found
                    if not db_document and lookup_doc_id != normalized_doc_id:
                        db_document = Document.objects.filter(project=project, doc_id=normalized_doc_id).first()
                    
                    if db_document and com_id is not None:
                        # Validate COM ID before storing in database
                        com_id_valid, validated_com_id = validate_com_id(com_id)
                        if com_id_valid:
                            db_document.com_id = validated_com_id
                            db_document.save()
                            print(f"DEBUG: Updated COM ID {validated_com_id} for document {lookup_doc_id} in database")
                        else:
                            print(f"DEBUG: Skipping database update - invalid COM ID format: {com_id}")
                except Exception as e:
                    print(f"DEBUG: Error updating COM ID for document {lookup_doc_id}: {str(e)}")
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
