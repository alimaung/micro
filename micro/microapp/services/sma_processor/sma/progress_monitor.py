"""
Progress Monitoring Module for SMA (film scanning) automation system.

This module handles progress tracking and monitoring during the SMA scanning process,
including ETA calculations, notification sending, and advanced finish warnings.
"""

import time
from datetime import datetime, timedelta
from .ui_automation import find_progress_controls, safe_get_window_text
from .sma_utils import (
    calculate_eta, format_progress_percent, should_send_notification, 
    format_notification_message, safe_int_conversion
)
from .advanced_finish import create_advanced_finish_manager
from .sma_exceptions import SMAProgressMonitorError

# Import notification system dynamically
try:
    import pathlib
    import importlib.util
    firebase_notif_spec = importlib.util.spec_from_file_location(
        "firebase_notif", 
        pathlib.Path(__file__).parent.parent / "firebase_notif.py"
    )
    if firebase_notif_spec:
        firebase_notif = importlib.util.module_from_spec(firebase_notif_spec)
        firebase_notif_spec.loader.exec_module(firebase_notif)
        FIREBASE_NOTIF_AVAILABLE = True
    else:
        FIREBASE_NOTIF_AVAILABLE = False
except Exception as e:
    print(f"Warning: firebase_notif module not available: {e}")
    FIREBASE_NOTIF_AVAILABLE = False

