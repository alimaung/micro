import os
import subprocess
import time

DISPLAY_EXE = r"Y:\micro\micro\saferoom_control\display64.exe"

def power_off(device_id):
    subprocess.run([DISPLAY_EXE, "/device", str(device_id), "/power", "off"])

def power_on(device_id):
    subprocess.run([DISPLAY_EXE, "/device", str(device_id), "/power", "on"])

def power_all_off():
    subprocess.run([DISPLAY_EXE, "/power", "off"])

def power_all_on():
    subprocess.run([DISPLAY_EXE, "/power", "on"])

def main():
    device_id = 2
    power_off(device_id)
    time.sleep(10)
    power_on(device_id)

if __name__ == "__main__":
    main()
