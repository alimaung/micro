import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import logging
import uuid
from datetime import timedelta

from ..models import (
    Roll, DevelopmentSession, ChemicalBatch, DevelopmentLog, 
    FilmType, Project
)

logger = logging.getLogger(__name__)

def develop_dashboard(request):
    """Main development dashboard view"""
    return render(request, 'microapp/develop/develop.html')

@require_http_methods(["GET"])
def get_rolls_for_development(request):
    """
    Get rolls that are ready for development (filming completed).
    Shows all completed rolls so user can choose which ones to develop.
    """
    try:
        # Get all rolls with filming completed status, regardless of development status
        rolls = Roll.objects.filter(
            filming_status='completed'
        ).select_related('project').order_by('-filming_completed_at')
        
        rolls_data = []
        for roll in rolls:
            # Check if there's an active development session
            active_session = DevelopmentSession.objects.filter(
                roll=roll,
                status='developing'
            ).first()
            
            # Determine if roll can be developed
            can_develop = roll.development_status in ['pending', 'failed']
            is_developing = roll.development_status == 'developing'
            is_completed = roll.development_status == 'completed'
            
            roll_data = {
                'id': roll.id,
                'film_number': roll.film_number,
                'film_type': roll.film_type,
                'project_name': roll.project.archive_id,
                'pages_used': roll.pages_used,
                'filming_completed_at': roll.filming_completed_at.isoformat() if roll.filming_completed_at else None,
                'development_status': roll.development_status,
                'development_progress': 0,
                'estimated_completion': None,
                'session_id': None,
                'can_develop': can_develop,
                'is_developing': is_developing,
                'is_completed': is_completed,
                'development_completed_at': roll.development_completed_at.isoformat() if roll.development_completed_at else None
            }
            
            if active_session:
                # Calculate progress based on time elapsed
                if active_session.started_at:
                    elapsed = timezone.now() - active_session.started_at
                    total_duration = active_session.development_duration_minutes * 60  # Convert to seconds
                    progress = min(100, (elapsed.total_seconds() / total_duration) * 100)
                    
                    roll_data.update({
                        'development_progress': progress,
                        'estimated_completion': (active_session.started_at + 
                                               timedelta(minutes=active_session.development_duration_minutes)).isoformat(),
                        'session_id': str(active_session.session_id)
                    })
            
            rolls_data.append(roll_data)
        
        return JsonResponse({
            'success': True,
            'rolls': rolls_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching rolls for development: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_chemical_status(request):
    """
    Get current chemical batch status for all chemical types.
    """
    try:
        chemical_data = {}
        
        for chemical_type, display_name in ChemicalBatch.CHEMICAL_TYPES:
            # Get the active batch for this chemical type
            batch = ChemicalBatch.objects.filter(
                chemical_type=chemical_type,
                is_active=True
            ).first()
            
            if batch:
                chemical_data[chemical_type] = {
                    'batch_id': batch.batch_id,
                    'capacity_percent': batch.capacity_percent,
                    'remaining_capacity': batch.remaining_capacity,
                    'used_area': batch.used_area,
                    'max_area': batch.max_area,
                    'used_16mm_rolls': batch.used_16mm_rolls,
                    'used_35mm_rolls': batch.used_35mm_rolls,
                    'is_critical': batch.is_critical,
                    'is_low': batch.is_low,
                    'created_at': batch.created_at.isoformat(),
                    'installation_date': batch.installation_date.isoformat(),
                    # Age-related fields
                    'days_since_installation': batch.days_since_installation,
                    'hours_since_installation': batch.hours_since_installation,
                    'age_status': batch.age_status,
                    'is_age_warning': batch.is_age_warning,
                    'is_age_locked': batch.is_age_locked,
                    'days_until_warning': batch.days_until_warning,
                    'hours_until_lockout': batch.hours_until_lockout,
                    'status': 'critical' if batch.is_critical else 'low' if batch.is_low else 'good'
                }
            else:
                # No active batch - create default data
                chemical_data[chemical_type] = {
                    'batch_id': 'No active batch',
                    'capacity_percent': 0,
                    'remaining_capacity': 0,
                    'used_area': 0,
                    'max_area': 10.0,
                    'used_16mm_rolls': 0,
                    'used_35mm_rolls': 0,
                    'is_critical': True,
                    'is_low': True,
                    'created_at': None,
                    'status': 'critical'
                }
        
        return JsonResponse({
            'success': True,
            'chemicals': chemical_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching chemical status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_development(request):
    """
    Start development for a specific roll.
    """
    try:
        data = json.loads(request.body)
        roll_id = data.get('roll_id')
        roll_ids = data.get('roll_ids', [])
        
        # Support both single roll and multiple rolls
        if roll_id:
            roll_ids = [roll_id]
        elif not roll_ids:
            return JsonResponse({
                'success': False,
                'error': 'Roll ID or roll IDs are required'
            }, status=400)
        
        # Get all rolls
        rolls = Roll.objects.filter(pk__in=roll_ids)
        if not rolls.exists():
            return JsonResponse({
                'success': False,
                'error': 'No valid rolls found'
            }, status=400)
        
        # Check if all rolls are ready for development
        for roll in rolls:
            if roll.filming_status != 'completed':
                return JsonResponse({
                    'success': False,
                    'error': f'Roll {roll.film_number} must be filmed before development can start'
                }, status=400)
            
            if roll.development_status == 'developing':
                return JsonResponse({
                    'success': False,
                    'error': f'Roll {roll.film_number} is already being developed'
                }, status=400)
        
        # Calculate total area needed for all rolls
        total_area_needed = 0
        total_film_length = 0
        roll_details = []
        
        for roll in rolls:
            total_frames = roll.pages_used + 100  # Add leader/trailer
            film_length_m = (total_frames * 1.0) / 100.0  # 1cm per frame, convert to meters
            
            if roll.film_type == FilmType.FILM_16MM:
                film_height_m = 0.016  # 16mm in meters
            else:  # 35mm
                film_height_m = 0.035  # 35mm in meters
            
            area_needed = film_length_m * film_height_m
            total_area_needed += area_needed
            total_film_length += film_length_m
            
            roll_details.append({
                'roll': roll,
                'area_needed': area_needed,
                'film_length_m': film_length_m
            })
        
        # Check for expert mode
        expert_mode = data.get('expert_mode', False)
        
        chemicals_ok = True
        chemical_warnings = []
        low_chemical_warnings = []
        age_warnings = []
        locked_warnings = []
        
        for chemical_type, display_name in ChemicalBatch.CHEMICAL_TYPES:
            batch = ChemicalBatch.objects.filter(
                chemical_type=chemical_type,
                is_active=True
            ).first()
            
            if not batch:
                chemicals_ok = False
                chemical_warnings.append(f"{display_name}: No active batch found")
            elif not batch.can_process_roll(total_area_needed, expert_mode=expert_mode):
                chemicals_ok = False
                remaining = batch.remaining_capacity
                
                if batch.is_age_locked and not expert_mode:
                    hours_over = batch.hours_since_installation - (14 * 24 + 48)
                    locked_warnings.append(f"{display_name}: Age-locked ({hours_over:.1f} hours past expiry). Chemistry must be replaced.")
                else:
                    chemical_warnings.append(f"{display_name}: Insufficient capacity ({remaining:.3f} m² remaining, {total_area_needed:.3f} m² needed)")
            else:
                # Check for warnings even if development can proceed
                if batch.is_age_locked and expert_mode:
                    hours_over = batch.hours_since_installation - (14 * 24 + 48)
                    age_warnings.append(f"{display_name}: EXPERT MODE - Age-locked ({hours_over:.1f} hours past expiry). Quality may be compromised.")
                elif batch.is_age_warning:
                    if batch.hours_until_lockout > 0:
                        age_warnings.append(f"{display_name}: Age warning - {batch.hours_until_lockout:.1f} hours until lockout. Quality may diminish.")
                    else:
                        age_warnings.append(f"{display_name}: Age warning - Past 2 weeks installation. Quality may be compromised.")
                
                if batch.is_critical:
                    # Critical level but can still process this roll
                    low_chemical_warnings.append(f"{display_name}: Critical level ({batch.capacity_percent:.1f}% remaining)")
                elif batch.is_low:
                    # Low level but can still process this roll
                    low_chemical_warnings.append(f"{display_name}: Low level ({batch.capacity_percent:.1f}% remaining)")
        
        if not chemicals_ok:
            # Determine the primary error type
            if locked_warnings:
                error_msg = 'Chemicals are age-locked and must be replaced'
                all_warnings = locked_warnings + chemical_warnings
            else:
                error_msg = 'Chemical batches need replacement before development'
                all_warnings = chemical_warnings
                
            return JsonResponse({
                'success': False,
                'error': error_msg,
                'warnings': all_warnings,
                'locked_chemicals': len(locked_warnings) > 0,
                'expert_mode_available': len(locked_warnings) > 0
            }, status=400)
        
        # If chemicals are OK but some are low, include warnings in success response
        response_data = {
            'success': True,
            'session_id': None,  # Will be set below
            'estimated_completion': None,  # Will be set below
            'duration_minutes': None,  # Will be set below
            'film_length_meters': total_film_length,
            'roll_count': len(rolls),
            'expert_mode': expert_mode
        }
        
        # Combine all warning types
        all_warnings = []
        if age_warnings:
            all_warnings.extend(age_warnings)
        if low_chemical_warnings:
            all_warnings.extend(low_chemical_warnings)
            
        if all_warnings:
            response_data['chemical_warnings'] = all_warnings
        
        with transaction.atomic():
            # Create development session for the batch
            session_id = f"dev_{uuid.uuid4().hex[:8]}"
            
            # For multiple rolls, we'll create one session and link all rolls to it
            # Use the first roll as the primary roll for the session
            primary_roll = rolls.first()
            
            session = DevelopmentSession.objects.create(
                session_id=session_id,
                roll=primary_roll,
                user=request.user,
                status='developing',
                development_duration_minutes=total_film_length,  # 1 minute per meter
                started_at=timezone.now()
            )
            
            # Set estimated completion
            session.estimated_completion = timezone.now() + timedelta(minutes=total_film_length)
            session.save()
            
            # Update all roll statuses
            roll_numbers = []
            for roll_detail in roll_details:
                roll = roll_detail['roll']
                roll.development_status = 'developing'
                roll.development_started_at = timezone.now()
                roll.development_progress_percent = 0.0
                roll.save(update_fields=[
                    'development_status', 'development_started_at', 'development_progress_percent'
                ])
                roll_numbers.append(roll.film_number)
            
            # Update chemical batches with total area used
            for chemical_type, _ in ChemicalBatch.CHEMICAL_TYPES:
                batch = ChemicalBatch.objects.filter(
                    chemical_type=chemical_type,
                    is_active=True
                ).first()
                if batch:
                    # Add usage for each roll type
                    for roll_detail in roll_details:
                        roll = roll_detail['roll']
                        area_used = roll_detail['area_needed']
                        batch.add_roll_usage(roll.film_type, area_used)
            
            # Log the start
            roll_list = ", ".join(roll_numbers)
            DevelopmentLog.objects.create(
                session=session,
                level='info',
                message=f"Development started for {len(rolls)} rolls: {roll_list} - Total duration: {total_film_length:.1f} minutes"
            )
        
        response_data['session_id'] = session_id
        response_data['estimated_completion'] = session.estimated_completion.isoformat()
        response_data['duration_minutes'] = total_film_length
        response_data['film_length_meters'] = total_film_length
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error starting development: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def complete_development(request):
    """
    Mark development as completed for a session.
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID is required'
            }, status=400)
        
        session = get_object_or_404(DevelopmentSession, session_id=session_id)
        
        if session.status != 'developing':
            return JsonResponse({
                'success': False,
                'error': 'Session is not currently developing'
            }, status=400)
        
        with transaction.atomic():
            # Update session
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.progress_percent = 100.0
            session.save(update_fields=['status', 'completed_at', 'progress_percent'])
            
            # Update roll
            roll = session.roll
            roll.development_status = 'completed'
            roll.development_completed_at = timezone.now()
            roll.development_progress_percent = 100.0
            roll.save(update_fields=[
                'development_status', 'development_completed_at', 'development_progress_percent'
            ])
            
            # Log completion
            DevelopmentLog.objects.create(
                session=session,
                level='info',
                message=f"Development completed for roll {roll.film_number}"
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Development completed for roll {session.roll.film_number}',
            'completed_at': session.completed_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error completing development: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_development_progress(request):
    """
    Get current progress for a development session.
    """
    try:
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID is required'
            }, status=400)
        
        session = get_object_or_404(DevelopmentSession, session_id=session_id)
        
        if session.status == 'developing' and session.started_at:
            # Calculate progress based on elapsed time
            elapsed = timezone.now() - session.started_at
            total_duration = timedelta(minutes=session.development_duration_minutes)
            progress = min(100.0, (elapsed.total_seconds() / total_duration.total_seconds()) * 100)
            
            # Update progress in database
            session.progress_percent = progress
            session.roll.development_progress_percent = progress
            session.save(update_fields=['progress_percent'])
            session.roll.save(update_fields=['development_progress_percent'])
        else:
            progress = session.progress_percent
        
        return JsonResponse({
            'success': True,
            'progress': progress,
            'status': session.status,
            'estimated_completion': session.estimated_completion.isoformat() if session.estimated_completion else None,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        })
        
    except Exception as e:
        logger.error(f"Error getting development progress: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def reset_chemical_batch(request, chemical_type):
    """Reset a specific chemical batch"""
    try:
        data = json.loads(request.body)
        batch_id = data.get('batch_id')
        max_area = float(data.get('max_area', 10.0))
        
        if not batch_id:
            return JsonResponse({
                'success': False,
                'error': 'Batch ID is required'
            }, status=400)
        
        # Create new batch
        batch = ChemicalBatch.objects.create(
            chemical_type=chemical_type,
            batch_id=batch_id,
            max_area=max_area,
            used_area=0.0,
            installation_date=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{chemical_type} batch reset successfully',
            'batch': {
                'chemical_type': batch.chemical_type,
                'batch_id': batch.batch_id,
                'max_area': batch.max_area,
                'installation_date': batch.installation_date.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_development_history(request):
    """
    Get recent development session history.
    """
    try:
        sessions = DevelopmentSession.objects.select_related(
            'roll', 'roll__project', 'user'
        ).order_by('-created_at')[:20]
        
        session_data = []
        for session in sessions:
            session_data.append({
                'session_id': session.session_id,
                'roll_number': session.roll.roll_number,
                'film_number': session.roll.film_number,
                'film_type': session.roll.film_type,
                'project_name': session.roll.project.archive_id or session.roll.project.archive_id,
                'status': session.status,
                'progress': session.progress_percent,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'duration_minutes': session.development_duration_minutes,
                'user': session.user.username if session.user else None
            })
        
        return JsonResponse({
            'success': True,
            'sessions': session_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching development history: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def insert_chemicals(request):
    """
    Insert/replace all chemical batches at once.
    """
    try:
        data = json.loads(request.body)
        capacity = float(data.get('capacity', 10.0))
        notes = data.get('notes', '')
        
        if capacity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Capacity must be greater than 0'
            }, status=400)
        
        created_batches = []
        
        with transaction.atomic():
            # Process each chemical type
            for chemical_type, display_name in ChemicalBatch.CHEMICAL_TYPES:
                # Deactivate current batch if exists
                current_batch = ChemicalBatch.objects.filter(
                    chemical_type=chemical_type,
                    is_active=True
                ).first()
                
                if current_batch:
                    current_batch.is_active = False
                    current_batch.replaced_at = timezone.now()
                    current_batch.save()
                
                # Create new batch
                batch_id = f"{chemical_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
                new_batch = ChemicalBatch.objects.create(
                    chemical_type=chemical_type,
                    batch_id=batch_id,
                    max_area=capacity,
                    used_area=0.0,
                    used_16mm_rolls=0,
                    used_35mm_rolls=0,
                    is_active=True
                )
                
                created_batches.append({
                    'chemical_type': new_batch.chemical_type,
                    'batch_id': new_batch.batch_id,
                    'capacity': new_batch.max_area,
                    'created_at': new_batch.created_at.isoformat()
                })
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully inserted {len(created_batches)} chemical batches',
            'batches': created_batches
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error inserting chemicals: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_density_measurement(request):
    """
    Save a density measurement for a development session.
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        density_value = data.get('density_value')
        measurement_time_minutes = data.get('measurement_time_minutes')
        notes = data.get('notes', '')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID is required'
            }, status=400)
        
        if density_value is None:
            return JsonResponse({
                'success': False,
                'error': 'Density value is required'
            }, status=400)
        
        if measurement_time_minutes is None:
            return JsonResponse({
                'success': False,
                'error': 'Measurement time is required'
            }, status=400)
        
        # Validate density value range
        try:
            density_value = float(density_value)
            if density_value < 0.0 or density_value > 2.0:
                return JsonResponse({
                    'success': False,
                    'error': 'Density value must be between 0.0 and 2.0'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid density value'
            }, status=400)
        
        # Validate measurement time
        try:
            measurement_time_minutes = int(measurement_time_minutes)
            if measurement_time_minutes < 0 or measurement_time_minutes > 60:
                return JsonResponse({
                    'success': False,
                    'error': 'Measurement time must be between 0 and 60 minutes'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid measurement time'
            }, status=400)
        
        session = get_object_or_404(DevelopmentSession, session_id=session_id)
        
        # Import DensityMeasurement here to avoid circular imports
        from ..models import DensityMeasurement
        
        # Create or update the measurement
        measurement, created = DensityMeasurement.objects.update_or_create(
            session=session,
            measurement_time_minutes=measurement_time_minutes,
            defaults={
                'density_value': density_value,
                'notes': notes,
                'user': request.user
            }
        )
        
        # Log the measurement
        DevelopmentLog.objects.create(
            session=session,
            level='info',
            message=f"Density measurement recorded: {density_value} at {measurement_time_minutes} minutes"
        )
        
        return JsonResponse({
            'success': True,
            'measurement': {
                'id': measurement.id,
                'density_value': measurement.density_value,
                'measurement_time_minutes': measurement.measurement_time_minutes,
                'notes': measurement.notes,
                'is_within_optimal_range': measurement.is_within_optimal_range,
                'quality_status': measurement.quality_status,
                'quality_color': measurement.quality_color,
                'created_at': measurement.created_at.isoformat()
            },
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error saving density measurement: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_density_measurements(request):
    """
    Get density measurements for a development session.
    """
    try:
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID is required'
            }, status=400)
        
        session = get_object_or_404(DevelopmentSession, session_id=session_id)
        
        # Import DensityMeasurement here to avoid circular imports
        from ..models import DensityMeasurement
        
        measurements = DensityMeasurement.objects.filter(
            session=session
        ).order_by('measurement_time_minutes')
        
        measurements_data = []
        for measurement in measurements:
            measurements_data.append({
                'id': measurement.id,
                'density_value': measurement.density_value,
                'measurement_time_minutes': measurement.measurement_time_minutes,
                'notes': measurement.notes,
                'is_within_optimal_range': measurement.is_within_optimal_range,
                'quality_status': measurement.quality_status,
                'quality_color': measurement.quality_color,
                'created_at': measurement.created_at.isoformat(),
                'user': measurement.user.username if measurement.user else None
            })
        
        return JsonResponse({
            'success': True,
            'measurements': measurements_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching density measurements: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_development_planner(request):
    """
    Get development run plan based on available rolls and chemical capacity.
    Analyzes rolls and suggests optimal development runs.
    """
    try:
        # Get all rolls that can be developed
        rolls = Roll.objects.filter(
            filming_status='completed',
            development_status__in=['pending', 'failed']
        ).select_related('project').order_by('project_id', 'pages_used')
        
        if not rolls.exists():
            return JsonResponse({
                'success': True,
                'run_plan': {
                    'rolls': [],
                    'grouped_by_project': [],
                    'totals': {'area_m2': 0, 'roll_count': 0, 'est_time_min': 0},
                    'chemistry': {'capacity_left_m2': 0, 'capacity_after_run_m2': 0, 'age_warning': False, 'lockout_at': None},
                    'advice': 'No rolls available for development',
                    'generated_at': timezone.now().isoformat()
                }
            })
        
        # Get chemical capacity (limiting reagent)
        min_remaining_capacity = float('inf')
        chemical_status = {}
        age_warning = False
        earliest_lockout = None
        
        for chemical_type, display_name in ChemicalBatch.CHEMICAL_TYPES:
            batch = ChemicalBatch.objects.filter(
                chemical_type=chemical_type,
                is_active=True
            ).first()
            
            if batch:
                min_remaining_capacity = min(min_remaining_capacity, batch.remaining_capacity)
                chemical_status[chemical_type] = {
                    'remaining_capacity': batch.remaining_capacity,
                    'is_age_warning': batch.is_age_warning,
                    'is_age_locked': batch.is_age_locked,
                    'hours_until_lockout': batch.hours_until_lockout
                }
                
                if batch.is_age_warning:
                    age_warning = True
                
                if batch.is_age_locked:
                    lockout_time = batch.installation_date + timedelta(days=14, hours=48)
                    if earliest_lockout is None or lockout_time < earliest_lockout:
                        earliest_lockout = lockout_time
            else:
                min_remaining_capacity = 0
        
        if min_remaining_capacity == float('inf'):
            min_remaining_capacity = 0
        
        # Calculate roll areas and group by project
        roll_data = []
        project_groups = {}
        
        for roll in rolls:
            # Calculate area needed
            total_frames = roll.pages_used + 100  # Add leader/trailer
            film_length_m = (total_frames * 1.0) / 100.0  # 1cm per frame
            
            if roll.film_type == FilmType.FILM_16MM:
                film_height_m = 0.016  # 16mm
            else:  # 35mm
                film_height_m = 0.035  # 35mm
            
            area_m2 = film_length_m * film_height_m
            
            roll_info = {
                'id': roll.id,
                'film_number': roll.film_number,
                'film_type': roll.film_type,
                'project_id': roll.project.id,
                'project_name': roll.project.archive_id,
                'pages_used': roll.pages_used,
                'area_m2': area_m2,
                'film_length_m': film_length_m,
                'ready_since': roll.filming_completed_at
            }
            
            roll_data.append(roll_info)
            
            # Group by project
            if roll.project.id not in project_groups:
                project_groups[roll.project.id] = {
                    'project_id': roll.project.id,
                    'project_name': roll.project.archive_id,
                    'total_area': 0,
                    'roll_count': 0,
                    'rolls': [],
                    'ready_since': roll.filming_completed_at
                }
            
            project_groups[roll.project.id]['total_area'] += area_m2
            project_groups[roll.project.id]['roll_count'] += 1
            project_groups[roll.project.id]['rolls'].append(roll_info)
            
            # Track earliest ready date for project
            if roll.filming_completed_at < project_groups[roll.project.id]['ready_since']:
                project_groups[roll.project.id]['ready_since'] = roll.filming_completed_at
        
        # Sort project groups by ready_since (older first), then by total_area (smaller first)
        sorted_projects = sorted(project_groups.values(), 
                               key=lambda p: (p['ready_since'], p['total_area']))
        
        # Packing algorithm - aim for 90% utilization
        target_utilization = min_remaining_capacity * 0.9
        selected_rolls = []
        selected_projects = []
        total_area = 0
        total_time = 0
        
        for project in sorted_projects:
            if total_area + project['total_area'] <= target_utilization:
                # Add entire project
                selected_projects.append(project)
                selected_rolls.extend(project['rolls'])
                total_area += project['total_area']
                total_time += sum(roll['film_length_m'] for roll in project['rolls'])
            else:
                # Try to fit individual rolls from this project (smaller first)
                project_rolls = sorted(project['rolls'], key=lambda r: r['area_m2'])
                for roll in project_rolls:
                    if total_area + roll['area_m2'] <= target_utilization:
                        selected_rolls.append(roll)
                        total_area += roll['area_m2']
                        total_time += roll['film_length_m']
                        
                        # Add partial project group
                        partial_project = next((p for p in selected_projects if p['project_id'] == project['project_id']), None)
                        if not partial_project:
                            partial_project = {
                                'project_id': project['project_id'],
                                'project_name': project['project_name'],
                                'total_area': 0,
                                'roll_count': 0,
                                'rolls': []
                            }
                            selected_projects.append(partial_project)
                        
                        partial_project['total_area'] += roll['area_m2']
                        partial_project['roll_count'] += 1
                        partial_project['rolls'].append(roll)
        
        # Generate advice
        if min_remaining_capacity == 0:
            advice = "No chemicals available - install chemical batches first"
        elif any(chemical_status[ct]['is_age_locked'] for ct, _ in ChemicalBatch.CHEMICAL_TYPES if ct in chemical_status):
            advice = "Chemicals are age-locked - replace chemicals before development"
        elif total_area < min_remaining_capacity * 0.5:  # Less than 50% utilization
            needed_area = min_remaining_capacity * 0.8 - total_area
            advice = f"Wait for more rolls (need {needed_area:.2f} m² more for efficient run)"
        else:
            advice = "Ready to start development run"
        
        return JsonResponse({
            'success': True,
            'run_plan': {
                'rolls': selected_rolls,
                'grouped_by_project': selected_projects,
                'totals': {
                    'area_m2': round(total_area, 3),
                    'roll_count': len(selected_rolls),
                    'est_time_min': round(total_time, 1)
                },
                'chemistry': {
                    'capacity_left_m2': round(min_remaining_capacity, 3),
                    'capacity_after_run_m2': round(min_remaining_capacity - total_area, 3),
                    'utilization_percent': round((total_area / min_remaining_capacity * 100) if min_remaining_capacity > 0 else 0, 1),
                    'age_warning': age_warning,
                    'lockout_at': earliest_lockout.isoformat() if earliest_lockout else None
                },
                'advice': advice,
                'generated_at': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating development plan: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_active_development_session(request):
    """
    Get the currently active development session for timer restoration.
    """
    try:
        # Find any active development session
        active_session = DevelopmentSession.objects.filter(
            status='developing'
        ).select_related('roll', 'roll__project').first()
        
        if not active_session:
            return JsonResponse({
                'success': True,
                'session': None
            })
        
        # Calculate development duration
        total_frames = active_session.roll.pages_used + 100  # Add leader/trailer
        film_length_m = (total_frames * 1.0) / 100.0  # 1cm per frame, convert to meters
        development_duration = film_length_m  # 1 minute per meter
        
        session_data = {
            'session_id': str(active_session.session_id),
            'roll_id': active_session.roll.id,
            'film_number': active_session.roll.film_number,
            'film_type': active_session.roll.film_type,
            'project_name': active_session.roll.project.archive_id,
            'pages_used': active_session.roll.pages_used,
            'duration_minutes': development_duration,
            'film_length_meters': film_length_m,
            'started_at': active_session.started_at.isoformat() if active_session.started_at else None,
            'status': active_session.status
        }
        
        return JsonResponse({
            'success': True,
            'session': session_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching active development session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 