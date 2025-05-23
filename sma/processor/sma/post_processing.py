"""
Post-Processing Module for SMA (film scanning) automation system.

This module handles end-of-process operations including log file verification,
cleanup tasks, and final system operations after scanning is complete.
"""

import os
import subprocess
import time
from .sma_utils import get_file_size, format_file_size, open_log_file_folder
from .sma_exceptions import SMAFileError
from .ui_automation import cleanup_and_exit

# Import lock_mouse dynamically for cleanup
try:
    import pathlib
    import importlib.util
    lock_mouse_spec = importlib.util.spec_from_file_location(
        "lock_mouse", 
        pathlib.Path(__file__).parent.parent / "lock_mouse.py"
    )
    if lock_mouse_spec:
        lock_mouse = importlib.util.module_from_spec(lock_mouse_spec)
        lock_mouse_spec.loader.exec_module(lock_mouse)
        LOCK_MOUSE_AVAILABLE = True
    else:
        LOCK_MOUSE_AVAILABLE = False
except Exception as e:
    print(f"Warning: lock_mouse module not available: {e}")
    LOCK_MOUSE_AVAILABLE = False

class PostProcessor:
    """Handles post-processing operations after SMA scanning completion."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def check_log_file(self, parent_folder, film_number):
        """Check if log file exists from the film application."""
        try:
            film_log_path = os.path.join(parent_folder, '.filmlogs', f"{film_number}.txt")
            
            if os.path.exists(film_log_path):
                self.logger.info(f"Film application log file exists: {film_log_path}")
                
                # Try to open the file to check its contents
                try:
                    with open(film_log_path, 'r', encoding='cp1252') as log_file:
                        contents = log_file.read()
                        file_size = get_file_size(film_log_path)
                        self.logger.info(f"Log file size: {format_file_size(file_size)}")
                        
                        # Basic content validation
                        if len(contents.strip()) == 0:
                            self.logger.warning("Log file is empty")
                        else:
                            self.logger.info(f"Log file contains {len(contents)} characters")
                            
                except Exception as e:
                    self.logger.error(f"Error reading log file: {e}")
                    raise SMAFileError(
                        file_path=film_log_path,
                        operation="read_log_file",
                        message=f"Failed to read log file: {str(e)}"
                    )
                
                return True, film_log_path
            else:
                self.logger.error(f"Film application log file does not exist: {film_log_path}")
                return False, film_log_path
            
        except Exception as e:
            self.logger.error(f"Error checking log file: {e}")
            raise SMAFileError(
                file_path=film_log_path if 'film_log_path' in locals() else "unknown",
                operation="check_log_file",
                message=f"Failed to check log file: {str(e)}"
            )
    
    def open_log_folder(self, log_path):
        """Open the log file folder in Windows Explorer."""
        try:
            success = open_log_file_folder(log_path)
            if success:
                self.logger.info(f"Opened log folder in Explorer: {os.path.dirname(log_path)}")
            else:
                self.logger.warning("Failed to open log folder in Explorer")
            return success
        except Exception as e:
            self.logger.error(f"Error opening log folder: {e}")
            return False
    
    def release_mouse_lock(self):
        """Release mouse lock if it's active."""
        try:
            if LOCK_MOUSE_AVAILABLE:
                self.logger.info("Ensuring mouse lock is released...")
                lock_mouse.stop_mouse_lock()
                self.logger.info("Mouse lock released successfully")
                return True
            else:
                self.logger.info("Mouse lock module not available, skipping release")
                return True
        except Exception as e:
            self.logger.error(f"Error releasing mouse lock: {e}")
            return False
    
    def cleanup_application(self, app):
        """Clean up and close the SMA application."""
        try:
            success = cleanup_and_exit(app, self.logger)
            if success:
                self.logger.info("Application cleanup completed successfully")
            else:
                self.logger.warning("Application cleanup encountered issues")
            return success
        except Exception as e:
            self.logger.error(f"Error during application cleanup: {e}")
            return False
    
    def validate_process_completion(self, film_number, parent_folder):
        """Validate that the scanning process completed successfully."""
        try:
            # Check if log file exists and is valid
            log_exists, log_path = self.check_log_file(parent_folder, film_number)
            
            if not log_exists:
                self.logger.error("Process validation failed: Log file not found")
                return False, "Log file not found"
            
            # Additional validation checks could be added here
            # For example, checking log file content, verifying scan completion markers, etc.
            
            self.logger.info("Process validation completed successfully")
            return True, "Process completed successfully"
            
        except Exception as e:
            self.logger.error(f"Error during process validation: {e}")
            return False, f"Validation error: {str(e)}"
    
    def perform_final_cleanup(self, app=None):
        """Perform all final cleanup operations."""
        cleanup_results = {}
        
        try:
            # Release mouse lock
            cleanup_results['mouse_lock'] = self.release_mouse_lock()
            
            # Clean up application if provided
            if app:
                cleanup_results['application'] = self.cleanup_application(app)
            else:
                cleanup_results['application'] = True  # No app to clean up
            
            # Small delay to ensure cleanup completes
            time.sleep(2)
            
            # Log cleanup summary
            all_successful = all(cleanup_results.values())
            if all_successful:
                self.logger.info("All cleanup operations completed successfully")
            else:
                failed_operations = [op for op, success in cleanup_results.items() if not success]
                self.logger.warning(f"Some cleanup operations failed: {failed_operations}")
            
            return all_successful, cleanup_results
            
        except Exception as e:
            self.logger.error(f"Error during final cleanup: {e}")
            return False, cleanup_results
    
    def generate_process_summary(self, film_number, start_time, total_frames=None, log_path=None):
        """Generate a summary of the scanning process."""
        try:
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Format elapsed time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            summary = {
                'film_number': film_number,
                'start_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                'end_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)),
                'duration': duration_str,
                'total_frames': total_frames,
                'log_file': log_path,
                'success': True
            }
            
            # Log summary
            self.logger.info("=== SCANNING PROCESS SUMMARY ===")
            self.logger.info(f"Film Number: {film_number}")
            self.logger.info(f"Duration: {duration_str}")
            if total_frames:
                self.logger.info(f"Total Frames: {total_frames}")
            if log_path:
                self.logger.info(f"Log File: {log_path}")
            self.logger.info("================================")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating process summary: {e}")
            return None

