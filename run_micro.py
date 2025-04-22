#!/usr/bin/env python
import os
import subprocess
import sys
import time
import webbrowser
import socket
import platform
import signal

# Django settings
HOST = "127.0.0.1"
PORT = 8000
DJANGO_URL = f"http://{HOST}:{PORT}"

# Caddy settings
# Update these paths to wherever your caddy.exe and Caddyfile actually live
CADDY_EXE = r"G:\My Drive\micro\caddy.exe"
CADDYFILE  = r"G:\My Drive\micro\caddyfile"

# The URL you want to open in kiosk mode (must match your Caddyfile site label)
PROXY_URL = "http://micro.film"

# Path to your Django manage.py
MANAGE_PY = r"G:\My Drive\micro\micro\manage.py"


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


def run_django():
    """Start Django's development server in a subprocess."""
    if not is_port_available(PORT):
        print(f"Port {PORT} is already in use. Stop any running Django servers and retry.")
        sys.exit(1)

    # Use explicit manage.py path
    if not os.path.exists(MANAGE_PY):
        print(f"Could not find manage.py at {MANAGE_PY}")
        sys.exit(1)

    print(f"Starting Django server at {DJANGO_URL} …")
    p = subprocess.Popen(
        [sys.executable, MANAGE_PY, "runserver", f"{HOST}:{PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if not wait_for_server(DJANGO_URL):
        print("Timed out waiting for Django.")
        p.terminate()
        sys.exit(1)

    print("Django server is up.")
    return p


def run_caddy():
    """Start Caddy using your Caddyfile."""
    if not os.path.exists(CADDY_EXE):
        print(f"Could not find Caddy executable at {CADDY_EXE}")
        sys.exit(1)
    if not os.path.exists(CADDYFILE):
        print(f"Could not find Caddyfile at {CADDYFILE}")
        sys.exit(1)

    cmd = [
        CADDY_EXE, "run",
        "--config", CADDYFILE
    ]
    print("Starting Caddy reverse proxy …")
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # NOTE: You might want to poll its stdout/err to ensure it started correctly.
    time.sleep(1)
    print("Caddy is up (hopefully).")
    return p


def open_chrome_kiosk(url):
    """Open Chrome/Chromium in kiosk mode pointing to `url`."""
    chrome = get_chrome_path()
    if not chrome:
        print("Could not find Chrome. Please install it or adjust get_chrome_path().")
        return False

    print(f"Opening Chrome kiosk at {url} …")
    if platform.system() == "Windows":
        args = [chrome, "--kiosk", "--app=" + url, "--start-fullscreen"]
    else:
        args = [chrome, "--kiosk", url]

    subprocess.Popen(args)
    return True


if __name__ == "__main__":
    django_proc = run_django()
    caddy_proc  = run_caddy()

    # Clean‐up handler for both processes
    def handle_exit(sig, frame):
        print("\nShutting down services …")
        for p in (django_proc, caddy_proc):
            try:
                p.terminate()
            except:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    if not open_chrome_kiosk(PROXY_URL):
        print("Failed to open Chrome. Exiting …")
        handle_exit(None, None)

    print("Everything is up. Press Ctrl+C to quit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)