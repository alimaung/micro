"""
Label management views for the microapp.
Handles label generation, printing queue, and PDF downloads.
"""

import json
import uuid
import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from ..models import Roll, Project, FilmType
from ..services.film_label_generator import FilmLabelGenerator

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def get_rolls_for_labels(request):
    """
    Get rolls that are available for label generation.
    """
    try:
        # Get rolls that have been developed (ready for labeling)
        rolls = Roll.objects.filter(
            development_status='completed',
            film_number__isnull=False
        ).select_related('project').order_by('-development_completed_at')
        
        rolls_data = []
        for roll in rolls:
            roll_data = {
                'id': roll.id,
                'film_number': roll.film_number,
                'film_type': roll.film_type,
                'project_name': roll.project.name or roll.project.archive_id,
                'archive_id': roll.project.archive_id,
                'doc_type': roll.project.doc_type or 'Document',
                'pages_used': roll.pages_used,
                'development_completed_at': roll.development_completed_at.isoformat() if roll.development_completed_at else None,
                'can_generate_label': bool(roll.film_number and roll.project.archive_id)
            }
            rolls_data.append(roll_data)
        
        return JsonResponse({
            'success': True,
            'rolls': rolls_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching rolls for labels: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_film_labels(request):
    """
    Generate film labels for selected rolls.
    """
    try:
        data = json.loads(request.body)
        roll_ids = data.get('roll_ids', [])
        
        if not roll_ids:
            return JsonResponse({
                'success': False,
                'error': 'No rolls selected for label generation'
            }, status=400)
        
        # Get the selected rolls
        rolls = Roll.objects.filter(
            id__in=roll_ids,
            development_status='completed',
            film_number__isnull=False
        ).select_related('project')
        
        if not rolls.exists():
            return JsonResponse({
                'success': False,
                'error': 'No valid rolls found for label generation'
            }, status=400)
        
        # Initialize the label generator
        generator = FilmLabelGenerator()
        
        generated_labels = []
        
        for roll in rolls:
            try:
                # Generate the label PDF
                pdf_content = generator.create_film_label(
                    film_number=roll.film_number,
                    archive_id=roll.project.archive_id,
                    doc_type=roll.project.doc_type or 'Document'
                )
                
                # Generate a unique label ID
                label_id = f"label_{uuid.uuid4().hex[:8]}"
                
                # Store the PDF content in cache for download (expires in 4 hours)
                cache_key = f"label_pdf_{label_id}"
                cache.set(cache_key, pdf_content, 14400)
                
                generated_labels.append({
                    'label_id': label_id,
                    'roll_id': roll.id,
                    'film_number': roll.film_number,
                    'archive_id': roll.project.archive_id,
                    'doc_type': roll.project.doc_type or 'Document',
                    'generated_at': timezone.now().isoformat()
                })
                
                logger.info(f"Generated label for roll {roll.film_number}")
                
            except Exception as e:
                logger.error(f"Error generating label for roll {roll.id}: {e}")
                continue
        
        if not generated_labels:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate any labels'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': f'Generated {len(generated_labels)} labels successfully',
            'labels': generated_labels
        })
        
    except Exception as e:
        logger.error(f"Error in label generation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def download_label_pdf(request, label_id):
    """
    Download a generated label PDF.
    """
    try:
        # Get the PDF content from cache
        cache_key = f"label_pdf_{label_id}"
        pdf_content = cache.get(cache_key)
        
        if not pdf_content:
            return JsonResponse({
                'success': False,
                'error': 'Label not found or expired'
            }, status=404)
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="film_label_{label_id}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error downloading label PDF: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_print_queue(request):
    """
    Get the current print queue for labels.
    """
    try:
        # Get print queue from cache
        print_queue = cache.get('label_print_queue', [])
        
        return JsonResponse({
            'success': True,
            'queue': print_queue,
            'count': len(print_queue)
        })
        
    except Exception as e:
        logger.error(f"Error fetching print queue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_to_print_queue(request):
    """
    Add labels to the print queue.
    """
    try:
        data = json.loads(request.body)
        label_ids = data.get('label_ids', [])
        
        if not label_ids:
            return JsonResponse({
                'success': False,
                'error': 'No labels specified'
            }, status=400)
        
        # Get current print queue
        print_queue = cache.get('label_print_queue', [])
        
        # Add new labels to queue
        for label_id in label_ids:
            # Check if label exists in cache
            cache_key = f"label_pdf_{label_id}"
            if cache.get(cache_key):
                queue_item = {
                    'queue_id': f"queue_{uuid.uuid4().hex[:8]}",
                    'label_id': label_id,
                    'added_at': timezone.now().isoformat(),
                    'status': 'pending'
                }
                print_queue.append(queue_item)
        
        # Update cache
        cache.set('label_print_queue', print_queue, 14400)
        
        return JsonResponse({
            'success': True,
            'message': f'Added {len(label_ids)} labels to print queue',
            'queue_count': len(print_queue)
        })
        
    except Exception as e:
        logger.error(f"Error adding to print queue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def remove_from_print_queue(request, queue_id):
    """
    Remove a label from the print queue.
    """
    try:
        # Get current print queue
        print_queue = cache.get('label_print_queue', [])
        
        # Remove the specified item
        print_queue = [item for item in print_queue if item['queue_id'] != queue_id]
        
        # Update cache
        cache.set('label_print_queue', print_queue, 14400)
        
        return JsonResponse({
            'success': True,
            'message': 'Label removed from print queue',
            'queue_count': len(print_queue)
        })
        
    except Exception as e:
        logger.error(f"Error removing from print queue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 