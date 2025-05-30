"""
SMA Process Manager - Manages SMA subprocess lifecycle and communication.

This module provides the bridge between the Django web service and the standalone
SMA processor, handling process lifecycle, real-time communication, and state management.
"""

import subprocess
import threading
import time
import json
import os
import signal
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class SMAProcessManager:
    """Manages SMA subprocess lifecycle and communication."""
    
    def __init__(self, session_id: str, project_data: Dict[str, Any], film_type: str, recovery: bool = False):
        self.session_id = session_id
        self.project_data = project_data
        self.film_type = film_type
        self.recovery = recovery
        
        # Process management
        self.process: Optional[subprocess.Popen] = None
        self.process_pid: Optional[int] = None
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
        # Communication
        self.callback_handler: Optional['SMACallbackHandler'] = None
        self.progress_thread: Optional[threading.Thread] = None
        self.log_thread: Optional[threading.Thread] = None
        
        # State tracking
        self.current_workflow_state = 'initialization'
        self.current_progress = 0.0
        self.total_documents = 0
        self.processed_documents = 0
        self.error_message: Optional[str] = None
        
        # File paths
        self.sma_script_path = self._get_sma_script_path()
        self.log_file_path = self._get_log_file_path()
        self.progress_file_path = self._get_progress_file_path()
        
    def _get_sma_script_path(self) -> str:
        """Get the path to the SMA script."""
        current_dir = Path(__file__).parent
        return str(current_dir / "sma.py")
    
    def _get_log_file_path(self) -> str:
        """Get the path for SMA process logs."""
        log_dir = Path(__file__).parent / "logs" / "sessions"
        log_dir.mkdir(parents=True, exist_ok=True)
        return str(log_dir / f"sma_session_{self.session_id}.log")
    
    def _get_progress_file_path(self) -> str:
        """Get the path for progress communication file."""
        progress_dir = Path(__file__).parent / "progress"
        progress_dir.mkdir(parents=True, exist_ok=True)
        return str(progress_dir / f"progress_{self.session_id}.json")
    
    def set_callback_handler(self, handler: 'SMACallbackHandler'):
        """Set the callback handler for progress updates."""
        self.callback_handler = handler
    
    def start_sma_process(self) -> bool:
        """Start the SMA subprocess with callback integration."""
        try:
            logger.info(f"Starting SMA process for session {self.session_id}")
            
            # Prepare command arguments
            cmd_args = self._build_command_args()
            
            # Set up environment variables for communication
            env = os.environ.copy()
            env['SMA_SESSION_ID'] = self.session_id
            env['SMA_PROGRESS_FILE'] = self.progress_file_path
            env['SMA_CALLBACK_MODE'] = 'true'
            
            # Start the SMA process
            self.process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=Path(self.sma_script_path).parent
            )
            
            self.process_pid = self.process.pid
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info(f"SMA process started with PID {self.process_pid}")
            
            # Start monitoring threads
            self._start_monitoring_threads()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SMA process: {e}")
            self.error_message = str(e)
            return False
    
    def _build_command_args(self) -> list:
        """Build command line arguments for SMA process."""
        args = [
            'python',
            self.sma_script_path,
            self.project_data['folder_path'],
            self.film_type
        ]
        
        # Add optional arguments
        if self.project_data.get('film_number'):
            args.extend(['--filmnumber', self.project_data['film_number']])
        
        if self.recovery:
            args.append('--recovery')
        
        return args
    
    def _start_monitoring_threads(self):
        """Start threads to monitor SMA process output and progress."""
        # Progress monitoring thread
        self.progress_thread = threading.Thread(
            target=self._monitor_progress,
            daemon=True
        )
        self.progress_thread.start()
        
        # Log monitoring thread
        self.log_thread = threading.Thread(
            target=self._monitor_logs,
            daemon=True
        )
        self.log_thread.start()
    
    def _monitor_progress(self):
        """Monitor progress updates from SMA process."""
        logger.info(f"Starting progress monitoring for session {self.session_id}")
        
        while self.is_running and self.process and self.process.poll() is None:
            try:
                # Check for progress file updates
                if os.path.exists(self.progress_file_path):
                    with open(self.progress_file_path, 'r') as f:
                        progress_data = json.load(f)
                    
                    # Update internal state
                    self._update_progress_state(progress_data)
                    
                    # Notify callback handler
                    if self.callback_handler:
                        self.callback_handler.on_progress_update(progress_data)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring progress: {e}")
                time.sleep(5)  # Wait longer on error
        
        logger.info(f"Progress monitoring stopped for session {self.session_id}")
    
    def _monitor_logs(self):
        """Monitor log output from SMA process."""
        logger.info(f"Starting log monitoring for session {self.session_id}")
        
        if not self.process:
            return
        
        try:
            # Monitor stdout
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': line.strip(),
                    'source': 'sma_stdout'
                }
                
                # Write to log file
                self._write_log_entry(log_entry)
                
                # Notify callback handler
                if self.callback_handler:
                    self.callback_handler.on_log_entry(log_entry)
                
                # Check for workflow state changes
                self._check_workflow_state_change(line.strip())
        
        except Exception as e:
            logger.error(f"Error monitoring logs: {e}")
        
        logger.info(f"Log monitoring stopped for session {self.session_id}")
    
    def _update_progress_state(self, progress_data: Dict[str, Any]):
        """Update internal progress state."""
        old_workflow_state = self.current_workflow_state
        
        self.current_progress = progress_data.get('progress_percent', 0.0)
        self.total_documents = progress_data.get('total_documents', 0)
        self.processed_documents = progress_data.get('processed_documents', 0)
        
        new_workflow_state = progress_data.get('workflow_state', self.current_workflow_state)
        
        # Check for workflow state change
        if new_workflow_state != old_workflow_state:
            self.current_workflow_state = new_workflow_state
            if self.callback_handler:
                self.callback_handler.on_workflow_state_change(old_workflow_state, new_workflow_state)
    
    def _check_workflow_state_change(self, log_line: str):
        """Check log line for workflow state changes."""
        workflow_indicators = {
            'initialization': ['Starting application', 'Application started', 'Initializing'],
            'monitoring': ['Starting to monitor progress', 'Progress monitoring started'],
            'advanced_finish': ['PREP mode triggered', 'Advanced finish', 'frames remaining'],
            'completed': ['Process completed', 'Script completed successfully']
        }
        
        for state, indicators in workflow_indicators.items():
            if any(indicator.lower() in log_line.lower() for indicator in indicators):
                if state != self.current_workflow_state:
                    old_state = self.current_workflow_state
                    self.current_workflow_state = state
                    if self.callback_handler:
                        self.callback_handler.on_workflow_state_change(old_state, state)
                break
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write log entry to file."""
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing log entry: {e}")
    
    def send_command(self, command: str, **kwargs) -> bool:
        """Send control commands to SMA process."""
        try:
            if not self.is_running or not self.process:
                return False
            
            command_data = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            # For now, we'll use file-based communication
            # In the future, this could be enhanced with named pipes or sockets
            command_file = Path(self.progress_file_path).parent / f"command_{self.session_id}.json"
            
            with open(command_file, 'w') as f:
                json.dump(command_data, f)
            
            logger.info(f"Sent command '{command}' to SMA process {self.process_pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to SMA process: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause the SMA process."""
        return self.send_command('pause')
    
    def resume(self) -> bool:
        """Resume the SMA process."""
        return self.send_command('resume')
    
    def cancel(self) -> bool:
        """Cancel the SMA process."""
        return self.send_command('cancel')
    
    def get_status(self) -> Dict[str, Any]:
        """Get current SMA process status."""
        status = {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'process_pid': self.process_pid,
            'workflow_state': self.current_workflow_state,
            'progress_percent': self.current_progress,
            'total_documents': self.total_documents,
            'processed_documents': self.processed_documents,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'error_message': self.error_message
        }
        
        # Add process-specific information if available
        if self.process:
            status['process_return_code'] = self.process.poll()
            
            # Get process resource usage if available
            try:
                if self.process_pid and psutil.pid_exists(self.process_pid):
                    proc = psutil.Process(self.process_pid)
                    status['cpu_percent'] = proc.cpu_percent()
                    status['memory_mb'] = proc.memory_info().rss / 1024 / 1024
            except Exception:
                pass  # Ignore errors getting process info
        
        return status
    
    def terminate(self, force: bool = False) -> bool:
        """Safely terminate SMA process."""
        try:
            logger.info(f"Terminating SMA process for session {self.session_id}")
            
            self.is_running = False
            
            if self.process:
                if force:
                    # Force kill
                    self.process.kill()
                    logger.info(f"Force killed SMA process {self.process_pid}")
                else:
                    # Graceful termination
                    self.process.terminate()
                    
                    # Wait for process to terminate
                    try:
                        self.process.wait(timeout=30)  # Wait up to 30 seconds
                        logger.info(f"SMA process {self.process_pid} terminated gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if graceful termination fails
                        self.process.kill()
                        logger.warning(f"Force killed SMA process {self.process_pid} after timeout")
            
            # Clean up monitoring threads
            if self.progress_thread and self.progress_thread.is_alive():
                self.progress_thread.join(timeout=5)
            
            if self.log_thread and self.log_thread.is_alive():
                self.log_thread.join(timeout=5)
            
            # Clean up temporary files
            self._cleanup_files()
            
            return True
            
        except Exception as e:
            logger.error(f"Error terminating SMA process: {e}")
            return False
    
    def _cleanup_files(self):
        """Clean up temporary communication files."""
        try:
            files_to_clean = [
                self.progress_file_path,
                Path(self.progress_file_path).parent / f"command_{self.session_id}.json"
            ]
            
            for file_path in files_to_clean:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up file: {file_path}")
        
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self.is_running:
            self.terminate(force=True)


class SMACallbackHandler:
    """Handles callbacks from SMA process and broadcasts to WebSocket."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = logging.getLogger(f"{__name__}.{session_id}")
        
        # Import here to avoid circular imports
        try:
            from channels.layers import get_channel_layer
            self.channel_layer = get_channel_layer()
        except ImportError:
            self.channel_layer = None
            self.logger.warning("Django Channels not available - WebSocket broadcasting disabled")
    
    def on_progress_update(self, progress_data: Dict[str, Any]):
        """Handle progress updates from SMA."""
        self.logger.debug(f"Progress update: {progress_data}")
        
        # Update database
        self._update_database_progress(progress_data)
        
        # Broadcast to WebSocket
        if self.channel_layer:
            self._broadcast_progress_update(progress_data)
    
    def on_workflow_state_change(self, old_state: str, new_state: str):
        """Handle workflow state transitions."""
        self.logger.info(f"Workflow state change: {old_state} -> {new_state}")
        
        # Update database
        self._update_database_workflow_state(new_state)
        
        # Broadcast to WebSocket
        if self.channel_layer:
            self._broadcast_workflow_state_change(old_state, new_state)
    
    def on_log_entry(self, log_data: Dict[str, Any]):
        """Handle log entries from SMA."""
        self.logger.debug(f"Log entry: {log_data['message']}")
        
        # Store in database
        self._store_log_entry(log_data)
        
        # Broadcast to WebSocket
        if self.channel_layer:
            self._broadcast_log_entry(log_data)
    
    def _update_database_progress(self, progress_data: Dict[str, Any]):
        """Update filming session progress in database."""
        try:
            from django.apps import apps
            FilmingSession = apps.get_model('microapp', 'FilmingSession')
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            session.progress_percent = progress_data.get('progress_percent', 0.0)
            session.processed_documents = progress_data.get('processed_documents', 0)
            session.total_documents = progress_data.get('total_documents', 0)
            session.save(update_fields=['progress_percent', 'processed_documents', 'total_documents', 'updated_at'])
            
        except Exception as e:
            self.logger.error(f"Error updating database progress: {e}")
    
    def _update_database_workflow_state(self, new_state: str):
        """Update workflow state in database."""
        try:
            from django.apps import apps
            FilmingSession = apps.get_model('microapp', 'FilmingSession')
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            session.workflow_state = new_state
            
            # Update timing information based on state
            if new_state == 'monitoring' and not session.started_at:
                session.started_at = datetime.now()
                session.status = 'running'
            elif new_state == 'completed':
                session.completed_at = datetime.now()
                session.status = 'completed'
                if session.started_at:
                    session.duration = session.completed_at - session.started_at
            
            session.save()
            
        except Exception as e:
            self.logger.error(f"Error updating database workflow state: {e}")
    
    def _store_log_entry(self, log_data: Dict[str, Any]):
        """Store log entry in database."""
        try:
            from django.apps import apps
            FilmingSessionLog = apps.get_model('microapp', 'FilmingSessionLog')
            FilmingSession = apps.get_model('microapp', 'FilmingSession')
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            
            FilmingSessionLog.objects.create(
                session=session,
                level=log_data.get('level', 'info'),
                message=log_data.get('message', ''),
                workflow_state=log_data.get('workflow_state')
            )
            
        except Exception as e:
            self.logger.error(f"Error storing log entry: {e}")
    
    def _broadcast_progress_update(self, progress_data: Dict[str, Any]):
        """Broadcast progress update to WebSocket."""
        try:
            import asyncio
            from asgiref.sync import async_to_sync
            
            group_name = f"sma_session_{self.session_id}"
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_progress',
                    'session_id': self.session_id,
                    'progress': progress_data
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error broadcasting progress update: {e}")
    
    def _broadcast_workflow_state_change(self, old_state: str, new_state: str):
        """Broadcast workflow state change to WebSocket."""
        try:
            import asyncio
            from asgiref.sync import async_to_sync
            
            group_name = f"sma_session_{self.session_id}"
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_workflow_state',
                    'session_id': self.session_id,
                    'old_state': old_state,
                    'new_state': new_state
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error broadcasting workflow state change: {e}")
    
    def _broadcast_log_entry(self, log_data: Dict[str, Any]):
        """Broadcast log entry to WebSocket."""
        try:
            import asyncio
            from asgiref.sync import async_to_sync
            
            group_name = f"sma_session_{self.session_id}"
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_log',
                    'session_id': self.session_id,
                    'log': log_data
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error broadcasting log entry: {e}") 