/**
 * WebSocket Client for SMA Filming Real-time Updates
 * Handles WebSocket connections for live progress, logs, and status updates
 */

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.isConnected = false;
        this.subscriptions = new Set();
        
        // Callback handlers
        this.onSMAUpdate = null;
        this.onConnectionChange = null;
        
        this.init();
    }
    
    init() {
        this.connect();
        this.bindEvents();
    }
    
    connect() {
        try {
            // Determine WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/sma/`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = (event) => this.onOpen(event);
            this.socket.onmessage = (event) => this.onMessage(event);
            this.socket.onclose = (event) => this.onClose(event);
            this.socket.onerror = (event) => this.onError(event);
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.scheduleReconnect();
        }
    }
    
    onOpen(event) {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        
        // Notify connection change
        if (this.onConnectionChange) {
            this.onConnectionChange(true);
        }
        
        // Re-subscribe to any active subscriptions
        this.resubscribe();
        
        // Send heartbeat to keep connection alive
        this.startHeartbeat();
    }
    
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
            
            this.handleMessage(data);
            
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }
    
    onClose(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
        this.isConnected = false;
        
        // Notify connection change
        if (this.onConnectionChange) {
            this.onConnectionChange(false);
        }
        
        // Stop heartbeat
        this.stopHeartbeat();
        
        // Attempt to reconnect unless it was a clean close
        if (event.code !== 1000) {
            this.scheduleReconnect();
        }
    }
    
    onError(event) {
        console.error('WebSocket error:', event);
        
        // Close the connection to trigger reconnect
        if (this.socket) {
            this.socket.close();
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'sma_progress':
                this.handleSMAProgress(data);
                break;
                
            case 'sma_log':
                this.handleSMALog(data);
                break;
                
            case 'sma_workflow_state':
                this.handleSMAWorkflowState(data);
                break;
                
            case 'sma_session_status':
                this.handleSMASessionStatus(data);
                break;
                
            case 'sma_error':
                this.handleSMAError(data);
                break;
                
            case 'heartbeat_response':
                // Heartbeat acknowledged
                break;
                
            case 'subscription_confirmed':
                console.log('Subscription confirmed:', data.subscription);
                break;
                
            case 'subscription_error':
                console.error('Subscription error:', data.error);
                break;
                
            default:
                console.warn('Unknown message type:', data.type);
        }
    }
    
    handleSMAProgress(data) {
        if (this.onSMAUpdate) {
            this.onSMAUpdate({
                type: 'sma_progress',
                session_id: data.session_id,
                data: data.progress
            });
        }
    }
    
    handleSMALog(data) {
        if (this.onSMAUpdate) {
            this.onSMAUpdate({
                type: 'sma_log',
                session_id: data.session_id,
                data: data.log
            });
        }
    }
    
    handleSMAWorkflowState(data) {
        if (this.onSMAUpdate) {
            this.onSMAUpdate({
                type: 'sma_workflow_state',
                session_id: data.session_id,
                data: {
                    old_state: data.old_state,
                    new_state: data.new_state
                }
            });
        }
    }
    
    handleSMASessionStatus(data) {
        if (this.onSMAUpdate) {
            this.onSMAUpdate({
                type: 'sma_session_status',
                session_id: data.session_id,
                data: data.status
            });
        }
    }
    
    handleSMAError(data) {
        if (this.onSMAUpdate) {
            this.onSMAUpdate({
                type: 'sma_error',
                session_id: data.session_id,
                data: {
                    error: data.error,
                    details: data.details
                }
            });
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached. Giving up.');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
        
        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }
    
    resubscribe() {
        // Re-subscribe to all active subscriptions
        this.subscriptions.forEach(subscription => {
            if (subscription.startsWith('sma_session_')) {
                // Extract session ID and use join_session action
                const sessionId = subscription.replace('sma_session_', '');
                this.send({
                    action: 'join_session',
                    session_id: sessionId
                });
            } else {
                // Use old format for other subscriptions
            this.send({
                type: 'subscribe',
                subscription: subscription
            });
            }
        });
    }
    
    startHeartbeat() {
        // Send heartbeat every 30 seconds
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({
                    action: 'ping',
                    timestamp: Date.now()
                });
            }
        }, 30000);
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    bindEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden, reduce activity
                this.stopHeartbeat();
            } else {
                // Page is visible, resume activity
                if (this.isConnected) {
                    this.startHeartbeat();
                } else {
                    // Try to reconnect if disconnected
                    this.connect();
                }
            }
        });
        
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });
    }
    
    // Public API methods
    
    /**
     * Subscribe to SMA session updates
     * @param {string} sessionId - The session ID to monitor
     */
    subscribeToSession(sessionId) {
        const subscription = `sma_session_${sessionId}`;
        this.subscriptions.add(subscription);
        
        if (this.isConnected) {
            this.send({
                action: 'join_session',
                session_id: sessionId
            });
        }
    }
    
    /**
     * Unsubscribe from SMA session updates
     * @param {string} sessionId - The session ID to stop monitoring
     */
    unsubscribeFromSession(sessionId) {
        const subscription = `sma_session_${sessionId}`;
        this.subscriptions.delete(subscription);
        
        if (this.isConnected) {
            this.send({
                action: 'leave_session',
                session_id: sessionId
            });
        }
    }
    
    /**
     * Subscribe to all SMA updates (for monitoring dashboard)
     */
    subscribeToAllSMA() {
        const subscription = 'sma_all';
        this.subscriptions.add(subscription);
        
        if (this.isConnected) {
            this.send({
                type: 'subscribe',
                subscription: subscription
            });
        }
    }
    
    /**
     * Unsubscribe from all SMA updates
     */
    unsubscribeFromAllSMA() {
        const subscription = 'sma_all';
        this.subscriptions.delete(subscription);
        
        if (this.isConnected) {
            this.send({
                type: 'unsubscribe',
                subscription: subscription
            });
        }
    }
    
    /**
     * Subscribe to project-specific updates
     * @param {number} projectId - The project ID to monitor
     */
    subscribeToProject(projectId) {
        const subscription = `project_${projectId}`;
        this.subscriptions.add(subscription);
        
        if (this.isConnected) {
            this.send({
                type: 'subscribe',
                subscription: subscription
            });
        }
    }
    
    /**
     * Unsubscribe from project-specific updates
     * @param {number} projectId - The project ID to stop monitoring
     */
    unsubscribeFromProject(projectId) {
        const subscription = `project_${projectId}`;
        this.subscriptions.delete(subscription);
        
        if (this.isConnected) {
            this.send({
                type: 'unsubscribe',
                subscription: subscription
            });
        }
    }
    
    /**
     * Send a message through the WebSocket
     * @param {Object} message - The message to send
     */
    send(message) {
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            try {
                this.socket.send(JSON.stringify(message));
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
            }
        } else {
            console.warn('Cannot send message: WebSocket not connected');
        }
    }
    
    /**
     * Manually disconnect the WebSocket
     */
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'Manual disconnect');
        }
        this.stopHeartbeat();
    }
    
    /**
     * Get connection status
     * @returns {boolean} True if connected
     */
    getConnectionStatus() {
        return this.isConnected;
    }
    
    /**
     * Get active subscriptions
     * @returns {Set} Set of active subscriptions
     */
    getSubscriptions() {
        return new Set(this.subscriptions);
    }
    
    /**
     * Clear all subscriptions
     */
    clearSubscriptions() {
        // Unsubscribe from all
        this.subscriptions.forEach(subscription => {
            if (this.isConnected) {
                this.send({
                    type: 'unsubscribe',
                    subscription: subscription
                });
            }
        });
        
        this.subscriptions.clear();
    }
    
    /**
     * Force reconnection
     */
    forceReconnect() {
        if (this.socket) {
            this.socket.close();
        }
        this.reconnectAttempts = 0;
        this.connect();
    }
}

