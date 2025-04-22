import subprocess
import sys
import os

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        # Windows check for admin privileges
        return os.name == 'nt' and subprocess.run('net session', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
    except:
        return False

def install_packages():
    """Install required packages"""
    packages = ["flask", "requests"]
    
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False
    return True

def setup_server():
    """Setup steps for the server (PC1)"""
    print("\n==== Setting up Server on PC1 (192.168.1.96) ====")
    print("1. Installing required packages...")
    if not install_packages():
        return
    
    print("\n2. Checking if port 5000 is open in the firewall...")
    if is_admin():
        # Add firewall rule for port 5000
        try:
            subprocess.check_call(
                'netsh advfirewall firewall add rule name="Microfilm Remote Server" '
                'dir=in action=allow protocol=TCP localport=5000',
                shell=True
            )
            print("Firewall rule added successfully!")
        except subprocess.CalledProcessError:
            print("Failed to add firewall rule. You may need to manually open port 5000.")
    else:
        print("Script is not running with admin privileges. Please run the following command manually in an admin command prompt:")
        print('netsh advfirewall firewall add rule name="Microfilm Remote Server" dir=in action=allow protocol=TCP localport=5000')
    
    print("\nSetup complete! Run 'python remote_server.py' to start the server.")

def setup_client():
    """Setup steps for the client (PC2)"""
    print("\n==== Setting up Client on PC2 (192.168.1.111) ====")
    print("1. Installing required packages...")
    if not install_packages():
        return
    
    print("\nSetup complete! Use the following commands on PC2:")
    print("- To start processing: python remote_client.py start --folder PATH_TO_FOLDER")
    print("- To check status: python remote_client.py status")

if __name__ == "__main__":
    print("Microfilm Remote Processing Setup")
    print("=================================")
    
    while True:
        choice = input("Is this PC1 (server - 192.168.1.96) or PC2 (client - 192.168.1.111)? [1/2]: ").strip()
        if choice == "1":
            setup_server()
            break
        elif choice == "2":
            setup_client()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.") 