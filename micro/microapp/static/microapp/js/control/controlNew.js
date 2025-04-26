// Control Panel JavaScript

// --- WebSocket setup and fallback logic ---
let ws;
let wsAvailable = false;
let wsUrl = 'ws://127.0.0.1:8000/ws/relay/'; // Replace with your Django server

function setupWebSocket() {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
        wsAvailable = true;
        console.log("WebSocket connected");
        // Optionally: update UI to show real-time mode
    };
    ws.onclose = () => {
        wsAvailable = false;
        console.log("WebSocket closed, falling back to HTTP");
        // Optionally: update UI to show fallback mode
    };
    ws.onerror = () => {
        wsAvailable = false;
        console.log("WebSocket error, falling back to HTTP");
    };
    ws.onmessage = (event) => {
        handleWsMessage(event.data);
    };
}

function handleWsMessage(data) {
    // Parse and route the message to the appropriate UI update function
    const msg = JSON.parse(data);
    // Example: handle relay state, system stats, etc.
    // You can expand this as needed for your UI
    if (msg.type === 'relays') {
        updateRelayStatesUI(msg.states);
    } else if (msg.type === 'system') {
        updateESP32StatsUI(msg);
    } else if (msg.type === 'relay') {
        // Single relay state update
        // Optionally update a single relay indicator
    } else if (msg.type === 'pong') {
        // Handle ping response
        updateLatencyDisplay(30); // Example: set to 30ms
    } else if (msg.type === 'error') {
        showNotification(msg.message, 'error');
    }
}

// Call this on page load
setupWebSocket();

// --- Unified action function ---
function sendRelayAction(actionObj, httpFallbackUrl, httpFallbackBody, onSuccess, onError) {
    if (wsAvailable && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(actionObj));
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (onSuccess) onSuccess(data);
        };
        ws.onerror = (event) => {
            wsAvailable = false;
            if (onError) onError(event);
        };
    } else {
        // Fallback to HTTP
        fetch(httpFallbackUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams(httpFallbackBody)
        })
        .then(response => response.json())
        .then(data => {
            if (onSuccess) onSuccess(data);
        })
        .catch(error => {
            if (onError) onError(error);
        });
    }
}

// --- Example usage for relay toggle ---
function toggleRelay(relayNum) {
    const relayIndicator = document.getElementById(`relay-indicator-${relayNum}`);
    const isCurrentlyOn = relayIndicator.classList.contains('on');
    const action = isCurrentlyOn ? 'off' : 'on';
    sendRelayAction(
        { action: action, relay: parseInt(relayNum), state: !isCurrentlyOn },
        '/control_relay/',
        { action: action, relay: relayNum, com_port: getActiveRelayPort() },
        (data) => {
            if (data.status === 'success' || data.type === 'relay') {
                // Update UI immediately
                setRelayIndicatorState(relayNum, !isCurrentlyOn, false);
                // Track intended state
                pendingRelayStates[relayNum] = !isCurrentlyOn;
                // Optionally: fetch all states for confirmation
                setTimeout(() => {
                    updateESP32Stats();
                }, 150); // 700ms delay (tune as needed)
            }
        },
        (error) => {
            showNotification('Error controlling relay', 'error');
        }
    );
}

// --- Example usage for status update ---
function updateESP32Stats() {
    sendRelayAction(
        { action: 'system' },
        '/get_system_stats/',
        {},
        (data) => {
            if (data.system_stats) {
                updateESP32StatsUI(data.system_stats);
            } else if (data.type === 'system') {
                updateESP32StatsUI(data);
            }
        },
        (error) => {
            showNotification('Error fetching ESP32 stats', 'error');
        }
    );
    sendRelayAction(
        { action: 'status' },
        '/get_relay_status/',
        {},
        (data) => {
            if (data.relay_states) {
                updateRelayStatesUI(data.relay_states);
            } else if (data.type === 'relays') {
                updateRelayStatesUI(data.states);
            }
        },
        (error) => {
            showNotification('Error fetching relay status', 'error');
        }
    );
}

// --- Example usage for ping/latency ---
function measureESP32Latency() {
    const start = performance.now();
    sendRelayAction(
        { action: 'ping' },
        '/control_relay/',
        { action: 'ping', com_port: getActiveRelayPort() },
        (data) => {
            const latency = Math.round(performance.now() - start);
            updateLatencyDisplay(latency);
        },
        (error) => {
            updateLatencyDisplay(999);
        }
    );
}

// --- Mode toggle (light/dark) for the relay ---
function toggleRelayMode() {
    if (!isRelayConnected) {
        showNotification('Relay not connected', 'error');
        return;
    }
    // Get current mode and determine target mode
    const currentModeIcon = document.getElementById('mode-indicator');
    const targetMode = currentModeIcon && currentModeIcon.classList.contains('fa-sun') ? 'dark' : 'light';
    sendRelayAction(
        { action: targetMode },
        '/control_relay/',
        { action: targetMode, com_port: getActiveRelayPort() },
        (data) => {
            if (data.status === 'success' || data.mode) {
                updateModeDisplay(data.mode || targetMode);
                if (data.relay_states) {
                    updateRelayStatesUI(data.relay_states);
                }
                showNotification(`${targetMode.charAt(0).toUpperCase() + targetMode.slice(1)} activated`, 'success');
            } else {
                showNotification(`Failed to change mode: ${data.message}`, 'error');
            }
        },
        (error) => {
            showNotification('Error toggling mode', 'error');
        }
    );
}

// --- Periodic relay state check ---
function checkRelayStates() {
    sendRelayAction(
        { action: 'status' },
        '/get_relay_status/',
        {},
        (data) => {
            if (data.relay_states) {
                updateRelayStatesUI(data.relay_states);
            } else if (data.type === 'relays') {
                updateRelayStatesUI(data.states);
            }
            if (data.current_mode) {
                updateModeDisplay(data.current_mode);
            }
        },
        (error) => {
            // Optionally show notification or log
        }
    );
}