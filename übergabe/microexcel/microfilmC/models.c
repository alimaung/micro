/**
 * @file models.c
 * @brief Implementation of data model functions for the microfilm system
 */

#include "microfilm.h"
#include <sys/stat.h>
#include <errno.h>
#include <stdarg.h>
#include <ctype.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir _mkdir
#else
#include <sys/stat.h>
#endif

// Project management functions

Project* project_create(void) {
    Project *project = calloc(1, sizeof(Project));
    if (!project) {
        return NULL;
    }
    
    // Initialize capacity for documents array
    project->documents_capacity = 10;
    project->documents = calloc(project->documents_capacity, sizeof(Document));
    if (!project->documents) {
        free(project);
        return NULL;
    }
    
    project->documents_count = 0;
    project->has_oversized = false;
    project->total_pages = 0;
    project->total_pages_with_refs = 0;
    project->total_oversized = 0;
    project->documents_with_oversized = 0;
    
    return project;
}

void project_destroy(Project *project) {
    if (!project) return;
    
    // Free documents array
    if (project->documents) {
        for (int i = 0; i < project->documents_count; i++) {
            document_destroy(&project->documents[i]);
        }
        free(project->documents);
    }
    
    // Free film allocation
    if (project->film_allocation) {
        film_allocation_destroy(project->film_allocation);
    }
    
    free(project);
}

const char* project_get_location_code(const Project *project) {
    if (!project) return "3";
    
    if (strcmp(project->location, "OU") == 0) {
        return "1";
    } else if (strcmp(project->location, "DW") == 0) {
        return "2";
    } else {
        return "3";
    }
}

// Document management functions

Document* document_create(const char *doc_id, const char *path) {
    Document *doc = calloc(1, sizeof(Document));
    if (!doc) return NULL;
    
    strncpy(doc->doc_id, doc_id, MAX_DOC_ID_LENGTH - 1);
    strncpy(doc->path, path, MAX_PATH_LENGTH - 1);
    
    doc->pages = 0;
    doc->has_oversized = false;
    doc->total_oversized = 0;
    doc->dimensions = NULL;
    doc->dimensions_count = 0;
    doc->ranges = NULL;
    doc->ranges_count = 0;
    doc->reference_pages = NULL;
    doc->reference_pages_count = 0;
    doc->total_references = 0;
    doc->is_split = false;
    doc->roll_count = 1;
    doc->com_id = -1;
    
    return doc;
}

void document_destroy(Document *document) {
    if (!document) return;
    
    if (document->dimensions) {
        free(document->dimensions);
    }
    if (document->ranges) {
        free(document->ranges);
    }
    if (document->reference_pages) {
        free(document->reference_pages);
    }
}

// Film allocation functions

FilmAllocation* film_allocation_create(const char *archive_id, const char *project_name) {
    FilmAllocation *allocation = calloc(1, sizeof(FilmAllocation));
    if (!allocation) return NULL;
    
    strncpy(allocation->archive_id, archive_id, MAX_ARCHIVE_ID_LENGTH - 1);
    strncpy(allocation->project_name, project_name, MAX_PATH_LENGTH - 1);
    
    // Initialize rolls arrays
    allocation->rolls_16mm_capacity = 10;
    allocation->rolls_16mm = calloc(allocation->rolls_16mm_capacity, sizeof(FilmRoll));
    if (!allocation->rolls_16mm) {
        free(allocation);
        return NULL;
    }
    
    allocation->rolls_35mm_capacity = 10;
    allocation->rolls_35mm = calloc(allocation->rolls_35mm_capacity, sizeof(FilmRoll));
    if (!allocation->rolls_35mm) {
        free(allocation->rolls_16mm);
        free(allocation);
        return NULL;
    }
    
    allocation->rolls_16mm_count = 0;
    allocation->rolls_35mm_count = 0;
    
    // Set version and creation date
    strcpy(allocation->version, "1.0");
    get_current_timestamp(allocation->creation_date, sizeof(allocation->creation_date));
    
    return allocation;
}

void film_allocation_destroy(FilmAllocation *film_allocation) {
    if (!film_allocation) return;
    
    // Free 16mm rolls
    if (film_allocation->rolls_16mm) {
        for (int i = 0; i < film_allocation->rolls_16mm_count; i++) {
            film_roll_destroy(&film_allocation->rolls_16mm[i]);
        }
        free(film_allocation->rolls_16mm);
    }
    
    // Free 35mm rolls
    if (film_allocation->rolls_35mm) {
        for (int i = 0; i < film_allocation->rolls_35mm_count; i++) {
            film_roll_destroy(&film_allocation->rolls_35mm[i]);
        }
        free(film_allocation->rolls_35mm);
    }
    
    free(film_allocation);
}

