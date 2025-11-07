#!/usr/bin/env python3
"""
SMA Window Toggle System Tray
Provides a system tray interface to toggle the "bring to window" functionality of SMA automation.
"""

import sys
import subprocess
import threading
import time
import json
import win32gui
from pathlib import Path

# Try to import pystray, install if not available
try:
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "pillow"])
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw, ImageFont

# Try to import pywinauto for window control
try:
    from pywinauto import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    print("Warning: pywinauto not available. Window control will be limited.")
    PYWINAUTO_AVAILABLE = False


class SMAWindowToggle:
    """SMA Window Toggle System Tray Application"""
    
    def __init__(self):
        self.icon = None
        self.status_thread = None
        self.should_stop = False
        
        # Window bring-to-front toggle state
        self.bring_to_front_enabled = True
        self.config_file = Path(__file__).parent / "sma_toggle_config.json"
        
        # SMA window tracking
        self.sma_windows = []
        self.last_window_check = 0
        self.window_check_interval = 2.0  # Check every 2 seconds
        
        # Load configuration
        self.load_config()
        
        # Get the directory where this script is located
        self.script_dir = Path(__file__).parent
        self.icon_path = self.script_dir / "sma-logo.ico"
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.bring_to_front_enabled = config.get('bring_to_front_enabled', True)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.bring_to_front_enabled = True
    
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'bring_to_front_enabled': self.bring_to_front_enabled
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_default_icon(self):
        """Create a default icon for SMA toggle"""
        width = 64
        height = 64
        
        # Use green if enabled, red if disabled
        color = 'green' if self.bring_to_front_enabled else 'red'
        
        image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a simple icon with SMA text
        dc.ellipse([width//8, height//8, 7*width//8, 7*height//8], fill=color)
        dc.text((width//2-15, height//2-8), "SMA", fill='white', font_size=16)
        
        return image
    
    def find_sma_windows(self):
        """Find SMA windows using win32gui."""
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # Look for SMA-related windows
                if (window_text and 
                    (window_text.startswith("SMA 51") or 
                     window_text == "Verfilmen der Dokumente" or
                     "SMA" in window_text)):
                    windows.append({
                        'hwnd': hwnd,
                        'title': window_text,
                        'class_name': class_name
                    })
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        return windows
    
    def bring_sma_windows_to_front(self):
        """Bring SMA windows to front if enabled."""
        if not self.bring_to_front_enabled:
            return False
        
        try:
            windows = self.find_sma_windows()
            brought_to_front = False
            
            for window in windows:
                hwnd = window['hwnd']
                title = window['title']
                
                try:
                    # Restore window if minimized
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                    
                    # Bring to foreground
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    
                    print(f"Brought SMA window to front: {title}")
                    brought_to_front = True
                    
                except Exception as e:
                    print(f"Error bringing window '{title}' to front: {e}")
            
            return brought_to_front
            
        except Exception as e:
            print(f"Error in bring_sma_windows_to_front: {e}")
            return False
    
    def bring_sma_windows_to_front_pywinauto(self):
        """Bring SMA windows to front using pywinauto if available."""
        if not self.bring_to_front_enabled or not PYWINAUTO_AVAILABLE:
            return False
        
        try:
            # Try to connect to SMA application
            app = Application(backend="uia").connect(title_re=".*SMA.*")
            
            # Find main SMA window
            main_window = None
            for window in app.windows():
                try:
                    title = window.window_text()
                    if title and (title.startswith("SMA 51") or "Verfilmen der Dokumente" in title):
                        main_window = window
                        break
                except Exception:
                    continue
            
            if main_window:
                try:
                    main_window.set_focus()
                    main_window.restore()  # In case it's minimized
                    main_window.bring_to_top()  # Bring to top of Z-order
                    print(f"Brought SMA window to front using pywinauto: {main_window.window_text()}")
                    return True
                except Exception as e:
                    print(f"Error with pywinauto window control: {e}")
                    return False
            
        except Exception as e:
            print(f"Error connecting to SMA with pywinauto: {e}")
            return False
        
        return False
    
    def status_monitor_thread(self):
        """Background thread to monitor SMA windows and update status."""
        while not self.should_stop:
            current_time = time.time()
            
            # Check for SMA windows periodically
            if current_time - self.last_window_check > self.window_check_interval:
                self.sma_windows = self.find_sma_windows()
                self.last_window_check = current_time
                
                # Update the menu
                if self.icon:
                    self.icon.menu = self.create_menu()
            
            time.sleep(1)  # Check every second
    
    def create_status_text(self):
        """Create the status text with current state."""
        status_icon = "🟢" if self.bring_to_front_enabled else "🔴"
        window_count = len(self.sma_windows)
        
        status_text = f"  {status_icon} Bring to Front: {'ON' if self.bring_to_front_enabled else 'OFF'}  "
        window_text = f"  📱 SMA Windows Found: {window_count}  "
        
        return status_text, window_text
    
    def create_menu(self):
        """Create the system tray menu."""
        status_text, window_text = self.create_status_text()
        
        menu_items = [
            # Status header
            item(status_text, None, enabled=False),
            item(window_text, None, enabled=False),
            Menu.SEPARATOR,
            
            # Toggle functionality
            item("✅ Enable Bring to Front" if not self.bring_to_front_enabled else "❌ Disable Bring to Front", 
                 self.toggle_bring_to_front),
            Menu.SEPARATOR,
            
            # Manual actions
            item("🔄 Bring SMA Windows to Front Now", self.manual_bring_to_front),
            item("🔍 Refresh Window List", self.refresh_windows),
            Menu.SEPARATOR,
        ]
        
        # Add individual window controls if windows are found
        if self.sma_windows:
            menu_items.append(item("SMA Windows:", None, enabled=False))
            for i, window in enumerate(self.sma_windows[:5]):  # Limit to 5 windows
                title = window['title'][:30] + "..." if len(window['title']) > 30 else window['title']
                menu_items.append(
                    item(f"  📋 {title}", 
                         lambda icon, item, hwnd=window['hwnd']: self.bring_specific_window_to_front(hwnd))
                )
            menu_items.append(Menu.SEPARATOR)
        
        # Exit
        menu_items.append(item("❌ Exit", self.quit_app))
        
        return Menu(*menu_items)
    
    def toggle_bring_to_front(self, icon, item):
        """Toggle the bring to front functionality."""
        self.bring_to_front_enabled = not self.bring_to_front_enabled
        self.save_config()
        
        # Update icon
        self.icon.icon = self.create_default_icon()
        
        status = "enabled" if self.bring_to_front_enabled else "disabled"
        print(f"SMA bring to front functionality {status}")
    
    def manual_bring_to_front(self, icon, item):
        """Manually bring SMA windows to front."""
        print("Manually bringing SMA windows to front...")
        
        # Try pywinauto first, then fall back to win32gui
        success = self.bring_sma_windows_to_front_pywinauto()
        if not success:
            success = self.bring_sma_windows_to_front()
        
        if not success:
            print("No SMA windows found or failed to bring to front")
    
    def bring_specific_window_to_front(self, hwnd):
        """Bring a specific window to front."""
        try:
            # Restore window if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
            
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            title = win32gui.GetWindowText(hwnd)
            print(f"Brought specific SMA window to front: {title}")
            
        except Exception as e:
            print(f"Error bringing specific window to front: {e}")
    
    def refresh_windows(self, icon, item):
        """Refresh the window list."""
        self.sma_windows = self.find_sma_windows()
        print(f"Refreshed window list. Found {len(self.sma_windows)} SMA windows.")
    
    def quit_app(self, icon, item):
        """Exit the application."""
        self.should_stop = True
        if self.status_thread:
            self.status_thread.join(timeout=1)
        icon.stop()
    
    def run(self):
        """Run the system tray application."""
        # Try to load the icon file, create a default one if not found
        if self.icon_path.exists():
            try:
                icon_image = Image.open(self.icon_path)
            except:
                icon_image = self.create_default_icon()
        else:
            icon_image = self.create_default_icon()
        
        # Initial window check
        self.sma_windows = self.find_sma_windows()
        
        # Create the system tray icon
        self.icon = pystray.Icon(
            "SMAToggle",
            icon_image,
            "SMA Window Toggle",
            self.create_menu()
        )
        
        # Start the status monitoring thread
        self.status_thread = threading.Thread(target=self.status_monitor_thread, daemon=True)
        self.status_thread.start()
        
        print("SMA Window Toggle system tray started")
        print(f"Bring to front functionality: {'ENABLED' if self.bring_to_front_enabled else 'DISABLED'}")
        print("Right-click the tray icon for options")
        
        # Run the icon
        self.icon.run()


def main():
    """Main function"""
    try:
        app = SMAWindowToggle()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



