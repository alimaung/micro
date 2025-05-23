import subprocess
import threading
import time
import json
import uuid
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from .notification_service import NotificationService
import logging
import os
import sys

logger = logging.getLogger(__name__)

class SMAService:
    """
    Service for controlling SMA filming processes.
    Manages filming sessions, progress tracking, and real-time updates.
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.active_sessions = {}  # In-memory session tracking
        
    def start_filming_process(self, project_data, film_type='16', recovery=False, user_id=None):
        """
        Start a new filming process or recover an existing one.
        
        Args:
            project_data (dict): Project information including folder_path, project_name
            film_type (str): '16' or '35' for film template
            recovery (bool): Whether this is a recovery session
            user_id (str): User identifier for notifications
            
        Returns:
            dict: Session information with session_id, status, etc.
        """
        session_id = str(uuid.uuid4())
        
        try:
            # Prepare session data
            session_data = {
                'session_id': session_id,
                'project_data': project_data,
                'film_type': film_type,
                'recovery': recovery,
                'user_id': user_id,
                'status': 'initializing',
                'created_at': datetime.now().isoformat(),
                'current_step': 'initialization',
                'progress_percent': 0,
                'processed_documents': 0,
                'total_documents': project_data.get('total_documents', 0),
                'logs': [],
                'eta': None,
                'processing_rate': 0
            }
            
            # Store session in cache and memory
            self._store_session_data(session_id, session_data)
            self.active_sessions[session_id] = session_data
            
            # Start the SMA process in a separate thread
            sma_thread = threading.Thread(
                target=self._run_sma_process,
                args=(session_id, project_data, film_type, recovery),
                daemon=True
            )
            sma_thread.start()
            
            # Send initial notification
            if user_id:
                self.notification_service.send_notification(
                    user_id=user_id,
                    title="SMA Process Started",
                    message=f"Filming process initiated for {project_data.get('project_name', 'Unknown Project')}",
                    notification_type='sma_started',
                    data={'session_id': session_id}
                )
            
            logger.info(f"Started SMA filming session {session_id}")
            return {
                'success': True,
                'session_id': session_id,
                'status': 'initializing',
                'message': 'Filming process started successfully'
            }
            
        except Exception as e:
            logger.error(f"Error starting SMA process: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to start filming process'
            }
    
    def control_filming_process(self, session_id, action, user_id=None):
        """
        Control an active filming process (pause, resume, cancel).
        
        Args:
            session_id (str): Session identifier
            action (str): 'pause', 'resume', 'cancel'
            user_id (str): User identifier
            
        Returns:
            dict: Operation result
        """
        try:
            session_data = self._get_session_data(session_id)
            if not session_data:
                return {
                    'success': False,
                    'error': 'Session not found',
                    'message': 'Invalid session ID'
                }
            
            current_status = session_data.get('status')
            
            if action == 'pause':
                if current_status in ['running', 'filming']:
                    session_data['status'] = 'paused'
                    session_data['paused_at'] = datetime.now().isoformat()
                    self._add_log_entry(session_id, 'Process paused by user')
                    
                    # Send pause notification
                    if user_id:
                        self.notification_service.send_notification(
                            user_id=user_id,
                            title="SMA Process Paused",
                            message="Filming process has been paused",
                            notification_type='sma_paused',
                            data={'session_id': session_id}
                        )
                    
                    return {'success': True, 'status': 'paused', 'message': 'Process paused'}
                else:
                    return {'success': False, 'message': 'Cannot pause process in current state'}
            
            elif action == 'resume':
                if current_status == 'paused':
                    session_data['status'] = 'running'
                    session_data['resumed_at'] = datetime.now().isoformat()
                    self._add_log_entry(session_id, 'Process resumed by user')
                    
                    # Send resume notification
                    if user_id:
                        self.notification_service.send_notification(
                            user_id=user_id,
                            title="SMA Process Resumed",
                            message="Filming process has been resumed",
                            notification_type='sma_resumed',
                            data={'session_id': session_id}
                        )
                    
                    return {'success': True, 'status': 'running', 'message': 'Process resumed'}
                else:
                    return {'success': False, 'message': 'Cannot resume process in current state'}
            
            elif action == 'cancel':
                session_data['status'] = 'cancelled'
                session_data['cancelled_at'] = datetime.now().isoformat()
                self._add_log_entry(session_id, 'Process cancelled by user')
                
                # Clean up active session
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                # Send cancellation notification
                if user_id:
                    self.notification_service.send_notification(
                        user_id=user_id,
                        title="SMA Process Cancelled",
                        message="Filming process has been cancelled",
                        notification_type='sma_cancelled',
                        data={'session_id': session_id}
                    )
                
                return {'success': True, 'status': 'cancelled', 'message': 'Process cancelled'}
            
            else:
                return {'success': False, 'message': 'Invalid action'}
            
        except Exception as e:
            logger.error(f"Error controlling SMA process {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        finally:
            # Update session data in cache
            if 'session_data' in locals():
                self._store_session_data(session_id, session_data)
    
    def get_session_status(self, session_id):
        """Get current status of a filming session."""
        session_data = self._get_session_data(session_id)
        if not session_data:
            return {'success': False, 'error': 'Session not found'}
        
        return {
            'success': True,
            'session_id': session_id,
            'status': session_data.get('status'),
            'current_step': session_data.get('current_step'),
            'progress_percent': session_data.get('progress_percent', 0),
            'processed_documents': session_data.get('processed_documents', 0),
            'total_documents': session_data.get('total_documents', 0),
            'eta': session_data.get('eta'),
            'processing_rate': session_data.get('processing_rate', 0),
            'created_at': session_data.get('created_at'),
            'project_data': session_data.get('project_data', {})
        }
    
    def get_session_logs(self, session_id, limit=100):
        """Get logs for a filming session."""
        session_data = self._get_session_data(session_id)
        if not session_data:
            return {'success': False, 'error': 'Session not found'}
        
        logs = session_data.get('logs', [])
        # Return most recent logs first
        recent_logs = logs[-limit:] if len(logs) > limit else logs
        
        return {
            'success': True,
            'session_id': session_id,
            'logs': recent_logs,
            'total_entries': len(logs)
        }
    
    def get_active_sessions(self, user_id=None):
        """Get all active filming sessions for a user."""
        try:
            # Get all sessions from cache that match user_id
            active_sessions = []
            cache_pattern = "sma_session:*"
            
            # This is a simplified approach - in production you'd want a better way to query sessions
            for session_id in self.active_sessions:
                session_data = self._get_session_data(session_id)
                if session_data and (not user_id or session_data.get('user_id') == user_id):
                    if session_data.get('status') in ['running', 'paused', 'initializing', 'filming']:
                        active_sessions.append({
                            'session_id': session_id,
                            'status': session_data.get('status'),
                            'project_name': session_data.get('project_data', {}).get('project_name'),
                            'progress_percent': session_data.get('progress_percent', 0),
                            'created_at': session_data.get('created_at')
                        })
            
            return {
                'success': True,
                'active_sessions': active_sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_sma_process(self, session_id, project_data, film_type, recovery):
        """
        Run the actual SMA process in a separate thread.
        This wraps the existing sma.py script and provides progress updates.
        """
        try:
            session_data = self._get_session_data(session_id)
            session_data['status'] = 'running'
            self._add_log_entry(session_id, 'SMA process thread started')
            
            # Import the SMA main function
            # Adjust the path to your SMA script location
            sma_script_path = os.path.join(settings.BASE_DIR, 'sma', 'processor', 'sma.py')
            
            # Prepare arguments for SMA script
            folder_path = project_data.get('folder_path')
            template = film_type
            filmnumber = project_data.get('film_number')
            
            # Create a mock args object similar to what SMA expects
            class SMArgs:
                def __init__(self):
                    self.folder_path = folder_path
                    self.template = template
                    self.filmnumber = filmnumber
                    self.recovery = recovery
            
            # This is a simplified approach - you'd need to modify the sma.py script
            # to accept a callback function for progress updates
            self._run_sma_with_callbacks(session_id, SMArgs())
            
        except Exception as e:
            logger.error(f"Error in SMA process thread {session_id}: {str(e)}")
            session_data = self._get_session_data(session_id)
            if session_data:
                session_data['status'] = 'error'
                session_data['error'] = str(e)
                self._add_log_entry(session_id, f'Error: {str(e)}')
                self._store_session_data(session_id, session_data)
    
    def _run_sma_with_callbacks(self, session_id, args):
        """
        Modified SMA execution with progress callbacks.
        This would need integration with the actual sma.py script.
        """
        # This is a placeholder - you'd need to modify the SMA script
        # to accept progress callback functions
        
        # For now, simulate the process with mock progress
        self._simulate_sma_process(session_id)
    
    def _simulate_sma_process(self, session_id):
        """
        Simulate SMA process for testing - replace with actual SMA integration.
        """
        session_data = self._get_session_data(session_id)
        total_docs = session_data.get('total_documents', 100)
        
        steps = ['initialization', 'preparation', 'filming', 'end_symbols', 'transport', 'completion']
        
        for step_idx, step in enumerate(steps):
            session_data['current_step'] = step
            self._add_log_entry(session_id, f'Starting {step} phase')
            
            if step == 'filming':
                # Simulate document processing
                for progress in range(0, 101, 2):
                    # Check if process was cancelled or paused
                    current_data = self._get_session_data(session_id)
                    if current_data.get('status') == 'cancelled':
                        return
                    
                    while current_data.get('status') == 'paused':
                        time.sleep(1)
                        current_data = self._get_session_data(session_id)
                        if current_data.get('status') == 'cancelled':
                            return
                    
                    # Update progress
                    session_data['progress_percent'] = progress
                    session_data['processed_documents'] = int((progress / 100) * total_docs)
                    session_data['processing_rate'] = 2.5 + (progress * 0.01)  # Mock rate
                    
                    # Calculate ETA
                    if progress > 0:
                        remaining_percent = 100 - progress
                        estimated_seconds = (remaining_percent / 2) * 30  # Mock calculation
                        eta = datetime.now() + timedelta(seconds=estimated_seconds)
                        session_data['eta'] = eta.isoformat()
                    
                    # Send progress notifications based on SMA notification logic
                    self._handle_progress_notifications(session_id, progress)
                    
                    # Log every 10%
                    if progress % 10 == 0:
                        self._add_log_entry(
                            session_id, 
                            f'Progress: {progress}% ({session_data["processed_documents"]}/{total_docs})'
                        )
                    
                    self._store_session_data(session_id, session_data)
                    time.sleep(0.5)  # Simulate processing time
            else:
                # Other steps take fixed time
                time.sleep(2)
            
            self._add_log_entry(session_id, f'Completed {step} phase')
        
        # Mark as completed
        session_data['status'] = 'completed'
        session_data['progress_percent'] = 100
        session_data['completed_at'] = datetime.now().isoformat()
        self._add_log_entry(session_id, 'SMA process completed successfully')
        
        # Send completion notification
        user_id = session_data.get('user_id')
        if user_id:
            self.notification_service.send_notification(
                user_id=user_id,
                title="SMA Process Complete",
                message=f"Filming completed for {session_data.get('project_data', {}).get('project_name', 'project')}",
                notification_type='sma_completed',
                data={'session_id': session_id}
            )
        
        self._store_session_data(session_id, session_data)
        
        # Clean up from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def _handle_progress_notifications(self, session_id, progress):
        """Handle progress-based notifications following SMA notification logic."""
        session_data = self._get_session_data(session_id)
        user_id = session_data.get('user_id')
        
        if not user_id:
            return
        
        # Implement the notification logic from the SMA script
        # Every 2% until 90%, then PREP notifications
        if progress < 90 and progress % 2 == 0 and progress > 0:
            eta_str = session_data.get('eta', 'N/A')
            remaining = session_data.get('total_documents', 0) - session_data.get('processed_documents', 0)
            
            self.notification_service.send_firebase_notification(
                title="RUNNING",
                message=f"{progress}% complete, {remaining} frames remaining, ETA: {eta_str}",
                message_id="process"
            )
        
        elif progress >= 90:
            # Handle PREP notifications
            if progress >= 90 and not session_data.get('prep1_sent'):
                self.notification_service.send_firebase_notification(
                    title="PREP1",
                    message="Process almost done, please prepare",
                    message_id="prep"
                )
                session_data['prep1_sent'] = True
            elif progress >= 93 and not session_data.get('prep2_sent'):
                self.notification_service.send_firebase_notification(
                    title="PREP2",
                    message="Process almost done, please prepare",
                    message_id="prep"
                )
                session_data['prep2_sent'] = True
            elif progress >= 96 and not session_data.get('prep3_sent'):
                self.notification_service.send_firebase_notification(
                    title="PREP3",
                    message="Process almost done, please prepare",
                    message_id="prep"
                )
                session_data['prep3_sent'] = True
    
    def _store_session_data(self, session_id, session_data):
        """Store session data in cache with expiration."""
        cache_key = f"sma_session:{session_id}"
        cache.set(cache_key, session_data, timeout=86400)  # 24 hours
        
        # Also update in-memory store
        self.active_sessions[session_id] = session_data
    
    def _get_session_data(self, session_id):
        """Retrieve session data from cache or memory."""
        cache_key = f"sma_session:{session_id}"
        session_data = cache.get(cache_key)
        
        if not session_data and session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
        
        return session_data
    
    def _add_log_entry(self, session_id, message, level='info'):
        """Add a log entry to the session."""
        session_data = self._get_session_data(session_id)
        if session_data:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'level': level
            }
            
            if 'logs' not in session_data:
                session_data['logs'] = []
            
            session_data['logs'].append(log_entry)
            self._store_session_data(session_id, session_data)
            
            # Also log to Django logger
            logger.info(f"SMA Session {session_id}: {message}")

# Singleton instance
sma_service = SMAService()
