"""
Film Allocation views for the microapp.
These views handle film allocation, processing, and management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json
import os
import time
import uuid
import threading
from pathlib import Path
from enum import Enum
import re

# Dictionary to store allocation tasks and their progress
allocation_tasks = {}

# Helper function for natural sorting
def natural_sort_key(item):
    """
    Natural sorting key function.
    Sorts strings with embedded numbers in the expected human way.
    For example: ["1", "10", "2"] sorts to ["1", "2", "10"]
    """
    if not isinstance(item, str):
        item = str(item)
    
    def atoi(text):
        return int(text) if text.isdigit() else text
    
    return [atoi(c) for c in re.split(r'(\d+)', item)]

# Constants for film capacity - matching the original implementation
CAPACITY_16MM = 2940  # Pages per 16mm film roll
CAPACITY_35MM = 690   # Pages per 35mm film roll

# Constants for partial roll padding
PADDING_16MM = 150  # Padding for 16mm partial rolls
PADDING_35MM = 150  # Padding for 35mm partial rolls

class FilmType(Enum):
    """Type of film used for microfilming."""
    FILM_16MM = "16mm"
    FILM_35MM = "35mm"

@csrf_exempt
def allocate_film(request):
    """
    API endpoint to start film allocation for a project.
    
    Args:
        projectId: Project ID (JSON parameter)
        analysisResults: Document analysis results (JSON parameter)
        
    Returns:
        JSON response with task ID and status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            analysis_results = data.get('analysisResults')
            
            # Validate inputs
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            if not analysis_results:
                return JsonResponse({
                    'error': 'Analysis results are required'
                }, status=400)
                
            # Create a unique ID for this allocation task
            task_id = str(uuid.uuid4())
            
            # Initialize allocation task status
            allocation_tasks[task_id] = {
                'status': 'pending',
                'projectId': project_id,
                'progress': 0,
                'hasOversized': analysis_results.get('hasOversized', False),
                'documentCount': analysis_results.get('documentCount', 0),
                'totalPages': analysis_results.get('totalPages', 0),
                'totalPagesWithRefs': analysis_results.get('totalPagesWithRefs', 0),
                'totalOversized': analysis_results.get('oversizedPages', 0),
                'documentsWithOversized': analysis_results.get('documentsWithOversized', 0),
                'results': None,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the allocation
            allocation_thread = threading.Thread(
                target=process_film_allocation, 
                args=(task_id, project_id, analysis_results)
            )
            allocation_thread.daemon = True
            allocation_thread.start()
            
            return JsonResponse({
                'taskId': task_id,
                'status': 'started',
                'message': 'Film allocation started successfully'
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

def get_allocation_status(request):
    """
    API endpoint to get the status of a film allocation task.
    
    Args:
        taskId: Task ID (GET parameter)
        
    Returns:
        JSON response with the task status
    """
    if request.method == 'GET':
        try:
            task_id = request.GET.get('taskId')
            
            if not task_id or task_id not in allocation_tasks:
                return JsonResponse({
                    'error': 'Invalid or unknown task ID'
                }, status=404)
                
            # Get the allocation task status
            task_status = allocation_tasks[task_id]
            
            # Clean up completed tasks after some time
            if task_status['status'] in ['completed', 'error', 'cancelled']:
                # If the task has been in a final state for more than 30 minutes, clean it up
                if time.time() - task_status['lastUpdateTime'] > 1800:
                    # Before deleting, return the status one last time
                    status_copy = task_status.copy()
                    del allocation_tasks[task_id]
                    return JsonResponse(status_copy)
            
            return JsonResponse(task_status)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def get_allocation_results(request):
    """
    API endpoint to get the full results of a completed film allocation.
    
    Args:
        projectId: Project ID (GET parameter)
        
    Returns:
        JSON response with allocation results
    """
    if request.method == 'GET':
        try:
            project_id = request.GET.get('projectId')
            
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
                
            # Find the most recent completed allocation for this project
            matching_tasks = [task for task_id, task in allocation_tasks.items() 
                             if task['projectId'] == project_id and task['status'] == 'completed']
            
            if not matching_tasks:
                return JsonResponse({
                    'error': 'No completed allocation found for this project'
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

def process_film_allocation(task_id, project_id, analysis_results):
    """
    Process film allocation in a background thread.
    
    Args:
        task_id: ID of the allocation task
        project_id: ID of the project
        analysis_results: Results from document analysis
    """
    try:
        # Get the task to update it
        task = allocation_tasks[task_id]
        task['status'] = 'in_progress'
        task['progress'] = 10
        task['lastUpdateTime'] = time.time()
        
        # Debug incoming data structure
        print(f"Processing allocation for project {project_id}")
        print(f"Analysis results keys: {list(analysis_results.keys())}")
        print(f"Has oversized: {analysis_results.get('hasOversized', False)}")
        
        # Extract required information
        has_oversized = analysis_results.get('hasOversized', False)
        
        # Handle different document array formats
        documents = []
        if 'documents' in analysis_results and analysis_results['documents']:
            print("Using 'documents' array for allocation")
            documents = analysis_results['documents']
        elif 'results' in analysis_results and analysis_results['results']:
            if isinstance(analysis_results['results'], list):
                print("Using 'results' array for allocation")
                documents = analysis_results['results']
            elif isinstance(analysis_results['results'], dict) and 'documents' in analysis_results['results']:
                print("Using nested 'results.documents' array for allocation")
                documents = analysis_results['results']['documents']
            
        project_name = analysis_results.get('projectName', f"Project-{project_id}")
        archive_id = analysis_results.get('archiveId', f"RRD00-{project_id}")

        print(f"Found {len(documents)} documents to allocate")
        if not documents or len(documents) == 0:
            print("Warning: No documents to allocate")
            # Create an empty film allocation to prevent errors
            film_allocation = {
                'archive_id': archive_id,
                'project_name': project_name,
                'rolls_16mm': [],
                'rolls_35mm': [],
                'split_documents_16mm': {},
                'split_documents_35mm': {},
                'partial_rolls_16mm': [],
                'partial_rolls_35mm': [],
                'total_rolls_16mm': 0,
                'total_pages_16mm': 0,
                'total_partial_rolls_16mm': 0,
                'total_split_documents_16mm': 0,
                'total_rolls_35mm': 0,
                'total_pages_35mm': 0,
                'total_partial_rolls_35mm': 0,
                'total_split_documents_35mm': 0,
                'doc_allocation_requests_35mm': [],
                'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'version': '1.0'
            }
            
            # Save the result
            task['results'] = film_allocation
            task['status'] = 'completed'
            task['progress'] = 100
            task['lastUpdateTime'] = time.time()
            return
            
        if documents and len(documents) > 0:
            print(f"First document structure: {documents[0]}")
            # Check for oversized documents
            oversized_docs = [doc for doc in documents if doc.get('hasOversized', False)]
            print(f"Found {len(oversized_docs)} oversized documents")
            if oversized_docs:
                print(f"First oversized document: {oversized_docs[0]}")

        # Create film allocation structure
        film_allocation = {
            'archive_id': archive_id,
            'project_name': project_name,
            'rolls_16mm': [],
            'rolls_35mm': [],
            'split_documents_16mm': {},
            'split_documents_35mm': {},
            'partial_rolls_16mm': [],
            'partial_rolls_35mm': [],
            'total_rolls_16mm': 0,
            'total_pages_16mm': 0,
            'total_partial_rolls_16mm': 0,
            'total_split_documents_16mm': 0,
            'total_rolls_35mm': 0,
            'total_pages_35mm': 0,
            'total_partial_rolls_35mm': 0,
            'total_split_documents_35mm': 0,
            'doc_allocation_requests_35mm': [],
            'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'version': '1.0'
        }
        
        # Ensure documents have docId set (fallback to name if needed)
        for doc in documents:
            if not doc.get('docId', ''):
                doc['docId'] = doc.get('name', f'doc-{hash(str(doc.get("path", "")))}')
        
        # Sort documents using natural sorting
        sorted_documents = sorted(documents, key=lambda d: natural_sort_key(d.get('docId', '') or d.get('name', '')))
        
        task['progress'] = 20
        task['lastUpdateTime'] = time.time()
        
        # Allocate documents based on whether there are oversized pages
        if has_oversized:
            print("Using hybrid allocation for oversized documents")
            # Specialized allocation for oversized documents
            film_allocation = allocate_with_oversized(film_allocation, sorted_documents)
        else:
            print("Using standard allocation for documents")
            # Standard allocation (no oversized pages)
            film_allocation = allocate_no_oversized(film_allocation, sorted_documents)
        
        task['progress'] = 80
        task['lastUpdateTime'] = time.time()
        
        #print("\033[31m" + f"Film allocation structure: {film_allocation}" + "\033[0m")
        # Update statistics 
        film_allocation = update_statistics(film_allocation)
        
        # Log allocation results
        print(f"Allocation complete: {film_allocation['total_rolls_16mm']} 16mm rolls, {film_allocation['total_rolls_35mm']} 35mm rolls")
        if film_allocation['total_rolls_35mm'] == 0 and has_oversized:
            print("Warning: No 35mm rolls were created despite having oversized documents")
            print(f"35mm allocation requests: {len(film_allocation['doc_allocation_requests_35mm'])}")
        
        # Save the result
        task['results'] = film_allocation
        task['status'] = 'completed'
        task['progress'] = 100
        task['lastUpdateTime'] = time.time()
        
    except Exception as e:
        # Update task with error
        print(f"Error during allocation: {str(e)}")
        import traceback
        traceback.print_exc()
        
        task = allocation_tasks[task_id]
        task['status'] = 'error'
        task['errors'].append(str(e))
        task['lastUpdateTime'] = time.time()

def allocate_no_oversized(film_allocation, documents):
    """
    Allocate documents to 16mm film rolls when there are no oversized pages.
    
    Args:
        film_allocation: Film allocation structure to update
        documents: List of documents to allocate
        
    Returns:
        Updated film allocation structure
    """
    # Track which documents are split across rolls
    split_documents = set()
    
    # Initialize the first roll
    current_roll_id = 1
    current_roll = {
        'roll_id': current_roll_id,
        'film_type': FilmType.FILM_16MM.value,
        'capacity': CAPACITY_16MM,
        'pages_used': 0,
        'pages_remaining': CAPACITY_16MM,
        'document_segments': [],
        'film_number': None,
        'status': 'active',
        'has_split_documents': False,
        'is_partial': False,
        'remaining_capacity': 0,
        'usable_capacity': 0,
        'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
    }
    
    # Add roll to allocation
    film_allocation['rolls_16mm'].append(current_roll)
    
    # Process each document in alphabetical order
    for document in documents:
        # Get document ID (use name as fallback)
        doc_id = document.get('docId', '') or document.get('name', '')
        doc_path = document.get('path', '')
        
        # Support different field names for page count
        doc_pages = document.get('totalPagesWithRefs', 0) or document.get('pages', 0)
        if isinstance(doc_pages, str):
            try:
                doc_pages = int(doc_pages)
            except ValueError:
                print(f"Warning: Invalid page count for document {doc_id}: {doc_pages}")
                doc_pages = 0
        
        # Skip documents with no pages
        if doc_pages <= 0:
            print(f"Warning: Skipping document with 0 pages: {doc_id}")
            continue
            
        has_oversized = document.get('hasOversized', False)
        
        # Check if document exceeds roll capacity (needs splitting)
        if doc_pages > CAPACITY_16MM:
            # Document requires splitting
            pages_left_to_allocate = doc_pages
            start_page = 1
            doc_roll_count = 0
            
            # Continue allocating pages until the entire document is allocated
            while pages_left_to_allocate > 0:
                current_roll = film_allocation['rolls_16mm'][-1]  # Get the last roll
                
                # Calculate how many pages can fit in the current roll
                pages_to_allocate = min(pages_left_to_allocate, current_roll['pages_remaining'])
                
                if pages_to_allocate > 0:
                    end_page = start_page + pages_to_allocate - 1
                    
                    # Add document segment to roll
                    add_document_segment(current_roll, doc_id, doc_path, pages_to_allocate, 
                                        (start_page, end_page), has_oversized)
                    
                    # Update tracking variables
                    pages_left_to_allocate -= pages_to_allocate
                    start_page = end_page + 1
                    doc_roll_count += 1
                
                # If we need more space and there are still pages to allocate, create a new roll
                if pages_left_to_allocate > 0:
                    # Mark the document as split
                    split_documents.add(doc_id)
                    current_roll['has_split_documents'] = True
                    
                    # Create a new roll
                    current_roll_id += 1
                    new_roll = {
                        'roll_id': current_roll_id,
                        'film_type': FilmType.FILM_16MM.value,
                        'capacity': CAPACITY_16MM,
                        'pages_used': 0,
                        'pages_remaining': CAPACITY_16MM,
                        'document_segments': [],
                        'film_number': None,
                        'status': 'active',
                        'has_split_documents': False,
                        'is_partial': False,
                        'remaining_capacity': 0,
                        'usable_capacity': 0,
                        'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
                    }
                    
                    # Add roll to allocation
                    film_allocation['rolls_16mm'].append(new_roll)
            
            # After allocating all pages, update document
            document['is_split'] = doc_roll_count > 1
            document['roll_count'] = doc_roll_count
        else:
            # Normal sized document - don't split unless necessary
            current_roll = film_allocation['rolls_16mm'][-1]  # Get the last roll
            
            # Check if this document fits completely in the current roll
            if doc_pages <= current_roll['pages_remaining']:
                # It fits completely - allocate it
                add_document_segment(current_roll, doc_id, doc_path, doc_pages, 
                                    (1, doc_pages), has_oversized)
                
                # Document fits on a single roll
                document['is_split'] = False
                document['roll_count'] = 1
            else:
                # Document doesn't fit in current roll - need to create a new roll
                
                # Mark current roll as partial
                current_roll['is_partial'] = True
                current_roll['remaining_capacity'] = current_roll['pages_remaining']
                current_roll['usable_capacity'] = current_roll['pages_remaining'] - PADDING_16MM
                
                film_allocation['partial_rolls_16mm'].append({
                    'roll_id': current_roll['roll_id'],
                    'remainingCapacity': current_roll['remaining_capacity'],
                    'usableCapacity': current_roll['usable_capacity'],
                    'isAvailable': True,
                    'creation_date': current_roll['creation_date']
                })
                
                # Create a new roll
                current_roll_id += 1
                new_roll = {
                    'roll_id': current_roll_id,
                    'film_type': FilmType.FILM_16MM.value,
                    'capacity': CAPACITY_16MM,
                    'pages_used': 0,
                    'pages_remaining': CAPACITY_16MM,
                    'document_segments': [],
                    'film_number': None,
                    'status': 'active',
                    'has_split_documents': False,
                    'is_partial': False,
                    'remaining_capacity': 0,
                    'usable_capacity': 0,
                    'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
                }
                
                # Add roll to allocation
                film_allocation['rolls_16mm'].append(new_roll)
                
                # Now add the document to the new roll
                add_document_segment(new_roll, doc_id, doc_path, doc_pages, 
                                    (1, doc_pages), has_oversized)
                
                # Document fits on a single roll (the new one)
                document['is_split'] = False
                document['roll_count'] = 1
    
    # Check if the last roll is a partial roll
    if film_allocation['rolls_16mm'][-1]['pages_remaining'] > 0:
        last_roll = film_allocation['rolls_16mm'][-1]
        last_roll['is_partial'] = True
        last_roll['remaining_capacity'] = last_roll['pages_remaining']
        last_roll['usable_capacity'] = last_roll['pages_remaining'] - PADDING_16MM
        
        # Only add to partial_rolls if not already there
        already_in_partial = any(pr['roll_id'] == last_roll['roll_id'] for pr in film_allocation['partial_rolls_16mm'])
        if not already_in_partial:
            film_allocation['partial_rolls_16mm'].append({
                'roll_id': last_roll['roll_id'],
                'remainingCapacity': last_roll['remaining_capacity'],
                'usableCapacity': last_roll['usable_capacity'],
                'isAvailable': True,
                'creation_date': last_roll['creation_date']
            })
    
    # Add detailed information about split documents
    for doc_id in split_documents:
        film_allocation['split_documents_16mm'][doc_id] = []
        
        # Find all rolls containing this document
        for roll in film_allocation['rolls_16mm']:
            segments = [seg for seg in roll['document_segments'] if seg['doc_id'] == doc_id]
            for segment in segments:
                film_allocation['split_documents_16mm'][doc_id].append({
                    'roll': roll['roll_id'],
                    'pageRange': segment['page_range'],
                    'frameRange': segment.get('frame_range', [0, 0])
                })
    
    # Sort the split document keys using natural sorting
    sorted_split_docs = {}
    for doc_id in sorted(split_documents, key=natural_sort_key):
        sorted_split_docs[doc_id] = film_allocation['split_documents_16mm'][doc_id]
    
    film_allocation['split_documents_16mm'] = sorted_split_docs
    
    return film_allocation

def allocate_with_oversized(film_allocation, documents):
    """
    Allocate documents to 16mm and 35mm film rolls when there are oversized pages.
    
    Args:
        film_allocation: Film allocation structure to update
        documents: List of documents to allocate
        
    Returns:
        Updated film allocation structure
    """
    print(f"Starting hybrid allocation with {len(documents)} documents")
    
    # First, allocate all standard pages to 16mm film rolls
    film_allocation = allocate_16mm_with_oversized(film_allocation, documents)
    
    # Check if we need to process any 35mm allocation
    standard_only = all(not doc.get('hasOversized', False) for doc in documents)
    if standard_only:
        print("Warning: No oversized documents found in hybrid workflow")
        return film_allocation
    
    # Next, allocate oversized pages to 35mm film rolls
    film_allocation = allocate_35mm_strict(film_allocation, documents)
    #print("\033[32m" + f"Film allocation structure after allocation: {film_allocation}" + "\033[0m") # Exists
    
    # Process 35mm allocation requests into proper roll allocations
    if film_allocation['doc_allocation_requests_35mm']:
        film_allocation = process_35mm_allocation_requests(film_allocation)
        
    #print("\033[31m" + f"Film allocation structure after allocation: {film_allocation}" + "\033[0m") # None
    return film_allocation

def allocate_16mm_with_oversized(film_allocation, documents):
    """
    Allocate documents to 16mm film rolls when project has oversized pages.
    
    This is similar to allocate_no_oversized but handles the complexities
    of documents with oversized pages and reference sheets.
    
    Args:
        film_allocation: Film allocation structure to update
        documents: List of documents to allocate
        
    Returns:
        Updated film allocation structure
    """
    print("Allocating documents to 16mm film with oversized support")
    print(f"Processing {len(documents)} documents")
    
    # Track which documents are split across rolls
    split_documents = set()
    
    # Initialize the first roll if needed
    if not film_allocation['rolls_16mm']:
        current_roll_id = 1
        current_roll = {
            'roll_id': current_roll_id,
            'film_type': FilmType.FILM_16MM.value,
            'capacity': CAPACITY_16MM,
            'pages_used': 0,
            'pages_remaining': CAPACITY_16MM,
            'document_segments': [],
            'film_number': None,
            'status': 'active',
            'has_split_documents': False,
            'is_partial': False,
            'remaining_capacity': 0,
            'usable_capacity': 0,
            'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
        }
        
        # Add roll to allocation
        film_allocation['rolls_16mm'].append(current_roll)
        
        print(f"Created 16mm roll {current_roll_id} with capacity {CAPACITY_16MM}")
    else:
        current_roll_id = len(film_allocation['rolls_16mm'])
        current_roll = film_allocation['rolls_16mm'][-1]
        
    # Process each document in alphabetical order
    for document in documents:
        # Get document ID (use name as fallback)
        doc_id = document.get('docId', '') or document.get('name', '')
        doc_path = document.get('path', '')
        
        # Support different field names for page count
        doc_base_pages = document.get('pages', 0)
        if isinstance(doc_base_pages, str):
            try:
                doc_base_pages = int(doc_base_pages)
            except ValueError:
                print(f"Warning: Invalid page count for document {doc_id}: {doc_base_pages}")
                doc_base_pages = 0
                
        # Check if the document has oversized pages and calculate reference sheets
        has_oversized = document.get('hasOversized', False)
        reference_count = 0
        
        # If document has oversized pages, then we need to account for reference pages
        if has_oversized:
            # Try to get the reference count from various possible fields
            reference_count = (
                document.get('totalReferences', 0) or 
                document.get('referenceCount', 0)
            )
            
            # If no reference count is explicitly stored, calculate from oversized pages
            if reference_count == 0 and 'oversizedPages' in document and isinstance(document['oversizedPages'], list):
                reference_count = len(document['oversizedPages'])
                
            # If still no reference count but we know it has oversized pages, try to get total oversized count
            if reference_count == 0:
                reference_count = (
                    document.get('totalOversized', 0) or 
                    document.get('oversizedCount', 0)
                )
                
            print(f"Document {doc_id} has {reference_count} reference pages for oversized content")
        
        # Calculate total pages including references
        doc_pages = doc_base_pages + reference_count
        
        # Use totalPagesWithRefs if available as a failsafe
        if 'totalPagesWithRefs' in document and document['totalPagesWithRefs'] > doc_pages:
            doc_pages = document['totalPagesWithRefs']
        
        print(f"Processing document {doc_id} with {doc_pages} total pages (including {reference_count} references)")
        
        # Check if document exceeds roll capacity (needs splitting)
        if doc_pages > CAPACITY_16MM:
            print(f"Document {doc_id} exceeds roll capacity, will be split across rolls")
            
            # Document requires splitting
            pages_left_to_allocate = doc_pages
            start_page = 1
            doc_roll_count = 0
            
            # Continue allocating pages until the entire document is allocated
            while pages_left_to_allocate > 0:
                current_roll = film_allocation['rolls_16mm'][-1]  # Get the last roll
                
                # Calculate how many pages can fit in the current roll
                pages_to_allocate = min(pages_left_to_allocate, current_roll['pages_remaining'])
                
                if pages_to_allocate > 0:
                    end_page = start_page + pages_to_allocate - 1
                    
                    # Add document segment to roll
                    add_document_segment(current_roll, doc_id, doc_path, pages_to_allocate, 
                                        (start_page, end_page), has_oversized)
                    
                    print(f"Added {pages_to_allocate} pages of document {doc_id} to roll {current_roll['roll_id']}")
                    
                    # Update tracking variables
                    pages_left_to_allocate -= pages_to_allocate
                    start_page = end_page + 1
                    doc_roll_count += 1
                
                # If we need more space and there are still pages to allocate, create a new roll
                if pages_left_to_allocate > 0:
                    # Mark the document as split
                    split_documents.add(doc_id)
                    current_roll['has_split_documents'] = True
                    
                    print(f"Document {doc_id} needs more rolls for allocation, {pages_left_to_allocate} pages remaining")
                    
                    # Create a new roll
                    current_roll_id += 1
                    new_roll = {
                        'roll_id': current_roll_id,
                        'film_type': FilmType.FILM_16MM.value,
                        'capacity': CAPACITY_16MM,
                        'pages_used': 0,
                        'pages_remaining': CAPACITY_16MM,
                        'document_segments': [],
                        'film_number': None,
                        'status': 'active',
                        'has_split_documents': False,
                        'is_partial': False,
                        'remaining_capacity': 0,
                        'usable_capacity': 0,
                        'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
                    }
                    
                    # Add roll to allocation
                    film_allocation['rolls_16mm'].append(new_roll)
                    
                    print(f"Created new roll {current_roll_id} with capacity {CAPACITY_16MM}")
            
            # After allocating all pages, update document
            document['is_split'] = doc_roll_count > 1
            document['roll_count'] = doc_roll_count
            
            if document['is_split']:
                print(f"Document {doc_id} is split across {doc_roll_count} rolls")
        else:
            # Normal sized document - don't split unless necessary
            current_roll = film_allocation['rolls_16mm'][-1]  # Get the last roll
            
            # Check if this document fits completely in the current roll
            if doc_pages <= current_roll['pages_remaining']:
                # It fits completely - allocate it
                add_document_segment(current_roll, doc_id, doc_path, doc_pages, 
                                    (1, doc_pages), has_oversized)
                
                print(f"Added document {doc_id} with {doc_pages} pages to roll {current_roll['roll_id']}")
                
                # Document fits on a single roll
                document['is_split'] = False
                document['roll_count'] = 1
            else:
                # Document doesn't fit in current roll - need to create a new roll
                print(f"Document {doc_id} doesn't fit in current roll (needs {doc_pages}, {current_roll['pages_remaining']} available), creating new roll")
                
                # Mark current roll as partial
                current_roll['is_partial'] = True
                current_roll['remaining_capacity'] = current_roll['pages_remaining']
                current_roll['usable_capacity'] = current_roll['pages_remaining'] - PADDING_16MM
                
                # Only add to partial_rolls if not already there
                already_in_partial = any(pr['roll_id'] == current_roll['roll_id'] for pr in film_allocation['partial_rolls_16mm'])
                if not already_in_partial:
                    film_allocation['partial_rolls_16mm'].append({
                        'roll_id': current_roll['roll_id'],
                        'remainingCapacity': current_roll['remaining_capacity'],
                        'usableCapacity': current_roll['usable_capacity'],
                        'isAvailable': True,
                        'creation_date': current_roll['creation_date']
                    })
                
                print(f"Marked roll {current_roll['roll_id']} as partial with {current_roll['remaining_capacity']} pages remaining")
                
                # Create a new roll
                current_roll_id += 1
                new_roll = {
                    'roll_id': current_roll_id,
                    'film_type': FilmType.FILM_16MM.value,
                    'capacity': CAPACITY_16MM,
                    'pages_used': 0,
                    'pages_remaining': CAPACITY_16MM,
                    'document_segments': [],
                    'film_number': None,
                    'status': 'active',
                    'has_split_documents': False,
                    'is_partial': False,
                    'remaining_capacity': 0,
                    'usable_capacity': 0,
                    'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
                }
                
                # Add roll to allocation
                film_allocation['rolls_16mm'].append(new_roll)
                
                print(f"Created new roll {current_roll_id} with capacity {CAPACITY_16MM}")
                
                # Now add the document to the new roll
                add_document_segment(new_roll, doc_id, doc_path, doc_pages, 
                                    (1, doc_pages), has_oversized)
                
                print(f"Added document {doc_id} with {doc_pages} pages to new roll {new_roll['roll_id']}")
                
                # Document fits on a single roll (the new one)
                document['is_split'] = False
                document['roll_count'] = 1
    
    # Check if the last roll is a partial roll
    if film_allocation['rolls_16mm'] and film_allocation['rolls_16mm'][-1]['pages_remaining'] > 0:
        last_roll = film_allocation['rolls_16mm'][-1]
        
        # Only mark as partial if not already marked
        if not last_roll['is_partial']:
            last_roll['is_partial'] = True
            last_roll['remaining_capacity'] = last_roll['pages_remaining']
            last_roll['usable_capacity'] = last_roll['pages_remaining'] - PADDING_16MM
            
            # Only add to partial_rolls if not already there
            already_in_partial = any(pr['roll_id'] == last_roll['roll_id'] for pr in film_allocation['partial_rolls_16mm'])
            if not already_in_partial:
                film_allocation['partial_rolls_16mm'].append({
                    'roll_id': last_roll['roll_id'],
                    'remainingCapacity': last_roll['remaining_capacity'],
                    'usableCapacity': last_roll['usable_capacity'],
                    'isAvailable': True,
                    'creation_date': last_roll['creation_date']
                })
            
            print(f"Last roll {last_roll['roll_id']} is partial with {last_roll['remaining_capacity']} pages remaining")
    
    # Add detailed information about split documents
    for doc_id in split_documents:
        film_allocation['split_documents_16mm'][doc_id] = []
        
        # Find all rolls containing this document
        for roll in film_allocation['rolls_16mm']:
            segments = [seg for seg in roll['document_segments'] if seg['doc_id'] == doc_id]
            for segment in segments:
                film_allocation['split_documents_16mm'][doc_id].append({
                    'roll': roll['roll_id'],
                    'pageRange': segment['page_range'],
                    'frameRange': segment['frame_range']
                })
    
    print(f"16mm allocation complete with oversized support")
    print(f"Total 16mm rolls: {len(film_allocation['rolls_16mm'])}")
    print(f"Total 16mm pages: {sum(roll['pages_used'] for roll in film_allocation['rolls_16mm'])}")
    print(f"Total partial 16mm rolls: {len(film_allocation['partial_rolls_16mm'])}")
    print(f"Total split documents on 16mm: {len(film_allocation['split_documents_16mm'])}")
    
    return film_allocation

def allocate_35mm_strict(film_allocation, documents):
    """
    Allocate oversized pages to 35mm film in strict alphabetical order.
    Creates document allocation requests, then processes those into rolls.
    
    Args:
        film_allocation: Film allocation structure to update
        documents: List of documents to allocate
        
    Returns:
        Updated film allocation structure
    """
    # Filter for documents with oversized pages
    oversized_docs = [doc for doc in documents if doc.get('hasOversized', False)]
    
    # Skip processing if no oversized documents
    if not oversized_docs:
        print("No oversized documents found for 35mm allocation")
        return film_allocation
        
    # Sort oversized documents by document ID using natural sorting
    sorted_oversized_docs = sorted(oversized_docs, key=lambda d: natural_sort_key(d.get('docId', '') or d.get('name', '')))
    
    print(f"Allocating {len(sorted_oversized_docs)} oversized documents to 35mm film")
    
    # Initialize the document allocation requests and prepare film rolls array
    film_allocation['doc_allocation_requests_35mm'] = []
    
    if 'rolls_35mm' not in film_allocation:
        film_allocation['rolls_35mm'] = []
    
    # Step 1: Create allocation requests for all oversized documents
    # Track which documents will need to be split across rolls
    large_docs = []
    
    # Process each document with oversized pages
    for document in sorted_oversized_docs:
        # Get document details - support both naming conventions
        doc_id = document.get('docId', '') or document.get('name', '')
        doc_path = document.get('path', '')
        
        # Calculate total oversized pages and reference pages more accurately
        # First try direct oversized count fields
        total_oversized = document.get('oversizedCount', 0) or document.get('totalOversized', 0)
        
        # If no count available but we have the list of oversized pages, use its length
        if total_oversized == 0 and 'oversizedPages' in document and document['oversizedPages']:
            if isinstance(document['oversizedPages'], list):
                total_oversized = len(document['oversizedPages'])
        
        # Get reference count - typically matches the number of oversized pages
        # (one reference page per oversized page)
        total_references = document.get('referenceCount', 0) or document.get('totalReferences', 0)
        
        # If no reference count, but we know it's oversized, assume one reference per oversized
        if total_references == 0 and total_oversized > 0:
            total_references = total_oversized
            
        # Calculate total oversized pages to allocate (including reference pages)
        total_oversized_with_refs = total_oversized + total_references
        
        # Skip if no oversized pages to allocate
        if total_oversized_with_refs <= 0:
            continue
            
        print(f"Processing document {doc_id} with {total_oversized} oversized pages and {total_references} references")
        
        # If document exceeds CAPACITY_35MM, it will need to be split
        if total_oversized_with_refs > CAPACITY_35MM:
            large_docs.append({
                'doc_id': doc_id,
                'path': doc_path,
                'pages': total_oversized_with_refs,
                'has_oversized': True
            })
            print(f"Document {doc_id} exceeds 35mm roll capacity, will be handled as a large document")
            continue
        
        # Create an allocation request for regular-sized document
        film_allocation['doc_allocation_requests_35mm'].append({
            'doc_id': doc_id,
            'path': doc_path,
            'pages': total_oversized_with_refs,
            'page_range': (1, total_oversized_with_refs),
            'has_oversized': True
        })
    
    # Now handle documents that need to be split
    for document in large_docs:
        doc_id = document['doc_id']
        doc_path = document['path']
        total_oversized_with_refs = document['pages']
        
        print(f"Splitting large document {doc_id} with {total_oversized_with_refs} oversized pages")
        
        # Split document into chunks that fit on a roll
        pages_left = total_oversized_with_refs
        start_page = 1
        
        while pages_left > 0:
            # Calculate how many pages to allocate in this chunk
            pages_to_allocate = min(pages_left, CAPACITY_35MM)
            end_page = start_page + pages_to_allocate - 1
                    
            # Create allocation request for this segment
            film_allocation['doc_allocation_requests_35mm'].append({
                'doc_id': doc_id,
                'path': doc_path,
                'pages': pages_to_allocate,
                'page_range': (start_page, end_page),
                'has_oversized': True
            })
            
            print(f"Created allocation request for {doc_id} pages {start_page}-{end_page}")
            
            # Update for next iteration
            pages_left -= pages_to_allocate
            start_page = end_page + 1
    
    print(f"Created {len(film_allocation['doc_allocation_requests_35mm'])} allocation requests for 35mm film")
        
    return film_allocation

def process_35mm_allocation_requests(film_allocation):
    """
    Process 35mm allocation requests into actual film rolls.
    
    Args:
        film_allocation: Film allocation structure containing allocation requests
        
    Returns:
        Updated film allocation structure
    """
    print("Processing 35mm allocation requests into film rolls")
    
    # Initialize if not present
    if 'rolls_35mm' not in film_allocation:
        film_allocation['rolls_35mm'] = []
    
    if 'split_documents_35mm' not in film_allocation:
        film_allocation['split_documents_35mm'] = {}
    
    # Initialize tracking variables
    roll_id = 1
    current_roll = None
    split_documents = set()
    
    # Process each allocation request
    for request in film_allocation['doc_allocation_requests_35mm']:
        doc_id = request['doc_id']
        doc_path = request['path']
        pages = request['pages']
        page_range = request['page_range']
        
        # Create new roll if needed
        if current_roll is None or current_roll['pages_remaining'] < pages:
            # If there's a current roll that's not full, mark it as partial
            if current_roll is not None and current_roll['pages_remaining'] > 0:
                current_roll['is_partial'] = True
                current_roll['remaining_capacity'] = current_roll['pages_remaining']
                current_roll['usable_capacity'] = current_roll['pages_remaining'] - PADDING_35MM
                
                # Add to partial rolls list if not already there
                already_in_partial = any(pr['roll_id'] == current_roll['roll_id'] for pr in film_allocation.get('partial_rolls_35mm', []))
                if not already_in_partial:
                    if 'partial_rolls_35mm' not in film_allocation:
                        film_allocation['partial_rolls_35mm'] = []
                        
                    film_allocation['partial_rolls_35mm'].append({
                        'roll_id': current_roll['roll_id'],
                        'remainingCapacity': current_roll['remaining_capacity'],
                        'usableCapacity': current_roll['usable_capacity'],
                        'isAvailable': True,
                        'creation_date': current_roll['creation_date']
                    })
            
            # Create a new roll
            current_roll = {
                'roll_id': roll_id,
                'film_type': FilmType.FILM_35MM.value,
                'capacity': CAPACITY_35MM,
                'pages_used': 0,
                'pages_remaining': CAPACITY_35MM,
                'document_segments': [],
                'film_number': None,
                'status': 'active',
                'has_split_documents': False,
                'is_partial': False,
                'remaining_capacity': 0,
                'usable_capacity': 0,
                'creation_date': time.strftime('%Y-%m-%dT%H:%M:%S%z')
            }
            
            # Add the new roll to the film allocation
            film_allocation['rolls_35mm'].append(current_roll)
            roll_id += 1
        
        # Add segment to current roll
        add_document_segment(current_roll, doc_id, doc_path, pages, page_range, True)
        
        # Check if this is part of a split document
        # We determine this by checking if there are other requests with the same doc_id
        if sum(1 for req in film_allocation['doc_allocation_requests_35mm'] if req['doc_id'] == doc_id) > 1:
            current_roll['has_split_documents'] = True
            split_documents.add(doc_id)
    
    # Check if the last roll is a partial roll
    if film_allocation['rolls_35mm'] and film_allocation['rolls_35mm'][-1]['pages_remaining'] > 0:
        last_roll = film_allocation['rolls_35mm'][-1]
        last_roll['is_partial'] = True
        last_roll['remaining_capacity'] = last_roll['pages_remaining']
        last_roll['usable_capacity'] = last_roll['pages_remaining'] - PADDING_35MM
        
        # Only add to partial_rolls if not already there
        already_in_partial = any(pr['roll_id'] == last_roll['roll_id'] for pr in film_allocation.get('partial_rolls_35mm', []))
        if not already_in_partial:
            if 'partial_rolls_35mm' not in film_allocation:
                film_allocation['partial_rolls_35mm'] = []
                
            film_allocation['partial_rolls_35mm'].append({
                'roll_id': last_roll['roll_id'],
                'remainingCapacity': last_roll['remaining_capacity'],
                'usableCapacity': last_roll['usable_capacity'],
                'isAvailable': True,
                'creation_date': last_roll['creation_date']
            })
    
    # Add detailed information about split documents
    for doc_id in split_documents:
        film_allocation['split_documents_35mm'][doc_id] = []
        
        # Find all rolls containing this document
        for roll in film_allocation['rolls_35mm']:
            segments = [seg for seg in roll['document_segments'] if seg['doc_id'] == doc_id]
            for segment in segments:
                film_allocation['split_documents_35mm'][doc_id].append({
                    'roll': roll['roll_id'],
                    'pageRange': segment['page_range'],
                    'frameRange': segment['frame_range']
                })
    
    print(f"35mm allocation complete: Created {len(film_allocation['rolls_35mm'])} rolls")
    print(f"Total 35mm pages: {sum(roll['pages_used'] for roll in film_allocation['rolls_35mm'])}")
    print(f"Total partial 35mm rolls: {len(film_allocation.get('partial_rolls_35mm', []))}")
    print(f"Total split documents on 35mm: {len(film_allocation['split_documents_35mm'])}")
    
    # Return the updated film_allocation
    return film_allocation

def add_document_segment(roll, doc_id, path, pages, page_range, has_oversized):
    """
    Add a document segment to a roll.
    
    Args:
        roll: Roll to add the segment to
        doc_id: Document ID
        path: Path to the PDF file
        pages: Number of pages in this segment
        page_range: Range of pages from the original document (start, end)
        has_oversized: Whether this segment contains oversized pages
    """
    # Calculate next document index
    document_index = len(roll['document_segments']) + 1
    
    # Calculate frame range
    start_frame = roll['pages_used'] + 1
    end_frame = start_frame + pages - 1
    
    # Create segment
    segment = {
        'doc_id': doc_id,
        'path': path,
        'pages': pages,
        'page_range': page_range,
        'frame_range': (start_frame, end_frame),
        'document_index': document_index,
        'has_oversized': has_oversized
    }
    
    # Update roll statistics
    roll['pages_used'] += pages
    roll['pages_remaining'] -= pages
    
    # Add segment to roll
    roll['document_segments'].append(segment)

def update_statistics(film_allocation):
    """
    Update all statistics for film allocation.
    
    Args:
        film_allocation: Film allocation structure to update
        
    Returns:
        Updated film allocation structure
    """
    # Update 16mm statistics
    film_allocation['total_rolls_16mm'] = len(film_allocation['rolls_16mm'])
    film_allocation['total_pages_16mm'] = sum(roll['pages_used'] for roll in film_allocation['rolls_16mm'])
    film_allocation['total_partial_rolls_16mm'] = len(film_allocation['partial_rolls_16mm'])
    film_allocation['total_split_documents_16mm'] = len(film_allocation['split_documents_16mm'])
    
    # Calculate average utilization for 16mm rolls (percentage of capacity used)
    if film_allocation['total_rolls_16mm'] > 0:
        total_utilization_16mm = sum((roll['pages_used'] / CAPACITY_16MM) * 100 for roll in film_allocation['rolls_16mm'])
        film_allocation['avg_utilization_16mm'] = round(total_utilization_16mm / film_allocation['total_rolls_16mm'])
    else:
        film_allocation['avg_utilization_16mm'] = 0
    
    # Update 35mm statistics
    film_allocation['total_rolls_35mm'] = len(film_allocation['rolls_35mm'])
    film_allocation['total_pages_35mm'] = sum(roll['pages_used'] for roll in film_allocation['rolls_35mm'])
    film_allocation['total_partial_rolls_35mm'] = len(film_allocation['partial_rolls_35mm'])
    film_allocation['total_split_documents_35mm'] = len(film_allocation['split_documents_35mm'])
    
    # Calculate average utilization for 35mm rolls (percentage of capacity used)
    if film_allocation['total_rolls_35mm'] > 0:
        total_utilization_35mm = sum((roll['pages_used'] / CAPACITY_35MM) * 100 for roll in film_allocation['rolls_35mm'])
        film_allocation['avg_utilization_35mm'] = round(total_utilization_35mm / film_allocation['total_rolls_35mm'])
    else:
        film_allocation['avg_utilization_35mm'] = 0
    
    # Also handle the 35mm allocation requests if no actual rolls exist yet
    if film_allocation['total_rolls_35mm'] == 0 and 'doc_allocation_requests_35mm' in film_allocation:
        # Calculate total pages for 35mm from allocation requests
        request_pages = sum(req.get('pages', 0) for req in film_allocation.get('doc_allocation_requests_35mm', []))
        if request_pages > 0:
            film_allocation['total_pages_35mm'] = request_pages
            # Estimate number of rolls needed
            estimated_rolls = (request_pages + CAPACITY_35MM - 1) // CAPACITY_35MM  # Ceiling division
            if estimated_rolls > 0:
                film_allocation['total_rolls_35mm'] = estimated_rolls
                # Estimate utilization
                avg_utilization = (request_pages / (estimated_rolls * CAPACITY_35MM)) * 100
                film_allocation['avg_utilization_35mm'] = round(avg_utilization)
    
    return film_allocation