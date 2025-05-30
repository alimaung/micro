#!/usr/bin/env python
"""
Test script for PyProxy certificate loading
"""
import os
import sys

# Add the pyrp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyrp'))

from caddy import PyProxy, setup_ssl_context, log, Colors

def test_certificate_loading():
    """Test if certificates can be loaded"""
    cert_dir = os.path.join(os.path.dirname(__file__), "pyrp", "cert")
    domain = "micro.film"
    
    print("Testing certificate loading...")
    print(f"Certificate directory: {cert_dir}")
    print(f"Domain: {domain}")
    
    # Check if certificate files exist
    cert_file = os.path.join(cert_dir, f"{domain}.crt")
    key_file = os.path.join(cert_dir, f"{domain}.key")
    
    print(f"Looking for certificate: {cert_file}")
    print(f"Looking for key: {key_file}")
    
    if os.path.exists(cert_file):
        print(f"✓ Certificate file found: {cert_file}")
    else:
        print(f"✗ Certificate file not found: {cert_file}")
    
    if os.path.exists(key_file):
        print(f"✓ Key file found: {key_file}")
    else:
        print(f"✗ Key file not found: {key_file}")
    
    # Test SSL context setup
    print("\nTesting SSL context setup...")
    ssl_context = setup_ssl_context(cert_dir, domain)
    
    if ssl_context:
        print("✓ SSL context created successfully")
        return True
    else:
        print("✗ Failed to create SSL context")
        return False

def test_pyproxy_init():
    """Test PyProxy initialization"""
    print("\nTesting PyProxy initialization...")
    try:
        proxy = PyProxy()
        print("✓ PyProxy initialized successfully")
        print(f"  - Proxy host: {proxy.proxy_host}")
        print(f"  - Proxy port: {proxy.proxy_port}")
        print(f"  - Target host: {proxy.target_host}")
        print(f"  - Target port: {proxy.target_port}")
        print(f"  - Domain: {proxy.domain}")
        print(f"  - Cert directory: {proxy.cert_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize PyProxy: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print(" PyProxy Certificate Test")
    print("=" * 60)
    
    cert_test = test_certificate_loading()
    proxy_test = test_pyproxy_init()
    
    print("\n" + "=" * 60)
    print(" Test Results")
    print("=" * 60)
    print(f"Certificate loading: {'PASS' if cert_test else 'FAIL'}")
    print(f"PyProxy initialization: {'PASS' if proxy_test else 'FAIL'}")
    
    if cert_test and proxy_test:
        print("\n✓ All tests passed! PyProxy should work correctly.")
    else:
        print("\n✗ Some tests failed. Check the certificate files.") 