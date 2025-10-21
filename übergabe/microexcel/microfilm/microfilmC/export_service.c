/**
 * @file export_service.c
 * @brief Implementation of export functions for the microfilm system
 */

#include "microfilm.h"

static MicrofilmError export_project_info(const Project *project, const char *output_dir);
static MicrofilmError export_documents_info(const Project *project, const char *output_dir);
static MicrofilmError export_film_allocation(const Project *project, const char *output_dir);
static MicrofilmError create_data_directory(const char *project_path, char *data_dir_path);
static void write_json_string(FILE *file, const char *key, const char *value, bool is_last);
static void write_json_int(FILE *file, const char *key, int value, bool is_last);
static void write_json_bool(FILE *file, const char *key, bool value, bool is_last);

MicrofilmError export_results(const Project *project, const char *output_dir, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project) {
        error.has_error = true;
        strcpy(error.message, "Project is NULL");
        return error;
    }
    
    logger_section(logger, "Exporting Results");
    logger_log(logger, LOG_INFO, "EXPORT", "Starting export of project results");
    
    // Create data directory
    char data_dir[MAX_PATH_LENGTH];
    error = create_data_directory(project->project_path, data_dir);
    if (error.has_error) {
        return error;
    }
    
    logger_log(logger, LOG_INFO, "EXPORT", "Creating data directory at %s", data_dir);
    
    // Export project information
    error = export_project_info(project, data_dir);
    if (error.has_error) {
        logger_log(logger, LOG_ERROR, "EXPORT", "Failed to export project info: %s", error.message);
        return error;
    }
    
    logger_log(logger, LOG_INFO, "EXPORT", "Exported project info");
    
    // Export documents information
    error = export_documents_info(project, data_dir);
    if (error.has_error) {
        logger_log(logger, LOG_ERROR, "EXPORT", "Failed to export documents info: %s", error.message);
        return error;
    }
    
    logger_log(logger, LOG_INFO, "EXPORT", "Exported documents info");
    
    // Export film allocation if available
    if (project->film_allocation) {
        error = export_film_allocation(project, data_dir);
        if (error.has_error) {
            logger_log(logger, LOG_ERROR, "EXPORT", "Failed to export film allocation: %s", error.message);
            return error;
        }
        
        logger_log(logger, LOG_INFO, "EXPORT", "Exported film allocation");
    }
    
    logger_log(logger, LOG_SUCCESS, "EXPORT", "Successfully exported all project results to %s", data_dir);
    
    return error;
}

static MicrofilmError create_data_directory(const char *project_path, char *data_dir_path) {
    MicrofilmError error = {false, ""};
    
    snprintf(data_dir_path, MAX_PATH_LENGTH, "%s/.data", project_path);
    
    if (!directory_exists(data_dir_path)) {
        error = create_directory(data_dir_path);
        if (error.has_error) {
            return error;
        }
    }
    
    return error;
}

static MicrofilmError export_project_info(const Project *project, const char *output_dir) {
    MicrofilmError error = {false, ""};
    
    char file_path[MAX_PATH_LENGTH];
    snprintf(file_path, MAX_PATH_LENGTH, "%s/%s_project_info.json", output_dir, project->archive_id);
    
    FILE *file = fopen(file_path, "w");
    if (!file) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to open file for writing: %s", file_path);
        return error;
    }
    
    fprintf(file, "{\n");
    write_json_string(file, "archive_id", project->archive_id, false);
    write_json_string(file, "location", project->location, false);
    write_json_string(file, "location_code", project_get_location_code(project), false);
    write_json_string(file, "doc_type", project->doc_type, false);
    write_json_string(file, "project_path", project->project_path, false);
    write_json_string(file, "project_folder_name", project->project_folder_name, false);
    
    if (strlen(project->document_folder_path) > 0) {
        write_json_string(file, "document_folder_path", project->document_folder_path, false);
    } else {
        fprintf(file, "  \"document_folder_path\": null,\n");
    }
    
    if (strlen(project->document_folder_name) > 0) {
        write_json_string(file, "document_folder_name", project->document_folder_name, false);
    } else {
        fprintf(file, "  \"document_folder_name\": null,\n");
    }
    
    write_json_bool(file, "has_oversized", project->has_oversized, false);
    write_json_int(file, "total_pages", project->total_pages, false);
    write_json_int(file, "total_pages_with_refs", project->total_pages_with_refs, false);
    write_json_int(file, "total_oversized", project->total_oversized, false);
    write_json_int(file, "documents_with_oversized", project->documents_with_oversized, false);
    
    if (strlen(project->comlist_path) > 0) {
        write_json_string(file, "comlist_path", project->comlist_path, true);
    } else {
        fprintf(file, "  \"comlist_path\": null\n");
    }
    
    fprintf(file, "}\n");
    
    fclose(file);
    return error;
}

