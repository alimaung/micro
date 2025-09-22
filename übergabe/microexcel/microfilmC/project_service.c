/**
 * @file project_service.c
 * @brief Implementation of project management functions
 */

#include "microfilm.h"
#include <dirent.h>
#include <libgen.h>

static bool validate_path(const char *path, MicrofilmError *error);
static bool try_extract_metadata(const char *folder_name, char *archive_id, 
    char *location, char *doc_type);
static bool find_document_folder(const char *project_path, const char *archive_id, 
    char *doc_folder_path);
static bool find_comlist_file(const char *folder_path, const char *archive_id, 
    char *comlist_path);

MicrofilmError project_initialize(Project *project, const char *path, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project || !path) {
        error.has_error = true;
        strcpy(error.message, "Invalid parameters");
        return error;
    }
    
    logger_section(logger, "Initializing Project");
    logger_log(logger, LOG_INFO, "PROJECT", "Processing path: %s", path);
    
    // Validate the path
    if (!validate_path(path, &error)) {
        return error;
    }
    
    // Copy the path and extract folder name
    strncpy(project->project_path, path, MAX_PATH_LENGTH - 1);
    
    // Extract folder name from path
    char *path_copy = strdup(path);
    char *folder_name = basename(path_copy);
    strncpy(project->project_folder_name, folder_name, MAX_PATH_LENGTH - 1);
    
    logger_log(logger, LOG_INFO, "PROJECT", "Folder name: %s", folder_name);
    
    // Try to extract metadata from folder name
    char archive_id[MAX_ARCHIVE_ID_LENGTH] = {0};
    char location[MAX_LOCATION_LENGTH] = {0};
    char doc_type[MAX_DOCTYPE_LENGTH] = {0};
    
    bool metadata_found = try_extract_metadata(folder_name, archive_id, location, doc_type);
    
    if (metadata_found) {
        // This is likely a project folder
        logger_log(logger, LOG_INFO, "PROJECT", "Path appears to be a project folder");
        
        strcpy(project->archive_id, archive_id);
        strcpy(project->location, location);
        strcpy(project->doc_type, doc_type);
        
        // Find document subfolder
        if (find_document_folder(path, archive_id, project->document_folder_path)) {
            char *doc_folder_name = basename(project->document_folder_path);
            strcpy(project->document_folder_name, doc_folder_name);
            logger_log(logger, LOG_INFO, "PROJECT", "Found document folder: %s", doc_folder_name);
        } else {
            logger_log(logger, LOG_WARNING, "PROJECT", "No document subfolder found");
        }
    } else {
        // Check if this might be a document subfolder
        char parent_path[MAX_PATH_LENGTH];
        strcpy(parent_path, path);
        char *parent_dir = dirname(parent_path);
        char *parent_name = basename(parent_dir);
        
        if (try_extract_metadata(parent_name, archive_id, location, doc_type)) {
            // This is a document subfolder
            logger_log(logger, LOG_INFO, "PROJECT", "Path appears to be a document subfolder");
            
            strcpy(project->archive_id, archive_id);
            strcpy(project->location, location);
            strcpy(project->doc_type, doc_type);
            strcpy(project->project_path, parent_dir);
            strcpy(project->project_folder_name, parent_name);
            strcpy(project->document_folder_path, path);
            strcpy(project->document_folder_name, folder_name);
        } else {
            error.has_error = true;
            snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
                "Could not extract project metadata from folder name: %s or parent: %s",
                folder_name, parent_name);
            free(path_copy);
            return error;
        }
    }
    
    free(path_copy);
    
    // Find COM list file
    if (find_comlist_file(project->project_path, project->archive_id, project->comlist_path)) {
        logger_log(logger, LOG_INFO, "PROJECT", "Found COM list file: %s", 
            basename(project->comlist_path));
    }
    
    logger_log(logger, LOG_INFO, "PROJECT", "Project initialized: %s (%s)", 
        project->archive_id, project->location);
    
    return error;
}

static bool validate_path(const char *path, MicrofilmError *error) {
    if (!directory_exists(path)) {
        error->has_error = true;
        snprintf(error->message, MAX_ERROR_MESSAGE_LENGTH,
            "Path does not exist or is not a directory: %s", path);
        return false;
    }
    return true;
}

