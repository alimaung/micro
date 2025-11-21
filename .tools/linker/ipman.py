import wmi
import time
from colorama import Fore, Style, init

init(autoreset=True)

w = wmi.WMI()

# Track current IP
current_ip = None

# WMI event watcher for IP changes
watcher = w.watch_for(
    notification_type="Modification",
    wmi_class="Win32_NetworkAdapterConfiguration",
    delay_secs=1
)

def get_ip():
    """Get the primary active IPv4 address"""
    for nic in w.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        if nic.IPAddress:
            for ip in nic.IPAddress:
                if "." in ip:  # IPv4 only
                    return ip
    return None

print("Starting event-based IP monitor...\n")
current_ip = get_ip()

while True:
    # ------------------------
    # 1. Non-blocking WMI event check
    # ------------------------
    try:
        event = watcher(timeout_ms=1)
        if event:
            new_ip = get_ip()
            if new_ip != current_ip:
                print(Fore.RED + f"[IP CHANGE DETECTED] {current_ip} → {new_ip}")
                current_ip = new_ip
    except wmi.x_wmi_timed_out:
        # No event — this is normal
        pass

    # ------------------------
    # 2. Print IP every 5 seconds
    # ------------------------
    print(f"Current IP: {current_ip}")
    time.sleep(5)
