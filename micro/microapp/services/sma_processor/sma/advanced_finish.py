"""
Advanced Finish Warning System for SMA (film scanning) automation.

This module provides sophisticated end-of-process warnings including:
- Red overlay warnings on specific monitors
- Mouse locking during critical phases
- Time-based opacity animations
- Multi-monitor support with fallback detection
"""

import time
import threading
from .sma_exceptions import SMAAdvancedFinishError, SMADependencyError

# Advanced finish features imports with availability tracking
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    print("Warning: tkinter not available. Red overlay will be disabled.")
    TKINTER_AVAILABLE = False

try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    print("Warning: screeninfo not available. Using fallback monitor detection.")
    SCREENINFO_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("Warning: pyautogui not available. Mouse control will be simulated.")
    PYAUTOGUI_AVAILABLE = False

class RedOverlay:
    """Creates a transparent red overlay on the specified monitor for finish warnings."""
    
    def __init__(self, monitor_info):
        self.monitor_info = monitor_info
        self.root = None
        self.is_visible = False
        self.current_opacity = 0.0
        self.warning_label = None
        self.frame_label = None
        self.start_time = None
        self.target_opacity = 0.75  # 75%
        self.fade_in_duration = 5.0  # 5 seconds to reach 75%
        
        # Threading support
        self.overlay_thread = None
        self.should_stop = False
        self.remaining_frames = 0
        self.thread_ready = False
        
    def show(self, remaining_frames=0):
        """Show the red overlay in a separate thread."""
        if not self.is_visible and TKINTER_AVAILABLE:
            try:
                self.remaining_frames = remaining_frames
                self.should_stop = False
                self.thread_ready = False
                
                # Start the overlay in its own thread
                self.overlay_thread = threading.Thread(target=self._run_overlay, daemon=True)
                self.overlay_thread.start()
                
                # Wait for thread to be ready (with timeout)
                timeout = 5.0
                start_wait = time.time()
                while not self.thread_ready and (time.time() - start_wait) < timeout:
                    time.sleep(0.1)
                
                if self.thread_ready:
                    self.is_visible = True
                    
            except Exception as e:
                raise SMAAdvancedFinishError(
                    feature="red_overlay",
                    message=f"Error showing red overlay: {str(e)}"
                )
    
    def _run_overlay(self):
        """Run the overlay in its own thread with its own mainloop."""
        try:
            # Create root in this thread
            self.root = tk.Tk()
            
            # Configure window
            self.root.overrideredirect(True)
            self.root.attributes('-topmost', True)
            self.root.configure(bg='red')
            
            # Set window to cover the entire monitor
            geometry = f"{self.monitor_info['width']}x{self.monitor_info['height']}+{self.monitor_info['x']}+{self.monitor_info['y']}"
            self.root.geometry(geometry)
            
            # Create labels
            self.warning_label = tk.Label(
                self.root, 
                text="⚠️ SMA PROCESS FINISHING ⚠️\nPREPARE TO RELEASE MOUSE CONTROL\nSTAY READY FOR COMPLETION", 
                bg='red', 
                fg='yellow', 
                font=('Arial', 28, 'bold'),
                justify='center'
            )
            self.warning_label.place(relx=0.5, rely=0.15, anchor='center')
            
            self.frame_label = tk.Label(
                self.root,
                text=f"{self.remaining_frames}",
                bg='red',
                fg='yellow',
                font=('Arial', 320, 'bold'),
                justify='center'
            )
            self.frame_label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Set initial state
            self.root.attributes('-alpha', 0.0)
            self.current_opacity = 0.0
            self.start_time = time.time()
            
            # Signal that thread is ready
            self.thread_ready = True
            
            # Schedule periodic updates
            self.root.after(50, self._update_in_thread)  # Update every 50ms
            
            # Start the mainloop (this will block until window is destroyed)
            self.root.mainloop()
            
        except Exception as e:
            print(f"Exception in _run_overlay(): {e}")
    
    def _update_in_thread(self):
        """Update the overlay from within its own thread."""
        try:
            if self.should_stop:
                self.root.quit()
                return
            
            # Update opacity
            if self.start_time:
                elapsed_time = time.time() - self.start_time
                
                if elapsed_time >= self.fade_in_duration:
                    opacity = self.target_opacity
                else:
                    progress = elapsed_time / self.fade_in_duration
                    opacity = progress * self.target_opacity
                    
                if abs(opacity - self.current_opacity) > 0.01:
                    self.current_opacity = opacity
                    self.root.attributes('-alpha', self.current_opacity)
            
            # Update frame count
            if self.frame_label:
                self.frame_label.config(text=f"{self.remaining_frames}")
            
            # Schedule next update
            self.root.after(50, self._update_in_thread)
            
        except Exception as e:
            print(f"Exception in _update_in_thread(): {e}")
    
    def update_opacity_smooth(self):
        """Update opacity smoothly based on elapsed time."""
        # This method is no longer used in the threaded version
        pass
                
    def update_frame_count(self, remaining_frames):
        """Update the frame count from the main thread."""
        self.remaining_frames = remaining_frames
        # The actual update happens in _update_in_thread()
                
    def hide(self):
        """Hide the red overlay."""
        if self.is_visible:
            try:
                self.should_stop = True
                self.is_visible = False
                
                # Wait for thread to finish (with timeout)
                if self.overlay_thread and self.overlay_thread.is_alive():
                    self.overlay_thread.join(timeout=2.0)
                
                # Clean up references
                self.root = None
                self.warning_label = None
                self.frame_label = None
                
            except Exception as e:
                raise SMAAdvancedFinishError(
                    feature="red_overlay_hide",
                    message=f"Error hiding red overlay: {str(e)}"
                )
            
    def update(self, remaining_frames=None):
        """Update the overlay (call this from main thread)."""
        if self.is_visible and remaining_frames is not None:
            self.update_frame_count(remaining_frames)
        # This is now non-blocking since the actual updates happen in the overlay thread

