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
    buttonStates: {},
    
    /**
     * Initialize relay controls including event listeners
     */
    init: function() {
        // Add spacebar hotkey to switch back to light mode when in dark mode
        document.addEventListener('keydown', (event) => {
            // Check if spacebar is pressed and we're in dark mode
            if (event.key === ' ' && !this.isLightMode) {
                // Only toggle if we're not in an input field or if specifically called from development
                const activeElement = document.activeElement;
                const isInInput = activeElement && (
                    activeElement.tagName === 'INPUT' || 
                    activeElement.tagName === 'TEXTAREA' || 
                    activeElement.contentEditable === 'true'
                );
                
                // Allow toggle if not in input field, or if we're on the development page
                if (!isInInput || window.location.pathname.includes('/develop/')) {
                    this.toggleRelayMode();
                    // Prevent page scrolling
                    event.preventDefault();
                }
            }
        });
    },
    
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
                    // For dark mode: turn on relays 2, 3, 4 and turn off relay 5 (room light)
                    this.setRelayIndicatorState(2, true);
                    this.setRelayIndicatorState(3, true);
                    this.setRelayIndicatorState(4, true);
                    this.setRelayIndicatorState(5, false); // Room light OFF in dark mode
                    
                    // Flash relay 1 briefly
                    this.setRelayIndicatorState(1, true);
                    setTimeout(() => {
                        this.setRelayIndicatorState(1, false);
                    }, 500); // Flash for 500ms
                } else if (targetMode === 'light') {
                    // For light mode: turn off relays 2, 3, 4 and turn on relay 5 (room light)
                    this.setRelayIndicatorState(2, false);
                    this.setRelayIndicatorState(3, false);
                    this.setRelayIndicatorState(4, false);
                    this.setRelayIndicatorState(5, true); // Room light ON in light mode
                    
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
        
        // Add loading state to the relay button
        const relayButton = relayIndicator.closest('.relay-toggle');
        if (relayButton) {
            relayButton.disabled = true;
            relayButton.classList.add('loading');
        }

        // Special handling for relay 1 - always use pulse action
        if (parseInt(relayNum) === 1) {
            console.log("Pulsing relay 1");
            Utils.sendRelayAction(
                { 
                    action: "pulse",
                    relay: 1
                },
                '/control_relay/',
                { 
                    action: 'pulse',
                    relay: 1, 
                    com_port: ConnectionManager.getActiveRelayPort() 
                }
            )
            .then((data) => {
                // For relay 1, we always just do the pulse animation regardless of the response
                // Flash the indicator briefly
                this.setRelayIndicatorState(1, true);
                setTimeout(() => {
                    this.setRelayIndicatorState(1, false);
                }, 500); // Flash for 500ms
                
                NotificationManager.showNotification('Relay 1 pulsed', 'success');
            })
            .catch((error) => {
                NotificationManager.showNotification('Error pulsing relay', 'error');
                console.error('Error pulsing relay:', error);
            })
            .finally(() => {
                // Remove loading state
                if (relayButton) {
                    relayButton.disabled = false;
                    relayButton.classList.remove('loading');
                }
            });
            return;
        }
        
        // Regular handling for other relays
        // Determine current state and target action
        const isCurrentlyOn = relayIndicator.classList.contains('on');
        const action = isCurrentlyOn ? 'off' : 'on';
        
        console.log(`Toggling relay ${relayNum} to ${action}`);
        
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
                    
                    // Check for dark/light mode after toggling
                    this.detectAndUpdateCurrentMode();
                } else {
                    // Fallback to just updating this relay
                    const newState = action === 'on';
                    this.setRelayIndicatorState(relayNum, newState, false);
                    
                    // Check for dark/light mode after toggling
                    this.detectAndUpdateCurrentMode();
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
                
                // Determine mode from relays 2,3,4,5 states
                if (Array.isArray(data.states) && data.states.length >= 5) {
                    // Dark mode if relays 2,3,4 are all ON and relay 5 is OFF
                    const isDarkMode = data.states[1] && data.states[2] && data.states[3] && !data.states[4];
                    this.isLightMode = !isDarkMode;
                    UIManager.updateModeDisplay(isDarkMode ? 'dark' : 'light');
                }
            // NEW: Handle button events
            } else if (data.type === 'buttons') {
                console.log("Received button event data:", data);
                // Store button states
                if (Array.isArray(data.pressed)) {
                    this.buttonStates = data.pressed;
                    console.log("Button states updated:", this.buttonStates);
                }
                
                // Update relay states if provided
                if (Array.isArray(data.states)) {
                    this.updateRelayStatesUI(data.states);
                    
                    // Determine mode from relays 2,3,4,5 states
                    if (data.states.length >= 5) {
                        // Dark mode if relays 2,3,4 are all ON and relay 5 is OFF
                        const isDarkMode = data.states[1] && data.states[2] && data.states[3] && !data.states[4];
                        this.isLightMode = !isDarkMode;
                        UIManager.updateModeDisplay(isDarkMode ? 'dark' : 'light');
                    }
                }
                
                // Notify user that buttons were physically pressed
                NotificationManager.showNotification("Relays updated via physical buttons", "info");
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
        
        // After updating all relay states, check if the mode has changed
        this.detectAndUpdateCurrentMode();
    },
    
    /**
     * Detect the current mode (light/dark) based on relay states and update the UI
     */
    detectAndUpdateCurrentMode: function() {
        // Relays 2, 3, and 4 all ON and relay 5 OFF = Dark mode
        const relay2 = this.relayStates['2'] === true;
        const relay3 = this.relayStates['3'] === true;
        const relay4 = this.relayStates['4'] === true;
        const relay5 = this.relayStates['5'] === false; // Relay 5 (room light) should be OFF in dark mode
        
        // Check using indicator states as fallback if relayStates object is not populated
        if (relay2 === undefined || relay3 === undefined || relay4 === undefined || relay5 === undefined) {
            const relay2Indicator = document.getElementById('relay-indicator-2');
            const relay3Indicator = document.getElementById('relay-indicator-3');
            const relay4Indicator = document.getElementById('relay-indicator-4');
            const relay5Indicator = document.getElementById('relay-indicator-5');
            
            if (relay2Indicator && relay3Indicator && relay4Indicator && relay5Indicator) {
                const relay2On = relay2Indicator.classList.contains('on');
                const relay3On = relay3Indicator.classList.contains('on');
                const relay4On = relay4Indicator.classList.contains('on');
                const relay5Off = !relay5Indicator.classList.contains('on'); // Relay 5 should be OFF in dark mode
                
                const isDarkMode = relay2On && relay3On && relay4On && relay5Off;
                
                // Only update if mode has changed
                if (this.isLightMode === isDarkMode) {
                    console.log(`Mode change detected through UI indicators: ${isDarkMode ? 'dark' : 'light'} mode`);
                    this.isLightMode = !isDarkMode;
                    UIManager.updateModeDisplay(isDarkMode ? 'dark' : 'light');
                }
            }
        } else {
            // Use stored relay states
            const isDarkMode = relay2 && relay3 && relay4 && relay5;
            
            // Only update if mode has changed
            if (this.isLightMode === isDarkMode) {
                console.log(`Mode change detected through relay states: ${isDarkMode ? 'dark' : 'light'} mode`);
                this.isLightMode = !isDarkMode;
                UIManager.updateModeDisplay(isDarkMode ? 'dark' : 'light');
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
        
        // Check if this relay change affects the mode (for relays 2,3,4)
        if (relayId >= 2 && relayId <= 4) {
            // Delay to allow multiple sequential relay updates to complete
            setTimeout(() => {
                this.detectAndUpdateCurrentMode();
            }, 50);
        }
    },
    
    /**
     * Get button states from the ESP32
     */
    getButtonStates: function() {
        if (!ConnectionManager.isRelayConnected) return;
        
        console.log("Requesting button states...");
        
        Utils.sendRelayAction(
            { action: 'get_buttons' },
            '/control_relay/',
            { 
                action: 'get_buttons',
                com_port: ConnectionManager.getActiveRelayPort() 
            }
        )
        .then((data) => {
            if (data.type === 'buttons') {
                console.log("Received button states:", data);
                // Store button states
                if (Array.isArray(data.pressed)) {
                    this.buttonStates = data.pressed;
                    console.log("Button states updated:", this.buttonStates);
                }
                
                // Update relay states if provided
                if (Array.isArray(data.states)) {
                    this.updateRelayStatesUI(data.states);
                }
            } else {
                console.error("Invalid response for button states:", data);
            }
        })
        .catch((error) => {
            console.error('Error getting button states:', error);
        });
    }
}; 