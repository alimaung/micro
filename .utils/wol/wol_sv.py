import socket
import sys
import subprocess

# Preconfigured machines with their IP and MAC addresses
MACHINES = {
    "micro": {"ip": "100.94.49.74", "mac": "02:01:04:31:35:33", "user": "microfilm"},
}
def wake(mac_address, ip_address, port=9):
    """
    Sends a Wake-on-LAN (WOL) magic packet to a specified MAC address.
    
    """
    mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))
        print(f"WOL magic packet sent to {mac_address} via {ip_address}:{port}")

def sleep(mac_address, ip_address, port=9):
    """
    Sends a "Sleep-on-LAN" packet to a specified MAC address (reversed MAC address for testing).
    
    """
    reverse_mac_address = ':'.join(mac_address.split(':')[::-1])

    wake(reverse_mac_address, ip_address, port)

def ping(ip_address):
    """
    Pings the specified IP address to check if the machine is reachable and outputs the same ping results.
    
    """
    try:
        # Run the ping command and capture its output in real-time
        process = subprocess.Popen(["ping", "-n", "4", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print each line of the process output as it occurs
        for line in process.stdout:
            print(line, end='')  # Print the output without adding an extra newline
        
        # Wait for the process to finish and capture the return code
        process.wait()
        
        # Check if the process was successful or if there were errors
        if process.returncode != 0:
            print(f"Error pinging {ip_address}: {process.stderr.read()}")
    except Exception as e:
        print(f"Error pinging {ip_address}: {e}")

def ssh(ip_address, user):
    """
    Initiates an SSH connection to the specified machine using the given user and IP address.
    
    """
    try:
        subprocess.run(["ssh", f"{user}@{ip_address}"], check=True)
        print(f"SSH connection initiated to {user}@{ip_address}")
    except subprocess.CalledProcessError as e:
        print(f"Error initiating SSH connection to {user}@{ip_address}: {e}")

def rdp(ip_address):
    """
    Initiates an RDP connection to the specified machine using the given IP address.
    """
    try:
        subprocess.Popen(["mstsc", f"/v:{ip_address}"])
        print(f"RDP connection initiated to {ip_address}")
    except subprocess.CalledProcessError as e:
        print(f"Error initiating RDP connection to {ip_address}: {e}")

def main():
    """
    Main function to parse command-line arguments and dispatch the appropriate function.
    Usage: python script.py <machine_name> <function_name> 
    """
    if len(sys.argv) < 3:
        print("Usage: python script.py <machine_name> <function_name>")
        print("Available functions: wake, sleep, ping, ssh, rdp")
        print("Available machines:", ", ".join(MACHINES.keys()))
        sys.exit(1)

    machine_name = sys.argv[1]
    function_name = sys.argv[2]

    if machine_name not in MACHINES:
        print(f"Error: Machine '{machine_name}' not found.")
        print("Available machines:", ", ".join(MACHINES.keys()))
        sys.exit(1)

    mac_address = MACHINES[machine_name]["mac"]
    ip_address = MACHINES[machine_name]["ip"]
    user = MACHINES[machine_name]["user"]

    if function_name == "wake":
        wake(mac_address, ip_address)
    elif function_name == "sleep":
        sleep(mac_address, ip_address)
    elif function_name == "ping":
        ping(ip_address)
    elif function_name == "ssh":
        ssh(ip_address, user)
    elif function_name == "rdp":
        rdp(ip_address)
    else:
        print(f"Error: Function '{function_name}' not found.")
        print("Available functions: wake, sleep, ping, ssh, rdp")

if __name__ == "__main__":
    main()
