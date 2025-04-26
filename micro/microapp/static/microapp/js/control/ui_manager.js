/**
 * ui_manager.js - UI management for microfilm control system
 * Handles UI updates and display functions
 */

// Create namespace for UI management functions
const UIManager = {
    // Constants
    TRANSITION_DURATION: 300, // ms

    /**
     * Update machine connection status in the UI
     * @param {boolean} isConnected - Whether the machine is connected
     */
    updateMachineConnectionUI: function(isConnected) {
        const machineConnectionStatus = document.getElementById('machine-connection-status');
        const machineSwitch = document.getElementById('machine-switch');
        const emergencyStop = document.getElementById('emergency-stop');
        const machineTestConnection = document.getElementById('machine-test-connection');
        
        // Update connection status indicator
        this.updateConnectionStatus(machineConnectionStatus, isConnected);
        
        // Update machine switch button
        if (machineSwitch) {
            machineSwitch.disabled = !isConnected;
            machineSwitch.classList.toggle('disabled', !isConnected);
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
        this.updateSystemStatus();
    },
    
    /**
     * Update relay connection status in the UI
     * @param {boolean} isConnected - Whether the relay is connected
     */
    updateRelayConnectionUI: function(isConnected) {
        const relayConnectionStatus = document.getElementById('relay-connection-status');
        const modeToggle = document.getElementById('mode-toggle');
        const relayTestConnection = document.getElementById('relay-test-connection');
        
        // Update connection status indicator
        this.updateConnectionStatus(relayConnectionStatus, isConnected);
        
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
        this.updateSystemStatus();
    },
    
    /**
     * Update connection status element
     * @param {HTMLElement} statusElement - The status element to update
     * @param {boolean} isConnected - Whether the device is connected
     */
    updateConnectionStatus: function(statusElement, isConnected) {
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
    },
    
    /**
     * Update machine status display
     * @param {boolean} isOn - Whether the machine is on
     */
    updateMachineStatus: function(isOn) {
        // Update other machine status indicators
        const machinePowerStatus = document.getElementById('machine-power-status');
        const machineIndicator = document.getElementById('machine-indicator');
        const statusBadges = document.querySelectorAll('.status-badge:not(#machine-power-status):not(#machine-connection-status):not(#relay-connection-status)');
        const statusDots = document.querySelectorAll('.status-dot');
        
        // Update machine power status badge specifically
        if (machinePowerStatus) {
            if (isOn) {
                machinePowerStatus.classList.remove('critical');
                machinePowerStatus.classList.add('operational');
                machinePowerStatus.innerHTML = '<i class="fas fa-bolt"></i> Powered (Verified)';
            } else {
                machinePowerStatus.classList.remove('operational');
                machinePowerStatus.classList.add('critical');
                machinePowerStatus.innerHTML = '<i class="fas fa-bolt"></i> Offline (Verified)';
            }
        }
        
        // Update other status badges
        statusBadges.forEach(badge => {
            if (isOn) {
                badge.classList.remove('critical');
                badge.classList.add('operational');
                badge.innerHTML = '<i class="fas fa-check-circle"></i> Operational';
            } else {
                badge.classList.remove('operational');
                badge.classList.add('critical');
                badge.innerHTML = '<i class="fas fa-times-circle"></i> Offline';
            }
        });
        
        // Update status dots
        statusDots.forEach(dot => {
            dot.classList.toggle('online', isOn);
            dot.classList.toggle('offline', !isOn);
        });
        
        // Update machine indicator appearance
        if (machineIndicator) {
            // Update indicator appearance
            machineIndicator.style.backgroundColor = isOn ? '#30d158' : '#ff453a';
            machineIndicator.style.boxShadow = isOn 
                ? '0 0 8px rgba(48, 209, 88, 0.5)' 
                : '0 0 6px rgba(255, 69, 58, 0.5)';
            
            // Toggle class for styling
            machineIndicator.classList.toggle('on', isOn);
        }
    },
    
    /**
     * Stop all motor animations
     */
    stopAllMotorAnimations: function() {
        document.querySelectorAll('.fa-spin').forEach(element => {
            element.classList.remove('fa-spin');
        });
    },
    
    /**
     * Update mode display
     * @param {string} mode - The mode to display
     */
    updateModeDisplay: function(mode) {
        if (!mode) return;
        
        // Find the mode indicator icon
        const modeIcon = document.getElementById('mode-indicator');
        const modeDisplay = document.getElementById('mode-display');
        
        if (modeIcon && modeDisplay) {
            // Update mode and display
            const isDarkMode = mode === 'dark';
            
            // Update display with proper styling classes
            if (isDarkMode) {
                modeIcon.className = 'fas fa-moon';
                modeDisplay.className = 'mode-indicator dark-mode-display';
                
                // Find or create the status text element
                let statusText = modeDisplay.querySelector('.mode-status-text');
                if (!statusText) {
                    // If not found, update the icon first
                    modeDisplay.innerHTML = '<i class="fas fa-moon"></i><span class="mode-status-text">Dark</span>';
                } else {
                    // Update only the icon and text content
                    const iconElement = modeDisplay.querySelector('i');
                    if (iconElement) iconElement.className = 'fas fa-moon';
                    statusText.textContent = 'Dark';
                }
            } else {
                modeIcon.className = 'fas fa-sun';
                modeDisplay.className = 'mode-indicator light-mode-display';
                
                // Find or create the status text element
                let statusText = modeDisplay.querySelector('.mode-status-text');
                if (!statusText) {
                    // If not found, update the icon first
                    modeDisplay.innerHTML = '<i class="fas fa-sun"></i><span class="mode-status-text">Light</span>';
                } else {
                    // Update only the icon and text content
                    const iconElement = modeDisplay.querySelector('i');
                    if (iconElement) iconElement.className = 'fas fa-sun';
                    statusText.textContent = 'Light';
                }
            }
            
            console.log(`Mode display updated to: ${mode}`);
        }
    },
    
    /**
     * Update system status display
     */
    updateSystemStatus: function() {
        const systemStatusIndicator = document.querySelector('.status-indicator');
        const systemStatusLabel = document.querySelector('.status-label');
        
        if (systemStatusIndicator && systemStatusLabel) {
            // Determine status based on connections
            if (ConnectionManager.isMachineConnected && ConnectionManager.isRelayConnected) {
                // All systems online
                systemStatusIndicator.classList.remove('warning', 'offline');
                systemStatusIndicator.classList.add('online');
                systemStatusLabel.textContent = 'All Systems Online';
            } else if (ConnectionManager.isMachineConnected || ConnectionManager.isRelayConnected) {
                // Partial connection
                systemStatusIndicator.classList.remove('online', 'offline');
                systemStatusIndicator.classList.add('warning');
                systemStatusLabel.textContent = 'Partial Connection';
            } else {
                // All systems offline
                systemStatusIndicator.classList.remove('online', 'warning');
                systemStatusIndicator.classList.add('offline');
                systemStatusLabel.textContent = 'All Systems Offline';
            }
        }
    },
    
    /**
     * Add tooltips to elements when disconnected
     */
    addDisconnectedTooltips: function() {
        const tooltipTargets = document.querySelectorAll('.stats-card .gauge, .motor-card, .motors-chart-container');
        
        tooltipTargets.forEach(element => {
            // Only add tooltip if it doesn't already have one
            if (!element.hasAttribute('data-tooltip')) {
                element.setAttribute('data-tooltip', 'Machine disconnected');
                element.classList.add('has-tooltip');
            }
        });
    },
    
    /**
     * Toggle machine stats card visibility
     */
    toggleMachineStatsCard: function() {
        const machineStatsCard = document.getElementById('machine-stats-card');
        const statsToggle = document.getElementById('stats-toggle');
        
        if (machineStatsCard) {
            const isCurrentlyVisible = machineStatsCard.style.display !== 'none';
            
            if (isCurrentlyVisible) {
                // Hide the card with animation
                machineStatsCard.style.opacity = '0';
                machineStatsCard.style.transform = 'translateY(-20px)';
                
                // Wait for animation to complete before hiding
                setTimeout(() => {
                    machineStatsCard.style.display = 'none';
                }, this.TRANSITION_DURATION);
                
                // Update toggle button
                if (statsToggle) {
                    statsToggle.innerHTML = '<i class="fas fa-chart-bar"></i> Show Statistics';
                }
            } else {
                // Show the card with animation
                machineStatsCard.style.display = 'block';
                machineStatsCard.style.opacity = '0';
                machineStatsCard.style.transform = 'translateY(-20px)';
                
                // Trigger reflow to ensure animation works
                void machineStatsCard.offsetWidth;
                
                // Apply visible state
                machineStatsCard.style.opacity = '1';
                machineStatsCard.style.transform = 'translateY(0)';
                
                // Update toggle button
                if (statsToggle) {
                    statsToggle.innerHTML = '<i class="fas fa-chart-bar"></i> Hide Statistics';
                }
                
                // If machine is connected, update stats
                if (ConnectionManager.isMachineConnected) {
                    MachineControls.fetchMachineStats();
                } else {
                    MachineControls.updateMachineStatsUIPlaceholders();
                }
            }
        }
    },
    
    /**
     * Toggle relay controls card visibility
     */
    toggleRelayControlsCard: function() {
        const relayControls = document.getElementById('relay-controls');
        const settingsToggle = document.getElementById('settings-toggle');
        
        if (relayControls) {
            const isCurrentlyVisible = getComputedStyle(relayControls).display !== 'none';
            
            if (isCurrentlyVisible) {
                // Hide with animation
                relayControls.style.opacity = '0';
                relayControls.style.transform = 'translateY(-20px)';
                
                // Wait for animation before hiding
                setTimeout(() => {
                    relayControls.style.display = 'none';
                }, this.TRANSITION_DURATION);
                
                // Update toggle button
                if (settingsToggle) {
                    settingsToggle.textContent = 'Show Relay Controls';
                }
            } else {
                // Show with animation
                relayControls.style.display = 'block';
                relayControls.style.opacity = '0';
                relayControls.style.transform = 'translateY(-20px)';
                
                // Trigger reflow
                void relayControls.offsetWidth;
                
                // Apply visible state
                relayControls.style.opacity = '1';
                relayControls.style.transform = 'translateY(0)';
                
                // Update toggle button
                if (settingsToggle) {
                    settingsToggle.textContent = 'Hide Relay Controls';
                }
            }
        }
    }
}; 