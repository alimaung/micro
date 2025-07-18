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

# Define Monitor boundaries - only restrict right side to prevent going to other monitor
RIGHT_MARGIN = 20  # Safety margin to prevent accidental movement to right monitor
MONITOR_BOUNDS = RECT(0, 0, 1920 - RIGHT_MARGIN, 1080)  # Only right side has margin

# Global variable to control the monitoring thread
monitoring_active = False
monitor_thread = None

def lock_mouse_to_monitor():
    """ Restricts the mouse to prevent movement to right monitor only """
    user32.ClipCursor(ctypes.byref(MONITOR_BOUNDS))
    print(f"[INFO] Mouse locked to left monitor area: {MONITOR_BOUNDS.left}-{MONITOR_BOUNDS.right}, {MONITOR_BOUNDS.top}-{MONITOR_BOUNDS.bottom}")

def release_mouse_lock():
    """ Releases the mouse restriction """
    # Passing NULL pointer to ClipCursor removes any restriction
    user32.ClipCursor(None)
    print("[INFO] Mouse lock released")

def check_mouse_position():
    """ Monitors if the mouse tries to go to right monitor and brings it back """
    global monitoring_active
    while monitoring_active:
        x, y = pyautogui.position()

        # Only check if mouse goes too far right (to other monitor)
        if x > MONITOR_BOUNDS.right:
            print(f"[WARNING] Mouse tried to go to right monitor! ({x}, {y}) - Bringing it back.")
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
