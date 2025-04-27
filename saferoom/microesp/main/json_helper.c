// json_helper.c
#include "json_helper.h"
#include "network_manager.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <cJSON.h>  // You'll need to add cJSON to your project

int json_parse_string(const char* json, const char* key, char* value, size_t max_len) {
    cJSON* root = cJSON_Parse(json);
    if (root == NULL) {
        return -1;
    }
    
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (!cJSON_IsString(item)) {
        cJSON_Delete(root);
        return -1;
    }
    
    strncpy(value, item->valuestring, max_len - 1);
    value[max_len - 1] = '\0';
    
    cJSON_Delete(root);
    return 0;
}

int json_parse_int(const char* json, const char* key, int* value) {
    cJSON* root = cJSON_Parse(json);
    if (root == NULL) {
        return -1;
    }
    
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (!cJSON_IsNumber(item)) {
        cJSON_Delete(root);
        return -1;
    }
    
    *value = item->valueint;
    
    cJSON_Delete(root);
    return 0;
}

int json_parse_bool(const char* json, const char* key, bool* value) {
    cJSON* root = cJSON_Parse(json);
    if (root == NULL) {
        return -1;
    }
    
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (!cJSON_IsBool(item)) {
        cJSON_Delete(root);
        return -1;
    }
    
    *value = cJSON_IsTrue(item);
    
    cJSON_Delete(root);
    return 0;
}

int json_parse_object(const char* json, const char* key, char* value, size_t max_len) {
    cJSON* root = cJSON_Parse(json);
    if (root == NULL) {
        return -1;
    }
    
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (!cJSON_IsObject(item)) {
        cJSON_Delete(root);
        return -1;
    }
    
    char* obj_str = cJSON_PrintUnformatted(item);
    if (obj_str == NULL) {
        cJSON_Delete(root);
        return -1;
    }
    
    strncpy(value, obj_str, max_len - 1);
    value[max_len - 1] = '\0';
    
    free(obj_str);
    cJSON_Delete(root);
    return 0;
}

void json_create_relay_state(char* buffer, size_t buffer_size, int relay, bool state) {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "relay");
    cJSON_AddNumberToObject(root, "relay", relay);
    cJSON_AddBoolToObject(root, "state", state);
    
    char* json_str = cJSON_PrintUnformatted(root);
    strncpy(buffer, json_str, buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
    
    free(json_str);
    cJSON_Delete(root);
}

void json_create_all_relay_states(char* buffer, size_t buffer_size, const bool* states, int num_relays) {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "relays");
    
    cJSON* states_array = cJSON_CreateArray();
    for (int i = 0; i < num_relays; i++) {
        cJSON_AddItemToArray(states_array, cJSON_CreateBool(states[i]));
    }
    cJSON_AddItemToObject(root, "states", states_array);
    
    char* json_str = cJSON_PrintUnformatted(root);
    strncpy(buffer, json_str, buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
    
    free(json_str);
    cJSON_Delete(root);
}

void json_create_system_stats(char* buffer, size_t buffer_size, const system_stats_t* stats) {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "system");
    cJSON_AddNumberToObject(root, "cpu_mhz", stats->cpu_freq_mhz);
    cJSON_AddNumberToObject(root, "temp_c", stats->cpu_temp);
    cJSON_AddNumberToObject(root, "ram_kb", stats->free_heap_bytes / 1024.0);
    cJSON_AddNumberToObject(root, "voltage_v", stats->main_voltage);
    cJSON_AddNumberToObject(root, "uptime_s", stats->uptime_sec);
    
    char* json_str = cJSON_PrintUnformatted(root);
    strncpy(buffer, json_str, buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
    
    free(json_str);
    cJSON_Delete(root);
}

void json_send_error(const char* message) {
    char buffer[128];
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "error");
    cJSON_AddStringToObject(root, "message", message);
    
    char* json_str = cJSON_PrintUnformatted(root);
    strncpy(buffer, json_str, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    
    network_websocket_broadcast(buffer);
    
    free(json_str);
    cJSON_Delete(root);
}

void json_create_config_response(char* buffer, size_t buffer_size, bool success, const char* message) {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "config");
    cJSON_AddStringToObject(root, "status", success ? "success" : "error");
    cJSON_AddStringToObject(root, "message", message);
    
    char* json_str = cJSON_PrintUnformatted(root);
    strncpy(buffer, json_str, buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
    
    free(json_str);
    cJSON_Delete(root);
}