class MouseLocker:
    """Locks mouse to a specific position on screen."""
    
    def __init__(self):
        self.is_locked = False
        self.lock_thread = None
        self.should_stop = False
        self.lock_position = None
        
    def lock_to_position(self, x, y):
        """Lock mouse to specific coordinates."""
        if self.is_locked or not PYAUTOGUI_AVAILABLE:
            return
            
        self.lock_position = (x, y)
        self.is_locked = True
        self.should_stop = False
        
        try:
            pyautogui.moveTo(x, y)
            self.lock_thread = threading.Thread(target=self._lock_loop, daemon=True)
            self.lock_thread.start()
        except Exception as e:
            raise SMAAdvancedFinishError(
                feature="mouse_lock",
                message=f"Error locking mouse: {str(e)}"
            )
        
    def release(self):
        """Release mouse lock."""
        if not self.is_locked:
            return
            
        try:
            self.should_stop = True
            self.is_locked = False
            
            if self.lock_thread and PYAUTOGUI_AVAILABLE:
                self.lock_thread.join(timeout=1)
        except Exception as e:
            raise SMAAdvancedFinishError(
                feature="mouse_release",
                message=f"Error releasing mouse lock: {str(e)}"
            )
        
    def _lock_loop(self):
        """Internal loop that keeps mouse locked to position."""
        while not self.should_stop and self.is_locked:
            try:
                if PYAUTOGUI_AVAILABLE:
                    current_pos = pyautogui.position()
                    if abs(current_pos.x - self.lock_position[0]) > 5 or abs(current_pos.y - self.lock_position[1]) > 5:
                        pyautogui.moveTo(self.lock_position[0], self.lock_position[1])
                time.sleep(0.05)  # Check every 50ms
            except Exception as e:
                print(f"Error in mouse lock loop: {e}")
                break

def get_monitor_info():
    """Get information about available monitors."""
    monitors = []
    
    if SCREENINFO_AVAILABLE:
        try:
            screen_monitors = get_monitors()
            for i, monitor in enumerate(screen_monitors):
                monitors.append({
                    'id': i + 1,
                    'x': monitor.x,
                    'y': monitor.y,
                    'width': monitor.width,
                    'height': monitor.height
                })
        except Exception as e:
            print(f"Error getting monitor info with screeninfo: {e}")
    
    # Fallback: Use tkinter to get primary monitor info
    if not monitors and TKINTER_AVAILABLE:
        try:
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            
            # Assume dual monitor setup with left monitor
            monitors = [
                {'id': 1, 'x': 0, 'y': 0, 'width': width, 'height': height},
                {'id': 2, 'x': -width, 'y': 0, 'width': width, 'height': height}  # Left monitor
            ]
        except Exception as e:
            print(f"Error with tkinter fallback: {e}")
    
    return monitors

def get_left_monitor():
    """Get information about the left monitor (monitor 2)."""
    try:
        monitors = get_monitor_info()
        
        if len(monitors) >= 2:
            # Find the leftmost monitor (most negative x coordinate)
            left_monitor = min(monitors, key=lambda m: m['x'])
            return left_monitor
        elif len(monitors) == 1:
            return monitors[0]
        else:
            return None
    except Exception as e:
        raise SMAAdvancedFinishError(
            feature="monitor_detection",
            message=f"Error getting left monitor: {str(e)}"
        )

