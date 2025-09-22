/**
 * @file film_service.c
 * @brief Implementation of film allocation functions
 */

#include "microfilm.h"

static MicrofilmError allocate_no_oversized(Project *project, Logger *logger);
static MicrofilmError allocate_with_oversized(Project *project, Logger *logger);
static MicrofilmError allocate_16mm_with_oversized(Project *project, FilmAllocation *allocation, Logger *logger);
static MicrofilmError allocate_35mm_strict(Project *project, FilmAllocation *allocation, Logger *logger);
static void log_allocation_statistics(const FilmAllocation *allocation, Logger *logger);
static FilmRoll* add_film_roll(FilmAllocation *allocation, FilmType film_type, int capacity);

MicrofilmError film_allocate(Project *project, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project) {
        error.has_error = true;
        strcpy(error.message, "Project is NULL");
        return error;
    }
    
    logger_section(logger, "Film Allocation");
    logger_log(logger, LOG_INFO, "FILM", "Starting film allocation for project %s", project->archive_id);
    
    // Log document and page counts
    logger_log(logger, LOG_INFO, "FILM", "Total documents: %d", project->documents_count);
    logger_log(logger, LOG_INFO, "FILM", "Total pages: %d", project->total_pages);
    logger_log(logger, LOG_INFO, "FILM", "Total pages with references: %d", project->total_pages_with_refs);
    
    // Check if we have any documents to allocate
    if (project->documents_count == 0) {
        logger_log(logger, LOG_WARNING, "FILM", "No documents to allocate");
        
        // Create an empty film allocation
        project->film_allocation = film_allocation_create(project->archive_id, project->project_folder_name);
        if (!project->film_allocation) {
            error.has_error = true;
            strcpy(error.message, "Failed to create film allocation");
        }
        return error;
    }
    
    // Choose allocation strategy based on oversized pages
    if (project->has_oversized) {
        logger_log(logger, LOG_INFO, "FILM", "Project has oversized pages, using specialized allocation");
        error = allocate_with_oversized(project, logger);
    } else {
        logger_log(logger, LOG_INFO, "FILM", "Project has no oversized pages, using standard allocation");
        error = allocate_no_oversized(project, logger);
    }
    
    if (!error.has_error && project->film_allocation) {
        log_allocation_statistics(project->film_allocation, logger);
    }
    
    return error;
}

