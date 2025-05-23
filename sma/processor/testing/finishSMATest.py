import time
import tkinter as tk
import threading
import sys
import os
import subprocess

# Try to import required modules with fallbacks
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("Warning: pyautogui not available. Mouse control will be simulated.")
    PYAUTOGUI_AVAILABLE = False

try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    print("Warning: screeninfo not available. Using fallback monitor detection.")
    SCREENINFO_AVAILABLE = False

try:
    import win32api
    import win32con
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    print("Warning: win32api not available. Some features may be limited.")
    WIN32_AVAILABLE = False

class RedOverlay:
    """Creates a transparent red overlay on the specified monitor."""
    
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
        self.fade_out_duration = 10.0  # 10 seconds to fade to 0%
        self.remaining_frames = 0
        self.phase = "fade_in"  # "fade_in", "stable", "fade_out"
        self.fade_out_start_time = None
        
    def show(self, remaining_frames=0):
        """Show the red overlay and start opacity animation."""
        if not self.is_visible:
            try:
                self.remaining_frames = remaining_frames
                self.start_time = time.time()
                self.phase = "fade_in"
                
                self.root = tk.Tk()
                self.root.overrideredirect(True)  # Remove window decorations
                self.root.attributes('-topmost', True)  # Always on top
                self.root.configure(bg='red')
                
                # Set window to cover the entire left monitor
                geometry = f"{self.monitor_info['width']}x{self.monitor_info['height']}+{self.monitor_info['x']}+{self.monitor_info['y']}"
                self.root.geometry(geometry)
                
                # Try to make window click-through (may not work on all systems)
                try:
                    self.root.wm_attributes('-transparentcolor', 'white')
                except:
                    pass
                
                # Warning text at the top - yellow, bold
                self.warning_label = tk.Label(
                    self.root, 
                    text="⚠️ SMA PROCESS FINISHING ⚠️\nPREPARE TO RELEASE MOUSE CONTROL\nSTAY READY FOR COMPLETION", 
                    bg='red', 
                    fg='yellow', 
                    font=('Arial', 28, 'bold'),
                    justify='center'
                )
                self.warning_label.place(relx=0.5, rely=0.15, anchor='center')
                
                # Frame count display - center, yellow, bold, huge
                self.frame_label = tk.Label(
                    self.root,
                    text=f"{remaining_frames}",
                    bg='red',
                    fg='yellow',
                    font=('Arial', 320, 'bold'),
                    justify='center'
                )
                self.frame_label.place(relx=0.5, rely=0.5, anchor='center')
                
                self.is_visible = True
                print(f"✓ Red overlay created on monitor 2 at {self.monitor_info['x']}, {self.monitor_info['y']}")
                
                # Start with 0% opacity
                self.root.attributes('-alpha', 0.0)
                self.current_opacity = 0.0
                
                # Force initial update
                self.root.update()
                
            except Exception as e:
                print(f"Error showing red overlay: {e}")
                import traceback
                traceback.print_exc()
    
    def update_opacity_smooth(self):
        """Update opacity smoothly based on current phase."""
        if not self.start_time or not self.root or not self.is_visible:
            return
            
        try:
            current_time = time.time()
            
            if self.phase == "fade_in":
                elapsed_time = current_time - self.start_time
                
                if elapsed_time >= self.fade_in_duration:
                    opacity = self.target_opacity  # Cap at 75%
                    self.phase = "stable"
                    print(f"✓ Overlay reached maximum opacity: {int(opacity * 100)}%")
                else:
                    progress = elapsed_time / self.fade_in_duration
                    opacity = progress * self.target_opacity
                    
            elif self.phase == "fade_out":
                if not self.fade_out_start_time:
                    self.fade_out_start_time = current_time
                    
                elapsed_fade_out = current_time - self.fade_out_start_time
                
                if elapsed_fade_out >= self.fade_out_duration:
                    opacity = 0.0
                else:
                    progress = elapsed_fade_out / self.fade_out_duration
                    opacity = self.target_opacity * (1.0 - progress)  # 75% → 0%
                    
            else:  # stable phase
                opacity = self.target_opacity
                
            # Update opacity if significantly changed
            if abs(opacity - self.current_opacity) > 0.01:  # Update every 1%
                self.current_opacity = opacity
                self.root.attributes('-alpha', self.current_opacity)
                
        except Exception as e:
            print(f"Error updating opacity: {e}")
    
    def start_fade_out(self):
        """Start the fade-out phase."""
        if self.phase != "fade_out":
            self.phase = "fade_out"
            self.fade_out_start_time = time.time()
            print("✓ Starting overlay fade-out (75% → 0% over 10 seconds)")
                
    def update_frame_count(self, remaining_frames):
        """Update the frame count display."""
        if self.frame_label and self.is_visible:
            try:
                self.remaining_frames = remaining_frames
                self.frame_label.config(text=f"{remaining_frames}")
            except Exception as e:
                print(f"Error updating frame count: {e}")
                
    def ensure_topmost(self):
        """Ensure overlay stays on top."""
        if self.root and self.is_visible:
            try:
                self.root.attributes('-topmost', True)
                self.root.lift()
            except Exception as e:
                print(f"Error ensuring topmost: {e}")
                
    def hide(self):
        """Hide the red overlay."""
        if self.root and self.is_visible:
            try:
                self.root.destroy()
                self.root = None
                self.warning_label = None
                self.frame_label = None
                self.is_visible = False
                print("✓ Red overlay hidden")
            except Exception as e:
                print(f"Error hiding red overlay: {e}")
            
    def update(self, remaining_frames=None):
        """Update the overlay (call this in main loop)."""
        if self.is_visible and self.root:
            try:
                # Update opacity animation
                self.update_opacity_smooth()
                
                # Update frame count
                if remaining_frames is not None:
                    self.update_frame_count(remaining_frames)
                
                # Update the GUI
                self.root.update()
                
            except Exception as e:
                print(f"Error updating overlay: {e}")

