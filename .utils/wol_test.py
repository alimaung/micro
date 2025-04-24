#!/usr/bin/env python3
import socket
import sys
import time
import threading
import argparse
import subprocess

# Try to import from the same directory
try:
    from wol_sniffer import listen_for_wol
except ImportError:
    print("Error: Cannot import wol_sniffer module. Make sure it's in the same directory.")
    sys.exit(1)

def send_wol_packet(mac_address, ip_address="255.255.255.255", port=9):
    """
    Send a Wake-on-LAN packet to the specified MAC address.
    
    Args:
        mac_address: MAC address of the target machine
        ip_address: IP address to send the packet to (default: broadcast 255.255.255.255)
        port: UDP port to use (default: 9)
    """
    # Convert the MAC address string to bytes
    mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
    
    # Create the magic packet: 6 bytes of 0xFF followed by the MAC address repeated 16 times
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Set socket options to allow broadcasting
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Send the magic packet
        sock.sendto(magic_packet, (ip_address, port))
        
        print(f"Sent WoL magic packet to {mac_address} via {ip_address}:{port}")
        
        # Return the packet for verification
        return magic_packet

def get_local_ip():
    """Get the IP address of the local machine."""
    try:
        # Create a socket and connect to an external address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        # Fall back to hostname resolution
        return socket.gethostbyname(socket.gethostname())

def run_wol_listener(mac=None):
    """
    Start a WoL packet listener using the local IP address.
    Runs indefinitely until interrupted.
    
    Args:
        mac: Optional MAC address to send a test packet to
    """
    # Get the local IP address
    local_ip = get_local_ip()
    print(f"Using local IP: {local_ip}")
    
    if mac:
        # Start a separate thread to send a test packet after a delay
        def send_test_packet():
            time.sleep(2)  # Wait for the listener to start
            print(f"\nSending test WoL packet to MAC: {mac}")
            send_wol_packet(mac)
        
        sender = threading.Thread(target=send_test_packet)
        sender.daemon = True
        sender.start()
    
    try:
        # Run the listener indefinitely (until Ctrl+C)
        print(f"Starting WoL packet listener on {local_ip}...")
        print("Press Ctrl+C to stop")
        
        # Pass a very large timeout to effectively run indefinitely
        listen_for_wol(local_ip, 9, 3600*24*365)  # Run for a year (effectively forever)
        
    except KeyboardInterrupt:
        print("\nListener stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")

def main():
    parser = argparse.ArgumentParser(description="Test Wake-on-LAN by sending and capturing packets")
    parser.add_argument("--mac", help="MAC address to send a test packet to (optional)")
    args = parser.parse_args()
    
    run_wol_listener(args.mac)

if __name__ == "__main__":
    main() 