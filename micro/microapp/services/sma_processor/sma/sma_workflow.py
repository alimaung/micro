"""
SMA Application Workflow Module for SMA (film scanning) automation system.

This module handles the main workflow steps for interacting with the SMA application,
including dialog navigation, form filling, and process initiation sequences.
"""

import time
import os
import traceback
from .ui_automation import (
    find_window, find_control, click_button, wait_for_window,
    safe_get_window_text, enumerate_window_children
)
from .sma_exceptions import SMAWindowNotFoundError, SMAControlNotFoundError, SMATimeoutError

def handle_main_screen(app, logger):
    """Handle the main application screen."""
    try:
        # Find the main window
        main_win = find_window(app, title_re="SMA 51.*", timeout=30, logger=logger)
        
        # Find the "Neue Verfilmung" static text control
        newfilm = find_control(
            main_win, 
            title="Neue Verfilmung", 
            auto_id="_Label_2", 
            control_type="Text", 
            timeout=30, 
            logger=logger
        )
        
        # Click on the "Neue Verfilmung" control
        newfilm.click_input()
        logger.info(f"Clicked on 'Neue Verfilmung' control")
        
        return True
    except Exception as e:
        logger.error(f"Error handling main screen: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_data_source_selection(app, template_name, logger):
    """Handle the data source selection dialog."""
    try:
        # Find "Datenquelle auswählen" window
        select_folder = find_window(
            app, 
            title="Datenquelle auswählen", 
            class_name="WindowsForms10.Window.8.app.0.141b42a_r6_ad1", 
            timeout=30, 
            logger=logger
        )
        
        # Select the template from the ComboBox
        try:
            # Find the ComboBox control
            template_combo = find_control(
                select_folder,
                auto_id="cmbTemplate", 
                control_type="ComboBox",
                timeout=30,
                logger=logger
            )
            
            # Select the item by text
            template_combo.select(template_name)
            logger.info(f"Selected template: {template_name}")
        except Exception as e:
            logger.error(f"Error selecting template: {e}")
            logger.info("Continuing anyway, as the default might be acceptable")
        
        # Find the "Neue Rolle beginnen" button
        newroll = find_control(
            select_folder, 
            title="Neue Rolle beginnen", 
            auto_id="cmdNewRoll", 
            control_type="Button", 
            timeout=30, 
            logger=logger
        )
        
        # Click on the "Neue Rolle beginnen" control
        click_button(newroll, logger)

        time.sleep(1)
        
        # Wait until the correct main window is visible again
        logger.info("Waiting for the main SMA window to reappear...")
        try:
            # Define the specific window class we're looking for
            main_window_class = "WindowsForms10.Window.8.app.0.141b42a_r6_ad1"
            
            # Wait for the window with the specific class to be visible
            main_win = find_window(app, 
                                   class_name=main_window_class,
                                   timeout=30,
                                   logger=logger)
            
            return main_win
        except Exception as e:
            logger.error(f"Error waiting for main window to reappear: {e}")
            
            # Try to print diagnostic information
            try:
                logger.info("Available windows:")
                for i, window in enumerate(app.windows()):
                    try:
                        logger.info(f"Window {i+1}: {window.window_text()} ({window.class_name()})")
                    except:
                        logger.info(f"Window {i+1}: [Could not get window information]")
            except Exception as diag_error:
                logger.error(f"Error getting diagnostic information: {diag_error}")
            
            raise
    
    except Exception as e:
        logger.error(f"Error handling data source selection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_start(main_win, app, logger):
    """Handle the film start process."""
    try:
        # Find the "Verfilmen starten" button
        start_film = find_control(
            main_win,
            title="Verfilmen starten", 
            auto_id="cmdStart", 
            control_type="Button", 
            timeout=30, 
            logger=logger
        )
        
        # Click the "Verfilmen starten" button
        click_button(start_film, logger)
        
        # Wait for the "Film einlegen" window to appear
        film_window_title = "Verfilmen der Dokumente"
        film_window = wait_for_window(
            app=app, 
            title=film_window_title, 
            timeout=30, 
            logger=logger
        )
        
        return film_window
    
    except Exception as e:
        logger.error(f"Error starting film process: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_insert(film_window, logger):
    """Handle the film insert dialog."""
    try:
        # Wait for the "Film einlegen" child window to appear
        logger.info("Waiting for 'Film einlegen' child window to appear...")
        
        # Find the "Film einlegen" window
        film_einlegen_window = None
        timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                children = film_window.children()
                logger.info(f"Found {len(children)} child controls in the window")
                
                for child in children:
                    try:
                        if child.window_text() == "Film einlegen":
                            film_einlegen_window = child
                            logger.info(f"Found 'Film einlegen' child window")
                            break
                    except Exception as e:
                        logger.error(f"Error checking child window: {e}")
                
                if film_einlegen_window is not None:
                    break
                    
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding 'Film einlegen' window: {e}")
                time.sleep(1)
        
        if film_einlegen_window is None:
            raise SMATimeoutError(
                operation="find_film_einlegen_window",
                timeout_duration=timeout,
                message=f"Could not find 'Film einlegen' child window within {timeout} seconds"
            )
        
        # Wait for the "Start" button to appear
        logger.info("Looking for 'Start' button...")
        start_button = None
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = film_einlegen_window.children()
                logger.info(f"Found {len(grandchildren)} grandchild controls in the 'Film einlegen' window")
                
                for grandchild in grandchildren:
                    try:
                        if grandchild.window_text() == "Start":
                            start_button = grandchild
                            logger.info(f"Found 'Start' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking grandchild control: {e}")
                
                if start_button is not None:
                    break
                    
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding 'Start' button: {e}")
                time.sleep(1)
        
        if start_button is None:
            raise SMATimeoutError(
                operation="find_start_button",
                timeout_duration=timeout,
                message=f"Could not find 'Start' button within {timeout} seconds"
            )
        
        # Click the "Start" button
        click_button(start_button, logger)
        
        return film_window
    
    except Exception as e:
        logger.error(f"Error handling film insert dialog: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def handle_film_number_entry(app, folder_path, film_window, logger, custom_filmnumber=None):
    """Handle the film number entry dialog."""
    try:
        # Either use the custom film number or extract it from the folder name
        if custom_filmnumber:
            filmnumber = custom_filmnumber
            logger.info(f"Using provided custom film number: {filmnumber}")
        else:
            # Extract the folder name from the selected folder path
            filmnumber = os.path.basename(folder_path)
            logger.info(f"Using folder name as film number: {filmnumber}")
        
        # Wait for the "Filmnummer eingeben" window to appear
        logger.info("Waiting for 'Filmnummer eingeben' window to appear...")
        timeout = 30
        start_time = time.time()
        filmnummer_window = None
        
        while time.time() - start_time < timeout:
            try:
                # Get all windows
                all_windows = app.windows()
                
                # Find the window with the "Filmnummer eingeben" child
                for window in all_windows:
                    try:
                        children = window.children()
                        for child in children:
                            try:
                                if child.window_text() == "Filmnummer eingeben":
                                    filmnummer_window = child
                                    logger.info("'Filmnummer eingeben' window found")
                                    break
                            except Exception as e:
                                logger.error(f"Error checking child window: {e}")
                        
                        if filmnummer_window is not None:
                            break
                    except Exception as e:
                        logger.error(f"Error finding 'Filmnummer eingeben' window: {e}")
                
                if filmnummer_window is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking window: {e}")
                time.sleep(1)
        
        if filmnummer_window is None:
            raise SMATimeoutError(
                operation="find_filmnummer_eingeben_window",
                timeout_duration=timeout,
                message=f"Could not find 'Filmnummer eingeben' window within {timeout} seconds"
            )
        
        # Find the text field in the "Filmnummer eingeben" window
        logger.info("Looking for text field in 'Filmnummer eingeben' window...")
        text_field = None
        
        try:
            # Get all child controls of the "Filmnummer eingeben" window
            grandchildren = filmnummer_window.children()
            logger.info(f"Found {len(grandchildren)} controls in 'Filmnummer eingeben' window")
            
            # Look for the text field with Control ID 6160962
            for control in grandchildren:
                try:
                    if control.control_id() == 6160962:
                        text_field = control
                        logger.info("Text field found by Control ID")
                        break
                except Exception as e:
                    logger.error(f"Error checking control: {e}")
            
            # If not found by Control ID, try by class name
            if text_field is None:
                for control in grandchildren:
                    try:
                        if control.class_name() == "WindowsForms10.EDIT.app.0.141b42a_r6_ad1":
                            text_field = control
                            logger.info("Text field found by class name")
                            break
                    except Exception as e:
                        logger.error(f"Error checking control: {e}")
        except Exception as e:
            logger.error(f"Error finding text field: {e}")
        
        if text_field is None:
            raise SMAControlNotFoundError(
                control_name="film_number_text_field",
                message="Could not find text field in 'Filmnummer eingeben' window"
            )
        
        # Set focus on the text field
        text_field.set_focus()
        logger.info("Text field focus set")
        
        # Clear the existing text and enter the film number
        text_field.set_text(filmnumber)
        logger.info(f"Entered film number: {filmnumber}")
        
        # Find and click the OK button
        logger.info("Looking for OK button...")
        ok_button = None
        
        try:
            # Look for the OK button
            for control in grandchildren:
                try:
                    if control.window_text() == "OK":
                        ok_button = control
                        logger.info("OK button found")
                        break
                except Exception as e:
                    logger.error(f"Error checking control for OK button: {e}")
        except Exception as e:
            logger.error(f"Error finding OK button: {e}")
        
        if ok_button is None:
            raise SMAControlNotFoundError(
                control_name="ok_button",
                message="Could not find OK button"
            )
        
        # Click the OK button
        click_button(ok_button, logger)
        
        return filmnumber, film_window
    
    except Exception as e:
        logger.error(f"Error handling film number entry: {e}")
        logger.error(traceback.format_exc())
        raise
    
def handle_endsymbole_prompt(film_window, app, logger):
    """Handle the Endsymbole prompt."""
    try:
        logger.info("Waiting for Endsymbole prompt...")
        timeout = 30
        start_time = time.time()
        ja_button = None
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
        
        # Now look for the Endsymbole text and 'Ja' button
        start_time = time.time()  # Reset timer
        found_endsymbole_text = False
        endsymbole_text = ""
        
        while time.time() - start_time < timeout:
            try:
                grandchildren = sma_title_window.children()
                
                # Search for Endsymbole text
                if not found_endsymbole_text:
                    for grandchild in grandchildren:
                        try:
                            if grandchild.class_name() == "WindowsForms10.STATIC.app.0.141b42a_r6_ad1":
                                grandchild_text = grandchild.window_text()
                                if "Endsymbole" in grandchild_text:
                                    found_endsymbole_text = True
                                    endsymbole_text = grandchild_text
                                    logger.info(f"Found 'Endsymbole' text: {grandchild_text}")
                                    break
                        except Exception as e:
                            logger.error(f"Error checking for Endsymbole text: {e}")
                
                # Look for the 'Ja' button
                for grandchild in grandchildren:
                    try:
                        if (grandchild.class_name() == "WindowsForms10.BUTTON.app.0.141b42a_r6_ad1" and 
                            grandchild.window_text() == "Ja"):
                            ja_button = grandchild
                            logger.info("Found 'Ja' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking for Ja button: {e}")
                
                if ja_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Endsymbole prompt: {e}")
                time.sleep(1)
        
        if ja_button is None:
            logger.warning("Could not find 'Ja' button for Endsymbole prompt within timeout")
            return False
        
        # Click the 'Ja' button
        click_button(ja_button, logger)
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Endsymbole prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def handle_nachspann_prompt(film_window, app, logger):
    """Handle the Nachspann prompt."""
    try:
        logger.info("Waiting for Nachspann prompt...")
        timeout = 30
        start_time = time.time()
        ja_button = None
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
        
        # Now look for the Nachspann text and 'Ja' button
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
                
                # Look for the 'Ja' button
                for grandchild in grandchildren:
                    try:
                        if (grandchild.class_name() == "WindowsForms10.BUTTON.app.0.141b42a_r6_ad1" and 
                            grandchild.window_text() == "Ja"):
                            ja_button = grandchild
                            logger.info("Found 'Ja' button")
                            break
                    except Exception as e:
                        logger.error(f"Error checking for Ja button: {e}")
                
                if ja_button is not None:
                    break
                
                # Wait a bit before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error finding Nachspann prompt: {e}")
                time.sleep(1)
        
        if ja_button is None:
            logger.warning("Could not find 'Ja' button for Nachspann prompt within timeout")
            return False
        
        # Click the 'Ja' button
        click_button(ja_button, logger)
        
        return True
    
    except Exception as e:
        logger.error(f"Error handling Nachspann prompt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def wait_for_transport_start(film_window, app, logger):
    """Wait for film transport to start."""
    try:
        logger.info("Waiting for film transport to start...")
        transport_started = False
        transport_window = None
        transport_control = None
        timeout = 60  # 1 minute timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout and not transport_started:
            try:
                # Get all windows
                all_windows = app.windows()
                
                # Check all windows for the transport message
                for window in all_windows:
                    try:
                        # Check the window text
                        window_text = window.window_text()
                        
                        if "Film wird transportiert" in window_text:
                            transport_started = True
                            transport_window = window
                            logger.info(f"Transport started: Found in window '{window_text}'")
                            break
                        
                        # Check all child controls
                        children = window.children()
                        
                        for child in children:
                            try:
                                # Check the child text
                                child_text = child.window_text()
                                
                                if "Film wird transportiert" in child_text:
                                    transport_started = True
                                    transport_window = window
                                    transport_control = child
                                    logger.info(f"Transport started: Found in child '{child_text}'")
                                    break
                                
                                # Check grandchild controls
                                try:
                                    grandchildren = child.children()
                                    
                                    for grandchild in grandchildren:
                                        try:
                                            grandchild_text = grandchild.window_text()
                                            
                                            if "Film wird transportiert" in grandchild_text:
                                                transport_started = True
                                                transport_window = window
                                                transport_control = grandchild
                                                logger.info(f"Transport started: Found in grandchild '{grandchild_text}'")
                                                break
                                        except Exception as e:
                                            pass
                                except Exception as e:
                                    pass
                            except Exception as e:
                                pass
                    except Exception as e:
                        pass
                    
                    if transport_started:
                        break
                
                if transport_started:
                    break
                
                # Wait before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking transport start: {e}")
                time.sleep(1)
        
        if not transport_started:
            logger.warning("Timeout waiting for film transport to start")
            return None, None
        
        return transport_window, transport_control
    
    except Exception as e:
        logger.error(f"Error waiting for transport to start: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None

def wait_for_transport_completion(transport_window, transport_control, app, logger):
    """Wait for film transport to complete."""
    try:
        # Now wait for the "Film wird transportiert" message to disappear
        logger.info("Waiting for film transport to complete...")
        transport_complete = False
        timeout = 300  # 5 minutes timeout
        start_time = time.time()
        
        # If we found a specific control, we can focus on that
        if transport_control is not None:
            logger.info(f"Monitoring specific control for disappearance: '{transport_control.window_text()}'")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Check if the control is still accessible by trying to get its text
                    try:
                        current_text = transport_control.window_text()
                        if "Film wird transportiert" not in current_text:
                            transport_complete = True
                            logger.info(f"Film transport completed! Transport control text changed to: '{current_text}'")
                            break
                    except Exception as e:
                        # If we can't get the text, the control might be gone
                        transport_complete = True
                        logger.info("Film transport completed! Could not access transport control text.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error checking transport control: {e}")
                    time.sleep(1)
        # If we only found the window but not a specific control
        elif transport_window is not None:
            logger.info(f"Monitoring window for transport message disappearance: '{transport_window.window_text()}'")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Check if the window is still accessible by trying to get its text
                    try:
                        current_text = transport_window.window_text()
                        if "Film wird transportiert" not in current_text:
                            transport_complete = True
                            logger.info(f"Film transport completed! Transport window text changed to: '{current_text}'")
                            break
                    except Exception as e:
                        # If we can't get the text, the window might be gone
                        transport_complete = True
                        logger.info("Film transport completed! Could not access transport window text.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error checking transport window: {e}")
                    time.sleep(1)
        # Fallback to checking all windows if we couldn't identify a specific window or control
        else:
            logger.info("No specific transport window or control identified. Checking all windows for message disappearance.")
            
            while time.time() - start_time < timeout and not transport_complete:
                try:
                    # Get all windows
                    all_windows = app.windows()
                    
                    # Check if the "Film wird transportiert" message is still present
                    transport_message_found = False
                    
                    # Check all windows for the transport message
                    for window in all_windows:
                        try:
                            # Check the window text
                            window_text = window.window_text()
                            
                            if "Film wird transportiert" in window_text:
                                transport_message_found = True
                                logger.info(f"Transport message still present: Found in window '{window_text}'")
                                break
                            
                            # Check all child controls
                            children = window.children()
                            
                            for child in children:
                                try:
                                    # Check the child text
                                    child_text = child.window_text()
                                    
                                    if "Film wird transportiert" in child_text:
                                        transport_message_found = True
                                        logger.info(f"Transport message still present: Found in child '{child_text}'")
                                        break
                                    
                                    # Check grandchild controls
                                    try:
                                        grandchildren = child.children()
                                        
                                        for grandchild in grandchildren:
                                            try:
                                                grandchild_text = grandchild.window_text()
                                                
                                                if "Film wird transportiert" in grandchild_text:
                                                    transport_message_found = True
                                                    logger.info(f"Transport message still present: Found in grandchild '{grandchild_text}'")
                                                    break
                                            except Exception as e:
                                                pass
                                    except Exception as e:
                                        pass
                                except Exception as e:
                                    pass
                        except Exception as e:
                            pass
                        
                        if transport_message_found:
                            break
                    
                    # If the message is not found, transport is complete
                    if not transport_message_found:
                        transport_complete = True
                        logger.info("Film transport completed! No transport message found in any window.")
                        break
                    
                    # Log status every 10 seconds
                    elapsed = time.time() - start_time
                    if elapsed % 10 < 1:  # Log approximately every 10 seconds
                        logger.info(f"Transport still in progress... ({int(elapsed)} seconds elapsed)")
                    
                    # Wait before checking again
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Error checking transport status: {e}")
                    time.sleep(2)
        
        if not transport_complete:
            logger.warning("Timeout waiting for film transport to complete")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error waiting for transport completion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False 