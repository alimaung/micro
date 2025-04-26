/**
 * utils.js - Utility functions for microfilm control system
 * Contains helper functions and utilities used across other modules
 */

// Create namespace for utility functions
const Utils = {
    // WebSocket properties
    ws: null,
    wsAvailable: false,
    wsUrl: 'ws://127.0.0.1:8000/ws/relay/',
    
    // Helper to compare two device info objects for equality
    isEqualDeviceInfo: function(obj1, obj2) {
        // Compare the most important fields for equality
        const fieldsToCompare = ['port', 'vendor_id', 'product_id', 'product', 'serial_number'];
        
        for (const field of fieldsToCompare) {
            if (obj1[field] !== obj2[field] && obj1[field] !== undefined && obj2[field] !== undefined) {
                return false;
            }
        }
        
        return true;
    },

    /**
     * Initialize WebSocket connection
     */
    setupWebSocket: function() {
        this.ws = new WebSocket(this.wsUrl);
        this.ws.onopen = () => {
            this.wsAvailable = true;
            console.log("WebSocket connected");
            // Optionally: update UI to show real-time mode
        };
        this.ws.onclose = () => {
            this.wsAvailable = false;
            console.log("WebSocket closed, falling back to HTTP");
            // Optionally: update UI to show fallback mode
        };
        this.ws.onerror = () => {
            this.wsAvailable = false;
            console.log("WebSocket error, falling back to HTTP");
        };
        this.ws.onmessage = (event) => {
            this.handleWsMessage(event.data);
        };
    },

    /**
     * Handle incoming WebSocket messages
     * @param {string} data - The message data
     */
    handleWsMessage: function(data) {
        // Parse and route the message to the appropriate UI update function
        const msg = JSON.parse(data);
        
        // Update UI based on message type
        if (msg.type === 'relays') {
            RelayControls.updateRelayStatesUI(msg.states);
        } else if (msg.type === 'system') {
            this.updateESP32StatsUI(msg);
        } else if (msg.type === 'relay') {
            // Single relay state update
            if (msg.relay && msg.state !== undefined) {
                RelayControls.setRelayIndicatorState(msg.relay, msg.state, false);
            }
        } else if (msg.type === 'pong') {
            this.updateLatencyDisplay(msg.latency || 30);
        } else if (msg.type === 'error') {
            NotificationManager.showNotification(msg.message, 'error');
        }
    },

    /**
     * Send action via WebSocket with HTTP fallback
     * @param {Object} actionObj - WebSocket action object
     * @param {string} httpFallbackUrl - Fallback HTTP endpoint
     * @param {Object} httpFallbackBody - Fallback HTTP request body
     * @returns {Promise} - Promise that resolves with the response
     */
    sendRelayAction: function(actionObj, httpFallbackUrl, httpFallbackBody) {
        return new Promise((resolve, reject) => {
            if (this.wsAvailable && this.ws && this.ws.readyState === WebSocket.OPEN) {
                // Set up a one-time message handler to capture the response
                const messageHandler = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        // Check if this is a response to our request by action-type pattern
                        const isResponse = this._isMatchingResponseType(actionObj.action, data.type);

                        // --- Accept also responses with status: "success" and no type field ---
                        if (isResponse || (data.status === "success" && data.type === undefined)) {
                            resolve(data);
                            this.ws.removeEventListener('message', messageHandler);
                            clearTimeout(timeoutId);
                        }
                    } catch (error) {
                        console.error("Error parsing WebSocket response:", error);
                    }
                };
                
                this.ws.addEventListener('message', messageHandler);
                
                // Set timeout to clean up if no response
                const timeoutId = setTimeout(() => {
                    this.ws.removeEventListener('message', messageHandler);
                    reject(new Error("WebSocket request timed out"));
                }, 10000);
                
                // Send the request
                this.ws.send(JSON.stringify(actionObj));
            } else {
                console.log("Fallback to HTTP");
                // Fallback to HTTP
                return fetch(httpFallbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new URLSearchParams(httpFallbackBody)
                })
                .then(response => response.json())
                .then(data => resolve(data))
                .catch(error => reject(error));
            }
        });
    },

    /**
     * Helper function to determine if response type matches action type
     */
    _isMatchingResponseType: function(actionType, responseType) {
        return (
            // Direct match (e.g., system -> system)
            (responseType === actionType) ||
            // Ping -> Pong pattern
            (actionType === 'ping' && responseType === 'pong') ||
            // Other specific patterns
            (actionType === 'set' && responseType === 'relay') ||
            (actionType === 'status' && responseType === 'relays') ||
            (actionType === 'dark' && responseType === 'status') ||
            (actionType === 'light' && responseType === 'status')
        );
    },

    /**
     * Measure ESP32 response latency
     * @returns {Promise} Promise that resolves with the latency in ms
     */
    measureESP32Latency: function() {
        const start = performance.now();
        return new Promise((resolve, reject) => {
            this.sendRelayAction(
                { action: 'ping' },
                '/control_relay/',
                {
                    'action': 'ping',
                    'com_port': ConnectionManager.getActiveRelayPort()
                },
                (data) => {
                    const endTime = performance.now();
                    const latency = endTime - start;
                    
                    if (data.type === 'pong') {
                        resolve(latency);  // Resolve the outer promise with latency
                    } else {
                        reject(new Error(data.message || 'Failed to ping ESP32'));
                    }
                },
                (error) => {
                    reject(error);  // Reject the outer promise
                }
            ).catch(error => {
                reject(error);  // Handle any promise rejection from sendRelayAction
            });
        });
    },

    /**
     * Update latency display in the UI
     * @param {number} latency - The latency in milliseconds
     */
    updateLatencyDisplay: function(latency) {
        const pingValue = document.querySelector('.ping-value');
        if (!pingValue) return;
        
        // Round to 1 decimal place
        const roundedLatency = Math.round(latency * 10) / 10;
        
        // Update the display
        pingValue.textContent = `${roundedLatency} ms`;
        
        // Update color based on latency value
        if (roundedLatency < 100) {
            pingValue.className = 'ping-value good';
        } else if (roundedLatency < 300) {
            pingValue.className = 'ping-value medium';
        } else {
            pingValue.className = 'ping-value poor';
        }
    },

    /**
     * Update ESP32 stats 
     */
    updateESP32Stats: function() {
        // Only attempt if relay is connected
        if (!ConnectionManager.isRelayConnected) {
            console.log('Cannot update ESP32 stats: Relay not connected');
            return;
        }
        
        // Send the system action request
        this.sendRelayAction(
            { action: 'system' },
            '/get_all_states/',
            {}
        )
        .then(data => {
            if (data.status === 'success' && data.data) {
                // We don't need to call updateESP32StatsUI here
                // handleWsMessage will already do this when the response comes in
                
                // Log that we successfully requested system stats
                console.log("ESP32 stats request sent successfully");
            }
        })
        .catch(error => {
            console.error('Error updating ESP32 stats:', error);
            this.showPlaceholderStats();
        });
        
        // Additionally measure ESP32 latency
        this.measureESP32Latency()
            .then(latency => {
                // We don't need to call updateLatencyDisplay here
                // handleWsMessage will update it when the pong response comes in
                console.log("Latency measurement sent");
            })
            .catch(error => {
                console.error('Error measuring ESP32 latency:', error);
            });
    },
    
    /**
     * Show placeholder ESP32 stats when connection fails
     */
    showPlaceholderStats: function() {
        const placeholders = {
            "cpu": "N/A",
            "temp": "N/A",
            "ram": "N/A",
            "uptime": "N/A",
            "voltage": "N/A"
        };
        this.updateESP32StatsUI(placeholders);
    },

    /**
     * Update ESP32 stats in the UI
     * @param {Object} stats - ESP32 statistics object
     */
    updateESP32StatsUI: function(stats) {
        if (!stats || typeof stats !== 'object') {
            console.error('Invalid ESP32 stats data:', stats);
            return;
        }
        
        console.log("Updating UI with stats:", stats);

        // Get all esp-stat-value elements from the UI
        const statValues = document.querySelectorAll('.esp-stat-value');
        
        // Find elements by their position or parent text
        let cpuElement, tempElement, memoryElement, uptimeElement, voltageElement;
        
        statValues.forEach(element => {
            const label = element.nextElementSibling;
            if (label && label.classList.contains('esp-stat-label')) {
                const labelText = label.textContent.toLowerCase();
                if (labelText.includes('cpu')) {
                    cpuElement = element;
                } else if (labelText.includes('temp')) {
                    tempElement = element;
                } else if (labelText.includes('memory')) {
                    memoryElement = element;
                } else if (labelText.includes('uptime')) {
                    uptimeElement = element;
                } else if (labelText.includes('voltage')) {
                    voltageElement = element;
                }
            }
        });
        
        // Update temperature
        if (tempElement) {
            const temperature = stats.temperature !== undefined ? stats.temperature : stats.temp_c;
            if (temperature !== undefined) {
                tempElement.textContent = `${Math.round(temperature * 10) / 10}°C`;
                
                // Set color based on temperature range
                if (temperature < 50) {
                    tempElement.classList.add('good');
                    tempElement.classList.remove('medium', 'poor');
                } else if (temperature < 70) {
                    tempElement.classList.add('medium');
                    tempElement.classList.remove('good', 'poor');
                } else {
                    tempElement.classList.add('poor');
                    tempElement.classList.remove('good', 'medium');
                }
                
                // Update progress bar if present
                const progressBar = tempElement.parentElement.querySelector('.mini-progress-fill');
                if (progressBar) {
                    // Assume reasonable range: 20-80°C
                    const percentage = Math.min(100, Math.max(0, (temperature - 20) / 60 * 100));
                    progressBar.style.width = `${percentage}%`;
                }
            }
        }
        
        // Update memory
        if (memoryElement) {
            const memory = stats.free_memory !== undefined ? stats.free_memory : stats.ram_kb;
            if (memory !== undefined) {
                const memoryKB = Math.round(memory);
                memoryElement.textContent = `${memoryKB} KB`;
                
                // Set color based on memory range
                if (memoryKB > 150) {
                    memoryElement.classList.add('good');
                    memoryElement.classList.remove('medium', 'poor');
                } else if (memoryKB > 50) {
                    memoryElement.classList.add('medium');
                    memoryElement.classList.remove('good', 'poor');
                } else {
                    memoryElement.classList.add('poor');
                    memoryElement.classList.remove('good', 'medium');
                }
                
                // Update progress bar if present
                const progressBar = memoryElement.parentElement.querySelector('.mini-progress-fill');
                if (progressBar) {
                    // Assume max memory is around 300KB
                    const percentage = Math.min(100, Math.max(0, (memory / 300) * 100));
                    progressBar.style.width = `${percentage}%`;
                }
            }
        }
        
        // Update CPU
        if (cpuElement) {
            // For CPU, we use cpu_mhz as a percentage of max (which is 240)
            const cpuUsage = stats.cpu_usage !== undefined ? stats.cpu_usage : 
                             (stats.cpu_mhz ? 100 : undefined); // Assuming cpu_mhz = 240 is 100% usage
            
            if (cpuUsage !== undefined) {
                cpuElement.textContent = `${Math.round(cpuUsage)}%`;
                
                // Set color based on CPU usage
                if (cpuUsage < 50) {
                    cpuElement.classList.add('good');
                    cpuElement.classList.remove('medium', 'poor');
                } else if (cpuUsage < 80) {
                    cpuElement.classList.add('medium');
                    cpuElement.classList.remove('good', 'poor');
                } else {
                    cpuElement.classList.add('poor');
                    cpuElement.classList.remove('good', 'medium');
                }
                
                // Update progress bar if present
                const progressBar = cpuElement.parentElement.querySelector('.mini-progress-fill');
                if (progressBar) {
                    progressBar.style.width = `${cpuUsage}%`;
                }
            }
        }
        
        // Update uptime
        if (uptimeElement) {
            const uptime = stats.uptime !== undefined ? stats.uptime : stats.uptime_s;
            if (uptime !== undefined) {
                // Format uptime in hours and minutes
                const hours = Math.floor(uptime / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                uptimeElement.textContent = `${hours}h ${minutes}m`;
            }
        }
        
        // Update voltage
        if (voltageElement && stats.voltage_v !== undefined) {
            voltageElement.textContent = `${stats.voltage_v.toFixed(2)}V`;
            
            // Update progress bar if present
            const progressBar = voltageElement.parentElement.querySelector('.mini-progress-fill');
            if (progressBar) {
                // Assume voltage range 0-12V
                const percentage = Math.min(100, Math.max(0, (stats.voltage_v / 12) * 100));
                progressBar.style.width = `${percentage}%`;
            }
        }
        
        console.log("ESP32 stats UI updated successfully");
    }
}; 