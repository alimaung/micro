// json_helper.h
#ifndef JSON_HELPER_H
#define JSON_HELPER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "relay_controller.h"

// Parse JSON helpers
int json_parse_string(const char* json, const char* key, char* value, size_t max_len);
int json_parse_int(const char* json, const char* key, int* value);
int json_parse_bool(const char* json, const char* key, bool* value);
int json_parse_object(const char* json, const char* key, char* value, size_t max_len);

// Create JSON helpers
void json_create_relay_state(char* buffer, size_t buffer_size, int relay, bool state);
void json_create_all_relay_states(char* buffer, size_t buffer_size, const bool* states, int num_relays);
void json_create_system_stats(char* buffer, size_t buffer_size, const system_stats_t* stats);
void json_send_error(const char* message);
void json_create_config_response(char* buffer, size_t buffer_size, bool success, const char* message);

#endif // JSON_HELPER_H