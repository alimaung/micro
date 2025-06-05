import sys
import os
import time

# Add the parent directory to the path to access sma module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pywinauto import Application, Desktop
from sma.ui_automation import find_window, find_control, click_button

def test_button_detection():
    """Simple test to detect Zurück and Nein buttons without clicking."""
    try:
        # Connect to existing SMA application by process name
        app = Application(backend="uia").connect(path="file-sma.exe")
        print("Connected to SMA application")
        
        # List all windows to debug
        print("Available windows from app:")
        for i, window in enumerate(app.windows()):
            try:
                title = window.window_text()
                class_name = window.class_name()
                print(f"  Window {i}: '{title}' (class: {class_name})")
            except:
                print(f"  Window {i}: [Could not get window info]")
        
        # Also search all desktop windows for SMA-related windows
        print("\nSearching all desktop windows for SMA process:")
        desktop = Desktop(backend="uia")
        all_windows = desktop.windows()
        sma_windows = []
        
        for window in all_windows:
            try:
                # Check if this window belongs to our SMA process
                if hasattr(window, 'process_id') and window.process_id() == app.process:
                    title = window.window_text()
                    class_name = window.class_name()
                    print(f"  SMA Window: '{title}' (class: {class_name})")
                    sma_windows.append(window)
            except:
                continue
        
        # Search for both Zurück and Nein buttons in all SMA windows (including grandchildren)
        print("\nSearching for Zurück and Nein buttons in all SMA windows (including grandchildren)...")
        zurueck_button = None
        nein_button = None
        
        for window in sma_windows:
            try:
                print(f"\nSearching in window: '{window.window_text()}'")
                children = window.children()
                
                # Search children
                for i, child in enumerate(children):
                    try:
                        text = child.window_text()
                        class_name = child.class_name()
                        print(f"  Child {i}: '{text}' (class: {class_name})")
                        
                        # Check for Zurück button
                        if text == "Zurück" and "BUTTON" in class_name:
                            zurueck_button = child
                            print(f"*** Found Zurück button in child {i}!")
                        
                        # Check for Nein button
                        if text == "Nein" and "BUTTON" in class_name:
                            nein_button = child
                            print(f"*** Found Nein button in child {i}!")
                        
                        # Search grandchildren (children of children)
                        try:
                            grandchildren = child.children()
                            for j, grandchild in enumerate(grandchildren):
                                try:
                                    gtext = grandchild.window_text()
                                    gclass = grandchild.class_name()
                                    print(f"    Grandchild {i}.{j}: '{gtext}' (class: {gclass})")
                                    
                                    # Check for Zurück button in grandchildren
                                    if gtext == "Zurück" and "BUTTON" in gclass:
                                        zurueck_button = grandchild
                                        print(f"*** Found Zurück button in grandchild {i}.{j}!")
                                    
                                    # Check for Nein button in grandchildren
                                    if gtext == "Nein" and "BUTTON" in gclass:
                                        nein_button = grandchild
                                        print(f"*** Found Nein button in grandchild {i}.{j}!")
                                        
                                except Exception as e:
                                    print(f"    Grandchild {i}.{j}: [Error: {e}]")
                                
                        except Exception as e:
                            pass  # No grandchildren or error accessing them
                            
                    except Exception as e:
                        print(f"  Child {i}: [Error: {e}]")
                    
            except Exception as e:
                print(f"Error searching window '{window.window_text()}': {e}")
        
        # Report findings
        print(f"\n=== DETECTION RESULTS ===")
        if zurueck_button is not None:
            print(f"✓ Zurück button found: class={zurueck_button.class_name()}")
        else:
            print("✗ Zurück button NOT found")
            
        if nein_button is not None:
            print(f"✓ Nein button found: class={nein_button.class_name()}")
        else:
            print("✗ Nein button NOT found")
        
        # Commented out clicking functionality
        # if zurueck_button is not None:
        #     print(f"Clicking Zurück button...")
        #     click_button(zurueck_button)
        #     print("Clicked Zurück button successfully")
        
        # if nein_button is not None:
        #     print(f"Clicking Nein button...")
        #     click_button(nein_button)
        #     print("Clicked Nein button successfully")
        
        return zurueck_button is not None or nein_button is not None
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing SMA button detection...")
    success = test_button_detection()
    
    # More specific success messages
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed - no buttons detected!")
