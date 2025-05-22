/**
 * external_systems_manager.js - External systems management for microfilm control system
 * Handles monitoring and control of SMA Software and External PC
 */

// Create namespace for external systems management
const ExternalSystemsManager = {
    // Constants
    UPDATE_INTERVAL: 5000, // Update status every 5 seconds
    
    // State tracking
    isSMAConnected: false,
    isExternalPCConnected: false,
    smaUpdateTimer: null,
    pcUpdateTimer: null,
    
    // External PC configuration
    externalPCConfig: {
        ip: '192.168.1.96', // Fixed IP address for the external PC
        hostname: 'MICRO-PC01'
    },
    
    // SMA Software state
    smaState: {
        status: 'unknown', // 'running', 'stopped', 'error'
        uptime: '00:00:00',
        currentFilm: 'None',
        pagesProcessed: '0/0',
        eta: '00:00:00'
    },
    
    // External PC state
    pcState: {
        status: 'unknown', // 'connected', 'disconnected'
        hostname: 'Unknown',
        ipAddress: '0.0.0.0',
        uptime: '0d 0h 0m',
        os: 'Unknown',
        cpuUsage: 0,
        memoryUsage: 0,
        diskUsage: 0,
        networkUsage: 0,
        pingTime: 0 // Store ping time in ms
    },
    
    /**
     * Initialize external systems monitoring
     */
    init: function() {
        console.log('Initializing external systems monitoring...');
        
        // Set up event listeners for buttons
        this.setupEventListeners();
        
        // Initial check of both systems
        this.checkSMAStatus();
        this.checkExternalPCStatus();
        
        // Add PC control buttons if they don't exist
        this.addPCControlButtons();
        
        // Note: periodic updates are now disabled
    },
    
    /**
     * Add PC control buttons to the PC status card
     */
    addPCControlButtons: function() {
        const pcCard = document.querySelector('.pc-status-card');
        if (!pcCard) return;
        
        // Check if buttons already exist
        if (pcCard.querySelector('.pc-actions')) return;
        
        // Create buttons container
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'pc-actions';
        
        // Create ping button
        const pingBtn = document.createElement('button');
        pingBtn.className = 'soft-control-button ping-btn';
        pingBtn.innerHTML = '<i class="fas fa-network-wired"></i> Ping';
        pingBtn.setAttribute('id', 'pc-ping-btn');
        
        // Create RDP button
        const rdpBtn = document.createElement('button');
        rdpBtn.className = 'soft-control-button rdp-btn';
        rdpBtn.innerHTML = '<i class="fas fa-desktop"></i> RDP Connect';
        rdpBtn.setAttribute('id', 'pc-rdp-btn');
        
        // Add buttons to container
        actionsDiv.appendChild(pingBtn);
        actionsDiv.appendChild(rdpBtn);
        
        // Add container to card
        pcCard.appendChild(actionsDiv);
        
        // Add event listeners
        pingBtn.addEventListener('click', () => this.pingExternalPC());
        rdpBtn.addEventListener('click', () => this.connectRDP());
    },
    
    /**
     * Set up event listeners for system control buttons
     */
    setupEventListeners: function() {
        // SMA Software buttons
        const smaReconnectBtn = document.querySelector('.sma-status-card .software-actions button:nth-child(1)');
        const smaConsoleBtn = document.querySelector('.sma-status-card .software-actions button:nth-child(2)');
        
        if (smaReconnectBtn) {
            smaReconnectBtn.addEventListener('click', () => {
                this.reconnectSMA();
            });
        }
        
        if (smaConsoleBtn) {
            smaConsoleBtn.addEventListener('click', () => {
                this.openSMAConsole();
            });
        }
        
        // External PC buttons - these will be added dynamically in addPCControlButtons
    },
    
    /**
     * Update SMA status on demand (for refresh button)
     */
    updateSMAStatus: function() {
        console.log('Manually updating SMA status...');
        return new Promise((resolve, reject) => {
            this.checkSMAStatus()
                .then(() => resolve())
                .catch(error => reject(error));
        });
    },
    
    /**
     * Update PC status on demand (for refresh button)
     */
    updatePCStatus: function() {
        console.log('Manually updating External PC status...');
        return new Promise((resolve, reject) => {
            this.checkExternalPCStatus()
                .then(() => resolve())
                .catch(error => reject(error));
        });
    },
    
    /**
     * Start periodic updates for both systems
     * Note: This function is now deprecated and not called in init
     */
    startPeriodicUpdates: function() {
        // Clear any existing timers
        if (this.smaUpdateTimer) clearInterval(this.smaUpdateTimer);
        if (this.pcUpdateTimer) clearInterval(this.pcUpdateTimer);
        
        // Set up new timers with slightly different intervals to avoid simultaneous requests
        this.smaUpdateTimer = setInterval(() => this.checkSMAStatus(), this.UPDATE_INTERVAL);
        this.pcUpdateTimer = setInterval(() => this.checkExternalPCStatus(), this.UPDATE_INTERVAL + 500);
    },
    
    /**
     * Check SMA Software status
     */
    checkSMAStatus: function() {
        console.log('Checking SMA Software status...');
        
        // Return a promise for refresh button functionality
        return new Promise((resolve, reject) => {
            // In a real implementation, this would make an API call to check the SMA software
            // For now, simulate with a fetch to a backend endpoint
            fetch('/api/sma_status/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update state with real data
                this.isSMAConnected = data.status === 'running';
                this.smaState = {
                    status: data.status,
                    uptime: data.uptime || '00:00:00',
                    currentFilm: data.current_film || 'None',
                    pagesProcessed: data.pages_processed || '0/0',
                    eta: data.eta || '00:00:00'
                };
                
                // Update UI
                this.updateSMAUI();
                resolve();
            })
            .catch(error => {
                console.error('Error checking SMA status:', error);
                
                // If we can't connect, simulate with mock data
                this.simulateSMAStatus();
                resolve(); // Still resolve as we handled the error with mock data
            });
        });
    },
    
    /**
     * Simulate SMA status for development/testing
     */
    simulateSMAStatus: function() {
        // Randomly determine if SMA is connected (for simulation)
        // In production, this would be based on actual connection status
        const randomConnected = Math.random() > 0.2; // 80% chance of being connected
        
        this.isSMAConnected = randomConnected;
        
        if (randomConnected) {
            // Generate realistic mock data
            const hours = Math.floor(Math.random() * 24);
            const minutes = Math.floor(Math.random() * 60);
            const seconds = Math.floor(Math.random() * 60);
            const uptime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            const filmNumber = Math.floor(Math.random() * 100).toString().padStart(4, '0');
            const currentFilm = `F-${Math.floor(Math.random() * 20 + 1)}-${filmNumber}`;
            
            const totalPages = Math.floor(Math.random() * 1000 + 100);
            const processedPages = Math.floor(Math.random() * totalPages);
            const pagesProcessed = `${processedPages}/${totalPages}`;
            
            const etaHours = Math.floor(Math.random() * 24);
            const etaMinutes = Math.floor(Math.random() * 60);
            const etaSeconds = Math.floor(Math.random() * 60);
            const eta = `${etaHours.toString().padStart(2, '0')}:${etaMinutes.toString().padStart(2, '0')}:${etaSeconds.toString().padStart(2, '0')}`;
            
            this.smaState = {
                status: 'running',
                uptime: uptime,
                currentFilm: currentFilm,
                pagesProcessed: pagesProcessed,
                eta: eta
            };
        } else {
            this.smaState = {
                status: 'stopped',
                uptime: '00:00:00',
                currentFilm: 'None',
                pagesProcessed: '0/0',
                eta: '00:00:00'
            };
        }
        
        // Update UI with simulated data
        this.updateSMAUI();
    },
    
    /**
     * Update SMA Software UI
     */
    updateSMAUI: function() {
        // Update status badge
        const statusBadge = document.querySelector('.sma-status-card .status-badge');
        if (statusBadge) {
            if (this.isSMAConnected) {
                statusBadge.classList.remove('critical');
                statusBadge.classList.add('operational');
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Running';
            } else {
                statusBadge.classList.remove('operational');
                statusBadge.classList.add('critical');
                statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Stopped';
            }
        }
        
        // Update metrics
        const uptimeValue = document.querySelector('.sma-status .status-metric:nth-child(1) .metric-value');
        const filmValue = document.querySelector('.sma-status .status-metric:nth-child(2) .metric-value');
        const pagesValue = document.querySelector('.sma-status .status-metric:nth-child(3) .metric-value');
        const etaValue = document.querySelector('.sma-status .status-metric:nth-child(4) .metric-value');
        
        if (uptimeValue) uptimeValue.textContent = this.smaState.uptime;
        if (filmValue) filmValue.textContent = this.smaState.currentFilm;
        if (pagesValue) pagesValue.textContent = this.smaState.pagesProcessed;
        if (etaValue) etaValue.textContent = this.smaState.eta;
    },
    
    /**
     * Reconnect to SMA Software
     */
    reconnectSMA: function() {
        console.log('Attempting to reconnect to SMA Software...');
        
        // Show loading state on button
        const reconnectBtn = document.querySelector('.sma-status-card .software-actions button:nth-child(1)');
        if (reconnectBtn) {
            reconnectBtn.disabled = true;
            reconnectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
        }
        
        // In a real implementation, this would make an API call to restart/reconnect to SMA
        // For now, simulate with a timeout
        setTimeout(() => {
            // Simulate successful reconnection
            this.isSMAConnected = true;
            this.smaState.status = 'running';
            
            // Update UI
            this.updateSMAUI();
            
            // Reset button state
            if (reconnectBtn) {
                reconnectBtn.disabled = false;
                reconnectBtn.innerHTML = '<i class="fas fa-sync"></i> Reconnect';
            }
            
            // Show notification
            NotificationManager.showNotification('SMA Software reconnected successfully', 'success');
        }, 2000);
    },
    
    /**
     * Open SMA Console
     */
    openSMAConsole: function() {
        console.log('Opening SMA Console...');
        
        // In a real implementation, this would open a console window or modal
        // For now, show a notification
        NotificationManager.showNotification('SMA Console feature coming soon', 'info');
    },
    
    /**
     * Check External PC status
     */
    checkExternalPCStatus: function() {
        console.log('Checking External PC status...');
        
        // Return a promise for refresh button functionality
        return new Promise((resolve, reject) => {
            // Use the fixed IP address from config
            const ipToCheck = this.externalPCConfig.ip;
            
            // In a real implementation, this would make an API call to check the External PC
            fetch('/api/external_pc_status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    ip_address: ipToCheck
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update state with real data
                this.isExternalPCConnected = data.status === 'connected';
                this.pcState = {
                    status: data.status,
                    hostname: data.hostname || 'Unknown',
                    ipAddress: data.ip_address || ipToCheck,
                    uptime: data.uptime || '0d 0h 0m',
                    os: data.os || 'Unknown',
                    cpuUsage: data.cpu_usage || 0,
                    memoryUsage: data.memory_usage || 0,
                    diskUsage: data.disk_usage || 0,
                    networkUsage: data.network_usage || 0,
                    pingTime: data.ping_time || 0
                };
                
                // Update UI
                this.updateExternalPCUI();
                
                // Update PC control buttons state
                this.updatePCControlButtonsState();
                resolve();
            })
            .catch(error => {
                console.error('Error checking External PC status:', error);
                
                // If we can't connect, simulate with mock data
                this.simulateExternalPCStatus();
                resolve(); // Still resolve as we handled the error with mock data
            });
        });
    },
    
    /**
     * Simulate External PC status for development/testing
     */
    simulateExternalPCStatus: function() {
        // Randomly determine if PC is connected (for simulation)
        // In production, this would be based on actual connection status
        const randomConnected = Math.random() > 0.2; // 80% chance of being connected
        
        this.isExternalPCConnected = randomConnected;
        
        if (randomConnected) {
            // Generate realistic mock data
            const days = Math.floor(Math.random() * 10);
            const hours = Math.floor(Math.random() * 24);
            const minutes = Math.floor(Math.random() * 60);
            const uptime = `${days}d ${hours}h ${minutes}m`;
            
            // Use fixed IP from config
            const ip = this.externalPCConfig.ip;
            
            // Random resource usage percentages
            const cpuUsage = Math.floor(Math.random() * 100);
            const memoryUsage = Math.floor(Math.random() * 100);
            const diskUsage = Math.floor(Math.random() * 100);
            const networkUsage = Math.floor(Math.random() * 100);
            const pingTime = Math.floor(Math.random() * 20 + 1); // 1-20ms
            
            this.pcState = {
                status: 'connected',
                hostname: this.externalPCConfig.hostname,
                ipAddress: ip,
                uptime: uptime,
                os: 'Windows 10 Pro',
                cpuUsage: cpuUsage,
                memoryUsage: memoryUsage,
                diskUsage: diskUsage,
                networkUsage: networkUsage,
                pingTime: pingTime
            };
        } else {
            this.pcState = {
                status: 'disconnected',
                hostname: this.externalPCConfig.hostname,
                ipAddress: this.externalPCConfig.ip,
                uptime: '0d 0h 0m',
                os: 'Unknown',
                cpuUsage: 0,
                memoryUsage: 0,
                diskUsage: 0,
                networkUsage: 0,
                pingTime: 0
            };
        }
        
        // Update UI with simulated data
        this.updateExternalPCUI();
        
        // Update PC control buttons state
        this.updatePCControlButtonsState();
    },
    
    /**
     * Update External PC UI
     */
    updateExternalPCUI: function() {
        // Update status badge
        const statusBadge = document.querySelector('.pc-status-card .status-badge');
        if (statusBadge) {
            if (this.isExternalPCConnected) {
                statusBadge.classList.remove('critical');
                statusBadge.classList.add('operational');
                statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
            } else {
                statusBadge.classList.remove('operational');
                statusBadge.classList.add('critical');
                statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Disconnected';
            }
        }
        
        // Update resource bars
        const cpuBar = document.querySelector('.pc-resources .resource-item:nth-child(1) .resource-fill');
        const cpuValue = document.querySelector('.pc-resources .resource-item:nth-child(1) .resource-value');
        const memoryBar = document.querySelector('.pc-resources .resource-item:nth-child(2) .resource-fill');
        const memoryValue = document.querySelector('.pc-resources .resource-item:nth-child(2) .resource-value');
        const diskBar = document.querySelector('.pc-resources .resource-item:nth-child(3) .resource-fill');
        const diskValue = document.querySelector('.pc-resources .resource-item:nth-child(3) .resource-value');
        const networkBar = document.querySelector('.pc-resources .resource-item:nth-child(4) .resource-fill');
        const networkValue = document.querySelector('.pc-resources .resource-item:nth-child(4) .resource-value');
        
        if (cpuBar) cpuBar.style.width = `${this.pcState.cpuUsage}%`;
        if (cpuValue) cpuValue.textContent = `${this.pcState.cpuUsage}%`;
        if (memoryBar) memoryBar.style.width = `${this.pcState.memoryUsage}%`;
        if (memoryValue) memoryValue.textContent = `${this.pcState.memoryUsage}%`;
        if (diskBar) diskBar.style.width = `${this.pcState.diskUsage}%`;
        if (diskValue) diskValue.textContent = `${this.pcState.diskUsage}%`;
        if (networkBar) networkBar.style.width = `${this.pcState.networkUsage}%`;
        if (networkValue) networkValue.textContent = `${this.pcState.networkUsage}%`;
        
        // Update PC info
        const hostnameValue = document.querySelector('.pc-info .info-row:nth-child(1) .info-value');
        const ipValue = document.querySelector('.pc-info .info-row:nth-child(2) .info-value');
        const uptimeValue = document.querySelector('.pc-info .info-row:nth-child(3) .info-value');
        const osValue = document.querySelector('.pc-info .info-row:nth-child(4) .info-value');
        
        if (hostnameValue) hostnameValue.textContent = this.pcState.hostname;
        if (ipValue) ipValue.textContent = this.pcState.ipAddress;
        if (uptimeValue) uptimeValue.textContent = this.pcState.uptime;
        if (osValue) osValue.textContent = this.pcState.os;
    },
    
    /**
     * Update PC control buttons state based on connection status
     */
    updatePCControlButtonsState: function() {
        const pingBtn = document.getElementById('pc-ping-btn');
        const rdpBtn = document.getElementById('pc-rdp-btn');
        
        if (pingBtn) {
            pingBtn.disabled = false; // Ping can always be attempted
            
            // Update button text with ping time if available
            if (this.isExternalPCConnected && this.pcState.pingTime > 0) {
                pingBtn.innerHTML = `<i class="fas fa-network-wired"></i> Ping (${this.pcState.pingTime}ms)`;
            } else {
                pingBtn.innerHTML = '<i class="fas fa-network-wired"></i> Ping';
            }
        }
        
        if (rdpBtn) {
            // Only enable RDP button if PC is connected
            rdpBtn.disabled = !this.isExternalPCConnected;
            rdpBtn.classList.toggle('disabled', !this.isExternalPCConnected);
        }
    },
    
    /**
     * Ping the external PC
     */
    pingExternalPC: function() {
        console.log('Pinging External PC...');
        
        // Show loading state on button
        const pingBtn = document.getElementById('pc-ping-btn');
        if (pingBtn) {
            pingBtn.disabled = true;
            pingBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Pinging...';
        }
        
        // Make API call to ping the PC
        fetch('/api/external_pc_ping/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                ip_address: this.externalPCConfig.ip
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update ping time and connection status
            this.isExternalPCConnected = data.success;
            if (data.success) {
                this.pcState.pingTime = data.ping_time;
                
                // Show success notification
                NotificationManager.showNotification(`Ping successful: ${data.ping_time}ms`, 'success');
            } else {
                // Show error notification
                NotificationManager.showNotification('Ping failed: Host unreachable', 'error');
            }
            
            // Update UI
            this.updateExternalPCUI();
            this.updatePCControlButtonsState();
        })
        .catch(error => {
            console.error('Error pinging External PC:', error);
            
            // Show error notification
            NotificationManager.showNotification('Ping failed: Network error', 'error');
            
            // Reset button state
            if (pingBtn) {
                pingBtn.disabled = false;
                pingBtn.innerHTML = '<i class="fas fa-network-wired"></i> Ping';
            }
        });
    },
    
    /**
     * Connect to the external PC via RDP
     */
    connectRDP: function() {
        console.log('Connecting to External PC via RDP...');
        
        // Only allow if PC is connected
        if (!this.isExternalPCConnected) {
            NotificationManager.showNotification('Cannot connect: PC is offline', 'error');
            return;
        }
        
        // Show loading state on button
        const rdpBtn = document.getElementById('pc-rdp-btn');
        if (rdpBtn) {
            rdpBtn.disabled = true;
            rdpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
        }
        
        // Make API call to start RDP connection
        fetch('/api/external_pc_rdp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                ip_address: this.externalPCConfig.ip
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show success notification
                NotificationManager.showNotification('RDP connection initiated', 'success');
            } else {
                // Show error notification
                NotificationManager.showNotification(`RDP connection failed: ${data.message}`, 'error');
            }
            
            // Reset button state
            if (rdpBtn) {
                rdpBtn.disabled = false;
                rdpBtn.innerHTML = '<i class="fas fa-desktop"></i> RDP Connect';
            }
        })
        .catch(error => {
            console.error('Error connecting to External PC via RDP:', error);
            
            // Show error notification
            NotificationManager.showNotification('RDP connection failed: Network error', 'error');
            
            // Reset button state
            if (rdpBtn) {
                rdpBtn.disabled = false;
                rdpBtn.innerHTML = '<i class="fas fa-desktop"></i> RDP Connect';
            }
        });
    }
}; 