import json
import logging
from pathlib import Path
import base64
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings

from microapp.models import (
    Project, Document, DocumentRange, ReferenceSheet, 
    ReadablePageDescription, AdjustedRange, ProcessedDocument
)
from microapp.services.reference_manager import ReferenceManager
from microapp.services.film_number_manager import FilmNumberManager

logger = logging.getLogger(__name__)

@require_GET
def reference_sheet_status(request, project_id):
    """
    Get the reference sheet status for a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with reference sheet status data
    """
    project = get_object_or_404(Project, pk=project_id)
    
    # Check if the project has any documents with oversized pages
    has_oversized = project.has_oversized
    
    # Count existing reference sheets
    reference_sheet_count = ReferenceSheet.objects.filter(
        document__project=project
    ).count()
    
    # Count documents with reference sheets
    documents_with_references = Document.objects.filter(
        project=project,
        reference_sheets__isnull=False
    ).distinct().count()
    
    # Get total oversized documents
    total_oversized_documents = Document.objects.filter(
        project=project,
        has_oversized=True
    ).count()
    
    response_data = {
        "has_oversized": has_oversized,
        "reference_sheet_count": reference_sheet_count,
        "documents_with_references": documents_with_references,
        "total_oversized_documents": total_oversized_documents,
        "status": "completed" if reference_sheet_count > 0 else "pending"
    }
    
    return JsonResponse(response_data)

