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
    
    Args:
        projectId: Project ID (JSON parameter)
        projectData: Project data (JSON parameter)
        analysisData: Document analysis data (JSON parameter)
        allocationData: Film allocation data (JSON parameter)
        indexData: Index data for updating (JSON parameter)
        
    Returns:
        JSON response with task ID and status
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
                print(project_id)
            except Project.DoesNotExist:
                return JsonResponse({
                    'error': 'Project not found'
                }, status=404)
                
            # Create a unique ID for this allocation task
            task_id = str(uuid.uuid4())
            
            # Initialize allocation task status
            filmnumber_tasks[task_id] = {
                'status': 'pending',
                'projectId': project_id,
                'progress': 0,
                'hasOversized': project_db.has_oversized,
                'results': None,
                'errors': [],
                'startTime': time.time(),
                'lastUpdateTime': time.time()
            }
            
            # Start a background thread to process the allocation
            allocation_thread = threading.Thread(
                target=process_film_number_allocation, 
                args=(task_id, project_id, project_data, analysis_data, allocation_data, index_data)
            )
            allocation_thread.daemon = True
            allocation_thread.start()
            
            return JsonResponse({
                'taskId': task_id,
                'status': 'started',
                'message': 'Film number allocation started successfully'
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
    
    Args:
        task_id: Task ID for tracking progress
        project_id: Project ID to allocate film numbers for
        project_data: Project data
        analysis_data: Document analysis data
        allocation_data: Film allocation data
        index_data: Optional index data to update
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
        
        # Update progress
        task['progress'] = 90
        task['lastUpdateTime'] = time.time()
        
        # Get allocation statistics
        from microapp.models import Roll
        allocation_stats = {
            "project_id": project.pk,
            "archive_id": project.archive_id,
            "film_allocation_complete": project.film_allocation_complete,
            "rolls_allocated": Roll.objects.filter(
                project=project,
                film_number__isnull=False
            ).count(),
            "total_rolls": Roll.objects.filter(project=project).count()
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
        
    except Exception as e:
        logger.error(f"Error in film number allocation: {str(e)}")
        task['status'] = 'error'
        task['errors'].append(str(e))
        task['lastUpdateTime'] = time.time()
