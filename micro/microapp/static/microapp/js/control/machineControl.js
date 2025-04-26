// Helper function to get the active COM port for machine
function getActiveMachinePort() {
    const machinePort = document.getElementById('machine-port');
    if (machinePort && isMachineConnected && machinePort.textContent !== 'N/A') {
        return machinePort.textContent;
    }
    return 'COM3'; // Default fallback
}

// Function to check the actual machine power state
function checkMachinePowerState(isAfterToggle = false) {
    console.log("Checking actual machine power state...");
    
    fetch('/check_machine_state/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({
            'port': getActiveMachinePort()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const oldPowerState = actualMachinePowerState;
            actualMachinePowerState = data.is_on;
            
            console.log(`Actual machine power state: ${actualMachinePowerState ? 'ON' : 'OFF'}`);
            
            // Check if UI indicators appear to match the actual state
            const uiIndicatesOn = machineIndicator && machineIndicator.classList.contains('on');
            const uiIsConsistent = (uiIndicatesOn === actualMachinePowerState);
            
            // Force update in these cases:
            // 1. After a toggle action
            // 2. When the actual state differs from our JS variable
            // 3. When the UI indicators don't match the actual state
            const shouldForceUpdate = isAfterToggle || (isMachineOn !== actualMachinePowerState) || !uiIsConsistent;
            
            if (shouldForceUpdate) {
                console.log(`Updating UI to match actual power state (inconsistency detected: ${!uiIsConsistent})`);
                
                // Update UI to match actual state
                isMachineOn = actualMachinePowerState;
                updateMachineState(isMachineOn, true); // Always force the update
                
                // Only show notification if state has changed or after toggle action
                if (oldPowerState !== actualMachinePowerState || isAfterToggle) {
                    showNotification(`Machine is now ${actualMachinePowerState ? 'ON' : 'OFF'}`, 'success');
                }
            } else if (isAfterToggle) {
                // If this check is after a toggle and state is as expected, show confirmation
                showNotification(`Machine state confirmed: ${actualMachinePowerState ? 'ON' : 'OFF'}`, 'success');
                
                // Force update indicator to ensure it's fully visible
                if (machineIndicator) {
                    machineIndicator.style.opacity = '1';
                    updateMachineState(isMachineOn, true);
                }
            }
        } else {
            console.error(`Error checking machine power: ${data.message}`);
            if (isAfterToggle) {
                showNotification("Couldn't confirm machine state change", 'warning');
                
                // Reset indicator to full visibility
                if (machineIndicator) {
                    machineIndicator.style.opacity = '1';
                }
            }
        }
    })
    .catch(error => {
        console.error('Error checking machine power:', error);
        if (isAfterToggle) {
            showNotification("Failed to verify machine state", 'error');
            
            // Reset indicator to full visibility
            if (machineIndicator) {
                machineIndicator.style.opacity = '1';
            }
        }
    });
}

// New helper function to clear machine info fields
function clearMachineInfo() {
    const machinePort = document.getElementById('machine-port');
    const machineVendor = document.getElementById('machine-vendor');
    const machineProductId = document.getElementById('machine-product-id');
    const machineSerial = document.getElementById('machine-serial');
    
    if (machinePort) machinePort.textContent = 'N/A';
    if (machineVendor) machineVendor.textContent = 'N/A';
    if (machineProductId) machineProductId.textContent = 'N/A';
    if (machineSerial) machineSerial.textContent = 'N/A';
}

// New helper function to update machine info fields
function updateMachineInfo(port) {
    const machinePort = document.getElementById('machine-port');
    const machineVendor = document.getElementById('machine-vendor');
    const machineProductId = document.getElementById('machine-product-id');
    const machineSerial = document.getElementById('machine-serial');
    
    if (machinePort) machinePort.textContent = port;
    if (machineVendor) machineVendor.textContent = '0x2A3C (TRINAMIC)';
    if (machineProductId) machineProductId.textContent = '0x0100';
    if (machineSerial) machineSerial.textContent = 'TMCSTEP';
}