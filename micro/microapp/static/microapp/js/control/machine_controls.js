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
        const action = intendedState ? 'machine_on' : 'machine_off';
        
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
                'com_port': ConnectionManager.getActiveRelayPort()
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