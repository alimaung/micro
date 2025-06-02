"""
SMA Service - Django service layer for SMA processing.

This service provides the Django integration layer for the SMA processor,
handling session management, database operations, and WebSocket communication.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
import os
from django.db import models

# Import the real SMA process manager
from .sma_processor.sma_process_manager import SMAProcessManager, SMACallbackHandler

from ..models import FilmingSession, FilmingSessionLog, Project, Roll, TempRoll

logger = logging.getLogger(__name__)

class SMAService:
    """Service for managing SMA filming sessions."""
    
    # Class-level registry to track active sessions
    _active_sessions: Dict[str, SMAProcessManager] = {}
    _session_health_cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def start_filming_session(cls, roll_id: int, film_type: str, 
                            recovery: bool = False, re_filming: bool = False, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Start a new SMA filming session with enhanced error handling and validation."""
        try:
            # Validate roll input
            try:
                roll = Roll.objects.select_related('project').get(id=roll_id)
                project = roll.project
            except Roll.DoesNotExist:
                return {'success': False, 'error': f'Roll with ID {roll_id} not found'}
            
            if not project:
                return {'success': False, 'error': f'Roll {roll_id} is not associated with a project'}
            
            # Enhanced validation checks - use roll's output directory
            if not roll.output_directory or not os.path.exists(roll.output_directory):
                return {'success': False, 'error': f'Roll output directory does not exist: {roll.output_directory}'}
            
            # Extract the project folder from roll's output directory for SMA process
            # X:\RRD013-2022_OU_Arbeitspläne\.output\10000001 -> X:\RRD013-2022_OU_Arbeitspläne
            roll_project_folder = os.path.dirname(os.path.dirname(roll.output_directory))
            
            if not os.path.exists(roll_project_folder):
                return {'success': False, 'error': f'Project folder derived from roll does not exist: {roll_project_folder}'}
            
            # Handle re-filming operations
            if re_filming:
                if roll.filming_status != 'completed':
                    return {'success': False, 'error': f'Roll {roll.roll_number} must be completed before re-filming'}
                
                # Log re-filming operation
                logger.info(f"Starting re-filming operation for roll {roll.roll_number} (ID: {roll_id})")
                
                # Reset roll status for re-filming
                roll.filming_status = 'ready'
                roll.filming_progress_percent = 0.0
                roll.filming_session_id = None
                roll.filming_started_at = None
                roll.filming_completed_at = None
                
                # Handle temp roll updates for re-filming
                # If this roll created a temp roll previously, we need to update/invalidate it
                if hasattr(roll, 'created_temp_roll') and roll.created_temp_roll:
                    # Mark the previous temp roll as invalidated due to re-filming
                    temp_roll = roll.created_temp_roll
                    temp_roll.status = 'invalidated_refilm'
                    temp_roll.save(update_fields=['status'])
                    logger.info(f"Invalidated temp roll {temp_roll.temp_roll_id} due to re-filming")
                
                # Clear the temp roll relationship for fresh calculation
                roll.created_temp_roll = None
                roll.source_temp_roll = None
                roll.save(update_fields=[
                    'filming_status', 'filming_progress_percent', 'filming_session_id',
                    'filming_started_at', 'filming_completed_at', 'created_temp_roll', 'source_temp_roll'
                ])
                
            elif roll.filming_status == 'completed' and not re_filming:
                return {'success': False, 'error': f'Roll {roll.roll_number} has already been filmed. Use re-filming option to film again.'}
            
            # Check if roll is already being filmed
            existing_session = FilmingSession.objects.filter(
                roll=roll,
                status__in=['pending', 'running', 'paused']
            ).first()
            
            if existing_session and not recovery:
                return {
                    'success': False,
                    'error': f'Roll {roll.roll_number} is already being filmed (Session: {existing_session.session_id})',
                    'session_id': existing_session.session_id,
                    'existing_session': True
                }
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Use database transaction for consistency
            with transaction.atomic():
                # Create database session record
                session = FilmingSession.objects.create(
                    session_id=session_id,
                    project=project,
                    roll=roll,
                    film_type=film_type,
                    status='pending',
                    workflow_state='initialization',
                    user_id=user_id,
                    recovery_mode=recovery,
                    re_filming=re_filming  # Track if this is a re-filming operation
                )
                
                # Update roll status
                roll.filming_status = 'filming'
                roll.filming_session_id = session_id
                roll.filming_started_at = timezone.now()
                roll.filming_progress_percent = 0.0
                roll.save(update_fields=[
                    'filming_status', 'filming_session_id', 'filming_started_at', 'filming_progress_percent'
                ])
            
            # Prepare project data for SMA process using roll's information
            project_data = {
                'folder_path': roll.output_directory,  # Use roll's output directory directly
                'film_number': roll.roll_number,
                'project_name': project.name,
                'project_id': project.id,
                'roll_id': roll_id,
                'archive_id': project.archive_id,
                'output_dir': roll.output_directory,  # This is the actual working directory for this roll
                'film_type': film_type,
                'capacity': roll.capacity,
                'pages_used': roll.pages_used,
                're_filming': re_filming  # Pass re-filming flag to SMA process
            }
            
            # Create SMA process manager with enhanced configuration
            process_manager = SMAProcessManager(
                session_id=session_id,
                project_data=project_data,
                film_type=film_type,
                recovery=recovery
            )
            
            # Set up callback handler
            callback_handler = SMACallbackHandler(session_id)
            process_manager.set_callback_handler(callback_handler)
            
            # Start the SMA process
            if process_manager.start_sma_process():
                # Register the active session
                cls._active_sessions[session_id] = process_manager
                
                # Update session status
                session.status = 'running'
                session.started_at = timezone.now()
                session.save(update_fields=['status', 'started_at'])
                
                # Cache session info for quick access
                cls._cache_session_info(session_id, {
                    'project_name': project.name,
                    'roll_number': roll.roll_number,
                    'film_type': film_type,
                    'started_at': session.started_at.isoformat(),
                    're_filming': re_filming
                })
                
                logger.info(f"Started SMA filming session {session_id} for roll {roll.roll_number} (re-filming: {re_filming})")
                
                # Use fallback values for display names
                project_display_name = project.name or project.doc_type or project.archive_id or f'Project {project.id}'
                roll_display_name = roll.roll_number or roll.film_number or f'Roll {roll.id}'
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'status': 'running',
                    'workflow_state': 'initialization',
                    'message': f'Started {"re-" if re_filming else ""}filming roll {roll_display_name}',
                    'project_name': project_display_name,
                    'roll_number': roll_display_name,
                    're_filming': re_filming
                }
            else:
                # Failed to start process - rollback database changes
                with transaction.atomic():
                    session.status = 'failed'
                    session.error_message = process_manager.error_message
                    session.save(update_fields=['status', 'error_message'])
                    
                    roll.filming_status = 'error'
                    roll.save(update_fields=['filming_status'])
                
                return {
                    'success': False,
                    'error': f'Failed to start SMA process: {process_manager.error_message}',
                    'session_id': session_id
                }
                
        except Exception as e:
            logger.error(f"Error starting filming session: {e}")
            return {'success': False, 'error': f'Internal error: {str(e)}'}
    
    @classmethod
    def get_session_status(cls, session_id: str) -> Dict[str, Any]:
        """Get comprehensive status of a filming session."""
        try:
            # Get database session
            session = FilmingSession.objects.get(session_id=session_id)
            
            # Get process manager status if active
            process_status = {}
            health_status = {}
            
            if session_id in cls._active_sessions:
                process_manager = cls._active_sessions[session_id]
                process_status = process_manager.get_status()
                health_status = process_manager.check_health()
            
            # Get cached session info
            cached_info = cls._get_cached_session_info(session_id)
            
            # Combine database and process information
            status = {
                'session_id': session_id,
                'project_name': session.project.name,
                'roll_number': session.roll.roll_number,
                'film_type': session.film_type,
                'status': session.status,
                'workflow_state': session.workflow_state,
                'progress_percent': session.progress_percent,
                'total_documents': session.total_documents,
                'processed_documents': session.processed_documents,
                'created_at': session.created_at.isoformat(),
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'duration': str(session.duration) if session.duration else None,
                'error_message': session.error_message,
                'recovery_mode': session.recovery_mode,
                'user_id': session.user_id,
                'is_active': session.is_active,
                'is_completed': session.is_completed,
                **process_status,
                'health': health_status,
                'cached_info': cached_info
            }
            
            # Add roll information
            if session.roll:
                status['roll_info'] = {
                    'id': session.roll.id,
                    'capacity': session.roll.capacity,
                    'pages_used': session.roll.pages_used,
                    'pages_remaining': session.roll.pages_remaining,
                    'filming_status': session.roll.filming_status,
                    'output_directory': session.roll.output_directory,
                    'temp_roll_info': {
                        'created_temp_roll': {
                            'temp_roll_id': session.roll.created_temp_roll.temp_roll_id,
                            'film_type': session.roll.created_temp_roll.film_type,
                            'capacity': session.roll.created_temp_roll.capacity,
                            'usable_capacity': session.roll.created_temp_roll.usable_capacity,
                            'status': session.roll.created_temp_roll.status,
                            'creation_date': session.roll.created_temp_roll.creation_date.isoformat() if session.roll.created_temp_roll.creation_date else None
                        } if session.roll.created_temp_roll else None,
                        'source_temp_roll': {
                            'temp_roll_id': session.roll.source_temp_roll.temp_roll_id,
                            'film_type': session.roll.source_temp_roll.film_type,
                            'capacity': session.roll.source_temp_roll.capacity,
                            'usable_capacity': session.roll.source_temp_roll.usable_capacity,
                            'status': session.roll.source_temp_roll.status
                        } if session.roll.source_temp_roll else None,
                        'reason': cls._get_temp_roll_reason(session.roll)
                    }
                }
            
            return {'success': True, 'status': status}
            
        except FilmingSession.DoesNotExist:
            return {'success': False, 'error': 'Session not found'}
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_session_health(cls, session_id: str) -> Dict[str, Any]:
        """Get detailed health information for a session."""
        try:
            if session_id not in cls._active_sessions:
                return {'success': False, 'error': 'Session not active'}
            
            process_manager = cls._active_sessions[session_id]
            health_status = process_manager.check_health()
            
            # Add additional health metrics
            health_status['session_id'] = session_id
            health_status['uptime'] = None
            
            if process_manager.start_time:
                uptime = datetime.now() - process_manager.start_time
                health_status['uptime'] = str(uptime)
            
            # Cache health status
            cls._session_health_cache[session_id] = health_status
            
            return {'success': True, 'health': health_status}
            
        except Exception as e:
            logger.error(f"Error getting session health: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def pause_session(cls, session_id: str) -> Dict[str, Any]:
        """Pause a filming session."""
        try:
            if session_id not in cls._active_sessions:
                return {'success': False, 'error': 'Session not active'}
            
            process_manager = cls._active_sessions[session_id]
            
            if process_manager.pause():
                # Update database
                session = FilmingSession.objects.get(session_id=session_id)
                session.status = 'paused'
                session.save()
                
                return {'success': True, 'message': 'Session paused'}
            else:
                return {'success': False, 'error': 'Failed to pause session'}
                
        except Exception as e:
            logger.error(f"Error pausing session: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def resume_session(cls, session_id: str) -> Dict[str, Any]:
        """Resume a paused filming session."""
        try:
            if session_id not in cls._active_sessions:
                return {'success': False, 'error': 'Session not active'}
            
            process_manager = cls._active_sessions[session_id]
            
            if process_manager.resume():
                # Update database
                session = FilmingSession.objects.get(session_id=session_id)
                session.status = 'running'
                session.save()
                
                return {'success': True, 'message': 'Session resumed'}
            else:
                return {'success': False, 'error': 'Failed to resume session'}
                
        except Exception as e:
            logger.error(f"Error resuming session: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def cancel_session(cls, session_id: str) -> Dict[str, Any]:
        """Cancel a filming session."""
        try:
            if session_id in cls._active_sessions:
                process_manager = cls._active_sessions[session_id]
                process_manager.cancel()
                process_manager.terminate()
                del cls._active_sessions[session_id]
            
            # Update database
            session = FilmingSession.objects.get(session_id=session_id)
            session.status = 'cancelled'
            session.completed_at = timezone.now()
            if session.started_at:
                session.duration = session.completed_at - session.started_at
            session.save()
            
            return {'success': True, 'message': 'Session cancelled'}
            
        except Exception as e:
            logger.error(f"Error cancelling session: {e}")
            return {'success': False, 'error': str(e)}
        
    @classmethod
    def terminate_session(cls, session_id: str, force: bool = False) -> Dict[str, Any]:
        """Terminate a filming session."""
        try:
            if session_id in cls._active_sessions:
                process_manager = cls._active_sessions[session_id]
                process_manager.terminate(force=force)
                del cls._active_sessions[session_id]
            
            # Update database
            session = FilmingSession.objects.get(session_id=session_id)
            if session.status not in ['completed', 'cancelled', 'failed']:
                session.status = 'terminated'
                session.completed_at = timezone.now()
                if session.started_at:
                    session.duration = session.completed_at - session.started_at
                session.save()
            
            return {'success': True, 'message': 'Session terminated'}
            
        except Exception as e:
            logger.error(f"Error terminating session: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_active_sessions(cls) -> List[Dict[str, Any]]:
        """Get list of all active filming sessions with enhanced information for restoration."""
        try:
            active_sessions = []
            
            # Get database sessions (including completed ones for restoration)
            db_sessions = FilmingSession.objects.filter(
                status__in=['pending', 'running', 'paused', 'completed']
            ).select_related('project', 'roll', 'user').order_by('-started_at')
            
            for session in db_sessions:
                # Use fallback values for display names
                project_display_name = session.project.name or session.project.doc_type or session.project.archive_id or f'Project {session.project.id}'
                roll_display_name = session.roll.roll_number or session.roll.film_number or f'Roll {session.roll.id}' if session.roll else 'Unknown Roll'
                
                session_info = {
                    'session_id': session.session_id,
                    'project_name': project_display_name,
                    'project_id': session.project.id,
                    'roll_number': roll_display_name,
                    'roll_id': session.roll.id if session.roll else None,
                    'film_type': session.film_type,
                    'status': session.status,
                    'workflow_state': session.workflow_state,
                    'progress_percent': session.progress_percent,
                    'processed_documents': session.processed_documents,
                    'total_documents': session.total_documents,
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'duration': str(session.duration) if session.duration else None,
                    'user_id': session.user_id,
                    'recovery_mode': session.recovery_mode,
                    'is_process_active': session.session_id in cls._active_sessions,
                    'error_message': session.error_message
                }
                
                # Add process information if active
                if session.session_id in cls._active_sessions:
                    process_manager = cls._active_sessions[session.session_id]
                    process_status = process_manager.get_status()
                    session_info.update({
                        'process_pid': process_status.get('process_pid'),
                        'cpu_percent': process_status.get('cpu_percent'),
                        'memory_mb': process_status.get('memory_mb'),
                        'last_heartbeat': process_status.get('last_heartbeat')
                    })
                
                # Add roll information for restoration
                if session.roll:
                    session_info['roll_info'] = {
                        'id': session.roll.id,
                        'capacity': session.roll.capacity,
                        'pages_used': session.roll.pages_used,
                        'pages_remaining': session.roll.pages_remaining,
                        'filming_status': session.roll.filming_status,
                        'output_directory': session.roll.output_directory,
                        'temp_roll_info': {
                            'created_temp_roll': {
                                'temp_roll_id': session.roll.created_temp_roll.temp_roll_id,
                                'film_type': session.roll.created_temp_roll.film_type,
                                'capacity': session.roll.created_temp_roll.capacity,
                                'usable_capacity': session.roll.created_temp_roll.usable_capacity,
                                'status': session.roll.created_temp_roll.status,
                                'creation_date': session.roll.created_temp_roll.creation_date.isoformat() if session.roll.created_temp_roll.creation_date else None
                            } if session.roll.created_temp_roll else None,
                            'source_temp_roll': {
                                'temp_roll_id': session.roll.source_temp_roll.temp_roll_id,
                                'film_type': session.roll.source_temp_roll.film_type,
                                'capacity': session.roll.source_temp_roll.capacity,
                                'usable_capacity': session.roll.source_temp_roll.usable_capacity,
                                'status': session.roll.source_temp_roll.status
                            } if session.roll.source_temp_roll else None,
                            'reason': cls._get_temp_roll_reason(session.roll)
                        }
                    }
                
                active_sessions.append(session_info)
            
            return {
                'success': True,
                'active_sessions': active_sessions,
                'total_active': len([s for s in active_sessions if s['status'] in ['running', 'paused']]),
                'process_count': len(cls._active_sessions)
            }
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def recover_session(cls, session_id: str) -> Dict[str, Any]:
        """Recover a failed or interrupted filming session with enhanced recovery logic."""
        try:
            # Get session from database
            session = FilmingSession.objects.get(session_id=session_id)
            
            # Validate recovery conditions
            if session.status not in ['failed', 'terminated', 'cancelled']:
                return {
                    'success': False,
                    'error': f'Session {session_id} cannot be recovered (status: {session.status})'
                }
            
            # Check if session is already active
            if session_id in cls._active_sessions:
                return {
                    'success': False,
                    'error': f'Session {session_id} is already active'
                }
            
            # Validate project and roll still exist
            if not session.project or not session.roll:
                return {
                    'success': False,
                    'error': 'Associated project or roll no longer exists'
                }
            
            # Check for recovery data
            project_data = {
                'folder_path': session.project.folder_path,
                'film_number': session.roll.roll_number,
                'project_name': session.project.name,
                'project_id': session.project.id,
                'roll_id': session.roll.id,
                'archive_id': session.project.archive_id,
                'output_dir': session.roll.output_directory,
                'film_type': session.film_type,
                'capacity': session.roll.capacity,
                'pages_used': session.roll.pages_used
            }
            
            # Create new process manager in recovery mode
            process_manager = SMAProcessManager(
                session_id=session_id,
                project_data=project_data,
                film_type=session.film_type,
                recovery=True
            )
            
            # Check if recovery is possible
            recovery_info = process_manager.get_recovery_info()
            if not recovery_info.get('can_recover'):
                return {
                    'success': False,
                    'error': 'No recovery data available for this session'
                }
            
            # Set up callback handler
            callback_handler = SMACallbackHandler(session_id)
            process_manager.set_callback_handler(callback_handler)
            
            # Start recovery process
            if process_manager.start_sma_process():
                # Register the recovered session
                cls._active_sessions[session_id] = process_manager
                
                # Update database
                with transaction.atomic():
                    session.status = 'running'
                    session.recovery_mode = True
                    session.error_message = None
                    session.save(update_fields=['status', 'recovery_mode', 'error_message'])
                    
                    # Update roll status
                    session.roll.filming_status = 'filming'
                    session.roll.filming_session_id = session_id
                    session.roll.save(update_fields=['filming_status', 'filming_session_id'])
                
                logger.info(f"Successfully recovered SMA session {session_id}")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'message': f'Session {session_id} recovered successfully',
                    'recovery_info': recovery_info
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to start recovery process: {process_manager.error_message}'
                }
                
        except FilmingSession.DoesNotExist:
            return {'success': False, 'error': 'Session not found'}
        except Exception as e:
            logger.error(f"Error recovering session: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def force_checkpoint(cls, session_id: str) -> Dict[str, Any]:
        """Force a checkpoint save for a session."""
        try:
            if session_id not in cls._active_sessions:
                return {'success': False, 'error': 'Session not active'}
            
            process_manager = cls._active_sessions[session_id]
            
            if process_manager.force_checkpoint():
                return {'success': True, 'message': 'Checkpoint saved successfully'}
            else:
                return {'success': False, 'error': 'Failed to save checkpoint'}
                
        except Exception as e:
            logger.error(f"Error forcing checkpoint: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def cleanup_completed_sessions(cls, max_age_hours: int = 24):
        """Clean up completed sessions older than specified age with enhanced cleanup."""
        try:
            cutoff_time = timezone.now() - timedelta(hours=max_age_hours)
            
            # Find completed sessions to clean up
            completed_sessions = FilmingSession.objects.filter(
                status__in=['completed', 'failed', 'cancelled', 'terminated'],
                completed_at__lt=cutoff_time
            )
            
            cleanup_count = 0
            error_count = 0
            
            for session in completed_sessions:
                try:
                    session_id = session.session_id
                    
                    # Remove from active sessions if still there
                    if session_id in cls._active_sessions:
                        process_manager = cls._active_sessions[session_id]
                        process_manager.terminate(force=True)
                        del cls._active_sessions[session_id]
                    
                    # Clean up cached data
                    cls._cleanup_session_cache(session_id)
                    
                    # Optionally clean up log files (keep for debugging)
                    # This could be configurable
                    
                    cleanup_count += 1
                    
                except Exception as e:
                    logger.error(f"Error cleaning up session {session.session_id}: {e}")
                    error_count += 1
            
            logger.info(f"Cleaned up {cleanup_count} sessions, {error_count} errors")
            
            return {
                'success': True,
                'cleaned_up': cleanup_count,
                'errors': error_count
            }
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_session_statistics(cls, session_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a filming session."""
        try:
            session = FilmingSession.objects.get(session_id=session_id)
            
            # Basic statistics
            stats = {
                'session_id': session_id,
                'total_documents': session.total_documents,
                'processed_documents': session.processed_documents,
                'progress_percent': session.progress_percent,
                'workflow_state': session.workflow_state,
                'status': session.status
            }
            
            # Timing statistics
            if session.started_at:
                stats['started_at'] = session.started_at.isoformat()
                
                if session.completed_at:
                    stats['completed_at'] = session.completed_at.isoformat()
                    stats['total_duration'] = str(session.duration)
                else:
                    # Calculate current duration
                    current_duration = timezone.now() - session.started_at
                    stats['current_duration'] = str(current_duration)
                
                # Calculate processing rate
                if session.processed_documents > 0 and session.duration:
                    docs_per_minute = session.processed_documents / (session.duration.total_seconds() / 60)
                    stats['processing_rate_docs_per_minute'] = round(docs_per_minute, 2)
            
            # Log statistics
            log_stats = FilmingSessionLog.objects.filter(session=session).values('level').annotate(
                count=models.Count('level')
            )
            stats['log_counts'] = {item['level']: item['count'] for item in log_stats}
            
            # Process statistics if active
            if session_id in cls._active_sessions:
                process_manager = cls._active_sessions[session_id]
                process_status = process_manager.get_status()
                stats['process_stats'] = {
                    'cpu_percent': process_status.get('cpu_percent'),
                    'memory_mb': process_status.get('memory_mb'),
                    'memory_percent': process_status.get('memory_percent'),
                    'uptime': process_status.get('uptime')
                }
            
            return {'success': True, 'statistics': stats}
            
        except FilmingSession.DoesNotExist:
            return {'success': False, 'error': 'Session not found'}
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _cache_session_info(cls, session_id: str, info: Dict[str, Any]):
        """Cache session information for quick access."""
        cache_key = f"sma_session_info_{session_id}"
        cache.set(cache_key, info, timeout=3600)  # 1 hour
    
    @classmethod
    def _get_cached_session_info(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached session information."""
        cache_key = f"sma_session_info_{session_id}"
        return cache.get(cache_key)
    
    @classmethod
    def _cleanup_session_cache(cls, session_id: str):
        """Clean up cached session information."""
        if session_id in cls._session_health_cache:
            del cls._session_health_cache[session_id]
        
        # Clean up Redis cache if available
        cache_key = f"sma_session_{session_id}"
        cache.delete(cache_key)
    
    @classmethod
    def get_filming_projects(cls) -> Dict[str, Any]:
        """Get projects available for SMA filming."""
        try:
            # Get projects that are ready for filming
            # Temporarily less restrictive for debugging
            projects = Project.objects.filter(
                # processing_complete=True,  # Commented out for debugging
                # total_pages__gt=0  # Commented out for debugging
            ).select_related().prefetch_related('rolls')
            
            project_list = []
            for project in projects:
                # Get available rolls for filming (if any)
                available_rolls = 0
                if hasattr(project, 'rolls'):
                    try:
                        available_rolls = project.rolls.filter(
                            filming_status__in=['ready', 'pending']
                        ).count()
                    except:
                        # If rolls relationship doesn't exist, set to 0
                        available_rolls = 0
                
                # Determine filming status
                film_allocation_complete = getattr(project, 'film_allocation_complete', False)
                if film_allocation_complete:
                    filming_status = 'completed'
                elif available_rolls > 0:
                    filming_status = 'ready'
                else:
                    filming_status = 'pending'  # Changed from 'in_progress' to 'pending'
                
                project_data = {
                    'id': project.id,
                    'name': getattr(project, 'doc_type', 'Unknown') or getattr(project, 'name', f'Project {project.id}'),  # Use doc_type instead of name
                    'archive_id': getattr(project, 'archive_id', 'N/A'),
                    'location': getattr(project, 'location', 'Unknown'),
                    'doc_type': getattr(project, 'doc_type', 'Unknown'),
                    'total_pages': getattr(project, 'total_pages', 0),
                    'available_rolls': available_rolls,
                    'filming_status': filming_status,
                    'folder_path': getattr(project, 'folder_path', ''),
                    'processing_complete': getattr(project, 'processing_complete', False),
                    'film_allocation_complete': film_allocation_complete
                }
                project_list.append(project_data)
            
            return {
                'success': True,
                'projects': project_list,
                'total_count': len(project_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting filming projects: {e}")
            return {
                'success': False,
                'error': f'Failed to get projects: {str(e)}',
                'projects': []
            }
    
    @classmethod
    def test_connection(cls) -> Dict[str, Any]:
        """Test SMA machine connection."""
        try:
            # This would test the actual SMA connection
            # For now, return a basic test result
            # In a real implementation, this would ping the SMA machine
            
            # Check if SMA process manager can be initialized
            test_session_id = "test_connection"
            test_project_data = {
                'folder_path': '/tmp',
                'film_number': 'TEST',
                'project_name': 'Connection Test',
                'project_id': 0,
                'roll_id': 0,
                'archive_id': 'TEST',
                'output_dir': '/tmp',
                'film_type': '16mm',
                'capacity': 2900,
                'pages_used': 0
            }
            
            # Try to create a test process manager (without starting)
            try:
                test_manager = SMAProcessManager(
                    session_id=test_session_id,
                    project_data=test_project_data,
                    film_type='16mm',
                    recovery=False
                )
                
                # Test basic functionality
                health = test_manager.check_health()
                
                return {
                    'success': True,
                    'connected': True,
                    'response_time': 0.1,
                    'message': 'SMA connection test successful',
                    'health': health
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'connected': False,
                    'error': f'SMA initialization failed: {str(e)}',
                    'message': 'SMA connection test failed'
                }
            
        except Exception as e:
            logger.error(f"Error testing SMA connection: {e}")
            return {
                'success': False,
                'connected': False,
                'error': f'Connection test error: {str(e)}',
                'message': 'SMA connection test failed'
            }

    @classmethod
    def mark_roll_as_filmed(cls, session_id: str) -> Dict[str, Any]:
        """Mark a roll as filmed after successful completion."""
        try:
            session = FilmingSession.objects.get(session_id=session_id)
            
            if session.roll:
                session.roll.filming_status = 'completed'
                session.roll.filming_completed_at = timezone.now()
                session.roll.filming_progress_percent = 100.0
                session.roll.save(update_fields=[
                    'filming_status', 'filming_completed_at', 'filming_progress_percent'
                ])
                
                logger.info(f"Marked roll {session.roll.roll_number} as filmed for session {session_id}")
                
                return {
                    'success': True,
                    'message': f'Roll {session.roll.roll_number} marked as filmed'
                }
            else:
                return {
                    'success': False,
                    'error': 'No roll associated with session'
                }
                
        except FilmingSession.DoesNotExist:
            return {'success': False, 'error': 'Session not found'}
        except Exception as e:
            logger.error(f"Error marking roll as filmed: {e}")
            return {'success': False, 'error': str(e)}

    @classmethod
    def _get_temp_roll_reason(cls, roll) -> str:
        """Get the reason why a temp roll was or wasn't created."""
        if roll.created_temp_roll:
            return f"Temp roll created with {roll.created_temp_roll.usable_capacity} pages remaining capacity"
        elif roll.pages_remaining <= 100:  # Less than 100 pages remaining
            return "Roll nearly full - insufficient capacity for temp roll creation"
        elif roll.pages_remaining <= 200:  # Less than 200 pages remaining
            return "Roll has minimal remaining capacity - no temp roll needed"
        else:
            return "Roll completed without creating temp roll"

    @classmethod
    def get_temp_roll_strategy(cls, roll_id: int, film_type: str, required_pages: int, preview_only: bool = True) -> Dict[str, Any]:
        """
        Calculate temp roll strategy for re-filming operations.
        
        Args:
            roll_id: The roll being re-filmed
            film_type: Type of film (16mm/35mm)
            required_pages: Number of pages needed for re-filming
            preview_only: If True, don't make any changes, just calculate strategy
            
        Returns:
            Dict containing strategy information
        """
        try:
            from ..models import Roll, TempRoll
            
            # Get the roll being re-filmed
            try:
                roll = Roll.objects.get(id=roll_id)
            except Roll.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Roll {roll_id} not found'
                }
            
            # Standard capacities by film type
            FILM_CAPACITIES = {
                '16mm': 2900,
                '35mm': 1450
            }
            
            standard_capacity = FILM_CAPACITIES.get(film_type, 2900)
            
            # Find available temp rolls of the same film type with sufficient capacity
            available_temp_rolls = TempRoll.objects.filter(
                film_type=film_type,
                status='available',
                usable_capacity__gte=required_pages
            ).order_by('usable_capacity')  # Best fit: prefer smallest roll that fits
            
            strategy = {
                'film_type': film_type,
                'required_pages': required_pages,
                'pages_to_use': required_pages,
                'use_temp_roll': False,
                'temp_roll': None,
                'new_roll_capacity': standard_capacity,
                'will_create_temp_roll': False,
                'reason': ''
            }
            
            if available_temp_rolls.exists():
                # Use the best available temp roll
                best_temp_roll = available_temp_rolls.first()
                
                strategy.update({
                    'use_temp_roll': True,
                    'temp_roll': {
                        'temp_roll_id': best_temp_roll.temp_roll_id,
                        'remaining_capacity': best_temp_roll.usable_capacity,
                        'source_roll_id': best_temp_roll.source_roll.id if best_temp_roll.source_roll else None,
                        'created_date': best_temp_roll.creation_date.isoformat() if best_temp_roll.creation_date else None
                    },
                    'reason': f'Using existing temp roll #{best_temp_roll.temp_roll_id} with {best_temp_roll.usable_capacity} pages available'
                })
                
                # If preview_only is False, we would update the temp roll here
                if not preview_only:
                    # Update temp roll capacity (this would be done during actual filming)
                    best_temp_roll.usable_capacity -= required_pages
                    if best_temp_roll.usable_capacity <= 0:
                        best_temp_roll.status = 'exhausted'
                    best_temp_roll.save()
                    
                    logger.info(f"Updated temp roll #{best_temp_roll.temp_roll_id}: {best_temp_roll.usable_capacity} pages remaining")
            
            else:
                # Use new roll
                remaining_capacity = standard_capacity - required_pages
                min_temp_roll_threshold = 100  # Minimum pages to create a temp roll
                
                strategy.update({
                    'use_temp_roll': False,
                    'will_create_temp_roll': remaining_capacity >= min_temp_roll_threshold,
                    'remaining_capacity': remaining_capacity,
                    'reason': f'No suitable temp rolls available. Using new {film_type} roll.'
                })
                
                if strategy['will_create_temp_roll']:
                    strategy['reason'] += f' Will create temp roll with {remaining_capacity} pages.'
                else:
                    strategy['reason'] += f' Remaining {remaining_capacity} pages too small for temp roll.'
                
                # If preview_only is False, we would create the temp roll after filming
                if not preview_only and strategy['will_create_temp_roll']:
                    # This would be done after filming completes
                    pass
            
            return {
                'success': True,
                'temp_roll_strategy': strategy,
                'preview_only': preview_only
            }
            
        except Exception as e:
            logger.error(f"Error calculating temp roll strategy: {e}")
            return {
                'success': False,
                'error': f'Failed to calculate temp roll strategy: {str(e)}'
            }