FilmRoll* film_roll_create(int roll_id, FilmType film_type, int capacity) {
    FilmRoll *roll = calloc(1, sizeof(FilmRoll));
    if (!roll) return NULL;
    
    roll->roll_id = roll_id;
    roll->film_type = film_type;
    roll->capacity = capacity;
    roll->pages_used = 0;
    roll->pages_remaining = capacity;
    
    // Initialize document segments array
    roll->segments_capacity = 50;
    roll->document_segments = calloc(roll->segments_capacity, sizeof(DocumentSegment));
    if (!roll->document_segments) {
        free(roll);
        return NULL;
    }
    roll->segments_count = 0;
    
    strcpy(roll->status, "active");
    roll->has_split_documents = false;
    roll->is_partial = false;
    roll->remaining_capacity = 0;
    roll->usable_capacity = 0;
    
    get_current_timestamp(roll->creation_date, sizeof(roll->creation_date));
    
    return roll;
}

void film_roll_destroy(FilmRoll *roll) {
    if (!roll) return;
    
    if (roll->document_segments) {
        free(roll->document_segments);
    }
}

MicrofilmError film_roll_add_document_segment(FilmRoll *roll, const char *doc_id, 
    const char *path, int pages, PageRange page_range, bool has_oversized) {
    
    MicrofilmError error = {false, ""};
    
    if (!roll) {
        error.has_error = true;
        strcpy(error.message, "Roll is NULL");
        return error;
    }
    
    // Check if we need to expand the segments array
    if (roll->segments_count >= roll->segments_capacity) {
        roll->segments_capacity *= 2;
        DocumentSegment *new_segments = realloc(roll->document_segments, 
            roll->segments_capacity * sizeof(DocumentSegment));
        if (!new_segments) {
            error.has_error = true;
            strcpy(error.message, "Failed to allocate memory for document segments");
            return error;
        }
        roll->document_segments = new_segments;
    }
    
    // Calculate document index and frame range
    int document_index = roll->segments_count + 1;
    int start_frame = roll->pages_used + 1;
    int end_frame = start_frame + pages - 1;
    
    // Create the segment
    DocumentSegment *segment = &roll->document_segments[roll->segments_count];
    strncpy(segment->doc_id, doc_id, MAX_DOC_ID_LENGTH - 1);
    strncpy(segment->path, path, MAX_PATH_LENGTH - 1);
    segment->pages = pages;
    segment->page_range = page_range;
    segment->frame_range.start = start_frame;
    segment->frame_range.end = end_frame;
    segment->document_index = document_index;
    segment->has_oversized = has_oversized;
    
    // Update roll statistics
    roll->pages_used += pages;
    roll->pages_remaining -= pages;
    roll->segments_count++;
    
    return error;
}

// Utility functions

void get_current_timestamp(char *buffer, size_t buffer_size) {
    time_t now;
    struct tm *timeinfo;
    
    time(&now);
    timeinfo = localtime(&now);
    
    strftime(buffer, buffer_size, "%Y-%m-%d %H:%M:%S", timeinfo);
}

bool file_exists(const char *path) {
    struct stat st;
    return (stat(path, &st) == 0 && S_ISREG(st.st_mode));
}

bool directory_exists(const char *path) {
    struct stat st;
    return (stat(path, &st) == 0 && S_ISDIR(st.st_mode));
}

MicrofilmError create_directory(const char *path) {
    MicrofilmError error = {false, ""};
    
#ifdef _WIN32
    if (_mkdir(path) != 0 && errno != EEXIST) {
#else
    if (mkdir(path, 0755) != 0 && errno != EEXIST) {
#endif
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH, 
            "Failed to create directory %s: %s", path, strerror(errno));
    }
    
    return error;
}

char* extract_archive_id(const char *folder_name) {
    // Pattern: RRDxxx-xxxx_Location_DocType
    // Extract RRDxxx-xxxx part
    
    if (!folder_name || strlen(folder_name) < 12) return NULL;
    
    // Look for RRD pattern
    if (strncmp(folder_name, "RRD", 3) != 0) return NULL;
    
    // Find the first underscore
    const char *underscore = strchr(folder_name, '_');
    if (!underscore) return NULL;
    
    // Calculate length of archive ID
    size_t id_length = underscore - folder_name;
    if (id_length >= MAX_ARCHIVE_ID_LENGTH) return NULL;
    
    char *archive_id = malloc(id_length + 1);
    if (!archive_id) return NULL;
    
    strncpy(archive_id, folder_name, id_length);
    archive_id[id_length] = '\0';
    
    return archive_id;
}

