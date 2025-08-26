
#!/usr/bin/env python3
"""
Simple window enumeration test script.
Prints out all current window titles and class names.
"""

import win32gui
import win32con

def enum_window_callback(hwnd, windows):
    """Callback function for enumerating windows."""
    if win32gui.IsWindowVisible(hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if window_text:  # Only show windows with titles
            windows.append((hwnd, window_text, class_name))
    return True

def get_all_windows():
    """Get all visible windows with titles."""
    windows = []
    win32gui.EnumWindows(enum_window_callback, windows)
    return windows

def main():
    """Main function to print all window information."""
    print("=== Current Windows ===")
    print()
    
    windows = get_all_windows()
    
    if not windows:
        print("No visible windows found.")
        return
    
    print(f"Found {len(windows)} visible windows:")
    print()
    
    for i, (hwnd, title, class_name) in enumerate(windows, 1):
        print(f"[{i:2}] Title: {title}")
        print(f"     Class: {class_name}")
        print(f"     Handle: {hwnd}")
        print()

if __name__ == "__main__":
    main()