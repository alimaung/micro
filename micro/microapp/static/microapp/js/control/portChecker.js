
const machineSwitch = document.getElementById('machine-switch');
// Add a state variable for tracking last notification time
let lastRelayNotificationTime = 0;
const NOTIFICATION_THROTTLE_MS = 30000; // 30 seconds 

// Add global device info tracking variables
let lastRelayDeviceData = {
    port: 'N/A',
    vendor_id: 'N/A',
    product_id: 'N/A',
    product: 'N/A',
    manufacturer: 'N/A'
};

let lastMachineDeviceData = {
    port: 'N/A',
    vendor_id: 'N/A',
    product_id: 'N/A',
    serial_number: 'N/A',
    manufacturer: 'N/A'
};
let isRelayConnected = false;

// Function to check for available COM ports with redundancy prevention
function checkAvailablePorts() {
    console.log("Checking connection status for all ports...");

    // Check for SMA51 Machine on COM3
    checkMachinePort();

    // Check for Saferoom Relay on COM7 or COM18
    checkRelayPort();

    // Update overall system status (without redundant UI updates)
    updateSystemStatus();
}

// Function to check if SMA51 Machine port is available (COM3)
function checkMachinePort() {
    console.log("Checking for SMA51 Machine on COM3...");
    // Disable machine toggle button during check
    if (machineSwitch) {
        machineSwitch.disabled = true;
        machineSwitch.classList.add('checking');
    }

    fetch('/check_port/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({
            'port': 'COM3'
        })
    })
    .then(response => response.json())
    .then(data => {
        // Store previous state to detect changes
        const previousState = isMachineConnected;
        
        if (data.status === 'success') {
            // Port is available
            isMachineConnected = true;
            
            // Update machine port info with the returned device info
            if (data.device_info) {
                // Only update UI if device info has changed
                if (!isEqualDeviceInfo(lastMachineDeviceData, data.device_info)) {
                    updateMachineInfoFromData(data.device_info);
                    // Store current data for future comparison
                    lastMachineDeviceData = { ...data.device_info };
                }
            } else {
                // Fallback to default values only if we don't already have data
                if (lastMachineDeviceData.port === 'N/A') {
                    updateMachineInfo('COM3');
                    lastMachineDeviceData.port = 'COM3';
                }
            }
            
            // Update machine connection UI
            updateMachineConnectionUI(true);
            
            // Show notification if state changed from disconnected to connected
            if (!previousState && isMachineConnected) {
                showNotification("Machine connected", "success");
                
                // Check actual power state now that we're connected
                checkMachinePowerState();
            }
            
            console.log("SMA51 Machine connected on COM3");
        } else {
            // Port is not available
            isMachineConnected = false;
            
            // Update machine connection UI
            updateMachineConnectionUI(false);
            
            // Show notification if state changed from connected to disconnected
            if (previousState && !isMachineConnected) {
                showNotification("Machine disconnected", "error");
                
                // Clear device info only if we're newly disconnected
                clearMachineInfo();
                lastMachineDeviceData = {
                    port: 'N/A',
                    vendor_id: 'N/A',
                    product_id: 'N/A',
                    serial_number: 'N/A',
                    manufacturer: 'N/A'
                };
                
                // If machine was on but now disconnected, update its state to off
                if (isMachineOn) {
                    isMachineOn = false;
                    updateMachineState(false);
                }
            }
            
            console.log("SMA51 Machine not connected");
        }
        
        // Re-enable machine toggle button after check
        if (machineSwitch) {
            machineSwitch.disabled = false;
            machineSwitch.classList.remove('checking');
        }
    })
    .catch(error => {
        console.error('Error checking machine port:', error);
        isMachineConnected = false;
        
        // Update machine connection UI
        updateMachineConnectionUI(false);
        
        // Re-enable machine toggle button after check
        if (machineSwitch) {
            machineSwitch.disabled = false;
            machineSwitch.classList.remove('checking');
        }
    });
    }

