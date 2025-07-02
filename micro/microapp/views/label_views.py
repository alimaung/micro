"""
Label management views for the microapp.
Handles label generation, printing queue, and PDF downloads.
"""

import json
import uuid
import logging
import os
import base64
from pathlib import Path
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from ..models import Roll, Project, FilmType, FilmLabel
from ..services.film_label_generator import FilmLabelGenerator
from ..services.printer_service import printer_service

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
            # Check if label already exists for this roll
            existing_label = FilmLabel.objects.filter(roll=roll).first()
            
            roll_data = {
                'id': roll.id,
                'film_number': roll.film_number,
                'film_type': roll.film_type,
                'project_name': roll.project.name or roll.project.archive_id,
                'archive_id': roll.project.archive_id,
                'doc_type': roll.project.doc_type or 'Document',
                'pages_used': roll.pages_used,
                'development_completed_at': roll.development_completed_at.isoformat() if roll.development_completed_at else None,
                'can_generate_label': bool(roll.film_number and roll.project.archive_id),
                'has_label': existing_label is not None,
                'label_status': existing_label.status if existing_label else None,
                'label_completed': existing_label.is_completed if existing_label else False
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
        generate_both_versions = data.get('generate_both_versions', False)
        
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
        
        with transaction.atomic():
            for roll in rolls:
                try:
                    # Check if labels already exist for this roll
                    existing_labels = FilmLabel.objects.filter(roll=roll)
                    if existing_labels.exists():
                        logger.info(f"Labels already exist for roll {roll.film_number}, skipping")
                        continue
                    
                    # Determine which versions to generate
                    versions_to_generate = ['normal', 'angled'] if generate_both_versions else ['normal']
                    
                    for version in versions_to_generate:
                        # Generate the label PDF for this version
                        pdf_content = generator.create_film_label(
                            film_number=roll.film_number,
                            archive_id=roll.project.archive_id,
                            doc_type=roll.project.doc_type or 'Document',
                            version=version
                        )
                        
                        # Generate a unique label ID
                        label_id = f"label_{uuid.uuid4().hex[:8]}_{version}"
                        
                        # Create labels directory in project path
                        labels_dir = None
                        pdf_file_path = None
                        if roll.project.project_path:
                            labels_dir = Path(roll.project.project_path) / '.labels'
                            labels_dir.mkdir(exist_ok=True)
                            pdf_file_path = labels_dir / f"{roll.film_number}_{label_id}.pdf"
                            
                            # Save PDF to file
                            with open(pdf_file_path, 'wb') as f:
                                f.write(pdf_content)
                            
                            logger.info(f"Saved {version} label PDF to {pdf_file_path}")
                        
                        # Store the PDF content in cache for immediate download (expires in 4 hours)
                        cache_key = f"label_pdf_{label_id}"
                        cache.set(cache_key, pdf_content, 14400)
                        
                        # Create FilmLabel record
                        film_label = FilmLabel.objects.create(
                            roll=roll,
                            project=roll.project,
                            user=request.user,
                            label_id=label_id,
                            version=version,
                            film_number=roll.film_number,
                            archive_id=roll.project.archive_id,
                            doc_type=roll.project.doc_type or 'Document',
                            pdf_path=str(pdf_file_path) if pdf_file_path else None,
                            cache_key=cache_key,
                            status='generated'
                        )
                        
                        generated_labels.append({
                            'label_id': label_id,
                            'roll_id': roll.id,
                            'version': version,
                            'film_number': roll.film_number,
                            'archive_id': roll.project.archive_id,
                            'doc_type': roll.project.doc_type or 'Document',
                            'generated_at': film_label.generated_at.isoformat(),
                            'status': film_label.status,
                            'pdf_saved': pdf_file_path is not None
                        })
                        
                        logger.info(f"Generated {version} label for roll {roll.film_number}")
                    
                except Exception as e:
                    logger.error(f"Error generating labels for roll {roll.id}: {e}")
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
        # Get version from query parameters
        version = request.GET.get('version', 'normal')
        
        # Get the FilmLabel record
        film_label = get_object_or_404(FilmLabel, label_id=label_id)
        
        pdf_content = None
        
        # Try to get from saved file first
        if film_label.pdf_path and os.path.exists(film_label.pdf_path):
            with open(film_label.pdf_path, 'rb') as f:
                pdf_content = f.read()
            logger.info(f"Loaded label PDF from file: {film_label.pdf_path}")
        else:
            # Fallback to cache
            cache_key = f"label_pdf_{label_id}"
            pdf_content = cache.get(cache_key)
            if pdf_content:
                logger.info(f"Loaded label PDF from cache: {cache_key}")
        
        if not pdf_content:
            return JsonResponse({
                'success': False,
                'error': 'Label not found or expired'
            }, status=404)
        
        # Mark as downloaded
        film_label.mark_downloaded()
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="film_label_{film_label.film_number}_{film_label.version}.pdf"'
        
        return response
        
    except FilmLabel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Label not found'
        }, status=404)
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
        # Get labels that are queued for printing
        queued_labels = FilmLabel.objects.filter(
            status='queued'
        ).select_related('roll', 'project').order_by('queued_at')
        
        queue_data = []
        for label in queued_labels:
            queue_data.append({
                'queue_id': f"queue_{label.id}",
                'label_id': label.label_id,
                'film_number': label.film_number,
                'archive_id': label.archive_id,
                'doc_type': label.doc_type,
                'added_at': label.queued_at.isoformat() if label.queued_at else label.generated_at.isoformat(),
                'status': label.status
            })
        
        return JsonResponse({
            'success': True,
            'queue': queue_data,
            'count': len(queue_data)
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
        
        # Get the labels and mark them as queued
        labels = FilmLabel.objects.filter(label_id__in=label_ids)
        
        queued_count = 0
        for label in labels:
            if label.status in ['generated', 'downloaded']:
                label.mark_queued()
                queued_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Added {queued_count} labels to print queue',
            'queue_count': FilmLabel.objects.filter(status='queued').count()
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
        # Extract label ID from queue_id (format: "queue_{label.id}")
        if queue_id.startswith('queue_'):
            label_db_id = queue_id.replace('queue_', '')
            label = get_object_or_404(FilmLabel, id=label_db_id)
            
            # Reset status to downloaded or generated
            if label.downloaded_at:
                label.status = 'downloaded'
            else:
                label.status = 'generated'
            label.queued_at = None
            label.save(update_fields=['status', 'queued_at'])
            
            return JsonResponse({
                'success': True,
                'message': 'Label removed from print queue',
                'queue_count': FilmLabel.objects.filter(status='queued').count()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid queue ID format'
            }, status=400)
        
    except FilmLabel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Label not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error removing from print queue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mark_label_printed(request, label_id):
    """
    Mark a label as printed.
    """
    try:
        film_label = get_object_or_404(FilmLabel, label_id=label_id)
        film_label.mark_printed()
        
        return JsonResponse({
            'success': True,
            'message': f'Label {label_id} marked as printed',
            'status': film_label.status
        })
        
    except FilmLabel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Label not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error marking label as printed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_generated_labels(request):
    """
    Get all generated labels with their current status.
    """
    try:
        labels = FilmLabel.objects.select_related(
            'roll', 'project'
        ).order_by('-generated_at')[:50]  # Limit to recent 50 labels
        
        labels_data = []
        for label in labels:
            labels_data.append({
                'label_id': label.label_id,
                'roll_id': label.roll.id,
                'version': label.version,
                'film_number': label.film_number,
                'archive_id': label.archive_id,
                'doc_type': label.doc_type,
                'status': label.status,
                'generated_at': label.generated_at.isoformat(),
                'downloaded_at': label.downloaded_at.isoformat() if label.downloaded_at else None,
                'printed_at': label.printed_at.isoformat() if label.printed_at else None,
                'download_count': label.download_count,
                'print_count': label.print_count,
                'is_completed': label.is_completed,
                'pdf_saved': bool(label.pdf_path and os.path.exists(label.pdf_path)) if label.pdf_path else False
            })
        
        return JsonResponse({
            'success': True,
            'labels': labels_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching generated labels: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def print_label_server_side(request, label_id):
    """
    Print a label using server-side printing (no user interaction required).
    """
    try:
        data = json.loads(request.body) if request.body else {}
        printer_name = data.get('printer_name')  # Optional: specify printer
        copies = data.get('copies', 1)
        
        # Get version from query parameters
        version = request.GET.get('version', 'normal')
        
        # Get the FilmLabel record
        film_label = get_object_or_404(FilmLabel, label_id=label_id)
        
        pdf_content = None
        
        # Try to get from saved file first
        if film_label.pdf_path and os.path.exists(film_label.pdf_path):
            with open(film_label.pdf_path, 'rb') as f:
                pdf_content = f.read()
            logger.info(f"Loaded label PDF from file: {film_label.pdf_path}")
        else:
            # Fallback to cache
            cache_key = f"label_pdf_{label_id}"
            pdf_content = cache.get(cache_key)
            if pdf_content:
                logger.info(f"Loaded label PDF from cache: {cache_key}")
        
        if not pdf_content:
            return JsonResponse({
                'success': False,
                'error': 'Label not found or expired'
            }, status=404)
        
        # Print using the printer service
        print_result = printer_service.print_pdf(
            pdf_content=pdf_content,
            printer_name=printer_name,
            copies=copies
        )
        
        if print_result['success']:
            # Mark as printed
            film_label.mark_printed()
            
            return JsonResponse({
                'success': True,
                'message': print_result['message'],
                'method': print_result.get('method'),
                'printer': printer_name or printer_service.default_printer,
                'copies': copies,
                'status': film_label.status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': print_result['error']
            }, status=500)
        
    except FilmLabel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Label not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error printing label server-side: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_printer_status(request):
    """
    Get the current printer status and available printers.
    """
    try:
        status = printer_service.get_printer_status()
        return JsonResponse({
            'success': True,
            'printer_status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting printer status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def print_multiple_labels(request):
    """
    Print multiple labels in batch using server-side printing.
    """
    try:
        data = json.loads(request.body)
        label_ids = data.get('label_ids', [])
        printer_name = data.get('printer_name')
        copies = data.get('copies', 1)
        
        if not label_ids:
            return JsonResponse({
                'success': False,
                'error': 'No labels specified'
            }, status=400)
        
        results = []
        successful_prints = 0
        
        for label_id in label_ids:
            try:
                # Get the FilmLabel record
                film_label = FilmLabel.objects.get(label_id=label_id)
                
                pdf_content = None
                
                # Try to get from saved file first
                if film_label.pdf_path and os.path.exists(film_label.pdf_path):
                    with open(film_label.pdf_path, 'rb') as f:
                        pdf_content = f.read()
                else:
                    # Fallback to cache
                    cache_key = f"label_pdf_{label_id}"
                    pdf_content = cache.get(cache_key)
                
                if not pdf_content:
                    results.append({
                        'label_id': label_id,
                        'success': False,
                        'error': 'Label not found or expired'
                    })
                    continue
                
                # Print using the printer service
                print_result = printer_service.print_pdf(
                    pdf_content=pdf_content,
                    printer_name=printer_name,
                    copies=copies
                )
                
                if print_result['success']:
                    # Mark as printed
                    film_label.mark_printed()
                    successful_prints += 1
                    
                    results.append({
                        'label_id': label_id,
                        'success': True,
                        'message': print_result['message'],
                        'method': print_result.get('method')
                    })
                else:
                    results.append({
                        'label_id': label_id,
                        'success': False,
                        'error': print_result['error']
                    })
                
            except FilmLabel.DoesNotExist:
                results.append({
                    'label_id': label_id,
                    'success': False,
                    'error': 'Label not found'
                })
            except Exception as e:
                results.append({
                    'label_id': label_id,
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'message': f'Printed {successful_prints} of {len(label_ids)} labels successfully',
            'successful_prints': successful_prints,
            'total_labels': len(label_ids),
            'results': results,
            'printer': printer_name or printer_service.default_printer
        })
        
    except Exception as e:
        logger.error(f"Error printing multiple labels: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def reveal_label_in_explorer(request, label_id):
    """
    Reveal a label PDF file in Windows Explorer.
    """
    try:
        # Get the FilmLabel record
        film_label = get_object_or_404(FilmLabel, label_id=label_id)
        
        # Check if the PDF file exists on disk
        if not film_label.pdf_path or not os.path.exists(film_label.pdf_path):
            return JsonResponse({
                'success': False,
                'error': 'Label file not found on disk. It may only exist in cache.'
            }, status=404)
        
        # Use subprocess to open Windows Explorer and select the file
        import subprocess
        subprocess.Popen(['explorer', '/select,', film_label.pdf_path])
        
        return JsonResponse({
            'success': True,
            'message': f'Revealed label file in Explorer: {film_label.pdf_path}'
        })
        
    except FilmLabel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Label not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error revealing label in explorer: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_custom_film_labels(request):
    """
    Generate custom film labels based on user input parameters.
    This endpoint doesn't create database records, just generates PDFs.
    """
    try:
        data = json.loads(request.body)
        archive_id = data.get('archive_id')
        film_number = data.get('film_number')
        doc_type = data.get('doc_type')
        
        # Validate required parameters
        if not archive_id or not film_number or not doc_type:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters (archive_id, film_number, doc_type)'
            }, status=400)
        
        # Validate format of film number (should start with 1 or 3 and have 8 digits, or be 6 digits)
        if not ((len(film_number) == 8 and (film_number.startswith('1') or film_number.startswith('3'))) or 
                (len(film_number) == 6 and film_number.isdigit())):
            return JsonResponse({
                'success': False,
                'error': 'Film number must be either 8 digits starting with 1 or 3, or 6 digits'
            }, status=400)
        
        # Initialize the label generator
        generator = FilmLabelGenerator()
        
        # Generate labels for both versions
        labels = {}
        for version in ['normal', 'angled']:
            # Generate the label PDF
            pdf_content = generator.create_film_label(
                film_number=film_number,
                archive_id=archive_id,
                doc_type=doc_type,
                version=version
            )
            
            # Generate a unique label ID for this custom label
            label_id = f"custom_label_{uuid.uuid4().hex[:8]}_{version}"
            
            # Store the PDF content in cache for immediate access (expires in 1 hour)
            cache_key = f"custom_label_pdf_{label_id}"
            cache.set(cache_key, pdf_content, 3600)  # 1 hour expiration
            
            # Convert PDF content to base64 for sending in response
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            labels[version] = {
                'label_id': label_id,
                'cache_key': cache_key,
                'content': pdf_base64,
                'version': version
            }
            
            logger.info(f"Generated custom {version} label for {archive_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Generated custom labels successfully',
            'labels': labels
        })
        
    except Exception as e:
        logger.error(f"Error generating custom labels: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def print_custom_label(request):
    """
    Print a custom label directly from provided PDF data.
    """
    try:
        data = json.loads(request.body)
        label_data_base64 = data.get('label_data')
        version = data.get('version', 'normal')
        
        if not label_data_base64:
            return JsonResponse({
                'success': False,
                'error': 'Missing label data'
            }, status=400)
        
        # Convert base64 back to binary
        try:
            pdf_content = base64.b64decode(label_data_base64)
        except Exception as e:
            logger.error(f"Error decoding base64 data: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid label data format'
            }, status=400)
        
        # Create a temporary file for printing
        temp_file_path = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tmp', f'custom_label_{uuid.uuid4().hex[:8]}.pdf'))
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        
        with open(temp_file_path, 'wb') as f:
            f.write(pdf_content)
        
        # Print the PDF
        print_result = printer_service.print_pdf(temp_file_path)
        
        # Clean up the temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {temp_file_path}: {e}")
        
        if print_result.get('success'):
            return JsonResponse({
                'success': True,
                'message': f'Custom {version} label sent to printer',
                'printer': print_result.get('printer', 'Default'),
                'method': print_result.get('method', 'Direct')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': print_result.get('error', 'Unknown printing error')
            }, status=500)
        
    except Exception as e:
        logger.error(f"Error printing custom label: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 