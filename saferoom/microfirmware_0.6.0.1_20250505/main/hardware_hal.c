#include "hardware_hal.h"
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_chip_info.h"  // For CPU frequency info
#include "esp_log.h"

static adc_oneshot_unit_handle_t adc1_handle;
static adc_cali_handle_t adc_cali_handle;

void hardware_hal_init(void) {
    // Initialize ADC with new API - handle errors gracefully
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1,
    };
    
    // Try to initialize ADC1, but don't crash if it fails
    esp_err_t err = adc_oneshot_new_unit(&init_config, &adc1_handle);
    if (err != ESP_OK) {
        // Log the error but continue
        ESP_LOGW("HAL", "Could not initialize ADC1, it may already be in use: %d", err);
        // Set handle to NULL to indicate it's not available
        adc1_handle = NULL;
    } else {
        // Only configure calibration if ADC initialization was successful
        adc_cali_line_fitting_config_t cali_config = {
            .unit_id = ADC_UNIT_1,
            .atten = ADC_ATTEN_DB_12,
            .bitwidth = ADC_BITWIDTH_12,
        };
        err = adc_cali_create_scheme_line_fitting(&cali_config, &adc_cali_handle);
        if (err != ESP_OK) {
            ESP_LOGW("HAL", "ADC calibration failed: %d", err);
            // Set calibration handle to NULL
            adc_cali_handle = NULL;
        }
    }
}

void hal_gpio_config_output(int pin) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

void hal_gpio_write(int pin, int level) {
    gpio_set_level(pin, level);
}

int hal_gpio_read(int pin) {
    return gpio_get_level(pin);
}

bool hal_is_valid_gpio(int pin) {
    return (pin >= 0 && pin < GPIO_NUM_MAX);
}

uint32_t hal_get_millis(void) {
    return (uint32_t)(esp_timer_get_time() / 1000);
}

void hal_delay_ms(uint32_t ms) {
    vTaskDelay(ms / portTICK_PERIOD_MS);
}

void hal_adc_init(hal_adc_channel_t channel) {
    // Convert HAL channel to ESP-IDF channel
    adc_channel_t esp_channel;
    
    switch(channel) {
        case HAL_ADC_CHANNEL_6:
            esp_channel = ADC_CHANNEL_6;
            break;
        // Add other channel mappings as needed
        default:
            return;
    }
    
    // Configure ADC channel with new API
    adc_oneshot_chan_cfg_t config = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, esp_channel, &config));
}

uint32_t hal_adc_read(hal_adc_channel_t channel) {
    // Check if ADC was initialized
    if (adc1_handle == NULL) {
        return 0; // Return 0 if ADC is not available
    }
    
    // Convert HAL channel to ESP-IDF channel
    adc_channel_t esp_channel;
    
    switch(channel) {
        case HAL_ADC_CHANNEL_6:
            esp_channel = ADC_CHANNEL_6;
            break;
        // Add other channel mappings as needed
        default:
            return 0;
    }
    
    // Read ADC with new API
    int adc_raw;
    esp_err_t err = adc_oneshot_read(adc1_handle, esp_channel, &adc_raw);
    if (err != ESP_OK) {
        ESP_LOGW("HAL", "ADC read failed: %d", err);
        return 0;
    }
    return adc_raw;
}

float hal_adc_to_voltage(uint32_t adc_value) {
    // If either ADC or calibration failed to initialize, return 0
    if (adc1_handle == NULL || adc_cali_handle == NULL) {
        return 0.0f;
    }
    
    // Convert ADC to voltage with new API
    int voltage_mv;
    esp_err_t err = adc_cali_raw_to_voltage(adc_cali_handle, adc_value, &voltage_mv);
    if (err != ESP_OK) {
        ESP_LOGW("HAL", "ADC calibration failed: %d", err);
        return 0.0f;
    }
    return voltage_mv / 1000.0f;
}

float hal_get_temperature(void) {
    // ESP32 temperature sensor API changed in ESP-IDF v5
    // Use a fixed placeholder value for now - replace with actual implementation
    // based on your ESP-IDF version
    return 50.0f;  // Placeholder value (50°C)
    
    // For ESP-IDF v5, you would need to use the temp_sensor APIs:
    // #include "driver/temperature_sensor.h"
    // temperature_sensor_handle_t temp_sensor = NULL;
    // float tsens_value;
    // temperature_sensor_get_celsius(temp_sensor, &tsens_value);
    // return tsens_value;
}

float hal_get_cpu_frequency(void) {
    // ESP-IDF v5.x uses rtc_cpu_freq_get_config to get CPU frequency
    // Use a simpler approach with esp_system.h
    return (float)CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ;  // Get from build configuration
}

uint32_t hal_get_free_heap(void) {
    return esp_get_free_heap_size();
}