static MicrofilmError allocate_no_oversized(Project *project, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    logger_section(logger, "16MM Film Allocation - No Oversized Pages");
    
    // Create film allocation
    FilmAllocation *allocation = film_allocation_create(project->archive_id, project->project_folder_name);
    if (!allocation) {
        error.has_error = true;
        strcpy(error.message, "Failed to create film allocation");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", "Processing %d documents in alphabetical order", project->documents_count);
    
    // Create first roll
    FilmRoll *current_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
    if (!current_roll) {
        error.has_error = true;
        strcpy(error.message, "Failed to create initial film roll");
        film_allocation_destroy(allocation);
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", "Created 16mm roll %d with capacity %d", 
        current_roll->roll_id, CAPACITY_16MM);
    
    // Process each document
    for (int i = 0; i < project->documents_count; i++) {
        Document *doc = &project->documents[i];
        int doc_pages = doc->pages + doc->total_references;
        
        // Check if document exceeds roll capacity
        if (doc_pages > CAPACITY_16MM) {
            logger_log(logger, LOG_INFO, "FILM", 
                "Document %s exceeds roll capacity, will be split across rolls", doc->doc_id);
            
            // Document requires splitting
            int pages_left = doc_pages;
            int start_page = 1;
            int doc_roll_count = 0;
            
            while (pages_left > 0) {
                current_roll = &allocation->rolls_16mm[allocation->rolls_16mm_count - 1];
                
                int pages_to_allocate = (pages_left < current_roll->pages_remaining) ? 
                    pages_left : current_roll->pages_remaining;
                
                if (pages_to_allocate > 0) {
                    int end_page = start_page + pages_to_allocate - 1;
                    PageRange page_range = {start_page, end_page};
                    
                    MicrofilmError segment_error = film_roll_add_document_segment(
                        current_roll, doc->doc_id, doc->path, pages_to_allocate, 
                        page_range, doc->has_oversized);
                    
                    if (segment_error.has_error) {
                        error = segment_error;
                        film_allocation_destroy(allocation);
                        return error;
                    }
                    
                    pages_left -= pages_to_allocate;
                    start_page = end_page + 1;
                    doc_roll_count++;
                }
                
                // Create new roll if needed
                if (pages_left > 0) {
                    current_roll->has_split_documents = true;
                    
                    FilmRoll *new_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
                    if (!new_roll) {
                        error.has_error = true;
                        strcpy(error.message, "Failed to create new film roll");
                        film_allocation_destroy(allocation);
                        return error;
                    }
                    
                    logger_log(logger, LOG_INFO, "FILM", 
                        "Created new roll %d with capacity %d", new_roll->roll_id, CAPACITY_16MM);
                }
            }
            
            doc->is_split = (doc_roll_count > 1);
            doc->roll_count = doc_roll_count;
            
            if (doc->is_split) {
                logger_log(logger, LOG_INFO, "FILM", 
                    "Document %s is split across %d rolls", doc->doc_id, doc_roll_count);
            }
        } else {
            // Normal sized document
            current_roll = &allocation->rolls_16mm[allocation->rolls_16mm_count - 1];
            
            if (doc_pages <= current_roll->pages_remaining) {
                // Fits in current roll
                PageRange page_range = {1, doc_pages};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    current_roll, doc->doc_id, doc->path, doc_pages, 
                    page_range, doc->has_oversized);
                
                if (segment_error.has_error) {
                    error = segment_error;
                    film_allocation_destroy(allocation);
                    return error;
                }
                
                doc->is_split = false;
                doc->roll_count = 1;
            } else {
                // Need new roll
                logger_log(logger, LOG_INFO, "FILM", 
                    "Document %s doesn't fit in current roll, creating new roll", doc->doc_id);
                
                // Mark current roll as partial
                current_roll->is_partial = true;
                current_roll->remaining_capacity = current_roll->pages_remaining;
                current_roll->usable_capacity = current_roll->pages_remaining - PADDING_16MM;
                
                // Create new roll
                FilmRoll *new_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
                if (!new_roll) {
                    error.has_error = true;
                    strcpy(error.message, "Failed to create new film roll");
                    film_allocation_destroy(allocation);
                    return error;
                }
                
                logger_log(logger, LOG_INFO, "FILM", 
                    "Created new roll %d with capacity %d", new_roll->roll_id, CAPACITY_16MM);
                
                // Add document to new roll
                PageRange page_range = {1, doc_pages};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    new_roll, doc->doc_id, doc->path, doc_pages, 
                    page_range, doc->has_oversized);
                
                if (segment_error.has_error) {
                    error = segment_error;
                    film_allocation_destroy(allocation);
                    return error;
                }
                
                doc->is_split = false;
                doc->roll_count = 1;
            }
        }
    }
    
    // Mark last roll as partial if it has remaining capacity
    if (allocation->rolls_16mm_count > 0) {
        FilmRoll *last_roll = &allocation->rolls_16mm[allocation->rolls_16mm_count - 1];
        if (last_roll->pages_remaining > 0 && !last_roll->is_partial) {
            last_roll->is_partial = true;
            last_roll->remaining_capacity = last_roll->pages_remaining;
            last_roll->usable_capacity = last_roll->pages_remaining - PADDING_16MM;
            
            logger_log(logger, LOG_INFO, "FILM", 
                "Last roll %d is partial with %d pages remaining", 
                last_roll->roll_id, last_roll->remaining_capacity);
        }
    }
    
    // Update statistics
    allocation->total_rolls_16mm = allocation->rolls_16mm_count;
    allocation->total_pages_16mm = 0;
    for (int i = 0; i < allocation->rolls_16mm_count; i++) {
        allocation->total_pages_16mm += allocation->rolls_16mm[i].pages_used;
    }
    
    project->film_allocation = allocation;
    
    logger_log(logger, LOG_SUCCESS, "FILM", "16mm allocation complete");
    logger_log(logger, LOG_INFO, "FILM", "Total rolls: %d", allocation->total_rolls_16mm);
    logger_log(logger, LOG_INFO, "FILM", "Total pages: %d", allocation->total_pages_16mm);
    
    return error;
}

