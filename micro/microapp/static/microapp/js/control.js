// Control Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const relayControls = document.getElementById('relay-controls');
    const settingsSection = document.getElementById('settings-section');
    const settingsToggle = document.getElementById('settings-toggle');
    const modeToggle = document.getElementById('mode-toggle');
    const modeIndicator = document.getElementById('mode-indicator');
    const machineSwitch = document.getElementById('machine-switch');
    const machineIndicator = document.getElementById('machine-indicator');
    const emergencyStop = document.getElementById('emergency-stop');
    
    // State variables
    let isLightMode = true;
    let isMachineOn = false;
    const relayStates = {};
    
    // Animation settings
    const TRANSITION_DURATION = 300; // ms

    // Toggle settings and relay controls visibility with animation
    settingsToggle.addEventListener('click', function() {
        // Animate settings icon rotation
        this.style.transform = this.style.transform === 'rotate(90deg)' ? 'rotate(0deg)' : 'rotate(90deg)';
        
        const isVisible = relayControls.style.display === 'none' || relayControls.style.display === '';
        
        // Show/hide elements with animation
        if (isVisible) {
            // First set display to block with opacity 0
            relayControls.style.display = 'block';
            settingsSection.style.display = 'block';
            relayControls.style.opacity = '0';
            settingsSection.style.opacity = '0';
            relayControls.style.transform = 'translateY(10px)';
            settingsSection.style.transform = 'translateY(10px)';
            
            // Then animate in
            setTimeout(() => {
                relayControls.style.opacity = '1';
                settingsSection.style.opacity = '1';
                relayControls.style.transform = 'translateY(0)';
                settingsSection.style.transform = 'translateY(0)';
            }, 10);
        } else {
            // Animate out then hide
            relayControls.style.opacity = '0';
            settingsSection.style.opacity = '0';
            relayControls.style.transform = 'translateY(10px)';
            settingsSection.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                relayControls.style.display = 'none';
                settingsSection.style.display = 'none';
            }, TRANSITION_DURATION);
        }
    });

    // Toggle light/dark mode with animation
    modeToggle.addEventListener('click', function() {
        isLightMode = !isLightMode;
        const action = isLightMode ? 'light' : 'dark';
        
        // Animate the mode indicator
        modeIndicator.style.transform = 'rotate(180deg) scale(0.5)';
        modeIndicator.style.opacity = '0';
        
        setTimeout(() => {
            // Update the icon
            modeIndicator.classList.toggle('fa-sun', isLightMode);
            modeIndicator.classList.toggle('fa-moon', !isLightMode);
            modeIndicator.style.color = isLightMode ? '#ffcc00' : '#c4c9cd';
            
            // Reset and apply new animation
            modeIndicator.style.transform = 'rotate(0) scale(1)';
            modeIndicator.style.opacity = '1';
            
            // Toggle dark mode on body
            document.body.classList.toggle('dark-mode', !isLightMode);
            
            console.log(`${action.charAt(0).toUpperCase() + action.slice(1)} mode activated`);
            
            // Send AJAX request to toggle light/dark mode
            fetch('/control_relay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'action': action,
                    'com_port': document.getElementById('com-port').value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== 'success') {
                    console.error(`Error: ${data.message}`);
                    // Show error feedback to the user
                    showNotification('Error switching mode', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Network error', 'error');
            });
        }, TRANSITION_DURATION / 2);
    });

    // Toggle machine switch with animation
    machineSwitch.addEventListener('click', function() {
        isMachineOn = !isMachineOn;
        const action = isMachineOn ? 'machine_on' : 'machine_off';
        
        // Start loading state
        this.classList.add('loading');
        
        // Animate the indicator
        machineIndicator.style.transform = 'scale(0.5)';
        machineIndicator.style.opacity = '0.5';
        
        console.log(`Machine ${isMachineOn ? 'turned on' : 'turned off'}`);

        // Send AJAX request to toggle machine switch
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': action,
                'com_port': document.getElementById('com-port').value
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            this.classList.remove('loading');
            
            if (data.status === 'success') {
                // Update UI with animation
                machineIndicator.style.backgroundColor = isMachineOn ? '#30d158' : '#ff453a';
                machineIndicator.style.boxShadow = isMachineOn 
                    ? '0 0 8px rgba(48, 209, 88, 0.5)' 
                    : '0 0 6px rgba(255, 69, 58, 0.5)';
                
                // Toggle class for styling
                machineIndicator.classList.toggle('on', isMachineOn);
                
                // Reset and apply new animation
                setTimeout(() => {
                    machineIndicator.style.transform = 'scale(1.2)';
                    machineIndicator.style.opacity = '1';
                    
                    setTimeout(() => {
                        machineIndicator.style.transform = 'scale(1)';
                    }, 200);
                }, 50);
                
                // Update machine status badges
                updateMachineStatus(isMachineOn);
                
                showNotification(`Machine ${isMachineOn ? 'turned on' : 'turned off'}`, 'success');
            } else {
                console.error(`Error: ${data.message}`);
                isMachineOn = !isMachineOn; // Revert state on error
                showNotification('Error switching machine', 'error');
                
                // Reset indicator
                machineIndicator.style.transform = 'scale(1)';
                machineIndicator.style.opacity = '1';
            }
        })
        .catch(error => {
            // End loading state
            this.classList.remove('loading');
            
            console.error('Error:', error);
            isMachineOn = !isMachineOn; // Revert state on error
            showNotification('Network error', 'error');
            
            // Reset indicator
            machineIndicator.style.transform = 'scale(1)';
            machineIndicator.style.opacity = '1';
        });
    });
    
    // Emergency stop button
    emergencyStop.addEventListener('click', function() {
        this.classList.add('loading');
        
        // Add visual pulse effect
        this.classList.add('pulse');
        
        // Send emergency stop AJAX request
        fetch('/control_relay/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'action': 'emergency_stop',
                'com_port': document.getElementById('com-port').value
            })
        })
        .then(response => response.json())
        .then(data => {
            // End loading state
            this.classList.remove('loading');
            this.classList.remove('pulse');
            
            if (data.status === 'success') {
                // Update all machine states to show stopped state
                isMachineOn = false;
                machineIndicator.style.backgroundColor = '#ff453a';
                machineIndicator.style.boxShadow = '0 0 6px rgba(255, 69, 58, 0.5)';
                machineIndicator.classList.remove('on');
                
                // Update all status badges
                updateMachineStatus(false);
                
                // Reset all motor animations
                stopAllMotorAnimations();
                
                showNotification('Emergency stop activated', 'warning');
            } else {
                console.error(`Error: ${data.message}`);
                showNotification('Error activating emergency stop', 'error');
            }
        })
        .catch(error => {
            // End loading state
            this.classList.remove('loading');
            this.classList.remove('pulse');
            
            console.error('Error:', error);
            showNotification('Network error', 'error');
        });
    });

    // Add event listeners for relay toggles
    document.querySelectorAll('.relay-toggle').forEach(button => {
        const relay = button.getAttribute('data-relay');
        const indicator = document.getElementById(`relay-indicator-${relay}`);
        relayStates[relay] = false; // Initialize relay state

        button.addEventListener('click', function() {
            console.log(`Button for relay ${relay} clicked`);
            relayStates[relay] = !relayStates[relay];
            const action = relayStates[relay] ? 'on' : 'off';
            
            // Start loading state
            this.classList.add('loading');
            indicator.style.transform = 'scale(0.5)';
            indicator.style.opacity = '0.5';

            // Send AJAX request to control relay
            fetch('/control_relay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'relay': relay,
                    'action': action,
                    'com_port': document.getElementById('com-port').value
                })
            })
            .then(response => response.json())
            .then(data => {
                // End loading state
                this.classList.remove('loading');
                
                if (data.status === 'success') {
                    console.log(`Relay ${relay} ${action} successful`);
                    
                    // Update UI with animation
                    indicator.style.backgroundColor = action === 'on' ? '#30d158' : '#ff453a';
                    indicator.style.boxShadow = action === 'on' 
                        ? '0 0 8px rgba(48, 209, 88, 0.5)' 
                        : '';
                    
                    // Toggle class for styling
                    indicator.classList.toggle('on', action === 'on');
                    
                    // Reset and apply new animation
                    setTimeout(() => {
                        indicator.style.transform = 'scale(1.2)';
                        indicator.style.opacity = '1';
                        
                        setTimeout(() => {
                            indicator.style.transform = 'scale(1)';
                        }, 200);
                    }, 50);
                    
                    showNotification(`Relay ${relay} turned ${action}`, 'success');
                } else {
                    console.error(`Error: ${data.message}`);
                    relayStates[relay] = !relayStates[relay]; // Revert state on error
                    showNotification(`Error switching relay ${relay}`, 'error');
                    
                    // Reset indicator
                    indicator.style.transform = 'scale(1)';
                    indicator.style.opacity = '1';
                }
            })
            .catch(error => {
                // End loading state
                this.classList.remove('loading');
                
                console.error('Error:', error);
                relayStates[relay] = !relayStates[relay]; // Revert state on error
                showNotification('Network error', 'error');
                
                // Reset indicator
                indicator.style.transform = 'scale(1)';
                indicator.style.opacity = '1';
            });
        });
    });
    
    // Connection testers
    const testConnectionBtn = document.getElementById('test-connection');
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', function() {
            this.classList.add('loading');
            
            setTimeout(() => {
                this.classList.remove('loading');
                showNotification('Connection test successful', 'success');
                
                // Update connection stats with random values for demo
                updateConnectionStats();
            }, 1500);
        });
    }
    
    // Save settings button
    const saveSettingsBtn = document.getElementById('save-settings');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', function() {
            this.classList.add('loading');
            
            setTimeout(() => {
                this.classList.remove('loading');
                showNotification('Settings saved successfully', 'success');
            }, 1000);
        });
    }
    
    // Function to update connection stats with random values (for demo)
    function updateConnectionStats() {
        // Get stats elements
        const signalQuality = document.querySelector('.stat-value:nth-child(2)');
        const signalBar = document.querySelector('.progress-fill:nth-child(1)');
        const transferRate = document.querySelector('.stat-value:nth-child(5)');
        const transferBar = document.querySelector('.progress-fill:nth-child(2)');
        
        if (signalQuality && signalBar) {
            const quality = Math.floor(85 + Math.random() * 15);
            signalQuality.textContent = quality + '%';
            signalBar.style.width = quality + '%';
        }
        
        if (transferRate && transferBar) {
            const rate = (10 + Math.random() * 5).toFixed(1);
            transferRate.textContent = rate + ' KB/s';
            transferBar.style.width = (rate / 20 * 100) + '%';
        }
    }
    
    // Function to update machine status based on power state
    function updateMachineStatus(isOn) {
        const statusBadges = document.querySelectorAll('.status-badge');
        const statusDots = document.querySelectorAll('.status-dot');
        
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
        // Temperature update
        const espTemp = document.querySelector('.esp-stat-item:nth-child(2) .esp-stat-value');
        const espTempBar = document.querySelector('.esp-stat-item:nth-child(2) .mini-progress-fill');
        if (espTemp && espTempBar) {
            const temp = 40 + Math.floor(Math.random() * 5);
            espTemp.textContent = `${temp}°C`;
            espTempBar.style.width = `${temp}%`;
        }
        
        // CPU load update
        const espCPU = document.querySelector('.esp-stat-item:nth-child(1) .esp-stat-value');
        const espCPUBar = document.querySelector('.esp-stat-item:nth-child(1) .mini-progress-fill');
        if (espCPU && espCPUBar) {
            const cpu = 75 + Math.floor(Math.random() * 15);
            espCPU.textContent = `${cpu}%`;
            espCPUBar.style.width = `${cpu}%`;
        }
        
        // Free memory update
        const espMem = document.querySelector('.esp-stat-item:nth-child(3) .esp-stat-value');
        const espMemBar = document.querySelector('.esp-stat-item:nth-child(3) .mini-progress-fill');
        if (espMem && espMemBar) {
            const mem = 110 + Math.floor(Math.random() * 30);
            espMem.textContent = `${mem.toFixed(1)} KB`;
            espMemBar.style.width = `${(mem / 200 * 100)}%`;
        }
    }
    
    // Update ESP32 stats periodically
    setInterval(updateESP32Stats, 8000);
    
    // Set transition styles for settings panels
    relayControls.style.transition = `opacity ${TRANSITION_DURATION}ms ease, transform ${TRANSITION_DURATION}ms ease`;
    settingsSection.style.transition = `opacity ${TRANSITION_DURATION}ms ease, transform ${TRANSITION_DURATION}ms ease`;
    modeIndicator.style.transition = `transform ${TRANSITION_DURATION}ms ease, opacity ${TRANSITION_DURATION}ms ease, color ${TRANSITION_DURATION}ms ease`;
    machineIndicator.style.transition = `transform ${TRANSITION_DURATION}ms ease, opacity ${TRANSITION_DURATION}ms ease, background-color ${TRANSITION_DURATION}ms ease, box-shadow ${TRANSITION_DURATION}ms ease`;
    
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
});