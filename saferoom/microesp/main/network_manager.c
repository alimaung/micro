// network_manager.c
#include "network_manager.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_https_ota.h"
#include <string.h>
#include <lwip/sockets.h>
#include "esp_log.h"

// Use a WebSocket library like https://github.com/Molorius/esp32-websocket
// This is a simplified version for example purposes
#include "websocket_server.h"  // You would need to implement or find this

static const char* TAG = "network";
static websocket_callback_t ws_callback = NULL;
static websocket_server_t ws_server;

// Event handler for WiFi events
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                              int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        esp_wifi_connect();
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ip4_addr_t ip4_addr;
        ip4_addr.addr = event->ip_info.ip.addr;
        ESP_LOGI(TAG, "Got IP: %s", ip4addr_ntoa(&ip4_addr));
    }
}

// WebSocket event handler
static void websocket_callback(websocket_server_t* server, 
                              websocket_client_t* client,
                              websocket_event_t type, 
                              const uint8_t* data, uint16_t len) {
    switch (type) {
        case WEBSOCKET_EVENT_CONNECT:
            ESP_LOGI(TAG, "Client connected");
            break;
        case WEBSOCKET_EVENT_DISCONNECT:
            ESP_LOGI(TAG, "Client disconnected");
            break;
        case WEBSOCKET_EVENT_DATA:
            if (ws_callback) {
                ws_callback((const char*)data, len);
            }
            break;
        default:
            break;
    }
}

error_code_t network_init(const system_config_t* config) {
    esp_err_t ret = esp_netif_init();
    if (ret != ESP_OK) return ERR_NETWORK;
    
    ret = esp_event_loop_create_default();
    if (ret != ESP_OK) return ERR_NETWORK;
    
    esp_netif_t* sta_netif = esp_netif_create_default_wifi_sta();
    esp_netif_t* ap_netif = esp_netif_create_default_wifi_ap();
    
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ret = esp_wifi_init(&cfg);
    if (ret != ESP_OK) return ERR_NETWORK;
    
    // Register event handlers
    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                       ESP_EVENT_ANY_ID,
                                                       &wifi_event_handler,
                                                       NULL,
                                                       &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                       IP_EVENT_STA_GOT_IP,
                                                       &wifi_event_handler,
                                                       NULL,
                                                       &instance_got_ip));
    
    // Configure WiFi based on the mode in config
    if (strcmp(config->wifi_mode, "ap") == 0) {
        // Configure AP mode
        wifi_config_t wifi_config = {
            .ap = {
                .ssid_len = strlen(config->wifi_ssid),
                .max_connection = 4,
                .authmode = WIFI_AUTH_WPA2_PSK
            },
        };
        strcpy((char*)wifi_config.ap.ssid, config->wifi_ssid);
        strcpy((char*)wifi_config.ap.password, config->wifi_password);
        
        ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
        ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_AP, &wifi_config));
    } else {
        // Configure STA mode
        wifi_config_t wifi_config = {
            .sta = {
                .pmf_cfg = {
                    .capable = true,
                    .required = false
                },
            },
        };
        strcpy((char*)wifi_config.sta.ssid, config->wifi_ssid);
        strcpy((char*)wifi_config.sta.password, config->wifi_password);
        
        // Configure static IP if provided
        esp_netif_dhcpc_stop(sta_netif);
        esp_netif_ip_info_t ip_info;
        ip_info.ip.addr = config->static_ip;
        ip_info.gw.addr = config->gateway;
        ip_info.netmask.addr = config->subnet;
        esp_netif_set_ip_info(sta_netif, &ip_info);
        
        ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
        ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config));
    }
    
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_LOGI(TAG, "WiFi initialized");
    
    return ERR_NONE;
}

error_code_t network_start_websocket(int port, websocket_callback_t callback) {
    ws_callback = callback;
    
    // Initialize WebSocket server
    websocket_server_init(&ws_server);
    websocket_server_set_callback(&ws_server, websocket_callback);
    
    int ret = websocket_server_start(&ws_server, port);
    if (ret != 0) {
        return ERR_NETWORK;
    }
    
    ESP_LOGI(TAG, "WebSocket server started on port %d", port);
    return ERR_NONE;
}

error_code_t network_websocket_send(uint8_t client_id, const char* data) {
    // This is a simplified example - in a real implementation you would
    // need to maintain a list of connected clients with their IDs
    int len = strlen(data);
    int ret = websocket_server_send_text(&ws_server, client_id, 
                                        (const uint8_t*)data, len);
    if (ret < 0) {
        return ERR_NETWORK;
    }
    return ERR_NONE;
}

error_code_t network_websocket_broadcast(const char* data) {
    int len = strlen(data);
    int ret = websocket_server_send_text_all(&ws_server, 
                                           (const uint8_t*)data, len);
    if (ret < 0) {
        return ERR_NETWORK;
    }
    return ERR_NONE;
}

void network_process(void) {
    websocket_server_process(&ws_server);
}

error_code_t network_start_ota_update(const char* url) {
    esp_http_client_config_t http_config = {
        .url = url,
        .timeout_ms = 10000,
    };
    
    esp_https_ota_config_t ota_config = {
        .http_config = &http_config,
    };
    
    esp_err_t ret = esp_https_ota(&ota_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "OTA Update failed");
        return ERR_NETWORK;
    }
    
    ESP_LOGI(TAG, "OTA Update successful");
    return ERR_NONE;
}