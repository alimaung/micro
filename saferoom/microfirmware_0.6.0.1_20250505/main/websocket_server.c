#include "websocket_server.h"
#include "esp_log.h"
#include "esp_http_server.h"
#include <string.h>
#include <sys/socket.h>

static const char* TAG = "websocket_server";

// WebSocket frame headers
#define WS_FIN            0x80
#define WS_OPCODE_TEXT    0x01
#define WS_OPCODE_BINARY  0x02
#define WS_OPCODE_CLOSE   0x08
#define WS_OPCODE_PING    0x09
#define WS_OPCODE_PONG    0x0A
#define WS_MASK           0x80

// Linked list of connected clients
static websocket_client_t* add_client(websocket_server_t* server, int sockfd) {
    websocket_client_t* client = (websocket_client_t*)malloc(sizeof(websocket_client_t));
    if (!client) {
        ESP_LOGE(TAG, "Failed to allocate memory for client");
        return NULL;
    }
    
    client->sockfd = sockfd;
    client->is_connected = true;
    client->id = server->client_count++;
    client->next = server->clients;
    server->clients = client;
    
    return client;
}

static void remove_client(websocket_server_t* server, websocket_client_t* client) {
    if (!client) return;
    
    // Handle first client in list
    if (server->clients == client) {
        server->clients = client->next;
        free(client);
        return;
    }
    
    // Find and remove from list
    websocket_client_t* current = server->clients;
    while (current && current->next != client) {
        current = current->next;
    }
    
    if (current && current->next == client) {
        current->next = client->next;
        free(client);
    }
}

// If the error persists, we need to implement a custom WebSocket solution
// Here's a simplified version using just the HTTP server for handshake and 
// raw sockets for communication

// Basic WebSocket frame parsing
typedef enum {
    WS_OP_CONT = 0x0,
    WS_OP_TEXT = 0x1,
    WS_OP_BIN = 0x2,
    WS_OP_CLOSE = 0x8,
    WS_OP_PING = 0x9,
    WS_OP_PONG = 0xA
} ws_opcode_t;

typedef struct {
    bool fin;
    bool mask;
    ws_opcode_t opcode;
    uint64_t payload_len;
    uint8_t mask_key[4];
    uint8_t* payload;
} ws_frame_t;

static esp_err_t parse_ws_frame(uint8_t* buf, size_t len, ws_frame_t* frame) {
    if (!buf || len < 2 || !frame) {
        return ESP_ERR_INVALID_ARG;
    }
    
    frame->fin = (buf[0] & 0x80) != 0;
    frame->opcode = buf[0] & 0x0F;
    frame->mask = (buf[1] & 0x80) != 0;
    frame->payload_len = buf[1] & 0x7F;
    
    int header_len = 2;
    
    // Extended payload length
    if (frame->payload_len == 126) {
        if (len < 4) return ESP_ERR_INVALID_SIZE;
        frame->payload_len = (buf[2] << 8) | buf[3];
        header_len += 2;
    } else if (frame->payload_len == 127) {
        if (len < 10) return ESP_ERR_INVALID_SIZE;
        frame->payload_len = 0;
        for (int i = 0; i < 8; i++) {
            frame->payload_len = (frame->payload_len << 8) | buf[2 + i];
        }
        header_len += 8;
    }
    
    // Mask key
    if (frame->mask) {
        if (len < header_len + 4) return ESP_ERR_INVALID_SIZE;
        memcpy(frame->mask_key, buf + header_len, 4);
        header_len += 4;
    }
    
    // Payload
    if (len < header_len + frame->payload_len) {
        return ESP_ERR_INVALID_SIZE;
    }
    
    frame->payload = buf + header_len;
    
    // Apply mask if needed
    if (frame->mask) {
        for (int i = 0; i < frame->payload_len; i++) {
            frame->payload[i] ^= frame->mask_key[i % 4];
        }
    }
    
    return ESP_OK;
}

