#!/usr/bin/env python
import os
import subprocess
import sys
import time
import webbrowser
import socket
import platform
import signal
import threading
import re
from datetime import datetime

# Django settings
HOST = "127.0.0.1"
PORT = 8000
DJANGO_URL = f"http://{HOST}:{PORT}"

# The URL you want to open in kiosk mode (must match your Caddyfile site label)
PROXY_URL = "https://micro.film"

# Get the /micro/launch directory (where run_micro.pyw lives)
LAUNCH_DIR = os.path.abspath(os.path.dirname(__file__))

# /micro/micro/manage.py is one level up + into micro/
MANAGE_PY = os.path.join(LAUNCH_DIR, "..", "micro", "manage.py")
# caddy.exe and caddyfile are in the same directory as run_micro.pyw
CADDY_EXE = os.path.join(LAUNCH_DIR, "caddy.exe")
CADDYFILE = os.path.join(LAUNCH_DIR, "caddyfile")

# Colors and formatting
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# Configure colors based on Windows or other platform
def init_colors():
    if platform.system() == "Windows":
        # Enable ANSI colors on Windows
        os.system("")

def timestamp():
    """Return formatted current time"""
    return datetime.now().strftime("%H:%M:%S")

def print_header(text, color=Colors.CYAN):
    """Print a section header"""
    print(f"\n{color}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{color}{Colors.BOLD} {text} {Colors.RESET}")
    print(f"{color}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

def print_status(text, color=Colors.GREEN):
    """Print a status message"""
    print(f"{color}[{timestamp()}] {text}{Colors.RESET}")

def get_chrome_path():
    """Locate the Chrome/Chromium binary."""
    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def is_port_available(port):
    """Check if a port is available for use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_server(url, timeout=60):
    """Wait until the given URL responds (or timeout)."""
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False

def stream_output(process, prefix, color):
    """Stream output from a process to the console with formatting"""
    def read_stream(stream):
        for line in iter(stream.readline, ''):
            if line:
                formatted_line = f"{color}[{timestamp()}] {prefix}: {line.rstrip()}{Colors.RESET}"
                print(formatted_line)
    
    # Start threads to read stdout and stderr
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout,))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr,))
    
    # Make them daemon threads so they exit when the main thread exits
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    
    stdout_thread.start()
    stderr_thread.start()

def run_django():
    """Start Django's development server in a subprocess."""
    if not is_port_available(PORT):
        print(f"{Colors.RED}Port {PORT} is already in use. Stop any running Django servers and retry.{Colors.RESET}")
        sys.exit(1)

    # Use explicit manage.py path
    if not os.path.exists(MANAGE_PY):
        print(f"{Colors.RED}Could not find manage.py at {MANAGE_PY}{Colors.RESET}")
        sys.exit(1)

    print_header("STARTING DJANGO SERVER", Colors.GREEN)
    print_status(f"Starting Django server at {DJANGO_URL}", Colors.GREEN)
    
    p = subprocess.Popen(
        [sys.executable, MANAGE_PY, "runserver", f"{HOST}:{PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
    )
    
    # Start streaming the output
    stream_output(p, "Django", Colors.GREEN)
    
    if not wait_for_server(DJANGO_URL):
        print_status("Timed out waiting for Django.", Colors.RED)
        p.terminate()
        sys.exit(1)

    print_status("Django server is up and running!", Colors.GREEN)
    return p

def run_caddy():
    """Start Caddy using your Caddyfile."""
    if not os.path.exists(CADDY_EXE):
        print(f"{Colors.RED}Could not find Caddy executable at {CADDY_EXE}{Colors.RESET}")
        sys.exit(1)
    if not os.path.exists(CADDYFILE):
        print(f"{Colors.RED}Could not find Caddyfile at {CADDYFILE}{Colors.RESET}")
        sys.exit(1)

    print_header("STARTING CADDY REVERSE PROXY", Colors.BLUE)
    cmd = [
        CADDY_EXE, "run",
        "--config", CADDYFILE
    ]
    
    print_status("Starting Caddy reverse proxy...", Colors.BLUE)
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
    )
    
    # Start streaming the output
    stream_output(p, "Caddy", Colors.BLUE)
    
    # Check if Caddy is running by testing the PROXY_URL
    import urllib.request
    import ssl
    
    # Create a context that doesn't verify certificates (for local testing)
    context = ssl._create_unverified_context()
    
    print_status(f"Waiting for Caddy to serve {PROXY_URL}...", Colors.BLUE)
    timeout = 30  # seconds to wait for Caddy to start
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the proxy URL
            urllib.request.urlopen(PROXY_URL, timeout=1, context=context)
            print_status("Caddy is up and running successfully!", Colors.BLUE)
            return p
        except Exception as e:
            # Check if process is still running
            if p.poll() is not None:
                print_status(f"Caddy process exited with code {p.returncode}", Colors.RED)
                stderr = p.stderr.read()
                if stderr:
                    print_status(f"Caddy error: {stderr}", Colors.RED)
                sys.exit(1)
            time.sleep(0.5)
    
    # If we get here, Caddy didn't start within the timeout period
    print_status("Timed out waiting for Caddy to start.", Colors.RED)
    p.terminate()
    sys.exit(1)

def open_chrome_kiosk(url):
    """Open Chrome/Chromium in kiosk mode pointing to `url`."""
    chrome = get_chrome_path()
    if not chrome:
        print_status("Could not find Chrome. Please install it or adjust get_chrome_path().", Colors.RED)
        return False

    print_status(f"Opening Chrome kiosk at {url}", Colors.MAGENTA)
    args = [chrome, "--kiosk", "--app=" + url, "--start-fullscreen"]

    subprocess.Popen(args)
    return True

if __name__ == "__main__":
    # Initialize colors for the terminal
    init_colors()
    
    print_header("MICRO FILM LAUNCHER", Colors.YELLOW)
    
    django_proc = run_django()
    caddy_proc = run_caddy()

    # Clean‐up handler for both processes
    def handle_exit(sig, frame):
        print_header("SHUTTING DOWN", Colors.RED)
        for name, p in [("Django", django_proc), ("Caddy", caddy_proc)]:
            try:
                print_status(f"Stopping {name}...", Colors.RED)
                p.terminate()
                print_status(f"{name} stopped", Colors.RED)
            except:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    if not open_chrome_kiosk(PROXY_URL):
        print_status("Failed to open Chrome. Exiting...", Colors.RED)
        handle_exit(None, None)

    print_header("SYSTEM STATUS", Colors.YELLOW)
    print_status("All services are running. Press Ctrl+C to quit.", Colors.YELLOW)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)