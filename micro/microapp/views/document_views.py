"""
Document analysis views for the microapp.
These views handle document analysis, processing, and management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ..models import Project

import json
import os
import time
import uuid
import threading
import PyPDF2
from pathlib import Path
from operator import itemgetter
from itertools import groupby

# Dictionary to store analysis tasks and their progress
analysis_tasks = {}

@csrf_exempt
def analyze_documents(request):
    """
    API endpoint to start document analysis for a project.
    
    Args:
        projectId: Project ID (JSON parameter)
        documentsPath: Path to documents directory (JSON parameter)
        
    Returns:
        JSON response with task ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            documents_path = data.get('documentsPath')
            
            # Validate inputs
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            if not documents_path:
                return JsonResponse({
                    'error': 'Documents path is required'
                }, status=400)
                
            # Create a unique ID for this analysis task
            task_id = str(uuid.uuid4())
            
            # Initialize analysis task status
            analysis_tasks[task_id] = {
                'status': 'pending',
                'projectId': project_id,
                'documentsPath': documents_path,
                'progress': 0,
                'currentFile': '',
                'documentCount': 0,
                'totalPages': 0,
                'oversizedPages': 0,
                'documentsWithOversized': 0,
                'results': [],
                'hasOversized': False,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the analysis
            analysis_thread = threading.Thread(
                target=process_document_analysis, 
                args=(task_id, project_id, documents_path)
            )
            analysis_thread.daemon = True
            analysis_thread.start()
            
            return JsonResponse({
                'taskId': task_id,
                'status': 'started',
                'message': 'Document analysis started successfully'
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

def get_analysis_status(request):
    """
    API endpoint to get the status of a document analysis task.
    
    Args:
        taskId: Task ID (GET parameter)
        
    Returns:
        JSON response with the task status
    """
    if request.method == 'GET':
        try:
            task_id = request.GET.get('taskId')
            
            if not task_id or task_id not in analysis_tasks:
                return JsonResponse({
                    'error': 'Invalid or unknown task ID'
                }, status=404)
                
            # Get the analysis task status
            task_status = analysis_tasks[task_id]
            
            # Clean up completed tasks after some time
            if task_status['status'] in ['completed', 'error', 'cancelled']:
                # If the task has been in a final state for more than 30 minutes, clean it up
                if time.time() - task_status['lastUpdateTime'] > 1800:
                    # Before deleting, return the status one last time
                    status_copy = task_status.copy()
                    del analysis_tasks[task_id]
                    return JsonResponse(status_copy)
            
            return JsonResponse(task_status)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def get_analysis_results(request):
    """
    API endpoint to get the full results of a completed document analysis.
    
    Args:
        projectId: Project ID (GET parameter)
        
    Returns:
        JSON response with analysis results
    """
    if request.method == 'GET':
        try:
            project_id = request.GET.get('projectId')
            
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            # Find the most recent completed analysis for this project
            matching_tasks = [task for task_id, task in analysis_tasks.items() 
                             if task['projectId'] == project_id and task['status'] == 'completed']
            
            if not matching_tasks:
                return JsonResponse({
                    'error': 'No completed analysis found for this project'
                }, status=404)
                
            # Sort by lastUpdateTime to get the most recent
            most_recent = sorted(matching_tasks, key=lambda x: x['lastUpdateTime'], reverse=True)[0]
            
            # Return the full results
            return JsonResponse({
                'status': 'success',
                'results': most_recent
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

@csrf_exempt
def calculate_references(request):
    """
    API endpoint to calculate reference sheet positions for documents with oversized pages.
    
    Args:
        projectId: Project ID (JSON parameter)
        
    Returns:
        JSON response with reference sheet calculation results
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            # Find the most recent completed analysis for this project
            matching_tasks = [task for task_id, task in analysis_tasks.items() 
                             if task['projectId'] == project_id and task['status'] == 'completed']
            
            if not matching_tasks:
                return JsonResponse({
                    'error': 'No completed analysis found for this project'
                }, status=404)
                
            # Sort by lastUpdateTime to get the most recent
            analysis_result = sorted(matching_tasks, key=lambda x: x['lastUpdateTime'], reverse=True)[0]
            
            # Only calculate references if there are oversized pages
            if not analysis_result['hasOversized']:
                return JsonResponse({
                    'status': 'success',
                    'message': 'No oversized pages found, no reference sheets needed',
                    'hasReferences': False,
                    'totalPagesWithRefs': analysis_result['totalPages']
                })
            
            # Calculate reference sheets
            references_result = calculate_reference_sheets(analysis_result)
            
            # Update the analysis task with reference information
            for task_id, task in analysis_tasks.items():
                if task['projectId'] == project_id and task['status'] == 'completed':
                    task.update(references_result)
                    task['lastUpdateTime'] = time.time()
            
            return JsonResponse({
                'status': 'success',
                'hasReferences': True,
                'totalReferences': references_result['totalReferences'],
                'totalPagesWithRefs': references_result['totalPagesWithRefs'],
                'documents': references_result['documents']
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
def select_workflow(request):
    """
    API endpoint to set the workflow type for a project based on analysis.
    
    Args:
        projectId: Project ID (JSON parameter)
        workflowType: Workflow type (standard or hybrid) (JSON parameter)
        
    Returns:
        JSON response with status and message
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            workflow_type = data.get('workflowType')
            
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            if not workflow_type or workflow_type not in ['standard', 'hybrid']:
                return JsonResponse({
                    'error': 'Valid workflow type is required (standard or hybrid)'
                }, status=400)
            
            try:
                # Get the project from the database
                project = Project.objects.get(id=project_id)
                
                # Update the project with workflow information
                project.workflow_type = workflow_type
                project.has_oversized = workflow_type == 'hybrid'
                project.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Workflow set to {workflow_type} for project {project_id}'
                })
                
            except Project.DoesNotExist:
                return JsonResponse({
                    'error': 'Project not found'
                }, status=404)
            
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

def process_document_analysis(task_id, project_id, documents_path):
    """
    Background process to analyze documents in a project.
    
    Args:
        task_id: The unique ID for this analysis task
        project_id: The project ID
        documents_path: The path to the documents directory
        
    Returns:
        None
    """
    task = analysis_tasks[task_id]
    task['status'] = 'in-progress'
    
    try:
        # Convert path to Path object
        path = Path(documents_path)
        
        # Check if the path exists and is a directory
        if not path.exists():
            task['status'] = 'error'
            task['errors'].append(f"Documents path does not exist: {documents_path}")
            task['lastUpdateTime'] = time.time()
            return
            
        if not path.is_dir():
            task['status'] = 'error'
            task['errors'].append(f"Documents path is not a directory: {documents_path}")
            task['lastUpdateTime'] = time.time()
            return
        
        # Find PDF files in the folder
        pdf_files = sorted([f for f in os.listdir(path) if f.lower().endswith('.pdf')],
                          key=lambda x: x.lower())
        
        if not pdf_files:
            task['status'] = 'completed'
            task['progress'] = 100
            task['message'] = f"No PDF documents found in {documents_path}"
            task['lastUpdateTime'] = time.time()
            return
        
        # Initialize counters
        total_files = len(pdf_files)
        task['documentCount'] = total_files
        processed_files = 0
        
        # Constants for oversized page detection
        OVERSIZE_THRESHOLD_WIDTH = 842  # A3 width in points
        OVERSIZE_THRESHOLD_HEIGHT = 1191  # A3 height in points
        
        # Process each document
        for pdf_file in pdf_files:
            # Update current file being processed
            task['currentFile'] = pdf_file
            
            # Process a single document
            doc_path = path / pdf_file
            
            try:
                # Create a document result object
                doc_result = {
                    'name': pdf_file,
                    'path': str(doc_path),
                    'pages': 0,
                    'hasOversized': False,
                    'totalOversized': 0,
                    'oversizedPages': [],
                    'dimensions': []
                }
                
                # Read the PDF file
                pdf_reader = PyPDF2.PdfReader(str(doc_path))
                page_count = len(pdf_reader.pages)
                doc_result['pages'] = page_count
                
                # Update total pages
                task['totalPages'] += page_count
                
                # Check each page for oversized dimensions
                for i, page in enumerate(pdf_reader.pages):
                    # Get page dimensions from mediabox
                    mediabox = page.mediabox
                    width, height = float(mediabox[2]), float(mediabox[3])
                    
                    # Check if page is oversized
                    is_oversized = ((width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
                                    (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH))
                    
                    # Record oversized pages
                    if is_oversized:
                        # Calculate percentage over threshold
                        width_percent = (width / OVERSIZE_THRESHOLD_WIDTH - 1) * 100
                        height_percent = (height / OVERSIZE_THRESHOLD_HEIGHT - 1) * 100
                        max_percent = max(width_percent, height_percent)
                        
                        # Mark document as having oversized pages
                        doc_result['hasOversized'] = True
                        task['hasOversized'] = True
                        
                        # Increment oversized page counters
                        doc_result['totalOversized'] += 1
                        task['oversizedPages'] += 1
                        
                        # Add page to list of oversized pages
                        doc_result['oversizedPages'].append(i + 1)  # 1-based page number
                        
                        # Store page dimensions
                        doc_result['dimensions'].append({
                            'page': i + 1,
                            'width': width,
                            'height': height,
                            'oversize_percent': max_percent
                        })
                
                # If document has oversized pages, increment counter
                if doc_result['hasOversized']:
                    task['documentsWithOversized'] += 1
                
                # Add document to results
                task['results'].append(doc_result)
                
            except Exception as e:
                # Log error but continue processing
                task['errors'].append(f"Error processing {pdf_file}: {str(e)}")
            
            # Update progress
            processed_files += 1
            task['progress'] = int((processed_files / total_files) * 100)
            task['lastUpdateTime'] = time.time()
        
        # Mark task as completed
        task['status'] = 'completed'
        task['message'] = f"Processed {total_files} documents with {task['totalPages']} total pages"
        task['lastUpdateTime'] = time.time()
        
    except Exception as e:
        task['status'] = 'error'
        task['errors'].append(f"Analysis failed: {str(e)}")
        task['lastUpdateTime'] = time.time()

def calculate_reference_sheets(analysis_result):
    """
    Calculate reference page positions for documents with oversized pages.
    
    Args:
        analysis_result: The analysis result containing document information
        
    Returns:
        Dictionary with reference sheet calculation results
    """
    if not analysis_result['hasOversized']:
        return {
            'totalReferences': 0,
            'totalPagesWithRefs': analysis_result['totalPages'],
            'documents': []
        }
    
    total_references = 0
    documents_with_refs = []
    
    for document in analysis_result['results']:
        # Skip documents with no oversized pages
        if not document['hasOversized'] or not document['oversizedPages']:
            document['referencePages'] = []
            document['totalReferences'] = 0
            document['adjusted_ranges'] = []  # Add empty adjusted ranges
            documents_with_refs.append(document)
            continue
        
        # Group consecutive oversized pages into ranges
        ranges = []
        for k, g in groupby(enumerate(sorted(document['oversizedPages'])), lambda x: x[0] - x[1]):
            group = list(map(itemgetter(1), g))
            if group:
                ranges.append((group[0], group[-1]))
        
        # Calculate reference page positions (one reference page per range)
        reference_pages = []
        
        for range_start, _ in ranges:
            reference_pages.append(range_start)
        
        # Update document with reference information
        document['referencePages'] = reference_pages
        document['totalReferences'] = len(reference_pages)
        document['ranges'] = ranges
        
        # Calculate adjusted ranges (accounting for inserted reference sheets)
        adjusted_ranges = []
        shift = 0  # Track how many reference sheets have been inserted
        
        for i, (start, end) in enumerate(ranges):
            # Adjust the range start and end based on previously inserted reference sheets
            adjusted_start = start + shift
            adjusted_end = end + shift
            
            # Store the adjusted range
            adjusted_ranges.append({
                'original': (start, end),
                'adjusted': (adjusted_start, adjusted_end),
                'reference_page': reference_pages[i] + shift  # The reference page also needs adjustment
            })
            
            # Increment shift for next ranges
            shift += 1
        
        document['adjusted_ranges'] = adjusted_ranges
        
        # Add readable descriptions of reference pages
        document['readablePages'] = [
            f"{i+1} of {len(ranges)}" for i in range(len(ranges))
        ]
        
        total_references += document['totalReferences']
        documents_with_refs.append(document)
    
    return {
        'totalReferences': total_references,
        'totalPagesWithRefs': analysis_result['totalPages'] + total_references,
        'documents': documents_with_refs
    } 