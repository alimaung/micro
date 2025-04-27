// relay_controller.h
#ifndef RELAY_CONTROLLER_H
#define RELAY_CONTROLLER_H

#include <stdbool.h>
#include <stdint.h>

// Configuration structure
typedef struct {
    int relay_pins[8];
    int pulse_duration_ms;
    char wifi_ssid[32];
    char wifi_password[32];
    char wifi_mode[4];  // "ap" or "sta"
    uint32_t static_ip;
    uint32_t gateway;
    uint32_t subnet;
} system_config_t;

// System status structure
typedef struct {
    float cpu_temp;
    float cpu_freq_mhz;
    uint32_t free_heap_bytes;
    float main_voltage;
    uint32_t uptime_sec;
} system_stats_t;

// Error codes
typedef enum {
    ERR_NONE = 0,
    ERR_INVALID_RELAY,
    ERR_INVALID_STATE,
    ERR_INVALID_CONFIG,
    ERR_MEMORY,
    ERR_HARDWARE,
    ERR_NETWORK
} error_code_t;

// Initialize the relay controller with default or stored configuration
error_code_t relay_controller_init(void);

// Control a specific relay
error_code_t relay_set_state(uint8_t relay_idx, bool state);

// Start a timed pulse on a relay
error_code_t relay_pulse(uint8_t relay_idx, uint32_t duration_ms);

// Process any pending relay operations (for non-blocking pulses)
void relay_process(void);

// Get current relay states
bool relay_get_state(uint8_t relay_idx);
void relay_get_all_states(bool *states, uint8_t count);

// System status
error_code_t system_get_stats(system_stats_t *stats);

// Configuration management
error_code_t config_load(void);
error_code_t config_save(void);
error_code_t config_set_pulse_duration(int duration_ms);
error_code_t config_set_relay_pins(const int *pins, uint8_t count);
const system_config_t* config_get_current(void);

#endif // RELAY_CONTROLLER_H