char* extract_location(const char *folder_name) {
    // Pattern: RRDxxx-xxxx_Location_DocType
    // Extract Location part
    
    const char *first_underscore = strchr(folder_name, '_');
    if (!first_underscore) return NULL;
    
    first_underscore++; // Move past the underscore
    
    const char *second_underscore = strchr(first_underscore, '_');
    size_t location_length;
    
    if (second_underscore) {
        location_length = second_underscore - first_underscore;
    } else {
        location_length = strlen(first_underscore);
    }
    
    if (location_length >= MAX_LOCATION_LENGTH) return NULL;
    
    char *location = malloc(location_length + 1);
    if (!location) return NULL;
    
    strncpy(location, first_underscore, location_length);
    location[location_length] = '\0';
    
    return location;
}

char* extract_doc_type(const char *folder_name) {
    // Pattern: RRDxxx-xxxx_Location_DocType
    // Extract DocType part
    
    const char *first_underscore = strchr(folder_name, '_');
    if (!first_underscore) return NULL;
    
    const char *second_underscore = strchr(first_underscore + 1, '_');
    if (!second_underscore) {
        // No doc type
        char *empty = malloc(1);
        if (empty) empty[0] = '\0';
        return empty;
    }
    
    second_underscore++; // Move past the underscore
    
    size_t doc_type_length = strlen(second_underscore);
    if (doc_type_length >= MAX_DOCTYPE_LENGTH) return NULL;
    
    char *doc_type = malloc(doc_type_length + 1);
    if (!doc_type) return NULL;
    
    strcpy(doc_type, second_underscore);
    
    return doc_type;
}

// Logger functions

Logger* logger_create(const char *log_file_path, bool console_output) {
    Logger *logger = calloc(1, sizeof(Logger));
    if (!logger) return NULL;
    
    logger->console_output = console_output;
    logger->log_level = LOG_INFO;
    
    if (log_file_path) {
        logger->log_file = fopen(log_file_path, "a");
        if (!logger->log_file) {
            if (console_output) {
                fprintf(stderr, "Warning: Could not open log file %s\n", log_file_path);
            }
        }
    }
    
    return logger;
}

void logger_destroy(Logger *logger) {
    if (!logger) return;
    
    if (logger->log_file) {
        fclose(logger->log_file);
    }
    
    free(logger);
}

void logger_log(Logger *logger, int level, const char *module, const char *format, ...) {
    if (!logger || level < logger->log_level) return;
    
    // Get current timestamp
    char timestamp[32];
    get_current_timestamp(timestamp, sizeof(timestamp));
    
    // Format the message
    va_list args;
    va_start(args, format);
    
    char message[1024];
    vsnprintf(message, sizeof(message), format, args);
    va_end(args);
    
    // Get level string and color
    const char *level_str;
    const char *color = COLOR_RESET;
    
    switch (level) {
        case LOG_DEBUG:
            level_str = "DEBUG";
            color = COLOR_CYAN;
            break;
        case LOG_INFO:
            level_str = "INFO";
            color = COLOR_WHITE;
            break;
        case LOG_SUCCESS:
            level_str = "SUCCESS";
            color = COLOR_GREEN;
            break;
        case LOG_WARNING:
            level_str = "WARNING";
            color = COLOR_YELLOW;
            break;
        case LOG_ERROR:
            level_str = "ERROR";
            color = COLOR_RED;
            break;
        case LOG_CRITICAL:
            level_str = "CRITICAL";
            color = COLOR_RED COLOR_BOLD;
            break;
        default:
            level_str = "UNKNOWN";
            color = COLOR_RESET;
    }
    
    // Log to console
    if (logger->console_output) {
        printf("%s%s - [%s] [%s] %s%s\n", 
            color, timestamp, module, level_str, message, COLOR_RESET);
    }
    
    // Log to file
    if (logger->log_file) {
        fprintf(logger->log_file, "%s - [%s] [%s] %s\n", 
            timestamp, module, level_str, message);
        fflush(logger->log_file);
    }
}

void logger_section(Logger *logger, const char *title) {
    if (!logger) return;
    
    char line[100];
    memset(line, '=', sizeof(line) - 1);
    line[sizeof(line) - 1] = '\0';
    
    if (logger->console_output) {
        printf("\n%s%s%s\n%s%s%s\n%s\n", 
            COLOR_BLUE COLOR_BOLD, line, COLOR_RESET,
            COLOR_BLUE COLOR_BOLD, title, COLOR_RESET,
            line);
    }
    
    if (logger->log_file) {
        fprintf(logger->log_file, "\n%s\n%s\n%s\n", line, title, line);
        fflush(logger->log_file);
    }
}
