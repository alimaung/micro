#!/usr/bin/env python3
"""
Simple System Tray Example
A basic test to ensure pystray works correctly
"""

import sys
import os
import subprocess
from pathlib import Path

# Try to import pystray, install if not available
try:
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pystray", "pillow"])
    import pystray
    from pystray import MenuItem as item, Menu
    from PIL import Image, ImageDraw


def create_default_icon():
    """Create a default icon"""
    width = 64
    height = 64
    color = 'blue'
    
    image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a simple icon
    dc.ellipse([width//4, height//4, 3*width//4, 3*height//4], fill=color)
    dc.text((width//2-10, height//2-10), "ST", fill='white')
    
    return image


def show_message(icon, item):
    """Show a simple message"""
    print("Menu item clicked!")


def quit_app(icon, item):
    """Quit the application"""
    print("Exiting...")
    icon.stop()


def main():
    """Main function"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    icon_path = script_dir / "app-logo.ico"
    
    # Try to load the icon file, create a default one if not found
    if icon_path.exists():
        try:
            icon_image = Image.open(icon_path)
            print(f"Loaded icon: {icon_path}")
        except Exception as e:
            print(f"Error loading icon: {e}")
            icon_image = create_default_icon()
    else:
        print("Icon file not found, using default")
        icon_image = create_default_icon()
    
    # Create a simple menu
    menu = Menu(
        item("Show Message", show_message),
        Menu.SEPARATOR,
        item("Exit", quit_app)
    )
    
    # Create the system tray icon
    icon = pystray.Icon(
        "SimpleTest",
        icon_image,
        "Simple System Tray Test",
        menu
    )
    
    print("Starting simple system tray application...")
    print("Right-click the system tray icon to see the menu")
    
    try:
        # Run the icon
        icon.run()
    except Exception as e:
        print(f"Error running icon: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
