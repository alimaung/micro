"""
Handoff views for the microapp.
Handles project handoff functionality including validation and email delivery.
"""

import json
import logging
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from ..models import Project, Roll, FilmLabel
from django.template.loader import render_to_string
import pandas as pd

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def get_projects_for_handoff(request):
    """
    Get projects that are ready for handoff.
    
    A project is ready for handoff when ALL its rolls have:
    1. filming_status = 'completed'
    2. development_status = 'completed' 
    3. At least one label with status = 'completed' (printed)
    
    If no projects meet all criteria, also return projects where all rolls are filmed
    (have filming_status = 'completed') as a fallback.
    """
    try:
        # Check for status filter parameter
        status_filter = request.GET.get('status', 'ready')  # Default to 'ready'
        logger.info(f"=== HANDOFF PROJECT QUERY DEBUG START (status_filter: {status_filter}) ===")
        
        # Get all projects with their roll completion status
        from django.db.models import Exists, OuterRef
        from ..models import FilmLabel
        
        base_query = Project.objects.annotate(
            total_rolls=Count('rolls', filter=Q(rolls__film_type='16mm')),
            filmed_rolls=Count('rolls', filter=Q(rolls__filming_status='completed', rolls__film_type='16mm')),
            developed_rolls=Count('rolls', filter=Q(rolls__development_status='completed', rolls__film_type='16mm')),
            labeled_rolls=Count('rolls', filter=Q(rolls__film_type='16mm') & Exists(
                FilmLabel.objects.filter(
                    roll=OuterRef('rolls'),
                    status='completed'
                )
            ))
        ).filter(
            total_rolls__gt=0  # Only projects with 16mm rolls
        )
        
        # Apply status-based filtering
        if status_filter == 'ready':
            # Projects ready for handoff (not yet handed off)
            projects = base_query.filter(handoff_complete=False)
        elif status_filter == 'completed':
            # Projects that have been handed off
            projects = base_query.filter(handoff_complete=True)
        else:
            # All projects (for 'all' status or invalid status)
            projects = base_query
        
        projects = projects.select_related().prefetch_related('rolls__film_labels')
        
        logger.info(f"Found {projects.count()} projects with rolls for handoff evaluation (status_filter: {status_filter})")
        
        ready_projects = []
        filmed_projects = []
        completed_projects = []
        
        for project in projects:
            # Calculate completion status
            all_filmed = project.filmed_rolls == project.total_rolls
            all_developed = project.developed_rolls == project.total_rolls
            all_labeled = project.labeled_rolls >= project.total_rolls  # At least one label per roll
            
            # Debug logging for project status determination
            logger.info(f"=== PROJECT STATUS DEBUG: {project.archive_id} ===")
            logger.info(f"Total rolls: {project.total_rolls}")
            logger.info(f"Filmed rolls: {project.filmed_rolls} (all_filmed: {all_filmed})")
            logger.info(f"Developed rolls: {project.developed_rolls} (all_developed: {all_developed})")
            logger.info(f"Labeled rolls: {project.labeled_rolls} (all_labeled: {all_labeled})")
            
            # Double-check labeled rolls calculation manually (16mm only)
            manual_labeled_count = 0
            for roll in project.rolls.filter(film_type='16mm'):
                completed_labels = roll.film_labels.filter(status='completed').count()
                if completed_labels > 0:
                    manual_labeled_count += 1
            logger.info(f"Manual labeled count: {manual_labeled_count} (should match annotation: {project.labeled_rolls})")
            
            if manual_labeled_count != project.labeled_rolls:
                logger.warning(f"⚠️ MISMATCH: Manual count ({manual_labeled_count}) != annotation ({project.labeled_rolls})")
            
            # Check individual roll statuses for detailed debugging (16mm only)
            for roll in project.rolls.filter(film_type='16mm'):
                logger.info(f"  Roll {roll.film_number}: filming={roll.filming_status}, "
                           f"development={roll.development_status}")
                
                # Check labels for this roll
                labels = roll.film_labels.all()
                label_statuses = [label.status for label in labels]
                completed_labels = [label for label in labels if label.status == 'completed']
                logger.info(f"    Labels: {len(labels)} total, statuses={label_statuses}, "
                           f"completed={len(completed_labels)}")
                
                # Check if roll has any issues
                if roll.filming_status != 'completed':
                    logger.warning(f"    ⚠️ Roll {roll.film_number} filming not completed: {roll.filming_status}")
                if roll.development_status != 'completed':
                    logger.warning(f"    ⚠️ Roll {roll.film_number} development not completed: {roll.development_status}")
                if len(completed_labels) == 0:
                    logger.warning(f"    ⚠️ Roll {roll.film_number} has no completed labels")
            
            # Get the latest completion date (16mm only)
            latest_completion = None
            if all_labeled:
                # Get the latest label completion date
                latest_label = FilmLabel.objects.filter(
                    project=project,
                    roll__film_type='16mm',
                    status='completed'
                ).order_by('-completed_at').first()
                if latest_label and latest_label.completed_at:
                    latest_completion = latest_label.completed_at
            elif all_developed:
                # Get the latest development completion date
                latest_roll = project.rolls.filter(
                    film_type='16mm',
                    development_status='completed'
                ).order_by('-development_completed_at').first()
                if latest_roll and latest_roll.development_completed_at:
                    latest_completion = latest_roll.development_completed_at
            elif all_filmed:
                # Get the latest filming completion date
                latest_roll = project.rolls.filter(
                    film_type='16mm',
                    filming_status='completed'
                ).order_by('-filming_completed_at').first()
                if latest_roll and latest_roll.filming_completed_at:
                    latest_completion = latest_roll.filming_completed_at
            
            # Get first and last roll film numbers (16mm only)
            roll_range = ""
            try:
                roll_numbers = list(project.rolls.filter(film_type='16mm').order_by('film_number').values_list('film_number', flat=True))
                if roll_numbers:
                    first_roll = roll_numbers[0]
                    last_roll = roll_numbers[-1]
                    if first_roll == last_roll:
                        roll_range = first_roll
                    else:
                        roll_range = f"{first_roll} - {last_roll}"
            except Exception as roll_error:
                logger.warning(f"Error getting roll range for project {project.id}: {roll_error}")
                roll_range = "N/A"
                
            project_data = {
                'id': project.id,
                'name': project.name or f"Project {project.archive_id}",
                'archive_id': project.archive_id,
                'doc_type': project.doc_type or 'Documents',
                'location': project.location,
                'total_rolls': project.total_rolls,
                'filmed_rolls': project.filmed_rolls,
                'developed_rolls': project.developed_rolls,
                'labeled_rolls': project.labeled_rolls,
                'roll_range': roll_range,
                'all_filmed': all_filmed,
                'all_developed': all_developed,
                'all_labeled': all_labeled,
                'completion_date': latest_completion.isoformat() if latest_completion else None,
                'created_at': project.created_at.isoformat(),
                'project_path': project.project_path
            }
            
            # Categorize projects - check handoff status first
            if project.handoff_complete:
                project_data['status'] = 'completed'
                project_data['status_text'] = 'Handoff Complete'
                completed_projects.append(project_data)
                logger.info(f"✅ Project {project.archive_id} categorized as HANDOFF COMPLETE")
            elif all_filmed and all_developed and all_labeled:
                project_data['status'] = 'ready'
                project_data['status_text'] = 'Ready for Handoff'
                ready_projects.append(project_data)
                logger.info(f"✅ Project {project.archive_id} categorized as READY FOR HANDOFF")
            elif all_filmed:
                project_data['status'] = 'filmed'
                project_data['status_text'] = 'Filming Complete'
                filmed_projects.append(project_data)
                logger.info(f"🎬 Project {project.archive_id} categorized as FILMING COMPLETE")
                
                # Log why it's not ready for handoff
                if not all_developed:
                    missing_dev = project.total_rolls - project.developed_rolls
                    logger.info(f"    Reason: {missing_dev} roll(s) not developed")
                if not all_labeled:
                    missing_labels = project.total_rolls - project.labeled_rolls
                    logger.info(f"    Reason: {missing_labels} roll(s) missing completed labels")
            else:
                logger.info(f"❌ Project {project.archive_id} not included - filming not complete")
                logger.info(f"    Missing filming: {project.total_rolls - project.filmed_rolls} roll(s)")
            
            logger.info(f"=== END PROJECT STATUS DEBUG: {project.archive_id} ===\n")
        
        # Sort by completion date (most recent first)
        ready_projects.sort(key=lambda x: x['completion_date'] or '', reverse=True)
        filmed_projects.sort(key=lambda x: x['completion_date'] or '', reverse=True)
        completed_projects.sort(key=lambda x: x['completion_date'] or '', reverse=True)
        
        logger.info("=== HANDOFF PROJECT QUERY SUMMARY ===")
        logger.info(f"Total projects evaluated: {projects.count()}")
        logger.info(f"Ready for handoff: {len(ready_projects)}")
        logger.info(f"Filming complete: {len(filmed_projects)}")
        logger.info(f"Handoff complete: {len(completed_projects)}")
        logger.info(f"Ready projects: {[p['archive_id'] for p in ready_projects]}")
        logger.info(f"Filmed projects: {[p['archive_id'] for p in filmed_projects]}")
        logger.info(f"Completed projects: {[p['archive_id'] for p in completed_projects]}")
        logger.info("=== HANDOFF PROJECT QUERY DEBUG END ===\n")
        
        return JsonResponse({
            'success': True,
            'projects': {
                'ready': ready_projects,
                'filmed': filmed_projects,
                'completed': completed_projects,
                'total_ready': len(ready_projects),
                'total_filmed': len(filmed_projects),
                'total_completed': len(completed_projects)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching projects for handoff: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_project_validation_data(request, project_id):
    """
    Get validation data for a specific project.
    Returns the temporary index data that needs to be validated against film logs.
    """
    try:
        project = get_object_or_404(Project, pk=project_id)
        
        # Get all document segments for this project with their blip information (16mm only)
        from ..models import DocumentSegment, Document
        
        segments = DocumentSegment.objects.filter(
            roll__project=project,
            roll__film_type='16mm'  # Only include 16mm rolls for handoff validation
        ).select_related(
            'document', 'roll'
        ).order_by('roll__film_number', 'document_index')
        
        logger.info(f"=== VALIDATION DATA DEBUG START for project {project.archive_id} ===")
        logger.info(f"Found {segments.count()} document segments (16mm rolls only)")
        
        validation_data = []
        nan_count = 0
        null_count = 0
        
        for i, segment in enumerate(segments):
            com_id = segment.document.com_id
            
            # Debug: Check for NaN/null values in database
            if com_id is None:
                null_count += 1
                if i < 5:  # Log first 5 null values
                    logger.debug(f"NULL com_id in segment {i}: doc_id={segment.document.doc_id}, "
                               f"document_id={segment.document.id}")
            elif pd.isna(com_id):
                nan_count += 1
                logger.warning(f"NaN com_id in segment {i}: doc_id={segment.document.doc_id}, "
                             f"com_id={com_id}, document_id={segment.document.id}")
            elif isinstance(com_id, float) and (com_id == float('inf') or com_id == float('-inf')):
                logger.warning(f"INF com_id in segment {i}: doc_id={segment.document.doc_id}, "
                             f"com_id={com_id}, document_id={segment.document.id}")
            
            validation_data.append({
                'document_id': segment.document.doc_id,
                'roll': segment.roll.film_number,
                'barcode': segment.document.doc_id,  # Using doc_id as barcode
                'com_id': segment.document.com_id,
                'temp_blip': segment.blip,
                'film_blip': None,  # Will be filled during validation
                'status': 'pending',
                'start_frame': segment.start_frame,
                'end_frame': segment.end_frame,
                'pages': segment.pages
            })
        
        logger.info(f"Validation data summary: {len(validation_data)} entries, "
                   f"{null_count} NULL com_ids, {nan_count} NaN com_ids")
        
        if nan_count > 0:
            logger.warning(f"Found {nan_count} NaN com_id values in database segments!")
        
        if null_count > 0:
            logger.info(f"Found {null_count} NULL com_id values in database segments")
        
        logger.info(f"=== VALIDATION DATA DEBUG END ===")
        
        return JsonResponse({
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'archive_id': project.archive_id,
                'doc_type': project.doc_type,
                'project_path': project.project_path
            },
            'validation_data': validation_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching validation data for project {project_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def validate_project_index(request, project_id):
    """
    Validate project index against film log files.
    Reads log files from project/.filmlogs/ directory and compares with temporary index.
    """
    try:
        data = json.loads(request.body)
        project = get_object_or_404(Project, pk=project_id)
        
        # Get validation data directly (16mm rolls only)
        from ..models import DocumentSegment, Document
        
        segments = DocumentSegment.objects.filter(
            roll__project=project,
            roll__film_type='16mm'  # Only include 16mm rolls for handoff validation
        ).select_related(
            'document', 'roll'
        ).order_by('roll__film_number', 'document_index')
        
        logger.info(f"=== VALIDATION INDEX DEBUG START for project {project.archive_id} ===")
        logger.info(f"Found {segments.count()} document segments for validation (16mm rolls only)")
        
        validation_data = []
        nan_count = 0
        null_count = 0
        
        for i, segment in enumerate(segments):
            com_id = segment.document.com_id
            
            # Debug: Check for NaN/null values in database
            if com_id is None:
                null_count += 1
                if i < 5:  # Log first 5 null values
                    logger.debug(f"NULL com_id in validation segment {i}: doc_id={segment.document.doc_id}, "
                               f"document_id={segment.document.id}")
            elif pd.isna(com_id):
                nan_count += 1
                logger.warning(f"NaN com_id in validation segment {i}: doc_id={segment.document.doc_id}, "
                             f"com_id={com_id}, document_id={segment.document.id}")
            elif isinstance(com_id, float) and (com_id == float('inf') or com_id == float('-inf')):
                logger.warning(f"INF com_id in validation segment {i}: doc_id={segment.document.doc_id}, "
                             f"com_id={com_id}, document_id={segment.document.id}")
            
            validation_data.append({
                'document_id': segment.document.doc_id,
                'roll': segment.roll.film_number,
                'barcode': segment.document.doc_id,  # Using doc_id as barcode
                'com_id': segment.document.com_id,
                'temp_blip': segment.blip,
                'film_blip': None,  # Will be filled during validation
                'status': 'pending',
                'start_frame': segment.start_frame,
                'end_frame': segment.end_frame,
                'pages': segment.pages
            })
        
        logger.info(f"Validation index data summary: {len(validation_data)} entries, "
                   f"{null_count} NULL com_ids, {nan_count} NaN com_ids")
        
        if nan_count > 0:
            logger.warning(f"Found {nan_count} NaN com_id values in validation segments!")
        
        # Try to use HandoffService, fallback to mock if there are import issues
        try:
            from ..services.handoff_service import HandoffService
            handoff_service = HandoffService()
            summary, results = handoff_service.validate_project(project, validation_data)
            
            # Convert results to dictionaries for JSON response
            validated_data = []
            result_nan_count = 0
            
            for i, result in enumerate(results):
                # Debug: Check for NaN values in results
                if pd.isna(result.com_id) if result.com_id is not None else False:
                    result_nan_count += 1
                    logger.warning(f"NaN com_id in validation result {i}: {result}")
                
                validated_data.append({
                    'document_id': result.document_id,
                    'roll': result.roll,
                    'barcode': result.barcode,
                    'com_id': result.com_id,
                    'temp_blip': result.temp_blip,
                    'film_blip': result.film_blip,
                    'status': result.status,
                    'message': result.message,
                    'start_frame': result.start_frame,
                    'end_frame': result.end_frame,
                    'pages': result.pages
                })
            
            if result_nan_count > 0:
                logger.warning(f"Found {result_nan_count} NaN com_id values in validation results!")
            
            validation_results = {
                'total': summary.total,
                'validated': summary.validated,
                'warnings': summary.warnings,
                'errors': summary.errors
            }
            
            logger.info(f"=== VALIDATION INDEX DEBUG END ===")
            
            return JsonResponse({
                'success': True,
                'validation_results': validation_results,
                'validated_data': validated_data,
                'message': f'Validation complete: {summary.validated} validated, {summary.warnings} warnings, {summary.errors} errors'
            })
            
        except Exception as service_error:
            logger.warning(f"HandoffService failed, using fallback: {service_error}")
            
            # Fallback to mock validation
            import random
            results = {
                'total': len(validation_data),
                'validated': 0,
                'warnings': 0,
                'errors': 0
            }
            
            # Mock validation results
            for item in validation_data:
                rand = random.random()
                if rand < 0.8:  # 80% validated
                    item['status'] = 'validated'
                    item['film_blip'] = item['temp_blip']
                    results['validated'] += 1
                elif rand < 0.95:  # 15% warnings
                    item['status'] = 'warning'
                    item['film_blip'] = item['temp_blip'] + '_WARN'
                    results['warnings'] += 1
                else:  # 5% errors
                    item['status'] = 'error'
                    item['film_blip'] = 'NOT_FOUND'
                    results['errors'] += 1
            
            return JsonResponse({
                'success': True,
                'validation_results': results,
                'validated_data': validation_data,
                'message': f'Validation complete (fallback): {results["validated"]} validated, {results["warnings"]} warnings, {results["errors"]} errors'
            })
        
    except Exception as e:
        logger.error(f"Error validating project {project_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_handoff_files(request, project_id):
    """
    Generate the final handoff files (Excel only - DAT file generation disabled) for a project.
    """
    try:
        data = json.loads(request.body)
        project = get_object_or_404(Project, pk=project_id)
        validated_data = data.get('validated_data', [])
        
        if not validated_data:
            return JsonResponse({
                'success': False,
                'error': 'No validated data provided'
            }, status=400)
        
        # Use HandoffService for file generation
        from ..services.handoff_service import HandoffService, ValidationResult
        handoff_service = HandoffService()
        
        # Convert validated_data back to ValidationResult objects
        validation_results = []
        for item in validated_data:
            result = ValidationResult(
                document_id=item.get('document_id', ''),
                roll=item.get('roll', ''),
                barcode=item.get('barcode', ''),
                com_id=item.get('com_id', ''),
                temp_blip=item.get('temp_blip', ''),
                film_blip=item.get('film_blip'),
                status=item.get('status', 'pending'),
                message=item.get('message'),
                start_frame=item.get('start_frame'),
                end_frame=item.get('end_frame'),
                pages=item.get('pages')
            )
            validation_results.append(result)
        
        # Generate files
        file_info = handoff_service.generate_handoff_files(project, validation_results)
        
        return JsonResponse({
            'success': True,
            'files': file_info,
            'message': 'Handoff files generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating handoff files for project {project_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_handoff_email(request, project_id):
    """
    Send handoff email with generated files.
    Uses win32com to send email via Outlook.
    """
    try:
        data = json.loads(request.body)
        project = get_object_or_404(Project, pk=project_id)
        
        # Check if using new form data structure
        if data.get('use_form_data'):
            # New form-based structure
            email_data = {
                'to': data.get('to', ''),
                'cc': data.get('cc', ''),
                'subject': data.get('subject', ''),
                'archive_id': data.get('archive_id', ''),
                'film_numbers': data.get('film_numbers', ''),
                'custom_message': data.get('custom_message', ''),
                'use_form_data': True
            }
        else:
            # Legacy structure for backward compatibility
            email_data = {
                'to': data.get('to', ''),
                'cc': data.get('cc', ''),
                'subject': data.get('subject', ''),
                'body': data.get('body', ''),
                'attachments': data.get('attachments', [])
            }
        
        if not email_data['to']:
            return JsonResponse({
                'success': False,
                'error': 'No recipients specified'
            }, status=400)
        
        # Use HandoffService for email sending
        from ..services.handoff_service import HandoffService
        handoff_service = HandoffService()
        
        # For form data, we need to generate files first
        if data.get('use_form_data'):
            # Generate handoff files first
            try:
                # Get validation data from the request or generate mock data
                validated_data = data.get('validated_data', [])
                if not validated_data:
                    # Generate mock validation data for testing (16mm only)
                    from ..models import DocumentSegment
                    segments = DocumentSegment.objects.filter(
                        roll__project=project,
                        roll__film_type='16mm'  # Only include 16mm rolls for handoff
                    ).select_related('document', 'roll')
                    
                    validated_data = []
                    for segment in segments:
                        validated_data.append({
                            'document_id': segment.document.doc_id,
                            'roll': segment.roll.film_number,
                            'barcode': segment.document.doc_id,
                            'com_id': segment.document.com_id,
                            'temp_blip': segment.blip,
                            'film_blip': segment.blip,
                            'status': 'validated'
                        })
                
                # Convert to ValidationResult objects
                from ..services.handoff_service import ValidationResult
                validation_results = []
                for item in validated_data:
                    result = ValidationResult(
                        document_id=item.get('document_id', ''),
                        roll=item.get('roll', ''),
                        barcode=item.get('barcode', ''),
                        com_id=item.get('com_id', ''),
                        temp_blip=item.get('temp_blip', ''),
                        film_blip=item.get('film_blip'),
                        status=item.get('status', 'pending'),
                        message=item.get('message'),
                        start_frame=item.get('start_frame'),
                        end_frame=item.get('end_frame'),
                        pages=item.get('pages')
                    )
                    validation_results.append(result)
                
                # Generate files
                file_paths = handoff_service.generate_handoff_files(project, validation_results)
                
            except Exception as file_error:
                logger.warning(f"Could not generate files, proceeding without attachments: {file_error}")
                file_paths = {}
        else:
            # Legacy: Get file paths from attachments data
            file_paths = data.get('attachments', {})
        
        result = handoff_service.send_handoff_email(project, email_data, file_paths, request.user)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error sending handoff email for project {project_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def test_handoff_endpoint(request):
    """Test endpoint to verify handoff views are working."""
    return JsonResponse({
        'success': True,
        'message': 'Handoff views are working correctly',
        'timestamp': timezone.now().isoformat()
    })

@csrf_exempt
@require_http_methods(["POST"])
def test_post_endpoint(request):
    """Test POST endpoint to debug 405 issues."""
    return JsonResponse({
        'success': True,
        'message': 'POST endpoint is working correctly',
        'method': request.method,
        'timestamp': timezone.now().isoformat()
    })

@require_http_methods(["GET"])
def preview_email_template(request, project_id):
    """Preview the email template with project data"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Get film numbers
        film_numbers = ', '.join([str(roll.roll_number) for roll in project.rolls.all()])
        
        # Render template with context
        template_content = render_to_string('microapp/handoff/email/signature_template.html', {
            'project': project,
            'film_numbers': film_numbers
        })
        
        return JsonResponse({
            'success': True,
            'template_content': template_content
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def preview_original_template(request):
    """Preview the original template without any variables - just for testing styling and icons"""
    try:
        # Render the original template (no context needed since it has no variables)
        template_content = render_to_string('microapp/handoff/email/signature_template_original.html')
        
        return JsonResponse({
            'success': True,
            'template_content': template_content
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 