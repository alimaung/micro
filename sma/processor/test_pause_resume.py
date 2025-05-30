"""
Test script for SMA pause/resume automation.

This script tests the ability to pause and resume an SMA filming process:
1. Monitor existing SMA process for 5 seconds
2. Pause the process (Verfilmen beenden -> Ja -> handle Nachspann)
3. Wait 10 seconds
4. Resume the process (Verfilmen starten)
5. Continue monitoring

Usage: Start SMA filming manually, then run this script.
"""

import time
import sys
from pywinauto import Application
from pywinauto.keyboard import send_keys
from sma.ui_automation import (
    find_window, find_control, click_button, safe_get_window_text,
    wait_for_window
)
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PauseResumeTest:
    def __init__(self):
        self.app = None
        self.film_window = None
        self.main_window = None
        self.zu_verfilmen_control = None
        self.verfilmt_control = None
        
    def connect_to_sma(self):
        """Connect to existing SMA application."""
        try:
            logger.info("Connecting to existing SMA application...")
            
            # Try to connect to SMA process by executable path (more reliable)
            sma_path = r"Y:\SMA\file-converter-64\file-sma.exe"
            try:
                self.app = Application(backend="uia").connect(path=sma_path)
                logger.info("Connected to SMA application via process path")
            except Exception as e:
                logger.info(f"Could not connect via path ({e}), trying by process name...")
                # Fallback: try to connect by process name
                self.app = Application(backend="uia").connect(process="file-sma.exe")
                logger.info("Connected to SMA application via process name")
            
            # Find the filming window
            self.film_window = find_window(
                self.app, 
                title="Verfilmen der Dokumente", 
                timeout=10, 
                logger=logger
            )
            
            # Find progress controls
            self._find_progress_controls()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SMA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _find_progress_controls(self):
        """Find the progress monitoring controls."""
        try:
            children = self.film_window.children()
            logger.info(f"Found {len(children)} children in film window")
            
            # Based on previous testing: Child 25 is "zu verfilmen", Child 7 is "verfilmt"
            if len(children) >= 26:
                self.zu_verfilmen_control = children[25]
                self.verfilmt_control = children[7]
                
                logger.info(f"Found 'zu verfilmen' control: {safe_get_window_text(self.zu_verfilmen_control)}")
                logger.info(f"Found 'verfilmt' control: {safe_get_window_text(self.verfilmt_control)}")
            else:
                logger.warning("Could not find expected progress controls")
                
        except Exception as e:
            logger.error(f"Error finding progress controls: {e}")
    
    def monitor_progress(self, duration_seconds):
        """Monitor progress for specified duration."""
        logger.info(f"Monitoring progress for {duration_seconds} seconds...")
        
        start_time = time.time()
        last_log_time = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                current_time = time.time()
                
                # Log progress every 2 seconds
                if current_time - last_log_time >= 2.0:
                    zu_verfilmen = safe_get_window_text(self.zu_verfilmen_control, "N/A")
                    verfilmt = safe_get_window_text(self.verfilmt_control, "N/A")
                    
                    elapsed = current_time - start_time
                    logger.info(f"[{elapsed:.1f}s] Progress - Zu verfilmen: {zu_verfilmen}, Verfilmt: {verfilmt}")
                    
                    last_log_time = current_time
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error monitoring progress: {e}")
                break
    
    def debug_window_controls(self):
        """Debug function to enumerate all controls in the filming window."""
        logger.info("=== DEBUG: Enumerating all controls in filming window ===")
        try:
            children = self.film_window.children()
            logger.info(f"Total children found: {len(children)}")
            
            for i, child in enumerate(children):
                try:
                    class_name = child.class_name()
                    window_text = safe_get_window_text(child, "")
                    control_type = getattr(child, 'control_type', 'Unknown')
                    
                    logger.info(f"Child {i}: Class='{class_name}', Text='{window_text}', Type='{control_type}'")
                    
                    # Look specifically for buttons
                    if "BUTTON" in class_name:
                        logger.info(f"  *** BUTTON FOUND: {class_name} - '{window_text}'")
                        
                except Exception as e:
                    logger.info(f"Child {i}: Error getting info - {e}")
                    
        except Exception as e:
            logger.error(f"Error enumerating controls: {e}")
        logger.info("=== END DEBUG ===")
    
    def pause_filming(self):
        """Pause the filming process."""
        logger.info("Starting pause sequence...")
        
        try:
            # Step 1: Click "Verfilmen beenden" button
            logger.info("Looking for 'Verfilmen beenden' button...")
            
            # Use the approach that worked: find by text only
            pause_button = find_control(
                self.film_window,
                title="Verfilmen beenden",
                control_type="Button",
                timeout=10,
                logger=logger
            )
            
            logger.info("Found 'Verfilmen beenden' button, clicking...")
            click_button(pause_button, logger)
            
            # Step 2: Wait for 2 seconds
            logger.info("Waiting for 2 seconds...")
            time.sleep(2)
            
            # Step 3: Send Enter key
            logger.info("Sending Enter key...")
            send_keys("{ENTER}")
            
            # Step 4: Handle Nachspann prompt
            logger.info("Handling Nachspann prompt...")
            time.sleep(2)  # Wait for Nachspann dialog
            
            nachspann_result = handle_nachspann_prompt_nein(self.film_window, self.app, logger)
            if nachspann_result:
                logger.info("Nachspann prompt handled successfully (selected 'Nein')")
            else:
                logger.warning("Nachspann prompt handling failed or not found")
            
            # Step 5: Wait for return to main window
            logger.info("Waiting for return to main window...")
            time.sleep(3)
            
            # Find the main window
            try:
                self.main_window = find_window(
                    self.app,
                    class_name="WindowsForms10.Window.8.app.0.141b42a_r6_ad1",
                    timeout=15,
                    logger=logger
                )
                logger.info("Successfully returned to main window")
                return True
                
            except Exception as e:
                logger.error(f"Failed to find main window: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error during pause sequence: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def resume_filming(self):
        """Resume the filming process."""
        logger.info("Starting resume sequence...")
        
        try:
            # Find "Verfilmen starten" button in main window
            logger.info("Looking for 'Verfilmen starten' button...")
            
            start_button = find_control(
                self.main_window,
                title="Verfilmen starten",
                auto_id="cmdStart",
                control_type="Button",
                timeout=10,
                logger=logger
            )
            
            logger.info("Found 'Verfilmen starten' button, clicking...")
            click_button(start_button, logger)
            
            # Wait for filming window to reappear
            logger.info("Waiting for filming window to reappear...")
            
            self.film_window = wait_for_window(
                self.app,
                title="Verfilmen der Dokumente",
                timeout=30,
                logger=logger
            )
            
            logger.info("Filming window reappeared")
            
            # Re-find progress controls
            self._find_progress_controls()
            
            logger.info("Resume sequence completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during resume sequence: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def run_test(self):
        """Run the complete pause/resume test."""
        logger.info("=== Starting Pause/Resume Test ===")
        
        # Step 1: Connect to existing SMA process
        if not self.connect_to_sma():
            logger.error("Failed to connect to SMA. Make sure SMA is running and filming.")
            return False
        
        # Step 2: Monitor for 5 seconds
        logger.info("Phase 1: Initial monitoring (5 seconds)")
        self.monitor_progress(5)
        
        # Step 3: Pause the process
        logger.info("Phase 2: Pausing filming process")
        if not self.pause_filming():
            logger.error("Failed to pause filming process")
            return False
        
        # Step 4: Wait 10 seconds
        logger.info("Phase 3: Waiting 10 seconds while paused")
        for i in range(10, 0, -1):
            logger.info(f"Waiting... {i} seconds remaining")
            time.sleep(1)
        
        # Step 5: Resume the process
        logger.info("Phase 4: Resuming filming process")
        if not self.resume_filming():
            logger.error("Failed to resume filming process")
            return False
        
        # Step 6: Monitor again for 10 seconds
        logger.info("Phase 5: Post-resume monitoring (10 seconds)")
        self.monitor_progress(10)
        
        logger.info("=== Pause/Resume Test Completed Successfully ===")
        return True

def handle_nachspann_prompt_nein(film_window, app, logger):
    """Handle the Nachspann prompt by selecting 'Nein' (for pause scenario)."""
    try:
        logger.info("Waiting for Nachspann prompt (will select 'Nein')...")
        timeout = 30
        start_time = time.time()
        nein_button = None
        sma_title_window = None
        
        # First find the SMA title window
        while time.time() - start_time < timeout:
            try:
                children = film_window.children()
                
                # Look for the SMA title window (usually contains version number)
                for child in children:
                    try:
                        child_text = child.window_text()
                        if "SMA 51" in child_text:
                            sma_title_window = child
                            logger.info(f"Found SMA title window: {child_text}")
                            break
                    except Exception as e:
                        logger.error(f"Error checking child window: {e}")
                
                if sma_title_window is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding SMA title window: {e}")
                time.sleep(1)
        
        if sma_title_window is None:
            logger.warning("Could not find SMA title window within timeout")
            # Try to continue with the film_window
            sma_title_window = film_window
        
        # Now look for the Nachspann text and 'Nein' button
        start_time = time.time()  # Reset timer
        found_nachspann_text = False
        nachspann_text = ""
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = sma_title_window.children()
                
                # Search for Nachspann text
                if not found_nachspann_text:
                    for grandchild in grandchildren:
                        try:
                            if grandchild.class_name() == "WindowsForms10.STATIC.app.0.141b42a_r6_ad1":
                                grandchild_text = grandchild.window_text()
                                if "Soll ein Nachspann abgefahren werden?" in grandchild_text:
                                    found_nachspann_text = True
                                    nachspann_text = grandchild_text
                                    logger.info(f"Found 'Nachspann' text: {grandchild_text}")
                                    break
                        except Exception as e:
                            logger.error(f"Error checking for Nachspann text: {e}")
                
                # Look for the 'Nein' button
                for grandchild in grandchildren:
                    try:
                        if (grandchild.class_name() == "WindowsForms10.BUTTON.app.0.141b42a_r6_ad1" and 
                            grandchild.window_text() == "Nein"):
                            nein_button = grandchild
                            logger.info("Found 'Nein' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking for Nein button: {e}")
                
                if nein_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Nachspann prompt: {e}")
                time.sleep(1)
        
        if nein_button is None:
            logger.warning("Could not find 'Nein' button for Nachspann prompt within timeout")
            return False
        
        # Click the 'Nein' button
        click_button(nein_button, logger)
        logger.info("Clicked 'Nein' for Nachspann prompt")
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Nachspann prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run the test."""
    test = PauseResumeTest()
    
    try:
        success = test.run_test()
        if success:
            logger.info("Test completed successfully!")
            sys.exit(0)
        else:
            logger.error("Test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 