class PostProcessingManager:
    """High-level manager for all post-processing operations."""
    
    def __init__(self, logger):
        self.logger = logger
        self.post_processor = PostProcessor(logger)
    
    def execute_post_processing(self, film_number, parent_folder, app=None, start_time=None, total_frames=None):
        """Execute complete post-processing workflow."""
        try:
            self.logger.info("Starting post-processing operations...")
            
            # Validate process completion
            validation_success, validation_message = self.post_processor.validate_process_completion(
                film_number, parent_folder
            )
            
            if not validation_success:
                self.logger.error(f"Process validation failed: {validation_message}")
                return False, validation_message
            
            # Check and open log file
            log_exists, log_path = self.post_processor.check_log_file(parent_folder, film_number)
            
            if log_exists:
                # Open log file folder in Explorer
                self.post_processor.open_log_folder(log_path)
            
            # Perform final cleanup
            cleanup_success, cleanup_results = self.post_processor.perform_final_cleanup(app)
            
            if not cleanup_success:
                self.logger.warning("Some cleanup operations failed, but process completed")
            
            # Generate process summary
            if start_time:
                summary = self.post_processor.generate_process_summary(
                    film_number, start_time, total_frames, log_path if log_exists else None
                )
            
            self.logger.info("Post-processing completed successfully")
            return True, "Post-processing completed successfully"
                    
        except Exception as e:
            self.logger.error(f"Error during post-processing: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False, f"Post-processing error: {str(e)}"

# Convenience functions for backward compatibility
def check_log_file(parent_folder, film_number, logger):
    """Check if log file exists from the film application."""
    post_processor = PostProcessor(logger)
    return post_processor.check_log_file(parent_folder, film_number)

def cleanup_and_exit_wrapper(app, logger):
    """Clean up and close application."""
    post_processor = PostProcessor(logger)
    return post_processor.cleanup_application(app) 