// Function to check if Saferoom Relay port is available (COM7 or COM18)
function checkRelayPort() {
    console.log("Checking for Saferoom Relay on COM18...");

    // Store previous states before any changes
    const wasConnected = isRelayConnected;
    const previousPort = getActiveRelayPort();

    // Don't clear device info - we'll update only if needed

    // Disable mode toggle during check
    if (modeToggle) {
        modeToggle.disabled = true;
        modeToggle.classList.add('checking');
    }

    // First try COM18
    fetch('/check_port/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: new URLSearchParams({
            'port': 'COM18'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // COM18 is available
            isRelayConnected = true;
            
            // Update relay port info with the returned device info
            if (data.device_info) {
                // Only update UI if device info has changed
                if (!isEqualDeviceInfo(lastRelayDeviceData, data.device_info)) {
                    updateRelayInfoFromData(data.device_info);
                    // Store current data for future comparison
                    lastRelayDeviceData = { ...data.device_info };
                }
            } else {
                // Fallback to default values only if we don't already have data
                if (lastRelayDeviceData.port === 'N/A') {
                    updateRelayInfo('COM18');
                    lastRelayDeviceData.port = 'COM18';
                }
            }
            
            // Update relay connection UI
            updateRelayConnectionUI(true);
            
            // Check conditions for showing notification
            const currentPort = getActiveRelayPort();
            const currentTime = Date.now();
            
            if (!wasConnected && currentTime - lastRelayNotificationTime > NOTIFICATION_THROTTLE_MS) {
                // Only notify if we weren't connected before and enough time has passed
                showNotification("Relay connected on COM18", "success");
                lastRelayNotificationTime = currentTime;
            } else if (wasConnected && previousPort !== 'COM18' && previousPort !== 'N/A' && 
                        currentTime - lastRelayNotificationTime > NOTIFICATION_THROTTLE_MS) {
                // Notify of port change only if enough time has passed
                showNotification("Relay connected on COM18", "info");
                lastRelayNotificationTime = currentTime;
            }
            
            console.log("Saferoom Relay connected on COM18");
        } else {
            // Try COM7 instead
            console.log("COM18 not available, checking COM7...");
            
            fetch('/check_port/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'port': 'COM7'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // COM7 is available
                    isRelayConnected = true;
                    
                    // Update relay port info with the returned device info
                    if (data.device_info) {
                        // Only update UI if device info has changed
                        if (!isEqualDeviceInfo(lastRelayDeviceData, data.device_info)) {
                            updateRelayInfoFromData(data.device_info);
                            // Store current data for future comparison
                            lastRelayDeviceData = { ...data.device_info };
                        }
                    } else {
                        // Fallback to default values only if we don't already have data
                        if (lastRelayDeviceData.port === 'N/A') {
                            updateRelayInfo('COM7');
                            lastRelayDeviceData.port = 'COM7';
                        }
                    }
                    
                    // Update relay connection UI
                    updateRelayConnectionUI(true);
                    
                    // Check conditions for showing notification
                    const currentPort = getActiveRelayPort();
                    const currentTime = Date.now();
                    
                    if (!wasConnected && currentTime - lastRelayNotificationTime > NOTIFICATION_THROTTLE_MS) {
                        // Only notify if we weren't connected before and enough time has passed
                        showNotification("Relay connected on COM7", "success");
                        lastRelayNotificationTime = currentTime;
                    } else if (wasConnected && previousPort !== 'COM7' && previousPort !== 'N/A' && 
                                currentTime - lastRelayNotificationTime > NOTIFICATION_THROTTLE_MS) {
                        // Notify of port change only if enough time has passed
                        showNotification("Relay connected on COM7", "info");
                        lastRelayNotificationTime = currentTime;
                    }
                    
                    console.log("Saferoom Relay connected on COM7");
                } else {
                    // Neither COM18 nor COM7 is available
                    isRelayConnected = false;
                    
                    // Update relay connection UI
                    updateRelayConnectionUI(false);
                    
                    // Show notification if state changed from connected to disconnected
                    const currentTime = Date.now();
                    if (wasConnected && currentTime - lastRelayNotificationTime > NOTIFICATION_THROTTLE_MS) {
                        showNotification("Relay disconnected", "error");
                        lastRelayNotificationTime = currentTime;
                        
                        // Clear device info only if we're newly disconnected
                        clearRelayInfo();
                        lastRelayDeviceData = {
                            port: 'N/A',
                            vendor_id: 'N/A',
                            product_id: 'N/A',
                            product: 'N/A',
                            manufacturer: 'N/A'
                        };
                    }
                    
                    console.log("Saferoom Relay not connected");
                }
                
                // Re-enable mode toggle after check
                if (modeToggle) {
                    modeToggle.disabled = false;
                    modeToggle.classList.remove('checking');
                }
            })
            .catch(error => {
                console.error('Error checking COM7:', error);
                isRelayConnected = false;
                
                // Update relay connection UI
                updateRelayConnectionUI(false);
                
                // Re-enable mode toggle after check
                if (modeToggle) {
                    modeToggle.disabled = false;
                    modeToggle.classList.remove('checking');
                }
            });
        }
    })
    .catch(error => {
        console.error('Error checking COM18:', error);
        isRelayConnected = false;
        
        // Update relay connection UI
        updateRelayConnectionUI(false);
        
        // Re-enable mode toggle after check
        if (modeToggle) {
            modeToggle.disabled = false;
            modeToggle.classList.remove('checking');
        }
    });
}

// Function to update the machine connection UI
function updateMachineConnectionUI(isConnected) {
    // Update connection status indicator
    updateConnectionStatus(machineConnectionStatus, isConnected);
    
    // Update machine switch UI based on connection state
    if (machineSwitch) {
        machineSwitch.disabled = !isConnected;
        machineSwitch.classList.toggle('disabled', !isConnected);
        
        if (!isConnected && isMachineOn) {
            // If machine disconnected but state was on, reset the state
            isMachineOn = false;
            updateMachineState(false);
        }
    }
    
    // Update emergency stop button
    if (emergencyStop) {
        emergencyStop.disabled = !isConnected;
        emergencyStop.classList.toggle('disabled', !isConnected);
    }
    
    // Update machine test connection button
    if (machineTestConnection) {
        machineTestConnection.classList.toggle('connected', isConnected);
    }
            
    // Update overall system status
    updateSystemStatus();
}

// Function to update the relay connection UI
function updateRelayConnectionUI(isConnected) {
    // Update connection status indicator
    updateConnectionStatus(relayConnectionStatus, isConnected);
    
    // Update mode toggle UI based on connection state
    if (modeToggle) {
        modeToggle.disabled = !isConnected;
        modeToggle.classList.toggle('disabled', !isConnected);
    }
    
    // Update relay test connection button
    if (relayTestConnection) {
        relayTestConnection.classList.toggle('connected', isConnected);
    }
    
    // Update all relay toggle buttons
    document.querySelectorAll('.relay-toggle').forEach(button => {
        button.disabled = !isConnected;
        button.classList.toggle('disabled', !isConnected);
    });
    
    // Update overall system status
    updateSystemStatus();
}

// Function to update connection status indicator
function updateConnectionStatus(statusElement, isConnected) {
    if (statusElement) {
        if (isConnected) {
            statusElement.classList.remove('critical');
            statusElement.classList.add('operational');
            statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
        } else {
            statusElement.classList.remove('operational');
            statusElement.classList.add('critical');
            statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
        }
    }
}