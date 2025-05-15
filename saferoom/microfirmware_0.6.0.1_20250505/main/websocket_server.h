#ifndef WEBSOCKET_SERVER_H
#define WEBSOCKET_SERVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_http_server.h"

// Forward declarations
typedef struct websocket_server websocket_server_t;
typedef struct websocket_client websocket_client_t;

typedef enum {
    WEBSOCKET_EVENT_CONNECT,
    WEBSOCKET_EVENT_DISCONNECT,
    WEBSOCKET_EVENT_DATA,
    WEBSOCKET_EVENT_ERROR
} websocket_event_t;

typedef void (*websocket_callback_fn)(
    websocket_server_t* server,
    websocket_client_t* client,
    websocket_event_t type,
    const uint8_t* data,
    uint16_t len
);

// Client structure
struct websocket_client {
    int sockfd;                    // Client socket
    bool is_connected;             // Connection status
    uint8_t id;                    // Client ID
    struct websocket_client* next; // Linked list
};

// Server structure
struct websocket_server {
    int port;                      // WebSocket port
    httpd_handle_t server;         // HTTP server handle
    websocket_callback_fn callback; // Event callback
    websocket_client_t* clients;   // Linked list of clients
    uint8_t client_count;          // Number of connected clients
};

// Initialize a WebSocket server
void websocket_server_init(websocket_server_t* server);

// Set the callback function for WebSocket events
void websocket_server_set_callback(websocket_server_t* server, websocket_callback_fn callback);

// Start the WebSocket server on the specified port
int websocket_server_start(websocket_server_t* server, int port);

// Stop the WebSocket server
void websocket_server_stop(websocket_server_t* server);

// Process incoming WebSocket messages (should be called in the main loop)
void websocket_server_process(websocket_server_t* server);

// Send text data to a specific client
int websocket_server_send_text(websocket_server_t* server, uint8_t client_id, const uint8_t* data, uint16_t len);

// Send text data to all connected clients
int websocket_server_send_text_all(websocket_server_t* server, const uint8_t* data, uint16_t len);

#endif // WEBSOCKET_SERVER_H 