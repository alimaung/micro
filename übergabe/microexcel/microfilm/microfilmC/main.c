/**
 * @file main.c
 * @brief Main entry point for the microfilm processing system
 */

#include "microfilm.h"
#include <getopt.h>

static void print_usage(const char *program_name);
static MicrofilmError parse_arguments(int argc, char *argv[], char *path, bool *debug);
static MicrofilmError process_project(const char *path, bool debug);
static void print_project_details(const Project *project, Logger *logger);

int main(int argc, char *argv[]) {
    char path[MAX_PATH_LENGTH] = {0};
    bool debug = false;
    
    // Parse command line arguments
    MicrofilmError parse_error = parse_arguments(argc, argv, path, &debug);
    if (parse_error.has_error) {
        fprintf(stderr, "Error: %s\n", parse_error.message);
        print_usage(argv[0]);
        return 1;
    }
    
    // Get path from user input if not provided
    if (strlen(path) == 0) {
        printf("Enter path to project or document folder: ");
        if (fgets(path, sizeof(path), stdin) == NULL) {
            fprintf(stderr, "Error reading input\n");
            return 1;
        }
        
        // Remove newline character
        size_t len = strlen(path);
        if (len > 0 && path[len - 1] == '\n') {
            path[len - 1] = '\0';
        }
    }
    
    // Process the project
    MicrofilmError error = process_project(path, debug);
    if (error.has_error) {
        fprintf(stderr, "Error: %s\n", error.message);
        return 1;
    }
    
    return 0;
}

static void print_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] [PATH]\n", program_name);
    printf("\nMicrofilm Processing System\n");
    printf("\nArguments:\n");
    printf("  PATH                    Path to project folder or document subfolder\n");
    printf("\nOptions:\n");
    printf("  -d, --debug            Show debug information\n");
    printf("  -h, --help             Show this help message\n");
    printf("\nExamples:\n");
    printf("  %s /path/to/project\n", program_name);
    printf("  %s --debug /path/to/project\n", program_name);
}

static MicrofilmError parse_arguments(int argc, char *argv[], char *path, bool *debug) {
    MicrofilmError error = {false, ""};
    
    static struct option long_options[] = {
        {"debug", no_argument, 0, 'd'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    int option_index = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "dh", long_options, &option_index)) != -1) {
        switch (c) {
            case 'd':
                *debug = true;
                break;
            case 'h':
                print_usage(argv[0]);
                exit(0);
                break;
            case '?':
                error.has_error = true;
                strcpy(error.message, "Invalid option");
                return error;
            default:
                error.has_error = true;
                strcpy(error.message, "Unknown error in argument parsing");
                return error;
        }
    }
    
    // Get path from remaining arguments
    if (optind < argc) {
        strncpy(path, argv[optind], MAX_PATH_LENGTH - 1);
    }
    
    return error;
}