@require_POST
@csrf_exempt
def generate_reference_sheets(request, project_id):
    """
    Generate reference sheets for all documents in a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with generation results
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # If the project has no oversized documents, return early
        if not project.has_oversized:
            return JsonResponse({
                "status": "skipped",
                "message": "No oversized documents found",
                "reference_sheets": {},
                "sheets_created": 0
            })
        
        # Check if we have frontend data in the request
        use_frontend_data = False
        frontend_data = None
        
        try:
            # Attempt to parse request body as JSON
            if request.body:
                frontend_data = json.loads(request.body)
                use_frontend_data = True
                logger.info("Using frontend data for reference sheet generation")
        except json.JSONDecodeError:
            # If parsing fails, proceed with database approach
            logger.info("No valid frontend data found, using database approach")
        
        # Initialize the reference manager
        film_number_manager = FilmNumberManager()
        reference_manager = ReferenceManager(film_number_manager=film_number_manager)
        
        # Generate reference sheets
        if use_frontend_data:
            # Use data from frontend
            reference_response = reference_manager.generate_reference_sheets_with_frontend_data(
                project_id, 
                frontend_data.get('projectData'),
                frontend_data.get('analysisData'),
                frontend_data.get('allocationData'),
                frontend_data.get('filmNumberResults')
            )
        else:
            # Use database approach
            reference_response = reference_manager.generate_reference_sheets(project_id)
        
        # Handle both response formats (new detailed structure or legacy dictionary)
        if isinstance(reference_response, dict) and 'reference_sheets' in reference_response:
            # New detailed response format
            reference_sheets = reference_response['reference_sheets']
            sheets_created = reference_response['statistics']['total_sheets']
            documents_details = reference_response.get('documents_details', {})
            timestamp = reference_response.get('timestamp')
        else:
            # Legacy response format (just the reference_sheets dictionary)
            reference_sheets = reference_response
            sheets_created = sum(len(sheets) for sheets in reference_sheets.values())
            documents_details = {}
            timestamp = datetime.datetime.now().isoformat()
        
        # Enhanced response with more details
        response = {
            "status": "success",
            "message": f"Generated {sheets_created} reference sheets for {len(reference_sheets)} documents",
            "reference_sheets": {k: [{"range": v["range"], "id": v["id"]} for v in vals] for k, vals in reference_sheets.items()},
            "sheets_created": sheets_created,
            "timestamp": timestamp
        }
        
        # Include additional details if available
        if documents_details:
            response["documents_details"] = documents_details
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error generating reference sheets: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_GET
def get_reference_sheets(request, project_id):
    """
    Get all reference sheets for a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with reference sheet data
    """
    project = get_object_or_404(Project, pk=project_id)
    
    # Get reference sheets grouped by document
    reference_sheets = {}
    
    # Get all reference sheets for the project
    sheets = ReferenceSheet.objects.filter(
        document__project=project
    ).select_related('document', 'document_range')
    
    # Group by document ID
    for sheet in sheets:
        doc_id = sheet.document.doc_id
        if doc_id not in reference_sheets:
            reference_sheets[doc_id] = []
        
        reference_sheets[doc_id].append({
            "id": sheet.id,
            "range": (sheet.range_start, sheet.range_end),
            "blip_35mm": sheet.blip_35mm,
            "film_number_35mm": sheet.film_number_35mm,
            "path": sheet.path,
            "human_range": sheet.human_range
        })
    
    return JsonResponse({
        "status": "success",
        "reference_sheets": reference_sheets
    })

@require_GET
def get_reference_sheet_pdf(request, reference_sheet_id):
    """
    Get a reference sheet PDF as a base64-encoded string.
    
    Args:
        request: HTTP request
        reference_sheet_id: ID of the reference sheet
        
    Returns:
        JSON response with base64-encoded PDF data
    """
    reference_sheet = get_object_or_404(ReferenceSheet, pk=reference_sheet_id)
    
    # Validate the path
    path = Path(reference_sheet.path)
    if not path.exists():
        return JsonResponse({
            "status": "error",
            "message": "Reference sheet file not found"
        }, status=404)
    
    # Read the PDF file
    try:
        with open(path, "rb") as f:
            pdf_data = f.read()
        
        # Encode as base64
        pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
        
        return JsonResponse({
            "status": "success",
            "pdf_data": pdf_base64,
            "reference_sheet": {
                "id": reference_sheet.id,
                "document_id": reference_sheet.document.doc_id,
                "range": (reference_sheet.range_start, reference_sheet.range_end),
                "blip_35mm": reference_sheet.blip_35mm,
                "film_number_35mm": reference_sheet.film_number_35mm,
                "human_range": reference_sheet.human_range
            }
        })
    except Exception as e:
        logger.error(f"Error reading reference sheet PDF: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_POST
@csrf_exempt
def insert_reference_sheets(request, project_id, document_id):
    """
    Insert reference sheets into a document.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        document_id: ID of the document
        
    Returns:
        JSON response with insertion results
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        document = get_object_or_404(Document, project=project, doc_id=document_id)
        
        # Parse request data
        try:
            data = json.loads(request.body)
            is_35mm = data.get('is_35mm', False)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data"
            }, status=400)
        
        # Initialize the reference manager
        reference_manager = ReferenceManager()
        
        # Use high-level method to prepare document
        result = reference_manager.prepare_document_for_distribution(
            project_id=project_id,
            document_id=document_id,
            is_35mm=is_35mm
        )
        
        if result.get('processed', False):
            return JsonResponse({
                "status": "success",
                "message": f"Successfully processed document {document_id}",
                "result": result
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": f"Failed to process document: {result.get('reason', 'unknown error')}",
                "result": result
            }, status=400)
        
    except Exception as e:
        logger.error(f"Error inserting reference sheets: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_GET
def get_document_ranges(request, project_id, document_id):
    """
    Get all ranges for a document.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        document_id: ID of the document
        
    Returns:
        JSON response with document range data
    """
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, project=project, doc_id=document_id)
    
    # Get all ranges for the document
    ranges = DocumentRange.objects.filter(document=document).order_by('start_page')
    
    # Format the ranges
    range_data = []
    for range_obj in ranges:
        range_data.append({
            "id": range_obj.id,
            "start_page": range_obj.start_page,
            "end_page": range_obj.end_page
        })
    
    # Get human-readable descriptions if available
    readable_descriptions = ReadablePageDescription.objects.filter(document=document).order_by('range_index')
    
    descriptions = []
    for desc in readable_descriptions:
        descriptions.append({
            "range_index": desc.range_index,
            "description": desc.description
        })
    
    return JsonResponse({
        "status": "success",
        "document_id": document_id,
        "ranges": range_data,
        "readable_descriptions": descriptions
    })

