/**
 * utils.js - Utility functions for microfilm control system
 * Contains helper functions and utilities used across other modules
 */

// Create namespace for utility functions
const Utils = {
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
     * Measure ESP32 response latency
     * @returns {Promise} Promise that resolves with the latency in ms
     */
    measureESP32Latency: function() {
        return new Promise((resolve, reject) => {
            const startTime = performance.now();
            
            fetch('/control_relay/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'action': 'ping',
                    'com_port': ConnectionManager.getActiveRelayPort()
                })
            })
            .then(response => response.json())
            .then(data => {
                const endTime = performance.now();
                const latency = endTime - startTime;
                
                if (data.status === 'success') {
                    resolve(latency);
                } else {
                    reject(new Error(data.message || 'Failed to ping ESP32'));
                }
            })
            .catch(error => {
                reject(error);
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
     * Update ESP32 stats (latency, etc)
     */
    updateESP32Stats: function() {
        // Only attempt if relay is connected
        if (!ConnectionManager.isRelayConnected) {
            console.log('Cannot update ESP32 stats: Relay not connected');
            return;
        }
        
        // Get ESP32 stats from get_all_states endpoint
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
                // Update ESP32 system stats
                Utils.updateESP32StatsUI(data.data.system_stats);
                
                // Update relay states if needed
                if (data.data.relay_states) {
                    RelayControls.updateRelayStatesUI(data.data.relay_states);
                }
                
                // Update mode display if available
                if (data.data.current_mode) {
                    UIManager.updateModeDisplay(data.data.current_mode);
                }
                
                console.log("ESP32 stats and relay states updated from real data");
            } else {
                console.error(`Error fetching ESP32 stats: ${data.message || 'Unknown error'}`);
                this.showPlaceholderStats();
            }
        })
        .catch(error => {
            console.error('Error updating ESP32 stats:', error);
            this.showPlaceholderStats();
        });
        
        // Additionally measure ESP32 latency
        this.measureESP32Latency()
            .then(latency => {
                this.updateLatencyDisplay(latency);
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
        
        // Update ESP32 temperature display
        const tempElement = document.getElementById('esp32-temp');
        if (tempElement && stats.temperature !== undefined) {
            tempElement.textContent = `${stats.temperature}°C`;
            
            // Set color based on temperature range
            if (stats.temperature < 50) {
                tempElement.className = 'esp32-stat-value good';
            } else if (stats.temperature < 70) {
                tempElement.className = 'esp32-stat-value medium';
            } else {
                tempElement.className = 'esp32-stat-value poor';
            }
        }
        
        // Update ESP32 free memory display
        const memoryElement = document.getElementById('esp32-memory');
        if (memoryElement && stats.free_memory !== undefined) {
            // Format memory in KB
            const memoryKB = Math.round(stats.free_memory / 1024);
            memoryElement.textContent = `${memoryKB}KB`;
            
            // Set color based on memory range
            if (memoryKB > 50) {
                memoryElement.className = 'esp32-stat-value good';
            } else if (memoryKB > 20) {
                memoryElement.className = 'esp32-stat-value medium';
            } else {
                memoryElement.className = 'esp32-stat-value poor';
            }
        }
        
        // Update ESP32 CPU usage display
        const cpuElement = document.getElementById('esp32-cpu');
        if (cpuElement && stats.cpu_usage !== undefined) {
            cpuElement.textContent = `${stats.cpu_usage}%`;
            
            // Set color based on CPU usage range
            if (stats.cpu_usage < 50) {
                cpuElement.className = 'esp32-stat-value good';
            } else if (stats.cpu_usage < 80) {
                cpuElement.className = 'esp32-stat-value medium';
            } else {
                cpuElement.className = 'esp32-stat-value poor';
            }
        }
        
        // Update ESP32 uptime display
        const uptimeElement = document.getElementById('esp32-uptime');
        if (uptimeElement && stats.uptime !== undefined) {
            // Format uptime in hours and minutes
            const hours = Math.floor(stats.uptime / 3600);
            const minutes = Math.floor((stats.uptime % 3600) / 60);
            uptimeElement.textContent = `${hours}h ${minutes}m`;
            uptimeElement.className = 'esp32-stat-value';
        }
    }
}; 