static MicrofilmError allocate_with_oversized(Project *project, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    logger_section(logger, "Film Allocation - With Oversized Pages");
    
    logger_log(logger, LOG_INFO, "FILM", "Starting specialized allocation for project with oversized pages");
    logger_log(logger, LOG_INFO, "FILM", "Project has %d oversized pages in %d documents", 
        project->total_oversized, project->documents_with_oversized);
    
    // Create film allocation
    FilmAllocation *allocation = film_allocation_create(project->archive_id, project->project_folder_name);
    if (!allocation) {
        error.has_error = true;
        strcpy(error.message, "Failed to create film allocation");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", "Created film allocation object for project %s", project->archive_id);
    logger_log(logger, LOG_INFO, "FILM", "Proceeding with dual film allocation (16mm for all pages, 35mm for oversized)");
    
    // Step 1: Allocate all documents to 16mm
    logger_log(logger, LOG_INFO, "FILM", "Step 1: Allocating all documents to 16mm film");
    error = allocate_16mm_with_oversized(project, allocation, logger);
    if (error.has_error) {
        film_allocation_destroy(allocation);
        return error;
    }
    
    // Step 2: Allocate oversized pages to 35mm
    logger_log(logger, LOG_INFO, "FILM", "Step 2: Allocating oversized pages to 35mm film");
    error = allocate_35mm_strict(project, allocation, logger);
    if (error.has_error) {
        film_allocation_destroy(allocation);
        return error;
    }
    
    project->film_allocation = allocation;
    
    logger_log(logger, LOG_SUCCESS, "FILM", "Completed specialized allocation for project with oversized pages");
    
    return error;
}

static MicrofilmError allocate_16mm_with_oversized(Project *project, FilmAllocation *allocation, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    logger_section(logger, "16MM Film Allocation - With Oversized Pages");
    
    logger_log(logger, LOG_INFO, "FILM", "Allocating %d documents to 16mm film", project->documents_count);
    logger_log(logger, LOG_INFO, "FILM", "Total regular pages: %d", project->total_pages);
    logger_log(logger, LOG_INFO, "FILM", "Total reference pages: %d", 
        project->total_pages_with_refs - project->total_pages);
    
    // Create first roll
    FilmRoll *current_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
    if (!current_roll) {
        error.has_error = true;
        strcpy(error.message, "Failed to create initial 16mm film roll");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", "Created 16mm roll %d with capacity %d", 
        current_roll->roll_id, CAPACITY_16MM);
    
    // Process documents (similar to allocate_no_oversized but with oversized handling)
    for (int i = 0; i < project->documents_count; i++) {
        Document *doc = &project->documents[i];
        int doc_pages = doc->pages + doc->total_references;
        
        logger_log(logger, LOG_INFO, "FILM", 
            "Processing document %s with %d total pages (including references)", 
            doc->doc_id, doc_pages);
        
        // Same allocation logic as standard allocation
        if (doc_pages > CAPACITY_16MM) {
            // Split document across rolls
            int pages_left = doc_pages;
            int start_page = 1;
            int doc_roll_count = 0;
            
            while (pages_left > 0) {
                current_roll = &allocation->rolls_16mm[allocation->rolls_16mm_count - 1];
                
                int pages_to_allocate = (pages_left < current_roll->pages_remaining) ? 
                    pages_left : current_roll->pages_remaining;
                
                if (pages_to_allocate > 0) {
                    int end_page = start_page + pages_to_allocate - 1;
                    PageRange page_range = {start_page, end_page};
                    
                    MicrofilmError segment_error = film_roll_add_document_segment(
                        current_roll, doc->doc_id, doc->path, pages_to_allocate, 
                        page_range, doc->has_oversized);
                    
                    if (segment_error.has_error) {
                        return segment_error;
                    }
                    
                    logger_log(logger, LOG_INFO, "FILM", 
                        "Added %d pages of document %s to roll %d", 
                        pages_to_allocate, doc->doc_id, current_roll->roll_id);
                    
                    pages_left -= pages_to_allocate;
                    start_page = end_page + 1;
                    doc_roll_count++;
                }
                
                if (pages_left > 0) {
                    current_roll->has_split_documents = true;
                    
                    FilmRoll *new_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
                    if (!new_roll) {
                        error.has_error = true;
                        strcpy(error.message, "Failed to create new 16mm film roll");
                        return error;
                    }
                    
                    logger_log(logger, LOG_INFO, "FILM", 
                        "Created new roll %d with capacity %d", new_roll->roll_id, CAPACITY_16MM);
                }
            }
            
            doc->is_split = (doc_roll_count > 1);
            doc->roll_count = doc_roll_count;
        } else {
            // Normal allocation logic
            current_roll = &allocation->rolls_16mm[allocation->rolls_16mm_count - 1];
            
            if (doc_pages <= current_roll->pages_remaining) {
                PageRange page_range = {1, doc_pages};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    current_roll, doc->doc_id, doc->path, doc_pages, 
                    page_range, doc->has_oversized);
                
                if (segment_error.has_error) {
                    return segment_error;
                }
                
                logger_log(logger, LOG_INFO, "FILM", 
                    "Added document %s with %d pages to roll %d", 
                    doc->doc_id, doc_pages, current_roll->roll_id);
                
                doc->is_split = false;
                doc->roll_count = 1;
            } else {
                // Create new roll
                current_roll->is_partial = true;
                current_roll->remaining_capacity = current_roll->pages_remaining;
                current_roll->usable_capacity = current_roll->pages_remaining - PADDING_16MM;
                
                FilmRoll *new_roll = add_film_roll(allocation, FILM_16MM, CAPACITY_16MM);
                if (!new_roll) {
                    error.has_error = true;
                    strcpy(error.message, "Failed to create new 16mm film roll");
                    return error;
                }
                
                PageRange page_range = {1, doc_pages};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    new_roll, doc->doc_id, doc->path, doc_pages, 
                    page_range, doc->has_oversized);
                
                if (segment_error.has_error) {
                    return segment_error;
                }
                
                doc->is_split = false;
                doc->roll_count = 1;
            }
        }
    }
    
    // Update statistics
    allocation->total_rolls_16mm = allocation->rolls_16mm_count;
    allocation->total_pages_16mm = 0;
    for (int i = 0; i < allocation->rolls_16mm_count; i++) {
        allocation->total_pages_16mm += allocation->rolls_16mm[i].pages_used;
    }
    
    logger_log(logger, LOG_SUCCESS, "FILM", "16mm allocation complete with oversized support");
    logger_log(logger, LOG_INFO, "FILM", "Total 16mm rolls: %d", allocation->total_rolls_16mm);
    logger_log(logger, LOG_INFO, "FILM", "Total 16mm pages: %d", allocation->total_pages_16mm);
    
    return error;
}

