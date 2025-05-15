// config_storage.c
#include "config_storage.h"
#include "nvs_flash.h"
#include "nvs.h"
#include <string.h>

error_code_t storage_read(const char* namespace, void* data, size_t size) {
    nvs_handle_t nvs_handle;
    esp_err_t err;
    
    // Initialize NVS
    err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        // NVS partition was truncated and needs to be erased
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    
    if (err != ESP_OK) {
        return ERR_HARDWARE;
    }
    
    // Open NVS namespace
    err = nvs_open(namespace, NVS_READONLY, &nvs_handle);
    if (err != ESP_OK) {
        return ERR_MEMORY;
    }
    
    // Read blob
    size_t required_size = size;
    err = nvs_get_blob(nvs_handle, "config", NULL, &required_size);
    
    if (err == ESP_OK && required_size == size) {
        err = nvs_get_blob(nvs_handle, "config", data, &required_size);
        if (err != ESP_OK) {
            nvs_close(nvs_handle);
            return ERR_MEMORY;
        }
    } else {
        nvs_close(nvs_handle);
        return ERR_INVALID_CONFIG;
    }
    
    // Close
    nvs_close(nvs_handle);
    return ERR_NONE;
}

error_code_t storage_write(const char* namespace, const void* data, size_t size) {
    nvs_handle_t nvs_handle;
    esp_err_t err;
    
    // Initialize NVS
    err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    
    if (err != ESP_OK) {
        return ERR_HARDWARE;
    }
    
    // Open
    err = nvs_open(namespace, NVS_READWRITE, &nvs_handle);
    if (err != ESP_OK) {
        return ERR_MEMORY;
    }
    
    // Write
    err = nvs_set_blob(nvs_handle, "config", data, size);
    if (err != ESP_OK) {
        nvs_close(nvs_handle);
        return ERR_MEMORY;
    }
    
    // Commit changes
    err = nvs_commit(nvs_handle);
    if (err != ESP_OK) {
        nvs_close(nvs_handle);
        return ERR_MEMORY;
    }
    
    // Close
    nvs_close(nvs_handle);
    return ERR_NONE;
}

error_code_t storage_erase(const char* namespace) {
    nvs_handle_t nvs_handle;
    esp_err_t err;
    
    // Open
    err = nvs_open(namespace, NVS_READWRITE, &nvs_handle);
    if (err != ESP_OK) {
        return ERR_MEMORY;
    }
    
    // Erase all keys in this namespace
    err = nvs_erase_all(nvs_handle);
    if (err != ESP_OK) {
        nvs_close(nvs_handle);
        return ERR_MEMORY;
    }
    
    // Commit
    err = nvs_commit(nvs_handle);
    if (err != ESP_OK) {
        nvs_close(nvs_handle);
        return ERR_MEMORY;
    }
    
    // Close
    nvs_close(nvs_handle);
    return ERR_NONE;
}