// Enhanced WebSocket client with additional SMA-specific features
class SMAWebSocketClient extends WebSocketClient {
    constructor() {
        super();
        
        // Enhanced session management
        this.sessionCallbacks = new Map();
        this.sessionSubscriptions = new Set();
        this.logSubscriptions = new Map(); // sessionId -> level
        this.healthMonitoring = new Set();
        
        // Message queue for when disconnected
        this.messageQueue = [];
        
        // Enhanced callbacks
        this.onSessionUpdate = null;
        this.onLogUpdate = null;
        this.onHealthAlert = null;
        this.onError = null;
    }
    
    // Enhanced session monitoring with comprehensive callbacks
    startSessionMonitoring(sessionId, callbacks = {}) {
        if (!sessionId) {
            console.warn('Cannot start monitoring: no session ID provided');
            return false;
        }
        
        console.log(`Starting enhanced monitoring for session: ${sessionId}`);
        
        // Store callbacks for this session
        this.sessionCallbacks.set(sessionId, {
            onProgress: callbacks.onProgress || null,
            onWorkflowState: callbacks.onWorkflowState || null,
            onLog: callbacks.onLog || null,
            onError: callbacks.onError || null,
            onComplete: callbacks.onComplete || null,
            onHealthAlert: callbacks.onHealthAlert || null,
            onStatusChange: callbacks.onStatusChange || null
        });
        
        // Subscribe to session updates
        this.subscribeToSession(sessionId);
        
        // Subscribe to logs with default level
        this.subscribeToSessionLogs(sessionId, 'info');
        
        // Enable health monitoring
        this.enableHealthMonitoring(sessionId);
        
        return true;
    }
    
