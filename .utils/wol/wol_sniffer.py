#!/usr/bin/env python3
import socket
import struct
import binascii
import argparse
import sys
import time
import datetime

# ANSI color codes for prettier output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def format_mac(mac_bytes):
    """Format MAC address bytes as a string."""
    return ':'.join(f"{b:02x}" for b in mac_bytes)

def print_wol_packet_structure(data):
    """Print the WoL packet in a structured, easy-to-read format."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== WAKE-ON-LAN PACKET STRUCTURE ==={Colors.ENDC}")
    
    # Print the sync stream (first 6 bytes)
    sync_stream = data[0:6]
    print(f"\n{Colors.BOLD}Synchronization Stream (6 bytes):{Colors.ENDC}")
    print(f"{Colors.BLUE}Hex: {Colors.CYAN}{' '.join(f'{b:02x}' for b in sync_stream)}{Colors.ENDC}")
    
    # Print the target MAC
    mac_bytes = data[6:12]
    mac_str = format_mac(mac_bytes)
    print(f"\n{Colors.BOLD}Target MAC Address:{Colors.ENDC} {Colors.GREEN}{mac_str}{Colors.ENDC}")
    
    # Print the 16 repetitions
    print(f"\n{Colors.BOLD}MAC Address Repetitions (16 times):{Colors.ENDC}")
    for i in range(16):
        offset = 6 + i * 6
        rep_bytes = data[offset:offset+6]
        rep_mac = format_mac(rep_bytes)
        
        # Check if this repetition matches the first MAC
        if rep_bytes == mac_bytes:
            status = f"{Colors.GREEN}✓{Colors.ENDC}"
        else:
            status = f"{Colors.RED}✗{Colors.ENDC}"
            
        print(f"  {i+1:2d}: {rep_mac} {status}")

def print_hexdump(data, bytes_per_line=16):
    """Print a nicely formatted hexdump of the packet."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== PACKET HEXDUMP ==={Colors.ENDC}")
    
    # Print header
    print(f"\n{Colors.BOLD}{'Offset':6} {'Hexadecimal':49} {'ASCII'}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'―' * 75}{Colors.ENDC}")
    
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i+bytes_per_line]
        
        # Format the hex part
        hex_part = ' '.join(f"{b:02x}" for b in chunk)
        hex_part = f"{hex_part:<{bytes_per_line * 3 - 1}}"
        
        # Format the ASCII part
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        
        # Colorize based on section of the packet
        if i < 6:  # Sync stream
            color = Colors.BLUE
        elif i < 12:  # First MAC
            color = Colors.GREEN
        else:  # Repetitions
            color = Colors.CYAN
            
        print(f"{color}0x{i:04x}:  {hex_part}  {ascii_part}{Colors.ENDC}")

def listen_for_wol(interface_ip, port=9, timeout=None):
    """
    Listen for Wake-on-LAN packets on the specified IP and port.
    
    Args:
        interface_ip: IP address to listen on
        port: UDP port to listen on (default: 9)
        timeout: Time in seconds to listen before giving up. None for indefinite (default: None)
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set a timeout so we don't block indefinitely but can check for user interruption
    sock.settimeout(1)
    
    # Bind to the specified IP and port
    sock.bind((interface_ip, port))
    
    print(f"Listening for WoL packets on {interface_ip}:{port}...")
    if timeout:
        print(f"Will listen for {timeout} seconds or until interrupted.")
        end_time = time.time() + timeout
    else:
        print("Listening indefinitely. Press Ctrl+C to stop.")
        end_time = float('inf')
    
    # Track time since last activity message
    last_status = time.time()
    status_interval = 60  # Print status message every minute
    packets_received = 0
    
    while time.time() < end_time:
        try:
            data, addr = sock.recvfrom(1024)
            packets_received += 1
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{Colors.BOLD}[{timestamp}] Received packet from {addr[0]}:{addr[1]} ({len(data)} bytes){Colors.ENDC}")
            
            # Check if it's a valid WoL magic packet
            if len(data) >= 102:  # 6 bytes of 0xFF + 16 repetitions of 6-byte MAC
                # Check for synchronization stream (6 bytes of 0xFF)
                if data[0:6] == b'\xff\xff\xff\xff\xff\xff':
                    print(f"{Colors.GREEN}✓ Synchronization stream verified (6 bytes of 0xFF){Colors.ENDC}")
                    
                    # Extract the first MAC address from the packet
                    mac_bytes = data[6:12]
                    mac_addr = format_mac(mac_bytes)
                    print(f"Target MAC address: {Colors.GREEN}{mac_addr}{Colors.ENDC}")
                    
                    # Verify the 16 repetitions of the MAC address
                    valid_repetitions = True
                    for i in range(16):
                        offset = 6 + i * 6
                        if data[offset:offset+6] != mac_bytes:
                            valid_repetitions = False
                            print(f"{Colors.RED}✗ Repetition {i+1} is invalid{Colors.ENDC}")
                            break
                    
                    if valid_repetitions:
                        print(f"{Colors.GREEN}✓ All 16 MAC address repetitions verified{Colors.ENDC}")
                        
                        # Print detailed packet structure and hexdump
                        print_wol_packet_structure(data)
                        print_hexdump(data)
                        
                        # Print success message at the end
                        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ VALID WAKE-ON-LAN PACKET DETECTED{Colors.ENDC}")
                        
                        if timeout:
                            return True
                    else:
                        print(f"{Colors.RED}✗ Not all MAC repetitions match the target MAC{Colors.ENDC}")
                        print_wol_packet_structure(data)
                        print_hexdump(data)
                else:
                    print(f"{Colors.RED}✗ Synchronization stream missing (expecting 6 bytes of 0xFF){Colors.ENDC}")
                    print_hexdump(data)
            else:
                print(f"{Colors.RED}✗ Packet too small to be a valid WoL packet{Colors.ENDC}")
                print_hexdump(data)
            
            # Reset the status timer after displaying a packet
            last_status = time.time()
            
        except socket.timeout:
            # Check if we should print a status message
            if time.time() - last_status > status_interval:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Colors.CYAN}[{timestamp}] Still listening... ({packets_received} packets received so far){Colors.ENDC}")
                last_status = time.time()
            
            continue
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Listener stopped by user.{Colors.ENDC}")
            return False
    
    if timeout:
        print(f"\n{Colors.YELLOW}⚠️ No valid WoL packets detected during the listen period.{Colors.ENDC}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Listen for Wake-on-LAN magic packets")
    parser.add_argument("interface_ip", help="IP address of the interface to listen on")
    parser.add_argument("--port", type=int, default=9, help="UDP port to listen on (default: 9)")
    parser.add_argument("--timeout", type=int, help="Time in seconds to listen (default: run indefinitely)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    args = parser.parse_args()
    
    # Disable colors if requested or if not in a terminal
    if args.no_color or not sys.stdout.isatty():
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')
    
    try:
        listen_for_wol(args.interface_ip, args.port, args.timeout)
    except KeyboardInterrupt:
        print("\nListener stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main() 