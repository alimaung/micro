/**
 * relay_controls.js - Relay control functions for microfilm system
 * Handles operations related to controlling the relay system
 */

// Create namespace for relay control functions
const RelayControls = {
    // State tracking
    isLightMode: true,
    relayStates: {},
    pendingRelayStates: {},
    
    /**
     * Toggle relay operation mode (light/dark)
     */
    // Replace toggleRelayMode function
    toggleRelayMode: function() {
        if (!ConnectionManager.isRelayConnected) {
            NotificationManager.showNotification('Relay not connected', 'error');
            return;
        }
        
        // Toggle the mode
        this.isLightMode = !this.isLightMode;
        const targetMode = this.isLightMode ? 'light' : 'dark';
        console.log(`Toggling relay mode to ${targetMode}`);
        
        // Update UI to show the transition is happening
        const modeIndicator = document.getElementById('mode-indicator');
        if (modeIndicator) {
            modeIndicator.style.transform = 'scale(0.8)';
            modeIndicator.style.opacity = '0.7';
        }
        
        Utils.sendRelayAction(
            { action: targetMode },
            '/control_relay/',
            {
                'action': targetMode,
                'com_port': ConnectionManager.getActiveRelayPort()
            }
        )
        .then((data) => {
            console.log("Relay data:", data)
            if (data.status === 'success') {
                UIManager.updateModeDisplay(data.mode || targetMode);
                NotificationManager.showNotification(`${targetMode.charAt(0).toUpperCase() + targetMode.slice(1)} mode activated`, 'success');

                // Reset indicator
                if (modeIndicator) {
                    modeIndicator.style.transform = 'scale(1)';
                    modeIndicator.style.opacity = '1';
                }                    
                // Toggle UI States manually
                if (targetMode === 'dark') {
                    // For dark mode: turn on relays 2, 3, 4
                    this.setRelayIndicatorState(2, true);
                    this.setRelayIndicatorState(3, true);
                    this.setRelayIndicatorState(4, true);
                    
                    // Flash relay 1 briefly
                    this.setRelayIndicatorState(1, true);
                    setTimeout(() => {
                        this.setRelayIndicatorState(1, false);
                    }, 500); // Flash for 500ms
                } else if (targetMode === 'light') {
                    // For light mode: turn off relays 2, 3, 4
                    this.setRelayIndicatorState(2, false);
                    this.setRelayIndicatorState(3, false);
                    this.setRelayIndicatorState(4, false);
                    
                    // Flash relay 1 briefly
                    this.setRelayIndicatorState(1, true);
                    setTimeout(() => {
                        this.setRelayIndicatorState(1, false);
                    }, 500); // Flash for 500ms
                }

                // Toggle UI States with actual state checks
                /* setTimeout(() => {
                    this.checkRelayStates();
                }, 50);
                setTimeout(() => {
                    this.checkRelayStates();
                }, 700); */
            } else {
                console.error(`Error: ${data.message}`);
                NotificationManager.showNotification('Error toggling mode', 'error');
                
                // Revert state change since it failed
                this.isLightMode = !this.isLightMode;
                
                // Reset indicator without animation
                if (modeIndicator) {
                    modeIndicator.style.transform = 'scale(1)';
                    modeIndicator.style.opacity = '1';
                }                
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            NotificationManager.showNotification('Network error', 'error');
            
            // Revert state change since it failed
            this.isLightMode = !this.isLightMode;
            
            // Reset indicator without animation
            if (modeIndicator) {
                modeIndicator.style.transform = 'scale(1)';
                modeIndicator.style.opacity = '1';
                modeIndicator.classList.remove('loading');
            }
        });
    },
    
    /**
     * Toggle a specific relay
     * @param {number} relayNum - The relay number to toggle
     */
    toggleRelay: function(relayNum) {
        if (!ConnectionManager.isRelayConnected) {
            NotificationManager.showNotification('Relay not connected', 'error');
            return;
        }
        
        // Find the relay indicator to determine current state
        const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
        if (!relayIndicator) return;
        
        // Determine current state and target action
        const isCurrentlyOn = relayIndicator.classList.contains('on');
        const action = isCurrentlyOn ? 'off' : 'on';
        
        console.log(`Toggling relay ${relayNum} to ${action}`);
        
        // Add loading state to the relay button
        const relayButton = relayIndicator.closest('.relay-toggle');
        if (relayButton) {
            relayButton.disabled = true;
            relayButton.classList.add('loading');
        }
        
        Utils.sendRelayAction(
            { 
                action: "set",
                relay: parseInt(relayNum),
                state: !isCurrentlyOn
            },
            '/control_relay/',
            { 
                action: action,
                relay: relayNum, 
                com_port: ConnectionManager.getActiveRelayPort() 
            }
        )
        .then((data) => {
            if (data.status === 'success' || data.type === 'relay') {
                // If server returned relay states, update UI
                console.log('Relay states:', data);
                
                // Check for both direct relay_states and nested response format
                if (data.relay_states) {
                    this.updateRelayStatesUI(data.relay_states);
                } else if (data.response && data.response.relay) {
                    // This is the case where we're getting a single relay update
                    // We need to update just this specific relay
                    const newState = data.response.state === true || data.response.state === 1;
                    this.setRelayIndicatorState(data.response.relay, newState, false);
                    
                    // If this is relay 8 (machine power), verify machine state
                    if (parseInt(data.response.relay) === 8) {
                        // Allow time for the machine state to change
                        setTimeout(() => {
                            MachineControls.checkMachinePowerState();
                        }, 1000);
                    }
                } else {
                    // Fallback to just updating this relay
                    const newState = action === 'on';
                    this.setRelayIndicatorState(relayNum, newState, false);
                }
                
                NotificationManager.showNotification(`Relay ${relayNum} turned ${action.toUpperCase()}`, 'success');
            } else {
                NotificationManager.showNotification(`Failed to control relay: ${data.message}`, 'error');
                console.error(`Error controlling relay: ${data.message}`);
            }
        })
        .catch((error) => {
            NotificationManager.showNotification('Error controlling relay', 'error');
            console.error('Error controlling relay:', error);
        })
        .finally(() => {
            // Remove loading state
            if (relayButton) {
                relayButton.disabled = false;
                relayButton.classList.remove('loading');
            }
        });
    },
    
    /**
     * Check current relay states
     */
    checkRelayStates: function() {
        if (!ConnectionManager.isRelayConnected) return;
        
        console.log("Checking relay states...");
        
        Utils.sendRelayAction(
            { action: 'status' },
            '/get_all_states/',
            {}
        )
        .then((data) => {
            // Handle light/dark mode toggle
            if (data.status === 'success' && data.states) {
                // Update relay states if available
                if (data.data.relay_states) {
                    // Compare with current states before updating
                    const hasChanges = Object.entries(data.data.relay_states).some(([key, value]) => {
                        console.log(`Comparing relay ${key}: current=${this.relayStates[key]}, new=${value}`);
                        const changed = this.relayStates[key] !== value;
                        if (changed) {
                            console.log(`Relay ${key} state changed: ${this.relayStates[key]} -> ${value}`);
                        }
                        return changed;
                    });
                    
                    if (hasChanges) {
                        console.log("Changes detected in relay states, updating UI");
                        // Only update UI if there are actual changes
                        Object.assign(this.relayStates, data.data.relay_states);
                        this.updateRelayStatesUI(data.data.relay_states);
                        console.log("Relay states updated due to changes detected");
                    } else {
                        console.log("No changes in relay states, skipping UI update");
                    }
                } else {
                    console.log("No relay_states found in response data");
                }
                
                // Update system stats if available
                if (data.data.system_stats) {
                    Utils.updateESP32StatsUI(data.data.system_stats);
                }
            
            // Handle relay states
            } else if (data.type === 'relays') {
                console.log("Received relay data with type 'relays':", data);
                console.log("Relay states from WebSocket:", JSON.stringify(data.states));
                this.updateRelayStatesUI(data.states);
                
                if (data.current_mode) {
                    console.log("Current mode detected in response:", data.current_mode);
                    UIManager.updateModeDisplay(data.current_mode);
                } else {
                    console.log("No current_mode found in relay response");
                }
            } else {
                console.error(`Error or missing data: ${data.message || 'Unknown error'}`);
            }
        })
        .catch((error) => {
            console.error('Error checking states:', error);
        });
    },
    
    /**
     * Update relay states in the UI
     * @param {Object} newRelayStates - Object containing relay states
     */
    updateRelayStatesUI: function(newRelayStates) {
        console.log("Updating relay states UI:", newRelayStates);
        
        // Loop through relays using zero-based indexing (0-7)
        for (let relayIndex = 0; relayIndex < 8; relayIndex++) {
            // Convert to 1-based for UI elements 
            const relayNum = relayIndex + 1;
            
            // Skip if this relay state is not in the array or undefined
            if (relayIndex >= newRelayStates.length || newRelayStates[relayIndex] === undefined) continue;
            
            // Get the current state from the UI (UI still uses 1-based numbering)
            const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
            if (!relayIndicator) continue;
            
            const isCurrentlyOnInUI = relayIndicator.classList.contains('on');
            const shouldBeOn = newRelayStates[relayIndex] === true || newRelayStates[relayIndex] === 1;
            
            // Check if this relay is pending a state change (pendingRelayStates might use 1-based keys)
            const isPending = this.pendingRelayStates[relayNum] !== undefined;
            
            // If the UI doesn't match the new state, update it
            if (isCurrentlyOnInUI !== shouldBeOn || isPending) {
                console.log(`Updating relay ${relayNum} UI: ${isCurrentlyOnInUI} -> ${shouldBeOn} (was pending: ${isPending})`);
                
                // Clear pending state
                if (isPending) {
                    delete this.pendingRelayStates[relayNum];
                }
                
                // Update the indicator (still using 1-based numbering for UI)
                this.setRelayIndicatorState(relayNum, shouldBeOn, false);
                
                // If this is relay 8 (machine power), verify machine state
                if (relayIndex === 7) { // Index 7 corresponds to relay #8
                    // Allow time for the machine state to change
                    setTimeout(() => {
                        MachineControls.checkMachinePowerState();
                    }, 1000);
                }
            }
        }
    },
    
    /**
     * Clear relay information display
     */
    clearRelayInfo: function() {
        const relayPort = document.getElementById('relay-port');
        const relayVendor = document.getElementById('relay-vendor');
        const relayProductId = document.getElementById('relay-product-id');
        const relayProduct = document.getElementById('relay-product');
        
        if (relayPort) relayPort.textContent = 'N/A';
        if (relayVendor) relayVendor.textContent = 'N/A';
        if (relayProductId) relayProductId.textContent = 'N/A';
        if (relayProduct) relayProduct.textContent = 'N/A';
    },
    
    /**
     * Update relay information display
     * @param {string} port - The COM port to display
     */
    updateRelayInfo: function(port) {
        const relayPort = document.getElementById('relay-port');
        const relayVendor = document.getElementById('relay-vendor');
        const relayProductId = document.getElementById('relay-product-id');
        const relayProduct = document.getElementById('relay-product');
        
        if (relayPort) relayPort.textContent = port;
        if (relayVendor) relayVendor.textContent = '0x1A86 (Qinheng)';
        if (relayProductId) relayProductId.textContent = '0x7523';
        if (relayProduct) relayProduct.textContent = 'USB-SERIAL CH340';
    },
    
    /**
     * Update relay information from device data
     * @param {Object} deviceInfo - Device information object
     */
    updateRelayInfoFromData: function(deviceInfo) {
        const relayPort = document.getElementById('relay-port');
        const relayVendor = document.getElementById('relay-vendor');
        const relayProductId = document.getElementById('relay-product-id');
        const relayProduct = document.getElementById('relay-product');
        
        if (relayPort) relayPort.textContent = deviceInfo.port || 'N/A';
        
        // Customize the vendor display for Qinheng devices
        if (relayVendor) {
            if (deviceInfo.vendor_id && deviceInfo.vendor_id.toLowerCase() === '0x1a86') {
                relayVendor.textContent = `${deviceInfo.vendor_id} (Qinheng)`;
            } else {
                relayVendor.textContent = deviceInfo.vendor_id || 'N/A';
                if (deviceInfo.manufacturer && deviceInfo.manufacturer !== 'N/A') {
                    relayVendor.textContent += ` (${deviceInfo.manufacturer})`;
                }
            }
        }
        
        if (relayProductId) relayProductId.textContent = deviceInfo.product_id || 'N/A';
        if (relayProduct) relayProduct.textContent = deviceInfo.product || 'N/A';
    },
    
    /**
     * Set relay indicator state in the UI
     * @param {number} relayNum - The relay number
     * @param {boolean} isOn - Whether the relay is on
     * @param {boolean} pending - Whether the state change is pending
     */
    setRelayIndicatorState: function(relayNum, isOn, pending = false) {
        // Make sure relayNum is correctly handled as a number
        const relayId = parseInt(relayNum, 10);
        const relayIndicator = document.getElementById(`relay-indicator-${relayId}`);
        
        console.log(`Setting relay ${relayId} indicator to ${isOn ? 'ON' : 'OFF'}${pending ? ' (pending)' : ''}`);
        
        // Store state with string key
        this.relayStates[relayId.toString()] = isOn;
        
        // Set visual state
        if (pending) {
            // Store in pending states
            this.pendingRelayStates[relayId.toString()] = isOn;
            
            // Add pending visual state (pulsing)
            relayIndicator.style.animation = 'pulse 1.5s infinite';
            relayIndicator.style.opacity = '0.7';
        } else {
            // Remove pending visual state
            relayIndicator.style.animation = '';
            relayIndicator.style.opacity = '1';
            
            // Remove from pending states if it was there
            delete this.pendingRelayStates[relayId.toString()];
        }
        
        // Set on/off state via class
        if (isOn) {
            relayIndicator.classList.add('on');
            relayIndicator.style.backgroundColor = '#30d158';
        } else {
            relayIndicator.classList.remove('on');
            relayIndicator.style.backgroundColor = '#ff453a';
        }
    }
}; 