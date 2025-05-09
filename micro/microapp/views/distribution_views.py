"""
Views for document distribution in microfilm processing.

These views handle the distribution of documents to roll directories based on film allocation.
"""

import json
import logging
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from microapp.models import Project, DistributionResult
from microapp.services.distribution_manager import DistributionManager
from microapp.services.reference_manager import ReferenceManager

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def distribution_status(request, project_id):
    """
    Get the status of document distribution for a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with distribution status
    """
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    try:
        # Check if distribution has been done
        if hasattr(project, 'distribution_result'):
            result = project.distribution_result
            response = {
                "status": "success",
                "distributionComplete": True,
                "results": {
                    "processed_count": result.processed_count,
                    "error_count": result.error_count,
                    "reference_sheets": result.reference_sheets,
                    "documents_with_references": result.documents_with_references,
                    "oversized_documents_extracted": result.oversized_documents_extracted,
                    "processed_35mm_documents": result.processed_35mm_documents,
                    "copied_35mm_documents": result.copied_35mm_documents,
                    "processed_16mm_documents": result.processed_16mm_documents,
                    "copied_16mm_documents": result.copied_16mm_documents,
                    "output_dir": result.output_dir,
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                }
            }
        else:
            response = {
                "status": "success", 
                "distributionComplete": False,
                "message": "Distribution has not been performed yet"
            }
            
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error getting distribution status: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def distribute_documents(request, project_id):
    """
    Distribute documents for a project based on film allocation.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with distribution results
    """
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    # Check if film allocation has been done
    if not project.film_allocation_complete:
        return JsonResponse({
            "status": "error", 
            "message": "Film allocation must be completed before distributing documents"
        }, status=400)
    
    try:
        # Parse JSON payload
        try:
            payload = json.loads(request.body)
            logger.info(f"Received payload: {type(payload)}")
        except Exception as e:
            logger.error(f"Failed to parse JSON payload: {str(e)}")
            payload = {}
        
        # Initialize services
        distribution_manager = DistributionManager()
        
        # Extract data from payload
        project_data = payload.get('projectData')
        allocation_data = payload.get('allocationData')
        reference_data = payload.get('referenceData')
        film_number_data = payload.get('filmNumberData')
        
        # Log received data
        logger.info(f"Distributing documents for project {project_id}")
        logger.info(f"Project data received: {project_data is not None}")
        logger.info(f"Allocation data received: {allocation_data is not None}")
        logger.info(f"Reference data received: {reference_data is not None}")
        logger.info(f"Film number data received: {film_number_data is not None}")
        
        # Always use the frontend data distribution method
        results = distribution_manager.distribute_documents_with_frontend_data(
            project_id, 
            project_data=project_data,
            allocation_data=allocation_data, 
            reference_data=reference_data, 
            film_number_data=film_number_data
        )
        
        # Check results
        if results.get('status') == 'error':
            return JsonResponse({
                "status": "error", 
                "message": results.get('message', 'Distribution failed')
            }, status=500)
        
        return JsonResponse({
            "status": "success",
            "message": "Distribution completed successfully",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error distributing documents: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def generate_reference_sheets(request, project_id):
    """
    Generate reference sheets for a project without distributing documents.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with reference sheet generation results
    """
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    try:
        # Parse JSON payload
        try:
            payload = json.loads(request.body)
        except Exception:
            payload = {}
        
        # Initialize reference manager
        reference_manager = ReferenceManager()
        
        # Extract data from payload
        project_data = payload.get('projectData')
        analysis_data = payload.get('analysisData')
        allocation_data = payload.get('allocationData')
        film_number_results = payload.get('filmNumberResults')
        
        # Generate reference sheets
        if all([project_data, analysis_data, allocation_data, film_number_results]):
            # Use frontend data if all required data is present
            results = reference_manager.generate_reference_sheets_with_frontend_data(
                project_id, project_data, analysis_data, allocation_data, film_number_results
            )
        else:
            # Use database data if frontend data is missing
            results = reference_manager.generate_reference_sheets(project_id)
        
        return JsonResponse({
            "status": "success",
            "reference_sheets": results
        })
        
    except Exception as e:
        logger.error(f"Error generating reference sheets: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

