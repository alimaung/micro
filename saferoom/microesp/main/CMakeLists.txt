idf_component_register(
    SRCS "main.c" 
         "relay_controller.c" 
         "hardware_hal.c" 
         "network_manager.c" 
         "json_helper.c"
         "config_storage.c"
         "websocket_server.c"
    INCLUDE_DIRS "."
    REQUIRES nvs_flash           # For NVS storage
             esp_http_client     # For HTTP client
             esp_https_ota       # For OTA updates
             json                # For cJSON
             driver              # For GPIO and ADC
             esp_adc            # For ADC functionality
             esp_wifi           # For WiFi functionality
             esp_system         # For system functions
             freertos           # For FreeRTOS
             esp_event          # For event handling
             lwip               # For sockets
             esp_common         # For common ESP functions
             log                # For ESP logging
             esp_http_server    # For WebSocket server
             esp_timer          # For esp_timer_get_time
             soc                # For access to chip info and temperature
)