static bool try_extract_metadata(const char *folder_name, char *archive_id, 
    char *location, char *doc_type) {
    
    // Pattern: RRDxxx-xxxx_Location_DocType
    
    if (!folder_name || strlen(folder_name) < 12) {
        return false;
    }
    
    // Check if it starts with RRD
    if (strncmp(folder_name, "RRD", 3) != 0) {
        return false;
    }
    
    // Find first underscore
    const char *first_underscore = strchr(folder_name, '_');
    if (!first_underscore) {
        return false;
    }
    
    // Extract archive ID
    size_t archive_id_len = first_underscore - folder_name;
    if (archive_id_len >= MAX_ARCHIVE_ID_LENGTH) {
        return false;
    }
    strncpy(archive_id, folder_name, archive_id_len);
    archive_id[archive_id_len] = '\0';
    
    // Extract location
    const char *location_start = first_underscore + 1;
    const char *second_underscore = strchr(location_start, '_');
    
    size_t location_len;
    if (second_underscore) {
        location_len = second_underscore - location_start;
    } else {
        location_len = strlen(location_start);
    }
    
    if (location_len >= MAX_LOCATION_LENGTH) {
        return false;
    }
    strncpy(location, location_start, location_len);
    location[location_len] = '\0';
    
    // Extract doc type if available
    if (second_underscore) {
        const char *doc_type_start = second_underscore + 1;
        size_t doc_type_len = strlen(doc_type_start);
        if (doc_type_len < MAX_DOCTYPE_LENGTH) {
            strcpy(doc_type, doc_type_start);
        }
    }
    
    return true;
}

static bool find_document_folder(const char *project_path, const char *archive_id, 
    char *doc_folder_path) {
    
    DIR *dir = opendir(project_path);
    if (!dir) return false;
    
    struct dirent *entry;
    char full_path[MAX_PATH_LENGTH];
    bool found = false;
    
    // Strategy 1: Look for folder with "PDFs zu" in the name
    rewinddir(dir);
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_DIR && strcmp(entry->d_name, ".") != 0 && 
            strcmp(entry->d_name, "..") != 0) {
            
            if (strstr(entry->d_name, "PDFs zu") != NULL) {
                snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", project_path, entry->d_name);
                strcpy(doc_folder_path, full_path);
                found = true;
                break;
            }
        }
    }
    
    // Strategy 2: Look for folder containing the archive ID
    if (!found) {
        rewinddir(dir);
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_type == DT_DIR && strcmp(entry->d_name, ".") != 0 && 
                strcmp(entry->d_name, "..") != 0) {
                
                if (strstr(entry->d_name, archive_id) != NULL) {
                    snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", project_path, entry->d_name);
                    strcpy(doc_folder_path, full_path);
                    found = true;
                    break;
                }
            }
        }
    }
    
    // Strategy 3: Look for folder containing PDF files
    if (!found) {
        rewinddir(dir);
        int max_pdfs = 0;
        char best_folder[MAX_PATH_LENGTH] = {0};
        
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_type == DT_DIR && strcmp(entry->d_name, ".") != 0 && 
                strcmp(entry->d_name, "..") != 0) {
                
                snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", project_path, entry->d_name);
                
                // Count PDF files in this directory
                DIR *subdir = opendir(full_path);
                if (subdir) {
                    struct dirent *subentry;
                    int pdf_count = 0;
                    
                    while ((subentry = readdir(subdir)) != NULL) {
                        if (subentry->d_type == DT_REG) {
                            const char *ext = strrchr(subentry->d_name, '.');
                            if (ext && (strcasecmp(ext, ".pdf") == 0)) {
                                pdf_count++;
                            }
                        }
                    }
                    closedir(subdir);
                    
                    if (pdf_count > max_pdfs) {
                        max_pdfs = pdf_count;
                        strcpy(best_folder, full_path);
                    }
                }
            }
        }
        
        if (max_pdfs > 0) {
            strcpy(doc_folder_path, best_folder);
            found = true;
        }
    }
    
    closedir(dir);
    return found;
}

static bool find_comlist_file(const char *folder_path, const char *archive_id, 
    char *comlist_path) {
    
    DIR *dir = opendir(folder_path);
    if (!dir) return false;
    
    struct dirent *entry;
    char full_path[MAX_PATH_LENGTH];
    bool found = false;
    
    // Look for Excel files containing the archive ID
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            const char *ext = strrchr(entry->d_name, '.');
            if (ext && (strcasecmp(ext, ".xls") == 0 || strcasecmp(ext, ".xlsx") == 0)) {
                // Check if filename contains archive ID
                if (strstr(entry->d_name, archive_id) != NULL) {
                    snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", folder_path, entry->d_name);
                    strcpy(comlist_path, full_path);
                    found = true;
                    break;
                }
            }
        }
    }
    
    // If no specific match, look for any Excel file
    if (!found) {
        rewinddir(dir);
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_type == DT_REG) {
                const char *ext = strrchr(entry->d_name, '.');
                if (ext && (strcasecmp(ext, ".xls") == 0 || strcasecmp(ext, ".xlsx") == 0)) {
                    snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", folder_path, entry->d_name);
                    strcpy(comlist_path, full_path);
                    found = true;
                    break;
                }
            }
        }
    }
    
    closedir(dir);
    return found;
}

