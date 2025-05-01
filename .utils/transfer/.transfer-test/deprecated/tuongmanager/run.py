#!/usr/bin/env python
"""
Barcode File Manager
Run script to start the application
"""

import os
import webbrowser
import signal
import sys
from threading import Timer
from app import app

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://127.0.0.1:5000/')

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to shutdown server gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

if __name__ == '__main__':
    print("Starting Barcode File Manager...")
    print("The web interface will open automatically in your default browser.")
    print("Press Ctrl+C to exit.")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Open browser after 1.5 seconds to allow Flask to start
    Timer(1.5, open_browser).start()
    
    # Run Flask app
    try:
        app.run(debug=False)  # Change to False for production
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0) 