# loop indefinitely on and off the magnet
# py .\io_control_cli.py --magnet-on / py .\io_control_cli.py --magnet-off

import time
import os
while True:
    time.sleep(2)
    print("magnet on")
    os.system(r"py .\io_control_cli.py --magnet-on")
    time.sleep(2)
    print("magnet off")
    os.system(r"py .\io_control_cli.py --magnet-off")
