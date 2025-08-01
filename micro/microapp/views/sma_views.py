"""
SMA Views - Django views for SMA filming operations.

This module provides the web API endpoints for managing SMA filming sessions,
integrating with the real SMA processor through the SMA service layer.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings

from ..services.sma_service import SMAService
from ..models import Project, Roll, FilmingSession, FilmingSessionLog

logger = logging.getLogger(__name__)

def sort_rolls_by_temp_roll_dependencies(rolls):
    """
    Sort rolls to respect temp roll dependency chains.
    
    Ensures that rolls that create temp rolls are filmed before rolls that use those temp rolls.
    
    Args:
        rolls: List of Roll objects
        
    Returns:
        List of rolls sorted by dependency order
    """
    if not rolls:
        return rolls
    
    # Create a map of temp roll ID to the roll that will create it
    temp_roll_creators = {}
    for roll in rolls:
        if roll.created_temp_roll:
            temp_roll_creators[roll.created_temp_roll.temp_roll_id] = roll
    
    # Calculate dependency depth for each roll
    def get_dependency_depth(roll, visited=None):
        if visited is None:
            visited = set()
            
        # Prevent circular dependencies
        if roll.id in visited:
            return 0
        visited.add(roll.id)
        
        # If this roll uses a temp roll, check if that temp roll is created by another roll
        if roll.source_temp_roll and roll.source_temp_roll.temp_roll_id in temp_roll_creators:
            creator_roll = temp_roll_creators[roll.source_temp_roll.temp_roll_id]
            # This roll depends on the creator roll, so it has depth + 1
            return get_dependency_depth(creator_roll, visited.copy()) + 1
        
        # No dependencies, this roll can be filmed first (depth 0)
        return 0
    
    # Sort by dependency depth (lower depth = film first), then by project and roll number
    sorted_rolls = sorted(rolls, key=lambda r: (
        get_dependency_depth(r),  # Primary: dependency depth
        r.project.archive_id,     # Secondary: project archive ID
        r.roll_number or 0        # Tertiary: roll number
    ))
    
    # Log the dependency chain for debugging
    if logger.isEnabledFor(logging.INFO):
        logger.info("Temp roll dependency order:")
        for i, roll in enumerate(sorted_rolls):
            depth = get_dependency_depth(roll)
            temp_roll_info = ""
            if roll.source_temp_roll:
                temp_roll_info = f" (uses T#{roll.source_temp_roll.temp_roll_id})"
            if roll.created_temp_roll:
                temp_roll_info += f" (creates T#{roll.created_temp_roll.temp_roll_id})"
            logger.info(f"  {i+1}. Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number} [depth={depth}]{temp_roll_info}")
    
    return sorted_rolls

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SMAFilmingView(View):
    """Handle SMA filming operations with enhanced validation and error handling."""
    
    def post(self, request):
        """Start a new filming session with comprehensive validation."""
        try:
            data = json.loads(request.body)
            
            # Extract and validate required parameters
            roll_id = data.get('roll_id')
            film_type = data.get('film_type', '16mm')
            recovery = data.get('recovery', False)
            re_filming = data.get('re_filming', False)
            
            # Enhanced validation
            validation_errors = []
            
            if not roll_id:
                validation_errors.append('roll_id is required')
            elif not isinstance(roll_id, int):
                try:
                    roll_id = int(roll_id)
                except (ValueError, TypeError):
                    validation_errors.append('roll_id must be a valid integer')
            
            if film_type not in ['16mm', '35mm']:
                validation_errors.append('film_type must be either "16mm" or "35mm"')
            
            if validation_errors:
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed',
                    'validation_errors': validation_errors
                }, status=400)
            
            # Check user permissions (could be enhanced with role-based access)
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required'
                }, status=401)
            
            # Start filming session with new roll-only interface
            result = SMAService.start_filming_session(
                roll_id=roll_id,
                film_type=film_type,
                recovery=recovery,
                re_filming=re_filming,
                user_id=request.user.id
            )
            
            # Enhanced response with additional context
            if result['success']:
                # Log successful start
                logger.info(f"User {request.user.username} started {'re-' if re_filming else ''}filming session {result['session_id']}")
                
                # Add user context to response
                result['user'] = {
                    'id': request.user.id,
                    'username': request.user.username
                }
            
            status_code = 200 if result['success'] else 400
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data',
                'details': 'Request body must contain valid JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"Error starting filming session: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e) if settings.DEBUG else 'An unexpected error occurred'
            }, status=500)
    
    def get(self, request):
        """Get active filming sessions with filtering and pagination."""
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 items per page
            status_filter = request.GET.get('status')
            project_filter = request.GET.get('project_id')
            user_filter = request.GET.get('user_id')
            
            # Get active sessions from service
            result = SMAService.get_active_sessions()
            
            if not result['success']:
                return JsonResponse(result, status=500)
            
            sessions = result['active_sessions']
            
            # Apply filters
            if status_filter:
                sessions = [s for s in sessions if s.get('status') == status_filter]
            
            if project_filter:
                try:
                    project_id = int(project_filter)
                    sessions = [s for s in sessions if s.get('project_id') == project_id]
                except ValueError:
                    pass
            
            if user_filter:
                try:
                    user_id = int(user_filter)
                    sessions = [s for s in sessions if s.get('user_id') == user_id]
                except ValueError:
                    pass
            
            # Paginate results
            paginator = Paginator(sessions, page_size)
            page_obj = paginator.get_page(page)
            
            return JsonResponse({
                'success': True,
                'active_sessions': list(page_obj),
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                },
                'summary': {
                    'total_active': result['total_active'],
                    'process_count': result['process_count']
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SMASessionView(View):
    """Handle individual SMA session operations with enhanced functionality."""
    
    def get(self, request, session_id):
        """Get comprehensive session status and details."""
        try:
            # Validate session_id format
            if not session_id or len(session_id) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid session ID format'
                }, status=400)
            
            result = SMAService.get_session_status(session_id)
            
            # Add additional context if successful
            if result['success']:
                # Check if user has access to this session
                session_status = result['status']
                if session_status.get('user_id') and session_status['user_id'] != request.user.id:
                    if not request.user.is_staff:  # Allow staff to view all sessions
                        return JsonResponse({
                            'success': False,
                            'error': 'Access denied'
                        }, status=403)
                
                # Add user information
                if session_status.get('user_id'):
                    try:
                        from django.contrib.auth.models import User
                        user = User.objects.get(id=session_status['user_id'])
                        session_status['user_info'] = {
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                    except User.DoesNotExist:
                        pass
            
            status_code = 200 if result['success'] else 404
            return JsonResponse(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def patch(self, request, session_id):
        """Update session with enhanced action validation."""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            # Validate action
            valid_actions = ['pause', 'resume', 'cancel', 'terminate']
            if action not in valid_actions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid action. Valid actions are: {", ".join(valid_actions)}'
                }, status=400)
            
            # Check user permissions for the session
            session_result = SMAService.get_session_status(session_id)
            if session_result['success']:
                session_user_id = session_result['status'].get('user_id')
                if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                    return JsonResponse({
                        'success': False,
                        'error': 'Access denied - you can only control your own sessions'
                    }, status=403)
            
            # Execute action
            if action == 'pause':
                result = SMAService.pause_session(session_id)
            elif action == 'resume':
                result = SMAService.resume_session(session_id)
            elif action == 'cancel':
                result = SMAService.cancel_session(session_id)
            elif action == 'terminate':
                force = data.get('force', False)
                result = SMAService.terminate_session(session_id, force=force)
            
            # Log the action
            if result['success']:
                logger.info(f"User {request.user.username} performed action '{action}' on session {session_id}")
            
            status_code = 200 if result['success'] else 400
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def delete(self, request, session_id):
        """Terminate and delete session with enhanced safety checks."""
        try:
            # Check user permissions
            session_result = SMAService.get_session_status(session_id)
            if session_result['success']:
                session_user_id = session_result['status'].get('user_id')
                if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                    return JsonResponse({
                        'success': False,
                        'error': 'Access denied - you can only delete your own sessions'
                    }, status=403)
            
            result = SMAService.terminate_session(session_id, force=True)
            
            if result['success']:
                logger.warning(f"User {request.user.username} force-deleted session {session_id}")
            
            status_code = 200 if result['success'] else 400
            return JsonResponse(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_health(request, session_id):
    """Get detailed health information for a session."""
    try:
        result = SMAService.get_session_health(session_id)
        status_code = 200 if result['success'] else 404
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        logger.error(f"Error getting session health: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def force_checkpoint(request, session_id):
    """Force a checkpoint save for a session."""
    try:
        # Check user permissions
        session_result = SMAService.get_session_status(session_id)
        if session_result['success']:
            session_user_id = session_result['status'].get('user_id')
            if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
        
        result = SMAService.force_checkpoint(session_id)
        
        if result['success']:
            logger.info(f"User {request.user.username} forced checkpoint for session {session_id}")
        
        status_code = 200 if result['success'] else 400
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        logger.error(f"Error forcing checkpoint: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def recover_session(request, session_id):
    """Recover a failed or interrupted filming session with enhanced validation."""
    try:
        # Check user permissions
        session_result = SMAService.get_session_status(session_id)
        if session_result['success']:
            session_user_id = session_result['status'].get('user_id')
            if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied - you can only recover your own sessions'
                }, status=403)
        
        result = SMAService.recover_session(session_id)
        
        if result['success']:
            logger.info(f"User {request.user.username} recovered session {session_id}")
        
        status_code = 200 if result['success'] else 400
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        logger.error(f"Error recovering session: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_logs(request, session_id):
    """Get logs for a filming session with enhanced filtering and pagination."""
    try:
        # Validate parameters
        try:
            limit = min(int(request.GET.get('limit', 100)), 1000)  # Max 1000 logs
            page = int(request.GET.get('page', 1))
            level_filter = request.GET.get('level')
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid parameters - limit and page must be integers'
            }, status=400)
        
        # Check user permissions
        session_result = SMAService.get_session_status(session_id)
        if session_result['success']:
            session_user_id = session_result['status'].get('user_id')
            if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
        
        # Get session logs from database
        try:
            session = FilmingSession.objects.get(session_id=session_id)
        except FilmingSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            }, status=404)
        
        # Build query
        logs_query = FilmingSessionLog.objects.filter(session=session)
        
        if level_filter:
            logs_query = logs_query.filter(level=level_filter)
        
        logs_query = logs_query.order_by('-created_at')
        
        # Paginate
        paginator = Paginator(logs_query, limit)
        page_obj = paginator.get_page(page)
        
        # Format logs
        log_entries = []
        for log in page_obj:
            log_entries.append({
                'id': log.id,
                'timestamp': log.created_at.isoformat(),
                'level': log.level,
                'message': log.message,
                'workflow_state': log.workflow_state
            })
        
        return JsonResponse({
            'success': True,
            'logs': log_entries,
            'pagination': {
                'page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session logs: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_statistics(request, session_id):
    """Get detailed statistics for a filming session with enhanced metrics."""
    try:
        # Check user permissions
        session_result = SMAService.get_session_status(session_id)
        if session_result['success']:
            session_user_id = session_result['status'].get('user_id')
            if session_user_id and session_user_id != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied'
                }, status=403)
        
        result = SMAService.get_session_statistics(session_id)
        status_code = 200 if result['success'] else 404
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        logger.error(f"Error getting session statistics: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def mark_roll_filmed(request, session_id):
    """Mark a roll as filmed after successful completion."""
    try:
        result = SMAService.mark_roll_as_filmed(session_id)
        status_code = 200 if result['success'] else 400
        return JsonResponse(result, status=status_code)
        
    except Exception as e:
        logger.error(f"Error marking roll as filmed: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def cleanup_sessions(request):
    """Clean up completed sessions with configurable age threshold."""
    try:
        # Only allow staff users to perform cleanup
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Access denied - staff privileges required'
            }, status=403)
        
        # Get optional parameters
        try:
            data = json.loads(request.body) if request.body else {}
            max_age_hours = int(data.get('max_age_hours', 24))
            
            if max_age_hours < 1 or max_age_hours > 168:  # 1 hour to 1 week
                return JsonResponse({
                    'success': False,
                    'error': 'max_age_hours must be between 1 and 168 (1 week)'
                }, status=400)
                
        except (json.JSONDecodeError, ValueError):
            max_age_hours = 24  # Default to 24 hours
        
        result = SMAService.cleanup_completed_sessions(max_age_hours=max_age_hours)
        
        if result['success']:
            logger.info(f"User {request.user.username} cleaned up {result['cleaned_up']} sessions")
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def project_rolls(request, project_id):
    """Get rolls for a project with their filming status and enhanced information."""
    try:
        # Validate project access
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)
            
        # Get query parameters
        status_filter = request.GET.get('status')
        include_sessions = request.GET.get('include_sessions', 'false').lower() == 'true'
        
        # Build query
        rolls_query = Roll.objects.filter(project=project).prefetch_related('source_temp_roll', 'created_temp_roll')
        
        if status_filter:
            rolls_query = rolls_query.filter(filming_status=status_filter)
        
        # Get all rolls and sort by dependencies for "ready" status
        all_rolls = list(rolls_query)
        if not status_filter or status_filter == 'ready':
            from ..services import FilmingOrderService
            filming_order = FilmingOrderService.analyze_rolls_for_filming(rolls_query)
            
            # Flatten the filming order for response
            ordered_rolls = []
            # Add creator rolls first (highest priority)
            for roll, analysis in filming_order['creator_rolls']:
                ordered_rolls.append(roll)
            # Then immediate rolls
            for roll, analysis in filming_order['immediate_rolls']:
                ordered_rolls.append(roll)
            # Then waiting rolls
            for roll, analysis in filming_order['waiting_rolls']:
                ordered_rolls.append(roll)
            # Finally problem rolls
            for roll, analysis in filming_order['problem_rolls']:
                ordered_rolls.append(roll)
                
            all_rolls = ordered_rolls
        else:
            # Default sorting for other statuses
            all_rolls.sort(key=lambda r: (r.roll_number or 0,))
        
        roll_data = []
        for roll in all_rolls:
            # Get filming priority information
            from ..services import FilmingOrderService
            priority_info = FilmingOrderService.get_filming_priority(roll)
            
            # Use getattr with defaults for fields that might not exist
            roll_info = {
                'id': roll.id,
                'roll_number': getattr(roll, 'roll_number', None),
                'filming_status': getattr(roll, 'filming_status', 'ready'),
                'filming_progress_percent': getattr(roll, 'filming_progress_percent', 0.0),
                'filming_started_at': roll.filming_started_at.isoformat() if getattr(roll, 'filming_started_at', None) else None,
                'filming_completed_at': roll.filming_completed_at.isoformat() if getattr(roll, 'filming_completed_at', None) else None,
                'capacity': getattr(roll, 'capacity', 0),
                'pages_used': getattr(roll, 'pages_used', 0),
                'pages_remaining': getattr(roll, 'pages_remaining', 0),
                'output_directory': getattr(roll, 'output_directory', None),
                'output_directory_exists': roll.output_directory_exists if hasattr(roll, 'output_directory_exists') else False,
                'created_at': roll.creation_date.isoformat() if hasattr(roll, 'creation_date') and roll.creation_date else None,
                'film_type': getattr(roll, 'film_type', '16mm'),
                'film_number': getattr(roll, 'film_number', None),
                'status': getattr(roll, 'status', 'active'),
                
                # Add temp roll relationship information for dependency indicators
                'source_temp_roll': {
                    'temp_roll_id': roll.source_temp_roll.temp_roll_id,
                    'capacity': roll.source_temp_roll.usable_capacity,
                    'status': roll.source_temp_roll.status
                } if roll.source_temp_roll else None,
                'created_temp_roll': {
                    'temp_roll_id': roll.created_temp_roll.temp_roll_id,
                    'capacity': roll.created_temp_roll.usable_capacity,
                    'status': roll.created_temp_roll.status
                } if roll.created_temp_roll else None,
                
                # Add debugging info for directory check
                'debug_directory_info': {
                    'has_output_directory': bool(getattr(roll, 'output_directory', None)),
                    'output_directory_path': getattr(roll, 'output_directory', None),
                    'directory_exists_check': roll.output_directory_exists if hasattr(roll, 'output_directory_exists') else 'property_missing'
                },
                # Add priority information
                'filming_priority': priority_info
            }
            
            # Include session information if requested
            if include_sessions:
                try:
                    sessions = FilmingSession.objects.filter(roll=roll).order_by('-created_at')[:5]  # Last 5 sessions
                    roll_info['recent_sessions'] = []
                    
                    for session in sessions:
                        session_info = {
                            'session_id': session.session_id,
                            'status': session.status,
                            'workflow_state': session.workflow_state,
                            'progress_percent': session.progress_percent,
                            'film_type': session.film_type,
                            'recovery_mode': session.recovery_mode,
                            'created_at': session.created_at.isoformat(),
                            'started_at': session.started_at.isoformat() if session.started_at else None,
                            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                            'duration': str(session.duration) if session.duration else None,
                            'error_message': session.error_message
                        }
                        roll_info['recent_sessions'].append(session_info)
                except Exception as e:
                    logger.warning(f"Error loading sessions for roll {roll.id}: {e}")
                    roll_info['recent_sessions'] = []
            
            roll_data.append(roll_info)
        
        return JsonResponse({
            'success': True,
            'project': {
                'id': project.id,
                'name': getattr(project, 'doc_type', 'Unknown') or getattr(project, 'name', f'Project {project.id}'),
                'folder_path': getattr(project, 'folder_path', ''),
                'archive_id': getattr(project, 'archive_id', 'N/A')
            },
            'rolls': roll_data,
            'total_rolls': len(roll_data)
        })
            
    except Exception as e:
        logger.error(f"Error getting project rolls: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'debug_error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def session_history(request):
    """Get filming session history with enhanced filtering and search."""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        status_filter = request.GET.get('status')
        project_filter = request.GET.get('project_id')
        user_filter = request.GET.get('user_id')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search = request.GET.get('search')
        
        # Build query
        sessions_query = FilmingSession.objects.select_related('project', 'roll', 'user').order_by('-created_at')
        
        # Apply filters
        if status_filter:
            sessions_query = sessions_query.filter(status=status_filter)
        
        if project_filter:
            try:
                project_id = int(project_filter)
                sessions_query = sessions_query.filter(project_id=project_id)
            except ValueError:
                pass
        
        if user_filter:
            try:
                user_id = int(user_filter)
                sessions_query = sessions_query.filter(user_id=user_id)
            except ValueError:
                pass
        
        # Date range filtering
        if date_from:
            try:
                from django.utils.dateparse import parse_datetime
                date_from_parsed = parse_datetime(date_from)
                if date_from_parsed:
                    sessions_query = sessions_query.filter(created_at__gte=date_from_parsed)
            except ValueError:
                pass
        
        if date_to:
            try:
                from django.utils.dateparse import parse_datetime
                date_to_parsed = parse_datetime(date_to)
                if date_to_parsed:
                    sessions_query = sessions_query.filter(created_at__lte=date_to_parsed)
            except ValueError:
                pass
        
        # Search functionality
        if search:
            sessions_query = sessions_query.filter(
                Q(project__name__icontains=search) |
                Q(roll__roll_number__icontains=search) |
                Q(session_id__icontains=search)
            )
        
        # Restrict to user's own sessions unless staff
        if not request.user.is_staff:
            sessions_query = sessions_query.filter(user=request.user)
        
        # Paginate
        paginator = Paginator(sessions_query, page_size)
        page_obj = paginator.get_page(page)
        
        # Format sessions
        session_data = []
        for session in page_obj:
            session_info = {
                'session_id': session.session_id,
                'project_name': session.project.name if session.project else None,
                'project_id': session.project.id if session.project else None,
                'roll_number': session.roll.roll_number if session.roll else None,
                'roll_id': session.roll.id if session.roll else None,
                'film_type': session.film_type,
                'status': session.status,
                'workflow_state': session.workflow_state,
                'progress_percent': session.progress_percent,
                'total_documents': session.total_documents,
                'processed_documents': session.processed_documents,
                'recovery_mode': session.recovery_mode,
                'created_at': session.created_at.isoformat(),
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'duration': str(session.duration) if session.duration else None,
                'error_message': session.error_message,
                'user_id': session.user_id,
                'user_username': session.user.username if session.user else None
            }
            session_data.append(session_info)
        
        return JsonResponse({
            'success': True,
            'sessions': session_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


# Function-based view wrappers for URL compatibility
@csrf_exempt
@login_required
def start_filming(request):
    """Start filming session - wrapper for SMAFilmingView.post()."""
    view = SMAFilmingView()
    view.request = request
    return view.post(request)


@csrf_exempt
@login_required
def control_filming(request):
    """Control filming session - wrapper for SMASessionView.patch()."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            if not session_id:
                return JsonResponse({
                    'success': False,
                    'error': 'session_id is required'
                }, status=400)
            
            view = SMASessionView()
            view.request = request
            return view.patch(request, session_id)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in control_filming: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)