static MicrofilmError allocate_35mm_strict(Project *project, FilmAllocation *allocation, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    logger_section(logger, "35MM Film Allocation");
    
    if (project->total_oversized == 0) {
        logger_log(logger, LOG_INFO, "FILM", "No oversized pages to allocate to 35mm film");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", 
        "Found %d oversized pages in %d documents", 
        project->total_oversized, project->documents_with_oversized);
    
    // Create first 35mm roll
    FilmRoll *current_roll = add_film_roll(allocation, FILM_35MM, CAPACITY_35MM);
    if (!current_roll) {
        error.has_error = true;
        strcpy(error.message, "Failed to create initial 35mm film roll");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "FILM", "Created 35mm roll %d with capacity %d", 
        current_roll->roll_id, CAPACITY_35MM);
    
    // Process documents with oversized pages
    for (int i = 0; i < project->documents_count; i++) {
        Document *doc = &project->documents[i];
        
        if (!doc->has_oversized) continue;
        
        int total_oversized_with_refs = doc->total_oversized + doc->total_references;
        
        logger_log(logger, LOG_INFO, "FILM", 
            "Processing document %s with %d oversized pages", 
            doc->doc_id, doc->total_oversized);
        
        if (total_oversized_with_refs > CAPACITY_35MM) {
            // Split large document
            logger_log(logger, LOG_INFO, "FILM", 
                "Splitting large document %s with %d pages", 
                doc->doc_id, total_oversized_with_refs);
            
            int pages_left = total_oversized_with_refs;
            int start_page = 1;
            
            while (pages_left > 0) {
                current_roll = &allocation->rolls_35mm[allocation->rolls_35mm_count - 1];
                
                int pages_to_allocate = (pages_left < current_roll->pages_remaining) ? 
                    pages_left : current_roll->pages_remaining;
                
                if (pages_to_allocate > 0) {
                    int end_page = start_page + pages_to_allocate - 1;
                    PageRange page_range = {start_page, end_page};
                    
                    MicrofilmError segment_error = film_roll_add_document_segment(
                        current_roll, doc->doc_id, doc->path, pages_to_allocate, 
                        page_range, true);
                    
                    if (segment_error.has_error) {
                        return segment_error;
                    }
                    
                    pages_left -= pages_to_allocate;
                    start_page = end_page + 1;
                }
                
                if (pages_left > 0) {
                    FilmRoll *new_roll = add_film_roll(allocation, FILM_35MM, CAPACITY_35MM);
                    if (!new_roll) {
                        error.has_error = true;
                        strcpy(error.message, "Failed to create new 35mm film roll");
                        return error;
                    }
                    
                    logger_log(logger, LOG_INFO, "FILM", 
                        "Created new 35mm roll %d with capacity %d", 
                        new_roll->roll_id, CAPACITY_35MM);
                }
            }
        } else {
            // Regular sized oversized document
            current_roll = &allocation->rolls_35mm[allocation->rolls_35mm_count - 1];
            
            if (total_oversized_with_refs <= current_roll->pages_remaining) {
                PageRange page_range = {1, total_oversized_with_refs};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    current_roll, doc->doc_id, doc->path, total_oversized_with_refs, 
                    page_range, true);
                
                if (segment_error.has_error) {
                    return segment_error;
                }
            } else {
                // Need new roll
                FilmRoll *new_roll = add_film_roll(allocation, FILM_35MM, CAPACITY_35MM);
                if (!new_roll) {
                    error.has_error = true;
                    strcpy(error.message, "Failed to create new 35mm film roll");
                    return error;
                }
                
                PageRange page_range = {1, total_oversized_with_refs};
                
                MicrofilmError segment_error = film_roll_add_document_segment(
                    new_roll, doc->doc_id, doc->path, total_oversized_with_refs, 
                    page_range, true);
                
                if (segment_error.has_error) {
                    return segment_error;
                }
            }
        }
    }
    
    // Update statistics
    allocation->total_rolls_35mm = allocation->rolls_35mm_count;
    allocation->total_pages_35mm = 0;
    for (int i = 0; i < allocation->rolls_35mm_count; i++) {
        allocation->total_pages_35mm += allocation->rolls_35mm[i].pages_used;
    }
    
    logger_log(logger, LOG_SUCCESS, "FILM", "35mm allocation complete");
    logger_log(logger, LOG_INFO, "FILM", "Total 35mm rolls: %d", allocation->total_rolls_35mm);
    logger_log(logger, LOG_INFO, "FILM", "Total 35mm pages: %d", allocation->total_pages_35mm);
    
    return error;
}

