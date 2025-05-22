/**
 * control_main.js - Main controller for microfilm control system
 * Initializes components and coordinates interactions between modules
 */

// TODOx2: Check current saferoom mode and set UI

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing microfilm control system...');
    
    
    // Verify that all required modules are loaded
    if (!Utils || !NotificationManager || !ConnectionManager || !MachineControls || 
        !RelayControls || !UIManager || !ChartManager || !ExternalSystemsManager) {
            console.error('ERROR: One or more required modules are not loaded!');
            
            // Check each module and log which ones are missing
            if (!Utils) console.error('Utils module not loaded');
            if (!NotificationManager) console.error('NotificationManager module not loaded');
            if (!ConnectionManager) console.error('ConnectionManager module not loaded');
            if (!MachineControls) console.error('MachineControls module not loaded');
            if (!RelayControls) console.error('RelayControls module not loaded');
            if (!UIManager) console.error('UIManager module not loaded');
            if (!ChartManager) console.error('ChartManager module not loaded');
            if (!ExternalSystemsManager) console.error('ExternalSystemsManager module not loaded');
            
            // Display error to user
            const controlContainer = document.querySelector('.control-container');
            if (controlContainer) {
                controlContainer.innerHTML = `
                <div style="padding: 20px; color: #ff453a; text-align: center;">
                <h2>Error Loading Control System</h2>
                <p>One or more required modules failed to load. Please check the browser console for details.</p>
                <p>Try refreshing the page or contact support if the issue persists.</p>
                </div>
                `;
            }
            
            return; // Stop initialization
    }
    
    // Initialize WebSocket connection
    Utils.setupWebSocket();
    
    // DOM element references
    const elements = {
        relayControls: document.getElementById('relay-controls'),
        settingsToggle: document.getElementById('settings-toggle'),
        modeToggle: document.getElementById('mode-toggle'),
        modeIndicator: document.getElementById('mode-indicator'),
        modeDisplay: document.getElementById('mode-display'),
        machineSwitch: document.getElementById('machine-switch'),
        machineIndicator: document.getElementById('machine-indicator'),
        emergencyStop: document.getElementById('emergency-stop'),
        machineTestConnection: document.getElementById('machine-test-connection'),
        relayTestConnection: document.getElementById('relay-test-connection'),
        machineConnectionStatus: document.getElementById('machine-connection-status'),
        relayConnectionStatus: document.getElementById('relay-connection-status'),
        machinePowerStatus: document.getElementById('machine-power-status'),
        systemStatusIndicator: document.querySelector('.status-indicator'),
        systemStatusLabel: document.querySelector('.status-label'),
        pingValue: document.querySelector('.ping-value'),
        machineStatsCard: document.getElementById('machine-stats-card'),
        statsToggle: document.getElementById('stats-toggle')
    };
    
    // Initialize mode display
    if (elements.modeDisplay) {
        elements.modeDisplay.classList.add('light-mode-display');
    }

    // Initialize device info fields to empty/N/A
    RelayControls.clearRelayInfo();
    MachineControls.clearMachineInfo();
    
    // Initialize relay controls with event listeners
    RelayControls.init();

    // Hide machine stats card initially
    if (elements.machineStatsCard) {
        elements.machineStatsCard.style.display = 'none';
    }
    
    // Initial check for available COM ports
    ConnectionManager.checkAvailablePorts();
    
    // Start connection polling
    ConnectionManager.startConnectionPolling();
    
    // Initialize charts
    ChartManager.initCharts();
    
    // Initialize external systems monitoring
    ExternalSystemsManager.init();
    
    // Set up event listeners
    
    // Show relay controls
    if (elements.settingsToggle) {
        elements.settingsToggle.addEventListener('click', function() {
            UIManager.toggleRelayControlsCard();
            // Fetch ESP32 stats and relay states when opening relay controls
            Utils.updateESP32Stats();
            RelayControls.checkRelayStates();
        });
    }

    // Toggle light/dark mode
    if (elements.modeToggle) {
        elements.modeToggle.addEventListener('click', function() {
            RelayControls.toggleRelayMode();
        });
    }

    // Machine toggle switch (requires hold)
    if (elements.machineSwitch) {
        // Hold timer variables
        let holdTimer = null;
        let progressOverlay = null;
        
        elements.machineSwitch.addEventListener('mousedown', function(e) {
            // Only allow toggle if machine is connected
            if (!ConnectionManager.isMachineConnected) {
                NotificationManager.showNotification('Machine not connected', 'error');
                return;
            }
            
            // Start the hold timer
            let holdDuration = 0;
            const requiredHoldTime = 2000; // 3 seconds for machine toggle
            
            // Create progress overlay if it doesn't exist yet
            progressOverlay = this.querySelector('.hold-progress');
            if (!progressOverlay) {
                progressOverlay = document.createElement('div');
                progressOverlay.className = 'hold-progress';
                progressOverlay.style.position = 'absolute';
                progressOverlay.style.bottom = '0';
                progressOverlay.style.left = '0';
                progressOverlay.style.height = '100%';
                progressOverlay.style.width = '0%';
                progressOverlay.style.backgroundColor = 'rgba(48, 209, 88, 0.3)';
                progressOverlay.style.borderRadius = 'inherit';
                progressOverlay.style.transition = 'width 0.1s linear';
                progressOverlay.style.zIndex = '0';
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(progressOverlay);
            } else {
                // Reset existing progress
                progressOverlay.style.width = '0%';
                progressOverlay.style.display = 'block';
            }
            
            // Add a pulsing effect to the machine indicator while holding
            if (elements.machineIndicator) {
                elements.machineIndicator.classList.add('pulse-hold');
            }
            
            // Start the interval to update the progress
            holdTimer = setInterval(() => {
                holdDuration += 100;
                const percentage = Math.min((holdDuration / requiredHoldTime) * 100, 100);
                progressOverlay.style.width = `${percentage}%`;
                
                // Give visual feedback about progress
                if (percentage < 33) {
                    progressOverlay.style.backgroundColor = 'rgba(48, 209, 88, 0.3)';
                } else if (percentage < 66) {
                    progressOverlay.style.backgroundColor = 'rgba(48, 209, 88, 0.5)';
                } else {
                    progressOverlay.style.backgroundColor = 'rgba(48, 209, 88, 0.7)';
                }
                
                // When hold time is reached, trigger the action
                if (holdDuration >= requiredHoldTime) {
                    clearInterval(holdTimer);
                    MachineControls.triggerMachineToggle();
                    
                    // Hide progress overlay
                    progressOverlay.style.display = 'none';
                    progressOverlay.style.width = '0%';
                    
                    // Remove pulse effect
                    if (elements.machineIndicator) {
                        elements.machineIndicator.classList.remove('pulse-hold');
                    }
                }
            }, 100);
        });
        
        const cancelHold = () => {
            // Cancel the hold timer
            if (holdTimer) {
                clearInterval(holdTimer);
                holdTimer = null;
            }
            
            // Hide progress overlay
            if (progressOverlay) {
                progressOverlay.style.display = 'none';
                progressOverlay.style.width = '0%';
            }
            
            // Remove pulse effect from indicator
            if (elements.machineIndicator) {
                elements.machineIndicator.classList.remove('pulse-hold');
            }
        };
        
        // Cancel hold if mouse is released
        elements.machineSwitch.addEventListener('mouseup', cancelHold);
        elements.machineSwitch.addEventListener('mouseleave', cancelHold);
        
        // Touch events for mobile
        elements.machineSwitch.addEventListener('touchstart', function(e) {
            // Simulate mousedown
            const mouseEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            this.dispatchEvent(mouseEvent);
        });
        
        elements.machineSwitch.addEventListener('touchend', function(e) {
            // Simulate mouseup
            const mouseEvent = new MouseEvent('mouseup', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            this.dispatchEvent(mouseEvent);
        });
    }

    // Emergency stop button
    if (elements.emergencyStop) {
        elements.emergencyStop.addEventListener('click', function() {
            // Only allow if machine is connected
            if (!ConnectionManager.isMachineConnected) {
                NotificationManager.showNotification('Machine not connected', 'error');
                return;
            }
            MachineControls.triggerEmergencyStop();
        });
    }

    // Connection test buttons
    if (elements.machineTestConnection) {
        elements.machineTestConnection.addEventListener('click', function() {
            this.classList.add('loading');
            ConnectionManager.checkMachinePort();
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1500);
        });
    }
    
    if (elements.relayTestConnection) {
        elements.relayTestConnection.addEventListener('click', function() {
            this.classList.add('loading');
            ConnectionManager.checkRelayPort();
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1500);
        });
    }

    // Relay toggle buttons
    document.querySelectorAll('.relay-toggle').forEach(button => {
        const relayNum = button.getAttribute('data-relay');
        if (!relayNum) return;

        button.addEventListener('click', function() {
            // Only allow toggle if relay is connected
            if (!ConnectionManager.isRelayConnected) {
                NotificationManager.showNotification('Relay not connected', 'error');
                return;
            }
            RelayControls.toggleRelay(relayNum);
        });
    });

    // Statistics toggle
    if (elements.statsToggle) {
        elements.statsToggle.addEventListener('click', function() {
            UIManager.toggleMachineStatsCard();
        });
    }

    // Machine stats button event listener
    const machineStatsButton = document.getElementById('machine-stats-button');
    if (machineStatsButton) {
        machineStatsButton.addEventListener('click', function() {
            UIManager.toggleMachineStatsCard();
        });
    }

    // Set transition styles for panels and elements
    if (elements.relayControls) {
        elements.relayControls.style.transition = `opacity ${UIManager.TRANSITION_DURATION}ms ease, transform ${UIManager.TRANSITION_DURATION}ms ease`;
    }
    if (elements.modeIndicator) {
        elements.modeIndicator.style.transition = `transform ${UIManager.TRANSITION_DURATION}ms ease, opacity ${UIManager.TRANSITION_DURATION}ms ease, color ${UIManager.TRANSITION_DURATION}ms ease`;
    }
    if (elements.machineIndicator) {
        // Set proper transition properties without units
        elements.machineIndicator.style.transition = 'transform 300ms ease, opacity 300ms ease';
        
        // Set initial styles for machine indicator
        elements.machineIndicator.style.display = 'inline-block';
        elements.machineIndicator.style.width = '12px';
        elements.machineIndicator.style.height = '12px';
        elements.machineIndicator.style.borderRadius = '50%';
        elements.machineIndicator.style.marginRight = '8px';
        elements.machineIndicator.style.backgroundColor = '#ff453a'; // Default to red/off
        elements.machineIndicator.style.boxShadow = '0 0 6px rgba(255, 69, 58, 0.5)';
    }
    
    // Add dynamic styles for loading state
    const style = document.createElement('style');
    style.textContent = `
        .loading {
            position: relative;
            pointer-events: none;
        }
        .loading:after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: inherit;
            z-index: 2;
        }
        .loading:before {
            content: '';
            position: absolute;
            top: calc(50% - 10px);
            left: calc(50% - 10px);
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-top-color: #fff;
            border-radius: 50%;
            z-index: 3;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .pulse-hold {
            animation: pulse-animation 1.5s infinite;
        }
        @keyframes pulse-animation {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(0.92); opacity: 0.8; }
            100% { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Set interval for the latency test
    setInterval(() => {
        if (ConnectionManager.isRelayConnected) {
            Utils.measureESP32Latency()
                .then(latency => {
                    Utils.updateLatencyDisplay(latency);
                })
                .catch(() => {
                    if (elements.pingValue) {
                        elements.pingValue.textContent = 'N/A';
                        elements.pingValue.style.color = '#ff453a';
                    }
                });
        } else if (elements.pingValue) {
            // If relay is not connected, show N/A
            elements.pingValue.textContent = 'N/A';
            elements.pingValue.style.color = '#ff453a';
        }
    }, 1000000); // Check every 10 seconds
    
    // Check relay states periodically
    setInterval(() => {
        RelayControls.checkRelayStates();
    }, 1000000); // Every 10 seconds

    // Add close button event listeners
    const statsCloseBtn = document.getElementById('stats-close-btn');
    if (statsCloseBtn) {
        statsCloseBtn.addEventListener('click', function() {
            UIManager.toggleMachineStatsCard();
        });
    }

    const relayCloseBtn = document.getElementById('relay-close-btn');
    if (relayCloseBtn) {
        relayCloseBtn.addEventListener('click', function() {
            UIManager.toggleRelayControlsCard();
        });
    }

    // Override the global fetchMachineStats function to use our MachineControls module
    window.fetchMachineStats = function() {
        MachineControls.refreshMachineStats();
    };

    // Get reference to the refresh button
    const statsRefreshButton = document.querySelector('.refresh-button');
    
    // Helper function to ensure minimum animation duration
    function animateWithMinDuration(element, operation, minDuration = 1000) {
        const startTime = performance.now();
        const icon = element.querySelector('i');
        
        // Add spinning class to the icon
        if (icon) icon.classList.add('spinning');
        
        // Return a promise that resolves after minimum duration
        return new Promise((resolve) => {
            // Start the operation (without waiting for it)
            operation();
            
            // Set minimum duration timer
            setTimeout(() => {
                if (icon) icon.classList.remove('spinning');
                resolve();
            }, minDuration);
        });
    }

    // Add event listener to the stats refresh button
    if (statsRefreshButton) {
        statsRefreshButton.addEventListener('click', function() {
            // Use our animation function but don't wait for operation to complete
            // since it handles its own completion
            animateWithMinDuration(this, () => {
                // Call the existing function - note it already handles its own animation state
                MachineControls.refreshMachineStats(false); // Pass false to avoid duplicate animation
            });
        });
    }

    // Add event listener to the relay refresh button
    const relayRefreshButton = document.querySelector('.refresh-button-relay');
    if (relayRefreshButton) {
        relayRefreshButton.addEventListener('click', function() {
            const button = this;
            const icon = button.querySelector('i');
            
            // Add spinning animation to icon
            if (icon) icon.classList.add('spinning');
            
            // Record start time
            const startTime = performance.now();
            
            // Execute operations
            Promise.all([
                RelayControls.checkRelayStates(),
                Utils.updateESP32Stats()
            ])
            .then(() => {
                NotificationManager.showNotification('Relay information updated', 'success');
            })
            .catch(error => {
                console.error('Error refreshing relay information:', error);
                NotificationManager.showNotification('Failed to update relay information', 'error');
            })
            .finally(() => {
                // Calculate elapsed time
                const elapsedTime = performance.now() - startTime;
                const remainingTime = Math.max(0, 1000 - elapsedTime);
                
                // Ensure minimum animation duration
                setTimeout(() => {
                    if (icon) icon.classList.remove('spinning');
                }, remainingTime);
            });
        });
    }

    // Emergency stop button for relay
    const relayEmergencyStop = document.getElementById('relay-emergency-stop');
    if (relayEmergencyStop) {
        relayEmergencyStop.addEventListener('click', function() {
            NotificationManager.showNotification('Relay emergency stop button pressed', 'warning');
            // Add actual emergency stop functionality here
        });
    }

    // Add event listeners for external systems refresh buttons
    const smaRefreshButton = document.querySelector('.sma-refresh-button');
    if (smaRefreshButton) {
        smaRefreshButton.addEventListener('click', function() {
            const icon = this.querySelector('i');
            
            // Add spinning animation to icon
            if (icon) icon.classList.add('spinning');
            
            // Record start time
            const startTime = performance.now();
            
            // Execute SMA update operation
            ExternalSystemsManager.updateSMAStatus()
                .then(() => {
                    NotificationManager.showNotification('SMA software status updated', 'success');
                })
                .catch(error => {
                    console.error('Error updating SMA status:', error);
                    NotificationManager.showNotification('Failed to update SMA status', 'error');
                })
                .finally(() => {
                    // Calculate elapsed time
                    const elapsedTime = performance.now() - startTime;
                    const remainingTime = Math.max(0, 1000 - elapsedTime);
                    
                    // Ensure minimum animation duration
                    setTimeout(() => {
                        if (icon) icon.classList.remove('spinning');
                    }, remainingTime);
                });
        });
    }

    const pcRefreshButton = document.querySelector('.pc-refresh-button');
    if (pcRefreshButton) {
        pcRefreshButton.addEventListener('click', function() {
            const icon = this.querySelector('i');
            
            // Add spinning animation to icon
            if (icon) icon.classList.add('spinning');
            
            // Record start time
            const startTime = performance.now();
            
            // Execute PC update operation
            ExternalSystemsManager.updatePCStatus()
                .then(() => {
                    NotificationManager.showNotification('External PC status updated', 'success');
                })
                .catch(error => {
                    console.error('Error updating PC status:', error);
                    NotificationManager.showNotification('Failed to update External PC status', 'error');
                })
                .finally(() => {
                    // Calculate elapsed time
                    const elapsedTime = performance.now() - startTime;
                    const remainingTime = Math.max(0, 1000 - elapsedTime);
                    
                    // Ensure minimum animation duration
                    setTimeout(() => {
                        if (icon) icon.classList.remove('spinning');
                    }, remainingTime);
                });
        });
    }
}); 
