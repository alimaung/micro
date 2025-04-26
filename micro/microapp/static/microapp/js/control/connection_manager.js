/**
 * connection_manager.js - Connection management for microfilm control system
 * Handles checking and maintaining connections to hardware devices
 */

// Create namespace for connection management functions
const ConnectionManager = {
    // Constants
    CONNECTION_POLL_INTERVAL: 10000, // Check every 10 seconds
    POWER_STATE_POLL_INTERVAL: 5000, // Check power state every 5 seconds
    
    // State tracking
    isMachineConnected: false,
    isRelayConnected: false,
    lastMachineDeviceData: {
        port: 'N/A',
        vendor_id: 'N/A',
        product_id: 'N/A',
        serial_number: 'N/A',
        manufacturer: 'N/A'
    },
    lastRelayDeviceData: {
        port: 'N/A',
        vendor_id: 'N/A',
        product_id: 'N/A',
        product: 'N/A',
        manufacturer: 'N/A'
    },

    /**
     * Start periodic polling for connections
     */
    startConnectionPolling: function() {
        // Only start power state polling, no more connection polling
        this.startPowerStatePolling();

        // Perform initial machine state check after connection is established 
        // (with slight delay to allow connection check to complete first)
        setTimeout(() => {
            if (this.isMachineConnected) {
                console.log("Performing initial machine power state check...");
                MachineControls.checkMachinePowerState(false);
            }
        }, 2000);
    },

    /**
     * Start power state polling
     */
    startPowerStatePolling: function() {
        // Removed interval polling for machine power state
        // Only check on page load (after connection) and after toggle
    },

    /**
     * Simple connection verification without UI updates
     */
    verifyMachineConnection: function() {
        fetch('/check_port/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'port': this.getActiveMachinePort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success' && this.isMachineConnected) {
                // Only if we detect a disconnect
                console.log("Machine connection lost during light check");
                // Force a full check next time
                setTimeout(() => this.checkMachinePort(), 1000);
            }
        })
        .catch(error => {
            console.error("Error during light machine check:", error);
        });
    },

    /**
     * Simple connection verification without UI updates
     */
    verifyRelayConnection: function() {
        fetch('/check_port/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'port': this.getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success' && this.isRelayConnected) {
                // Only if we detect a disconnect
                console.log("Relay connection lost during light check");
                // Force a full check next time
                setTimeout(() => this.checkRelayPort(), 1000);
            }
        })
        .catch(error => {
            console.error("Error during light relay check:", error);
        });
    },

    /**
     * Check available ports
     */
    checkAvailablePorts: function() {
        console.log("Checking connection status for all ports...");
        
        // Check for SMA51 Machine on COM3
        this.checkMachinePort();
        
        // Check for Saferoom Relay on COM7 or COM18
        this.checkRelayPort();
        
        // Update overall system status (without redundant UI updates)
        UIManager.updateSystemStatus();
    },

    /**
     * Check if SMA51 Machine port is available (COM3)
     */
    checkMachinePort: function() {
        console.log("Checking for SMA51 Machine on COM3...");
        
        // Disable machine toggle button during check
        const machineSwitch = document.getElementById('machine-switch');
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
            const previousState = this.isMachineConnected;
            
            if (data.status === 'success') {
                // Port is available
                this.isMachineConnected = true;
                
                // Update machine port info with the returned device info
                if (data.device_info) {
                    // Only update UI if device info has changed
                    if (!Utils.isEqualDeviceInfo(this.lastMachineDeviceData, data.device_info)) {
                        MachineControls.updateMachineInfoFromData(data.device_info);
                        // Store current data for future comparison
                        this.lastMachineDeviceData = { ...data.device_info };
                    }
                } else {
                    // Fallback to default values only if we don't already have data
                    if (this.lastMachineDeviceData.port === 'N/A') {
                        MachineControls.updateMachineInfo('COM3');
                        this.lastMachineDeviceData.port = 'COM3';
                    }
                }
                
                // Update machine connection UI
                UIManager.updateMachineConnectionUI(true);
                
                // Show notification if state changed from disconnected to connected
                if (!previousState && this.isMachineConnected) {
                    NotificationManager.showNotification("Machine connected", "success");
                    
                    // Check actual power state now that we're connected
                    MachineControls.checkMachinePowerState();
                }
                
                console.log("SMA51 Machine connected on COM3");
            } else {
                // Port is not available
                this.isMachineConnected = false;
                
                // Update machine connection UI
                UIManager.updateMachineConnectionUI(false);
                
                // Show notification if state changed from connected to disconnected
                if (previousState && !this.isMachineConnected) {
                    NotificationManager.showNotification("Machine disconnected", "error");
                    
                    // Clear device info only if we're newly disconnected
                    MachineControls.clearMachineInfo();
                    this.lastMachineDeviceData = {
                        port: 'N/A',
                        vendor_id: 'N/A',
                        product_id: 'N/A',
                        serial_number: 'N/A',
                        manufacturer: 'N/A'
                    };
                    
                    // If machine was on but now disconnected, update its state to off
                    if (MachineControls.isMachineOn) {
                        MachineControls.isMachineOn = false;
                        MachineControls.updateMachineState(false);
                    }
                }
                else if (!this.isMachineConnected) {
                    NotificationManager.showNotification("Machine not available", "error");
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
            this.isMachineConnected = false;
            
            // Update machine connection UI
            UIManager.updateMachineConnectionUI(false);
            
            // Re-enable machine toggle button after check
            if (machineSwitch) {
                machineSwitch.disabled = false;
                machineSwitch.classList.remove('checking');
            }
        });
    },

    /**
     * Check if Saferoom Relay port is available (COM7 or COM18)
     */
    checkRelayPort: function() {
        console.log("Checking for Saferoom Relay on COM18...");
        
        // Store previous states before any changes
        const wasConnected = this.isRelayConnected;
        const previousPort = this.getActiveRelayPort();
        
        // Disable mode toggle during check
        const modeToggle = document.getElementById('mode-toggle');
        if (modeToggle) {
            modeToggle.disabled = true;
            modeToggle.classList.add('checking');
        }
        
        // First try COM7
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
                this.isRelayConnected = true;
                
                // Update relay port info with the returned device info
                if (data.device_info) {
                    // Only update UI if device info has changed
                    if (!Utils.isEqualDeviceInfo(this.lastRelayDeviceData, data.device_info)) {
                        RelayControls.updateRelayInfoFromData(data.device_info);
                        // Store current data for future comparison
                        this.lastRelayDeviceData = { ...data.device_info };
                    }
                } else {
                    // Fallback to default values only if we don't already have data
                    if (this.lastRelayDeviceData.port === 'N/A') {
                        RelayControls.updateRelayInfo('COM7');
                        this.lastRelayDeviceData.port = 'COM7';
                    }
                }
                
                // Update relay connection UI
                UIManager.updateRelayConnectionUI(true);
                
                // Show notification if state changed from disconnected to connected
                if (!wasConnected) {
                    NotificationManager.showNotification("Relay connected on COM7", "success");
                } else {
                    // Show notification even if it was already connected
                    NotificationManager.showNotification("Relay connection confirmed on COM7", "success");
                }
                
                console.log("Saferoom Relay connected on COM7");
                
                // Enable the mode toggle
                if (modeToggle) {
                    modeToggle.disabled = false;
                    modeToggle.classList.remove('checking');
                }
                
                // Fetch initial relay states and ESP32 status now that we're connected
                Utils.updateESP32Stats();
            } else {
                // Try COM18 instead
                console.log("COM7 not available, checking COM18...");
                this.tryBackupRelayPort();
            }
        })
        .catch(error => {
            console.error('Error checking relay port COM7:', error);
            // Try COM18 as backup
            this.tryBackupRelayPort();
        });
    },

    /**
     * Try connecting to backup relay port (COM18)
     */
    tryBackupRelayPort: function() {
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
            // Enable the mode toggle button
            const modeToggle = document.getElementById('mode-toggle');
            if (modeToggle) {
                modeToggle.disabled = false;
                modeToggle.classList.remove('checking');
            }
            
            if (data.status === 'success') {
                // COM18 is available
                this.isRelayConnected = true;
                
                // Update relay port info
                if (data.device_info) {
                    RelayControls.updateRelayInfoFromData(data.device_info);
                    this.lastRelayDeviceData = { ...data.device_info };
                } else {
                    RelayControls.updateRelayInfo('COM18');
                    this.lastRelayDeviceData.port = 'COM18';
                }
                
                // Update relay connection UI
                UIManager.updateRelayConnectionUI(true);
                
                // Show success notification
                NotificationManager.showNotification("Relay connected on COM18", "success");
                
                console.log("Saferoom Relay connected on COM18");
                
                // Fetch initial relay states and ESP32 status
                Utils.updateESP32Stats();
            } else {
                // Neither COM7 nor COM18 is available
                this.isRelayConnected = false;
                
                // Update UI to show disconnected state
                UIManager.updateRelayConnectionUI(false);
                
                // Show error notification
                NotificationManager.showNotification("Relay not found. Please check connection.", "error");
                
                console.log("Saferoom Relay not found on any port");
            }
        })
        .catch(error => {
            console.error('Error checking relay port COM18:', error);
            
            // Enable the mode toggle button
            const modeToggle = document.getElementById('mode-toggle');
            if (modeToggle) {
                modeToggle.disabled = false;
                modeToggle.classList.remove('checking');
            }
            
            // Update connection state
            this.isRelayConnected = false;
            
            // Update UI
            UIManager.updateRelayConnectionUI(false);
            
            // Show error notification
            NotificationManager.showNotification("Error checking relay connection", "error");
        });
    },

    /**
     * Get the active relay port
     * @returns {string} The COM port for the relay connection
     */
    getActiveRelayPort: function() {
        const relayPort = document.getElementById('relay-port');
        if (relayPort && this.isRelayConnected && relayPort.textContent !== 'N/A') {
            return relayPort.textContent;
        }
        return 'COM7'; // Default fallback to COM18
    },

    /**
     * Get the active machine port
     * @returns {string} The COM port for the machine connection
     */
    getActiveMachinePort: function() {
        const machinePort = document.getElementById('machine-port');
        if (machinePort && this.isMachineConnected && machinePort.textContent !== 'N/A') {
            return machinePort.textContent;
        }
        return 'COM3'; // Default fallback
    }
}; 