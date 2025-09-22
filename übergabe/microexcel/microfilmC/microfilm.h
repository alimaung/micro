/**
 * @file microfilm.h
 * @brief Main header file for the microfilm processing system
 * 
 * This file contains the main structures and function declarations for the
 * microfilm processing system, including document processing, film allocation,
 * and data management.
 */

#ifndef MICROFILM_H
#define MICROFILM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <sqlite3.h>

// Maximum string lengths
#define MAX_PATH_LENGTH 1024
#define MAX_DOC_ID_LENGTH 256
#define MAX_ARCHIVE_ID_LENGTH 32
#define MAX_LOCATION_LENGTH 8
#define MAX_DOCTYPE_LENGTH 64
#define MAX_FILM_NUMBER_LENGTH 32
#define MAX_ERROR_MESSAGE_LENGTH 1024

// Film type enumeration
typedef enum {
    FILM_16MM,
    FILM_35MM
} FilmType;

// Film capacity constants
#define CAPACITY_16MM 2900
#define CAPACITY_35MM 690
#define PADDING_16MM 150
#define PADDING_35MM 150

// Oversized page detection thresholds
#define OVERSIZE_THRESHOLD_WIDTH 842.0
#define OVERSIZE_THRESHOLD_HEIGHT 1191.0

// Page range structure
typedef struct {
    int start;
    int end;
} PageRange;

// Document dimension structure
typedef struct {
    double width;
    double height;
    int page_index;
    double percent_over;
} PageDimension;

// Document segment structure
typedef struct {
    char doc_id[MAX_DOC_ID_LENGTH];
    char path[MAX_PATH_LENGTH];
    int pages;
    PageRange page_range;
    PageRange frame_range;
    int document_index;
    bool has_oversized;
} DocumentSegment;

// Document structure
typedef struct {
    char doc_id[MAX_DOC_ID_LENGTH];
    char path[MAX_PATH_LENGTH];
    int pages;
    bool has_oversized;
    int total_oversized;
    PageDimension *dimensions;
    int dimensions_count;
    PageRange *ranges;
    int ranges_count;
    int *reference_pages;
    int reference_pages_count;
    int total_references;
    bool is_split;
    int roll_count;
    int com_id;
} Document;

// Film roll structure
typedef struct {
    int roll_id;
    FilmType film_type;
    int capacity;
    int pages_used;
    int pages_remaining;
    DocumentSegment *document_segments;
    int segments_count;
    int segments_capacity;
    char film_number[MAX_FILM_NUMBER_LENGTH];
    char status[32];
    bool has_split_documents;
    bool is_partial;
    int remaining_capacity;
    int usable_capacity;
    char creation_date[32];
} FilmRoll;

// Film allocation structure
typedef struct {
    char archive_id[MAX_ARCHIVE_ID_LENGTH];
    char project_name[MAX_PATH_LENGTH];
    FilmRoll *rolls_16mm;
    int rolls_16mm_count;
    int rolls_16mm_capacity;
    FilmRoll *rolls_35mm;
    int rolls_35mm_count;
    int rolls_35mm_capacity;
    int total_rolls_16mm;
    int total_pages_16mm;
    int total_partial_rolls_16mm;
    int total_split_documents_16mm;
    int total_rolls_35mm;
    int total_pages_35mm;
    int total_partial_rolls_35mm;
    int total_split_documents_35mm;
    char creation_date[32];
    char version[16];
} FilmAllocation;

// Project structure
typedef struct {
    char archive_id[MAX_ARCHIVE_ID_LENGTH];
    char location[MAX_LOCATION_LENGTH];
    char project_path[MAX_PATH_LENGTH];
    char project_folder_name[MAX_PATH_LENGTH];
    char document_folder_path[MAX_PATH_LENGTH];
    char document_folder_name[MAX_PATH_LENGTH];
    char doc_type[MAX_DOCTYPE_LENGTH];
    bool has_oversized;
    int total_pages;
    int total_pages_with_refs;
    int total_oversized;
    int documents_with_oversized;
    char output_dir[MAX_PATH_LENGTH];
    char comlist_path[MAX_PATH_LENGTH];
    Document *documents;
    int documents_count;
    int documents_capacity;
    FilmAllocation *film_allocation;
} Project;

// Error handling structure
typedef struct {
    bool has_error;
    char message[MAX_ERROR_MESSAGE_LENGTH];
} MicrofilmError;

// Logger structure
typedef struct {
    FILE *log_file;
    bool console_output;
    int log_level;
} Logger;

// Function declarations

// Project management functions
Project* project_create(void);
void project_destroy(Project *project);
MicrofilmError project_initialize(Project *project, const char *path, Logger *logger);
const char* project_get_location_code(const Project *project);

// Document processing functions
MicrofilmError document_process_all(Project *project, Logger *logger);
MicrofilmError document_calculate_references(Project *project, Logger *logger);
Document* document_create(const char *doc_id, const char *path);
void document_destroy(Document *document);

// Film allocation functions
FilmAllocation* film_allocation_create(const char *archive_id, const char *project_name);
void film_allocation_destroy(FilmAllocation *film_allocation);
MicrofilmError film_allocate(Project *project, Logger *logger);
FilmRoll* film_roll_create(int roll_id, FilmType film_type, int capacity);
void film_roll_destroy(FilmRoll *roll);
MicrofilmError film_roll_add_document_segment(FilmRoll *roll, const char *doc_id, 
    const char *path, int pages, PageRange page_range, bool has_oversized);

// Database operations
MicrofilmError database_init(const char *db_path);
MicrofilmError database_save_project(const Project *project, const char *db_path);
MicrofilmError database_allocate_film_numbers(Project *project, const char *db_path, Logger *logger);

// Export functions
MicrofilmError export_results(const Project *project, const char *output_dir, Logger *logger);

// Utility functions
void get_current_timestamp(char *buffer, size_t buffer_size);
bool file_exists(const char *path);
bool directory_exists(const char *path);
MicrofilmError create_directory(const char *path);
char* extract_archive_id(const char *folder_name);
char* extract_location(const char *folder_name);
char* extract_doc_type(const char *folder_name);

// Logger functions
Logger* logger_create(const char *log_file_path, bool console_output);
void logger_destroy(Logger *logger);
void logger_log(Logger *logger, int level, const char *module, const char *format, ...);
void logger_section(Logger *logger, const char *title);

// Log levels
#define LOG_DEBUG 0
#define LOG_INFO 1
#define LOG_SUCCESS 2
#define LOG_WARNING 3
#define LOG_ERROR 4
#define LOG_CRITICAL 5

// Color codes for console output
#define COLOR_RESET "\033[0m"
#define COLOR_BOLD "\033[1m"
#define COLOR_RED "\033[31m"
#define COLOR_GREEN "\033[32m"
#define COLOR_YELLOW "\033[33m"
#define COLOR_BLUE "\033[34m"
#define COLOR_MAGENTA "\033[35m"
#define COLOR_CYAN "\033[36m"
#define COLOR_WHITE "\033[37m"

#endif // MICROFILM_H
