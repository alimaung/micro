document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const relayControls = document.getElementById('relay-controls');
    const settingsToggle = document.getElementById('settings-toggle');
    const modeToggle = document.getElementById('mode-toggle');
    const modeIndicator = document.getElementById('mode-indicator');
    const modeDisplay = document.getElementById('mode-display');
    const machineSwitch = document.getElementById('machine-switch');
    const machineIndicator = document.getElementById('machine-indicator');
    const emergencyStop = document.getElementById('emergency-stop');
    const machineTestConnection = document.getElementById('machine-test-connection');
    const relayTestConnection = document.getElementById('relay-test-connection');
    const machineConnectionStatus = document.getElementById('machine-connection-status');
    const relayConnectionStatus = document.getElementById('relay-connection-status');
    const machinePowerStatus = document.getElementById('machine-power-status');
    const systemStatusIndicator = document.querySelector('.status-indicator');
    const systemStatusLabel = document.querySelector('.status-label');
    const pingValue = document.querySelector('.ping-value');
    
    // State variables
    let isLightMode = true;
    let isMachineOn = false;
    let actualMachinePowerState = false;
    let isMachineConnected = false;
    let isRelayConnected = false;
    let lastPingTime = 0;
    const relayStates = {};
    
    // Animation settings
    const TRANSITION_DURATION = 300; // ms
    
    

    let pendingRelayStates = {};
 
    // Initialize mode display with correct classes
    if (modeDisplay) {
        // Ensure light mode class is applied 
        modeDisplay.classList.add('light-mode-display');
    }

    // Initialize device info fields to empty/N/A
    clearMachineInfo();
    clearRelayInfo();

    // Initialize machine stats card as hidden
    const machineStatsCard = document.getElementById('machine-stats-card');
    if (machineStatsCard) {
        machineStatsCard.style.display = 'none';
    }

    // Initial check for available COM ports
    checkAvailablePorts();
    
    // Set up periodic polling for connection status
    startConnectionPolling();

    // Function to start periodic polling for connection status
    function startConnectionPolling() {

        // Perform initial machine state check after connection is established 
        // (with slight delay to allow connection check to complete first)
        setTimeout(() => {
            if (isMachineConnected) {
                console.log("Performing initial machine power state check...");
                checkMachinePowerState(false);
            }
        }, 2000);
    }

    // Simple connection verification without UI updates
    function verifyMachineConnection() {
        fetch('/check_port/', {
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
            if (data.status !== 'success' && isMachineConnected) {
                // Only if we detect a disconnect
                console.log("Machine connection lost during light check");
                // Force a full check next time
                setTimeout(checkMachinePort, 1000);
            }
        })
        .catch(error => {
            console.error("Error during light machine check:", error);
        });
    }

    // Simple connection verification without UI updates
    function verifyRelayConnection() {
        fetch('/check_port/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'port': getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success' && isRelayConnected) {
                // Only if we detect a disconnect
                console.log("Relay connection lost during light check");
                // Force a full check next time
                setTimeout(checkRelayPort, 1000);
            }
        })
        .catch(error => {
            console.error("Error during light relay check:", error);
        });
    }


    // Function to update machine power state UI
    function updateMachineState(isOn, forceUpdate = false) {
        console.log(`Updating machine state UI to: ${isOn ? 'ON' : 'OFF'}, force update: ${forceUpdate}`);
        
        // Update if state has changed or force update is requested
        if (isMachineOn !== isOn || forceUpdate) {
            // Update UI state
            isMachineOn = isOn;
            
            // Always update the machine indicator icon regardless of previous state
            if (machineIndicator) {
                // Update both color and background color for visibility
                machineIndicator.style.color = isOn ? '#00ff00' : '#ff0000';
                machineIndicator.style.backgroundColor = isOn ? '#30d158' : '#ff453a';
                machineIndicator.style.boxShadow = isOn 
                    ? '0 0 8px rgba(48, 209, 88, 0.5)' 
                    : '0 0 6px rgba(255, 69, 58, 0.5)';
                
                // Reset opacity in case it was changed during animation
                machineIndicator.style.opacity = '1';
                
                // Toggle class for styling
                machineIndicator.classList.toggle('on', isOn);
            }
            
            // Always update the machine power status indicator
            if (machinePowerStatus) {
                updateMachineStatus(isOn);
            }
            
            // If we turn off, stop all motor animations if they exist
            if (!isOn) {
                stopAllMotorAnimations();
            }
            
            console.log(`Machine state UI updated to: ${isOn ? 'ON' : 'OFF'}`);
        } else {
            console.log('Machine state unchanged, skipping UI update');
            
            // Even if we skip the update, ensure status indicators are still consistent with current state
            // This handles cases where the UI might be out of sync with the state variable
            if (machineIndicator && ((isOn && !machineIndicator.classList.contains('on')) || 
                                    (!isOn && machineIndicator.classList.contains('on')))) {
                console.log('Detected UI inconsistency, forcing update...');
                
                // Directly toggle the indicator class
                machineIndicator.classList.toggle('on', isOn);
                machineIndicator.style.backgroundColor = isOn ? '#30d158' : '#ff453a';
                machineIndicator.style.opacity = '1';
                
                // Update status badge as well
                if (machinePowerStatus) {
                    updateMachineStatus(isOn);
                }
                
                console.log('UI inconsistency fixed');
            }
        }
    }

    // Show relay controls
    if (settingsToggle) {
        settingsToggle.addEventListener('click', function() {
            toggleRelayControlsCard();
            // Fetch ESP32 stats and relay states when opening relay controls
            updateESP32Stats();
        });
    }

    // Toggle light/dark mode with animation
    modeToggle.addEventListener('click', function() {
        // Only allow toggle if relay is connected
        if (!isRelayConnected) {
            showNotification('Relay not connected', 'error');
            return;
        }
        // Call our new toggle function
        toggleRelayMode();
        // Fetch ESP32 stats and relay states after mode change
        setTimeout(() => {
            updateESP32Stats();
        }, 150);
        setTimeout(() => {
            updateESP32Stats();
        }, 700);
    });

    // Toggle machine switch with animation
    machineSwitch.addEventListener('mousedown', function(e) {
        // Only allow toggle if machine is connected
        if (!isMachineConnected) {
            showNotification('Machine not connected', 'error');
            return;
        }
        
        // Start the hold timer
        let holdDuration = 0;
        const requiredHoldTime = 3000; // 3 seconds for machine toggle
        let holdInterval;
        
        // Create progress overlay if it doesn't exist yet
        let progressOverlay = this.querySelector('.hold-progress');
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
        if (machineIndicator) {
            machineIndicator.classList.add('pulse-hold');
            // Create this style if not already added to document
            if (!document.querySelector('#pulse-hold-style')) {
                const pulseStyle = document.createElement('style');
                pulseStyle.id = 'pulse-hold-style';
                pulseStyle.textContent = `
                    .pulse-hold {
                        animation: pulse-animation 1.5s infinite;
                    }
                    @keyframes pulse-animation {
                        0% { transform: scale(1); opacity: 1; }
                        50% { transform: scale(0.92); opacity: 0.8; }
                        100% { transform: scale(1); opacity: 1; }
                    }
                `;
                document.head.appendChild(pulseStyle);
            }
        }
        
        // Start the interval to update the progress
        holdInterval = setInterval(() => {
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
                clearInterval(holdInterval);
                triggerMachineToggle();
            }
        }, 100);
        
        // Function to handle mouseup and mouseleave
        const cancelHold = () => {
            clearInterval(holdInterval);
            if (progressOverlay) {
                // Fade out the progress overlay
                progressOverlay.style.transition = 'opacity 0.3s ease';
                progressOverlay.style.opacity = '0';
                setTimeout(() => {
                    progressOverlay.style.width = '0%';
                    progressOverlay.style.opacity = '1';
                    progressOverlay.style.transition = 'width 0.1s linear';
                    progressOverlay.style.display = 'none';
                }, 300);
            }
            
            // Remove pulse effect from indicator
            if (machineIndicator) {
                machineIndicator.classList.remove('pulse-hold');
            }
            
            // Remove the event listeners
            document.removeEventListener('mouseup', cancelHold);
            this.removeEventListener('mouseleave', cancelHold);
        };
        
        // Add event listeners to cancel on mouseup or mouseleave
        document.addEventListener('mouseup', cancelHold);
        this.addEventListener('mouseleave', cancelHold);
        
        // Prevent default to avoid text selection
        e.preventDefault();
    });
    
    // Function to actually trigger the machine toggle action
    function triggerMachineToggle() {
        // Store the intended state
        const intendedState = !isMachineOn;
        const action = intendedState ? 'machine_on' : 'machine_off';
        
        // Start loading state
        machineSwitch.classList.add('loading');
        
        // Animate the indicator to show processing state
        machineIndicator.style.transform = 'scale(0.5)';
        machineIndicator.style.opacity = '0.5';
        machineIndicator.classList.remove('pulse-hold');
        
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
                'com_port': getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            machineSwitch.classList.remove('loading');
            
            if (data.status === 'success') {
                // Don't update UI yet, just show a pending notification
                showNotification(`Machine state change initiated`, 'info');
                
                // Reset indicator appearance but keep in a "pending" state
                machineIndicator.style.transform = 'scale(1)';
                machineIndicator.style.opacity = '0.7';
                
                // Check actual power state after a delay to allow machine to respond
                setTimeout(() => {
                    checkMachinePowerState(true); // Pass true to indicate this is after a toggle action
                }, 2000);
            } else {
                console.error(`Error: ${data.message}`);
                showNotification('Error switching machine', 'error');
                
                // Reset indicator without changing state
                machineIndicator.style.transform = 'scale(1)';
                machineIndicator.style.opacity = '1';
            }
        })
        .catch(error => {
            // End loading state
            machineSwitch.classList.remove('loading');
            
            console.error('Error:', error);
            showNotification('Network error', 'error');
            
            // Reset indicator without changing state
            machineIndicator.style.transform = 'scale(1)';
            machineIndicator.style.opacity = '1';
        });
    }

    // Emergency stop button - also with hold to activate
    if (emergencyStop) {
        emergencyStop.addEventListener('mousedown', function(e) {
            // Only allow toggle if machine is connected
            if (!isMachineConnected) {
                showNotification('Machine not connected', 'error');
                return;
            }
            
            // Start the hold timer
            let holdDuration = 0;
            const requiredHoldTime = 750; // 0.75 seconds for emergency
            let holdInterval;
            
            // Create progress overlay if it doesn't exist yet
            let progressOverlay = this.querySelector('.hold-progress');
            if (!progressOverlay) {
                progressOverlay = document.createElement('div');
                progressOverlay.className = 'hold-progress';
                progressOverlay.style.position = 'absolute';
                progressOverlay.style.bottom = '0';
                progressOverlay.style.left = '0';
                progressOverlay.style.height = '100%';
                progressOverlay.style.width = '0%';
                progressOverlay.style.backgroundColor = 'rgba(255, 69, 58, 0.4)';
                progressOverlay.style.borderRadius = 'inherit';
                progressOverlay.style.transition = 'width 0.05s linear';
                progressOverlay.style.zIndex = '0';
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(progressOverlay);
            } else {
                // Reset existing progress
                progressOverlay.style.width = '0%';
                progressOverlay.style.display = 'block';
            }
            
            // Add a rapid pulsing effect
            this.classList.add('emergency-pulse');
            // Create this style if not already added to document
            if (!document.querySelector('#emergency-pulse-style')) {
                const pulseStyle = document.createElement('style');
                pulseStyle.id = 'emergency-pulse-style';
                pulseStyle.textContent = `
                    .emergency-pulse {
                        animation: emergency-pulse-animation 0.5s infinite;
                    }
                    @keyframes emergency-pulse-animation {
                        0% { transform: scale(1); }
                        50% { transform: scale(0.95); box-shadow: 0 0 15px rgba(255, 69, 58, 0.8); }
                        100% { transform: scale(1); }
                    }
                `;
                document.head.appendChild(pulseStyle);
            }
            
            // Start the interval to update the progress
            holdInterval = setInterval(() => {
                holdDuration += 50;
                const percentage = Math.min((holdDuration / requiredHoldTime) * 100, 100);
                progressOverlay.style.width = `${percentage}%`;
                
                // Make the color more intense as it progresses
                progressOverlay.style.backgroundColor = `rgba(255, 69, 58, ${0.4 + (percentage / 100) * 0.4})`;
                
                // When hold time is reached, trigger the action
                if (holdDuration >= requiredHoldTime) {
                    clearInterval(holdInterval);
                    triggerEmergencyStop();
                }
            }, 50);
            
            // Function to handle mouseup and mouseleave
            const cancelHold = () => {
                clearInterval(holdInterval);
                if (progressOverlay) {
                    // Fade out the progress overlay
                    progressOverlay.style.transition = 'opacity 0.3s ease';
                    progressOverlay.style.opacity = '0';
                    setTimeout(() => {
                        progressOverlay.style.width = '0%';
                        progressOverlay.style.opacity = '1';
                        progressOverlay.style.transition = 'width 0.05s linear';
                        progressOverlay.style.display = 'none';
                    }, 300);
                }
                
                // Remove pulse effect
                this.classList.remove('emergency-pulse');
                
                // Remove the event listeners
                document.removeEventListener('mouseup', cancelHold);
                this.removeEventListener('mouseleave', cancelHold);
            };
            
            // Add event listeners to cancel on mouseup or mouseleave
            document.addEventListener('mouseup', cancelHold);
            this.addEventListener('mouseleave', cancelHold);
            
            // Prevent default to avoid text selection
            e.preventDefault();
        });
    }

    // Function to actually trigger the emergency stop
    function triggerEmergencyStop() {
        // Add loading state
        emergencyStop.classList.add('loading');
        
        // Add visual pulse effect (different from hold pulse)
        emergencyStop.classList.add('pulse');
        emergencyStop.classList.remove('emergency-pulse');
        
        // Send emergency stop AJAX request
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': 'emergency_stop',
                'com_port': getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            emergencyStop.classList.remove('loading');
            emergencyStop.classList.remove('pulse');
            
            if (data.status === 'success') {
                // Show notification
                showNotification('Emergency stop activated', 'warning');
                
                // Temporarily show visual indicator that we're in emergency mode
                // but don't update the actual state until verified
                machineIndicator.style.backgroundColor = '#ffcc00'; // Yellow for emergency mode
                machineIndicator.style.boxShadow = '0 0 10px rgba(255, 204, 0, 0.8)';
                machineIndicator.style.opacity = '0.7';
                
                // Check actual machine state after emergency stop
                setTimeout(() => {
                    checkMachinePowerState(true); // Use post-toggle check
                }, 1500);
            } else {
                console.error(`Error: ${data.message}`);
                showNotification('Error activating emergency stop', 'error');
            }
        })
        .catch(error => {
            // End loading state
            emergencyStop.classList.remove('loading');
            emergencyStop.classList.remove('pulse');
            
            console.error('Error:', error);
            showNotification('Network error', 'error');
        });
    }

    // Add event listeners for relay toggles
    document.querySelectorAll('.relay-toggle').forEach(button => {
        const relayNum = button.getAttribute('data-relay');
        if (!relayNum) return;

        button.addEventListener('click', function() {
            // Only allow toggle if relay is connected
            if (!isRelayConnected) {
                showNotification('Relay not connected', 'error');
                return;
            }
            // Call our new toggle function
            toggleRelay(relayNum);
            // Fetch ESP32 stats and relay states after toggle
            // In toggleRelay, after sending the toggle request:
            setTimeout(() => {
                updateESP32Stats();
            }, 150); // 700ms delay (tune as needed)
        });
    });
    
    // Connection test buttons
    if (machineTestConnection) {
        machineTestConnection.addEventListener('click', function() {
            this.classList.add('loading');
            
            // Use the port check function (already updates UI)
            checkMachinePort();
            
            // Remove loading state after a delay
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1500);
        });
    }
    
    if (relayTestConnection) {
        relayTestConnection.addEventListener('click', function() {
            this.classList.add('loading');
            
            // Use the port check function (already updates UI)
            checkRelayPort();
            
            // Remove loading state after a delay
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1500);
        });
    }
    
    // Function to update machine status based on power state
    function updateMachineStatus(isOn) {
        // Update other machine status indicators
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
    }
    
    // Function to stop all motor animations
    function stopAllMotorAnimations() {
        document.querySelectorAll('.fa-spin').forEach(element => {
            element.classList.remove('fa-spin');
        });
    }
    
    // Function to show notifications
    function showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
            
            // Add styles if not in stylesheet
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.padding = '12px 20px';
            notification.style.borderRadius = '8px';
            notification.style.color = '#fff';
            notification.style.fontWeight = '500';
            notification.style.zIndex = '9999';
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
            notification.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }
        
        // Set color based on notification type
        switch(type) {
            case 'success':
                notification.style.backgroundColor = '#34a853';
                break;
            case 'error':
                notification.style.backgroundColor = '#ea4335';
                break;
            case 'warning':
                notification.style.backgroundColor = '#fbbc04';
                break;
            default:
                notification.style.backgroundColor = '#1a73e8';
        }
        
        // Set message
        notification.textContent = message;
        
        // Show notification
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
        
        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateY(100px)';
            notification.style.opacity = '0';
        }, 3000);
    }
    
    // Initialize charts
    initCharts();
    
    // Function to initialize all charts
    function initCharts() {
        if (typeof Chart !== 'undefined') {
            // Motor performance chart
            const motorsCtx = document.getElementById('motors-chart');
            if (motorsCtx) {
                const motorChart = new Chart(motorsCtx, {
                    type: 'line',
                    data: {
                        labels: ['1m ago', '50s', '40s', '30s', '20s', '10s', 'Now'],
                        datasets: [{
                            label: 'Shutter Motor (RPM)',
                            data: [175, 178, 180, 182, 180, 179, 180],
                            borderColor: 'rgba(90, 200, 250, 1)',
                            backgroundColor: 'rgba(90, 200, 250, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }, {
                            label: 'Spool Motor (RPM)',
                            data: [59, 60, 62, 60, 61, 59, 60],
                            borderColor: 'rgba(255, 159, 10, 1)',
                            backgroundColor: 'rgba(255, 159, 10, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2.5,
                        scales: {
                            y: {
                                beginAtZero: false,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                align: 'end',
                                labels: {
                                    boxWidth: 10,
                                    usePointStyle: true
                                }
                            }
                        }
                    }
                });
                
                // Update chart periodically
                setInterval(() => {
                    if (isMachineOn) {
                        const shutterData = motorChart.data.datasets[0].data;
                        const spoolData = motorChart.data.datasets[1].data;
                        
                        // Shift all data points to the left
                        shutterData.shift();
                        spoolData.shift();
                        
                        // Add new random data point
                        shutterData.push(180 + (Math.random() * 5 - 2.5));
                        spoolData.push(60 + (Math.random() * 4 - 2));
                        
                        motorChart.update('none');
                    }
                }, 5000);
            }
            
            // System temperature chart
            const tempCtx = document.getElementById('temperature-chart');
            if (tempCtx) {
                const tempChart = new Chart(tempCtx, {
                    type: 'line',
                    data: {
                        labels: ['1m ago', '50s', '40s', '30s', '20s', '10s', 'Now'],
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: [37.8, 38.2, 38.5, 38.3, 38.0, 37.9, 38.1],
                            borderColor: 'rgba(255, 69, 58, 1)',
                            backgroundColor: 'rgba(255, 69, 58, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2.5,
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 35,
                                max: 42,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                align: 'end',
                                labels: {
                                    boxWidth: 10,
                                    usePointStyle: true
                                }
                            }
                        }
                    }
                });
                
                // Update chart periodically
                setInterval(() => {
                    if (isMachineOn) {
                        const data = tempChart.data.datasets[0].data;
                        
                        // Shift all data points to the left
                        data.shift();
                        
                        // Add new random data point
                        data.push(38 + (Math.random() * 1.5 - 0.75));
                        
                        tempChart.update('none');
                    }
                }, 5000);
            }
            
            // Developer temperature chart
            const devTempCtx = document.getElementById('developer-temp-chart');
            if (devTempCtx) {
                const hoursLabels = [];
                for (let i = 24; i >= 0; i--) {
                    hoursLabels.push(i === 0 ? 'Now' : `${i}h ago`);
                }
                
                const devTempChart = new Chart(devTempCtx, {
                    type: 'line',
                    data: {
                        labels: hoursLabels,
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: Array.from({length: 25}, () => 37 + Math.random() * 2),
                            borderColor: 'rgba(48, 209, 88, 1)',
                            backgroundColor: 'rgba(48, 209, 88, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2.5,
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 35,
                                max: 40,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    maxRotation: 0,
                                    autoSkip: true,
                                    maxTicksLimit: 8
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        } else {
            console.warn('Chart.js not loaded. Charts disabled.');
        }
    }
    
    // Update network latency periodically
    setInterval(() => {
        const pingValue = document.querySelector('.ping-value');
        if (pingValue) {
            const latency = 30 + Math.floor(Math.random() * 15);
            pingValue.textContent = `${latency}ms`;
            
            // Change color based on latency
            if (latency < 35) {
                pingValue.style.color = '#30d158';
            } else if (latency < 45) {
                pingValue.style.color = '#ffcc00';
            } else {
                pingValue.style.color = '#ff453a';
            }
        }
    }, 5000);
    
    // ESP32 stats periodic update
    function updateESP32Stats() {
        if (isRelayConnected) {
            // Fetch real ESP32 stats
            fetch('/get_all_states/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update ESP32 system stats
                    updateESP32StatsUI(data.data.system_stats);
                    
                    // Update relay states
                    updateRelayStatesUI(data.data.relay_states);
                    
                    // Update mode display
                    updateModeDisplay(data.data.current_mode);
                    
                    console.log("ESP32 stats and relay states updated from real data");
                } else {
                    console.error(`Error fetching ESP32 stats: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error fetching ESP32 stats:', error);
            });
        } else {
            // If not connected, use placeholder values
            const placeholders = {
                "cpu": "N/A",
                "temp": "N/A",
                "ram": "N/A",
                "uptime": "N/A",
                "voltage": "N/A"
            };
            updateESP32StatsUI(placeholders);
        }
        
        // Measure actual ESP32 ping latency
        if (isRelayConnected) {
            measureESP32Latency();
        }
    }
    
    // Update ESP32 stats in the UI
    function updateESP32StatsUI(stats) {
        // Temperature update
        const espTemp = document.querySelector('.esp-stat-item:nth-child(2) .esp-stat-value');
        const espTempBar = document.querySelector('.esp-stat-item:nth-child(2) .mini-progress-fill');
        if (espTemp && espTempBar && stats.temp) {
            // Extract numeric value from temperature (e.g., "42.5C" -> 42.5)
            const temp = parseFloat(stats.temp);
            if (!isNaN(temp)) {
                espTemp.textContent = stats.temp;
                espTempBar.style.width = `${Math.min(temp, 100)}%`;
            }
        }
        
        // CPU load/frequency update
        const espCPU = document.querySelector('.esp-stat-item:nth-child(1) .esp-stat-value');
        const espCPUBar = document.querySelector('.esp-stat-item:nth-child(1) .mini-progress-fill');
        if (espCPU && espCPUBar && stats.cpu) {
            // For CPU MHz, map to a percentage (240MHz max for ESP32)
            const cpuMHz = parseFloat(stats.cpu);
            if (!isNaN(cpuMHz)) {
                espCPU.textContent = stats.cpu;
                const cpuPercentage = (cpuMHz / 320) * 100; // Assuming 240MHz is max
                espCPUBar.style.width = `${Math.min(cpuPercentage, 100)}%`;
            }
        }
        
        // Free memory update
        const espMem = document.querySelector('.esp-stat-item:nth-child(3) .esp-stat-value');
        const espMemBar = document.querySelector('.esp-stat-item:nth-child(3) .mini-progress-fill');
        if (espMem && espMemBar && stats.ram) {
            espMem.textContent = stats.ram;
            // Extract numeric value from RAM (e.g., "124.6KB" -> 124.6)
            const ramKB = parseFloat(stats.ram);
            if (!isNaN(ramKB)) {
                // Assuming 320KB total RAM for ESP32
                const ramPercentage = (ramKB / 480) * 100;
                espMemBar.style.width = `${Math.min(ramPercentage, 100)}%`;
            }
        }
        
        // Uptime update
        const espUptime = document.querySelector('.esp-stat-item:nth-child(4) .esp-stat-value');
        if (espUptime && stats.uptime) {
            espUptime.textContent = stats.uptime;
        }
        
        // Voltage update
        const espVoltage = document.querySelector('.esp-stat-item:nth-child(5) .esp-stat-value');
        const espVoltageBar = document.querySelector('.esp-stat-item:nth-child(5) .mini-progress-fill');
        if (espVoltage && espVoltageBar && stats.voltage) {
            espVoltage.textContent = stats.voltage;
            // Extract numeric value from voltage (e.g., "3.3V" -> 3.3)
            const voltage = parseFloat(stats.voltage);
            if (!isNaN(voltage)) {
                // Map voltage to percentage (3.0V to 3.6V is typical ESP32 operating range)
                // This creates a meaningful display with normal voltage in the middle range
                const voltagePercentage = ((voltage - 3.0) / 0.6) * 100;
                espVoltageBar.style.width = `${Math.min(Math.max(voltagePercentage, 0), 100)}%`;
                
                // Add color coding for voltage
                if (voltage < 3.1) {
                    // Too low
                    espVoltageBar.style.backgroundColor = '#ff453a'; // red
                } else if (voltage > 3.5) {
                    // Too high
                    espVoltageBar.style.backgroundColor = '#ffcc00'; // yellow
                } else {
                    // Normal range
                    espVoltageBar.style.backgroundColor = ''; // default color
                }
            }
        }
    }

    // Update relay states in the UI
    function updateRelayStatesUI(newRelayStates) {
        if (!newRelayStates) return;
    
        if (Array.isArray(newRelayStates)) {
            newRelayStates.forEach((isOn, idx) => {
                const relayNum = idx + 1;
                const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
                if (relayIndicator) {
                    const currentState = relayIndicator.classList.contains('on');
                    // Check for pending state and discrepancy
                    if (pendingRelayStates[relayNum] !== undefined) {
                        if (pendingRelayStates[relayNum] !== isOn) {
                            console.log(`[updateRelayStatesUI] Relay ${relayNum}: Hardware mismatch (pending=${pendingRelayStates[relayNum]}, actual=${isOn}) - reverting UI`);
                            console.log(`[updateRelayStatesUI] Before update: relayNum=${relayNum}, classList=${relayIndicator.className}`);
                            setRelayIndicatorState(relayNum, isOn, false);
                            console.log(`[updateRelayStatesUI] After update: relayNum=${relayNum}, classList=${relayIndicator.className}`);
                            showNotification(`Relay ${relayNum} state reverted (hardware mismatch)`, 'warning');
                        } else {
                            console.log(`[updateRelayStatesUI] Relay ${relayNum}: Pending state confirmed (state=${isOn}) - updating UI`);
                            setRelayIndicatorState(relayNum, isOn, false);
                        }
                        // Remove pending state after confirmation
                        delete pendingRelayStates[relayNum];
                    } else if (currentState !== isOn) {
                        console.log(`[updateRelayStatesUI] Relay ${relayNum}: UI out of sync (current=${currentState}, actual=${isOn}) - updating UI`);
                        setRelayIndicatorState(relayNum, isOn, false);
                    } else {
                        console.log(`[updateRelayStatesUI] Relay ${relayNum}: No update needed (current=${currentState}, actual=${isOn})`);
                    }
                }
            });
        } else {
            Object.entries(newRelayStates).forEach(([relayNum, isOn]) => {
                const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
                if (relayIndicator) {
                    const currentState = relayIndicator.classList.contains('on');
                    if (pendingRelayStates[relayNum] !== undefined) {
                        if (pendingRelayStates[relayNum] !== isOn) {
                            console.log(`[updateRelayStatesUI] Relay ${relayNum}: Hardware mismatch (pending=${pendingRelayStates[relayNum]}, actual=${isOn}) - reverting UI`);
                            console.log(`[updateRelayStatesUI] Before update: relayNum=${relayNum}, classList=${relayIndicator.className}`);
                            setRelayIndicatorState(relayNum, isOn, false);
                            console.log(`[updateRelayStatesUI] After update: relayNum=${relayNum}, classList=${relayIndicator.className}`);
                            showNotification(`Relay ${relayNum} state reverted (hardware mismatch)`, 'warning');
                        } else {
                            console.log(`[updateRelayStatesUI] Relay ${relayNum}: Pending state confirmed (state=${isOn}) - updating UI`);
                            setRelayIndicatorState(relayNum, isOn, false);
                        }
                        delete pendingRelayStates[relayNum];
                    } else if (currentState !== isOn) {
                        console.log(`[updateRelayStatesUI] Relay ${relayNum}: UI out of sync (current=${currentState}, actual=${isOn}) - updating UI`);
                        setRelayIndicatorState(relayNum, isOn, false);
                    } else {
                        console.log(`[updateRelayStatesUI] Relay ${relayNum}: No update needed (current=${currentState}, actual=${isOn})`);
                    }
                }
            });
        }
        
        // Log relay 8 state changes but don't update machine power UI
        if (newRelayStates[8] !== undefined) {
            const relay8State = newRelayStates[8] === true;
            console.log(`Machine power relay (8) state: ${relay8State ? 'ON' : 'OFF'}`);
            
            // Only update internal relay state tracking, don't update UI or actual machine power state
            if (relay8State !== relayStates[8]) {
                console.log(`Relay 8 state changed from ${relayStates[8] ? 'ON' : 'OFF'} to ${relay8State ? 'ON' : 'OFF'}`);
                // Update our internal tracking of relay states
                relayStates[8] = relay8State;
                
                // If this was a manual relay toggle operation, trigger a machine state verification
                // But DON'T update the UI yet - wait for the verification result
                if (isMachineConnected) {
                    console.log("Triggering machine power state verification after relay change");
                    setTimeout(() => checkMachinePowerState(false), 1000);
                    console.log("Machine power state verification triggered");
                }
            }
        }
    }
    
    // Update the light/dark mode display
    function updateModeDisplay(mode) {
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
    }
    
    // Toggle mode (light/dark) for the relay
    function toggleRelayMode() {
        if (!isRelayConnected) {
            showNotification('Relay not connected', 'error');
            return;
        }
        
        // Disable button during the mode change
        if (modeToggle) {
            modeToggle.disabled = true;
            modeToggle.classList.add('loading');
        }
        
        // Get current mode and determine target mode
        const currentModeIcon = document.getElementById('mode-indicator');
        const targetMode = currentModeIcon && currentModeIcon.classList.contains('fa-sun') ? 'dark' : 'light';
        
        console.log(`Toggling relay mode to: ${targetMode}`);
        
        // Send the mode toggle request to the server
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': targetMode,
                'com_port': getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update UI to match the new mode
                updateModeDisplay(data.mode);

                // If server returned relay states, update those too
                if (data.relay_states) {
                    updateRelayStatesUI(data.relay_states);
                }

                showNotification(`${targetMode.charAt(0).toUpperCase() + targetMode.slice(1)} activated`, 'success');
                console.log(`${targetMode} mode activated successfully`);
            } else {
                showNotification(`Failed to change mode: ${data.message}`, 'error');
                console.error(`Error toggling mode: ${data.message}`);
            }
        })
        .catch(error => {
            showNotification('Error toggling mode', 'error');
            console.error('Error toggling mode:', error);
        })
        .finally(() => {
            // Re-enable button and remove loading state
            if (modeToggle) {
                modeToggle.disabled = false;
                modeToggle.classList.remove('loading');
            }
        });
    }
    
    // Toggle individual relay
    function toggleRelay(relayNum) {
        if (!isRelayConnected) {
            showNotification('Relay not connected', 'error');
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
        
        // Send the relay control request
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': action,
                'relay': relayNum,
                'com_port': getActiveRelayPort()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // If server returned relay states, update UI
                if (data.relay_states) {
                    updateRelayStatesUI(data.relay_states);
                } else {
                    // Otherwise update just this relay
                    if (action === 'on') {
                        relayIndicator.classList.add('on');
                    } else {
                        relayIndicator.classList.remove('on');
                    }
                }
                
                showNotification(`Relay ${relayNum} turned ${action.toUpperCase()}`, 'success');
            } else {
                showNotification(`Failed to control relay: ${data.message}`, 'error');
                console.error(`Error controlling relay: ${data.message}`);
            }
        })
        .catch(error => {
            showNotification('Error controlling relay', 'error');
            console.error('Error controlling relay:', error);
        })
        .finally(() => {
            // Remove loading state
            if (relayButton) {
                relayButton.disabled = false;
                relayButton.classList.remove('loading');
            }
        });
    }
    
    // Function to check relay states periodically with redundancy prevention
    function checkRelayStates() {
        if (!isRelayConnected) return;
        
        console.log("Checking relay states...");
        
        fetch('/get_all_states/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.data) {
                // Update relay states if available
                if (data.data.relay_states) {
                    // Compare with current states before updating
                    const hasChanges = Object.entries(data.data.relay_states).some(([key, value]) => {
                        // Check if the relay state has changed
                        return relayStates[key] !== value;
                    });
                    
                    if (hasChanges) {
                        // Only update UI if there are actual changes
                        Object.assign(relayStates, data.data.relay_states);
                        updateRelayStatesUI(data.data.relay_states);
                        console.log("Relay states updated due to changes detected");
                    } else {
                        console.log("No changes in relay states, skipping UI update");
                    }
                }
                
                // Update system stats if available
                if (data.data.system_stats) {
                    updateESP32StatsUI(data.data.system_stats);
                }
            } else {
                console.error(`Error or missing data: ${data.message || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error('Error checking states:', error);
        });
    }

    // Function to measure actual ESP32 latency
    function measureESP32Latency() {
        lastPingTime = performance.now();
        
        // Send a simple ping request to the relay controller
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': 'ping',
                'com_port': getActiveRelayPort()
            })
        })
        .then(response => {
            // Calculate round-trip time
            const pingLatency = Math.round(performance.now() - lastPingTime);
            
            // Update latency display
            updateLatencyDisplay(pingLatency);
            
            return response.json();
        })
        .catch(error => {
            console.error('Error pinging ESP32:', error);
            // If error, show high latency
            updateLatencyDisplay(999);
        });
    }
    
    // Function to update the latency display
    function updateLatencyDisplay(latency) {
        if (pingValue) {
            pingValue.textContent = `${latency}ms`;
            
            // Change color based on latency
            if (latency < 50) {
                pingValue.style.color = '#30d158'; // Good (green)
            } else if (latency < 100) {
                pingValue.style.color = '#ffcc00'; // Warning (yellow)
            } else {
                pingValue.style.color = '#ff453a'; // Poor (red)
            }
        }
    }
    
    // Initialize the overall system status on page load
    updateSystemStatus();
    
    // Set a slower interval for the latency test (since we're doing real measurements)
    setInterval(() => {
        if (isRelayConnected) {
            measureESP32Latency();
        } else if (pingValue) {
            // If relay is not connected, show N/A
            pingValue.textContent = 'N/A';
            pingValue.style.color = '#ff453a';
        }
    }, 10000); // Check every 10 seconds
    
    // Check relay states periodically
    setInterval(checkRelayStates, 30000); // Every 30 seconds

    // Set transition styles for panels and elements
    if (relayControls) {
    relayControls.style.transition = `opacity ${TRANSITION_DURATION}ms ease, transform ${TRANSITION_DURATION}ms ease`;
    }
    if (modeIndicator) {
    modeIndicator.style.transition = `transform ${TRANSITION_DURATION}ms ease, opacity ${TRANSITION_DURATION}ms ease, color ${TRANSITION_DURATION}ms ease`;
    }
    if (machineIndicator) {
    machineIndicator.style.transition = `transform ${TRANSITION_DURATION}ms ease, opacity ${TRANSITION_DURATION}ms ease, background-color ${TRANSITION_DURATION}ms ease, box-shadow ${TRANSITION_DURATION}ms ease`;
    }
    
    // Add dynamic styles for loading state
    const style = document.createElement('style');
    style.textContent = `
        .loading {
            position: relative;
            pointer-events: none;
        }
        .loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.4);
            border-radius: inherit;
        }
        .dark-mode .loading::after {
            background: rgba(0, 0, 0, 0.4);
        }
    `;
    document.head.appendChild(style);

    // Helper function to get the active COM port for relay
    function getActiveRelayPort() {
        const relayPort = document.getElementById('relay-port');
        if (relayPort && isRelayConnected && relayPort.textContent !== 'N/A') {
            return relayPort.textContent;
        }
        return 'COM18'; // Default fallback to COM18
    }

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
    
    // New helper function to clear relay info fields
    function clearRelayInfo() {
        const relayPort = document.getElementById('relay-port');
        const relayVendor = document.getElementById('relay-vendor');
        const relayProductId = document.getElementById('relay-product-id');
        const relayProduct = document.getElementById('relay-product');
        
        if (relayPort) relayPort.textContent = 'N/A';
        if (relayVendor) relayVendor.textContent = 'N/A';
        if (relayProductId) relayProductId.textContent = 'N/A';
        if (relayProduct) relayProduct.textContent = 'N/A';
    }
    
    // New helper function to update relay info fields
    function updateRelayInfo(port) {
        const relayPort = document.getElementById('relay-port');
        const relayVendor = document.getElementById('relay-vendor');
        const relayProductId = document.getElementById('relay-product-id');
        const relayProduct = document.getElementById('relay-product');
        
        if (relayPort) relayPort.textContent = port;
        if (relayVendor) relayVendor.textContent = '0x1A86 (Qinheng)';
        if (relayProductId) relayProductId.textContent = '0x7523';
        if (relayProduct) relayProduct.textContent = 'USB-SERIAL CH340';
    }

    // New helper function to update machine info fields from device data
    function updateMachineInfoFromData(deviceInfo) {
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
    }
    
    // New helper function to update relay info fields from device data
    function updateRelayInfoFromData(deviceInfo) {
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
    }

    // Helper function to compare device info objects
    function isEqualDeviceInfo(obj1, obj2) {
        // Compare the most important fields for equality
        const fieldsToCompare = ['port', 'vendor_id', 'product_id', 'product', 'serial_number'];
        
        for (const field of fieldsToCompare) {
            if (obj1[field] !== obj2[field] && obj1[field] !== undefined && obj2[field] !== undefined) {
                return false;
            }
        }
        
        return true;
    }

    // Function to update overall system status indicator
    function updateSystemStatus() {
        if (systemStatusIndicator && systemStatusLabel) {
            // Determine status based on connections
            if (isMachineConnected && isRelayConnected) {
                // All systems online
                systemStatusIndicator.classList.remove('warning', 'offline');
                systemStatusIndicator.classList.add('online');
                systemStatusLabel.textContent = 'System Online';
            } else if (!isMachineConnected && !isRelayConnected) {
                // All systems offline
                systemStatusIndicator.classList.remove('online', 'warning');
                systemStatusIndicator.classList.add('offline');
                systemStatusLabel.textContent = 'System Offline';
            } else {
                // Partial connectivity - warning state
                systemStatusIndicator.classList.remove('online', 'offline');
                systemStatusIndicator.classList.add('warning');
                
                if (!isMachineConnected) {
                    systemStatusLabel.textContent = 'Machine Disconnected';
                } else {
                    systemStatusLabel.textContent = 'Relay Disconnected';
                }
            }
        }
    }

    // Machine stats button
    const machineStatsButton = document.getElementById('machine-stats-button');
    if (machineStatsButton) {
        machineStatsButton.addEventListener('click', function() {
            // Use the toggleMachineStatsCard function
            toggleMachineStatsCard();
        });
    }

    // Function to fetch machine stats
    function fetchMachineStats() {
        // Get the stats card (no loading state will be added)
        const statsCard = document.getElementById('machine-stats-card');
        
        fetch('/get_machine_stats/', {
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
            console.log('Received machine stats data:', data);
            
            if (data.status === 'success') {
                // Use the data directly from the response
                updateMachineStatsUI(data.data);
            } else {
                console.error(`Error fetching machine stats: ${data.message}`);
                showNotification('Failed to fetch machine stats', 'error');
            }
        })
        .catch(error => {
            console.error('Error fetching machine stats:', error);
            showNotification('Network error while fetching machine stats', 'error');
        });
    }
    
    // Function to update machine stats UI with placeholder data for disconnected state
    function updateMachineStatsUIPlaceholders() {
        // System gauge placeholders
        updateMachineGauge('voltage-value', null, 0, 50, 'V', null, true);
        updateMachineGauge('temp-value', null, 0, 100, '°C', null, true);
        
        // Motor placeholders for all three motors
        for (let i = 0; i < 3; i++) {
            // Update gauges with placeholder data
            updateMachineGauge(`motor${i}-speed-value`, null, 0, 1000, 'RPM', null, true);
            updateMachineGauge(`motor${i}-current-value`, null, 0, 2500, 'mA', null, true);
            
            // Update position display with placeholder
            updatePositionDisplay(`motor${i}-position`, 'N/A', true);
            
            // Update motor state indicator to show disconnected
            updateMotorStateIndicator(`motor${i}-state`, 'disconnected');
        }
        
        // Update connection status badge to show disconnected
        const statsConnectionStatus = document.getElementById('stats-connection-status');
        if (statsConnectionStatus) {
            statsConnectionStatus.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
            statsConnectionStatus.className = 'status-badge critical';
        }
    }

    // Add tooltips to disconnected elements
    function addDisconnectedTooltips() {
        // For gauge placeholders
        document.querySelectorAll('.gauge.placeholder').forEach(function(element) {
            if (!element.classList.contains('tooltip')) {
                element.classList.add('tooltip');
                const tooltipSpan = document.createElement('span');
                tooltipSpan.className = 'tooltip-text';
                tooltipSpan.textContent = 'Connect to a machine to view real-time data';
                element.appendChild(tooltipSpan);
            }
        });
        
        // For disconnected motor states
        document.querySelectorAll('.motor-state.disconnected').forEach(function(element) {
            if (!element.classList.contains('tooltip')) {
                element.classList.add('tooltip');
                const tooltipSpan = document.createElement('span');
                tooltipSpan.className = 'tooltip-text';
                tooltipSpan.textContent = 'Motor status will be shown when connected';
                element.appendChild(tooltipSpan);
            }
        });
    }

    // Function to update machine stats UI
    function updateMachineStatsUI(stats) {
        try {
            // Check if the data is valid
            if (!stats || typeof stats !== 'object') {
                console.error('Invalid machine stats data:', stats);
                return;
            }

            console.log('Updating machine stats UI with data:', stats);
            
            // Update voltage (directly from flat structure)
            if (stats.voltage !== undefined) {
                updateMachineGauge('voltage-value', stats.voltage, 0, 50, 'V', [
                    { percentage: 33, color: '#ff453a' },  // Low voltage (red)
                    { percentage: 66, color: '#ffcc00' },  // Medium voltage (yellow)
                    { percentage: 100, color: '#30d158' }  // High voltage (green)
                ]);
            }
            
            // Update temperature (directly from flat structure)
            if (stats.temperature !== undefined) {
                // Divide by 100 if temperature is above 1000 (assuming it's in millidegrees)
                const tempValue = stats.temperature > 1000 ? stats.temperature / 100 : stats.temperature;
                updateMachineGauge('temp-value', tempValue, 0, 100, '°C', [
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
                    updateMachineGauge(`motor${i}-speed-value`, stats[`motor${i}_speed`], 0, 1000, 'RPM', [
                        { percentage: 33, color: '#30d158' },  // Low speed (green)
                        { percentage: 66, color: '#ffcc00' },  // Medium speed (yellow)
                        { percentage: 100, color: '#ff453a' }  // High speed (red)
                    ]);
                }
                
                if (stats[`motor${i}_current`] !== undefined) {
                    // Update current gauge
                    updateMachineGauge(`motor${i}-current-value`, stats[`motor${i}_current`], 0, 2500, 'mA', [
                        { percentage: 33, color: '#30d158' },  // Low current (green)
                        { percentage: 66, color: '#ffcc00' },  // Medium current (yellow)
                        { percentage: 100, color: '#ff453a' }  // High current (red)
                    ]);
                }
                
                if (stats[`motor${i}_position`] !== undefined) {
                    // Update position display
                    updatePositionDisplay(`motor${i}-position`, stats[`motor${i}_position`]);
                }
                
                if (stats[`motor${i}_state`] !== undefined) {
                    // Update motor state indicator
                    updateMotorStateIndicator(`motor${i}-state`, stats[`motor${i}_state`]);
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
    }
    
    // Helper function to update a gauge
    function updateMachineGauge(gaugeId, value, min, max, unit, colorStops, isPlaceholder = false) {
        console.log(`Updating gauge ${gaugeId} with value ${value}`);
        
        // Get the value element
        const valueElement = document.getElementById(gaugeId);
        
        if (!valueElement) {
            console.warn(`Element with ID ${gaugeId} not found`);
            return;
        }
        
        // Get the fill element ID
        // If ID is something like 'motor0-speed-value', the fill ID should be 'motor0-speed-fill'
        let fillId;
        if (gaugeId.endsWith('-value')) {
            fillId = gaugeId.replace('-value', '-fill');
        } else {
            fillId = gaugeId + '-fill';
        }
        
        const fillElement = document.getElementById(fillId);
        
        if (!fillElement) {
            console.warn(`Fill element with ID ${fillId} not found for gauge ${gaugeId}`);
        }
        
        // Format the value display with units
        const displayValue = (isPlaceholder || value === null || value === undefined) 
            ? `N/A ${unit}` 
            : `${value} ${unit}`;
        
        // Update the displayed value
        valueElement.innerText = displayValue;
        
        // Add or remove placeholder styling
        if (isPlaceholder) {
            valueElement.classList.add('placeholder');
        } else {
            valueElement.classList.remove('placeholder');
        }
        
        // If we have access to a fill element, update it
        if (fillElement && !isPlaceholder && value !== null && value !== undefined) {
            // Calculate percentage for the progress bar
            let percentage = ((value - min) / (max - min)) * 100;
            percentage = Math.max(0, Math.min(100, percentage)); // Clamp between 0-100%
            
            console.log(`Setting ${fillId} width to ${percentage}%`);
            
            // Apply the percentage to the fill element
            fillElement.style.width = `${percentage}%`;
            
            // Apply color stops if provided
            if (colorStops) {
                // Find the color based on the percentage
                let color = '#5ac8fa'; // Default color
                
                for (const stop of colorStops) {
                    if (percentage <= stop.percentage) {
                        color = stop.color;
                        break;
                    }
                }
                
                fillElement.style.backgroundColor = color;
            }
        } else if (fillElement && isPlaceholder) {
            // Set width to 0 for placeholder
            fillElement.style.width = '0%';
        }
    }
    
    // Helper function to update position display
    function updatePositionDisplay(elementId, position, isPlaceholder = false) {
        console.log(`Updating position display ${elementId} with value ${position}`);
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Position display element with ID ${elementId} not found`);
            return;
        }
        
        // Update the text content
        element.innerText = isPlaceholder ? 'N/A' : position;
        
        // Add or remove placeholder styling
        if (isPlaceholder) {
            element.classList.add('placeholder');
        } else {
            element.classList.remove('placeholder');
        }
    }
    
    // Helper function to update motor state indicator
    function updateMotorStateIndicator(elementId, state) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // Reset classes
        element.classList.remove('stopped', 'running-cw', 'running-ccw', 'error', 'disconnected');
        
        // Add appropriate class
        element.classList.add(state);
        
        // Update text
        let stateText = 'Stopped';
        let icon = '<i class="fas fa-stop-circle"></i>';
        
        switch (state) {
            case 'running-cw':
                stateText = 'Running CW';
                icon = '<i class="fas fa-arrow-circle-right fa-spin"></i>';
                break;
            case 'running-ccw':
                stateText = 'Running CCW';
                icon = '<i class="fas fa-arrow-circle-left fa-spin"></i>';
                break;
            case 'error':
                stateText = 'Error';
                icon = '<i class="fas fa-exclamation-circle"></i>';
                break;
            case 'disconnected':
                stateText = 'Disconnected';
                icon = '<i class="fas fa-unlink"></i>';
                break;
        }
        
        element.innerHTML = `${icon} ${stateText}`;
    }

    /**
     * Toggles the visibility of the machine stats card.
     * If the machine is connected, it shows the stats card and starts polling for stats.
     * If the machine is disconnected, it shows the stats card with placeholder data.
     */
    function toggleMachineStatsCard() {
        const statsCard = document.getElementById('machine-stats-card');
        const relayCard = document.getElementById('relay-controls');
        
        if (statsCard) {
            // Toggle visibility
            if (statsCard.style.display === 'none') {
                // Remove any existing animation classes
                statsCard.classList.remove('animate-in');
                statsCard.classList.remove('card-reveal');
                
                // Show the stats card and set active status
                statsCard.style.display = 'block';
                statsCard.classList.add('active');
                
                // If relay card is also visible, adjust z-index
                if (relayCard && relayCard.style.display !== 'none') {
                    relayCard.classList.remove('active');
                }
                
                // Add animation after a tiny delay to ensure display change is applied
                setTimeout(function() {
                    statsCard.classList.add('card-reveal');
                }, 10);
                
                // Update the connection status on the stats card
                const statsConnectionStatus = document.getElementById('stats-connection-status');
                if (statsConnectionStatus) {
                    if (isMachineConnected) {
                        statsConnectionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
                        statsConnectionStatus.className = 'status-badge operational';
                        // Fetch machine stats once when opening
                        fetchMachineStats();
                    } else {
                        statsConnectionStatus.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
                        statsConnectionStatus.className = 'status-badge critical';
                        // Display placeholders for disconnected state
                        updateMachineStatsUIPlaceholders();
                    }
                }
            } else {
                // Hide the stats card
                statsCard.style.display = 'none';
                statsCard.classList.remove('active');
                statsCard.classList.remove('card-reveal');
            }
        }
    }

    // Add refresh button click handler for machine stats
    document.querySelectorAll('.refresh-button').forEach(function(button) {
        button.addEventListener('click', function() {
            if (isMachineConnected) {
                fetchMachineStats();
            }
        });
    });

    /**
     * Toggles the visibility of the relay controls card.
     * Handles animation effects and z-index with the machine stats card.
     */
    function toggleRelayControlsCard() {
        const relayCard = document.getElementById('relay-controls');
        const statsCard = document.getElementById('machine-stats-card');
        
        if (relayCard) {
            // Toggle visibility
            if (relayCard.style.display === 'none') {
                // Remove any existing animation classes
                relayCard.classList.remove('card-reveal');
                
                // Show the relay card and set active status
                relayCard.style.display = 'block';
                relayCard.classList.add('active');
                
                // If stats card is also visible, adjust z-index
                if (statsCard && statsCard.style.display !== 'none') {
                    statsCard.classList.remove('active');
                }
                
                // Add animation after a tiny delay to ensure display change is applied
                setTimeout(function() {
                    relayCard.classList.add('card-reveal');
                }, 10);
            } else {
                // Hide the relay card
                relayCard.style.display = 'none';
                relayCard.classList.remove('active');
                relayCard.classList.remove('card-reveal');
            }
        }
    }

    // Add close button event listeners
    const statsCloseBtn = document.getElementById('stats-close-btn');
    if (statsCloseBtn) {
        statsCloseBtn.addEventListener('click', function() {
            const statsCard = document.getElementById('machine-stats-card');
            if (statsCard) {
                statsCard.style.display = 'none';
                statsCard.classList.remove('active');
                statsCard.classList.remove('card-reveal');
            }
        });
    }
    
    const relayCloseBtn = document.getElementById('relay-close-btn');
    if (relayCloseBtn) {
        relayCloseBtn.addEventListener('click', function() {
            const relayCard = document.getElementById('relay-controls');
            if (relayCard) {
                relayCard.style.display = 'none';
                relayCard.classList.remove('active');
                relayCard.classList.remove('card-reveal');
            }
        });
    }
    
    // Add refresh button click handler for machine stats
    document.querySelectorAll('.refresh-button').forEach(function(button) {
        button.addEventListener('click', function() {
            if (isMachineConnected) {
                fetchMachineStats();
            }
        });
    });

    /**
     * Sets the visual state of a relay indicator.
     * @param {number|string} relayNum - The relay number (1-based).
     * @param {boolean} isOn - True if the relay should be shown as ON.
     * @param {boolean} pending - If true, show a "pending" state (e.g., yellow).
     */
    function setRelayIndicatorState(relayNum, isOn, pending = false) {
        const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
        if (!relayIndicator) {
            console.warn(`[setRelayIndicatorState] Relay indicator not found for relayNum=${relayNum}`);
            return;
        }

        // Remove all possible state classes
        relayIndicator.classList.remove('on', 'pending');

        if (pending) {
            console.log(`[setRelayIndicatorState] Relay ${relayNum}: PENDING (yellow)`);
            relayIndicator.classList.add('pending');
            relayIndicator.style.backgroundColor = '#ffcc00'; // yellow for pending
        } else if (isOn) {
            console.log(`[setRelayIndicatorState] Relay ${relayNum}: ON (green)`);
            relayIndicator.classList.add('on');
            relayIndicator.style.backgroundColor = ''; // reset to default
        } else {
            relayIndicator.classList.remove('on');
            relayIndicator.style.backgroundColor = ''; // reset to default
        }
    }
});