static MicrofilmError export_documents_info(const Project *project, const char *output_dir) {
    MicrofilmError error = {false, ""};
    
    char file_path[MAX_PATH_LENGTH];
    snprintf(file_path, MAX_PATH_LENGTH, "%s/%s_documents.json", output_dir, project->archive_id);
    
    FILE *file = fopen(file_path, "w");
    if (!file) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to open file for writing: %s", file_path);
        return error;
    }
    
    fprintf(file, "[\n");
    
    for (int i = 0; i < project->documents_count; i++) {
        const Document *doc = &project->documents[i];
        
        fprintf(file, "  {\n");
        write_json_string(file, "doc_id", doc->doc_id, false);
        write_json_string(file, "path", doc->path, false);
        write_json_int(file, "pages", doc->pages, false);
        write_json_bool(file, "has_oversized", doc->has_oversized, false);
        write_json_int(file, "total_oversized", doc->total_oversized, false);
        
        // Export dimensions array
        fprintf(file, "    \"dimensions\": [\n");
        for (int j = 0; j < doc->dimensions_count; j++) {
            const PageDimension *dim = &doc->dimensions[j];
            fprintf(file, "      [%.2f, %.2f, %d, %.2f]", 
                dim->width, dim->height, dim->page_index, dim->percent_over);
            if (j < doc->dimensions_count - 1) {
                fprintf(file, ",");
            }
            fprintf(file, "\n");
        }
        fprintf(file, "    ],\n");
        
        // Export ranges array
        fprintf(file, "    \"ranges\": [\n");
        for (int j = 0; j < doc->ranges_count; j++) {
            const PageRange *range = &doc->ranges[j];
            fprintf(file, "      [%d, %d]", range->start, range->end);
            if (j < doc->ranges_count - 1) {
                fprintf(file, ",");
            }
            fprintf(file, "\n");
        }
        fprintf(file, "    ],\n");
        
        // Export reference pages array
        fprintf(file, "    \"reference_pages\": [\n");
        for (int j = 0; j < doc->reference_pages_count; j++) {
            fprintf(file, "      %d", doc->reference_pages[j]);
            if (j < doc->reference_pages_count - 1) {
                fprintf(file, ",");
            }
            fprintf(file, "\n");
        }
        fprintf(file, "    ],\n");
        
        write_json_int(file, "total_references", doc->total_references, false);
        write_json_bool(file, "is_split", doc->is_split, false);
        write_json_int(file, "roll_count", doc->roll_count, false);
        write_json_int(file, "com_id", doc->com_id, false);
        write_json_int(file, "total_pages_with_refs", doc->pages + doc->total_references, true);
        
        fprintf(file, "  }");
        if (i < project->documents_count - 1) {
            fprintf(file, ",");
        }
        fprintf(file, "\n");
    }
    
    fprintf(file, "]\n");
    
    fclose(file);
    return error;
}