class MouseLocker:
    """Locks mouse to a specific position on screen."""
    
    def __init__(self):
        self.is_locked = False
        self.lock_thread = None
        self.should_stop = False
        self.lock_position = None
        
    def lock_to_position(self, x, y):
        """Lock mouse to specific coordinates."""
        if self.is_locked:
            return
            
        self.lock_position = (x, y)
        self.is_locked = True
        self.should_stop = False
        
        if PYAUTOGUI_AVAILABLE:
            # Move mouse to position immediately
            pyautogui.moveTo(x, y)
            
            # Start locking thread
            self.lock_thread = threading.Thread(target=self._lock_loop, daemon=True)
            self.lock_thread.start()
            
            print(f"✓ Mouse locked to position {x}, {y}")
        else:
            print(f"✓ Mouse lock simulated at position {x}, {y}")
        
    def release(self):
        """Release mouse lock."""
        if not self.is_locked:
            return
            
        self.should_stop = True
        self.is_locked = False
        
        if self.lock_thread and PYAUTOGUI_AVAILABLE:
            self.lock_thread.join(timeout=1)
            
        print("✓ Mouse lock released")
        
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

class SMAController:
    """Controls the SMA application."""
    
    def __init__(self):
        self.sma_process = None
        self.sma_window = None
        self.sma_path = r"Y:\SMA\file-converter-64\file-sma.exe"
        
    def start_sma(self):
        """Start the SMA application."""
        try:
            if os.path.exists(self.sma_path):
                print(f"🚀 Starting SMA application: {self.sma_path}")
                self.sma_process = subprocess.Popen([self.sma_path])
                
                # Wait a moment for the application to start
                time.sleep(3)
                
                # Try to find the SMA window
                if WIN32_AVAILABLE:
                    self._find_sma_window()
                
                print("✓ SMA application started")
                return True
            else:
                print(f"❌ SMA executable not found at: {self.sma_path}")
                return False
        except Exception as e:
            print(f"Error starting SMA application: {e}")
            return False
    
    def _find_sma_window(self):
        """Find the SMA application window."""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if "SMA 51" in window_text or "file-sma" in window_text.lower():
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                self.sma_window = windows[0]
                window_text = win32gui.GetWindowText(self.sma_window)
                print(f"✓ Found SMA window: {window_text}")
            else:
                print("⚠️ Could not find SMA window")
                
        except Exception as e:
            print(f"Error finding SMA window: {e}")
    
    def show_sma(self):
        """Show the SMA application window."""
        try:
            if self.sma_window and WIN32_AVAILABLE:
                # Try multiple methods to bring window to foreground
                try:
                    # Method 1: Standard approach
                    win32gui.ShowWindow(self.sma_window, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.sma_window)
                    print("✓ SMA application brought to foreground (method 1)")
                    return True
                except Exception as e1:
                    print(f"Method 1 failed: {e1}")
                    
                    # Method 2: Alternative approach
                    try:
                        # Get current foreground window
                        current_fg = win32gui.GetForegroundWindow()
                        current_thread = win32process.GetWindowThreadProcessId(current_fg)[0]
                        target_thread = win32process.GetWindowThreadProcessId(self.sma_window)[0]
                        
                        # Attach input to target window's thread
                        if current_thread != target_thread:
                            win32process.AttachThreadInput(current_thread, target_thread, True)
                        
                        # Now try to set foreground
                        win32gui.ShowWindow(self.sma_window, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(self.sma_window)
                        win32gui.BringWindowToTop(self.sma_window)
                        
                        # Detach input
                        if current_thread != target_thread:
                            win32process.AttachThreadInput(current_thread, target_thread, False)
                        
                        print("✓ SMA application brought to foreground (method 2)")
                        return True
                        
                    except Exception as e2:
                        print(f"Method 2 failed: {e2}")
                        
                        # Method 3: Simple show and activate
                        try:
                            win32gui.ShowWindow(self.sma_window, win32con.SW_SHOW)
                            win32gui.SetActiveWindow(self.sma_window)
                            print("✓ SMA application activated (method 3)")
                            return True
                        except Exception as e3:
                            print(f"Method 3 failed: {e3}")
                            print("✓ SMA foreground - all methods failed, but window should be visible")
                            return False
            else:
                print("✓ SMA foreground simulation (window not found or WIN32 not available)")
                return False
        except Exception as e:
            print(f"Error showing SMA window: {e}")
            return False
    
    def cleanup(self):
        """Clean up SMA process."""
        try:
            if self.sma_process:
                self.sma_process.terminate()
                print("✓ SMA application terminated")
        except Exception as e:
            print(f"Error terminating SMA application: {e}")

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
    if not monitors:
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        
        # Assume dual monitor setup with left monitor
        monitors = [
            {'id': 1, 'x': 0, 'y': 0, 'width': width, 'height': height},
            {'id': 2, 'x': -width, 'y': 0, 'width': width, 'height': height}  # Left monitor
        ]
    
    return monitors

def get_left_monitor():
    """Get information about the left monitor (monitor 2)."""
    monitors = get_monitor_info()
    
    print(f"Found {len(monitors)} monitors:")
    for monitor in monitors:
        print(f"  Monitor {monitor['id']}: {monitor['width']}x{monitor['height']} at ({monitor['x']}, {monitor['y']})")
    
    if len(monitors) >= 2:
        # Find the leftmost monitor (most negative x coordinate)
        left_monitor = min(monitors, key=lambda m: m['x'])
        print(f"Using monitor at {left_monitor['x']}, {left_monitor['y']} as left monitor")
        return left_monitor
    else:
        print("Only one monitor found, using primary monitor for test")
        return monitors[0]

def get_monitor_center(monitor_info):
    """Get the center point of a specific monitor."""
    center_x = monitor_info['x'] + (monitor_info['width'] // 2)
    center_y = monitor_info['y'] + (monitor_info['height'] // 2)
    print(f"Monitor 2 center calculated at {center_x}, {center_y}")
    return center_x, center_y

def simulate_sma_finish():
    """Simulate the final stages of SMA processing."""
    print("=" * 60)
    print("🎬 SMA FINISH TEST SIMULATION")
    print("=" * 60)
    print("This will simulate the last 30 frames of SMA processing")
    print()
    print("Behavior:")
    print("• 30 frames remaining: Start file-sma.exe")
    print("• 20 frames remaining: Red warning overlay starts (0% → 75% over 5 seconds)")
    print("• 10 frames remaining: Mouse locks to monitor 2 center")
    print("•  7 frames remaining: Mouse lock released")
    print("•  5 frames remaining: Overlay hidden, SMA brought to foreground")
    print("•  0 frames remaining: Process complete")
    print()
    print("Press Ctrl+C to stop the test at any time")
    print("=" * 60)
    
    # Get monitor information
    left_monitor = get_left_monitor()
    monitor2_center = get_monitor_center(left_monitor)
    
    # Initialize components
    overlay = RedOverlay(left_monitor)
    mouse_locker = MouseLocker()
    sma_controller = SMAController()
    
    # State tracking
    overlay_active = False
    mouse_locked = False
    app_brought_to_front = False
    sma_started = False
    
    try:
        print("\n🚀 Starting simulation...")
        time.sleep(2)  # Give user time to read
        
        # Simulate countdown from 30 to 0
        for remaining_frames in range(30, -1, -1):
            print(f"\n📊 Frames remaining: {remaining_frames}")
            
            # At 30 frames: Start SMA application
            if remaining_frames == 30 and not sma_started:
                print("🚀 TRIGGER: Starting SMA application")
                sma_controller.start_sma()
                sma_started = True
                
            # At 20 frames: Start red overlay with time-based opacity animation
            elif remaining_frames == 20 and not overlay_active:
                print("🔴 TRIGGER: Starting red warning overlay (0% → 75% over 5 seconds)")
                overlay.show(remaining_frames=remaining_frames)
                overlay_active = True
                
            # At 10 frames: Lock mouse to monitor 2 center
            elif remaining_frames == 10 and not mouse_locked:
                print("🖱️  TRIGGER: Locking mouse to monitor 2 center")
                mouse_locker.lock_to_position(monitor2_center[0], monitor2_center[1])
                mouse_locked = True
                
            # At 7 frames: Release mouse lock (couple frames before foreground)
            elif remaining_frames == 7 and mouse_locked:
                print("🖱️  TRIGGER: Releasing mouse lock (preparing for foreground)")
                mouse_locker.release()
                mouse_locked = False
                
            # At 5 frames: Hide overlay completely, then bring app to foreground
            elif remaining_frames == 5 and not app_brought_to_front:
                print("🖥️  TRIGGER: Hiding overlay and bringing SMA to foreground")
                
                # Hide overlay completely first
                if overlay_active:
                    overlay.hide()
                    overlay_active = False
                    print("✓ Overlay completely hidden")
                
                # Then bring SMA to foreground
                sma_brought_to_front = sma_controller.show_sma()
                app_brought_to_front = True
                
            # At 0 frames: Process complete
            elif remaining_frames == 0:
                print("🎉 TRIGGER: Process complete!")
                print("\n✅ SMA processing simulation completed successfully!")
            
            # Update overlay if it's active
            if overlay_active:
                overlay.update(remaining_frames=remaining_frames)
            
            # Wait 1 second to simulate processing time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        if overlay_active:
            overlay.hide()
        if mouse_locked:
            mouse_locker.release()
        sma_controller.cleanup()
        print("✅ Test completed and cleaned up")

def main():
    """Main function."""
    try:
        simulate_sma_finish()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