static FilmRoll* add_film_roll(FilmAllocation *allocation, FilmType film_type, int capacity) {
    FilmRoll **rolls;
    int *count;
    int *roll_capacity;
    
    if (film_type == FILM_16MM) {
        rolls = &allocation->rolls_16mm;
        count = &allocation->rolls_16mm_count;
        roll_capacity = &allocation->rolls_16mm_capacity;
    } else {
        rolls = &allocation->rolls_35mm;
        count = &allocation->rolls_35mm_count;
        roll_capacity = &allocation->rolls_35mm_capacity;
    }
    
    // Check if we need to expand the array
    if (*count >= *roll_capacity) {
        *roll_capacity *= 2;
        FilmRoll *new_rolls = realloc(*rolls, *roll_capacity * sizeof(FilmRoll));
        if (!new_rolls) {
            return NULL;
        }
        *rolls = new_rolls;
    }
    
    // Create new roll
    int roll_id = *count + 1;
    FilmRoll *new_roll = film_roll_create(roll_id, film_type, capacity);
    if (!new_roll) {
        return NULL;
    }
    
    // Copy roll data into the array
    (*rolls)[*count] = *new_roll;
    free(new_roll); // Free the temporary roll structure
    
    (*count)++;
    
    return &(*rolls)[*count - 1];
}

static void log_allocation_statistics(const FilmAllocation *allocation, Logger *logger) {
    if (!allocation) {
        logger_log(logger, LOG_WARNING, "FILM", "No film allocation to log statistics for");
        return;
    }
    
    logger_section(logger, "Film Allocation Statistics");
    
    // Log 16mm statistics
    logger_log(logger, LOG_INFO, "FILM", "16mm Film Statistics:");
    logger_log(logger, LOG_INFO, "FILM", "- Total rolls: %d", allocation->total_rolls_16mm);
    logger_log(logger, LOG_INFO, "FILM", "- Total pages: %d", allocation->total_pages_16mm);
    logger_log(logger, LOG_INFO, "FILM", "- Partial rolls: %d", allocation->total_partial_rolls_16mm);
    logger_log(logger, LOG_INFO, "FILM", "- Split documents: %d", allocation->total_split_documents_16mm);
    
    // Log 35mm statistics if applicable
    if (allocation->total_rolls_35mm > 0) {
        logger_log(logger, LOG_INFO, "FILM", "35mm Film Statistics:");
        logger_log(logger, LOG_INFO, "FILM", "- Total rolls: %d", allocation->total_rolls_35mm);
        logger_log(logger, LOG_INFO, "FILM", "- Total pages: %d", allocation->total_pages_35mm);
        logger_log(logger, LOG_INFO, "FILM", "- Partial rolls: %d", allocation->total_partial_rolls_35mm);
        logger_log(logger, LOG_INFO, "FILM", "- Split documents: %d", allocation->total_split_documents_35mm);
    }
}

