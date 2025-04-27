// network_manager.h
#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include "relay_controller.h"

typedef void (*websocket_callback_t)(const char* data, size_t len);

// Initialize network stack
error_code_t network_init(const system_config_t* config);

// Start WebSocket server
error_code_t network_start_websocket(int port, websocket_callback_t callback);

// Send data to WebSocket client
error_code_t network_websocket_send(uint8_t client_id, const char* data);

// Broadcast data to all WebSocket clients
error_code_t network_websocket_broadcast(const char* data);

// Process network events
void network_process(void);

// OTA update
error_code_t network_start_ota_update(const char* url);

#endif // NETWORK_MANAGER_H