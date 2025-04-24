def trinamic_supply_voltage_ok():
    target = 1
    inst = 15
    motor = 1
    type1 = 8
    value = 0
    no_answer = False
    
    # Get the voltage response
    voltage = send_bin_command_to_trinamic(target, inst, motor, type1, value, no_answer)
    print(f"Voltage value: {voltage}")
    
    # Simple threshold check: over 10000 means ON, under means OFF
    is_on = voltage > 10000
    return is_on

def send_bin_command_to_trinamic(target, inst, motor, type1, value, no_answer=False):
    array = bytearray(10)  # 10 bytes (0-9)
    
    # Fill the command packet
    array[1] = target & 0xFF
    array[2] = inst & 0xFF
    array[3] = type1 & 0xFF
    array[4] = motor & 0xFF
    
    # Break value into bytes
    array[5] = (value & 0xFF000000) >> 24
    array[6] = (value & 0x00FF0000) >> 16
    array[7] = (value & 0x0000FF00) >> 8
    array[8] = (value & 0x000000FF)
    
    # Calculate checksum
    checksum = 0
    for i in range(1, 9):
        checksum += array[i]
    
    array[9] = checksum & 0xFF
    
    return send_bin_to_trinamic(array, no_answer)

def send_bin_to_trinamic(cmd, no_answer=False):
    # Configure for COM3 with baud rate 38400
    import serial
    import time
    
    try:
        ser = serial.Serial('COM3', 38400, timeout=1)
        
        # Send the command bytes
        for i in range(1, 10):
            ser.write(bytes([cmd[i]]))
        
        # Read the response if not suppressed
        result = 0
        
        if not no_answer:
            # Wait for the device to respond
            time.sleep(0.2)
            
            # Read all available bytes at once
            response = bytearray()
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
            
            # Debug output
            print(f"Received {len(response)} bytes: {[hex(b) for b in response]}")
            
            # Calculate voltage from bytes 7-8 if we have enough bytes
            if len(response) >= 9:
                result = (response[7] * 256 + response[8])
                print(f"  Calculated from bytes 7,8: {hex(response[7])}*256 + {hex(response[8])} = {result}")
            else:
                print("  Incomplete response - returning 0")
        
        ser.close()
        return result
    
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return 0
    
if __name__ == "__main__":
    is_on = trinamic_supply_voltage_ok()
    print(f"Machine is {'ON' if is_on else 'OFF'}")