static MicrofilmError export_film_allocation(const Project *project, const char *output_dir) {
    MicrofilmError error = {false, ""};
    
    const FilmAllocation *allocation = project->film_allocation;
    if (!allocation) {
        return error;
    }
    
    char file_path[MAX_PATH_LENGTH];
    snprintf(file_path, MAX_PATH_LENGTH, "%s/%s_film_allocation.json", output_dir, project->archive_id);
    
    FILE *file = fopen(file_path, "w");
    if (!file) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to open file for writing: %s", file_path);
        return error;
    }
    
    fprintf(file, "{\n");
    write_json_string(file, "archive_id", allocation->archive_id, false);
    write_json_string(file, "project_name", allocation->project_name, false);
    
    // Export 16mm rolls
    fprintf(file, "  \"rolls_16mm\": [\n");
    for (int i = 0; i < allocation->rolls_16mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_16mm[i];
        
        fprintf(file, "    {\n");
        write_json_int(file, "roll_id", roll->roll_id, false);
        write_json_string(file, "film_type", "16mm", false);
        write_json_int(file, "capacity", roll->capacity, false);
        write_json_int(file, "pages_used", roll->pages_used, false);
        write_json_int(file, "pages_remaining", roll->pages_remaining, false);
        write_json_string(file, "film_number", roll->film_number, false);
        write_json_string(file, "status", roll->status, false);
        write_json_bool(file, "has_split_documents", roll->has_split_documents, false);
        write_json_bool(file, "is_partial", roll->is_partial, false);
        write_json_int(file, "remaining_capacity", roll->remaining_capacity, false);
        write_json_int(file, "usable_capacity", roll->usable_capacity, false);
        write_json_string(file, "creation_date", roll->creation_date, false);
        
        // Export document segments
        fprintf(file, "      \"document_segments\": [\n");
        for (int j = 0; j < roll->segments_count; j++) {
            const DocumentSegment *segment = &roll->document_segments[j];
            
            fprintf(file, "        {\n");
            write_json_string(file, "doc_id", segment->doc_id, false);
            write_json_string(file, "path", segment->path, false);
            write_json_int(file, "pages", segment->pages, false);
            fprintf(file, "          \"page_range\": [%d, %d],\n", 
                segment->page_range.start, segment->page_range.end);
            fprintf(file, "          \"frame_range\": [%d, %d],\n", 
                segment->frame_range.start, segment->frame_range.end);
            write_json_int(file, "document_index", segment->document_index, false);
            write_json_bool(file, "has_oversized", segment->has_oversized, true);
            fprintf(file, "        }");
            if (j < roll->segments_count - 1) {
                fprintf(file, ",");
            }
            fprintf(file, "\n");
        }
        fprintf(file, "      ]\n");
        
        fprintf(file, "    }");
        if (i < allocation->rolls_16mm_count - 1) {
            fprintf(file, ",");
        }
        fprintf(file, "\n");
    }
    fprintf(file, "  ],\n");
    
    // Export 35mm rolls
    fprintf(file, "  \"rolls_35mm\": [\n");
    for (int i = 0; i < allocation->rolls_35mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_35mm[i];
        
        fprintf(file, "    {\n");
        write_json_int(file, "roll_id", roll->roll_id, false);
        write_json_string(file, "film_type", "35mm", false);
        write_json_int(file, "capacity", roll->capacity, false);
        write_json_int(file, "pages_used", roll->pages_used, false);
        write_json_int(file, "pages_remaining", roll->pages_remaining, false);
        write_json_string(file, "film_number", roll->film_number, false);
        write_json_string(file, "status", roll->status, false);
        write_json_bool(file, "has_split_documents", roll->has_split_documents, false);
        write_json_bool(file, "is_partial", roll->is_partial, false);
        write_json_int(file, "remaining_capacity", roll->remaining_capacity, false);
        write_json_int(file, "usable_capacity", roll->usable_capacity, false);
        write_json_string(file, "creation_date", roll->creation_date, false);
        
        // Export document segments
        fprintf(file, "      \"document_segments\": [\n");
        for (int j = 0; j < roll->segments_count; j++) {
            const DocumentSegment *segment = &roll->document_segments[j];
            
            fprintf(file, "        {\n");
            write_json_string(file, "doc_id", segment->doc_id, false);
            write_json_string(file, "path", segment->path, false);
            write_json_int(file, "pages", segment->pages, false);
            fprintf(file, "          \"page_range\": [%d, %d],\n", 
                segment->page_range.start, segment->page_range.end);
            fprintf(file, "          \"frame_range\": [%d, %d],\n", 
                segment->frame_range.start, segment->frame_range.end);
            write_json_int(file, "document_index", segment->document_index, false);
            write_json_bool(file, "has_oversized", segment->has_oversized, true);
            fprintf(file, "        }");
            if (j < roll->segments_count - 1) {
                fprintf(file, ",");
            }
            fprintf(file, "\n");
        }
        fprintf(file, "      ]\n");
        
        fprintf(file, "    }");
        if (i < allocation->rolls_35mm_count - 1) {
            fprintf(file, ",");
        }
        fprintf(file, "\n");
    }
    fprintf(file, "  ],\n");
    
    // Export statistics
    write_json_int(file, "total_rolls_16mm", allocation->total_rolls_16mm, false);
    write_json_int(file, "total_pages_16mm", allocation->total_pages_16mm, false);
    write_json_int(file, "total_partial_rolls_16mm", allocation->total_partial_rolls_16mm, false);
    write_json_int(file, "total_split_documents_16mm", allocation->total_split_documents_16mm, false);
    write_json_int(file, "total_rolls_35mm", allocation->total_rolls_35mm, false);
    write_json_int(file, "total_pages_35mm", allocation->total_pages_35mm, false);
    write_json_int(file, "total_partial_rolls_35mm", allocation->total_partial_rolls_35mm, false);
    write_json_int(file, "total_split_documents_35mm", allocation->total_split_documents_35mm, false);
    write_json_string(file, "creation_date", allocation->creation_date, false);
    write_json_string(file, "version", allocation->version, true);
    
    fprintf(file, "}\n");
    
    fclose(file);
    return error;
}

static void write_json_string(FILE *file, const char *key, const char *value, bool is_last) {
    fprintf(file, "  \"%s\": \"%s\"", key, value);
    if (!is_last) {
        fprintf(file, ",");
    }
    fprintf(file, "\n");
}

static void write_json_int(FILE *file, const char *key, int value, bool is_last) {
    fprintf(file, "  \"%s\": %d", key, value);
    if (!is_last) {
        fprintf(file, ",");
    }
    fprintf(file, "\n");
}

static void write_json_bool(FILE *file, const char *key, bool value, bool is_last) {
    fprintf(file, "  \"%s\": %s", key, value ? "true" : "false");
    if (!is_last) {
        fprintf(file, ",");
    }
    fprintf(file, "\n");
}

