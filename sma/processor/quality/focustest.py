"""
Focus Test Automation for SMA

This script tests 5 different exposure settings (80, 100, 120, 140, 160) by:
1. Modifying docufile.ini settings (VORSPANN=0, NACHSPANN=1)
2. Modifying template VerschlussGeschw for each exposure
3. Running SMA workflow for each setting with corresponding film number
4. Handling "Nein" response for Nachspann prompt
5. Restoring original settings when complete
"""

import sys
import os
import time
import shutil
import configparser
from datetime import datetime

# Add the parent directory to the path to access sma module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pywinauto import Application, Desktop
from sma.ui_automation import (
    start_application, check_running_instance, find_window, find_control, 
    click_button, cleanup_and_exit
)
from sma.sma_workflow import (
    handle_main_screen, handle_data_source_selection, handle_film_start,
    handle_film_insert, handle_film_number_entry, handle_endsymbole_prompt
)

# Configuration
DOCUFILE_PATH = r"Y:\SMA\file-converter-64\docufile.ini"
TEMPLATE_PATH = r"Y:\SMA\file-converter-64\TEMPLATES\16mm-Test.TPL"
SOURCE_FOLDER = r"Y:\.quality\focustest\source"
SMA_EXE_PATH = r"Y:\SMA\file-converter-64\file-sma.exe"

# Test settings
EXPOSURE_SETTINGS = [80, 100, 120, 140, 160]

class FocusTestError(Exception):
    """Custom exception for focus test errors."""
    pass

def backup_config_files(logger):
    """Create backups of configuration files."""
    try:
        # Backup docufile.ini
        docufile_backup = DOCUFILE_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(DOCUFILE_PATH, docufile_backup)
        logger.info(f"Backed up docufile.ini to: {docufile_backup}")
        
        # Backup template file
        template_backup = TEMPLATE_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(TEMPLATE_PATH, template_backup)
        logger.info(f"Backed up template to: {template_backup}")
        
        return docufile_backup, template_backup
    except Exception as e:
        logger.error(f"Error creating backups: {e}")
        raise FocusTestError(f"Failed to create backups: {e}")

def restore_config_files(docufile_backup, template_backup, logger):
    """Restore configuration files from backups."""
    try:
        # Restore docufile.ini
        shutil.copy2(docufile_backup, DOCUFILE_PATH)
        logger.info(f"Restored docufile.ini from backup")
        
        # Restore template file
        shutil.copy2(template_backup, TEMPLATE_PATH)
        logger.info(f"Restored template from backup")
        
        # Clean up backup files
        os.remove(docufile_backup)
        os.remove(template_backup)
        logger.info("Cleaned up backup files")
        
    except Exception as e:
        logger.error(f"Error restoring backups: {e}")
        raise FocusTestError(f"Failed to restore backups: {e}")

def modify_docufile_ini(logger):
    """Modify docufile.ini for focus test settings using direct text manipulation."""
    try:
        # Read the file as text
        with open(DOCUFILE_PATH, 'r') as f:
            lines = f.readlines()
        
        # Track if we found and modified the values
        vorspann_found = False
        nachspann_found = False
        
        # Process each line
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Look for VORSPANN setting
            if stripped.startswith('VORSPANN='):
                lines[i] = 'VORSPANN=0\n'
                vorspann_found = True
                logger.info(f"Modified VORSPANN=0 at line {i+1}")
            
            # Look for NACHSPANN setting
            elif stripped.startswith('NACHSPANN='):
                lines[i] = 'NACHSPANN=1\n'
                nachspann_found = True
                logger.info(f"Modified NACHSPANN=1 at line {i+1}")
        
        # If settings weren't found, add them to the [SYSTEM] section
        if not vorspann_found or not nachspann_found:
            # Find the [SYSTEM] section
            system_section_index = None
            for i, line in enumerate(lines):
                if line.strip() == '[SYSTEM]':
                    system_section_index = i
                    break
            
            if system_section_index is not None:
                # Add missing settings after the [SYSTEM] line
                insert_index = system_section_index + 1
                if not vorspann_found:
                    lines.insert(insert_index, 'VORSPANN=0\n')
                    logger.info(f"Added VORSPANN=0 to [SYSTEM] section")
                    insert_index += 1
                if not nachspann_found:
                    lines.insert(insert_index, 'NACHSPANN=1\n')
                    logger.info(f"Added NACHSPANN=1 to [SYSTEM] section")
            else:
                # If no [SYSTEM] section found, add it at the end
                lines.append('\n[SYSTEM]\n')
                if not vorspann_found:
                    lines.append('VORSPANN=0\n')
                    logger.info("Added [SYSTEM] section with VORSPANN=0")
                if not nachspann_found:
                    lines.append('NACHSPANN=1\n')
                    logger.info("Added NACHSPANN=1 to new [SYSTEM] section")
        
        # Write the modified content back
        with open(DOCUFILE_PATH, 'w') as f:
            f.writelines(lines)
        
        logger.info("Successfully modified docufile.ini: VORSPANN=0, NACHSPANN=1")
        
    except Exception as e:
        logger.error(f"Error modifying docufile.ini: {e}")
        raise FocusTestError(f"Failed to modify docufile.ini: {e}")

