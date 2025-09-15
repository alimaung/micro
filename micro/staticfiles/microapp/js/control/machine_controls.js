/**
 * machine_controls.js - Machine control functions for microfilm system
 * Handles operations related to controlling the main machine
 */

// Create namespace for machine control functions
const MachineControls = {
    // State tracking
    isMachineOn: false,
    actualMachinePowerState: false,
    
    // Constants
    TRANSITION_DURATION: 300, // ms

    /**
     * Toggle the machine power state
     */
    triggerMachineToggle: function() {
        // Store the intended state
        const intendedState = !this.isMachineOn;
        const action = intendedState ? 'on' : 'off';
        
        // Get DOM elements
        const machineSwitch = document.getElementById('machine-switch');
        const machineIndicator = document.getElementById('machine-indicator');
        
        // Start loading state
        if (machineSwitch) machineSwitch.classList.add('loading');
        
        // Animate the indicator to show processing state
        if (machineIndicator) {
            machineIndicator.style.transform = 'scale(0.5)';
            machineIndicator.style.opacity = '0.5';
            machineIndicator.classList.remove('pulse-hold');
        }
        
        console.log(`Requesting machine state change to: ${intendedState ? 'ON' : 'OFF'}`);

        // Send AJAX request to toggle machine switch
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': action,
                'relay': '8'  // Machine control relay
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            if (machineSwitch) machineSwitch.classList.remove('loading');
            
            if (data.status === 'success') {
                // Don't update UI yet, just show a pending notification
                NotificationManager.showNotification(`Machine state change initiated`, 'info');
                
                // Reset indicator appearance but keep in a "pending" state
                if (machineIndicator) {
                    machineIndicator.style.transform = 'scale(1)';
                    machineIndicator.style.opacity = '0.7';
                }
                
                // Check actual power state after a delay to allow machine to respond
                setTimeout(() => {
                    this.checkMachinePowerState(true); // Pass true to indicate this is after a toggle action
                }, 2000);
            } else {
                console.error(`Error: ${data.message}`);
                NotificationManager.showNotification('Error switching machine', 'error');
                
                // Reset indicator without changing state
                if (machineIndicator) {
                    machineIndicator.style.transform = 'scale(1)';
                    machineIndicator.style.opacity = '1';
                }
            }
        })
        .catch(error => {
            // End loading state
            if (machineSwitch) machineSwitch.classList.remove('loading');
            
            console.error('Error:', error);
            NotificationManager.showNotification('Network error', 'error');
            
            // Reset indicator without changing state
            if (machineIndicator) {
                machineIndicator.style.transform = 'scale(1)';
                machineIndicator.style.opacity = '1';
            }
        });
    },

    /**
     * Trigger an emergency stop
     */
    triggerEmergencyStop: function() {
        const emergencyStop = document.getElementById('emergency-stop');
        
        // Add loading state
        if (emergencyStop) {
            emergencyStop.classList.add('loading');
            emergencyStop.classList.add('pulse');
            emergencyStop.classList.remove('emergency-pulse');
        }
        
        // Send emergency stop AJAX request
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': 'emergency_stop',
                'com_port': ConnectionManager.getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            if (emergencyStop) {
                emergencyStop.classList.remove('loading');
                emergencyStop.classList.remove('pulse');
            }
            
            if (data.status === 'success') {
                // Show notification
                NotificationManager.showNotification('Emergency stop activated', 'warning');
                
                // Update machine state to reflect the emergency stop (machine off)
                this.isMachineOn = false;
                this.actualMachinePowerState = false;
                this.updateMachineState(false, true);
                
                // Ensure motors are stopped visually
                UIManager.stopAllMotorAnimations();
            } else {
                console.error(`Error: ${data.message}`);
                NotificationManager.showNotification('Error activating emergency stop', 'error');
            }
        })
        .catch(error => {
            // End loading state
            if (emergencyStop) {
                emergencyStop.classList.remove('loading');
                emergencyStop.classList.remove('pulse');
            }
            
            console.error('Error:', error);
            NotificationManager.showNotification('Network error', 'error');
        });
    },

    /**
     * Check the current power state of the machine
     * @param {boolean} isAfterToggle - Whether this check is after a toggle operation
     */
    checkMachinePowerState: function(isAfterToggle = false) {
        console.log("Checking actual machine power state...");
        const machineIndicator = document.getElementById('machine-indicator');
        
        fetch('/check_machine_state/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'port': ConnectionManager.getActiveMachinePort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const oldPowerState = this.actualMachinePowerState;
                this.actualMachinePowerState = data.is_on;
                
                console.log(`Actual machine power state: ${this.actualMachinePowerState ? 'ON' : 'OFF'}`);
                
                // Check if UI indicators appear to match the actual state
                const uiIndicatesOn = machineIndicator && machineIndicator.classList.contains('on');
                const uiIsConsistent = (uiIndicatesOn === this.actualMachinePowerState);
                
                // Force update in these cases:
                // 1. After a toggle action
                // 2. When the actual state differs from our JS variable
                // 3. When the UI indicators don't match the actual state
                const shouldForceUpdate = isAfterToggle || (this.isMachineOn !== this.actualMachinePowerState) || !uiIsConsistent;
                
                if (shouldForceUpdate) {
                    console.log(`Updating UI to match actual power state (inconsistency detected: ${!uiIsConsistent})`);
                    
                    // Update UI to match actual state
                    this.isMachineOn = this.actualMachinePowerState;
                    this.updateMachineState(this.isMachineOn, true); // Always force the update
                    
                    // Only show notification if state has changed or after toggle action
                    if (oldPowerState !== this.actualMachinePowerState || isAfterToggle) {
                        NotificationManager.showNotification(`Machine is now ${this.actualMachinePowerState ? 'ON' : 'OFF'}`, 'success');
                    }
                } else if (isAfterToggle) {
                    // If this check is after a toggle and state is as expected, show confirmation
                    NotificationManager.showNotification(`Machine state confirmed: ${this.actualMachinePowerState ? 'ON' : 'OFF'}`, 'success');
                    
                    // Force update indicator to ensure it's fully visible
                    if (machineIndicator) {
                        machineIndicator.style.opacity = '1';
                        this.updateMachineState(this.isMachineOn, true);
                    }
                }
            } else {
                console.error(`Error checking machine power: ${data.message}`);
                if (isAfterToggle) {
                    NotificationManager.showNotification("Couldn't confirm machine state change", 'warning');
                    
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
                NotificationManager.showNotification("Failed to verify machine state", 'error');
                
                // Reset indicator to full visibility
                if (machineIndicator) {
                    machineIndicator.style.opacity = '1';
                }
            }
        });
    },

    /**
     * Update the machine's power state and UI
     * @param {boolean} isOn - Whether the machine is on
     * @param {boolean} forceUpdate - Whether to force the UI update
     */
    updateMachineState: function(isOn, forceUpdate = false) {
        console.log(`Updating machine state UI to: ${isOn ? 'ON' : 'OFF'}, force update: ${forceUpdate}`);
        
        const machineIndicator = document.getElementById('machine-indicator');
        const machinePowerStatus = document.getElementById('machine-power-status');
        
        // Update if state has changed or force update is requested
        if (this.isMachineOn !== isOn || forceUpdate) {
            // Update UI state
            this.isMachineOn = isOn;
            
            // Always update the machine indicator icon regardless of previous state
            if (machineIndicator) {
                // Direct style application instead of using CSS transitions
                if (isOn) {
                    machineIndicator.style.color = '#00ff00';
                    machineIndicator.style.backgroundColor = '#30d158';
                    machineIndicator.style.boxShadow = '0 0 8px rgba(48, 209, 88, 0.5)';
                } else {
                    machineIndicator.style.color = '#ff0000';
                    machineIndicator.style.backgroundColor = '#ff453a';
                    machineIndicator.style.boxShadow = '0 0 6px rgba(255, 69, 58, 0.5)';
                }
                
                // Reset opacity in case it was changed during animation
                machineIndicator.style.opacity = '1';
                
                // Toggle class for styling
                if (isOn) {
                    machineIndicator.classList.add('on');
                } else {
                    machineIndicator.classList.remove('on');
                }
            }
            
            // Always update the machine power status indicator
            if (machinePowerStatus) {
                UIManager.updateMachineStatus(isOn);
            }
            
            // If we turn off, stop all motor animations if they exist
            if (!isOn) {
                UIManager.stopAllMotorAnimations();
            }
            
            console.log(`Machine state UI updated to: ${isOn ? 'ON' : 'OFF'}`);
        } else {
            console.log('Machine state unchanged, skipping UI update');
            
            // Even if we skip the update, ensure status indicators are still consistent with current state
            // This handles cases where the UI might be out of sync with the state variable
            if (machineIndicator && ((isOn && !machineIndicator.classList.contains('on')) || 
                                    (!isOn && machineIndicator.classList.contains('on')))) {
                console.log('Detected UI inconsistency, forcing update...');
                
                // Apply direct style changes
                if (isOn) {
                    machineIndicator.style.color = '#00ff00';
                    machineIndicator.style.backgroundColor = '#30d158';
                    machineIndicator.style.boxShadow = '0 0 8px rgba(48, 209, 88, 0.5)';
                    machineIndicator.classList.add('on');
                } else {
                    machineIndicator.style.color = '#ff0000';
                    machineIndicator.style.backgroundColor = '#ff453a';
                    machineIndicator.style.boxShadow = '0 0 6px rgba(255, 69, 58, 0.5)';
                    machineIndicator.classList.remove('on');
                }
                
                machineIndicator.style.opacity = '1';
                
                // Update status badge as well
                if (machinePowerStatus) {
                    UIManager.updateMachineStatus(isOn);
                }
                
                console.log('UI inconsistency fixed');
            }
        }
    },

    /**
     * Clear machine information display
     */
    clearMachineInfo: function() {
        const machinePort = document.getElementById('machine-port');
        const machineVendor = document.getElementById('machine-vendor');
        const machineProductId = document.getElementById('machine-product-id');
        const machineSerial = document.getElementById('machine-serial');
        
        if (machinePort) machinePort.textContent = 'N/A';
        if (machineVendor) machineVendor.textContent = 'N/A';
        if (machineProductId) machineProductId.textContent = 'N/A';
        if (machineSerial) machineSerial.textContent = 'N/A';
    },

    /**
     * Update machine information display
     * @param {string} port - The COM port to display
     */
    updateMachineInfo: function(port) {
        const machinePort = document.getElementById('machine-port');
        const machineVendor = document.getElementById('machine-vendor');
        const machineProductId = document.getElementById('machine-product-id');
        const machineSerial = document.getElementById('machine-serial');
        
        if (machinePort) machinePort.textContent = port;
        if (machineVendor) machineVendor.textContent = '0x2A3C (TRINAMIC)';
        if (machineProductId) machineProductId.textContent = '0x0100';
        if (machineSerial) machineSerial.textContent = 'TMCSTEP';
    },

    /**
     * Update machine information from device data
     * @param {Object} deviceInfo - Device information object
     */
    updateMachineInfoFromData: function(deviceInfo) {
        const machinePort = document.getElementById('machine-port');
        const machineVendor = document.getElementById('machine-vendor');
        const machineProductId = document.getElementById('machine-product-id');
        const machineSerial = document.getElementById('machine-serial');
        
        if (machinePort) machinePort.textContent = deviceInfo.port || 'N/A';
        
        // Customize the vendor display for TRINAMIC devices
        if (machineVendor) {
            if (deviceInfo.vendor_id && deviceInfo.vendor_id.toLowerCase() === '0x2a3c') {
                machineVendor.textContent = `${deviceInfo.vendor_id} (TRINAMIC)`;
            } else {
                machineVendor.textContent = deviceInfo.vendor_id || 'N/A';
                if (deviceInfo.manufacturer && deviceInfo.manufacturer !== 'N/A') {
                    machineVendor.textContent += ` (${deviceInfo.manufacturer})`;
                }
            }
        }
        
        if (machineProductId) machineProductId.textContent = deviceInfo.product_id || 'N/A';
        if (machineSerial) machineSerial.textContent = deviceInfo.serial_number || 'N/A';
    },

    /**
     * Fetch machine statistics
     */
    fetchMachineStats: function() {
        // Get the stats card (no loading state will be added)
        const statsCard = document.getElementById('machine-stats-card');
        
        fetch('/get_machine_stats/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'port': ConnectionManager.getActiveMachinePort()
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received machine stats data:', data);
            
            if (data.status === 'success') {
                // Use the data directly from the response
                this.updateMachineStatsUI(data.data);
            } else {
                console.error(`Error fetching machine stats: ${data.message}`);
                NotificationManager.showNotification('Failed to fetch machine stats', 'error');
            }
        })
        .catch(error => {
            console.error('Error fetching machine stats:', error);
            NotificationManager.showNotification('Network error while fetching machine stats', 'error');
        });
    },

    /**
     * Update machine stats UI with placeholder data for disconnected state
     */
    updateMachineStatsUIPlaceholders: function() {
        // System gauge placeholders
        ChartManager.updateMachineGauge('voltage-value', null, 0, 50, 'V', null, true);
        ChartManager.updateMachineGauge('temp-value', null, 0, 100, '°C', null, true);
        
        // Motor placeholders for all three motors
        for (let i = 0; i < 3; i++) {
            // Update gauges with placeholder data
            ChartManager.updateMachineGauge(`motor${i}-speed-value`, null, 0, 1000, 'RPM', null, true);
            ChartManager.updateMachineGauge(`motor${i}-current-value`, null, 0, 2500, 'mA', null, true);
            
            // Update position display with placeholder
            ChartManager.updatePositionDisplay(`motor${i}-position`, 'N/A', true);
            
            // Update motor state indicator to show disconnected
            ChartManager.updateMotorStateIndicator(`motor${i}-state`, 'disconnected');
        }
        
        // Update connection status badge to show disconnected
        const statsConnectionStatus = document.getElementById('stats-connection-status');
        if (statsConnectionStatus) {
            statsConnectionStatus.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
            statsConnectionStatus.className = 'status-badge critical';
        }

        // Add tooltips to disconnected elements
        UIManager.addDisconnectedTooltips();
    },

    /**
     * Update machine stats UI with actual data
     * @param {Object} stats - Machine statistics object
     */
    updateMachineStatsUI: function(stats) {
        try {
            // Check if the data is valid
            if (!stats || typeof stats !== 'object') {
                console.error('Invalid machine stats data:', stats);
                return;
            }

            console.log('Updating machine stats UI with data:', stats);
            
            // Update voltage (directly from flat structure)
            if (stats.voltage !== undefined) {
                ChartManager.updateMachineGauge('voltage-value', stats.voltage, 0, 50, 'V', [
                    { percentage: 33, color: '#ff453a' },  // Low voltage (red)
                    { percentage: 66, color: '#ffcc00' },  // Medium voltage (yellow)
                    { percentage: 100, color: '#30d158' }  // High voltage (green)
                ]);
            }
            
            // Update temperature (directly from flat structure)
            if (stats.temperature !== undefined) {
                // Divide by 100 if temperature is above 1000 (assuming it's in millidegrees)
                const tempValue = stats.temperature > 1000 ? stats.temperature / 100 : stats.temperature;
                ChartManager.updateMachineGauge('temp-value', tempValue, 0, 100, '°C', [
                    { percentage: 50, color: '#30d158' },  // Normal temp (green)
                    { percentage: 75, color: '#ffcc00' },  // Warm temp (yellow)
                    { percentage: 100, color: '#ff453a' }  // Hot temp (red)
                ]);
            }
            
            // Update motor data (loop through 3 motors)
            for (let i = 0; i < 3; i++) {
                // Check if motor data exists for this index
                if (stats[`motor${i}_speed`] !== undefined) {
                    // Update speed gauge
                    ChartManager.updateMachineGauge(`motor${i}-speed-value`, stats[`motor${i}_speed`], 0, 1000, 'RPM', [
                        { percentage: 33, color: '#30d158' },  // Low speed (green)
                        { percentage: 66, color: '#ffcc00' },  // Medium speed (yellow)
                        { percentage: 100, color: '#ff453a' }  // High speed (red)
                    ]);
                }
                
                if (stats[`motor${i}_current`] !== undefined) {
                    // Update current gauge
                    ChartManager.updateMachineGauge(`motor${i}-current-value`, stats[`motor${i}_current`], 0, 2500, 'mA', [
                        { percentage: 33, color: '#30d158' },  // Low current (green)
                        { percentage: 66, color: '#ffcc00' },  // Medium current (yellow)
                        { percentage: 100, color: '#ff453a' }  // High current (red)
                    ]);
                }
                
                if (stats[`motor${i}_position`] !== undefined) {
                    // Update position display
                    ChartManager.updatePositionDisplay(`motor${i}-position`, stats[`motor${i}_position`]);
                }
                
                if (stats[`motor${i}_state`] !== undefined) {
                    // Update motor state indicator
                    ChartManager.updateMotorStateIndicator(`motor${i}-state`, stats[`motor${i}_state`]);
                }
            }
            
            // Update connection status indicator
            const statsConnectionStatus = document.getElementById('stats-connection-status');
            if (statsConnectionStatus) {
                statsConnectionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
                statsConnectionStatus.className = 'status-badge operational';
            }
        } catch (error) {
            console.error('Error updating machine stats UI:', error);
        }
    },

    /**
     * Refreshes the machine statistics by fetching the latest data
     * @param {boolean} showLoading - Whether to show loading animation during refresh
     */
    refreshMachineStats: function(showLoading = true) {
        // Fetch the latest machine stats
        fetch('/get_machine_stats/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'com_port': ConnectionManager.getActiveMachinePort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update the UI with the new stats
                this.updateMachineStatsUI(data.machine_stats);
                
                // If relay states are included, update those too
                if (data.relay_states) {
                    RelayControls.updateRelayStatesUI(data.relay_states);
                }
                
                console.log('Machine stats refreshed successfully');
                NotificationManager.showNotification('Machine stats updated', 'success');
            } else {
                console.error('Failed to refresh machine stats:', data.message);
                NotificationManager.showNotification('Failed to update machine stats', 'error');
            }
        })
        .catch(error => {
            console.error('Error fetching machine stats:', error);
            NotificationManager.showNotification('Error updating machine stats', 'error');
        });
    }
};