@csrf_exempt
@login_required
def filming_status(request, session_id):
    """Get filming status - wrapper for SMASessionView.get()."""
    view = SMASessionView()
    view.request = request
    return view.get(request, session_id)


@csrf_exempt
@login_required
def filming_logs(request, session_id):
    """Get filming logs - alias for session_logs."""
    return session_logs(request, session_id)


@csrf_exempt
@login_required
def filming_progress(request, session_id):
    """Get filming progress - alias for filming_status."""
    return filming_status(request, session_id)


@csrf_exempt
@login_required
def active_sessions(request):
    """Get active sessions - wrapper for SMAFilmingView.get()."""
    view = SMAFilmingView()
    view.request = request
    return view.get(request)


@csrf_exempt
@login_required
def machine_status(request):
    """Get SMA machine status."""
    try:
        # This would check the actual SMA machine status
        # For now, return a basic status
        return JsonResponse({
            'success': True,
            'status': 'connected',
            'machine_type': 'SMA',
            'last_check': '2024-01-01T00:00:00Z'
        })
        
    except Exception as e:
        logger.error(f"Error getting machine status: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@csrf_exempt
@login_required
def test_sma_connection(request):
    """Test SMA machine connection."""
    try:
        result = SMAService.test_connection()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error testing SMA connection: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Connection test failed'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def pause_session(request, session_id):
    """Pause a filming session."""
    try:
        result = SMAService.pause_session(session_id)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error pausing session {session_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to pause session'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def resume_session(request, session_id):
    """Resume a paused filming session."""
    try:
        result = SMAService.resume_session(session_id)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error resuming session {session_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to resume session'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def cancel_session(request, session_id):
    """Cancel a filming session."""
    try:
        result = SMAService.cancel_session(session_id)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error cancelling session {session_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to cancel session'
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def sma_projects(request):
    """Get projects available for SMA filming."""
    try:
        # Add debugging information
        from ..models import Project
        
        # Get all projects for debugging
        all_projects = Project.objects.all()
        total_projects = all_projects.count()
        
        # Get projects that meet the criteria
        result = SMAService.get_filming_projects()
        
        # Add debugging info to the response
        if result['success']:
            result['debug_info'] = {
                'total_projects_in_db': total_projects,
                'user_authenticated': request.user.is_authenticated,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'user_username': request.user.username if request.user.is_authenticated else None
            }
            
            # Add sample of all projects for debugging
            if total_projects > 0:
                sample_projects = []
                for project in all_projects[:3]:  # First 3 projects
                    sample_projects.append({
                        'id': project.id,
                        'name': project.name,
                        'processing_complete': project.processing_complete,
                        'total_pages': project.total_pages,
                        'film_allocation_complete': getattr(project, 'film_allocation_complete', None)
                    })
                result['debug_info']['sample_all_projects'] = sample_projects
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error getting SMA projects: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to get projects',
            'debug_error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def all_rolls(request):
    """Get all rolls across all projects with their filming status and enhanced information."""
    try:
        # Get query parameters
        status_filter = request.GET.get('status')
        film_type_filter = request.GET.get('film_type')
        include_sessions = request.GET.get('include_sessions', 'false').lower() == 'true'
        sort_by_dependencies = request.GET.get('sort_dependencies', 'true').lower() == 'true'
        
        # Build query - get all rolls with project information
        rolls_query = Roll.objects.select_related('project').prefetch_related('source_temp_roll', 'created_temp_roll')
        
        if status_filter:
            rolls_query = rolls_query.filter(filming_status=status_filter)
            
        if film_type_filter:
            rolls_query = rolls_query.filter(film_type=film_type_filter)
        
        # Get all rolls first
        all_rolls = list(rolls_query)
        
        # Use FilmingOrderService for intelligent sorting when status is ready
        if sort_by_dependencies and (not status_filter or status_filter == 'ready'):
            from ..services import FilmingOrderService
            filming_order = FilmingOrderService.analyze_rolls_for_filming(rolls_query)
            
            # Flatten the filming order for response
            ordered_rolls = []
            # Add creator rolls first (highest priority)
            for roll, analysis in filming_order['creator_rolls']:
                ordered_rolls.append(roll)
            # Then immediate rolls
            for roll, analysis in filming_order['immediate_rolls']:
                ordered_rolls.append(roll)
            # Then waiting rolls
            for roll, analysis in filming_order['waiting_rolls']:
                ordered_rolls.append(roll)
            # Finally problem rolls
            for roll, analysis in filming_order['problem_rolls']:
                ordered_rolls.append(roll)
                
            all_rolls = ordered_rolls
        else:
            # Default sorting: creation date, archive ID, roll number
            all_rolls.sort(key=lambda r: (-r.creation_date.timestamp(), r.project.archive_id, r.roll_number or 0))
        
        roll_data = []
        for roll in all_rolls:
            # Get filming priority information
            from ..services import FilmingOrderService
            priority_info = FilmingOrderService.get_filming_priority(roll)
            
            # Use getattr with defaults for fields that might not exist
            roll_info = {
                'id': roll.id,
                'roll_number': getattr(roll, 'roll_number', None),
                'film_number': getattr(roll, 'film_number', None),
                'film_type': getattr(roll, 'film_type', '16mm'),
                'filming_status': getattr(roll, 'filming_status', 'ready'),
                'filming_progress_percent': getattr(roll, 'filming_progress_percent', 0.0),
                'filming_started_at': roll.filming_started_at.isoformat() if getattr(roll, 'filming_started_at', None) else None,
                'filming_completed_at': roll.filming_completed_at.isoformat() if getattr(roll, 'filming_completed_at', None) else None,
                'capacity': getattr(roll, 'capacity', 0),
                'pages_used': getattr(roll, 'pages_used', 0),
                'pages_remaining': getattr(roll, 'pages_remaining', 0),
                'document_count': getattr(roll, 'document_count', 0),
                'output_directory': getattr(roll, 'output_directory', None),
                'output_directory_exists': roll.output_directory_exists if hasattr(roll, 'output_directory_exists') else False,
                'created_at': roll.creation_date.isoformat() if hasattr(roll, 'creation_date') and roll.creation_date else None,
                'status': getattr(roll, 'status', 'active'),
                # Project information
                'project_id': roll.project.id if roll.project else None,
                'project_name': getattr(roll.project, 'name', None) or getattr(roll.project, 'doc_type', None) or f'Project {roll.project.id}' if roll.project else 'Unknown Project',
                'project_archive_id': getattr(roll.project, 'archive_id', 'Unknown') if roll.project else 'Unknown',
                'project_location': getattr(roll.project, 'location', 'Unknown') if roll.project else 'Unknown',
                # Check if this is a re-filming operation (completed rolls can be re-filmed)
                'is_re_filming': getattr(roll, 'filming_status', 'ready') == 'completed',
                
                # Add temp roll relationship information for dependency indicators
                'source_temp_roll': {
                    'temp_roll_id': roll.source_temp_roll.temp_roll_id,
                    'capacity': roll.source_temp_roll.usable_capacity,
                    'status': roll.source_temp_roll.status
                } if roll.source_temp_roll else None,
                'created_temp_roll': {
                    'temp_roll_id': roll.created_temp_roll.temp_roll_id,
                    'capacity': roll.created_temp_roll.usable_capacity,
                    'status': roll.created_temp_roll.status
                } if roll.created_temp_roll else None,
                
                # Add debugging info for directory check
                'debug_directory_info': {
                    'has_output_directory': bool(getattr(roll, 'output_directory', None)),
                    'output_directory_path': getattr(roll, 'output_directory', None),
                    'directory_exists_check': roll.output_directory_exists if hasattr(roll, 'output_directory_exists') else 'property_missing'
                },
                # Add priority information
                'filming_priority': priority_info
            }
            
            # Include session information if requested
            if include_sessions:
                try:
                    sessions = FilmingSession.objects.filter(roll=roll).order_by('-created_at')[:5]  # Last 5 sessions
                    roll_info['recent_sessions'] = []
                    
                    for session in sessions:
                        session_info = {
                            'session_id': session.session_id,
                            'status': session.status,
                            'workflow_state': session.workflow_state,
                            'progress_percent': session.progress_percent,
                            'film_type': session.film_type,
                            'recovery_mode': session.recovery_mode,
                            'created_at': session.created_at.isoformat(),
                            'started_at': session.started_at.isoformat() if session.started_at else None,
                            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                            'duration': str(session.duration) if session.duration else None,
                            'error_message': session.error_message
                        }
                        roll_info['recent_sessions'].append(session_info)
                except Exception as e:
                    logger.warning(f"Error loading sessions for roll {roll.id}: {e}")
                    roll_info['recent_sessions'] = []
            
            roll_data.append(roll_info)
        
        return JsonResponse({
            'success': True,
            'rolls': roll_data,
            'total_rolls': len(roll_data),
            'filters_applied': {
                'status': status_filter,
                'film_type': film_type_filter,
                'include_sessions': include_sessions
            }
        })
            
    except Exception as e:
        logger.error(f"Error getting all rolls: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'debug_error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def temp_roll_preview(request):
    """Get temp roll strategy preview for re-filming without making changes."""
    try:
        data = json.loads(request.body)
        
        # Extract parameters
        roll_id = data.get('roll_id')
        film_type = data.get('film_type', '16mm')
        required_pages = data.get('required_pages', 0)
        preview_only = data.get('preview_only', True)
        
        # Validation
        if not roll_id:
            return JsonResponse({
                'success': False,
                'error': 'roll_id is required'
            }, status=400)
        
        if not isinstance(required_pages, int) or required_pages <= 0:
            return JsonResponse({
                'success': False,
                'error': 'required_pages must be a positive integer'
            }, status=400)
        
        # Get temp roll strategy from service
        result = SMAService.get_temp_roll_strategy(
            roll_id=roll_id,
            film_type=film_type,
            required_pages=required_pages,
            preview_only=preview_only
        )
        
        if result['success']:
            logger.info(f"Temp roll preview generated for roll {roll_id}: {result['temp_roll_strategy']['use_temp_roll']}")
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error generating temp roll preview: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'details': str(e) if settings.DEBUG else 'An unexpected error occurred'
        }, status=500)
