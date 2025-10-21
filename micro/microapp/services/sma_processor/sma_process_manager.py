"""
SMA Process Manager - Manages SMA subprocess lifecycle and communication.

This module provides the bridge between the Django web service and the standalone
SMA processor, handling process lifecycle, real-time communication, and state management.

File Creation Control:
- By default, file creation is DISABLED (enable_file_creation=False)
- This prevents creation of log files, progress files, command files, checkpoint files, and W:/sma directories
- Set enable_file_creation=True to enable file-based communication and logging
- When disabled, the manager relies on stdout/stderr parsing for monitoring and WebSocket for communication
"""

import subprocess
import threading
import time
import json
import os
import signal
import psutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import logging
import shutil
import tempfile

logger = logging.getLogger(__name__)

class SMAProcessManager:
    """Manages SMA subprocess lifecycle and communication."""
    
    def __init__(self, session_id: str, project_data: Dict[str, Any], film_type: str, recovery: bool = False, enable_file_creation: bool = False):
        self.session_id = session_id
        self.project_data = project_data
        self.film_type = film_type
        self.recovery = recovery
        self.enable_file_creation = enable_file_creation  # Disabled by default
        
        # Process management
        self.process: Optional[subprocess.Popen] = None
        self.process_pid: Optional[int] = None
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.last_heartbeat: Optional[datetime] = None
        
        # Communication
        self.callback_handler: Optional['SMACallbackHandler'] = None
        self.progress_thread: Optional[threading.Thread] = None
        self.log_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # State tracking
        self.current_workflow_state = 'initialization'
        self.current_progress = 0.0
        self.total_documents = 0
        self.processed_documents = 0
        self.error_message: Optional[str] = None
        self.last_known_state: Dict[str, Any] = {}
        
        # Recovery and checkpointing
        self.checkpoint_interval = 30  # seconds
        self.last_checkpoint: Optional[datetime] = None
        self.recovery_data: Dict[str, Any] = {}
        
        # File paths
        self.sma_script_path = self._get_sma_script_path()
        self.log_file_path = self._get_log_file_path()
        self.progress_file_path = self._get_progress_file_path()
        self.checkpoint_file_path = self._get_checkpoint_file_path()
        self.command_pipe_path = self._get_command_pipe_path()
        
        # Process monitoring
        self.max_memory_mb = 2048  # Maximum memory usage in MB
        self.max_cpu_percent = 90  # Maximum CPU usage percentage
        self.heartbeat_timeout = 60  # seconds
        
    def _get_sma_script_path(self) -> str:
        """Get the path to the SMA script."""
        current_dir = Path(__file__).parent
        return str(current_dir / "sma.py")
    
    def _get_log_file_path(self) -> str:
        """Get the path for SMA process logs."""
        if not self.enable_file_creation:
            return None
        log_dir = Path("W:/sma") / "logs" / "sessions"
        log_dir.mkdir(parents=True, exist_ok=True)
        return str(log_dir / f"sma_session_{self.session_id}.log")
    
    def _get_progress_file_path(self) -> str:
        """Get the path for progress communication file."""
        if not self.enable_file_creation:
            return None
        progress_dir = Path("W:/sma") / "progress"
        progress_dir.mkdir(parents=True, exist_ok=True)
        return str(progress_dir / f"progress_{self.session_id}.json")
    
    def _get_checkpoint_file_path(self) -> str:
        """Get the path for checkpoint data."""
        if not self.enable_file_creation:
            return None
        checkpoint_dir = Path("W:/sma") / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return str(checkpoint_dir / f"checkpoint_{self.session_id}.json")
    
    def _get_command_pipe_path(self) -> str:
        """Get the path for command communication pipe."""
        if not self.enable_file_creation:
            return None
        pipe_dir = Path("W:/sma") / "pipes"
        pipe_dir.mkdir(parents=True, exist_ok=True)
        return str(pipe_dir / f"commands_{self.session_id}.pipe")
    
    def set_callback_handler(self, handler: 'SMACallbackHandler'):
        """Set the callback handler for progress updates."""
        self.callback_handler = handler
    
    def start_sma_process(self) -> bool:
        """Start the SMA subprocess with callback integration."""
        try:
            logger.info(f"Starting SMA process for session {self.session_id}")
            
            # Load recovery data if in recovery mode
            if self.recovery:
                self._load_recovery_data()
            
            # Prepare command arguments
            cmd_args = self._build_command_args()
            
            # Log the exact command for debugging
            logger.info(f"Starting SMA process with command: {' '.join(cmd_args)}")
            
            # Set up environment variables for communication
            env = os.environ.copy()
            env['SMA_SESSION_ID'] = self.session_id
            env['SMA_CALLBACK_MODE'] = 'true'
            env['SMA_RECOVERY_MODE'] = 'true' if self.recovery else 'false'
            env['SMA_FILE_CREATION_ENABLED'] = 'true' if self.enable_file_creation else 'false'
            
            # Only set file paths if file creation is enabled
            if self.enable_file_creation:
                if self.progress_file_path:
                    env['SMA_PROGRESS_FILE'] = self.progress_file_path
                if self.checkpoint_file_path:
                    env['SMA_CHECKPOINT_FILE'] = self.checkpoint_file_path
                if self.command_pipe_path:
                    env['SMA_COMMAND_PIPE'] = self.command_pipe_path
            
            # Create command pipe for two-way communication
            self._create_command_pipe()
            
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
            self.last_heartbeat = datetime.now()
            
            logger.info(f"SMA process started with PID {self.process_pid}")
            
            # Send initial log entries to frontend
            if self.callback_handler:
                initial_log = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': f"SMA process started with PID {self.process_pid}",
                    'source': 'process_manager'
                }
                self.callback_handler.on_log_entry(initial_log)
                
                command_log = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': f"Command: {' '.join(cmd_args)}",
                    'source': 'process_manager'
                }
                self.callback_handler.on_log_entry(command_log)
            
            # Start monitoring threads
            self._start_monitoring_threads()
            
            # Save initial checkpoint
            self._save_checkpoint()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SMA process: {e}")
            self.error_message = str(e)
            return False
    
    def _create_command_pipe(self):
        """Create a named pipe for command communication."""
        if not self.enable_file_creation or not self.command_pipe_path:
            return
            
        try:
            if os.path.exists(self.command_pipe_path):
                os.remove(self.command_pipe_path)
            
            # On Windows, use a temporary file instead of named pipe
            if os.name == 'nt':
                # Create an empty command file
                with open(self.command_pipe_path, 'w') as f:
                    json.dump({}, f)
            else:
                os.mkfifo(self.command_pipe_path)
                
        except Exception as e:
            logger.warning(f"Failed to create command pipe: {e}")
    
    def _load_recovery_data(self):
        """Load recovery data from checkpoint file."""
        if not self.enable_file_creation or not self.checkpoint_file_path:
            self.recovery_data = {}
            return
            
        try:
            if os.path.exists(self.checkpoint_file_path):
                with open(self.checkpoint_file_path, 'r') as f:
                    self.recovery_data = json.load(f)
                    
                logger.info(f"Loaded recovery data for session {self.session_id}")
                
                # Restore state from recovery data
                self.current_workflow_state = self.recovery_data.get('workflow_state', 'initialization')
                self.current_progress = self.recovery_data.get('progress', 0.0)
                self.total_documents = self.recovery_data.get('total_documents', 0)
                self.processed_documents = self.recovery_data.get('processed_documents', 0)
                
        except Exception as e:
            logger.error(f"Failed to load recovery data: {e}")
            self.recovery_data = {}
    
    def _save_checkpoint(self):
        """Save current state to checkpoint file."""
        if not self.enable_file_creation or not self.checkpoint_file_path:
            return
            
        try:
            checkpoint_data = {
                'session_id': self.session_id,
                'workflow_state': self.current_workflow_state,
                'progress': self.current_progress,
                'total_documents': self.total_documents,
                'processed_documents': self.processed_documents,
                'timestamp': datetime.now().isoformat(),
                'process_pid': self.process_pid,
                'project_data': self.project_data,
                'film_type': self.film_type
            }
            
            with open(self.checkpoint_file_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
            self.last_checkpoint = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def _build_command_args(self) -> list:
        """Build command line arguments for SMA process."""
        # Convert film type from '16mm'/'35mm' to '16'/'35' as expected by SMA script
        template_arg = self.film_type.replace('mm', '') if self.film_type else '16'
        
        args = [
            'python',
            self.sma_script_path,
            self.project_data['folder_path'],
            template_arg
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
        
        # Log monitoring thread (stdout)
        self.log_thread = threading.Thread(
            target=self._monitor_logs,
            daemon=True
        )
        self.log_thread.start()
        
        # Error monitoring thread (stderr)
        self.error_thread = threading.Thread(
            target=self._monitor_errors,
            daemon=True
        )
        self.error_thread.start()
        
        # Heartbeat thread
        self.heartbeat_thread = threading.Thread(
            target=self._monitor_heartbeat,
            daemon=True
        )
        self.heartbeat_thread.start()
    
    def _monitor_progress(self):
        """Monitor progress updates from SMA process."""
        logger.info(f"Starting progress monitoring for session {self.session_id}")
        
        while self.is_running and self.process and self.process.poll() is None:
            try:
                # Check for progress file updates only if file creation is enabled
                if self.enable_file_creation and self.progress_file_path and os.path.exists(self.progress_file_path):
                    with open(self.progress_file_path, 'r') as f:
                        progress_data = json.load(f)
                    
                    # Update internal state
                    self._update_progress_state(progress_data)
                    
                    # Notify callback handler
                    if self.callback_handler:
                        self.callback_handler.on_progress_update(progress_data)
                elif not self.enable_file_creation:
                    # When file creation is disabled, we rely solely on stdout parsing
                    # Progress updates will come through _monitor_logs via workflow state detection
                    pass
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring progress: {e}")
                time.sleep(5)  # Wait longer on error
        
        # Check if process completed
        if self.process and self.process.poll() is not None:
            exit_code = self.process.poll()
            logger.info(f"SMA process completed with exit code: {exit_code}")
            
            # Handle process completion
            if exit_code == 0:
                completion_data = {
                    'message': 'SMA process completed successfully',
                    'exit_code': exit_code,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id
                }
                if self.callback_handler:
                    self.callback_handler.on_completion(completion_data)
            else:
                error_data = {
                    'message': f'SMA process failed with exit code {exit_code}',
                    'exit_code': exit_code,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id
                }
                if self.callback_handler:
                    self.callback_handler.on_error(error_data)
        
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
                
                line = line.strip()
                if not line:
                    continue
                
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': line,
                    'source': 'sma_stdout'
                }
                
                # Parse special SMA messages
                if line.startswith('SMA_PROGRESS:'):
                    self._handle_progress_message(line)
                elif line.startswith('SMA_WORKFLOW_STATE:'):
                    self._handle_workflow_state_message(line)
                elif line.startswith('SMA_COMPLETION:'):
                    self._handle_completion_message(line)
                elif line.startswith('SMA_STATUS:'):
                    self._handle_status_message(line)
                else:
                    # Regular log entry
                    self._write_log_entry(log_entry)
                    
                    # Notify callback handler for all messages
                    if self.callback_handler:
                        self.callback_handler.on_log_entry(log_entry)
                
                # Update heartbeat for any activity
                self.last_heartbeat = datetime.now()
        
        except Exception as e:
            logger.error(f"Error monitoring logs: {e}")
        
        logger.info(f"Log monitoring stopped for session {self.session_id}")
    
    def _monitor_errors(self):
        """Monitor error output from SMA process stderr."""
        logger.info(f"Starting error monitoring for session {self.session_id}")
        
        if not self.process:
            return
        
        try:
            # Monitor stderr
            for line in iter(self.process.stderr.readline, ''):
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # All stderr output is treated as error level
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'error',
                    'message': line,
                    'source': 'sma_stderr'
                }
                
                # Write to log file
                self._write_log_entry(log_entry)
                
                # Notify callback handler for all error messages
                if self.callback_handler:
                    self.callback_handler.on_log_entry(log_entry)
                    
                    # Also trigger error handling for critical errors
                    if any(keyword in line.lower() for keyword in ['traceback', 'exception', 'fatal', 'critical']):
                        error_data = {
                            'message': f"SMA process error: {line}",
                            'timestamp': datetime.now().isoformat(),
                            'session_id': self.session_id,
                            'source': 'stderr'
                        }
                        self.callback_handler.on_error(error_data)
                
                # Update heartbeat for any activity
                self.last_heartbeat = datetime.now()
        
        except Exception as e:
            logger.error(f"Error monitoring stderr: {e}")
        
        logger.info(f"Error monitoring stopped for session {self.session_id}")
    
    def _handle_progress_message(self, line: str):
        """Handle SMA_PROGRESS messages."""
        try:
            # Extract progress from "SMA_PROGRESS: 25.5% (123/500)"
            progress_part = line.split('SMA_PROGRESS:')[1].strip()
            
            # Extract percentage
            percent_str = progress_part.split('%')[0].strip()
            progress_percent = float(percent_str)
            
            # Extract counts if available
            if '(' in progress_part and ')' in progress_part:
                counts_part = progress_part.split('(')[1].split(')')[0]
                if '/' in counts_part:
                    processed_str, total_str = counts_part.split('/')
                    processed_documents = int(processed_str.strip())
                    total_documents = int(total_str.strip())
                else:
                    processed_documents = 0
                    total_documents = 0
            else:
                processed_documents = 0
                total_documents = 0
            
            # Create progress data
            progress_data = {
                'progress_percent': progress_percent,
                'processed_documents': processed_documents,
                'total_documents': total_documents,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update internal state
            self._update_progress_state(progress_data)
            
            # Notify callback handler
            if self.callback_handler:
                self.callback_handler.on_progress_update(progress_data)
                
            logger.debug(f"Progress update: {progress_percent:.1f}% ({processed_documents}/{total_documents})")
            
        except Exception as e:
            logger.error(f"Error parsing progress message '{line}': {e}")
    
    def _handle_workflow_state_message(self, line: str):
        """Handle SMA_WORKFLOW_STATE messages."""
        try:
            # Extract state from "SMA_WORKFLOW_STATE: monitoring"
            new_state = line.split('SMA_WORKFLOW_STATE:')[1].strip()
            old_state = self.current_workflow_state
            
            if new_state != old_state:
                self.current_workflow_state = new_state
                
                # Notify callback handler
                if self.callback_handler:
                    self.callback_handler.on_workflow_state_change(old_state, new_state)
                
                logger.info(f"Workflow state changed: {old_state} -> {new_state}")
            
        except Exception as e:
            logger.error(f"Error parsing workflow state message '{line}': {e}")
    
    def _handle_completion_message(self, line: str):
        """Handle SMA_COMPLETION messages."""
        try:
            # Extract completion info from "SMA_COMPLETION: Process completed successfully with 500 frames"
            completion_info = line.split('SMA_COMPLETION:')[1].strip()
            
            completion_data = {
                'message': completion_info,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id
            }
            
            # Notify callback handler
            if self.callback_handler:
                self.callback_handler.on_completion(completion_data)
                
            logger.info(f"SMA process completed: {completion_info}")
            
        except Exception as e:
            logger.error(f"Error parsing completion message '{line}': {e}")
    
    def _handle_status_message(self, line: str):
        """Handle SMA_STATUS messages."""
        try:
            # Extract status from "SMA_STATUS: Starting progress monitoring"
            status_info = line.split('SMA_STATUS:')[1].strip()
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': status_info,
                'source': 'sma_status'
            }
            
            # Write to log file
            self._write_log_entry(log_entry)
            
            # Notify callback handler
            if self.callback_handler:
                self.callback_handler.on_log_entry(log_entry)
                
        except Exception as e:
            logger.error(f"Error parsing status message '{line}': {e}")
    
    def _monitor_heartbeat(self):
        """Monitor heartbeat to detect process hang."""
        logger.info(f"Starting heartbeat monitoring for session {self.session_id}")
        
        while self.is_running:
            try:
                if datetime.now() - self.last_heartbeat > timedelta(seconds=self.heartbeat_timeout):
                    logger.warning(f"Heartbeat timeout for session {self.session_id}")
                    self.is_running = False
                    break
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring heartbeat: {e}")
                time.sleep(5)  # Wait longer on error
        
        logger.info(f"Heartbeat monitoring stopped for session {self.session_id}")
    
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
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write log entry to file."""
        # Only write to file if file creation is enabled
        if not self.enable_file_creation or not self.log_file_path:
            return
            
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
            
            # If file creation is disabled, we can't send commands via files
            if not self.enable_file_creation or not self.command_pipe_path:
                logger.warning(f"Cannot send command '{command}' - file creation is disabled")
                return False
            
            command_data = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                **kwargs
            }
            
            # Use command pipe for communication
            if os.name == 'nt':
                # On Windows, use file-based communication
                with open(self.command_pipe_path, 'w') as f:
                    json.dump(command_data, f)
            else:
                # On Unix, use named pipe
                with open(self.command_pipe_path, 'w') as f:
                    f.write(json.dumps(command_data) + '\n')
            
            logger.info(f"Sent command '{command}' to SMA process {self.process_pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
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
        """Get comprehensive status of the SMA process."""
        status = {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'workflow_state': self.current_workflow_state,
            'progress_percent': self.current_progress,
            'total_documents': self.total_documents,
            'processed_documents': self.processed_documents,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'error_message': self.error_message,
            'process_pid': self.process_pid,
            'recovery_mode': self.recovery
        }
        
        # Add process resource information if available
        if self.process_pid and self.is_running:
            try:
                process = psutil.Process(self.process_pid)
                status.update({
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'memory_percent': process.memory_percent(),
                    'status': process.status(),
                    'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
                })
                
                # Check for resource issues
                if status['memory_mb'] > self.max_memory_mb:
                    status['warnings'] = status.get('warnings', [])
                    status['warnings'].append(f"High memory usage: {status['memory_mb']:.1f}MB")
                
                if status['cpu_percent'] > self.max_cpu_percent:
                    status['warnings'] = status.get('warnings', [])
                    status['warnings'].append(f"High CPU usage: {status['cpu_percent']:.1f}%")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status['process_status'] = 'not_found'
        
        return status
    
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the SMA process."""
        health_status = {
            'healthy': True,
            'issues': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if process is running
        if not self.is_running:
            health_status['healthy'] = False
            health_status['issues'].append('Process is not running')
            return health_status
        
        # Check process existence
        if self.process_pid:
            try:
                process = psutil.Process(self.process_pid)
                
                # Check memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > self.max_memory_mb:
                    health_status['warnings'].append(f'High memory usage: {memory_mb:.1f}MB')
                
                # Check CPU usage
                cpu_percent = process.cpu_percent()
                if cpu_percent > self.max_cpu_percent:
                    health_status['warnings'].append(f'High CPU usage: {cpu_percent:.1f}%')
                
                # Check heartbeat
                if self.last_heartbeat:
                    heartbeat_age = datetime.now() - self.last_heartbeat
                    if heartbeat_age > timedelta(seconds=self.heartbeat_timeout):
                        health_status['healthy'] = False
                        health_status['issues'].append(f'Heartbeat timeout: {heartbeat_age.total_seconds():.1f}s')
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                health_status['healthy'] = False
                health_status['issues'].append('Process not found or access denied')
        
        # Check file system health only if file creation is enabled
        if self.enable_file_creation:
            required_files = [self.progress_file_path, self.log_file_path]
            for file_path in required_files:
                if file_path and not os.path.exists(file_path):
                    health_status['warnings'].append(f'Missing file: {file_path}')
        else:
            health_status['warnings'].append('File creation is disabled - using memory-only monitoring')
        
        return health_status
    
    def force_checkpoint(self) -> bool:
        """Force save a checkpoint immediately."""
        if not self.enable_file_creation:
            logger.warning("Cannot force checkpoint - file creation is disabled")
            return False
            
        try:
            self._save_checkpoint()
            return True
        except Exception as e:
            logger.error(f"Failed to force checkpoint: {e}")
            return False
    
    def terminate(self, force: bool = False) -> bool:
        """Terminate the SMA process."""
        try:
            logger.info(f"Terminating SMA process {self.process_pid} (force={force})")
            
            self.is_running = False
            
            if self.process:
                if force:
                    # Force kill the process
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/F', '/PID', str(self.process_pid)], 
                                     capture_output=True)
                    else:
                        os.kill(self.process_pid, signal.SIGKILL)
                else:
                    # Graceful termination
                    self.send_command('terminate')
                    
                    # Wait for graceful shutdown
                    try:
                        self.process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Process {self.process_pid} did not terminate gracefully, forcing...")
                        if os.name == 'nt':
                            subprocess.run(['taskkill', '/F', '/PID', str(self.process_pid)], 
                                         capture_output=True)
                        else:
                            os.kill(self.process_pid, signal.SIGKILL)
                
                self.process = None
                self.process_pid = None
            
            # Wait for monitoring threads to finish
            if self.progress_thread and self.progress_thread.is_alive():
                self.progress_thread.join(timeout=5)
            
            if self.log_thread and self.log_thread.is_alive():
                self.log_thread.join(timeout=5)
            
            if hasattr(self, 'error_thread') and self.error_thread and self.error_thread.is_alive():
                self.error_thread.join(timeout=5)
            
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=5)
            
            # Save final checkpoint
            self._save_checkpoint()
            
            # Clean up temporary files
            self._cleanup_files()
            
            logger.info(f"SMA process {self.session_id} terminated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error terminating SMA process: {e}")
            return False
    
    def _cleanup_files(self):
        """Clean up temporary files and resources."""
        # Only clean up files if file creation was enabled
        if not self.enable_file_creation:
            return
            
        try:
            files_to_clean = []
            
            # Add files that exist
            if self.progress_file_path:
                files_to_clean.append(self.progress_file_path)
            if self.command_pipe_path:
                files_to_clean.append(self.command_pipe_path)
            
            # Don't clean up checkpoint and log files - they may be needed for recovery
            
            for file_path in files_to_clean:
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Cleaned up file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up file {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_recovery_info(self) -> Dict[str, Any]:
        """Get information needed for session recovery."""
        return {
            'session_id': self.session_id,
            'checkpoint_file': self.checkpoint_file_path,
            'log_file': self.log_file_path,
            'last_checkpoint': self.last_checkpoint.isoformat() if self.last_checkpoint else None,
            'recovery_data': self.recovery_data,
            'can_recover': (self.enable_file_creation and 
                           self.checkpoint_file_path and 
                           os.path.exists(self.checkpoint_file_path))
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self.is_running:
            self.terminate(force=True)


class SMACallbackHandler:
    """Handles callbacks from SMA process and integrates with Django."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_progress_update = None
        self.last_workflow_state = None
        
        # Import Django components here to avoid circular imports
        from django.core.cache import cache
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        self.cache = cache
        self.channel_layer = get_channel_layer()
        self.async_to_sync = async_to_sync
    
    def on_progress_update(self, progress_data: Dict[str, Any]):
        """Handle progress updates from SMA process."""
        try:
            # Update database
            self._update_database_progress(progress_data)
        
            # Cache the latest progress
            cache_key = f"sma_progress_{self.session_id}"
            self.cache.set(cache_key, progress_data, timeout=300)  # 5 minutes
            
            # Broadcast to WebSocket clients
            self._broadcast_progress_update(progress_data)
            
            # Store for comparison
            self.last_progress_update = progress_data
            
            logger.debug(f"Progress update processed for session {self.session_id}: {progress_data.get('progress_percent', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Error handling progress update: {e}")
    
    def on_workflow_state_change(self, old_state: str, new_state: str):
        """Handle workflow state changes from SMA process."""
        try:
            # Update database
            self._update_database_workflow_state(new_state)
        
            # Cache the state change
            cache_key = f"sma_workflow_state_{self.session_id}"
            state_data = {
                'old_state': old_state,
                'new_state': new_state,
                'timestamp': datetime.now().isoformat()
            }
            self.cache.set(cache_key, state_data, timeout=300)
            
            # Broadcast to WebSocket clients
            self._broadcast_workflow_state_change(old_state, new_state)
            
            # Store for comparison
            self.last_workflow_state = new_state
            
            logger.info(f"Workflow state changed for session {self.session_id}: {old_state} -> {new_state}")
            
        except Exception as e:
            logger.error(f"Error handling workflow state change: {e}")
    
    def on_log_entry(self, log_data: Dict[str, Any]):
        """Handle log entries from SMA process."""
        try:
            # Store log entry in database
            self._store_log_entry(log_data)
        
            # Broadcast ALL log entries to WebSocket clients for real-time viewing
            self._broadcast_log_entry(log_data)
            
            # Check for error conditions
            log_level = log_data.get('level', 'info')
            if log_level in ['error', 'critical']:
                self._handle_error_condition(log_data)
            
        except Exception as e:
            logger.error(f"Error handling log entry: {e}")
    
    def on_error(self, error_data: Dict[str, Any]):
        """Handle error conditions from SMA process."""
        try:
            # Update database with error
            self._update_database_error(error_data)
            
            # Broadcast error to WebSocket clients
            self._broadcast_error(error_data)
            
            # Trigger error recovery if configured
            self._trigger_error_recovery(error_data)
            
            logger.error(f"SMA process error for session {self.session_id}: {error_data}")
            
        except Exception as e:
            logger.error(f"Error handling SMA error: {e}")
    
    def on_completion(self, completion_data: Dict[str, Any]):
        """Handle completion of SMA process."""
        try:
            # Update database with completion
            self._update_database_completion(completion_data)
            
            # Broadcast completion to WebSocket clients
            self._broadcast_completion(completion_data)
            
            # Trigger post-completion tasks
            self._trigger_post_completion_tasks(completion_data)
            
            logger.info(f"SMA process completed for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error handling completion: {e}")
    
    def _update_database_progress(self, progress_data: Dict[str, Any]):
        """Update database with progress information."""
        try:
            from ...models import FilmingSession
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            
            # Update progress fields
            session.progress_percent = progress_data.get('progress_percent', 0.0)
            session.total_documents = progress_data.get('total_documents', 0)
            session.processed_documents = progress_data.get('processed_documents', 0)
            
            # Update workflow state if provided
            if 'workflow_state' in progress_data:
                session.workflow_state = progress_data['workflow_state']
            
            session.save(update_fields=[
                'progress_percent', 'total_documents', 'processed_documents', 
                'workflow_state', 'updated_at'
            ])
            
        except Exception as e:
            logger.error(f"Error updating database progress: {e}")
    
    def _update_database_workflow_state(self, new_state: str):
        """Update database with new workflow state."""
        try:
            from ...models import FilmingSession
            from django.utils import timezone
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            session.workflow_state = new_state
            
            # Update status based on workflow state
            if new_state == 'completed':
                session.status = 'completed'
                session.completed_at = timezone.now()
                
                # Calculate duration
                if session.started_at:
                    session.duration = session.completed_at - session.started_at
            
            session.save(update_fields=['workflow_state', 'status', 'completed_at', 'duration', 'updated_at'])
            
        except Exception as e:
            logger.error(f"Error updating database workflow state: {e}")
    
    def _update_database_error(self, error_data: Dict[str, Any]):
        """Update database with error information."""
        try:
            from ...models import FilmingSession
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            session.status = 'failed'
            session.error_message = error_data.get('message', 'Unknown error')
            session.save(update_fields=['status', 'error_message', 'updated_at'])
            
        except Exception as e:
            logger.error(f"Error updating database with error: {e}")
    
    def _update_database_completion(self, completion_data: Dict[str, Any]):
        """Update database with completion information."""
        try:
            from ...models import FilmingSession
            from django.utils import timezone
            from ...services.sma_service import SMAService
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            session.status = 'completed'
            session.workflow_state = 'completed'
            session.completed_at = timezone.now()
            session.progress_percent = 100.0
            
            # Calculate duration
            if session.started_at:
                session.duration = session.completed_at - session.started_at
            
            # Mark roll as filmed and handle temp roll creation
            if session.roll:
                # Use SMAService method which handles temp roll creation
                result = SMAService.mark_roll_as_filmed(self.session_id)
                if result.get('success'):
                    logger.info(f"Successfully processed roll completion for session {self.session_id}")
                    if result.get('temp_roll_created'):
                        logger.info("Temp roll was created during filming completion")
                else:
                    logger.error(f"Failed to mark roll as filmed: {result.get('error')}")
            
            session.save(update_fields=[
                'status', 'workflow_state', 'completed_at', 'duration', 'progress_percent', 'updated_at'
            ])
            
        except Exception as e:
            logger.error(f"Error updating database with completion: {e}")
    
    def _store_log_entry(self, log_data: Dict[str, Any]):
        """Store log entry in database."""
        try:
            from ...models import FilmingSession, FilmingSessionLog
            
            session = FilmingSession.objects.get(session_id=self.session_id)
            
            FilmingSessionLog.objects.create(
                session=session,
                level=log_data.get('level', 'info'),
                message=log_data.get('message', ''),
                workflow_state=log_data.get('workflow_state', session.workflow_state)
            )
            
        except Exception as e:
            logger.error(f"Error storing log entry: {e}")
    
    def _handle_error_condition(self, log_data: Dict[str, Any]):
        """Handle error conditions detected in logs."""
        try:
            error_message = log_data.get('message', '')
            
            # Check for specific error patterns
            if 'memory' in error_message.lower():
                self._handle_memory_error(log_data)
            elif 'timeout' in error_message.lower():
                self._handle_timeout_error(log_data)
            elif 'connection' in error_message.lower():
                self._handle_connection_error(log_data)
            
        except Exception as e:
            logger.error(f"Error handling error condition: {e}")
    
    def _handle_memory_error(self, log_data: Dict[str, Any]):
        """Handle memory-related errors."""
        logger.warning(f"Memory error detected for session {self.session_id}")
        # Could trigger memory cleanup or process restart
    
    def _handle_timeout_error(self, log_data: Dict[str, Any]):
        """Handle timeout-related errors."""
        logger.warning(f"Timeout error detected for session {self.session_id}")
        # Could trigger retry logic
    
    def _handle_connection_error(self, log_data: Dict[str, Any]):
        """Handle connection-related errors."""
        logger.warning(f"Connection error detected for session {self.session_id}")
        # Could trigger reconnection logic
    
    def _trigger_error_recovery(self, error_data: Dict[str, Any]):
        """Trigger error recovery procedures."""
        try:
            # This could be enhanced to implement automatic recovery
            logger.info(f"Error recovery triggered for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error in error recovery: {e}")
    
    def _trigger_post_completion_tasks(self, completion_data: Dict[str, Any]):
        """Trigger tasks that should run after completion."""
        try:
            # Note: mark_roll_as_filmed is already called in _update_database_completion
            # Only include additional post-completion tasks here
            
            # Could trigger other post-completion tasks like:
            # - File cleanup
            # - Notification sending
            # - Report generation
            logger.info(f"Post-completion tasks completed for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error in post-completion tasks: {e}")
    
    def _broadcast_progress_update(self, progress_data: Dict[str, Any]):
        """Broadcast progress update to WebSocket."""
        try:
            group_name = f"sma_session_{self.session_id}"
            
            self.async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_progress',
                    'session_id': self.session_id,
                    'progress': progress_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting progress update: {e}")
    
    def _broadcast_workflow_state_change(self, old_state: str, new_state: str):
        """Broadcast workflow state change to WebSocket."""
        try:
            group_name = f"sma_session_{self.session_id}"
            
            self.async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_workflow_state',
                    'session_id': self.session_id,
                    'old_state': old_state,
                    'new_state': new_state
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting workflow state change: {e}")
    
    def _broadcast_log_entry(self, log_data: Dict[str, Any]):
        """Broadcast log entry to WebSocket."""
        try:
            group_name = f"sma_session_{self.session_id}"
            
            self.async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_log',
                    'session_id': self.session_id,
                    'log': log_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting log entry: {e}")
    
    def _broadcast_error(self, error_data: Dict[str, Any]):
        """Broadcast error to WebSocket."""
        try:
            group_name = f"sma_session_{self.session_id}"
            
            self.async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_error',
                    'session_id': self.session_id,
                    'error': error_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting error: {e}")
    
    def _broadcast_completion(self, completion_data: Dict[str, Any]):
        """Broadcast completion to WebSocket."""
        try:
            group_name = f"sma_session_{self.session_id}"
            
            self.async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'sma_completed',
                    'session_id': self.session_id,
                    'completion': completion_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting completion: {e}") 