// Create namespace for SMA Machine control functions
const SMAControls = {
    // State tracking
    isConnected: false,
    connectionPort: 'COM3',
    baudrate: 9600,
    address: 1,
    
    // Motor configurations
    motorConfigs: {
        0: { // Shutter motor
            speed: 100,
            current: 200,
            acceleration: 500,
            resolution: 2
        },
        1: { // Film motor
            speed: 100,
            current: 200,
            acceleration: 500,
            resolution: 2
        }
    },

    // Continuous movement tracking
    continuousMovement: {
        0: {
            interval: null,
            direction: 0,
            speed: 50,
            intervalMs: 100
        },
        1: {
            interval: null,
            direction: 0,
            speed: 50,
            intervalMs: 100
        }
    },

    /**
     * Connect to the Trinamic controller
     */
    connect: function(port = null, baudrate = null, address = null) {
        const connectData = {
            port: port || this.connectionPort,
            baudrate: baudrate || this.baudrate,
            address: address || this.address
        };

        console.log(`Connecting to Trinamic controller on ${connectData.port}...`);

        fetch('/trinamic/connect/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(connectData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.isConnected = true;
                this.connectionPort = connectData.port;
                this.updateConnectionStatus(true);
                NotificationManager.showNotification(`Connected to Trinamic controller on ${connectData.port}`, 'success');
                this.refreshStatus();
            } else {
                console.error(`Connection failed: ${data.message}`);
                NotificationManager.showNotification(`Connection failed: ${data.message}`, 'error');
                this.updateConnectionStatus(false);
            }
        })
        .catch(error => {
            console.error('Connection error:', error);
            NotificationManager.showNotification('Network error during connection', 'error');
            this.updateConnectionStatus(false);
        });
    },

    /**
     * Disconnect from the Trinamic controller
     */
    disconnect: function() {
        console.log('Disconnecting from Trinamic controller...');

        fetch('/trinamic/disconnect/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                NotificationManager.showNotification('Disconnected from Trinamic controller', 'info');
                this.clearStatus();
            } else {
                console.error(`Disconnect failed: ${data.message}`);
                NotificationManager.showNotification(`Disconnect failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Disconnect error:', error);
            NotificationManager.showNotification('Network error during disconnect', 'error');
        });
    },

    /**
     * Control I/O devices (vacuum, LED, magnet, sensors)
     */
    controlIO: function(device, action) {
        if (!this.isConnected) {
            NotificationManager.showNotification('Not connected to Trinamic controller', 'warning');
            return;
        }

        console.log(`I/O Control: ${device} ${action}`);

        const requestData = {
            device: device,
            action: action
        };

        fetch('/trinamic/io/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const message = `${device.toUpperCase()} ${action}: ${data.message}`;
                NotificationManager.showNotification(message, 'success');
                this.updateIOStatus(device, action, data.data);
            } else {
                console.error(`I/O control failed: ${data.message}`);
                NotificationManager.showNotification(`I/O control failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('I/O control error:', error);
            NotificationManager.showNotification('Network error during I/O control', 'error');
        });
    },

    /**
     * Control motors (move, stop, home, configure)
     */
    controlMotor: function(motor, action, parameters = {}) {
        if (!this.isConnected) {
            NotificationManager.showNotification('Not connected to Trinamic controller', 'warning');
            return;
        }

        console.log(`Motor Control: Motor ${motor} ${action}`, parameters);

        const requestData = {
            motor: motor,
            action: action,
            ...parameters
        };

        fetch('/trinamic/motor/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const message = `Motor ${motor} ${action}: ${data.message}`;
                NotificationManager.showNotification(message, 'success');
                this.updateMotorStatus(motor, action, data.data);
            } else {
                console.error(`Motor control failed: ${data.message}`);
                NotificationManager.showNotification(`Motor control failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Motor control error:', error);
            NotificationManager.showNotification('Network error during motor control', 'error');
        });
    },

    /**
     * Emergency stop all motors
     */
    emergencyStop: function() {
        console.log('EMERGENCY STOP TRIGGERED');

        // Immediately stop all continuous movements
        this.stopAllContinuousMovement();

        fetch('/trinamic/emergency_stop/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                NotificationManager.showNotification('EMERGENCY STOP ACTIVATED', 'warning');
                this.refreshStatus();
            } else {
                console.error(`Emergency stop failed: ${data.message}`);
                NotificationManager.showNotification(`Emergency stop failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Emergency stop error:', error);
            NotificationManager.showNotification('Network error during emergency stop', 'error');
        });
    },

    /**
     * Configure motor parameters
     */
    configureMotors: function(configurations) {
        if (!this.isConnected) {
            NotificationManager.showNotification('Not connected to Trinamic controller', 'warning');
            return;
        }

        console.log('Configuring motors:', configurations);

        fetch('/trinamic/configure/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ motors: configurations })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                NotificationManager.showNotification('Motor configuration applied', 'success');
                // Update local configurations
                Object.assign(this.motorConfigs, configurations);
                this.refreshStatus();
            } else {
                console.error(`Configuration failed: ${data.message}`);
                NotificationManager.showNotification(`Configuration failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Configuration error:', error);
            NotificationManager.showNotification('Network error during configuration', 'error');
        });
    },

    /**
     * Refresh system status
     */
    refreshStatus: function() {
        if (!this.isConnected) {
            this.clearStatus();
            return;
        }

        fetch('/trinamic/system_status/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.updateSystemStatus(data.data);
            } else {
                console.error(`Status refresh failed: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Status refresh error:', error);
        });
    },

    /**
     * Update connection status UI
     */
    updateConnectionStatus: function(connected) {
        const statusElement = document.getElementById('sma-connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
                statusElement.className = 'status-badge operational';
            } else {
                statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
                statusElement.className = 'status-badge critical';
            }
        }

        // Update connect/disconnect button states
        const connectBtn = document.getElementById('sma-connect-btn');
        const disconnectBtn = document.getElementById('sma-disconnect-btn');
        
        if (connectBtn) connectBtn.disabled = connected;
        if (disconnectBtn) disconnectBtn.disabled = !connected;
    },

    /**
     * Update I/O status displays
     */
    updateIOStatus: function(device, action, data) {
        // Update vacuum status
        if (device === 'vacuum') {
            const vacuumStatus = document.getElementById('sma-vacuum-status');
            if (vacuumStatus && data) {
                if (action === 'status') {
                    vacuumStatus.textContent = data.vacuum_ok ? 'OK' : 'Not OK';
                    vacuumStatus.className = data.vacuum_ok ? 'status-good' : 'status-error';
                } else {
                    vacuumStatus.textContent = action === 'on' ? 'ON' : 'OFF';
                    vacuumStatus.className = action === 'on' ? 'status-good' : 'status-neutral';
                }
            }
        }

        // Update LED status
        if (device === 'led') {
            const ledStatus = document.getElementById('sma-led-status');
            if (ledStatus) {
                ledStatus.textContent = action === 'on' ? 'ON' : 'OFF';
                ledStatus.className = action === 'on' ? 'status-good' : 'status-neutral';
            }
        }

        // Update magnet status
        if (device === 'magnet') {
            const magnetStatus = document.getElementById('sma-magnet-status');
            if (magnetStatus) {
                magnetStatus.textContent = action === 'on' ? 'ON' : 'OFF';
                magnetStatus.className = action === 'on' ? 'status-good' : 'status-neutral';
            }
        }

        // Update sensor readings
        if (device === 'light_sensor' && data) {
            const lightSensorValue = document.getElementById('sma-light-sensor-value');
            if (lightSensorValue) {
                lightSensorValue.textContent = data.light_sensor_value || 'N/A';
            }
        }

        if (device === 'machine_state' && data) {
            const machineStateValue = document.getElementById('sma-machine-state');
            if (machineStateValue) {
                machineStateValue.textContent = data.state || 'UNKNOWN';
                machineStateValue.className = data.lid_closed ? 'status-good' : 'status-warning';
            }
        }
    },

    /**
     * Update motor status displays
     */
    updateMotorStatus: function(motor, action, data) {
        const motorStatusElement = document.getElementById(`sma-motor-${motor}-status`);
        if (motorStatusElement) {
            if (action === 'status' && data) {
                motorStatusElement.textContent = data.running ? 'RUNNING' : 'STOPPED';
                motorStatusElement.className = data.running ? 'status-warning' : 'status-good';
            } else if (action === 'stop') {
                motorStatusElement.textContent = 'STOPPED';
                motorStatusElement.className = 'status-good';
            }
        }
    },

    /**
     * Update comprehensive system status
     */
    updateSystemStatus: function(statusData) {
        if (!statusData || !statusData.success) return;

        // Update machine state
        if (statusData.machine_state) {
            this.updateIOStatus('machine_state', 'get', statusData.machine_state);
        }

        // Update vacuum status
        if (statusData.vacuum_status) {
            this.updateIOStatus('vacuum', 'status', statusData.vacuum_status);
        }

        // Update zero point status
        if (statusData.zero_point) {
            const zeroPointElement = document.getElementById('sma-zero-point-status');
            if (zeroPointElement) {
                zeroPointElement.textContent = statusData.zero_point.at_zero_point ? 'AT ZERO' : 'NOT AT ZERO';
                zeroPointElement.className = statusData.zero_point.at_zero_point ? 'status-good' : 'status-neutral';
            }
        }

        // Update light sensor
        if (statusData.light_sensor) {
            this.updateIOStatus('light_sensor', 'read', statusData.light_sensor);
        }

        // Update motor statuses
        if (statusData.motor_statuses) {
            for (const [motorKey, motorData] of Object.entries(statusData.motor_statuses)) {
                const motorNumber = motorKey.split('_')[1];
                this.updateMotorStatus(parseInt(motorNumber), 'status', motorData);
            }
        }
    },

    /**
     * Clear all status displays
     */
    clearStatus: function() {
        // Clear I/O statuses
        const ioElements = ['sma-vacuum-status', 'sma-led-status', 'sma-magnet-status', 
                           'sma-light-sensor-value', 'sma-machine-state', 'sma-zero-point-status'];
        
        ioElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = 'N/A';
                element.className = 'status-neutral';
            }
        });

        // Clear motor statuses
        for (let i = 0; i < 2; i++) {
            const motorStatusElement = document.getElementById(`sma-motor-${i}-status`);
            if (motorStatusElement) {
                motorStatusElement.textContent = 'N/A';
                motorStatusElement.className = 'status-neutral';
            }
        }
    },

    /**
     * Start continuous movement (joystick style)
     */
    startContinuousMovement: function(motor, direction) {
        if (!this.isConnected) {
            NotificationManager.showNotification('Not connected to Trinamic controller', 'warning');
            return;
        }

        // Stop any existing movement for this motor
        this.stopContinuousMovement(motor);

        // Get settings from UI
        const speedElement = document.getElementById(`motor${motor}-continuous-speed`);
        const intervalElement = document.getElementById(`motor${motor}-continuous-interval`);
        
        const speed = speedElement ? parseInt(speedElement.value) : 50;
        const intervalMs = intervalElement ? parseInt(intervalElement.value) : 100;

        // Update tracking
        this.continuousMovement[motor].direction = direction;
        this.continuousMovement[motor].speed = speed;
        this.continuousMovement[motor].intervalMs = intervalMs;

        console.log(`Starting continuous movement: Motor ${motor}, Direction ${direction}, Speed ${speed}, Interval ${intervalMs}ms`);

        // Add active class to the button
        const buttons = document.querySelectorAll(`.joystick-controls .control-button.joystick`);
        buttons.forEach(btn => {
            if (btn.getAttribute('onmousedown')?.includes(`(${motor}, ${direction})`)) {
                btn.classList.add('active');
            }
        });

        // Start the interval
        this.continuousMovement[motor].interval = setInterval(() => {
            this.controlMotor(motor, 'move', {
                steps: speed,
                direction: direction
            });
        }, intervalMs);

        // Provide haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
    },

    /**
     * Stop continuous movement
     */
    stopContinuousMovement: function(motor) {
        if (this.continuousMovement[motor].interval) {
            clearInterval(this.continuousMovement[motor].interval);
            this.continuousMovement[motor].interval = null;
            console.log(`Stopped continuous movement for motor ${motor}`);
        }

        // Remove active class from all joystick buttons for this motor
        const buttons = document.querySelectorAll(`.joystick-controls .control-button.joystick`);
        buttons.forEach(btn => {
            if (btn.getAttribute('onmousedown')?.includes(`(${motor},`)) {
                btn.classList.remove('active');
            }
        });

        // Stop the motor
        if (this.isConnected) {
            this.controlMotor(motor, 'stop', {});
        }
    },

    /**
     * Stop all continuous movements (emergency)
     */
    stopAllContinuousMovement: function() {
        console.log('Stopping all continuous movements');
        for (let motor = 0; motor <= 1; motor++) {
            this.stopContinuousMovement(motor);
        }
    },

    /**
     * Execute motor command with current settings
     */
    executeMotorCommand: function(motor) {
        if (!this.isConnected) {
            NotificationManager.showNotification('Not connected to Trinamic controller', 'warning');
            return;
        }

        // Get all current settings from UI
        const speed = parseInt(document.getElementById(`motor${motor}-speed`).value);
        const current = parseInt(document.getElementById(`motor${motor}-current`).value);
        const standbyCurrent = parseInt(document.getElementById(`motor${motor}-standby-current`).value);
        const acceleration = parseInt(document.getElementById(`motor${motor}-acceleration`).value);
        const steps = parseInt(document.getElementById(`motor${motor}-steps`).value);
        const directionToggle = document.getElementById(`motor${motor}-direction`).checked;
        const direction = directionToggle ? 1 : -1; // Forward = 1, Backward = -1
        
        // Get selected resolution
        const resolutionRadios = document.querySelectorAll(`input[name="motor${motor}-resolution"]:checked`);
        const resolution = resolutionRadios.length > 0 ? parseInt(resolutionRadios[0].value) : 4;

        console.log(`Executing motor ${motor} command: Speed=${speed}, Current=${current}, Standby Current=${standbyCurrent}, Acceleration=${acceleration}, Steps=${steps}, Direction=${direction}, Resolution=${resolution}`);

        // Set all motor parameters first
        Promise.all([
            fetch('/trinamic/motor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    motor: motor,
                    action: 'set_speed',
                    speed: speed
                })
            }),
            fetch('/trinamic/motor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    motor: motor,
                    action: 'set_current',
                    current: current
                })
            }),
            fetch('/trinamic/motor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    motor: motor,
                    action: 'set_standby_current',
                    standby_current: standbyCurrent
                })
            }),
            fetch('/trinamic/motor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    motor: motor,
                    action: 'set_acceleration',
                    acceleration: acceleration
                })
            }),
            fetch('/trinamic/motor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    motor: motor,
                    action: 'set_resolution',
                    resolution: resolution
                })
            })
        ])
        .then(responses => Promise.all(responses.map(r => r.json())))
        .then(results => {
            // Check if all parameters were set successfully
            const allSuccess = results.every(result => result.status === 'success');
            
            if (!allSuccess) {
                NotificationManager.showNotification('Failed to configure motor settings', 'error');
                return;
            }

            // Now execute the movement
            return this.controlMotor(motor, 'move', {
                steps: steps,
                direction: direction
            });
        })
        .catch(error => {
            console.error('Motor command error:', error);
            NotificationManager.showNotification('Error executing motor command', 'error');
        });
    },

    /**
     * Update direction toggle text
     */
    updateDirectionToggle: function(motor) {
        const toggle = document.getElementById(`motor${motor}-direction`);
        const text = document.querySelector(`#motor${motor}-direction + .toggle-label + .toggle-text`);
        
        if (toggle && text) {
            text.textContent = toggle.checked ? 'Forward' : 'Backward';
        }
    },

    /**
     * Cleanup connections and stop all operations
     */
    cleanup: function() {
        console.log('SMA Controls cleanup initiated');
        
        // Stop all continuous movements
        this.stopAllContinuousMovement();
        
        // Disconnect if connected
        if (this.isConnected) {
            // Use sendBeacon for reliable cleanup during page unload
            const data = JSON.stringify({});
            const blob = new Blob([data], {type: 'application/json'});
            
            try {
                navigator.sendBeacon('/trinamic/disconnect/', blob);
                console.log('Cleanup disconnect sent via beacon');
            } catch (e) {
                // Fallback for older browsers
                fetch('/trinamic/disconnect/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: data,
                    keepalive: true
                }).catch(() => {
                    // Ignore errors during cleanup
                });
            }
            
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    },

    /**
     * Initialize SMA controls
     */
    initialize: function() {
        console.log('Initializing SMA Controls...');
        this.updateConnectionStatus(false);
        this.clearStatus();
        
        // Add global event listeners for safety
        document.addEventListener('keydown', (e) => {
            // Stop all continuous movement on ESC key
            if (e.key === 'Escape') {
                this.stopAllContinuousMovement();
                NotificationManager.showNotification('Emergency stop: All continuous movements stopped', 'warning');
            }
        });

        // Stop continuous movement if the window loses focus
        window.addEventListener('blur', () => {
            this.stopAllContinuousMovement();
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Cleanup on page hide (mobile/tab switching)
        window.addEventListener('pagehide', () => {
            this.cleanup();
        });

        // Add event listeners for direction toggles
        for (let motor = 0; motor <= 1; motor++) {
            const toggle = document.getElementById(`motor${motor}-direction`);
            if (toggle) {
                toggle.addEventListener('change', () => {
                    this.updateDirectionToggle(motor);
                });
                // Set initial text
                this.updateDirectionToggle(motor);
            }
        }
    }
};

// Initialize SMA Controls when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof SMAControls !== 'undefined') {
        SMAControls.initialize();
    }
});