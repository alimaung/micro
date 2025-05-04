"""
API endpoints for microfilm processing services.

This module provides REST API endpoints for interacting with
microfilm processing services.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from microapp.services import (
    FilmNumberManager,
    RollManager,
    ProjectManager,
    DocumentManager,
)
from microapp.models import Project, Document, Roll

logger = logging.getLogger(__name__)

# Helper functions
def json_response(data, status=200):
    """Helper function to create a JSON response."""
    return JsonResponse(data, status=status, safe=False)

def error_response(message, status=400):
    """Helper function to create an error response."""
    return JsonResponse({"error": message}, status=status)

def parse_request_data(request):
    """Parse JSON data from request."""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing request data: {str(e)}")

# Project endpoints
@csrf_exempt
@require_http_methods(["GET"])
def get_projects(request):
    """Get a list of projects."""
    try:
        # Get optional filters from query params
        status = request.GET.get('status')
        location = request.GET.get('location')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if location:
            query['location'] = location
            
        # Get projects
        projects = Project.objects.filter(**query)
        
        # Convert to list of dicts
        project_list = []
        for project in projects:
            project_data = {
                "id": project.pk,
                "archive_id": project.archive_id,
                "name": project.name,
                "location": project.location,
                "status": project.status,
                "has_oversized": project.has_oversized,
                "creation_date": project.creation_date.isoformat() if project.creation_date else None,
                "completion_date": project.completion_date.isoformat() if project.completion_date else None,
            }
            project_list.append(project_data)
            
        return json_response({"projects": project_list})
        
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return error_response(f"Error getting projects: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def get_project(request, project_id):
    """Get detailed information about a project."""
    try:
        project_manager = ProjectManager()
        stats = project_manager.get_project_stats(project_id)
        return json_response(stats)
        
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        return error_response(f"Error getting project: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def create_project(request):
    """Create a new project."""
    try:
        data = parse_request_data(request)
        
        # Extract required fields
        archive_id = data.get('archive_id')
        location = data.get('location')
        
        if not archive_id or not location:
            return error_response("archive_id and location are required")
        
        # Extract optional fields
        name = data.get('name')
        notes = data.get('notes')
        has_oversized = data.get('has_oversized', False)
        
        # Create project
        project_manager = ProjectManager()
        project = project_manager.create_project(
            archive_id=archive_id,
            location=location,
            name=name,
            notes=notes,
            has_oversized=has_oversized
        )
        
        # Return project data
        return json_response({
            "id": project.pk,
            "archive_id": project.archive_id,
            "name": project.name,
            "location": project.location,
            "status": project.status,
            "has_oversized": project.has_oversized,
            "creation_date": project.creation_date.isoformat() if project.creation_date else None,
        }, status=201)
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        return error_response(f"Error creating project: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def process_project(request, project_id):
    """Process a project to create rolls and allocate film numbers."""
    try:
        data = parse_request_data(request)
        
        # Extract optional fields
        allocate_film_numbers = data.get('allocate_film_numbers', True)
        document_data = data.get('document_data')
        
        # Process project
        project_manager = ProjectManager()
        project, stats = project_manager.process_project(
            project_id=project_id,
            document_data=document_data,
            allocate_film_numbers=allocate_film_numbers
        )
        
        # Return statistics
        return json_response(stats)
        
    except Exception as e:
        logger.error(f"Error processing project {project_id}: {str(e)}")
        return error_response(f"Error processing project: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def import_documents(request, project_id):
    """Import documents for a project."""
    try:
        data = parse_request_data(request)
        
        # Get document data
        document_data = data.get('document_data')
        if not document_data:
            return error_response("document_data is required")
        
        # Process document data
        project_manager = ProjectManager()
        project, imported_data = project_manager.import_document_data(
            project_id=project_id,
            data_json=json.dumps(document_data)
        )
        
        # Count document statistics
        doc_count = len(imported_data.get("documents", []))
        regular_count = sum(1 for doc in imported_data.get("documents", []) 
                           if not doc.get("is_oversized", False))
        oversized_count = sum(1 for doc in imported_data.get("documents", []) 
                            if doc.get("is_oversized", False))
        
        # Return statistics
        return json_response({
            "project_id": project.pk,
            "archive_id": project.archive_id,
            "total_documents": doc_count,
            "regular_documents": regular_count,
            "oversized_documents": oversized_count,
            "status": project.status
        })
        
    except Exception as e:
        logger.error(f"Error importing documents for project {project_id}: {str(e)}")
        return error_response(f"Error importing documents: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def complete_project(request, project_id):
    """Mark a project as completed."""
    try:
        data = parse_request_data(request)
        
        # Extract optional fields
        notes = data.get('notes')
        
        # Mark project as completed
        project_manager = ProjectManager()
        project = project_manager.mark_project_as_completed(
            project_id=project_id,
            notes=notes
        )
        
        # Return project data
        return json_response({
            "id": project.pk,
            "archive_id": project.archive_id,
            "status": project.status,
            "completion_date": project.completion_date.isoformat() if project.completion_date else None,
        })
        
    except Exception as e:
        logger.error(f"Error completing project {project_id}: {str(e)}")
        return error_response(f"Error completing project: {str(e)}")

# Document endpoints
@csrf_exempt
@require_http_methods(["GET"])
def get_document(request, doc_id):
    """Get information about a document."""
    try:
        # Get optional project_id from query params
        project_id = request.GET.get('project_id')
        
        # Get document info
        document_manager = DocumentManager()
        doc_info = document_manager.get_document_info(
            doc_id=doc_id,
            project_id=project_id
        )
        
        return json_response(doc_info)
        
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {str(e)}")
        return error_response(f"Error getting document: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def lookup_blip(request, blip):
    """Look up a document by its blip code."""
    try:
        # Get document info by blip
        document_manager = DocumentManager()
        doc_info = document_manager.lookup_document_by_blip(blip=blip)
        
        return json_response(doc_info)
        
    except Exception as e:
        logger.error(f"Error looking up blip {blip}: {str(e)}")
        return error_response(f"Error looking up blip: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def bulk_import_documents(request, project_id):
    """Bulk import documents for a project."""
    try:
        data = parse_request_data(request)
        
        # Get document list
        document_list = data.get('documents')
        if not document_list:
            return error_response("documents list is required")
        
        # Import documents
        document_manager = DocumentManager()
        stats = document_manager.bulk_import_documents(
            project_id=project_id,
            document_list=document_list
        )
        
        return json_response(stats)
        
    except Exception as e:
        logger.error(f"Error bulk importing documents for project {project_id}: {str(e)}")
        return error_response(f"Error bulk importing documents: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def split_document(request, doc_id, project_id):
    """Split a document into multiple allocation requests."""
    try:
        data = parse_request_data(request)
        
        # Get page ranges
        page_ranges = data.get('page_ranges')
        if not page_ranges:
            return error_response("page_ranges are required")
        
        # Split document
        document_manager = DocumentManager()
        requests = document_manager.split_oversized_document(
            doc_id=doc_id,
            project_id=project_id,
            page_ranges=page_ranges
        )
        
        # Return request data
        request_data = [
            {
                "id": req.pk,
                "start_page": req.start_page,
                "end_page": req.end_page,
                "pages": req.pages,
                "processed": req.processed
            }
            for req in requests
        ]
        
        return json_response({"allocation_requests": request_data})
        
    except Exception as e:
        logger.error(f"Error splitting document {doc_id}: {str(e)}")
        return error_response(f"Error splitting document: {str(e)}")

# Roll endpoints
@csrf_exempt
@require_http_methods(["GET"])
def get_rolls(request, project_id):
    """Get rolls for a project."""
    try:
        # Get optional filters from query params
        film_type = request.GET.get('film_type')
        status = request.GET.get('status')
        
        # Build query
        query = {"project_id": project_id}
        if film_type:
            query['film_type'] = film_type
        if status:
            query['status'] = status
            
        # Get rolls
        rolls = Roll.objects.filter(**query)
        
        # Convert to list of dicts
        roll_list = []
        for roll in rolls:
            roll_data = {
                "id": roll.pk,
                "roll_id": roll.roll_id,
                "film_number": roll.film_number,
                "film_type": roll.film_type,
                "capacity": roll.capacity,
                "pages_used": roll.pages_used,
                "pages_remaining": roll.pages_remaining,
                "status": roll.status,
                "is_full": roll.is_full,
                "is_partial": roll.is_partial,
                "creation_date": roll.creation_date.isoformat() if roll.creation_date else None,
            }
            roll_list.append(roll_data)
            
        return json_response({"rolls": roll_list})
        
    except Exception as e:
        logger.error(f"Error getting rolls for project {project_id}: {str(e)}")
        return error_response(f"Error getting rolls: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def get_roll(request, roll_id):
    """Get detailed information about a roll."""
    try:
        # Get roll
        roll = Roll.objects.get(pk=roll_id)
        
        # Get document segments for this roll
        from microapp.models import DocumentSegment
        segments = DocumentSegment.objects.filter(roll=roll).order_by('document_index')
        
        # Build segment data
        segment_list = []
        for segment in segments:
            segment_data = {
                "id": segment.pk,
                "document_id": segment.document_id,
                "doc_id": segment.document.doc_id,
                "pages": segment.pages,
                "start_page": segment.start_page,
                "end_page": segment.end_page,
                "document_index": segment.document_index,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "blip": segment.blip,
                "blipend": segment.blipend,
                "has_oversized": segment.has_oversized
            }
            segment_list.append(segment_data)
        
        # Build roll data
        roll_data = {
            "id": roll.pk,
            "roll_id": roll.roll_id,
            "film_number": roll.film_number,
            "film_type": roll.film_type,
            "capacity": roll.capacity,
            "pages_used": roll.pages_used,
            "pages_remaining": roll.pages_remaining,
            "status": roll.status,
            "is_full": roll.is_full,
            "is_partial": roll.is_partial,
            "creation_date": roll.creation_date.isoformat() if roll.creation_date else None,
            "project_id": roll.project_id,
            "archive_id": roll.project.archive_id if roll.project else None,
            "documents": segment_list
        }
        
        return json_response(roll_data)
        
    except Roll.DoesNotExist:
        return error_response(f"Roll {roll_id} not found", status=404)
    except Exception as e:
        logger.error(f"Error getting roll {roll_id}: {str(e)}")
        return error_response(f"Error getting roll: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def mark_roll_scanned(request, roll_id):
    """Mark a roll as scanned."""
    try:
        data = parse_request_data(request)
        
        # Extract optional fields
        notes = data.get('notes')
        scanned_date = data.get('scanned_date')
        
        # Convert scanned_date if provided
        if scanned_date:
            from datetime import datetime
            scanned_date = datetime.fromisoformat(scanned_date)
        
        # Mark roll as scanned
        roll_manager = RollManager()
        roll = roll_manager.mark_roll_as_scanned(
            roll_id=roll_id,
            scanned_date=scanned_date,
            notes=notes
        )
        
        # Return roll data
        return json_response({
            "id": roll.pk,
            "roll_id": roll.roll_id,
            "status": roll.status,
            "scan_date": roll.scan_date.isoformat() if roll.scan_date else None,
        })
        
    except Exception as e:
        logger.error(f"Error marking roll {roll_id} as scanned: {str(e)}")
        return error_response(f"Error marking roll as scanned: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def merge_rolls(request):
    """Merge two rolls."""
    try:
        data = parse_request_data(request)
        
        # Extract required fields
        source_roll_id = data.get('source_roll_id')
        target_roll_id = data.get('target_roll_id')
        
        if not source_roll_id or not target_roll_id:
            return error_response("source_roll_id and target_roll_id are required")
        
        # Merge rolls
        roll_manager = RollManager()
        roll = roll_manager.merge_rolls(
            source_roll_id=source_roll_id,
            target_roll_id=target_roll_id
        )
        
        # Return roll data
        return json_response({
            "id": roll.pk,
            "roll_id": roll.roll_id,
            "film_number": roll.film_number,
            "film_type": roll.film_type,
            "pages_used": roll.pages_used,
            "pages_remaining": roll.pages_remaining,
            "status": roll.status,
            "is_full": roll.is_full,
            "is_partial": roll.is_partial,
        })
        
    except Exception as e:
        logger.error(f"Error merging rolls: {str(e)}")
        return error_response(f"Error merging rolls: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def export_allocation_data(request, project_id):
    """Export allocation data for a project."""
    try:
        # Get optional params
        include_documents = request.GET.get('include_documents', 'true').lower() == 'true'
        
        # Export data
        project_manager = ProjectManager()
        data = project_manager.export_allocation_data(
            project_id=project_id,
            include_documents=include_documents
        )
        
        return json_response(data)
        
    except Exception as e:
        logger.error(f"Error exporting allocation data for project {project_id}: {str(e)}")
        return error_response(f"Error exporting allocation data: {str(e)}")

# Film number endpoints
@csrf_exempt
@require_http_methods(["POST"])
def allocate_film_numbers(request, project_id):
    """Allocate film numbers for a project."""
    try:
        data = parse_request_data(request)
        
        # Extract data fields
        project_data = data.get('project_data')
        analysis_data = data.get('analysis_data')
        allocation_data = data.get('allocation_data')
        index_data = data.get('index_data')
        
        # Allocate film numbers
        film_number_manager = FilmNumberManager()
        project, updated_index = film_number_manager.allocate_film_numbers(
            project_id=project_id,
            project_data=project_data,
            analysis_data=analysis_data,
            allocation_data=allocation_data,
            index_data=index_data
        )
        
        # Get allocation statistics
        from microapp.models import Roll
        stats = {
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
            stats["index_updated"] = True
            stats["index_data"] = updated_index
        
        return json_response(stats)
        
    except Exception as e:
        logger.error(f"Error allocating film numbers for project {project_id}: {str(e)}")
        return error_response(f"Error allocating film numbers: {str(e)}") 