"""
SMA Controller Module - Main Orchestrator for SMA (film scanning) automation system.

This module serves as the main entry point and orchestrator for the SMA automation
process, coordinating all other modules to execute the complete scanning workflow.
"""

import sys
import time
from .sma_config import SMAConfig
from .ui_automation import (
    start_application, check_running_instance, recover_session
)
from .sma_workflow import (
    handle_main_screen, handle_data_source_selection, handle_film_start,
    handle_film_insert, handle_film_number_entry, handle_endsymbole_prompt,
    handle_nachspann_prompt, wait_for_transport_start, wait_for_transport_completion
)
from .progress_monitor import ProgressMonitor
from .post_processing import PostProcessingManager
from .sma_exceptions import (
    SMAException, SMAConfigurationError, log_exception, SMARecoveryError
)
from .sma_utils import setup_logging, log_system_info, PerformanceTimer

# Import lock_mouse dynamically for process-wide mouse control
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

class SMAController:
    """Main controller for the SMA automation process."""
    
    def __init__(self, args=None):
        """Initialize the SMA controller."""
        # Set up logging first
        self.logger = setup_logging()
        
        # Log system information
        log_system_info(self.logger)
        
        # Initialize configuration
        self.config_manager = SMAConfig()
        if args is None:
            self.args = self.config_manager.parse_arguments()
        else:
            self.args = args
        
        # Load configuration
        try:
            self.config = self.config_manager.load_configuration(self.args)
            self.logger.info(f"Configuration loaded successfully")
            self.logger.info(f"Processing folder: {self.config['folder_path']}")
            self.logger.info(f"Template: {self.config['template_name']}")
            self.logger.info(f"Recovery mode: {self.config['recovery_mode']}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise SMAConfigurationError(f"Configuration loading failed: {str(e)}")
        
        # Initialize other components
        self.app = None
        self.film_window = None
        self.filmnumber = None
        self.start_time = None
        self.filmlogs_dir = None
        self.parent_folder = None
        
        # Initialize post-processing manager
        self.post_processor = PostProcessingManager(self.logger)
    
    def run(self):
        """Execute the complete SMA automation workflow."""
        self.start_time = time.time()
        
        try:
            self.logger.info("=== Starting SMA Automation Process ===")
            
            # Activate mouse lock for the entire process if available
            if LOCK_MOUSE_AVAILABLE:
                self.logger.info("Activating mouse lock for the entire SMA process...")
                lock_mouse.start_mouse_lock()
            
            # Phase 1: Setup and Configuration
            with PerformanceTimer("Setup and Configuration", self.logger):
                self._setup_environment()
            
            # Phase 2: Application and Session Management
            with PerformanceTimer("Application and Session Management", self.logger):
                self._handle_application_lifecycle()
            
            # Phase 3: SMA Workflow Execution
            with PerformanceTimer("SMA Workflow Execution", self.logger):
                self._execute_sma_workflow()
            
            # Phase 4: Progress Monitoring
            with PerformanceTimer("Progress Monitoring", self.logger):
                self._monitor_scanning_progress()
            
            # Phase 5: End-of-Process Handling
            with PerformanceTimer("End-of-Process Handling", self.logger):
                self._handle_end_of_process()
            
            # Phase 6: Post-Processing
            with PerformanceTimer("Post-Processing", self.logger):
                self._execute_post_processing()
            
            self.logger.info("=== SMA Automation Process Completed Successfully ===")
            return True
            
        except SMARecoveryError as e:
            # Special handling for recovery errors - don't do emergency cleanup
            # since we want to leave the existing process running
            self.logger.error("=== Recovery Mode Failed - Manual Intervention Required ===")
            self.logger.error(str(e))
            self.logger.error("Existing SMA process has been left running for safety.")
            return False
            
        except Exception as e:
            self.logger.error(f"SMA automation process failed: {e}")
            log_exception(self.logger, e, "SMA automation")
            self._emergency_cleanup()
            return False
        finally:
            # Always release mouse lock at the end
            if LOCK_MOUSE_AVAILABLE:
                try:
                    self.logger.info("Releasing mouse lock - SMA process completed...")
                    lock_mouse.stop_mouse_lock()
                except Exception as e:
                    self.logger.error(f"Error releasing mouse lock: {e}")
    
    def _setup_environment(self):
        """Setup the environment and prepare for processing."""
        # Create log directory
        self.filmlogs_dir, self.parent_folder = self.config_manager.create_log_directory(
            self.config['folder_path'], self.logger
        )
        
        # Update template file
        tpl_file_path = self.config_manager.get_template_path(self.config['template_name'])
        self.config_manager.update_template_file(
            tpl_file_path, self.filmlogs_dir, self.config['template_name'], self.logger
        )
        
        # Update INI file
        self.config_manager.update_ini_file(
            self.config['ini_file_path'], self.config['folder_path'], self.logger
        )
        
        self.logger.info("Environment setup completed")
    
    def _handle_application_lifecycle(self):
        """Handle application startup and session management."""
        recovery_mode = self.config['recovery_mode']
        
        # Check for running instance, with recovery mode if requested
        start_new, existing_app, existing_window = check_running_instance(
            self.config['app_path'], self.logger, recovery_mode
        )
        
        if start_new:
            # Normal flow - start from beginning
            self.logger.info("Starting new scanning session...")
            self.app = start_application(self.config['app_path'], self.logger)
        else:
            # Recovery flow - continue from existing session
            self.logger.info("Attempting to recover existing scanning session...")
            self.app = existing_app
            self.film_window = existing_window
            
            # Try to recover the session
            recovered, recovered_filmnumber = recover_session(
                self.app, self.film_window, self.logger
            )
            
            if recovered:
                self.logger.info("Successfully recovered scanning session!")
                if recovered_filmnumber:
                    self.filmnumber = recovered_filmnumber
                elif self.config['custom_filmnumber']:
                    self.filmnumber = self.config['custom_filmnumber']
                    self.logger.info(f"Using provided film number for recovered session: {self.filmnumber}")
                else:
                    # If we couldn't recover the film number, use the folder name
                    self.filmnumber = self.config_manager.get_film_number(
                        self.config['folder_path'], self.config['custom_filmnumber']
                    )
                    self.logger.info(f"Using folder name as film number for recovered session: {self.filmnumber}")
                
                # Skip to monitoring phase for recovered sessions
                return
            else:
                # SAFE FAILURE: Never kill existing process in recovery mode
                self.logger.error("Failed to recover existing scanning session.")
                self.logger.error("SMA application is still running but cannot be recovered automatically.")
                self.logger.error("This could be due to:")
                self.logger.error("  - SMA is in an unexpected state")
                self.logger.error("  - Required window is not accessible")
                self.logger.error("  - Film number cannot be determined")
                self.logger.error("")
                self.logger.error("MANUAL INTERVENTION REQUIRED:")
                self.logger.error("1. Check the SMA application manually")
                self.logger.error("2. If SMA is actively scanning, let it complete")
                self.logger.error("3. If SMA is stuck or idle, manually close it")
                self.logger.error("4. Then run the script again WITHOUT --recovery flag")
                self.logger.error("")
                self.logger.error("NEVER killing existing process to prevent data loss!")
                
                raise SMARecoveryError(
                    "Cannot recover existing session. SMA process left running for safety. "
                    "Manual intervention required - check SMA application state and close manually if safe."
                )
        
        self.logger.info("Application lifecycle management completed")
    
    def _execute_sma_workflow(self):
        """Execute the main SMA application workflow."""
        # Skip workflow if we recovered a session
        if self.film_window is not None and self.filmnumber is not None:
            self.logger.info("Skipping workflow execution for recovered session")
            return
        
        # Handle main screen
        handle_main_screen(self.app, self.logger)
        
        # Handle data source selection
        main_win = handle_data_source_selection(
            self.app, self.config['template_name'], self.logger
        )
        
        # Start the film process
        self.film_window = handle_film_start(main_win, self.app, self.logger)
        
        # Handle film insert
        self.film_window = handle_film_insert(self.film_window, self.logger)
        
        # Handle film number entry
        self.filmnumber, self.film_window = handle_film_number_entry(
            self.app, self.config['folder_path'], self.film_window, 
            self.logger, self.config['custom_filmnumber']
        )
        
        self.logger.info("SMA workflow execution completed")
    
    def _monitor_scanning_progress(self):
        """Monitor the scanning progress until completion."""
        if not self.film_window:
            raise SMAException("Film window not available for progress monitoring")
        
        # Create and run progress monitor
        progress_monitor = ProgressMonitor(self.film_window, self.logger)
        progress_monitor.monitor_progress()
        
        self.logger.info("Progress monitoring completed")
    
    def _handle_end_of_process(self):
        """Handle end-of-process prompts and operations."""
        if not self.film_window or not self.app:
            self.logger.warning("Film window or app not available for end-of-process handling")
            return
        
        # Handle end symbols prompt
        handle_endsymbole_prompt(self.film_window, self.app, self.logger)
        
        # Handle nachspann prompt
        handle_nachspann_prompt(self.film_window, self.app, self.logger)
        
        # Wait for film transport to start and complete
        transport_window, transport_control = wait_for_transport_start(
            self.film_window, self.app, self.logger
        )
        
        wait_for_transport_completion(
            transport_window, transport_control, self.app, self.logger
        )
        
        self.logger.info("End-of-process handling completed")
    
    def _execute_post_processing(self):
        """Execute post-processing operations."""
        if not self.filmnumber or not self.parent_folder:
            self.logger.warning("Film number or parent folder not available for post-processing")
            return
        
        # Get total frames from progress monitor if available
        total_frames = None  # This could be extracted from the progress monitor
        
        # Execute post-processing
        success, message = self.post_processor.execute_post_processing(
            self.filmnumber, 
            self.parent_folder, 
            self.app, 
            self.start_time, 
            total_frames
        )
        
        if success:
            self.logger.info("Post-processing completed successfully")
        else:
            self.logger.warning(f"Post-processing completed with issues: {message}")
    
    def _emergency_cleanup(self):
        """Perform emergency cleanup in case of errors."""
        try:
            self.logger.info("Performing emergency cleanup...")
            
            # Release mouse lock
            if LOCK_MOUSE_AVAILABLE:
                try:
                    lock_mouse.stop_mouse_lock()
                    self.logger.info("Mouse lock released during emergency cleanup")
                except Exception as e:
                    self.logger.error(f"Error releasing mouse lock during emergency cleanup: {e}")
            
            # Kill application
            if self.app:
                try:
                    self.app.kill()
                    self.logger.info("Application closed during emergency cleanup")
                except Exception as e:
                    self.logger.error(f"Error closing application during emergency cleanup: {e}")
            
            self.logger.info("Emergency cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during emergency cleanup: {e}")
    
    def get_status(self):
        """Get current status of the SMA controller."""
        return {
            'config_loaded': bool(self.config),
            'app_started': bool(self.app),
            'film_window_available': bool(self.film_window),
            'film_number': self.filmnumber,
            'start_time': self.start_time,
            'recovery_mode': self.config.get('recovery_mode', False) if self.config else False
        }

def main(args=None):
    """Main entry point for the SMA automation system."""
    try:
        controller = SMAController(args)
        return controller.run()
    except Exception as e:
        print(f"Fatal error in SMA automation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 