@require_POST
@csrf_exempt
def generate_readable_descriptions(request, project_id, document_id):
    """
    Generate human-readable page descriptions for a document.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        document_id: ID of the document
        
    Returns:
        JSON response with generated descriptions
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        document = get_object_or_404(Document, project=project, doc_id=document_id)
        
        # Initialize the reference manager
        reference_manager = ReferenceManager()
        
        # Generate readable descriptions
        readable_pages = reference_manager.generate_readable_pages(document)
        
        return JsonResponse({
            "status": "success",
            "document_id": document_id,
            "readable_pages": readable_pages
        })
        
    except Exception as e:
        logger.error(f"Error generating readable descriptions: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_POST
@csrf_exempt
def calculate_adjusted_ranges(request, project_id, document_id):
    """
    Calculate adjusted page ranges for a document.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        document_id: ID of the document
        
    Returns:
        JSON response with calculated ranges
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        document = get_object_or_404(Document, project=project, doc_id=document_id)
        
        # Initialize the reference manager
        reference_manager = ReferenceManager()
        
        # Calculate adjusted ranges
        adjusted_ranges = reference_manager.calculate_adjusted_ranges(document)
        
        # Format the response
        formatted_ranges = []
        for i, (adjusted_start, adjusted_end) in enumerate(adjusted_ranges):
            # Get original range
            original_ranges = DocumentRange.objects.filter(document=document).order_by('start_page')
            if i < len(original_ranges):
                original_start = original_ranges[i].start_page
                original_end = original_ranges[i].end_page
                
                formatted_ranges.append({
                    "original": [original_start, original_end],
                    "adjusted": [adjusted_start, adjusted_end]
                })
        
        return JsonResponse({
            "status": "success",
            "document_id": document_id,
            "adjusted_ranges": formatted_ranges
        })
        
    except Exception as e:
        logger.error(f"Error calculating adjusted ranges: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_GET
def get_processed_documents(request, project_id):
    """
    Get all processed documents for a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with processed document data
    """
    project = get_object_or_404(Project, pk=project_id)
    
    # Get all processed documents for the project
    processed_docs = ProcessedDocument.objects.filter(
        document__project=project
    ).select_related('document')
    
    # Format the response
    processed_data = []
    for proc_doc in processed_docs:
        processed_data.append({
            "id": proc_doc.id,
            "document_id": proc_doc.document.doc_id,
            "path": proc_doc.path,
            "processing_type": proc_doc.processing_type,
            "start_page": proc_doc.start_page,
            "end_page": proc_doc.end_page,
            "copied_to_output": proc_doc.copied_to_output,
            "output_path": proc_doc.output_path,
            "processed_at": proc_doc.processed_at.isoformat()
        })
    
    return JsonResponse({
        "status": "success",
        "processed_documents": processed_data
    })

@require_POST
@csrf_exempt
def copy_to_output(request, project_id):
    """
    Copy processed documents to the output directory.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with copy results
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # Parse request data
        try:
            data = json.loads(request.body)
            document_ids = data.get('document_ids', [])
            output_dir = data.get('output_dir')
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data"
            }, status=400)
        
        # Initialize the reference manager
        reference_manager = ReferenceManager()
        
        # Process each document
        results = []
        successful_copies = 0
        
        for doc_id in document_ids:
            # Get the document
            document = Document.objects.filter(project=project, doc_id=doc_id).first()
            if not document:
                results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "message": "Document not found"
                })
                continue
            
            # Get the latest processed document
            processed_doc = ProcessedDocument.objects.filter(
                document=document
            ).order_by('-processed_at').first()
            
            if not processed_doc:
                results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "message": "No processed document found"
                })
                continue
            
            # Copy to output
            success = reference_manager.copy_to_output(
                source_path=processed_doc.path,
                destination_dir=output_dir or project.output_dir,
                doc_id=doc_id
            )
            
            if success:
                successful_copies += 1
                results.append({
                    "document_id": doc_id,
                    "status": "success",
                    "message": "Copied to output directory"
                })
            else:
                results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "message": "Failed to copy to output directory"
                })
        
        return JsonResponse({
            "status": "success",
            "message": f"Copied {successful_copies} of {len(document_ids)} documents to output directory",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error copying to output: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_POST
@csrf_exempt
def clean_temporary_files(request, project_id):
    """
    Clean up temporary files for a project.
    
    Args:
        request: HTTP request
        project_id: ID of the project
        
    Returns:
        JSON response with cleanup results
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # Initialize the reference manager
        reference_manager = ReferenceManager()
        
        # Clean temporary files
        cleaned_count = reference_manager.clean_temporary_files(project_id)
        
        return JsonResponse({
            "status": "success",
            "message": f"Marked {cleaned_count} temporary files as cleaned",
            "cleaned_count": cleaned_count
        })
        
    except Exception as e:
        logger.error(f"Error cleaning temporary files: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