    stopSessionMonitoring(sessionId) {
        if (!sessionId) {
            console.warn('Cannot stop monitoring: no session ID provided');
            return;
        }
        
        console.log(`Stopping monitoring for session: ${sessionId}`);
        
        // Remove callbacks
        this.sessionCallbacks.delete(sessionId);
        
        // Unsubscribe from session
        this.unsubscribeFromSession(sessionId);
        
        // Unsubscribe from logs
        this.unsubscribeFromSessionLogs(sessionId);
        
        // Disable health monitoring
        this.disableHealthMonitoring(sessionId);
    }
    
    // Enhanced subscription methods
    subscribeToSession(sessionId) {
        if (!sessionId) return false;
        
        this.sessionSubscriptions.add(sessionId);
        
        const message = {
            type: 'subscribe_session',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    unsubscribeFromSession(sessionId) {
        if (!sessionId) return false;
        
        this.sessionSubscriptions.delete(sessionId);
        
        const message = {
            type: 'unsubscribe_session',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    subscribeToSessionLogs(sessionId, level = 'info') {
        if (!sessionId) return false;
        
        this.logSubscriptions.set(sessionId, level);
        
        const message = {
            type: 'subscribe_logs',
            session_id: sessionId,
            level: level,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    unsubscribeFromSessionLogs(sessionId) {
        if (!sessionId) return false;
        
        this.logSubscriptions.delete(sessionId);
        
        const message = {
            type: 'unsubscribe_logs',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    enableHealthMonitoring(sessionId) {
        if (!sessionId) return false;
        
        this.healthMonitoring.add(sessionId);
        
        const message = {
            type: 'enable_health_monitoring',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    disableHealthMonitoring(sessionId) {
        if (!sessionId) return false;
        
        this.healthMonitoring.delete(sessionId);
        
        const message = {
            type: 'disable_health_monitoring',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Enhanced message handling
    handleMessage(data) {
        // Call parent handler first
        super.handleMessage(data);
        
        // Handle enhanced SMA-specific messages
                    switch (data.type) {
                        case 'sma_progress':
                this.handleEnhancedProgress(data);
                break;
                
            case 'sma_workflow_state':
                this.handleEnhancedWorkflowState(data);
                            break;
                
                        case 'sma_log':
                this.handleEnhancedLog(data);
                break;
                
            case 'sma_error':
                this.handleEnhancedError(data);
                break;
                
            case 'sma_completed':
                this.handleSessionComplete(data);
                break;
                
            case 'sma_health_alert':
                this.handleHealthAlert(data);
                break;
                
            case 'sma_status_change':
                this.handleStatusChange(data);
                            break;
                
            case 'session_subscribed':
                console.log(`Successfully subscribed to session: ${data.session_id}`);
                            break;
                
            case 'session_unsubscribed':
                console.log(`Successfully unsubscribed from session: ${data.session_id}`);
                            break;
                
            case 'subscription_error':
                console.error(`Subscription error: ${data.error}`);
                this.handleSubscriptionError(data);
                            break;
                    }
                }
    
    handleEnhancedProgress(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onProgress) {
            callbacks.onProgress(data.data);
    }
    
        // Also call global callback
        if (this.onSessionUpdate) {
            this.onSessionUpdate({
                type: 'progress',
                sessionId: sessionId,
                data: data.data
            });
        }
    }
    
    handleEnhancedWorkflowState(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onWorkflowState) {
            callbacks.onWorkflowState(data.data);
        }
        
        // Also call global callback
        if (this.onSessionUpdate) {
            this.onSessionUpdate({
                type: 'workflow_state',
                sessionId: sessionId,
                data: data.data
            });
        }
    }
    
    handleEnhancedLog(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onLog) {
            callbacks.onLog(data.data);
        }
        
        // Also call global log callback
        if (this.onLogUpdate) {
            this.onLogUpdate({
                sessionId: sessionId,
                logEntry: data.data
            });
        }
    }
    
    handleEnhancedError(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onError) {
            callbacks.onError(data.data);
        }
        
        // Also call global error callback
        if (this.onError) {
            this.onError({
                sessionId: sessionId,
                error: data.data
            });
        }
    }
    
    handleSessionComplete(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onComplete) {
            callbacks.onComplete(data.data);
        }
        
        // Also call global callback
        if (this.onSessionUpdate) {
            this.onSessionUpdate({
                type: 'completed',
                sessionId: sessionId,
                data: data.data
            });
        }
    }
    
    handleHealthAlert(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onHealthAlert) {
            callbacks.onHealthAlert(data.data);
    }
    
        // Also call global health callback
        if (this.onHealthAlert) {
            this.onHealthAlert({
                sessionId: sessionId,
                health: data.data
            });
        }
    }
    
    handleStatusChange(data) {
        const sessionId = data.session_id;
        const callbacks = this.sessionCallbacks.get(sessionId);
        
        if (callbacks && callbacks.onStatusChange) {
            callbacks.onStatusChange(data.data);
        }
        
        // Also call global callback
        if (this.onSessionUpdate) {
            this.onSessionUpdate({
                type: 'status_change',
                sessionId: sessionId,
                data: data.data
            });
        }
    }
    
    handleSubscriptionError(data) {
        console.error('Subscription error:', data);
        
        if (this.onError) {
            this.onError({
                type: 'subscription_error',
                error: data.error,
                details: data.details
            });
        }
    }
    
    // Enhanced session commands
    sendSessionCommand(sessionId, command, params = {}) {
        if (!sessionId || !command) {
            console.warn('Cannot send command: missing session ID or command');
            return false;
        }
        
        const message = {
            type: 'session_command',
            session_id: sessionId,
            command: command,
            params: params,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Request session status
    requestSessionStatus(sessionId) {
        if (!sessionId) {
            console.warn('Cannot request status: no session ID provided');
            return false;
        }
        
        const message = {
            type: 'get_session_status',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Request session health
    requestSessionHealth(sessionId) {
        if (!sessionId) {
            console.warn('Cannot request health: no session ID provided');
            return false;
        }
        
        const message = {
            type: 'get_health_status',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Request session logs
    requestSessionLogs(sessionId, limit = 50, level = null) {
        if (!sessionId) {
            console.warn('Cannot request logs: no session ID provided');
            return false;
        }
        
        const message = {
            type: 'get_session_logs',
            session_id: sessionId,
            limit: limit,
            level: level,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Request session statistics
    requestSessionStatistics(sessionId) {
        if (!sessionId) {
            console.warn('Cannot request statistics: no session ID provided');
            return false;
        }
        
        const message = {
            type: 'get_session_statistics',
            session_id: sessionId,
            timestamp: new Date().toISOString()
        };
        
        return this.send(message);
    }
    
    // Enhanced send method with queuing
    send(message) {
        if (this.isConnected && this.socket && this.socket.readyState === WebSocket.OPEN) {
            try {
                this.socket.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
                this.messageQueue.push(message);
                return false;
            }
        } else {
            // Queue message for when connection is restored
            this.messageQueue.push(message);
            console.log('Message queued (not connected):', message.type);
            return false;
        }
    }
    
    // Process queued messages when connection is restored
    processMessageQueue() {
        console.log(`Processing ${this.messageQueue.length} queued messages`);
        
        while (this.messageQueue.length > 0 && this.isConnected) {
            const message = this.messageQueue.shift();
            if (!this.send(message)) {
                // If sending fails, put it back at the front
                this.messageQueue.unshift(message);
                break;
            }
        }
    }
    
    // Enhanced resubscribe method
    resubscribe() {
        super.resubscribe();
        
        // Re-subscribe to session-specific subscriptions
        for (const sessionId of this.sessionSubscriptions) {
            this.subscribeToSession(sessionId);
        }
        
        // Re-subscribe to log subscriptions
        for (const [sessionId, level] of this.logSubscriptions) {
            this.subscribeToSessionLogs(sessionId, level);
        }
        
        // Re-enable health monitoring
        for (const sessionId of this.healthMonitoring) {
            this.enableHealthMonitoring(sessionId);
        }
        
        // Process any queued messages
        this.processMessageQueue();
    }
    
    // Enhanced connection handling
    onOpen(event) {
        super.onOpen(event);
        
        // Process queued messages
        this.processMessageQueue();
    }
    
    // Get enhanced connection status
    getEnhancedStatus() {
        return {
            ...this.getConnectionStatus(),
            sessionSubscriptions: Array.from(this.sessionSubscriptions),
            logSubscriptions: Object.fromEntries(this.logSubscriptions),
            healthMonitoring: Array.from(this.healthMonitoring),
            queuedMessages: this.messageQueue.length,
            activeCallbacks: this.sessionCallbacks.size
        };
    }
    
    // Clean up all session-specific data
    cleanup() {
        this.sessionCallbacks.clear();
        this.sessionSubscriptions.clear();
        this.logSubscriptions.clear();
        this.healthMonitoring.clear();
        this.messageQueue = [];
        
        this.disconnect();
    }
    
    // Utility methods
    isMonitoringSession(sessionId) {
        return this.sessionCallbacks.has(sessionId);
    }
    
    getMonitoredSessions() {
        return Array.from(this.sessionCallbacks.keys());
    }
    
    setLogLevel(sessionId, level) {
        if (this.logSubscriptions.has(sessionId)) {
            this.subscribeToSessionLogs(sessionId, level);
        }
    }
}

// Export for use in other modules
window.WebSocketClient = WebSocketClient;
window.SMAWebSocketClient = SMAWebSocketClient;

// Auto-initialize if in SMA filming context
if (window.location.pathname.includes('/film/sma')) {
    window.smaWebSocket = new SMAWebSocketClient();
} 