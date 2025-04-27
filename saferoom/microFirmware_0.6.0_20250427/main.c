// main.c
#include <stdio.h>
#include "relay_controller.h"
#include "network_manager.h"
#include "hardware_hal.h"
#include "json_helper.h"

void websocket_event_handler(const char* data, size_t len);
void handle_command(const char* json_data);
void send_relay_state(uint8_t relay_idx);
void send_all_relay_states(void);
void send_system_stats(void);

int main(void) {
    // Initialize hardware abstraction layer
    hal_init();
    
    // Initialize relay controller
    error_code_t err = relay_controller_init();
    if (err != ERR_NONE) {
        printf("Failed to initialize relay controller: %d\n", err);
        return 1;
    }
    
    // Initialize network stack with current configuration
    const system_config_t* config = config_get_current();
    err = network_init(config);
    if (err != ERR_NONE) {
        printf("Failed to initialize network: %d\n", err);
        return 1;
    }
    
    // Start WebSocket server
    err = network_start_websocket(81, websocket_event_handler);
    if (err != ERR_NONE) {
        printf("Failed to start WebSocket server: %d\n", err);
        return 1;
    }
    
    // Main loop
    while (1) {
        // Process relay tasks (handle pulse timeouts)
        relay_process();
        
        // Process network events
        network_process();
        
        // Optional: Broadcast status periodically
        // static uint32_t last_status_time = 0;
        // uint32_t current_time = hal_get_millis();
        // if (current_time - last_status_time > 5000) {
        //     send_all_relay_states();
        //     last_status_time = current_time;
        // }
    }
    
    return 0;
}

void websocket_event_handler(const char* data, size_t len) {
    handle_command(data);
}

void handle_command(const char* json_data) {
    // Note: Implementation would use the json_helper.h module to parse JSON
    // This is a simplified pseudocode representation
    char action[16];
    if (json_parse_string(json_data, "action", action, sizeof(action)) != 0) {
        json_send_error("Invalid JSON");
        return;
    }
    
    if (strcmp(action, "set") == 0) {
        int relay;
        bool state;
        
        if (json_parse_int(json_data, "relay", &relay) != 0 ||
            json_parse_bool(json_data, "state", &state) != 0) {
            json_send_error("Missing relay or state parameter");
            return;
        }
        
        if (relay < 1 || relay > 8) {
            json_send_error("Invalid relay number");
            return;
        }
        
        error_code_t err = relay_set_state(relay - 1, state);
        if (err != ERR_NONE) {
            json_send_error("Failed to set relay state");
            return;
        }
        
        send_relay_state(relay - 1);
    } 
    else if (strcmp(action, "pulse") == 0) {
        int relay;
        
        if (json_parse_int(json_data, "relay", &relay) != 0) {
            json_send_error("Missing relay parameter");
            return;
        }
        
        if (relay != 1) {
            json_send_error("Pulse only allowed for relay 1");
            return;
        }
        
        const system_config_t* config = config_get_current();
        error_code_t err = relay_pulse(0, config->pulse_duration_ms);
        if (err != ERR_NONE) {
            json_send_error("Failed to start pulse");
            return;
        }
        
        send_relay_state(0);
    }
    else if (strcmp(action, "status") == 0) {
        send_all_relay_states();
    }
    else if (strcmp(action, "system") == 0) {
        send_system_stats();
    }
    else if (strcmp(action, "config") == 0) {
        // Handle configuration updates
        // Implementation omitted for brevity
    }
    else {
        json_send_error("Unknown action");
    }
}

void send_relay_state(uint8_t relay_idx) {
    char buffer[64];
    json_create_relay_state(buffer, sizeof(buffer), relay_idx + 1, relay_get_state(relay_idx));
    network_websocket_broadcast(buffer);
}

void send_all_relay_states(void) {
    bool states[8];
    relay_get_all_states(states, 8);
    
    char buffer[128];
    json_create_all_relay_states(buffer, sizeof(buffer), states, 8);
    network_websocket_broadcast(buffer);
}

void send_system_stats(void) {
    system_stats_t stats;
    error_code_t err = system_get_stats(&stats);
    if (err != ERR_NONE) {
        json_send_error("Failed to get system stats");
        return;
    }
    
    char buffer[256];
    json_create_system_stats(buffer, sizeof(buffer), &stats);
    network_websocket_broadcast(buffer);
}