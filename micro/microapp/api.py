"""
API endpoints for microfilm processing services.

This module provides REST API endpoints for interacting with
microfilm processing services.
"""

import json
import logging
import csv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from datetime import datetime

from microapp.services import (
    FilmNumberManager,
    RollManager,
    ProjectManager,
    DocumentManager,
)
from microapp.models import Project, Document, Roll, TempRoll

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
    """Get detailed information about a document."""
    try:
        # Get optional project_id from query params
        project_id = request.GET.get('project_id')
        
        # Get document info
        document_manager = DocumentManager()
        doc_info = document_manager.get_document_info(
            doc_id=doc_id,
            project_id=project_id
        )
        
        # If the document manager returns basic info, enhance it with additional details
        if doc_info and 'document' not in doc_info:
            # Try to get the document from database for additional details
            try:
                if project_id:
                    document = Document.objects.get(doc_id=doc_id, project_id=project_id)
                else:
                    document = Document.objects.filter(doc_id=doc_id).first()
                
                if document:
                    # Get file information
                    import os
                    file_size = "N/A"
                    file_type = "Unknown"
                    last_modified = None
                    
                    if document.path and os.path.exists(document.path):
                        try:
                            stat = os.stat(document.path)
                            file_size = f"{stat.st_size / (1024*1024):.2f} MB"
                            last_modified = stat.st_mtime
                            file_type = os.path.splitext(document.path)[1].upper().lstrip('.')
                        except:
                            pass
                    
                    # Get roll allocation information
                    from microapp.models import DocumentSegment
                    segments = DocumentSegment.objects.filter(document=document).order_by('roll__roll_id')
                    
                    roll_info = []
                    for segment in segments:
                        roll_info.append({
                            "roll_id": segment.roll.id,
                            "roll_number": segment.roll.roll_id,
                            "film_number": segment.roll.film_number,
                            "start_page": segment.start_page,
                            "end_page": segment.end_page,
                            "start_frame": segment.start_frame,
                            "end_frame": segment.end_frame
                        })
                    
                    # Enhanced document data
                    enhanced_doc = {
                        "id": document.id,
                        "doc_id": document.doc_id,
                        "name": os.path.basename(document.path) if document.path else f"Document {document.doc_id}",
                        "path": document.path,
                        "file_type": file_type,
                        "file_size": file_size,
                        "pages": document.pages,
                        "has_oversized": document.has_oversized,
                        "total_oversized": document.total_oversized,
                        "total_references": document.total_references,
                        "is_split": document.is_split,
                        "roll_count": document.roll_count,
                        "project_id": document.project_id,
                        "com_id": document.com_id,
                        "is_processed": bool(document.segments.exists()),  # Has segments means it's been processed
                        "creation_date": document.created_at.isoformat() if document.created_at else None,
                        "last_modified": last_modified,
                        "checksum": "N/A",  # Could be calculated if needed
                        "roll_allocations": roll_info
                    }
                    
                    # Add roll allocation summary
                    if roll_info:
                        enhanced_doc["roll_id"] = roll_info[0]["roll_id"]  # Primary roll
                        enhanced_doc["start_page"] = min(r["start_page"] for r in roll_info)
                        enhanced_doc["end_page"] = max(r["end_page"] for r in roll_info)
                    
                    return json_response({"document": enhanced_doc})
                    
            except Document.DoesNotExist:
                pass
        
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
def get_documents(request, project_id):
    """Get documents for a project."""
    try:
        # Get optional filters from query params
        has_oversized = request.GET.get('has_oversized')
        is_split = request.GET.get('is_split')
        
        # Build query
        query = {"project_id": project_id}
        if has_oversized is not None:
            query['has_oversized'] = has_oversized.lower() == 'true'
        if is_split is not None:
            query['is_split'] = is_split.lower() == 'true'
            
        # Get documents
        documents = Document.objects.filter(**query).order_by('doc_id')
        
        # Convert to list of dicts
        document_list = []
        for doc in documents:
            document_data = {
                "id": doc.pk,
                "doc_id": doc.doc_id,
                "path": doc.path,
                "com_id": doc.com_id,
                "pages": doc.pages,
                "has_oversized": doc.has_oversized,
                "total_oversized": doc.total_oversized,
                "total_references": doc.total_references,
                "is_split": doc.is_split,
                "roll_count": doc.roll_count,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
                "name": doc.path.split('/')[-1] if doc.path else f"Document {doc.doc_id}"
            }
            document_list.append(document_data)
            
        return json_response({"documents": document_list})
        
    except Exception as e:
        logger.error(f"Error getting documents for project {project_id}: {str(e)}")
        return error_response(f"Error getting documents: {str(e)}")

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
        
        return JsonResponse({
            'success': True,
            'message': 'Film numbers allocated successfully',
            'project': {
                'id': project.id,
                'archive_id': project.archive_id,
                'film_allocation_complete': project.film_allocation_complete
            },
            'index_updated': updated_index is not None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_roll_documents(request, roll_id):
    """Get documents allocated to a specific roll."""
    try:
        # Get roll
        roll = Roll.objects.get(pk=roll_id)
        
        # Get document segments for this roll
        from microapp.models import DocumentSegment
        segments = DocumentSegment.objects.filter(roll=roll).select_related('document').order_by('document_index')
        
        # Build document list
        documents = []
        for segment in segments:
            doc = segment.document
            
            # Get file information
            import os
            file_size = "N/A"
            file_type = "Unknown"
            
            if doc.path and os.path.exists(doc.path):
                try:
                    stat = os.stat(doc.path)
                    file_size = f"{stat.st_size / (1024*1024):.2f} MB"
                    file_type = os.path.splitext(doc.path)[1].upper().lstrip('.')
                except:
                    pass
            
            document_data = {
                "id": doc.id,
                "doc_id": doc.doc_id,
                "name": os.path.basename(doc.path) if doc.path else f"Document {doc.doc_id}",
                "path": doc.path,
                "file_type": file_type,
                "file_size": file_size,
                "pages": doc.pages,
                "has_oversized": doc.has_oversized,
                "total_oversized": doc.total_oversized,
                "is_split": doc.is_split,
                "project_id": doc.project_id,
                # Roll-specific information
                "start_page": segment.start_page,
                "end_page": segment.end_page,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "document_index": segment.document_index,
                "blip": segment.blip,
                "blipend": segment.blipend,
                "segment_pages": segment.pages,
                "segment_has_oversized": segment.has_oversized
            }
            documents.append(document_data)
        
        return json_response({
            "roll_id": roll.id,
            "roll_number": roll.roll_id,
            "film_number": roll.film_number,
            "documents": documents,
            "total_documents": len(documents),
            "total_pages": sum(doc["segment_pages"] for doc in documents)
        })
        
    except Roll.DoesNotExist:
        return error_response(f"Roll {roll_id} not found", status=404)
    except Exception as e:
        logger.error(f"Error getting documents for roll {roll_id}: {str(e)}")
        return error_response(f"Error getting roll documents: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def get_document_segments(request, doc_id):
    """Get roll allocation segments for a document."""
    try:
        # Get optional project_id from query params
        project_id = request.GET.get('project_id')
        
        # Get document
        if project_id:
            document = Document.objects.get(doc_id=doc_id, project_id=project_id)
        else:
            document = Document.objects.filter(doc_id=doc_id).first()
            
        if not document:
            return error_response(f"Document {doc_id} not found", status=404)
        
        # Get document segments
        from microapp.models import DocumentSegment
        segments = DocumentSegment.objects.filter(document=document).select_related('roll').order_by('roll__roll_id', 'document_index')
        
        # Build segment list
        segment_list = []
        for segment in segments:
            roll = segment.roll
            segment_data = {
                "id": segment.id,
                "pages": segment.pages,
                "start_page": segment.start_page,
                "end_page": segment.end_page,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "document_index": segment.document_index,
                "has_oversized": segment.has_oversized,
                "blip": segment.blip,
                "blipend": segment.blipend,
                "created_at": segment.created_at.isoformat() if segment.created_at else None,
                # Roll information
                "roll": {
                    "id": roll.id,
                    "roll_id": roll.roll_id,
                    "film_number": roll.film_number,
                    "film_type": roll.film_type,
                    "capacity": roll.capacity,
                    "pages_used": roll.pages_used,
                    "status": roll.status,
                    "is_full": roll.is_full,
                    "is_partial": roll.is_partial
                }
            }
            segment_list.append(segment_data)
        
        return json_response({
            "document_id": document.id,
            "doc_id": document.doc_id,
            "total_pages": document.pages,
            "is_split": document.is_split,
            "roll_count": document.roll_count,
            "segments": segment_list,
            "total_segments": len(segment_list)
        })
        
    except Document.DoesNotExist:
        return error_response(f"Document {doc_id} not found", status=404)
    except Exception as e:
        logger.error(f"Error getting segments for document {doc_id}: {str(e)}")
        return error_response(f"Error getting document segments: {str(e)}")

# Temp Roll API Endpoints

@csrf_exempt
@require_http_methods(["GET"])
def get_temp_rolls(request):
    """Get list of temp rolls with optional filtering."""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        film_type = request.GET.get('film_type')
        status = request.GET.get('status')
        min_capacity = request.GET.get('min_capacity')
        search = request.GET.get('search')
        sort_field = request.GET.get('sort_field', 'temp_roll_id')
        sort_direction = request.GET.get('sort_direction', 'desc')
        exists_param = request.GET.get('exists')
        
        # Build queryset
        queryset = TempRoll.objects.all()
        
        # Apply filters
        if film_type:
            queryset = queryset.filter(film_type=film_type)
        if status:
            queryset = queryset.filter(status=status)
        if exists_param is not None:
            # Treat any truthy string ("1","true","True") as True
            exists_bool = str(exists_param).lower() in ['1', 'true', 'yes', 'y']
            queryset = queryset.filter(exists=exists_bool)
        if min_capacity:
            queryset = queryset.filter(usable_capacity__gte=int(min_capacity))
        if search:
            queryset = queryset.filter(
                Q(temp_roll_id__icontains=search) |
                Q(film_type__icontains=search) |
                Q(status__icontains=search)
            )
        
        # Apply sorting
        if sort_direction == 'desc':
            sort_field = f'-{sort_field}'
        queryset = queryset.order_by(sort_field)
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize temp rolls
        temp_rolls = []
        for temp_roll in page_obj:
            temp_roll_data = {
                'temp_roll_id': temp_roll.temp_roll_id,
                'film_type': temp_roll.film_type,
                'capacity': temp_roll.capacity,
                'usable_capacity': temp_roll.usable_capacity,
                'status': temp_roll.status,
                    'exists': getattr(temp_roll, 'exists', False),
                'creation_date': temp_roll.creation_date.isoformat() if temp_roll.creation_date else None,
                'source_roll_id': temp_roll.source_roll_id,
                'used_by_roll_id': temp_roll.used_by_roll_id,
            }
            
            # Add related roll information if available
            if temp_roll.source_roll:
                temp_roll_data['source_roll'] = {
                    'id': temp_roll.source_roll.id,
                    'roll_id': temp_roll.source_roll.roll_id,
                    'film_number': temp_roll.source_roll.film_number
                }
            
            if temp_roll.used_by_roll:
                temp_roll_data['used_by_roll'] = {
                    'id': temp_roll.used_by_roll.id,
                    'roll_id': temp_roll.used_by_roll.roll_id,
                    'film_number': temp_roll.used_by_roll.film_number
                }
            
            temp_rolls.append(temp_roll_data)
        
        return JsonResponse({
            'temp_rolls': temp_rolls,
            'total_count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_temp_roll(request, temp_roll_id):
    """Get detailed information about a specific temp roll."""
    try:
        temp_roll = get_object_or_404(TempRoll, temp_roll_id=temp_roll_id)
        
        temp_roll_data = {
            'temp_roll_id': temp_roll.temp_roll_id,
            'film_type': temp_roll.film_type,
            'capacity': temp_roll.capacity,
            'usable_capacity': temp_roll.usable_capacity,
            'status': temp_roll.status,
            'creation_date': temp_roll.creation_date.isoformat() if temp_roll.creation_date else None,
            'source_roll_id': temp_roll.source_roll_id,
            'used_by_roll_id': temp_roll.used_by_roll_id,
        }
        
        # Add related roll information if available
        if temp_roll.source_roll:
            temp_roll_data['source_roll'] = {
                'id': temp_roll.source_roll.id,
                'roll_id': temp_roll.source_roll.roll_id,
                'film_number': temp_roll.source_roll.film_number,
                'film_type': temp_roll.source_roll.film_type,
                'capacity': temp_roll.source_roll.capacity,
                'pages_used': temp_roll.source_roll.pages_used,
                'status': temp_roll.source_roll.status,
                'is_full': temp_roll.source_roll.is_full,
                'is_partial': temp_roll.source_roll.is_partial
            }
        
        if temp_roll.used_by_roll:
            temp_roll_data['used_by_roll'] = {
                'id': temp_roll.used_by_roll.id,
                'roll_id': temp_roll.used_by_roll.roll_id,
                'film_number': temp_roll.used_by_roll.film_number,
                'film_type': temp_roll.used_by_roll.film_type,
                'capacity': temp_roll.used_by_roll.capacity,
                'pages_used': temp_roll.used_by_roll.pages_used,
                'status': temp_roll.used_by_roll.status,
                'is_full': temp_roll.used_by_roll.is_full,
                'is_partial': temp_roll.used_by_roll.is_partial
            }
        
        return JsonResponse({
            'temp_roll': temp_roll_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_temp_roll(request):
    """Create a new temp roll."""
    try:
        data = parse_request_data(request)
        
        # Validate required fields
        required_fields = ['film_type', 'capacity', 'usable_capacity']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Create temp roll
        temp_roll = TempRoll.objects.create(
            film_type=data['film_type'],
            capacity=data['capacity'],
            usable_capacity=data['usable_capacity'],
            status=data.get('status', 'available'),
            source_roll_id=data.get('source_roll_id'),
            used_by_roll_id=data.get('used_by_roll_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Temp roll created successfully',
            'temp_roll': {
                'temp_roll_id': temp_roll.temp_roll_id,
                'film_type': temp_roll.film_type,
                'capacity': temp_roll.capacity,
                'usable_capacity': temp_roll.usable_capacity,
                'status': temp_roll.status,
                'creation_date': temp_roll.creation_date.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def update_temp_roll(request, temp_roll_id):
    """Update an existing temp roll."""
    try:
        temp_roll = get_object_or_404(TempRoll, temp_roll_id=temp_roll_id)
        data = parse_request_data(request)
        
        # Update fields
        if 'film_type' in data:
            temp_roll.film_type = data['film_type']
        if 'capacity' in data:
            temp_roll.capacity = data['capacity']
        if 'usable_capacity' in data:
            temp_roll.usable_capacity = data['usable_capacity']
        if 'status' in data:
            temp_roll.status = data['status']
        if 'source_roll_id' in data:
            temp_roll.source_roll_id = data['source_roll_id']
        if 'used_by_roll_id' in data:
            temp_roll.used_by_roll_id = data['used_by_roll_id']
        
        temp_roll.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Temp roll updated successfully',
            'temp_roll': {
                'temp_roll_id': temp_roll.temp_roll_id,
                'film_type': temp_roll.film_type,
                'capacity': temp_roll.capacity,
                'usable_capacity': temp_roll.usable_capacity,
                'status': temp_roll.status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_temp_roll(request, temp_roll_id):
    """Delete a temp roll."""
    try:
        temp_roll = get_object_or_404(TempRoll, temp_roll_id=temp_roll_id)
        temp_roll.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Temp roll deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def export_temp_rolls(request):
    """Export temp rolls to various formats."""
    try:
        data = parse_request_data(request)
        temp_roll_ids = data.get('temp_roll_ids')
        format_type = data.get('format', 'csv')
        
        # Get temp rolls
        if temp_roll_ids:
            temp_rolls = TempRoll.objects.filter(temp_roll_id__in=temp_roll_ids)
        else:
            temp_rolls = TempRoll.objects.all()
        
        # For now, return a simple CSV response
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="temp_rolls.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Temp Roll ID', 'Film Type', 'Capacity', 'Usable Capacity', 'Status', 'Source Roll', 'Used By Roll', 'Creation Date'])
            
            for temp_roll in temp_rolls:
                writer.writerow([
                    temp_roll.temp_roll_id,
                    temp_roll.film_type,
                    temp_roll.capacity,
                    temp_roll.usable_capacity,
                    temp_roll.status,
                    temp_roll.source_roll.roll_id if temp_roll.source_roll else 'None',
                    temp_roll.used_by_roll.roll_id if temp_roll.used_by_roll else 'None',
                    temp_roll.creation_date.strftime('%Y-%m-%d') if temp_roll.creation_date else 'N/A'
                ])
            
            return response
        
        return JsonResponse({
            'error': f'Unsupported format: {format_type}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

# Document API Endpoints

@csrf_exempt
@require_http_methods(["GET"])
def get_documents_list(request):
    """Get list of documents with optional filtering and pagination."""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        search = request.GET.get('search', '')
        file_type = request.GET.get('file_type', '')
        status = request.GET.get('status', '')
        oversized = request.GET.get('oversized', '')
        project_id = request.GET.get('project_id', '')
        roll_id = request.GET.get('roll_id', '')
        min_pages = request.GET.get('min_pages', '')
        max_pages = request.GET.get('max_pages', '')
        sort_field = request.GET.get('sort_field', 'id')
        sort_direction = request.GET.get('sort_direction', 'asc')
        
        # Build queryset
        queryset = Document.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(doc_id__icontains=search) |
                Q(path__icontains=search) |
                Q(project__archive_id__icontains=search)
            )
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        if roll_id:
            queryset = queryset.filter(segments__roll_id=roll_id).distinct()
            
        if oversized:
            oversized_bool = oversized.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(has_oversized=oversized_bool)
            
        if min_pages:
            queryset = queryset.filter(pages__gte=int(min_pages))
            
        if max_pages:
            queryset = queryset.filter(pages__lte=int(max_pages))
        
        # Apply sorting
        if sort_direction == 'desc':
            sort_field = f'-{sort_field}'
        queryset = queryset.order_by(sort_field)
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize documents
        documents = []
        for doc in page_obj:
            # Determine file type from path
            file_extension = doc.path.split('.')[-1].upper() if doc.path else 'UNKNOWN'
            
            # Determine status based on document properties
            if doc.is_split:
                status = 'processed'
            elif doc.has_oversized:
                status = 'pending'
            else:
                status = 'draft'
            
            # Calculate file size (mock for now)
            file_size = doc.pages * 50000 if doc.pages else 0
            
            documents.append({
                'id': doc.id,
                'doc_id': doc.doc_id,
                'name': doc.path.split('/')[-1] if doc.path else f"Document {doc.doc_id}",
                'path': doc.path,
                'file_type': file_extension,
                'status': status,
                'pages': doc.pages,
                'has_oversized': doc.has_oversized,
                'file_size': file_size,
                'project_id': doc.project_id,
                'roll_id': doc.segments.first().roll_id if doc.segments.exists() else None,
                'creation_date': doc.created_at.isoformat() if doc.created_at else None,
                'last_modified': doc.updated_at.isoformat() if doc.updated_at else None,
                'com_id': doc.com_id,
                'total_oversized': doc.total_oversized,
                'total_references': doc.total_references,
                'is_split': doc.is_split,
                'roll_count': doc.roll_count
            })
        
        return json_response({
            'documents': documents,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages
        })
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return error_response(f"Error getting documents: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def get_document_by_id(request, document_id):
    """Get a single document by ID."""
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Get related data
        segments = document.segments.all().order_by('roll__roll_id', 'start_page')
        
        # Determine file type and status
        file_extension = document.path.split('.')[-1].upper() if document.path else 'UNKNOWN'
        
        if document.is_split:
            status = 'processed'
        elif document.has_oversized:
            status = 'pending'
        else:
            status = 'draft'
        
        # Calculate file size (mock for now)
        file_size = document.pages * 50000 if document.pages else 0
        
        document_data = {
            'id': document.id,
            'doc_id': document.doc_id,
            'name': document.path.split('/')[-1] if document.path else f"Document {document.doc_id}",
            'path': document.path,
            'file_type': file_extension,
            'status': status,
            'pages': document.pages,
            'has_oversized': document.has_oversized,
            'file_size': file_size,
            'project_id': document.project_id,
            'project_archive_id': document.project.archive_id if document.project else None,
            'creation_date': document.created_at.isoformat() if document.created_at else None,
            'last_modified': document.updated_at.isoformat() if document.updated_at else None,
            'com_id': document.com_id,
            'total_oversized': document.total_oversized,
            'total_references': document.total_references,
            'is_split': document.is_split,
            'roll_count': document.roll_count,
            'segments': [
                {
                    'id': seg.id,
                    'roll_id': seg.roll_id,
                    'roll_film_number': seg.roll.film_number if seg.roll else None,
                    'pages': seg.pages,
                    'start_page': seg.start_page,
                    'end_page': seg.end_page,
                    'start_frame': seg.start_frame,
                    'end_frame': seg.end_frame,
                    'document_index': seg.document_index,
                    'has_oversized': seg.has_oversized,
                    'blip': seg.blip,
                    'blipend': seg.blipend
                } for seg in segments
            ]
        }
        
        return json_response({'document': document_data})
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return error_response(f"Error getting document: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def create_document(request):
    """Create a new document."""
    try:
        data = parse_request_data(request)
        
        # Validate required fields
        required_fields = ['doc_id', 'path', 'project_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}")
        
        # Get project
        project = get_object_or_404(Project, id=data['project_id'])
        
        # Check if document already exists
        if Document.objects.filter(project=project, doc_id=data['doc_id']).exists():
            return error_response(f"Document with ID {data['doc_id']} already exists in this project")
        
        # Create document
        document = Document.objects.create(
                project=project,
            doc_id=data['doc_id'],
            path=data['path'],
            com_id=data.get('com_id'),
            pages=data.get('pages', 0),
            has_oversized=data.get('has_oversized', False),
            total_oversized=data.get('total_oversized', 0),
            total_references=data.get('total_references', 0),
            is_split=data.get('is_split', False),
            roll_count=data.get('roll_count', 1)
        )
        
        return json_response({
            'success': True,
            'message': 'Document created successfully',
            'document': {
                'id': document.id,
                'doc_id': document.doc_id,
                'path': document.path,
                'project_id': document.project_id,
                'pages': document.pages,
                'has_oversized': document.has_oversized,
                'created_at': document.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        return error_response(f"Error creating document: {str(e)}")

@csrf_exempt
@require_http_methods(["PUT"])
def update_document(request, document_id):
    """Update an existing document."""
    try:
        data = parse_request_data(request)
        document = get_object_or_404(Document, id=document_id)
        
        # Update fields
        updatable_fields = [
            'doc_id', 'path', 'com_id', 'pages', 'has_oversized',
            'total_oversized', 'total_references', 'is_split', 'roll_count'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(document, field, data[field])
        
        document.save()
        
        return json_response({
            'success': True,
            'message': 'Document updated successfully',
            'document': {
                'id': document.id,
                'doc_id': document.doc_id,
                'path': document.path,
                'project_id': document.project_id,
                'pages': document.pages,
                'has_oversized': document.has_oversized,
                'updated_at': document.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        return error_response(f"Error updating document: {str(e)}")

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_document(request, document_id):
    """Delete a document."""
    try:
        document = get_object_or_404(Document, id=document_id)
        doc_id = document.doc_id
        document.delete()
        
        return json_response({
            'success': True,
            'message': f'Document {doc_id} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return error_response(f"Error deleting document: {str(e)}")

@csrf_exempt
@require_http_methods(["GET"])
def search_documents(request):
    """Search documents by keyword."""
    try:
        keyword = request.GET.get('q', '')
        project_id = request.GET.get('project_id', '')
        limit = int(request.GET.get('limit', 20))
        
        if not keyword:
            return error_response("Search keyword is required")
        
        # Build query
        query = Q(doc_id__icontains=keyword) | Q(path__icontains=keyword)
        
        if project_id:
            query &= Q(project_id=project_id)
        
        # Search documents
        documents = Document.objects.filter(query)[:limit]
        
        # Serialize results
        results = []
        for doc in documents:
            file_extension = doc.path.split('.')[-1].upper() if doc.path else 'UNKNOWN'
            
            if doc.is_split:
                status = 'processed'
            elif doc.has_oversized:
                status = 'pending'
            else:
                status = 'draft'
            
            results.append({
                'id': doc.id,
                'doc_id': doc.doc_id,
                'name': doc.path.split('/')[-1] if doc.path else f"Document {doc.doc_id}",
                'path': doc.path,
                'file_type': file_extension,
                'status': status,
                'pages': doc.pages,
                'has_oversized': doc.has_oversized,
                'project_id': doc.project_id,
                'project_archive_id': doc.project.archive_id if doc.project else None
            })
        
        return json_response({
            'documents': results,
            'total': len(results),
            'keyword': keyword
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return error_response(f"Error searching documents: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def export_documents(request):
    """Export documents to various formats."""
    try:
        data = parse_request_data(request)
        document_ids = data.get('document_ids', [])
        format_type = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Get documents
        if document_ids:
            documents = Document.objects.filter(id__in=document_ids)
        else:
            # Apply filters if no specific IDs provided
            documents = Document.objects.all()
            
            if filters.get('project_id'):
                documents = documents.filter(project_id=filters['project_id'])
            if filters.get('has_oversized') is not None:
                documents = documents.filter(has_oversized=filters['has_oversized'])
        
        documents = documents.order_by('project__archive_id', 'doc_id')
        
        # Generate export data based on format
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="documents_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Document ID', 'Project Archive ID', 'Path', 'Pages', 
                'Has Oversized', 'Total Oversized', 'Total References',
                'Is Split', 'Roll Count', 'COM ID', 'Created', 'Updated'
            ])
            
            for doc in documents:
                writer.writerow([
                    doc.doc_id,
                    doc.project.archive_id if doc.project else '',
                    doc.path,
                    doc.pages,
                    doc.has_oversized,
                    doc.total_oversized,
                    doc.total_references,
                    doc.is_split,
                    doc.roll_count,
                    doc.com_id or '',
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S') if doc.created_at else '',
                    doc.updated_at.strftime('%Y-%m-%d %H:%M:%S') if doc.updated_at else ''
                ])
            
            return response
            
        elif format_type == 'json':
            documents_data = []
            for doc in documents:
                documents_data.append({
                    'id': doc.id,
                    'doc_id': doc.doc_id,
                    'project_archive_id': doc.project.archive_id if doc.project else None,
                    'path': doc.path,
                    'pages': doc.pages,
                    'has_oversized': doc.has_oversized,
                    'total_oversized': doc.total_oversized,
                    'total_references': doc.total_references,
                    'is_split': doc.is_split,
                    'roll_count': doc.roll_count,
                    'com_id': doc.com_id,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None,
                    'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
                })
            
            response = HttpResponse(
                json.dumps(documents_data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="documents_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
            
        else:
            return error_response(f"Unsupported export format: {format_type}")
        
    except Exception as e:
        logger.error(f"Error exporting documents: {str(e)}")
        return error_response(f"Error exporting documents: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def batch_import_documents(request):
    """Batch import documents."""
    try:
        data = parse_request_data(request)
        documents_data = data.get('documents', [])
        project_id = data.get('project_id')
        
        if not project_id:
            return error_response("Project ID is required")
        
        project = get_object_or_404(Project, id=project_id)
        
        imported_count = 0
        failed_count = 0
        errors = []
        
        with transaction.atomic():
            for doc_data in documents_data:
                try:
                    # Check if document already exists
                    if Document.objects.filter(project=project, doc_id=doc_data['doc_id']).exists():
                        errors.append(f"Document {doc_data['doc_id']} already exists")
                        failed_count += 1
                        continue
                    
                    # Create document
                    Document.objects.create(
                        project=project,
                        doc_id=doc_data['doc_id'],
                        path=doc_data['path'],
                        com_id=doc_data.get('com_id'),
                        pages=doc_data.get('pages', 0),
                        has_oversized=doc_data.get('has_oversized', False),
                        total_oversized=doc_data.get('total_oversized', 0),
                        total_references=doc_data.get('total_references', 0),
                        is_split=doc_data.get('is_split', False),
                        roll_count=doc_data.get('roll_count', 1)
                    )
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing document {doc_data.get('doc_id', 'unknown')}: {str(e)}")
                    failed_count += 1
        
        return json_response({
            'success': True,
            'message': f'Batch import completed. {imported_count} imported, {failed_count} failed.',
            'imported_count': imported_count,
            'failed_count': failed_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in batch import: {str(e)}")
        return error_response(f"Error in batch import: {str(e)}")

@csrf_exempt
@require_http_methods(["PUT"])
def batch_update_documents(request):
    """Batch update documents."""
    try:
        data = parse_request_data(request)
        documents_data = data.get('documents', [])
        
        updated_count = 0
        failed_count = 0
        errors = []
        
        with transaction.atomic():
            for doc_data in documents_data:
                try:
                    document_id = doc_data.get('id')
                    if not document_id:
                        errors.append("Document ID is required for updates")
                        failed_count += 1
                        continue
                    
                    document = Document.objects.get(id=document_id)
                    
                    # Update fields
                    updatable_fields = [
                        'doc_id', 'path', 'com_id', 'pages', 'has_oversized',
                        'total_oversized', 'total_references', 'is_split', 'roll_count'
                    ]
                    
                    for field in updatable_fields:
                        if field in doc_data:
                            setattr(document, field, doc_data[field])
                    
                    document.save()
                    updated_count += 1
                    
                except Document.DoesNotExist:
                    errors.append(f"Document with ID {document_id} not found")
                    failed_count += 1
                except Exception as e:
                    errors.append(f"Error updating document {document_id}: {str(e)}")
                    failed_count += 1
        
        return json_response({
            'success': True,
            'message': f'Batch update completed. {updated_count} updated, {failed_count} failed.',
            'updated_count': updated_count,
            'failed_count': failed_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        return error_response(f"Error in batch update: {str(e)}")

@csrf_exempt
@require_http_methods(["DELETE"])
def batch_delete_documents(request):
    """Batch delete documents."""
    try:
        data = parse_request_data(request)
        document_ids = data.get('document_ids', [])
        
        if not document_ids:
            return error_response("Document IDs are required")
        
        deleted_count = 0
        failed_count = 0
        errors = []
        
        with transaction.atomic():
            for document_id in document_ids:
                try:
                    document = Document.objects.get(id=document_id)
                    doc_id = document.doc_id
                    document.delete()
                    deleted_count += 1
                    
                except Document.DoesNotExist:
                    errors.append(f"Document with ID {document_id} not found")
                    failed_count += 1
                except Exception as e:
                    errors.append(f"Error deleting document {document_id}: {str(e)}")
                    failed_count += 1
        
        return json_response({
            'success': True,
            'message': f'Batch delete completed. {deleted_count} deleted, {failed_count} failed.',
            'deleted_count': deleted_count,
            'failed_count': failed_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in batch delete: {str(e)}")
        return error_response(f"Error in batch delete: {str(e)}") 