class ProgressMonitor:
    """Monitors SMA scanning progress and handles notifications."""
    
    def __init__(self, film_window, logger):
        self.film_window = film_window
        self.logger = logger
        
        # Progress tracking variables
        self.zu_verfilmen_control = None
        self.verfilmt_control = None
        self.prev_zu_verfilmen = None
        self.prev_verfilmt = None
        self.start_time = time.time()
        self.first_update_time = None
        self.first_verfilmt = None
        self.total_docs = 0
        self.last_log_time = 0
        self.min_log_interval = 1.0  # Minimum time between logs in seconds
        self.last_progress_value = 0
        self.last_logged_verfilmt = None
        self.process_completed = False
        
        # Notification variables
        self.last_notification_percent = 0
        self.prep_mode = None  # 'time' or 'percentage'
        self.prep_start_time = None
        self.prep_notifications_sent = {"PREP1": False, "PREP2": False, "PREP3": False}
        self.foreground_brought = False
        
        # Advanced finish system
        self.advanced_finish_manager = create_advanced_finish_manager(logger)
        
        # Find progress controls
        self._initialize_progress_controls()
    
    def _initialize_progress_controls(self):
        """Initialize progress monitoring controls."""
        try:
            self.zu_verfilmen_control, self.verfilmt_control = find_progress_controls(
                self.film_window, self.logger
            )
            
            if self.zu_verfilmen_control is None or self.verfilmt_control is None:
                raise SMAProgressMonitorError("Could not find progress controls. Unable to monitor progress.")
                
        except Exception as e:
            raise SMAProgressMonitorError(f"Failed to initialize progress controls: {str(e)}")
    
    def monitor_progress(self):
        """Monitor progress until completion."""
        try:
            self.logger.info("Starting to monitor progress...")
            
            while not self.process_completed:
                # Get the current values
                try:
                    zu_verfilmen_value = safe_get_window_text(self.zu_verfilmen_control, "Not found")
                    verfilmt_value = safe_get_window_text(self.verfilmt_control, "Not found")
                    
                    # Process values if they've changed
                    if zu_verfilmen_value != self.prev_zu_verfilmen or verfilmt_value != self.prev_verfilmt:
                        self._process_progress_update(zu_verfilmen_value, verfilmt_value)
                    
                    # Update the previous values
                    self.prev_zu_verfilmen = zu_verfilmen_value
                    self.prev_verfilmt = verfilmt_value
                    
                except Exception as e:
                    self.logger.error(f"Error getting control values: {e}")
                
                # Check for stalled process - increased timeout and added process health check
                if time.time() - self.last_log_time > 300 and self.last_logged_verfilmt is not None:  # 5 minutes instead of 1
                    # Before assuming stall, check if we're actually near completion
                    if self.total_docs > 0 and self.last_logged_verfilmt >= (self.total_docs * 0.95):
                        self.logger.info("No progress for 5 minutes but near completion (>95%) - continuing to monitor")
                        # Reset timer to give more time for completion
                        self.last_log_time = time.time()
                    else:
                        # Check if the SMA window is still active and responsive
                        if self._is_sma_window_active():
                            self.logger.warning("No progress for 5 minutes but SMA window is still active - continuing to monitor")
                            # Reset timer to give more time
                            self.last_log_time = time.time()
                        else:
                            self.logger.warning("No progress for 5 minutes and SMA window appears inactive. Film process may be stalled or complete.")
                            break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during progress monitoring: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            # Cleanup advanced finish components
            self._cleanup()
        
        return True
    
    def _process_progress_update(self, zu_verfilmen_value, verfilmt_value):
        """Process a progress update."""
        # Calculate progress
        if zu_verfilmen_value.isdigit() and verfilmt_value.isdigit():
            zu_verfilmen = int(zu_verfilmen_value)
            verfilmt = int(verfilmt_value)
            
            # Check if process is complete
            if self.total_docs > 0 and verfilmt >= self.total_docs and not self.process_completed:
                self._handle_completion(verfilmt)
                return
            
            # Skip if we've already logged this exact verfilmt value
            if verfilmt == self.last_logged_verfilmt:
                return
            
            total = zu_verfilmen + verfilmt
            
            if total > 0:
                progress_percent = format_progress_percent(verfilmt, total)
                
                # Initialize progress tracking on first update
                if self.total_docs == 0:
                    self._initialize_progress_tracking(total, verfilmt)
                else:
                    # Calculate and log ETA
                    self._log_progress_with_eta(verfilmt, total, progress_percent)
    
    def _initialize_progress_tracking(self, total, verfilmt):
        """Initialize progress tracking variables."""
        self.total_docs = total
        self.logger.info(f"Total frames to process: {self.total_docs}")
        
        # Initialize time prediction variables
        self.first_update_time = time.time()
        self.first_verfilmt = verfilmt
        self.last_progress_value = verfilmt
    
    def _log_progress_with_eta(self, verfilmt, total, progress_percent):
        """Log progress with ETA calculation."""
        if self.first_update_time is not None and verfilmt != self.last_logged_verfilmt:
            eta, duration_str, rate = calculate_eta(
                self.first_update_time, self.first_verfilmt, verfilmt, self.total_docs
            )
            
            # Calculate remaining time in seconds
            remaining_seconds = None
            if eta:
                remaining_seconds = (eta - datetime.now()).total_seconds()
            
            # Only log if enough time has passed since the last log
            current_time = time.time()
            if current_time - self.last_log_time >= self.min_log_interval:
                self._log_current_progress(progress_percent, verfilmt, eta, duration_str, rate)
                self._handle_advanced_finish_warnings(verfilmt, remaining_seconds, current_time, progress_percent, eta)
                self._handle_notifications(progress_percent, verfilmt, eta, remaining_seconds, current_time)
                
                self.last_log_time = current_time
                self.last_logged_verfilmt = verfilmt
                self.last_progress_value = verfilmt
    
    def _log_current_progress(self, progress_percent, verfilmt, eta, duration_str, rate):
        """Log current progress information."""
        if eta and duration_str:
            progress_message = (
                f"Progress: {progress_percent:.2f}% ({verfilmt}/{self.total_docs}) - "
                f"ETA: {eta.strftime('%H:%M:%S')} - Remaining: {duration_str} - Rate: {rate:.2f} docs/sec"
            )
            self.logger.info(progress_message)
            
            # Output to stdout for process manager to capture
            print(f"SMA_PROGRESS: {progress_percent:.2f}% ({verfilmt}/{self.total_docs})")
            print(f"SMA_WORKFLOW_STATE: monitoring")
            
        else:
            progress_message = f"Progress: {progress_percent:.2f}% ({verfilmt}/{self.total_docs})"
            self.logger.info(progress_message)
            
            # Output to stdout for process manager to capture
            print(f"SMA_PROGRESS: {progress_percent:.2f}% ({verfilmt}/{self.total_docs})")
            print(f"SMA_WORKFLOW_STATE: monitoring")
    
    def _handle_advanced_finish_warnings(self, verfilmt, remaining_seconds, current_time, progress_percent, eta):
        """Handle advanced finish warning system."""
        remaining_frames = self.total_docs - verfilmt
        
        try:
            self.advanced_finish_manager.handle_frame_countdown(remaining_frames, self.film_window)
        except Exception as e:
            self.logger.error(f"Error in advanced finish system: {e}")
    
    def _handle_notifications(self, progress_percent, verfilmt, eta, remaining_seconds, current_time):
        """Handle notification sending."""
        if not FIREBASE_NOTIF_AVAILABLE:
            return
        
        try:
            # Check if we need to trigger PREP mode
            self._check_prep_mode_trigger(remaining_seconds, progress_percent, current_time)
            
            # Handle PREP notifications based on mode
            self._send_prep_notifications(current_time, progress_percent)
            
            # Send regular RUNNING notifications every 2% (continue even during PREP mode)
            # RUNNING notifications use "process" message_id, PREP uses "prep" message_id
            self._send_running_notifications(progress_percent, verfilmt, eta)
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    def _check_prep_mode_trigger(self, remaining_seconds, progress_percent, current_time):
        """Check if PREP mode should be triggered."""
        if self.prep_mode is None:
            # Check for time trigger (remaining < 3 minutes = 180 seconds)
            if remaining_seconds is not None and remaining_seconds <= 180:
                self.prep_mode = 'time'
                self.prep_start_time = current_time
                self.logger.info(f"PREP mode triggered by time: {remaining_seconds:.0f} seconds remaining")
            # Check for percentage trigger (90%)
            elif progress_percent >= 90.0:
                self.prep_mode = 'percentage'
                self.prep_start_time = current_time
                self.logger.info(f"PREP mode triggered by percentage: {progress_percent:.2f}%")
    
    def _send_prep_notifications(self, current_time, progress_percent):
        """Send PREP notifications based on current mode."""
        if self.prep_mode == 'time':
            self._send_time_based_prep_notifications(current_time)
        elif self.prep_mode == 'percentage':
            self._send_percentage_based_prep_notifications(progress_percent)
    
    def _send_time_based_prep_notifications(self, current_time):
        """Send time-based PREP notifications."""
        elapsed_prep_time = current_time - self.prep_start_time
        
        # PREP1: immediately (0m)
        if not self.prep_notifications_sent["PREP1"]:
            firebase_notif.send_notification("PREP1", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP1"] = True
            self.logger.info("Sent PREP1 notification (time mode - immediate)")
        
        # PREP2: after 1 minute (60 seconds)
        elif elapsed_prep_time >= 60 and not self.prep_notifications_sent["PREP2"]:
            firebase_notif.send_notification("PREP2", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP2"] = True
            self.logger.info("Sent PREP2 notification (time mode - after 1 minute)")
        
        # PREP3: after 2 minutes (120 seconds)
        elif elapsed_prep_time >= 120 and not self.prep_notifications_sent["PREP3"]:
            firebase_notif.send_notification("PREP3", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP3"] = True
            self.logger.info("Sent PREP3 notification (time mode - after 2 minutes)")
    
    def _send_percentage_based_prep_notifications(self, progress_percent):
        """Send percentage-based PREP notifications."""
        # PREP1: immediately at 90%
        if progress_percent >= 90.0 and not self.prep_notifications_sent["PREP1"]:
            firebase_notif.send_notification("PREP1", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP1"] = True
            self.logger.info(f"Sent PREP1 notification (percentage mode - {progress_percent:.2f}%)")
        
        # PREP2: at 93%
        elif progress_percent >= 93.0 and not self.prep_notifications_sent["PREP2"]:
            firebase_notif.send_notification("PREP2", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP2"] = True
            self.logger.info(f"Sent PREP2 notification (percentage mode - {progress_percent:.2f}%)")
        
        # PREP3: at 96%
        elif progress_percent >= 96.0 and not self.prep_notifications_sent["PREP3"]:
            firebase_notif.send_notification("PREP3", "Process almost done, please prepare", "prep")
            self.prep_notifications_sent["PREP3"] = True
            self.logger.info(f"Sent PREP3 notification (percentage mode - {progress_percent:.2f}%)")
    
    def _send_running_notifications(self, progress_percent, verfilmt, eta):
        """Send regular RUNNING notifications."""
        if should_send_notification(progress_percent, self.last_notification_percent, interval=2):
            current_notification_percent = int(progress_percent // 2) * 2
            if current_notification_percent > self.last_notification_percent and current_notification_percent > 0:
                self.last_notification_percent = current_notification_percent
                remaining_frames = self.total_docs - verfilmt
                eta_str = eta.strftime('%H:%M:%S') if eta else "N/A"
                
                message = format_notification_message(progress_percent, remaining_frames, eta_str)
                firebase_notif.send_notification("RUNNING", message, "process")
                self.logger.info(f"Sent RUNNING notification at {current_notification_percent}%: {message}")
    
    def _handle_completion(self, verfilmt):
        """Handle process completion."""
        self.process_completed = True
        completion_message = f"SMA scanning process completed! Total frames processed: {verfilmt}"
        self.logger.info(completion_message)
        
        # Output to stdout for process manager to capture
        print(f"SMA_PROGRESS: 100.0% ({verfilmt}/{self.total_docs})")
        print(f"SMA_WORKFLOW_STATE: completed")
        print(f"SMA_COMPLETION: Process completed successfully with {verfilmt} frames")
        
        # Send completion notification if available
        if FIREBASE_NOTIF_AVAILABLE:
            try:
                firebase_notif.send_notification(
                    "SMA Process Complete",
                    f"Scanning completed! {verfilmt} frames processed.",
                    "completion"
                )
            except Exception as e:
                self.logger.error(f"Error sending completion notification: {e}")
        
        self.logger.info("Process monitoring completed")
    
    def _is_sma_window_active(self):
        """Check if the SMA window is still active and responsive."""
        try:
            # Check if the film window still exists and is responsive
            if self.film_window and hasattr(self.film_window, 'exists'):
                return self.film_window.exists()
            return False
        except Exception as e:
            self.logger.debug(f"Error checking SMA window activity: {e}")
            return False
    
    def _cleanup(self):
        """Clean up advanced finish components."""
        try:
            self.advanced_finish_manager.cleanup()
        except Exception as e:
            self.logger.error(f"Error cleaning up progress monitor: {e}")
    
    def is_completed(self):
        """Check if monitoring is completed."""
        return self.process_completed
    
    def get_status(self):
        """Get current monitoring status."""
        return {
            'total_docs': self.total_docs,
            'current_docs': self.last_progress_value,
            'process_completed': self.process_completed,
            'prep_mode': self.prep_mode,
            'prep_notifications_sent': self.prep_notifications_sent.copy(),
            'advanced_finish_status': self.advanced_finish_manager.get_status() if self.advanced_finish_manager else None
        }

# Convenience function for backward compatibility
def monitor_progress(film_window, logger):
    """Monitor progress until completion."""
    monitor = ProgressMonitor(film_window, logger)
    return monitor.monitor_progress() 