static MicrofilmError process_project(const char *path, bool debug) {
    MicrofilmError error = {false, ""};
    
    // Initialize logger
    Logger *logger = logger_create(NULL, true);
    if (!logger) {
        error.has_error = true;
        strcpy(error.message, "Failed to create logger");
        return error;
    }
    
    if (debug) {
        logger->log_level = LOG_DEBUG;
    }
    
    logger_log(logger, LOG_INFO, "MAIN", "Starting microfilm processing system");
    
    // Create project
    Project *project = project_create();
    if (!project) {
        error.has_error = true;
        strcpy(error.message, "Failed to create project");
        logger_destroy(logger);
        return error;
    }
    
    // Initialize project
    error = project_initialize(project, path, logger);
    if (error.has_error) {
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Configure logger to save logs in project directory
    char log_file_path[MAX_PATH_LENGTH];
    snprintf(log_file_path, MAX_PATH_LENGTH, "%s/.logs/%s.log", 
        project->project_path, project->archive_id);
    
    // Create logs directory
    char logs_dir[MAX_PATH_LENGTH];
    snprintf(logs_dir, MAX_PATH_LENGTH, "%s/.logs", project->project_path);
    create_directory(logs_dir);
    
    // Recreate logger with file output
    logger_destroy(logger);
    logger = logger_create(log_file_path, true);
    if (!logger) {
        error.has_error = true;
        strcpy(error.message, "Failed to create logger with file output");
        project_destroy(project);
        return error;
    }
    
    if (debug) {
        logger->log_level = LOG_DEBUG;
    }
    
    logger_log(logger, LOG_INFO, "MAIN", "Logs will be saved to: %s", log_file_path);
    
    // Process documents to identify oversized pages
    error = document_process_all(project, logger);
    if (error.has_error) {
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Branch workflow based on whether the project has oversized pages
    if (project->has_oversized) {
        logger_log(logger, LOG_INFO, "MAIN", "Project has oversized pages, following oversized workflow");
        
        // Calculate reference pages for oversized documents
        error = document_calculate_references(project, logger);
        if (error.has_error) {
            project_destroy(project);
            logger_destroy(logger);
            return error;
        }
    } else {
        logger_log(logger, LOG_INFO, "MAIN", "Project has no oversized pages, following standard workflow");
    }
    
    // Allocate documents to film rolls
    error = film_allocate(project, logger);
    if (error.has_error) {
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Initialize database
    char db_path[MAX_PATH_LENGTH];
    strcpy(db_path, "film_allocation.sqlite3");
    
    error = database_init(db_path);
    if (error.has_error) {
        logger_log(logger, LOG_ERROR, "MAIN", "Failed to initialize database: %s", error.message);
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Allocate film numbers
    error = database_allocate_film_numbers(project, db_path, logger);
    if (error.has_error) {
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Save project to database
    error = database_save_project(project, db_path);
    if (error.has_error) {
        logger_log(logger, LOG_ERROR, "MAIN", "Failed to save project to database: %s", error.message);
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    // Export results
    error = export_results(project, NULL, logger);
    if (error.has_error) {
        logger_log(logger, LOG_ERROR, "MAIN", "Failed to export results: %s", error.message);
        project_destroy(project);
        logger_destroy(logger);
        return error;
    }
    
    printf("Project Path: %s\n", project->project_path);
    
    // Display project information if requested
    if (debug) {
        print_project_details(project, logger);
    }
    
    logger_log(logger, LOG_SUCCESS, "MAIN", "Project processed successfully");
    
    project_destroy(project);
    logger_destroy(logger);
    
    return error;
}

static void print_project_details(const Project *project, Logger *logger) {
    logger_log(logger, LOG_DEBUG, "MAIN", "Project Details:");
    logger_log(logger, LOG_DEBUG, "MAIN", "Archive ID: %s", project->archive_id);
    logger_log(logger, LOG_DEBUG, "MAIN", "Location: %s (code: %s)", 
        project->location, project_get_location_code(project));
    logger_log(logger, LOG_DEBUG, "MAIN", "Document Type: %s", project->doc_type);
    logger_log(logger, LOG_DEBUG, "MAIN", "Project Path: %s", project->project_path);
    
    if (strlen(project->document_folder_path) > 0) {
        logger_log(logger, LOG_DEBUG, "MAIN", "Document Folder: %s", project->document_folder_path);
    } else {
        logger_log(logger, LOG_DEBUG, "MAIN", "Document Folder: Not found (using project folder)");
    }
    
    if (strlen(project->comlist_path) > 0) {
        logger_log(logger, LOG_DEBUG, "MAIN", "COM List File: %s", project->comlist_path);
    } else {
        logger_log(logger, LOG_DEBUG, "MAIN", "COM List File: Not found");
    }
    
    // Document and page statistics
    logger_log(logger, LOG_DEBUG, "MAIN", "Has Oversized Pages: %s", 
        project->has_oversized ? "true" : "false");
    logger_log(logger, LOG_DEBUG, "MAIN", "Total Documents: %d", project->documents_count);
    logger_log(logger, LOG_DEBUG, "MAIN", "Total Pages: %d", project->total_pages);
    logger_log(logger, LOG_DEBUG, "MAIN", "Total Pages with References: %d", project->total_pages_with_refs);
    logger_log(logger, LOG_DEBUG, "MAIN", "Total Oversized Pages: %d", project->total_oversized);
    logger_log(logger, LOG_DEBUG, "MAIN", "Documents with Oversized Pages: %d", project->documents_with_oversized);
    
    // Show details of oversized documents if any
    if (project->has_oversized && project->documents_with_oversized > 0) {
        logger_log(logger, LOG_DEBUG, "MAIN", "Oversized Documents:");
        for (int i = 0; i < project->documents_count; i++) {
            const Document *doc = &project->documents[i];
            if (doc->has_oversized) {
                logger_log(logger, LOG_DEBUG, "MAIN", "  - %s: %d oversized pages, %d reference sheets",
                    doc->doc_id, doc->total_oversized, doc->total_references);
            }
        }
    }
    
    // Show film allocation details if available
    if (project->film_allocation) {
        logger_log(logger, LOG_DEBUG, "MAIN", "Film Allocation:");
        logger_log(logger, LOG_DEBUG, "MAIN", "  16mm Rolls: %d", project->film_allocation->total_rolls_16mm);
        logger_log(logger, LOG_DEBUG, "MAIN", "  16mm Pages: %d", project->film_allocation->total_pages_16mm);
        
        if (project->has_oversized) {
            logger_log(logger, LOG_DEBUG, "MAIN", "  35mm Rolls: %d", project->film_allocation->total_rolls_35mm);
            logger_log(logger, LOG_DEBUG, "MAIN", "  35mm Pages: %d", project->film_allocation->total_pages_35mm);
        }
    }
}
