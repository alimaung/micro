"""
Film Number views for the microapp.
These views handle film number allocation, processing, and management.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings

import json
import os
import time
import uuid
import threading
from pathlib import Path
import logging

from microapp.models import (
    Project, Roll, Document, FilmAllocation,
    DocumentSegment, DocumentReferenceInfo, RangeReferenceInfo
)
from microapp.services import (
    FilmNumberManager, 
    RollManager, 
    ProjectManager,
    DocumentManager
)

# Dictionary to store film number allocation tasks and their progress
filmnumber_tasks = {}

logger = logging.getLogger(__name__)

# Constants
DEFAULT_PAGE_SIZE = 20  # Default number of items per page for pagination

@login_required
def film_number_view(request, project_id=None):
    """
    Main view for film number allocation interface.
    
    Args:
        request: HTTP request
        project_id: Optional project ID to pre-load (default: None)
        
    Returns:
        Rendered HTML response
    """
    # Initialize context
    context = {
        'page_title': 'Film Number Allocation',
        'active_tab': 'filmnumber',
        'projects': [],
        'selected_project': None,
        'allocation_summary': None,
        'roll_summary': None,
        'has_oversized': False,
        'has_temp_rolls': False,
        'allocation_complete': False
    }
    
    # Get all projects with status in progress or film_numbers_allocated
    project_manager = ProjectManager()
    projects = Project.objects.filter(
        status__in=['in_progress', 'film_numbers_allocated']
    ).order_by('-creation_date')
    
    # Format projects for display
    context['projects'] = [{
        'id': project.pk,
        'archive_id': project.archive_id,
        'name': project.name,
        'location': project.location,
        'status': project.status,
        'has_oversized': project.has_oversized,
        'creation_date': project.creation_date.isoformat() if project.creation_date else None,
    } for project in projects]
    
    # If project_id is provided, load that project's data
    if project_id:
        try:
            project = Project.objects.get(pk=project_id)
            context['selected_project'] = {
                'id': project.pk,
                'archive_id': project.archive_id,
                'name': project.name,
                'location': project.location,
                'status': project.status,
                'has_oversized': project.has_oversized,
                'creation_date': project.creation_date.isoformat() if project.creation_date else None,
            }
            
            # Get allocation summary
            try:
                film_allocation = FilmAllocation.objects.get(project=project)
                context['allocation_summary'] = {
                    'total_rolls': film_allocation.total_rolls,
                    'total_rolls_16mm': film_allocation.total_rolls_16mm,
                    'total_rolls_35mm': film_allocation.total_rolls_35mm,
                }
                
                # Get roll summary
                rolls_16mm = Roll.objects.filter(project=project, film_type='16mm').count()
                rolls_35mm = Roll.objects.filter(project=project, film_type='35mm').count()
                rolls_allocated = Roll.objects.filter(project=project, film_number__isnull=False).count()
                rolls_unallocated = Roll.objects.filter(project=project, film_number__isnull=True).count()
                
                context['roll_summary'] = {
                    'rolls_16mm': rolls_16mm,
                    'rolls_35mm': rolls_35mm,
                    'rolls_allocated': rolls_allocated,
                    'rolls_unallocated': rolls_unallocated,
                    'allocation_percentage': (rolls_allocated / film_allocation.total_rolls * 100) if film_allocation.total_rolls > 0 else 0
                }
                
                # Check if there are temp rolls
                from microapp.models import TempRoll
                context['has_temp_rolls'] = TempRoll.objects.filter(status='available').exists()
                
                # Check allocation status
                context['allocation_complete'] = project.film_allocation_complete
                context['has_oversized'] = project.has_oversized
                
            except FilmAllocation.DoesNotExist:
                # No allocation exists yet
                pass
                
        except Project.DoesNotExist:
            # Project not found, don't set selected_project
            pass
    
    # Render the template
    return render(request, 'microapp/filmnumber.html', context)

@login_required
def roll_detail_view(request, roll_id):
    """
    View for showing detailed information about a roll.
    
    Args:
        request: HTTP request
        roll_id: ID of the roll to view
        
    Returns:
        Rendered HTML response
    """
    # Get the roll
    roll = get_object_or_404(Roll, pk=roll_id)
    
    # Get document segments for this roll
    document_segments = DocumentSegment.objects.filter(roll=roll).order_by('document_index')
    
    # Get reference info for this roll
    roll_reference = None
    try:
        from microapp.models import RollReferenceInfo
        roll_reference = RollReferenceInfo.objects.get(roll=roll)
    except RollReferenceInfo.DoesNotExist:
        pass
    
    # Build context
    context = {
        'page_title': f'Roll {roll.film_number or roll.roll_id} Details',
        'active_tab': 'filmnumber',
        'roll': {
            'id': roll.pk,
            'roll_id': roll.roll_id,
            'film_number': roll.film_number,
            'film_type': roll.film_type,
            'capacity': roll.capacity,
            'pages_used': roll.pages_used,
            'pages_remaining': roll.pages_remaining,
            'status': roll.status,
            'is_full': roll.is_full,
            'is_partial': roll.is_partial,
            'creation_date': roll.creation_date.isoformat() if roll.creation_date else None,
            'project_id': roll.project_id,
            'archive_id': roll.project.archive_id if roll.project else None,
        },
        'document_segments': [],
        'roll_reference': None,
        'created_temp_roll': None,
        'source_temp_roll': None
    }
    
    # Add document segments to context
    for segment in document_segments:
        segment_data = {
            'id': segment.pk,
            'document_id': segment.document_id,
            'doc_id': segment.document.doc_id,
            'pages': segment.pages,
            'start_page': segment.start_page,
            'end_page': segment.end_page,
            'document_index': segment.document_index,
            'start_frame': segment.start_frame,
            'end_frame': segment.end_frame,
            'blip': segment.blip,
            'blipend': segment.blipend,
            'has_oversized': segment.has_oversized
        }
        context['document_segments'].append(segment_data)
    
    # Add roll reference info if exists
    if roll_reference:
        context['roll_reference'] = {
            'id': roll_reference.pk,
            'is_new_roll': roll_reference.is_new_roll,
            'last_frame_position': roll_reference.last_frame_position,
            'last_blipend': roll_reference.last_blipend
        }
    
    # Add created temp roll if exists
    if roll.created_temp_roll:
        context['created_temp_roll'] = {
            'id': roll.created_temp_roll.pk,
            'capacity': roll.created_temp_roll.capacity,
            'usable_capacity': roll.created_temp_roll.usable_capacity,
            'status': roll.created_temp_roll.status
        }
    
    # Add source temp roll if exists
    if roll.source_temp_roll:
        context['source_temp_roll'] = {
            'id': roll.source_temp_roll.pk,
            'capacity': roll.source_temp_roll.capacity,
            'usable_capacity': roll.source_temp_roll.usable_capacity,
            'status': roll.source_temp_roll.status
        }
    
    # Render the template
    return render(request, 'microapp/roll_detail.html', context)

@login_required
def results_view(request, project_id):
    """
    View for showing film number allocation results.
    
    Args:
        request: HTTP request
        project_id: ID of the project to view results for
        
    Returns:
        Rendered HTML response
    """
    # Get the project
    project = get_object_or_404(Project, pk=project_id)
    
    # Ensure project has film allocation complete
    if not project.film_allocation_complete:
        return redirect(reverse('register_filmnumber'))
    
    # Get project manager to load stats
    project_manager = ProjectManager()
    project_stats = project_manager.get_project_stats(project_id)
    
    # Get allocation data for export
    allocation_data = project_manager.export_allocation_data(project_id, include_documents=False)
    
    # Get rolls for this project
    rolls_16mm = Roll.objects.filter(project=project, film_type='16mm').order_by('film_number')
    rolls_35mm = Roll.objects.filter(project=project, film_type='35mm').order_by('film_number')
    
    # Paginate rolls
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    rolls_per_page = int(request.GET.get('per_page', DEFAULT_PAGE_SIZE))
    
    # Get selected film type
    film_type = request.GET.get('film_type', 'all')
    
    # Filter rolls by film type
    if film_type == '16mm':
        rolls_to_display = rolls_16mm
    elif film_type == '35mm':
        rolls_to_display = rolls_35mm
    else:
        # Display all, sorted by film type then film number
        rolls_to_display = list(rolls_16mm) + list(rolls_35mm)
    
    # Calculate pagination
    start_idx = (page - 1) * rolls_per_page
    end_idx = start_idx + rolls_per_page
    
    total_rolls = len(rolls_to_display)
    total_pages = (total_rolls + rolls_per_page - 1) // rolls_per_page
    
    paginated_rolls = rolls_to_display[start_idx:end_idx]
    
    # Get the original roll mappings from allocation data
    # Handle different data structures: direct data, wrapped in allocationResults, or nested in allocationResults.results
    original_roll_mappings = {}
    allocation_results = allocation_data
    if 'allocationResults' in allocation_data:
        alloc_results = allocation_data['allocationResults']
        if 'results' in alloc_results:
            allocation_results = alloc_results['results']
        else:
            allocation_results = alloc_results
    
    # Additional check: if allocation_results still doesn't have rolls_16mm but has 'results' key, go deeper
    if 'rolls_16mm' not in allocation_results and 'results' in allocation_results:
        logger.info("Allocation results doesn't have rolls_16mm directly, checking nested results")
        allocation_results = allocation_results['results']

    # Map 16mm rolls
    for roll in allocation_results['rolls_16mm']:
        original_roll_mappings[str(roll['roll_id'])] = {
            'film_type': '16mm',
            'original_roll_id': roll['roll_id']
        }

    # Map 35mm rolls if they exist
    if 'rolls_35mm' in allocation_results:
        for roll in allocation_results['rolls_35mm']:
            original_roll_mappings[str(roll['roll_id'])] = {
                'film_type': '35mm',
                'original_roll_id': roll['roll_id']
            }

    logger.info(f"Original roll mappings: {original_roll_mappings}")

    # Format rolls for display
    formatted_rolls = []
    for roll in paginated_rolls:
        roll_data = {
            'id': roll.pk,
            'roll_id': roll.roll_id,
            'film_number': roll.film_number,
            'film_type': roll.film_type,
            'capacity': roll.capacity,
            'pages_used': roll.pages_used,
            'pages_remaining': roll.pages_remaining,
            'status': roll.status,
            'is_full': roll.is_full,
            'is_partial': roll.is_partial,
            'document_count': DocumentSegment.objects.filter(roll=roll).count()
        }
        formatted_rolls.append(roll_data)
    
    # Build context
    context = {
        'page_title': 'Film Number Allocation Results',
        'active_tab': 'filmnumber',
        'project': {
            'id': project.pk,
            'archive_id': project.archive_id,
            'name': project.name,
            'location': project.location,
            'status': project.status,
            'has_oversized': project.has_oversized,
            'creation_date': project.creation_date.isoformat() if project.creation_date else None,
        },
        'stats': project_stats,
        'rolls': formatted_rolls,
        'total_rolls': total_rolls,
        'total_pages': total_pages,
        'current_page': page,
        'film_type': film_type,
        'per_page': rolls_per_page,
        'allocation_summary': allocation_data.get('allocation_info', {})
    }
    
    # Add pagination links
    if page > 1:
        context['prev_page'] = page - 1
    
    if page < total_pages:
        context['next_page'] = page + 1
    
    # Render the template
    return render(request, 'microapp/film_allocation_results.html', context)

@csrf_exempt
def start_film_number_allocation(request):
    """
    API endpoint to start film number allocation for a project.
    """
    if request.method == 'POST':
        print("Starting film number allocation")
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            project_data = data.get('projectData')
            analysis_data = data.get('analysisData')
            allocation_data = data.get('allocationData')
            index_data = data.get('indexData')
            
            # Validate inputs
            if not project_id:
                return JsonResponse({
                    'error': 'Project ID is required'
                }, status=400)
            
            if not project_data or not allocation_data:
                return JsonResponse({
                    'error': 'Project data and allocation data are required'
                }, status=400)
            
            # Get basic project info from database for verification
            try:
                project_db = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return JsonResponse({
                    'error': 'Project not found'
                }, status=404)
                
            # Create a unique ID for this allocation task
            task_id = str(uuid.uuid4())
            
            # Initialize allocation task status
            filmnumber_tasks[task_id] = {
                'status': 'processing',
                'projectId': project_id,
                'progress': 0,
                'hasOversized': project_db.has_oversized,
                'results': None,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Process the allocation directly instead of in a thread
            process_film_number_allocation(task_id, project_id, project_data, analysis_data, allocation_data, index_data)
            
            # Return the task ID - the client can still poll for status
            return JsonResponse({
                'taskId': task_id,
                'status': 'completed',  # Since we're processing synchronously now
                'message': 'Film number allocation completed'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error starting film number allocation: {str(e)}")
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def get_film_number_status(request):
    """
    API endpoint to get the status of a film number allocation task.
    
    Args:
        taskId: Task ID (GET parameter)
        
    Returns:
        JSON response with the task status
    """
    if request.method == 'GET':
        try:
            task_id = request.GET.get('taskId')
            
            if not task_id or task_id not in filmnumber_tasks:
                return JsonResponse({
                    'error': 'Invalid or unknown task ID'
                }, status=404)
                
            # Get the allocation task status
            task_status = filmnumber_tasks[task_id]
            
            # Clean up completed tasks after some time
            if task_status['status'] in ['completed', 'error', 'cancelled']:
                # If the task has been in a final state for more than 30 minutes, clean it up
                if time.time() - task_status['lastUpdateTime'] > 1800:
                    # Before deleting, return the status one last time
                    status_copy = task_status.copy()
                    del filmnumber_tasks[task_id]
                    return JsonResponse(status_copy)
            
            return JsonResponse(task_status)
            
        except Exception as e:
            logger.error(f"Error getting film number status: {str(e)}")
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=400)

def process_film_number_allocation(task_id, project_id, project_data, analysis_data, allocation_data, index_data=None):
    """
    Background thread function to process film number allocation.
    """
    task = filmnumber_tasks[task_id]
    task['status'] = 'processing'
    task['progress'] = 5
    task['lastUpdateTime'] = time.time()
    
    try:
        # Create film number manager
        film_number_manager = FilmNumberManager(logger=logger)
        
        # Update progress
        task['progress'] = 10
        task['lastUpdateTime'] = time.time()
        
        # Call allocate_film_numbers on the manager with all the necessary data
        project, updated_index = film_number_manager.allocate_film_numbers(
            project_id=project_id,
            project_data=project_data,
            analysis_data=analysis_data,
            allocation_data=allocation_data,
            index_data=index_data
        )
        #logger.info(f"\033[34mAllocation data: {allocation_data}\033[0m")
        # Update progress
        task['progress'] = 90
        task['lastUpdateTime'] = time.time()
        
        # Get all rolls with film numbers for this project
        rolls_16mm = Roll.objects.filter(
            project=project,
            film_type='16mm',
            film_number__isnull=False
        ).order_by('film_number')

        rolls_35mm = Roll.objects.filter(
            film_type='35mm',
            film_number__isnull=False
        ).order_by('film_number')

        # Format roll data
        formatted_rolls_16mm = []
        formatted_rolls_35mm = []

        # Get the original roll mappings from allocation data
        # Handle different data structures: direct data, wrapped in allocationResults, or nested in allocationResults.results
        original_roll_mappings = {}
        allocation_results = allocation_data
        if 'allocationResults' in allocation_data:
            alloc_results = allocation_data['allocationResults']
            if 'results' in alloc_results:
                allocation_results = alloc_results['results']
            else:
                allocation_results = alloc_results
        
        # Additional check: if allocation_results still doesn't have rolls_16mm but has 'results' key, go deeper
        if 'rolls_16mm' not in allocation_results and 'results' in allocation_results:
            logger.info("Allocation results doesn't have rolls_16mm directly, checking nested results")
            allocation_results = allocation_results['results']
        
        logger.info(f"Using allocation results structure with keys: {list(allocation_results.keys()) if isinstance(allocation_results, dict) else 'Not a dict'}")

        # Map 16mm rolls
        for roll in allocation_results['rolls_16mm']:
            original_roll_mappings[str(roll['roll_id'])] = {
                'film_type': '16mm',
                'original_roll_id': roll['roll_id']
            }

        # Map 35mm rolls if they exist
        if 'rolls_35mm' in allocation_results:
            for roll in allocation_results['rolls_35mm']:
                original_roll_mappings[str(roll['roll_id'])] = {
                    'film_type': '35mm',
                    'original_roll_id': roll['roll_id']
                }

        logger.info(f"Original roll mappings: {original_roll_mappings}")

        # Format 16mm rolls
        for roll in rolls_16mm:
            segments = DocumentSegment.objects.filter(roll=roll).order_by('document_index')
            formatted_segments = []
            
            # Find the original roll_id from the segments
            first_segment = segments.first()
            original_roll_id = None
            if first_segment:
                # Look through segments to find matching document in allocation data
                for roll_data in allocation_results['rolls_16mm']:
                    for seg in roll_data['document_segments']:
                        if seg['doc_id'] == first_segment.document.doc_id:
                            original_roll_id = roll_data['roll_id']
                            break
                    if original_roll_id:
                        break
            
            for segment in segments:
                formatted_segments.append({
                    'doc_id': segment.document.doc_id,
                    'document_id': segment.document.doc_id,  # For compatibility
                    'pages': segment.pages,
                    'start_page': segment.start_page,
                    'end_page': segment.end_page,
                    'blip': segment.blip,
                    'blipend': segment.blipend
                })

            # Add temp roll information
            temp_roll_info = {}
            capacity_breakdown = {
                'used': roll.pages_used,
                'total': roll.capacity,
                'remaining': roll.pages_remaining
            }
            
            if roll.source_temp_roll:
                temp_roll_info['source_temp_roll'] = {
                    'id': roll.source_temp_roll.pk,
                    'capacity': roll.source_temp_roll.capacity,
                    'usable_capacity': roll.source_temp_roll.usable_capacity,
                    'status': roll.source_temp_roll.status
                }
                # For USE case: used pages (green), remaining usable (blue)
                capacity_breakdown['temp_type'] = 'used'
                capacity_breakdown['temp_remaining'] = roll.pages_remaining
            
            if roll.created_temp_roll:
                temp_roll_info['created_temp_roll'] = {
                    'id': roll.created_temp_roll.pk,
                    'capacity': roll.created_temp_roll.capacity,
                    'usable_capacity': roll.created_temp_roll.usable_capacity,
                    'status': roll.created_temp_roll.status
                }
                # For CREATE case: used pages (green), temp roll capacity (yellow)
                capacity_breakdown['temp_type'] = 'created'
                capacity_breakdown['temp_capacity'] = roll.created_temp_roll.capacity
            
            # Check for UNWIND case (unusable leftover space)
            has_unwind = False
            if roll.is_partial and roll.pages_remaining > 0 and not roll.created_temp_roll:
                # Calculate if there would be unusable space
                from microapp.services.film_number_manager import TEMP_ROLL_PADDING_16MM, TEMP_ROLL_PADDING_35MM, TEMP_ROLL_MIN_USABLE_PAGES
                
                padding = TEMP_ROLL_PADDING_16MM if roll.film_type == 'film_16mm' else TEMP_ROLL_PADDING_35MM
                usable_remainder = roll.pages_remaining - padding
                
                if roll.pages_remaining > 0 and usable_remainder < TEMP_ROLL_MIN_USABLE_PAGES:
                    has_unwind = True
                    temp_roll_info['has_unwind'] = True
                    temp_roll_info['unwind_capacity'] = roll.pages_remaining
                    # For UNWIND case: used pages (green), unusable remainder (red)
                    capacity_breakdown['temp_type'] = 'unwind'
                    capacity_breakdown['unwind_capacity'] = roll.pages_remaining

            formatted_rolls_16mm.append({
                'roll_id': original_roll_id,  # Use the found original roll_id
                'film_number': roll.film_number,
                'capacity': roll.capacity,
                'pages_used': roll.pages_used,
                'pages_remaining': roll.pages_remaining,
                'film_number_source': roll.film_number_source,  # "temp_roll" or "new"
                'is_partial': roll.is_partial,
                'temp_roll_info': temp_roll_info,
                'capacity_breakdown': capacity_breakdown,
                'document_segments': formatted_segments
            })
            

        # Format 35mm rolls
        formatted_rolls_35mm = []
        for roll in rolls_35mm:
            # Check if this roll has any segments for the current project
            has_segments_for_project = DocumentSegment.objects.filter(
                roll=roll,
                document__project=project
            ).exists()
            
            # Skip rolls that don't have segments for this project
            if not has_segments_for_project:
                continue
            
            segments = DocumentSegment.objects.filter(
                roll=roll,
                document__project=project
            ).order_by('document_index')
            
            # Find the original roll_id from the segments by matching documents in allocation data
            # Similar to how it's done for 16mm rolls
            first_segment = segments.first()
            original_roll_id = None
            
            if first_segment:
                # Look through segments to find matching document in allocation data for 35mm
                if 'rolls_35mm' in allocation_results:
                    for roll_data in allocation_results['rolls_35mm']:
                        for seg in roll_data.get('document_segments', []):
                            if seg.get('doc_id') == first_segment.document.doc_id:
                                original_roll_id = roll_data.get('roll_id')
                                break
                        if original_roll_id:
                            break
                
                # If not found in 35mm rolls, check doc_allocation_requests_35mm
                if not original_roll_id and 'doc_allocation_requests_35mm' in allocation_results:
                    # For 35mm allocation requests, try to use doc_id to infer the original roll
                    for i, req in enumerate(allocation_results['doc_allocation_requests_35mm']):
                        if req.get('doc_id') == first_segment.document.doc_id:
                            # Use index + 1 as a roll ID if nothing else is available
                            original_roll_id = i + 1
                            break
            
            # If we still don't have an original_roll_id, use a safe default
            if original_roll_id is None:
                # Use roll_id from the database if it's not None, otherwise default to 1
                original_roll_id = roll.roll_id if roll.roll_id is not None else 1
            
            formatted_segments = []
            for segment in segments:
                formatted_segments.append({
                    'doc_id': segment.document.doc_id,
                    'document_id': segment.document.doc_id,  # For compatibility
                    'pages': segment.pages,
                    'start_page': segment.start_page,
                    'end_page': segment.end_page,
                    'blip': segment.blip,
                    'blipend': segment.blipend
                })

            formatted_rolls_35mm.append({
                'roll_id': original_roll_id,  # Use the found original roll_id, consistent with 16mm approach
                'film_number': roll.film_number,
                'capacity': roll.capacity,
                'pages_used': roll.pages_used,
                'pages_remaining': roll.pages_remaining,
                'document_segments': formatted_segments
            })

        # Create complete response data
        allocation_stats = {
            "project_id": project.pk,
            "archive_id": project.archive_id,
            "film_allocation_complete": project.film_allocation_complete,
            "total_rolls_16mm": rolls_16mm.count(),
            "total_rolls_35mm": rolls_35mm.count(),
            "total_pages_16mm": sum(r.pages_used for r in rolls_16mm),
            "total_pages_35mm": sum(r.pages_used for r in rolls_35mm),
            "rolls_16mm": formatted_rolls_16mm,
            "rolls_35mm": formatted_rolls_35mm
        }
        
        # Include updated index if provided
        if updated_index:
            allocation_stats["index_updated"] = True
            allocation_stats["index_data"] = updated_index
        
        # Update task with results
        task['status'] = 'completed'
        task['progress'] = 100
        task['results'] = allocation_stats
        task['lastUpdateTime'] = time.time()
        
        # Film number allocation completion is already logged by FilmNumberManager
        # logger.info(f"Film number allocation completed successfully for project {project.archive_id}")
        
    except Exception as e:
        logger.error(f"Error in film number allocation: {str(e)}")
        task['status'] = 'error'
        task['errors'].append(str(e))
        task['lastUpdateTime'] = time.time()
