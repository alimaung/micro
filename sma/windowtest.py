
#!/usr/bin/env python3
"""
Continuous window monitoring script for SMA automation debugging.
Monitors only WindowsForms10.Window.8.app.0.141b42a_r6_ad1 class windows.
"""

import win32gui
import time
import datetime

TARGET_CLASS = ["WindowsForms10.Window.8.app.0.141b42a_r6_ad1", "WindowsForms10.Window.8.app.0.141b42a_r7_ad1"]

def enum_window_callback(hwnd, windows):
    """Callback function for enumerating windows."""
    if win32gui.IsWindowVisible(hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if class_name in TARGET_CLASS:
            windows.append((hwnd, window_text, class_name))
    return True

def get_target_windows():
    """Get all visible windows with the target class."""
    windows = []
    win32gui.EnumWindows(enum_window_callback, windows)
    return windows

def format_timestamp():
    """Get current timestamp formatted for display."""
    return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    """Main monitoring loop."""
    print(f"=== Monitoring Windows with Class: {TARGET_CLASS} ===")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            timestamp = format_timestamp()
            windows = get_target_windows()
            
            if windows:
                # Print all found windows on one line
                titles = [f'"{title}"' if title else "(No title)" for _, title, _ in windows]
                print(f"[{timestamp}] Found {len(windows)}: {' | '.join(titles)}")
            else:
                print(f"[{timestamp}] No windows found")
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()