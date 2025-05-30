import ctypes
import time
import pyautogui
import threading

# Get user32 DLL
user32 = ctypes.windll.user32

# Define RECT structure manually
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

# Define Monitor 2 (Left) boundaries **with padding**
MARGIN = 20  # Shrinking the boundary by 20px on each side
LEFT_MONITOR_BOUNDS = RECT(0 + MARGIN, 0 + MARGIN, 1920 - MARGIN, 1080 - MARGIN)

# Global variable to control the monitoring thread
monitoring_active = False
monitor_thread = None

def lock_mouse_to_monitor():
    """ Restricts the mouse to only Monitor 2 (with a safety margin) """
    user32.ClipCursor(ctypes.byref(LEFT_MONITOR_BOUNDS))
    print(f"[INFO] Mouse locked inside adjusted area: {LEFT_MONITOR_BOUNDS.left}-{LEFT_MONITOR_BOUNDS.right}, {LEFT_MONITOR_BOUNDS.top}-{LEFT_MONITOR_BOUNDS.bottom}")

def release_mouse_lock():
    """ Releases the mouse restriction """
    # Passing NULL pointer to ClipCursor removes any restriction
    user32.ClipCursor(None)
    print("[INFO] Mouse lock released")

def check_mouse_position():
    """ Monitors if the mouse escapes and brings it back """
    global monitoring_active
    while monitoring_active:
        x, y = pyautogui.position()

        if x < LEFT_MONITOR_BOUNDS.left or x > LEFT_MONITOR_BOUNDS.right - 1 or \
           y < LEFT_MONITOR_BOUNDS.top or y > LEFT_MONITOR_BOUNDS.bottom - 1:
            print(f"[WARNING] Mouse tried to escape! ({x}, {y}) - Bringing it back.")
            lock_mouse_to_monitor()  # Reapply the lock

        time.sleep(0.05)  # Check every 50ms (faster reaction)

def start_mouse_lock():
    """ Starts the mouse lock and monitoring thread """
    global monitoring_active, monitor_thread
    
    if monitor_thread and monitor_thread.is_alive():
        print("[INFO] Mouse lock already active")
        return
    
    # Apply restriction initially
    lock_mouse_to_monitor()
    
    # Start monitoring in a thread
    monitoring_active = True
    monitor_thread = threading.Thread(target=check_mouse_position, daemon=True)
    monitor_thread.start()
    print("[INFO] Mouse lock monitoring started")

def stop_mouse_lock():
    """ Stops the mouse lock and monitoring thread """
    global monitoring_active, monitor_thread
    
    # Signal the thread to stop
    monitoring_active = False
    
    # Wait for the thread to terminate
    if monitor_thread and monitor_thread.is_alive():
        monitor_thread.join(timeout=1.0)
        
    # Release the mouse lock
    release_mouse_lock()
    print("[INFO] Mouse lock monitoring stopped")

# This block only runs when the script is executed directly, not when imported
if __name__ == "__main__":
    try:
        start_mouse_lock()
        print("[INFO] Press Ctrl+C to exit and release mouse lock")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_mouse_lock()
        print("[INFO] Mouse lock script terminated by user")
