#!/usr/bin/env python3
"""
Django Micro Project System Tray
Shows Django server status and provides basic controls
"""

import sys
import subprocess
import threading
import time
import requests
from pathlib import Path

# Try to import pystray, install if not available
try:
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "pillow", "requests"])
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw, ImageFont


class DjangoTrayApp:
    """Django System Tray Application"""
    
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.server_status = "Unknown"
        self.is_running = False
        self.icon = None
        self.status_thread = None
        self.should_stop = False
        
        # Get the directory where this script is located
        self.script_dir = Path(__file__).parent
        self.icon_path = self.script_dir / "app-logo.ico"
        self.django_dir = Path(__file__).parent.parent.parent / "micro"
    
    def create_default_icon(self):
        """Create a default icon if app-logo.ico is not available"""
        width = 64
        height = 64
        color = 'blue'
        
        image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a simple icon
        dc.ellipse([width//4, height//4, 3*width//4, 3*height//4], fill=color)
        dc.text((width//2-10, height//2-10), "ST", fill='white')
        
        return image
    
    def check_server_status(self):
        """Check if Django server is running"""
        try:
            response = requests.get(self.server_url, timeout=2)
            if response.status_code == 200:
                self.server_status = "Running"
                self.is_running = True
            else:
                self.server_status = f"Error {response.status_code}"
                self.is_running = False
        except requests.exceptions.ConnectionError:
            self.server_status = "Stopped"
            self.is_running = False
        except requests.exceptions.Timeout:
            self.server_status = "Timeout"
            self.is_running = False
        except Exception as e:
            self.server_status = f"Error: {str(e)[:20]}"
            self.is_running = False
    
    def status_monitor_thread(self):
        """Background thread to monitor server status"""
        while not self.should_stop:
            self.check_server_status()
            if self.icon:
                # Update the menu
                self.icon.menu = self.create_menu()
            time.sleep(5)  # Check every 5 seconds
    
    def create_status_item_text(self):
        """Create the status text with LED indicator - taller appearance"""
        led = "🟢" if self.is_running else "🔴"
        # Add padding spaces to make it appear taller
        return f"  {led} Django Server: {self.server_status}  "
    
    def create_menu(self):
        """Create the system tray menu"""
        return Menu(
            # Status header (single row with LED, status, and URL)
            item(self.create_status_item_text(), None, enabled=False),
            Menu.SEPARATOR,
            
            # Quick actions
            item("Open in Browser", self.open_browser),
            item("Start Server", self.start_server, enabled=not self.is_running),
            item("Stop Server", self.stop_server, enabled=self.is_running),
            Menu.SEPARATOR,
            
            # Exit
            item("Exit", self.quit_app)
        )
    
    def show_status(self, icon, item):
        """Show detailed status (placeholder)"""
        pass
    
    def open_browser(self, icon, item):
        """Open the Django site in browser"""
        import webbrowser
        webbrowser.open(self.server_url)
    
    def start_server(self, icon, item):
        """Start the Django development server"""
        try:
            import subprocess
            import os
            
            # Change to the Django project directory
            os.chdir(self.django_dir)
            
            # Start the server in a separate process
            subprocess.Popen([
                sys.executable, 
                "manage.py", 
                "runserver", 
                "localhost:8000"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            
            # Give it a moment to start
            time.sleep(2)
            self.check_server_status()
            
        except Exception as e:
            print(f"Error starting server: {e}")
    
    def stop_server(self, icon, item):
        """Stop the Django development server"""
        try:
            # On Windows, we can use taskkill to stop the server
            if sys.platform == "win32":
                # Kill all python processes running manage.py
                subprocess.run([
                    "taskkill", "/f", "/im", "python.exe", "/fi", 
                    "WINDOWTITLE eq*manage.py*"
                ], capture_output=True)
            
            # Give it a moment to stop
            time.sleep(2)
            self.check_server_status()
            
        except Exception as e:
            print(f"Error stopping server: {e}")
    
    def quit_app(self, icon, item):
        """Exit the application"""
        self.should_stop = True
        if self.status_thread:
            self.status_thread.join(timeout=1)
        icon.stop()
    
    def run(self):
        """Run the system tray application"""
        # Try to load the icon file, create a default one if not found
        if self.icon_path.exists():
            try:
                icon_image = Image.open(self.icon_path)
            except:
                icon_image = self.create_default_icon()
        else:
            icon_image = self.create_default_icon()
        
        # Initial status check
        self.check_server_status()
        
        # Create the system tray icon
        self.icon = pystray.Icon(
            "DjangoMicro",
            icon_image,
            "Django Micro Project",
            self.create_menu()
        )
        
        # Start the status monitoring thread
        self.status_thread = threading.Thread(target=self.status_monitor_thread, daemon=True)
        self.status_thread.start()
        
        print("Django Micro system tray started")
        print(f"Monitoring: {self.server_url}")
        print("Right-click the tray icon for options")
        
        # Run the icon
        self.icon.run()


def main():
    """Main function"""
    try:
        app = DjangoTrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