def modify_template_exposure(exposure_value, logger):
    """Modify template file with new exposure setting using direct text manipulation."""
    try:
        # Read the file as text
        with open(TEMPLATE_PATH, 'r') as f:
            lines = f.readlines()
        
        # Track if we found and modified the value
        verschluss_found = False
        
        # Process each line
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Look for VerschlussGeschw setting
            if stripped.startswith('VerschlussGeschw='):
                lines[i] = f'VerschlussGeschw={exposure_value}\n'
                verschluss_found = True
                logger.info(f"Modified VerschlussGeschw={exposure_value} at line {i+1}")
                break
        
        # If setting wasn't found, add it to the [TEMPLATE] section
        if not verschluss_found:
            # Find the [TEMPLATE] section
            template_section_index = None
            for i, line in enumerate(lines):
                if line.strip() == '[TEMPLATE]':
                    template_section_index = i
                    break
            
            if template_section_index is not None:
                # Add the setting after the [TEMPLATE] line
                lines.insert(template_section_index + 1, f'VerschlussGeschw={exposure_value}\n')
                logger.info(f"Added VerschlussGeschw={exposure_value} to [TEMPLATE] section")
            else:
                # If no [TEMPLATE] section found, add it at the end
                lines.append('\n[TEMPLATE]\n')
                lines.append(f'VerschlussGeschw={exposure_value}\n')
                logger.info(f"Added [TEMPLATE] section with VerschlussGeschw={exposure_value}")
        
        # Write the modified content back
        with open(TEMPLATE_PATH, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"Successfully modified template: VerschlussGeschw={exposure_value}")
        
    except Exception as e:
        logger.error(f"Error modifying template: {e}")
        raise FocusTestError(f"Failed to modify template: {e}")