static esp_err_t ws_handler(httpd_req_t *req) {
    websocket_server_t* server = (websocket_server_t*)req->user_ctx;
    if (req->method == HTTP_GET) {
        ESP_LOGI(TAG, "Handshake done, new WebSocket connection established");
        
        // Get the socket descriptor
        int sockfd = httpd_req_to_sockfd(req);
        websocket_client_t* client = add_client(server, sockfd);
        
        if (client && server->callback) {
            server->callback(server, client, WEBSOCKET_EVENT_CONNECT, NULL, 0);
        }
        
        return ESP_OK;
    }
    
    // Handle WebSocket data - using custom frame handling
    uint8_t buf[1024];  // Adjust size as needed
    int len = httpd_req_recv(req, (char*)buf, sizeof(buf));
    
    if (len <= 0) {
        if (len == HTTPD_SOCK_ERR_TIMEOUT) {
            return ESP_OK;  // Timeout, just return
        }
        
        // Client disconnected
        int sockfd = httpd_req_to_sockfd(req);
        websocket_client_t* client = server->clients;
        while (client && client->sockfd != sockfd) {
            client = client->next;
        }
        
        if (client && server->callback) {
            server->callback(server, client, WEBSOCKET_EVENT_DISCONNECT, NULL, 0);
            remove_client(server, client);
        }
        
        return ESP_OK;
    }
    
    // Parse WebSocket frame
    ws_frame_t frame = {0};
    if (parse_ws_frame(buf, len, &frame) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to parse WebSocket frame");
        return ESP_OK;
    }
    
    // Find the client
    int sockfd = httpd_req_to_sockfd(req);
    websocket_client_t* client = server->clients;
    while (client && client->sockfd != sockfd) {
        client = client->next;
    }
    
    // Process based on opcode
    if (client && server->callback) {
        switch (frame.opcode) {
            case WS_OP_TEXT:
                server->callback(server, client, WEBSOCKET_EVENT_DATA, 
                                frame.payload, frame.payload_len);
                break;
            case WS_OP_CLOSE:
                server->callback(server, client, WEBSOCKET_EVENT_DISCONNECT, NULL, 0);
                remove_client(server, client);
                break;
            default:
                ESP_LOGW(TAG, "Unhandled WebSocket opcode: %d", frame.opcode);
                break;
        }
    }
    
    return ESP_OK;
}

void websocket_server_init(websocket_server_t* server) {
    if (!server) return;
    
    memset(server, 0, sizeof(websocket_server_t));
}

void websocket_server_set_callback(websocket_server_t* server, websocket_callback_fn callback) {
    if (!server) return;
    
    server->callback = callback;
}

int websocket_server_start(websocket_server_t* server, int port) {
    if (!server) return -1;
    
    server->port = port;
    server->clients = NULL;
    server->client_count = 0;
    
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = port;
    config.max_open_sockets = 10;  // Adjust as needed
    
    esp_err_t ret = httpd_start(&server->server, &config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to start HTTP server: %d", ret);
        return -1;
    }
    
    httpd_uri_t ws_uri = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = ws_handler,
        .user_ctx = server
    };
    
    httpd_register_uri_handler(server->server, &ws_uri);
    ESP_LOGI(TAG, "WebSocket server started on port %d", port);
    
    return 0;
}

void websocket_server_stop(websocket_server_t* server) {
    if (!server || !server->server) return;
    
    // Free all clients
    websocket_client_t* client = server->clients;
    while (client) {
        websocket_client_t* next = client->next;
        free(client);
        client = next;
    }
    server->clients = NULL;
    
    httpd_stop(server->server);
    server->server = NULL;
    ESP_LOGI(TAG, "WebSocket server stopped");
}

void websocket_server_process(websocket_server_t* server) {
    // No active processing needed, as httpd handles connections in its own task
}

int websocket_server_send_text(websocket_server_t* server, uint8_t client_id, const uint8_t* data, uint16_t len) {
    if (!server || !data) return -1;
    
    // Find client with matching ID
    websocket_client_t* client = server->clients;
    while (client && client->id != client_id) {
        client = client->next;
    }
    
    if (!client || !client->is_connected) {
        ESP_LOGW(TAG, "Client %d not found or not connected", client_id);
        return -1;
    }
    
    // Create WebSocket frame
    uint8_t* frame;
    size_t frame_len;
    
    if (len < 126) {
        frame_len = 2 + len;
        frame = malloc(frame_len);
        if (!frame) return -1;
        
        frame[0] = 0x81;  // FIN=1, opcode=text
        frame[1] = len;   // No mask, payload len
        memcpy(frame + 2, data, len);
    } else {
        frame_len = 4 + len;
        frame = malloc(frame_len);
        if (!frame) return -1;
        
        frame[0] = 0x81;      // FIN=1, opcode=text
        frame[1] = 126;       // No mask, payload len = 126 (extended)
        frame[2] = (len >> 8) & 0xFF;  // Extended len MSB
        frame[3] = len & 0xFF;         // Extended len LSB
        memcpy(frame + 4, data, len);
    }
    
    // Send frame via socket
    int ret = send(client->sockfd, frame, frame_len, 0);
    free(frame);
    
    if (ret < 0) {
        ESP_LOGE(TAG, "Failed to send data: %d", errno);
        return -1;
    }
    
    return len;
}

int websocket_server_send_text_all(websocket_server_t* server, const uint8_t* data, uint16_t len) {
    if (!server || !data) return -1;
    
    int count = 0;
    websocket_client_t* client = server->clients;
    
    while (client) {
        if (client->is_connected) {
            if (websocket_server_send_text(server, client->id, data, len) > 0) {
                count++;
            }
        }
        client = client->next;
    }
    
    return count;
} 