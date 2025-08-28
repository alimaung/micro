#!/usr/bin/env python3
"""
System Tray Example Application
A comprehensive example showing how to create a Windows system tray application
with a rich menu interface and various functionality.
"""

import sys
import os
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import webbrowser
import subprocess
import json
from pathlib import Path

# Try to import pystray, install if not available
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "pillow"])
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw


class SystemTrayApp:
    """Main system tray application class"""
    
    def __init__(self):
        self.icon = None
        self.running = False
        self.status = "Active"
        self.notifications_enabled = True
        self.auto_start = False
        self.settings = self.load_settings()
        
        # Get the directory where this script is located
        self.script_dir = Path(__file__).parent
        self.icon_path = self.script_dir / "app-logo.ico"
        
        # Create the system tray icon
        self.create_icon()
        
    def load_settings(self):
        """Load application settings from JSON file"""
        settings_file = Path(__file__).parent / "settings.json"
        default_settings = {
            "notifications_enabled": True,
            "auto_start": False,
            "theme": "default",
            "language": "en"
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        """Save application settings to JSON file"""
        settings_file = Path(__file__).parent / "settings.json"
        self.settings.update({
            "notifications_enabled": self.notifications_enabled,
            "auto_start": self.auto_start
        })
        
        with open(settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def create_icon(self):
        """Create the system tray icon with menu"""
        
        # Try to load the icon file, create a default one if not found
        if self.icon_path.exists():
            try:
                icon_image = Image.open(self.icon_path)
            except:
                icon_image = self.create_default_icon()
        else:
            icon_image = self.create_default_icon()
        
        # Create the menu structure using correct pystray syntax
        menu = pystray.Menu(
            # Main status item
            item(f"Status: {self.status}", self.show_status, enabled=False),
            pystray.Menu.SEPARATOR,
            
            # Quick actions
            item("Show Main Window", self.show_main_window),
            item("Open Log File", self.open_log_file),
            item("Check for Updates", self.check_updates),
            pystray.Menu.SEPARATOR,
            
            # Settings submenu
            item(
                "Settings",
                pystray.Menu(
                    item("Notifications", self.toggle_notifications),
                    item("Auto Start", self.toggle_auto_start),
                    pystray.Menu.SEPARATOR,
                    item("Preferences...", self.show_preferences),
                    item("Reset Settings", self.reset_settings)
                )
            ),
            
            # Tools submenu
            item(
                "Tools",
                pystray.Menu(
                    item("System Information", self.show_system_info),
                    item("Network Status", self.show_network_status),
                    item("Process Monitor", self.show_process_monitor),
                    pystray.Menu.SEPARATOR,
                    item("Open Task Manager", self.open_task_manager),
                    item("Open Control Panel", self.open_control_panel)
                )
            ),
            
            # Help submenu
            item(
                "Help",
                pystray.Menu(
                    item("Documentation", self.open_documentation),
                    item("About", self.show_about),
                    item("Report Bug", self.report_bug),
                    pystray.Menu.SEPARATOR,
                    item("Check for Updates", self.check_updates)
                )
            ),
            
            pystray.Menu.SEPARATOR,
            
            # Exit option
            item("Exit", self.stop)
        )
        
        # Create the system tray icon
        self.icon = pystray.Icon(
            "SystemTrayExample",
            icon_image,
            "System Tray Example App",
            menu
        )
    
    def create_default_icon(self):
        """Create a default icon if the .ico file is not available"""
        # Create a simple colored icon
        width = 64
        height = 64
        color = 'blue'
        
        image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a simple icon
        dc.ellipse([width//4, height//4, 3*width//4, 3*height//4], fill=color)
        dc.text((width//2-10, height//2-10), "ST", fill='white')
        
        return image
    
    def show_status(self, icon, item):
        """Show current application status"""
        messagebox.showinfo("Status", f"Application Status: {self.status}\nRunning since: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_main_window(self, icon, item):
        """Show the main application window"""
        self.create_main_window()
    
    def create_main_window(self):
        """Create and show the main application window"""
        root = tk.Tk()
        root.title("System Tray Example - Main Window")
        root.geometry("600x400")
        root.resizable(True, True)
        
        # Center the window
        root.eval('tk::PlaceWindow . center')
        
        # Create main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="System Tray Example Application", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status section
        status_frame = tk.LabelFrame(main_frame, text="Application Status", padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(status_frame, text=f"Status: {self.status}").pack(anchor=tk.W)
        tk.Label(status_frame, text=f"Notifications: {'Enabled' if self.notifications_enabled else 'Disabled'}").pack(anchor=tk.W)
        tk.Label(status_frame, text=f"Auto Start: {'Enabled' if self.auto_start else 'Disabled'}").pack(anchor=tk.W)
        
        # Quick actions section
        actions_frame = tk.LabelFrame(main_frame, text="Quick Actions", padx=10, pady=10)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(actions_frame, text="Refresh Status", 
                 command=lambda: self.refresh_status(status_frame)).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Toggle Notifications", 
                 command=self.toggle_notifications_from_gui).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Open Settings", 
                 command=self.show_preferences).pack(side=tk.LEFT, padx=5)
        
        # Log section
        log_frame = tk.LabelFrame(main_frame, text="Recent Activity", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add some sample log entries
        log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Application started\n")
        log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Main window opened\n")
        log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Status: {self.status}\n")
        log_text.see(tk.END)
        
        # Close button
        tk.Button(main_frame, text="Close", command=root.destroy).pack(pady=(10, 0))
        
        # Make window modal
        root.transient()
        root.grab_set()
        root.wait_window()
    
    def refresh_status(self, status_frame):
        """Refresh the status display"""
        for widget in status_frame.winfo_children():
            widget.destroy()
        
        tk.Label(status_frame, text=f"Status: {self.status}").pack(anchor=tk.W)
        tk.Label(status_frame, text=f"Notifications: {'Enabled' if self.notifications_enabled else 'Disabled'}").pack(anchor=tk.W)
        tk.Label(status_frame, text=f"Auto Start: {'Enabled' if self.auto_start else 'Disabled'}").pack(anchor=tk.W)
    
    def toggle_notifications_from_gui(self):
        """Toggle notifications from GUI"""
        self.notifications_enabled = not self.notifications_enabled
        self.save_settings()
        messagebox.showinfo("Settings", f"Notifications {'enabled' if self.notifications_enabled else 'disabled'}")
    
    def open_log_file(self, icon, item):
        """Open the application log file"""
        log_file = self.script_dir / "app.log"
        
        # Create a sample log file if it doesn't exist
        if not log_file.exists():
            with open(log_file, 'w') as f:
                f.write(f"[{datetime.now()}] Application log started\n")
                f.write(f"[{datetime.now()}] System tray initialized\n")
        
        try:
            os.startfile(str(log_file))
        except:
            messagebox.showinfo("Log File", f"Log file location: {log_file}")
    
    def check_updates(self, icon, item):
        """Check for application updates"""
        # Simulate update check
        messagebox.showinfo("Updates", "Checking for updates...\nNo updates available at this time.")
    
    def toggle_notifications(self, icon, item):
        """Toggle notification settings"""
        self.notifications_enabled = not self.notifications_enabled
        self.save_settings()
        
        if self.notifications_enabled:
            self.show_notification("Notifications Enabled", "You will now receive notifications")
        else:
            self.show_notification("Notifications Disabled", "You will no longer receive notifications")
    
    def toggle_auto_start(self, icon, item):
        """Toggle auto-start setting"""
        self.auto_start = not self.auto_start
        self.save_settings()
        
        status = "enabled" if self.auto_start else "disabled"
        messagebox.showinfo("Auto Start", f"Auto start {status}")
    
    def show_preferences(self, icon=None, item=None):
        """Show preferences dialog"""
        root = tk.Tk()
        root.title("Preferences")
        root.geometry("400x300")
        root.resizable(False, False)
        
        # Center the window
        root.eval('tk::PlaceWindow . center')
        
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings
        tk.Label(main_frame, text="Application Preferences", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Notifications
        notif_var = tk.BooleanVar(value=self.notifications_enabled)
        tk.Checkbutton(main_frame, text="Enable Notifications", variable=notif_var).pack(anchor=tk.W, pady=5)
        
        # Auto start
        auto_var = tk.BooleanVar(value=self.auto_start)
        tk.Checkbutton(main_frame, text="Start with Windows", variable=auto_var).pack(anchor=tk.W, pady=5)
        
        # Theme selection
        theme_frame = tk.Frame(main_frame)
        theme_frame.pack(fill=tk.X, pady=10)
        tk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        theme_var = tk.StringVar(value=self.settings.get("theme", "default"))
        theme_combo = tk.OptionMenu(theme_frame, theme_var, "default", "dark", "light")
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_preferences():
            self.notifications_enabled = notif_var.get()
            self.auto_start = auto_var.get()
            self.settings["theme"] = theme_var.get()
            self.save_settings()
            messagebox.showinfo("Preferences", "Settings saved successfully!")
            root.destroy()
        
        tk.Button(button_frame, text="Save", command=save_preferences).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side=tk.RIGHT)
        
        # Make window modal
        root.transient()
        root.grab_set()
        root.wait_window()
    
    def reset_settings(self, icon, item):
        """Reset all settings to default"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to default?"):
            self.notifications_enabled = True
            self.auto_start = False
            self.settings = {
                "notifications_enabled": True,
                "auto_start": False,
                "theme": "default",
                "language": "en"
            }
            self.save_settings()
            messagebox.showinfo("Settings Reset", "All settings have been reset to default values.")
    
    def show_system_info(self, icon, item):
        """Show system information"""
        import platform
        
        info = f"""System Information:
        
OS: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}
Python Version: {platform.python_version()}
        
Application Status: {self.status}
Notifications: {'Enabled' if self.notifications_enabled else 'Disabled'}
Auto Start: {'Enabled' if self.auto_start else 'Disabled'}"""
        
        messagebox.showinfo("System Information", info)
    
    def show_network_status(self, icon, item):
        """Show network status"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            info = f"""Network Status:
            
Hostname: {hostname}
Local IP: {local_ip}
Status: Connected"""
            
            messagebox.showinfo("Network Status", info)
        except:
            messagebox.showinfo("Network Status", "Unable to retrieve network information")
    
    def show_process_monitor(self, icon, item):
        """Show process monitor"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            info = "Top 10 Processes by CPU Usage:\n\n"
            for i, proc in enumerate(processes[:10]):
                info += f"{i+1}. {proc['name']} (PID: {proc['pid']})\n"
                info += f"   CPU: {proc['cpu_percent']:.1f}% | Memory: {proc['memory_percent']:.1f}%\n\n"
            
            messagebox.showinfo("Process Monitor", info)
        except ImportError:
            messagebox.showinfo("Process Monitor", "psutil not available. Install with: pip install psutil")
        except:
            messagebox.showinfo("Process Monitor", "Unable to retrieve process information")
    
    def open_task_manager(self, icon, item):
        """Open Windows Task Manager"""
        try:
            subprocess.Popen("taskmgr")
        except:
            messagebox.showinfo("Task Manager", "Unable to open Task Manager")
    
    def open_control_panel(self, icon, item):
        """Open Windows Control Panel"""
        try:
            subprocess.Popen("control")
        except:
            messagebox.showinfo("Control Panel", "Unable to open Control Panel")
    
    def open_documentation(self, icon, item):
        """Open documentation"""
        webbrowser.open("https://github.com/your-repo/system-tray-example")
    
    def show_about(self, icon, item):
        """Show about dialog"""
        about_text = """System Tray Example Application
Version 1.0.0

A comprehensive example of a Windows system tray application
with rich menu functionality and user interface.

Features:
• System tray integration
• Rich menu system
• Settings management
• System information display
• Process monitoring
• Network status
• Logging capabilities

Created with Python and pystray library."""
        
        messagebox.showinfo("About", about_text)
    
    def report_bug(self, icon, item):
        """Report a bug"""
        webbrowser.open("https://github.com/your-repo/system-tray-example/issues")
    
    def show_notification(self, title, message):
        """Show a system notification"""
        if self.notifications_enabled and self.icon:
            self.icon.notify(title, message)
    
    def run(self):
        """Run the system tray application"""
        self.running = True
        print("Starting System Tray Application...")
        print(f"Icon file: {self.icon_path}")
        print("Right-click the system tray icon to see the menu")
        
        # Show initial notification
        self.show_notification("System Tray App", "Application started successfully!")
        
        # Run the icon
        self.icon.run()
    
    def stop(self, icon, item):
        """Stop the application"""
        self.running = False
        self.save_settings()
        self.show_notification("System Tray App", "Application shutting down...")
        self.icon.stop()


def main():
    """Main function"""
    try:
        app = SystemTrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Application error: {e}")


if __name__ == "__main__":
    main()
