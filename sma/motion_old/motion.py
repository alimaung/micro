import serial
import time

# Configure serial connection
ser = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    return checksum & 0xFF

def send_tmcl_command(command, type_number, motor, value):
    # Construct command (address=1 by default)
    data = [
        1,                    # Module address
        command,
        type_number,
        motor,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ]
    
    checksum = calculate_checksum(data)
    data.append(checksum)
    
    ser.write(bytes(data))
    return ser.read(9)

try:
    # Start rotating axis 2 (motor 1) with speed 500
    motor = 1  # Axis 2 has index 1
    speed = 500
    
    print(f"Starting motor {motor} at speed {speed}")
    send_tmcl_command(1, 0, motor, speed)  # ROR command (1) to rotate right
    
    # Wait for 10 seconds
    time.sleep(10)
    
    # Stop the motor
    print(f"Stopping motor {motor}")
    send_tmcl_command(3, 0, motor, 0)  # MST command (3) to stop

except Exception as e:
    print(f"Error: {e}")
    # Emergency stop in case of error
    send_tmcl_command(3, 0, motor, 0)

finally:
    # Always close the serial connection
    ser.close()
    print("Connection closed")