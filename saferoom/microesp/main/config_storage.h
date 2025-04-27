// config_storage.h
#ifndef CONFIG_STORAGE_H
#define CONFIG_STORAGE_H

#include <stdint.h>
#include <stddef.h>
#include "relay_controller.h"

// Error codes for storage operations
error_code_t storage_read(const char* namespace, void* data, size_t size);
error_code_t storage_write(const char* namespace, const void* data, size_t size);
error_code_t storage_erase(const char* namespace);

#endif // CONFIG_STORAGE_H