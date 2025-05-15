// hardware_hal.h
#ifndef HARDWARE_HAL_H
#define HARDWARE_HAL_H

#include <stdint.h>
#include <stdbool.h>

#define HAL_HIGH 1
#define HAL_LOW 0

typedef enum {
    HAL_ADC_CHANNEL_0 = 0,
    HAL_ADC_CHANNEL_1,
    HAL_ADC_CHANNEL_2,
    HAL_ADC_CHANNEL_3,
    HAL_ADC_CHANNEL_4,
    HAL_ADC_CHANNEL_5,
    HAL_ADC_CHANNEL_6,  // Voltage monitoring pin
    HAL_ADC_CHANNEL_7
} hal_adc_channel_t;

// Initialize hardware abstraction layer
void hardware_hal_init(void);

// GPIO functions
void hal_gpio_config_output(int pin);
void hal_gpio_write(int pin, int level);
int hal_gpio_read(int pin);
bool hal_is_valid_gpio(int pin);

// Time functions
uint32_t hal_get_millis(void);
void hal_delay_ms(uint32_t ms);

// ADC functions
void hal_adc_init(hal_adc_channel_t channel);
uint32_t hal_adc_read(hal_adc_channel_t channel);
float hal_adc_to_voltage(uint32_t adc_value);

// System functions
float hal_get_temperature(void);
float hal_get_cpu_frequency(void);
uint32_t hal_get_free_heap(void);

#endif // HARDWARE_HAL_H