def get_monitor_center(monitor_info):
    """Get the center point of a specific monitor."""
    try:
        if monitor_info:
            center_x = monitor_info['x'] + (monitor_info['width'] // 2)
            center_y = monitor_info['y'] + (monitor_info['height'] // 2)
            return center_x, center_y
        return None, None
    except Exception as e:
        raise SMAAdvancedFinishError(
            feature="monitor_center_calculation",
            message=f"Error calculating monitor center: {str(e)}"
        )

def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    if not TKINTER_AVAILABLE:
        missing_deps.append("tkinter")
    if not SCREENINFO_AVAILABLE:
        missing_deps.append("screeninfo")
    if not PYAUTOGUI_AVAILABLE:
        missing_deps.append("pyautogui")
    
    return missing_deps

def get_availability_status():
    """Get the availability status of all advanced finish features."""
    return {
        'tkinter': TKINTER_AVAILABLE,
        'screeninfo': SCREENINFO_AVAILABLE,
        'pyautogui': PYAUTOGUI_AVAILABLE,
        'red_overlay': TKINTER_AVAILABLE,
        'mouse_lock': PYAUTOGUI_AVAILABLE,
        'monitor_detection': SCREENINFO_AVAILABLE or TKINTER_AVAILABLE
    }

class AdvancedFinishManager:
    """Manages all advanced finish warning components."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.left_monitor = None
        self.monitor_center = None
        self.overlay = None
        self.mouse_locker = None
        self.overlay_active = False
        self.mouse_locked = False
        self.foreground_brought = False
        self.overlay_finished = False  # Flag to prevent restarting overlay after it's been hidden
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize advanced finish components."""
        try:
            # Get monitor information
            self.left_monitor = get_left_monitor()
            if self.left_monitor:
                self.monitor_center = get_monitor_center(self.left_monitor)
                if self.logger:
                    self.logger.info(f"Left monitor detected: {self.left_monitor}")
                    self.logger.info(f"Monitor center: {self.monitor_center}")
            else:
                if self.logger:
                    self.logger.warning("No left monitor detected")
            
            # Initialize overlay
            if self.left_monitor:
                self.overlay = RedOverlay(self.left_monitor)
            
            # Initialize mouse locker
            self.mouse_locker = MouseLocker()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error initializing advanced finish components: {e}")
    
    def handle_frame_countdown(self, remaining_frames, film_window=None):
        """Handle the countdown based on remaining frames."""
        try:
            # At 20 frames: Start red overlay (only if not already finished)
            if remaining_frames <= 20 and not self.overlay_active and not self.overlay_finished and self.overlay:
                if self.logger:
                    self.logger.info(f"[RED] {remaining_frames} frames remaining - starting red warning overlay")
                self.overlay.show(remaining_frames=remaining_frames)
                self.overlay_active = True
            
            # At 10 frames: Lock mouse to monitor 2 center
            if remaining_frames <= 10 and remaining_frames > 7 and not self.mouse_locked and self.monitor_center[0] is not None:
                if self.logger:
                    self.logger.info(f"[MOUSE] {remaining_frames} frames remaining - locking mouse to monitor 2 center")
                self.mouse_locker.lock_to_position(self.monitor_center[0], self.monitor_center[1])
                self.mouse_locked = True
            
            # At 7 frames: Release mouse lock
            if remaining_frames <= 7 and remaining_frames > 5 and self.mouse_locked:
                if self.logger:
                    self.logger.info(f"[MOUSE] {remaining_frames} frames remaining - releasing mouse lock")
                self.mouse_locker.release()
                self.mouse_locked = False
            
            # At exactly 5 frames: Hide overlay and bring SMA to foreground (only once)
            if remaining_frames == 5 and not self.foreground_brought:
                if self.logger:
                    self.logger.info(f"[DISPLAY] {remaining_frames} frames remaining - hiding overlay and bringing SMA to foreground")
                
                # Hide overlay completely first
                if self.overlay_active and self.overlay:
                    self.overlay.hide()
                    self.overlay_active = False
                    self.overlay_finished = True  # Mark overlay as finished to prevent restart
                    if self.logger:
                        self.logger.info("[OK] Overlay completely hidden")
                
                # Then bring SMA to foreground
                if film_window:
                    try:
                        film_window.set_focus()
                        film_window.restore()  # In case it's minimized
                        film_window.bring_to_top()  # Bring to top of Z-order
                        self.foreground_brought = True
                        if self.logger:
                            self.logger.info("[OK] SMA application brought to foreground")
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Could not fully bring window to front: {e}")
            
            # Update overlay if it's active (only if overlay hasn't been hidden)
            if self.overlay_active and self.overlay and remaining_frames > 5:
                self.overlay.update(remaining_frames=remaining_frames)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in frame countdown handling: {e}")
    
    def cleanup(self):
        """Clean up all advanced finish components."""
        try:
            if self.overlay_active and self.overlay:
                self.overlay.hide()
                if self.logger:
                    self.logger.info("[OK] Cleaned up overlay")
            
            if self.mouse_locked and self.mouse_locker:
                self.mouse_locker.release()
                if self.logger:
                    self.logger.info("[OK] Cleaned up mouse lock")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error cleaning up advanced finish components: {e}")
    
    def reset(self):
        """Reset all advanced finish states."""
        self.overlay_active = False
        self.mouse_locked = False
        self.foreground_brought = False
        self.overlay_finished = False
    
    def get_status(self):
        """Get the current status of all components."""
        return {
            'overlay_active': self.overlay_active,
            'mouse_locked': self.mouse_locked,
            'foreground_brought': self.foreground_brought,
            'left_monitor': self.left_monitor,
            'monitor_center': self.monitor_center,
            'availability': get_availability_status()
        }

# Convenience functions for backward compatibility
def create_advanced_finish_manager(logger=None):
    """Create and return an AdvancedFinishManager instance."""
    return AdvancedFinishManager(logger=logger) 