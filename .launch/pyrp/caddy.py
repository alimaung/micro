#!/usr/bin/env python
import asyncio
import ssl
import socket
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import os
import sys
from socketserver import ThreadingMixIn

# Configuration
PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8443  # Use 8443 instead of 443 to avoid requiring admin privileges
TARGET_HOST = "localhost"
TARGET_PORT = 8000
DOMAIN = "micro.film"

# Colors for logging
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"

def timestamp():
    """Return formatted current time"""
    return datetime.now().strftime("%H:%M:%S")

def log(message, color=Colors.CYAN):
    """Log a message with timestamp and color"""
    print(f"{color}[{timestamp()}] PyProxy: {message}{Colors.RESET}")

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP Server that handles requests in separate threads"""
    daemon_threads = True
    allow_reuse_address = True

class ReverseProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler that proxies requests to the target server"""
    
    def log_message(self, format, *args):
        """Override to use our custom logging"""
        log(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def do_HEAD(self):
        self.proxy_request()
    
    def do_OPTIONS(self):
        self.proxy_request()
    
    def proxy_request(self):
        """Proxy the request to the target server"""
        try:
            # Build the target URL
            target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{self.path}"
            
            # Get request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create the request
            req = urllib.request.Request(target_url, data=request_body, method=self.command)
            
            # Copy headers (excluding some that should not be forwarded)
            skip_headers = {'host', 'connection', 'upgrade', 'proxy-connection'}
            for header, value in self.headers.items():
                if header.lower() not in skip_headers:
                    req.add_header(header, value)
            
            # Add the original host header pointing to our target
            req.add_header('Host', f"{TARGET_HOST}:{TARGET_PORT}")
            
            # Make the request
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in {'connection', 'transfer-encoding'}:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    
        except urllib.error.HTTPError as e:
            # Forward HTTP errors
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<h1>Error {e.code}</h1><p>{e.reason}</p>".encode())
            
        except Exception as e:
            log(f"Proxy error: {e}", Colors.RED)
            self.send_response(502)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>502 Bad Gateway</h1><p>Proxy error occurred</p>")

def generate_self_signed_cert(cert_file, key_file, domain):
    """Generate a self-signed certificate for the given domain"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        from datetime import timedelta
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Micro Film"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        log(f"Generated self-signed certificate for {domain}", Colors.GREEN)
        return True
        
    except ImportError:
        log("cryptography library not found. Install with: pip install cryptography", Colors.RED)
        return False
    except Exception as e:
        log(f"Failed to generate certificate: {e}", Colors.RED)
        return False

def setup_ssl_context(cert_dir, domain):
    """Setup SSL context with certificate"""
    cert_file = os.path.join(cert_dir, f"{domain}.crt")
    key_file = os.path.join(cert_dir, f"{domain}.key")
    
    # Create cert directory if it doesn't exist
    os.makedirs(cert_dir, exist_ok=True)
    
    # Check if existing certificate files exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        log(f"Using existing certificate files: {cert_file} and {key_file}", Colors.GREEN)
    else:
        log(f"Certificate files not found: {cert_file} or {key_file}", Colors.YELLOW)
        log("Falling back to generating self-signed certificate...", Colors.YELLOW)
        
        # Fallback to PEM files if CRT files don't exist
        cert_file_pem = os.path.join(cert_dir, "cert.pem")
        key_file_pem = os.path.join(cert_dir, "key.pem")
        
        if not os.path.exists(cert_file_pem) or not os.path.exists(key_file_pem):
            if not generate_self_signed_cert(cert_file_pem, key_file_pem, domain):
                return None
        
        cert_file = cert_file_pem
        key_file = key_file_pem
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        context.load_cert_chain(cert_file, key_file)
        log("SSL certificate loaded successfully", Colors.GREEN)
        return context
    except Exception as e:
        log(f"Failed to load SSL certificate: {e}", Colors.RED)
        return None

def wait_for_target_server(host, port, timeout=60):
    """Wait for the target server to be available"""
    log(f"Waiting for target server {host}:{port}...", Colors.YELLOW)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    log(f"Target server {host}:{port} is available", Colors.GREEN)
                    return True
        except:
            pass
        time.sleep(0.5)
    
    log(f"Timeout waiting for target server {host}:{port}", Colors.RED)
    return False

class PyProxy:
    """Python reverse proxy server"""
    
    def __init__(self, proxy_host=PROXY_HOST, proxy_port=PROXY_PORT, 
                 target_host=TARGET_HOST, target_port=TARGET_PORT, domain=DOMAIN):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.target_host = target_host
        self.target_port = target_port
        self.domain = domain
        self.server = None
        self.cert_dir = os.path.join(os.path.dirname(__file__), "cert")
        
    def start(self):
        """Start the reverse proxy server"""
        # Wait for target server
        if not wait_for_target_server(self.target_host, self.target_port):
            return False
        
        # Setup SSL
        ssl_context = setup_ssl_context(self.cert_dir, self.domain)
        if not ssl_context:
            log("Failed to setup SSL. Running without HTTPS.", Colors.YELLOW)
            ssl_context = None
        
        # Create server
        try:
            self.server = ThreadingHTTPServer((self.proxy_host, self.proxy_port), ReverseProxyHandler)
            
            if ssl_context:
                self.server.socket = ssl_context.wrap_socket(self.server.socket, server_side=True)
                protocol = "HTTPS"
            else:
                protocol = "HTTP"
            
            log(f"Starting {protocol} reverse proxy on {self.proxy_host}:{self.proxy_port}", Colors.GREEN)
            log(f"Proxying {self.domain} -> {self.target_host}:{self.target_port}", Colors.GREEN)
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
            
        except Exception as e:
            log(f"Failed to start proxy server: {e}", Colors.RED)
            return False
    
    def stop(self):
        """Stop the reverse proxy server"""
        if self.server:
            log("Stopping reverse proxy server...", Colors.YELLOW)
            self.server.shutdown()
            self.server.server_close()
            log("Reverse proxy server stopped", Colors.GREEN)

def main():
    """Main function to run the proxy server"""
    proxy = PyProxy()
    
    try:
        if proxy.start():
            log("Proxy server started successfully. Press Ctrl+C to stop.", Colors.GREEN)
            while True:
                time.sleep(1)
        else:
            log("Failed to start proxy server", Colors.RED)
            sys.exit(1)
    except KeyboardInterrupt:
        log("Received interrupt signal", Colors.YELLOW)
    finally:
        proxy.stop()

if __name__ == "__main__":
    main()
