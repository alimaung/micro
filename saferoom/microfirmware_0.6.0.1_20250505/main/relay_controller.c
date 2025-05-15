// relay_controller.c
#include "relay_controller.h"
#include "hardware_hal.h"
#include "config_storage.h"
#include <string.h>

#define NUM_RELAYS 8
#define MAX_PULSE_TASKS 3

// Default configuration
static system_config_t system_config = {
    .relay_pins = {16, 17, 18, 19, 21, 22, 23, 5},
    .pulse_duration_ms = 500,
    .wifi_ssid = "4G-UFI-0E4",
    .wifi_password = "1234567890",
    .wifi_mode = "ap",
    .static_ip = 0xC0A80165,  // 192.168.1.101
    .gateway = 0xC0A80101,    // 192.168.1.1
    .subnet = 0xFFFFFF00      // 255.255.255.0
};

// Relay states
static bool relay_states[NUM_RELAYS] = {false};

// Pulse task structure
typedef struct {
    uint8_t relay_idx;
    uint32_t end_time;
    bool active;
} pulse_task_t;

static pulse_task_t pulse_tasks[MAX_PULSE_TASKS] = {0};
static uint32_t boot_time = 0;

error_code_t relay_controller_init(void) {
    error_code_t err;
    
    // Load configuration from NVS
    err = config_load();
    if (err != ERR_NONE) {
        // Use defaults if configuration loading fails
        config_save();
    }
    
    // Initialize hardware
    hardware_hal_init();
    boot_time = hal_get_millis();
    
    // Configure relay pins as outputs and initialize to OFF state
    for (int i = 0; i < NUM_RELAYS; i++) {
        hal_gpio_config_output(system_config.relay_pins[i]);
        hal_gpio_write(system_config.relay_pins[i], HAL_HIGH);  // Relays are active LOW
    }
    
    // Initialize ADC for voltage monitoring
    hal_adc_init(HAL_ADC_CHANNEL_6);
    
    return ERR_NONE;
}

error_code_t relay_set_state(uint8_t relay_idx, bool state) {
    if (relay_idx >= NUM_RELAYS) {
        return ERR_INVALID_RELAY;
    }
    
    // Relays are active LOW, so invert the logic
    hal_gpio_write(system_config.relay_pins[relay_idx], state ? HAL_LOW : HAL_HIGH);
    relay_states[relay_idx] = state;
    
    return ERR_NONE;
}

error_code_t relay_pulse(uint8_t relay_idx, uint32_t duration_ms) {
    if (relay_idx >= NUM_RELAYS) {
        return ERR_INVALID_RELAY;
    }
    
    // Find an available pulse task slot
    int slot = -1;
    for (int i = 0; i < MAX_PULSE_TASKS; i++) {
        if (!pulse_tasks[i].active) {
            slot = i;
            break;
        }
    }
    
    if (slot == -1) {
        return ERR_MEMORY; // No available slots
    }
    
    // Set relay ON
    relay_set_state(relay_idx, true);
    
    // Set up pulse task
    pulse_tasks[slot].relay_idx = relay_idx;
    pulse_tasks[slot].end_time = hal_get_millis() + duration_ms;
    pulse_tasks[slot].active = true;
    
    return ERR_NONE;
}

void relay_process(void) {
    uint32_t current_time = hal_get_millis();
    
    // Process active pulse tasks
    for (int i = 0; i < MAX_PULSE_TASKS; i++) {
        if (pulse_tasks[i].active && current_time >= pulse_tasks[i].end_time) {
            // Turn relay OFF when pulse duration expires
            relay_set_state(pulse_tasks[i].relay_idx, false);
            pulse_tasks[i].active = false;
        }
    }
}

bool relay_get_state(uint8_t relay_idx) {
    if (relay_idx >= NUM_RELAYS) {
        return false;
    }
    return relay_states[relay_idx];
}

void relay_get_all_states(bool *states, uint8_t count) {
    if (states == NULL || count > NUM_RELAYS) {
        return;
    }
    memcpy(states, relay_states, count * sizeof(bool));
}

error_code_t system_get_stats(system_stats_t *stats) {
    if (stats == NULL) {
        return ERR_INVALID_STATE;
    }
    
    stats->cpu_temp = hal_get_temperature();
    stats->cpu_freq_mhz = hal_get_cpu_frequency();
    stats->free_heap_bytes = hal_get_free_heap();
    
    // Sample voltage with averaging
    uint32_t voltage_sample = 0;
    for (int i = 0; i < 64; i++) {
        voltage_sample += hal_adc_read(HAL_ADC_CHANNEL_6);
    }
    stats->main_voltage = hal_adc_to_voltage(voltage_sample / 64);
    
    stats->uptime_sec = (hal_get_millis() - boot_time) / 1000;
    
    return ERR_NONE;
}

error_code_t config_load(void) {
    return storage_read("relaycfg", &system_config, sizeof(system_config_t));
}

error_code_t config_save(void) {
    return storage_write("relaycfg", &system_config, sizeof(system_config_t));
}

error_code_t config_set_pulse_duration(int duration_ms) {
    if (duration_ms <= 0 || duration_ms > 10000) {
        return ERR_INVALID_CONFIG;
    }
    
    system_config.pulse_duration_ms = duration_ms;
    return ERR_NONE;
}

error_code_t config_set_relay_pins(const int *pins, uint8_t count) {
    if (pins == NULL || count != NUM_RELAYS) {
        return ERR_INVALID_CONFIG;
    }
    
    // Validate pin numbers
    for (int i = 0; i < count; i++) {
        if (!hal_is_valid_gpio(pins[i])) {
            return ERR_INVALID_CONFIG;
        }
    }
    
    memcpy(system_config.relay_pins, pins, count * sizeof(int));
    
    // Reconfigure GPIO pins
    for (int i = 0; i < NUM_RELAYS; i++) {
        hal_gpio_config_output(system_config.relay_pins[i]);
        hal_gpio_write(system_config.relay_pins[i], relay_states[i] ? HAL_LOW : HAL_HIGH);
    }
    
    return ERR_NONE;
}

const system_config_t* config_get_current(void) {
    return &system_config;
}