def handle_nachspann_nein_prompt(app, logger):
    """Handle the Nachspann prompt by clicking 'Nein' instead of 'Ja'."""
    try:
        logger.info("Waiting for Nachspann prompt to click 'Nein'...")
        timeout = 30
        start_time = time.time()
        nein_button = None
        
        while time.time() - start_time < timeout:
            try:
                # Search all SMA windows for the Nein button
                desktop = Desktop(backend="uia")
                all_windows = desktop.windows()
                
                for window in all_windows:
                    try:
                        # Check if this window belongs to our SMA process
                        if hasattr(window, 'process_id') and window.process_id() == app.process:
                            # Search children and grandchildren for Nein button
                            children = window.children()
                            for child in children:
                                try:
                                    # Check child
                                    if child.window_text() == "Nein" and "BUTTON" in child.class_name():
                                        nein_button = child
                                        logger.info("Found 'Nein' button in child")
                                        break
                                    
                                    # Check grandchildren
                                    try:
                                        grandchildren = child.children()
                                        for grandchild in grandchildren:
                                            try:
                                                if (grandchild.window_text() == "Nein" and 
                                                    "BUTTON" in grandchild.class_name()):
                                                    nein_button = grandchild
                                                    logger.info("Found 'Nein' button in grandchild")
                                                    break
                                            except:
                                                continue
                                        if nein_button is not None:
                                            break
                                    except:
                                        pass
                                except:
                                    continue
                            if nein_button is not None:
                                break
                    except:
                        continue
                
                if nein_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Nein button: {e}")
                time.sleep(1)
        
        if nein_button is None:
            logger.warning("Could not find 'Nein' button for Nachspann prompt within timeout")
            return False
        
        # Click the 'Nein' button
        click_button(nein_button, logger)
        logger.info("Clicked 'Nein' button for Nachspann prompt")
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Nachspann Nein prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_single_exposure_test(exposure_value, logger):
    """Run a single exposure test with the given value."""
    try:
        logger.info(f"\n{'='*50}")
        logger.info(f"Starting exposure test: {exposure_value}")
        logger.info(f"{'='*50}")
        
        # Modify template with current exposure setting
        modify_template_exposure(exposure_value, logger)
        
        # Check for existing SMA process and kill if needed
        should_start_new, existing_app, existing_window = check_running_instance(
            SMA_EXE_PATH, logger, recovery_mode=False
        )
        
        if should_start_new:
            # Start new SMA application
            app = start_application(SMA_EXE_PATH, logger)
        else:
            app = existing_app
        
        try:
            # Step 1: Handle main screen
            logger.info("Step 1: Handling main screen...")
            handle_main_screen(app, logger)
            
            # Step 2: Handle data source selection
            logger.info("Step 2: Handling data source selection...")
            main_win = handle_data_source_selection(app, "16mm-Test.TPL", logger)
            
            # Step 3: Handle film start
            logger.info("Step 3: Starting film process...")
            film_window = handle_film_start(main_win, app, logger)
            
            # Step 4: Handle film insert
            logger.info("Step 4: Handling film insert...")
            film_window = handle_film_insert(film_window, logger)
            
            # Step 5: Handle film number entry (use exposure value as film number)
            logger.info("Step 5: Entering film number...")
            film_number, film_window = handle_film_number_entry(
                app, SOURCE_FOLDER, film_window, logger, custom_filmnumber=str(exposure_value)
            )
            
            # Step 6: Wait for filming to complete (no Endsymbole expected)
            logger.info("Step 6: Waiting for filming to complete...")
            # We could add progress monitoring here if needed
            time.sleep(5)  # Give some time for filming to start
            
            # Step 7: Handle Nachspann prompt with "Nein"
            logger.info("Step 7: Handling Nachspann prompt...")
            nachspann_handled = handle_nachspann_nein_prompt(app, logger)
            
            if not nachspann_handled:
                logger.warning("Nachspann prompt not handled, continuing anyway...")
            
            # Wait a bit for process to complete
            time.sleep(3)
            
            logger.info(f"Exposure test {exposure_value} completed successfully!")
            return True
            
        finally:
            # Clean up this SMA instance
            try:
                cleanup_and_exit(app, logger)
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
    
    except Exception as e:
        logger.error(f"Error in exposure test {exposure_value}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_focus_test(logger):
    """Run the complete focus test with all exposure settings."""
    docufile_backup = None
    template_backup = None
    
    try:
        logger.info("Starting Focus Test Automation")
        logger.info(f"Testing exposure values: {EXPOSURE_SETTINGS}")
        
        # Create backups
        docufile_backup, template_backup = backup_config_files(logger)
        
        # Modify docufile.ini for test settings
        modify_docufile_ini(logger)
        
        # Run tests for each exposure setting
        successful_tests = 0
        failed_tests = 0
        
        for exposure in EXPOSURE_SETTINGS:
            try:
                success = run_single_exposure_test(exposure, logger)
                if success:
                    successful_tests += 1
                    logger.info(f"✓ Exposure {exposure}: SUCCESS")
                else:
                    failed_tests += 1
                    logger.error(f"✗ Exposure {exposure}: FAILED")
            except Exception as e:
                failed_tests += 1
                logger.error(f"✗ Exposure {exposure}: FAILED with exception: {e}")
            
            # Wait between tests
            if exposure != EXPOSURE_SETTINGS[-1]:  # Not the last test
                logger.info("Waiting before next test...")
                time.sleep(5)
        
        # Report results
        logger.info(f"\n{'='*50}")
        logger.info("FOCUS TEST RESULTS")
        logger.info(f"{'='*50}")
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {failed_tests}")
        logger.info(f"Total tests: {len(EXPOSURE_SETTINGS)}")
        
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.warning(f"⚠️  {failed_tests} tests failed")
        
        return failed_tests == 0
        
    except Exception as e:
        logger.error(f"Critical error in focus test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # Always restore backups
        if docufile_backup and template_backup:
            try:
                restore_config_files(docufile_backup, template_backup, logger)
                logger.info("Configuration files restored successfully")
            except Exception as e:
                logger.error(f"Failed to restore configuration files: {e}")

def main():
    """Main entry point for focus test."""
    # Set up logging
    import logging
    
    # Create logger
    logger = logging.getLogger('FocusTest')
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler
    log_filename = f"focustest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    try:
        # Verify paths exist
        if not os.path.exists(DOCUFILE_PATH):
            raise FocusTestError(f"docufile.ini not found at: {DOCUFILE_PATH}")
        
        if not os.path.exists(TEMPLATE_PATH):
            raise FocusTestError(f"Template file not found at: {TEMPLATE_PATH}")
        
        if not os.path.exists(SOURCE_FOLDER):
            raise FocusTestError(f"Source folder not found at: {SOURCE_FOLDER}")
        
        if not os.path.exists(SMA_EXE_PATH):
            raise FocusTestError(f"SMA executable not found at: {SMA_EXE_PATH}")
        
        # Run the focus test
        success = run_focus_test(logger)
        
        if success:
            logger.info("Focus test completed successfully!")
            return 0
        else:
            logger.error("Focus test failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
