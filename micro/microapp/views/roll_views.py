"""
Views for roll management and filming operations.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from pathlib import Path

from ..models import Project, Roll, DocumentSegment, TempRoll

logger = logging.getLogger(__name__)

def get_temp_roll_instructions(roll):
    """
    Generate instructions for temp roll usage based on the roll's source.
    """
    if roll.film_number_source == 'temp_roll' and roll.source_temp_roll:
        temp_roll = roll.source_temp_roll
        return {
            'use_temp_roll': True,
            'temp_roll_id': temp_roll.temp_roll_id,
            'instruction': f"Use existing temp roll #{temp_roll.temp_roll_id} ({temp_roll.film_type})",
            'details': f"Remaining capacity: {temp_roll.usable_capacity} pages"
        }
    else:
        return {
            'use_temp_roll': False,
            'temp_roll_id': None,
            'instruction': f"Insert new {roll.film_type} film roll",
            'details': f"New roll with {roll.capacity} pages capacity"
        }

@require_http_methods(["GET"])
def get_project_rolls(request, project_id):
    """
    Get all rolls for a specific project.
    
    Returns roll information including filming status, output directory,
    and document counts.
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # Get all rolls for the project
        rolls = Roll.objects.filter(project=project).order_by('film_type', 'roll_id')
        
        roll_data = []
        for roll in rolls:
            # Count documents in this roll
            document_count = DocumentSegment.objects.filter(roll=roll).count()
            
            # Check if output directory exists
            output_dir_exists = roll.output_directory_exists if roll.output_directory else False
            
            # Determine roll status for filming
            if roll.filming_status == 'completed':
                status = 'completed'
            elif roll.filming_status == 'filming':
                status = 'filming'
            elif roll.output_directory and output_dir_exists and document_count > 0:
                status = 'ready'
            else:
                status = 'not_ready'
            
            roll_info = {
                'id': roll.id,
                'roll_id': roll.roll_id,
                'film_number': roll.film_number,
                'film_type': roll.film_type,
                'capacity': roll.capacity,
                'pages_used': roll.pages_used,
                'pages_remaining': roll.pages_remaining,
                'document_count': document_count,
                'output_directory': roll.output_directory,
                'output_directory_exists': output_dir_exists,
                'filming_status': roll.filming_status,
                'filming_progress_percent': roll.filming_progress_percent,
                'filming_started_at': roll.filming_started_at.isoformat() if roll.filming_started_at else None,
                'filming_completed_at': roll.filming_completed_at.isoformat() if roll.filming_completed_at else None,
                'status': status,
                'utilization': roll.utilization,
                'is_partial': roll.is_partial,
                'has_split_documents': roll.has_split_documents,
                'film_number_source': roll.film_number_source,
                'source_temp_roll': {
                    'id': roll.source_temp_roll.temp_roll_id,
                    'capacity': roll.source_temp_roll.capacity,
                    'usable_capacity': roll.source_temp_roll.usable_capacity,
                    'film_type': roll.source_temp_roll.film_type
                } if roll.source_temp_roll else None,
                'is_new_roll': roll.film_number_source != 'temp_roll',
                'temp_roll_instructions': get_temp_roll_instructions(roll)
            }
            roll_data.append(roll_info)
        
        return JsonResponse({
            'status': 'success',
            'project': {
                'id': project.id,
                'archive_id': project.archive_id,
                'project_folder_name': project.project_folder_name,
                'location': project.location
            },
            'rolls': roll_data,
            'total_rolls': len(roll_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting rolls for project {project_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to get project rolls: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_roll_filming_status(request, roll_id):
    """
    Update the filming status of a roll.
    
    Expected JSON payload:
    {
        "status": "filming|completed|error|ready",
        "session_id": "optional_session_id",
        "progress_percent": 0-100,
        "error_message": "optional_error_message"
    }
    """
    try:
        data = json.loads(request.body)
        roll = get_object_or_404(Roll, pk=roll_id)
        
        status = data.get('status')
        session_id = data.get('session_id')
        progress_percent = data.get('progress_percent', 0)
        
        if status not in ['ready', 'filming', 'completed', 'error']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status. Must be one of: ready, filming, completed, error'
            }, status=400)
        
        with transaction.atomic():
            # Update roll status
            roll.filming_status = status
            roll.filming_progress_percent = progress_percent
            
            if session_id:
                roll.filming_session_id = session_id
            
            # Set timestamps based on status
            if status == 'filming' and not roll.filming_started_at:
                roll.filming_started_at = timezone.now()
            elif status == 'completed':
                roll.filming_completed_at = timezone.now()
                roll.filming_progress_percent = 100.0
            elif status == 'ready':
                # Reset filming timestamps if going back to ready
                roll.filming_started_at = None
                roll.filming_completed_at = None
                roll.filming_progress_percent = 0.0
                roll.filming_session_id = None
            
            roll.save()
        
        logger.info(f"Updated roll {roll.film_number} status to {status}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Roll status updated to {status}',
            'roll': {
                'id': roll.id,
                'film_number': roll.film_number,
                'filming_status': roll.filming_status,
                'filming_progress_percent': roll.filming_progress_percent,
                'filming_started_at': roll.filming_started_at.isoformat() if roll.filming_started_at else None,
                'filming_completed_at': roll.filming_completed_at.isoformat() if roll.filming_completed_at else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating roll {roll_id} filming status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to update roll status: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_roll_details(request, roll_id):
    """
    Get detailed information about a specific roll including documents.
    """
    try:
        roll = get_object_or_404(Roll, pk=roll_id)
        
        # Get document segments for this roll
        segments = DocumentSegment.objects.filter(roll=roll).select_related('document').order_by('document_index')
        
        documents = []
        for segment in segments:
            doc_info = {
                'document_id': segment.document.id,
                'doc_id': segment.document.doc_id,
                'pages': segment.pages,
                'start_page': segment.start_page,
                'end_page': segment.end_page,
                'start_frame': segment.start_frame,
                'end_frame': segment.end_frame,
                'document_index': segment.document_index,
                'has_oversized': segment.has_oversized,
                'blip': segment.blip,
                'blipend': segment.blipend
            }
            documents.append(doc_info)
        
        # Check output directory
        output_dir_exists = roll.output_directory_exists if roll.output_directory else False
        output_dir_file_count = 0
        
        if output_dir_exists:
            try:
                output_path = Path(roll.output_directory)
                output_dir_file_count = len([f for f in output_path.iterdir() if f.is_file()])
            except Exception as e:
                logger.warning(f"Could not count files in {roll.output_directory}: {str(e)}")
        
        roll_details = {
            'id': roll.id,
            'roll_id': roll.roll_id,
            'film_number': roll.film_number,
            'film_type': roll.film_type,
            'capacity': roll.capacity,
            'pages_used': roll.pages_used,
            'pages_remaining': roll.pages_remaining,
            'status': roll.status,
            'output_directory': roll.output_directory,
            'output_directory_exists': output_dir_exists,
            'output_directory_file_count': output_dir_file_count,
            'filming_status': roll.filming_status,
            'filming_session_id': roll.filming_session_id,
            'filming_progress_percent': roll.filming_progress_percent,
            'filming_started_at': roll.filming_started_at.isoformat() if roll.filming_started_at else None,
            'filming_completed_at': roll.filming_completed_at.isoformat() if roll.filming_completed_at else None,
            'utilization': roll.utilization,
            'is_partial': roll.is_partial,
            'has_split_documents': roll.has_split_documents,
            'documents': documents,
            'document_count': len(documents),
            'project': {
                'id': roll.project.id,
                'archive_id': roll.project.archive_id,
                'project_folder_name': roll.project.project_folder_name
            },
            'temp_roll_info': {
                'created_temp_roll': {
                    'temp_roll_id': roll.created_temp_roll.temp_roll_id,
                    'film_type': roll.created_temp_roll.film_type,
                    'capacity': roll.created_temp_roll.capacity,
                    'usable_capacity': roll.created_temp_roll.usable_capacity,
                    'status': roll.created_temp_roll.status,
                    'creation_date': roll.created_temp_roll.creation_date.isoformat() if roll.created_temp_roll.creation_date else None
                } if roll.created_temp_roll else None,
                'source_temp_roll': {
                    'temp_roll_id': roll.source_temp_roll.temp_roll_id,
                    'film_type': roll.source_temp_roll.film_type,
                    'capacity': roll.source_temp_roll.capacity,
                    'usable_capacity': roll.source_temp_roll.usable_capacity,
                    'status': roll.source_temp_roll.status
                } if roll.source_temp_roll else None,
                'reason': _get_temp_roll_reason(roll)
            }
        }
        
        return JsonResponse({
            'success': True,
            'roll': roll_details
        })
        
    except Exception as e:
        logger.error(f"Error getting roll details for {roll_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to get roll details: {str(e)}'
        }, status=500)

def _get_temp_roll_reason(roll):
    """Get the reason why a temp roll was or wasn't created."""
    if roll.created_temp_roll:
        return f"Temp roll created with {roll.created_temp_roll.usable_capacity} pages remaining capacity"
    elif roll.pages_remaining <= 100:  # Less than 100 pages remaining
        return "Roll nearly full - insufficient capacity for temp roll creation"
    elif roll.pages_remaining <= 200:  # Less than 200 pages remaining
        return "Roll has minimal remaining capacity - no temp roll needed"
    else:
        return "Roll completed without creating temp roll" 