"""
I/O Control Module

Functions for controlling inputs and outputs on the Trinamic controller
"""

from .trinamic_controller import TrinamicController
from .logger import logger

# Define machine state constants
class MachineState:
    ON = "ON"           # Machine ON with lid closed
    LID_OPEN = "LID_OPEN"   # Machine ON with lid open
    OFF = "OFF"         # Machine completely OFF
    UNKNOWN = "UNKNOWN"     # State couldn't be determined

# Define voltage thresholds based on analysis
VOLTAGE_THRESHOLD_ON = 30000       # Above this = ON with closed lid
VOLTAGE_THRESHOLD_LID_OPEN = 3800  # Between this and ON = lid open, below = machine OFF

class IOControl:
    """
    I/O control functions for Trinamic controllers
    """
    
    def __init__(self, controller):
        """Initialize with a controller instance"""
        self.controller = controller
        logger.debug("IO", "IO Control initialized")
        
    def vacuum_on(self):
        """Turn on the vacuum"""
        logger.debug("IO", "Sending vacuum on command (CMD=14, TYPE=3, MOTOR=2, VALUE=1)")
        return self.controller.send_command(14, 3, 2, 1)
    
    def vacuum_off(self):
        """Turn off the vacuum"""
        logger.debug("IO", "Sending vacuum off command (CMD=14, TYPE=3, MOTOR=2, VALUE=0)")
        return self.controller.send_command(14, 3, 2, 0)
    
    def led_on(self):
        """Turn on the LED"""
        logger.debug("IO", "Sending LED on command (CMD=14, TYPE=0, MOTOR=2, VALUE=1)")
        return self.controller.send_command(14, 0, 2, 1)
    
    def led_off(self):
        """Turn off the LED"""
        logger.debug("IO", "Sending LED off command (CMD=14, TYPE=0, MOTOR=2, VALUE=0)")
        return self.controller.send_command(14, 0, 2, 0)
    
    def magnet_on(self):
        """Turn on the magnet"""
        logger.debug("IO", "Sending magnet on command (CMD=14, TYPE=7, MOTOR=2, VALUE=1)")
        return self.controller.send_command(14, 7, 2, 1)
    
    def magnet_off(self):
        """Turn off the magnet"""
        logger.debug("IO", "Sending magnet off command (CMD=14, TYPE=7, MOTOR=2, VALUE=0)")
        return self.controller.send_command(14, 7, 2, 0)
    
    def is_vacuum_ok(self):
        """Check if vacuum is OK"""
        logger.debug("IO", "Checking vacuum status (CMD=15, TYPE=1, MOTOR=0, VALUE=0)")
        # Log the exact VB code reference for debugging
        logger.debug("IO", "VB original: SendBinComandToTrinamic(1, 15, 0, 1, 0)")
        full_result = self.controller.send_command(15, 1, 0, 0)
        logger.debug("IO", f"Vacuum status raw result: {full_result}")
        
        # Extract the relevant byte (byte 7 or high byte)
        high_byte = (full_result >> 8) & 0xFF
        
        # Log both interpretations
        logger.debug("IO", f"Vacuum status - full value: {full_result}, high byte: {high_byte}")
        
        # Based on the logs, it appears vacuum OK is when high_byte is 0, not OK when high_byte is 1
        # This matches the VB.NET code: Return Conversions.ToBoolean(Interaction.IIf(num7 = 0S, True, False))
        is_vacuum_ok = high_byte == 0
        
        logger.debug("IO", f"Vacuum interpretation: {'OK' if is_vacuum_ok else 'Not OK'}")
        
        return is_vacuum_ok
    
    def is_lid_closed(self):
        """
        Check if the lid is closed.
        
        Note: This function is deprecated. Use is_supply_voltage_ok() instead,
        which correctly determines lid status from the supply voltage.
        """
        logger.debug("IO", "WARNING: Using deprecated is_lid_closed() function")
        logger.debug("IO", "Please use is_supply_voltage_ok() for accurate lid status")
        return self.is_supply_voltage_ok()
    
    def is_at_zero_point(self):
        """Check if at zero point"""
        logger.debug("IO", "Checking zero point status (CMD=15, TYPE=3, MOTOR=0, VALUE=0)")
        # Log the exact VB code reference for debugging
        logger.debug("IO", "VB original: SendBinComandToTrinamic(1, 15, 0, 3, 0)")
        full_result = self.controller.send_command(15, 3, 0, 0)
        logger.debug("IO", f"Zero point status raw result: {full_result}")
        
        # Extract the relevant byte (byte 7 or high byte)
        # The full_result contains all 4 bytes, so we need to extract the byte 
        # that the VB.NET code is checking
        high_byte = (full_result >> 8) & 0xFF
        
        # Log both interpretations
        logger.debug("IO", f"Zero point status - full value: {full_result}, high byte: {high_byte}")
        
        # Check if high byte equals 1 (matches VB.NET behavior)
        is_at_zero = high_byte == 1
        logger.debug("IO", f"Zero point interpretation: {'At zero point' if is_at_zero else 'Not at zero point'}")
        
        return is_at_zero
    
    def get_light_sensor(self):
        """Get light sensor value"""
        logger.debug("IO", "Reading light sensor (CMD=15, TYPE=0, MOTOR=1, VALUE=0)")
        # Log the exact VB code reference for debugging
        logger.debug("IO", "VB original: SendBinComandToTrinamic(1, 15, 1, 0, 0)")
        result = self.controller.send_command(15, 0, 1, 0)
        logger.debug("IO", f"Light sensor raw result: {result}")
        value = int(result / 8)
        logger.debug("IO", f"Light sensor calculated value: {value}")
        return value
    
    def is_supply_voltage_ok(self):
        """
        Check if supply voltage is OK, which indicates lid status.
        
        Based on observed values:
        - Lid closed: ~61000-63000
        - Lid open: drops rapidly to ~4500-5000
        - Machine off: ~3200
        
        According to VB.NET implementation, lid is considered closed
        when the supply voltage is above threshold.
        """
        logger.debug("IO", "Checking supply voltage (CMD=15, TYPE=8, MOTOR=1, VALUE=0)")
        # Log the exact VB code reference for debugging
        logger.debug("IO", "VB original: SendBinComandToTrinamic(1, 15, 1, 8, 0)")
        result = self.controller.send_command(15, 8, 1, 0)
        logger.debug("IO", f"Supply voltage raw result: {result}")
        
        # Set threshold based on observed real-world values
        # When lid is opened, voltage drops rapidly below 10000
        SUPPLY_VOLTAGE_THRESHOLD = 10000
        
        is_ok = result > SUPPLY_VOLTAGE_THRESHOLD
        
        # Provide more descriptive status that directly ties to lid
        status_text = "OK (Lid closed)" if is_ok else "Low (Lid open or machine OFF)"
        logger.debug("IO", f"Supply voltage status: {status_text} (value={result}, threshold={SUPPLY_VOLTAGE_THRESHOLD})")
        
        return is_ok
    
    def get_machine_state(self):
        """
        Determine the complete machine state based on supply voltage.
        
        Returns one of:
        - MachineState.ON: Machine is ON with lid closed (~62000 units)
        - MachineState.LID_OPEN: Machine is ON but lid is open (~4500 units)
        - MachineState.OFF: Machine is completely OFF (~3200 units)
        - MachineState.UNKNOWN: Couldn't determine state
        
        Based on analysis of actual voltage patterns in different states.
        """
        logger.debug("IO", "Determining machine state from supply voltage")
        
        try:
            # Get the supply voltage
            voltage = self.controller.send_command(15, 8, 1, 0)
            logger.debug("IO", f"Supply voltage for state detection: {voltage}")
            
            # Determine state based on thresholds from analysis
            if voltage > VOLTAGE_THRESHOLD_ON:
                state = MachineState.ON
                desc = "ON (Lid closed)"
            elif voltage > VOLTAGE_THRESHOLD_LID_OPEN:
                state = MachineState.LID_OPEN  
                desc = "ON (Lid open)"
            else:
                state = MachineState.OFF
                desc = "OFF"
                
            logger.debug("IO", f"Machine state determined: {state} - {desc} (voltage={voltage})")
            return state
            
        except Exception as e:
            logger.error("IO", f"Error determining machine state: {e}")
            return MachineState.UNKNOWN
            
    # ===== JSON-friendly methods =====
    
    def vacuum_on_json(self):
        """Turn on vacuum and return JSON-friendly result"""
        result = self.vacuum_on()
        return {
            "success": True if result else False,
            "vacuum": "on",
            "result": result
        }
    
    def vacuum_off_json(self):
        """Turn off vacuum and return JSON-friendly result"""
        result = self.vacuum_off()
        return {
            "success": True if result else False,
            "vacuum": "off",
            "result": result
        }
    
    def is_vacuum_ok_json(self):
        """Check vacuum status and return JSON-friendly result"""
        status = self.is_vacuum_ok()
        return {
            "success": True,
            "vacuum_ok": status,
            "vacuum_status": "OK" if status else "Not OK"
        }
    
    def magnet_on_json(self):
        """Turn on magnet and return JSON-friendly result"""
        result = self.magnet_on()
        return {
            "success": True if result else False,
            "magnet": "on",
            "result": result
        }
    
    def magnet_off_json(self):
        """Turn off magnet and return JSON-friendly result"""
        result = self.magnet_off()
        return {
            "success": True if result else False, 
            "magnet": "off",
            "result": result
        }
        
    def get_machine_state_json(self):
        """Get machine state and return JSON-friendly result"""
        state = self.get_machine_state()
        return {
            "success": state != MachineState.UNKNOWN,
            "state": state,
            "lid_closed": state == MachineState.ON
        }