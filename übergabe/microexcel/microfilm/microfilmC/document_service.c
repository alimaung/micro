/**
 * @file document_service.c
 * @brief Implementation of document processing functions
 */

#include "microfilm.h"
#include <dirent.h>
#include <ctype.h>

static MicrofilmError process_single_document(Project *project, const char *folder_path, 
    const char *filename, Logger *logger);
static bool is_oversized_page(double width, double height);
static char* extract_doc_id_from_filename(const char *filename);
static int compare_documents(const void *a, const void *b);
static void group_consecutive_pages(Document *document);

MicrofilmError document_process_all(Project *project, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project) {
        error.has_error = true;
        strcpy(error.message, "Project is NULL");
        return error;
    }
    
    logger_section(logger, "Processing Documents");
    
    // Determine documents path
    const char *documents_path;
    if (strlen(project->document_folder_path) > 0) {
        documents_path = project->document_folder_path;
    } else {
        documents_path = project->project_path;
    }
    
    logger_log(logger, LOG_INFO, "DOCUMENT", "Looking for documents in: %s", documents_path);
    
    // Check if directory exists
    if (!directory_exists(documents_path)) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Documents path does not exist: %s", documents_path);
        return error;
    }
    
    // Open directory and scan for PDF files
    DIR *dir = opendir(documents_path);
    if (!dir) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to open directory: %s", documents_path);
        return error;
    }
    
    // Count PDF files first
    struct dirent *entry;
    int pdf_count = 0;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            const char *ext = strrchr(entry->d_name, '.');
            if (ext && strcasecmp(ext, ".pdf") == 0) {
                pdf_count++;
            }
        }
    }
    
    logger_log(logger, LOG_INFO, "DOCUMENT", "Found %d PDF documents to process", pdf_count);
    
    if (pdf_count == 0) {
        logger_log(logger, LOG_WARNING, "DOCUMENT", "No PDF documents found");
        closedir(dir);
        return error;
    }
    
    // Ensure documents array has enough capacity
    if (pdf_count > project->documents_capacity) {
        project->documents_capacity = pdf_count + 10;
        Document *new_documents = realloc(project->documents, 
            project->documents_capacity * sizeof(Document));
        if (!new_documents) {
            error.has_error = true;
            strcpy(error.message, "Failed to allocate memory for documents");
            closedir(dir);
            return error;
        }
        project->documents = new_documents;
    }
    
    // Reset project statistics
    project->total_pages = 0;
    project->total_oversized = 0;
    project->documents_with_oversized = 0;
    project->has_oversized = false;
    project->documents_count = 0;
    
    // Process each PDF file
    rewinddir(dir);
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            const char *ext = strrchr(entry->d_name, '.');
            if (ext && strcasecmp(ext, ".pdf") == 0) {
                logger_log(logger, LOG_INFO, "DOCUMENT", "Processing document: %s", entry->d_name);
                
                MicrofilmError doc_error = process_single_document(project, documents_path, 
                    entry->d_name, logger);
                if (doc_error.has_error) {
                    logger_log(logger, LOG_ERROR, "DOCUMENT", "Error processing %s: %s", 
                        entry->d_name, doc_error.message);
                    // Continue processing other documents
                }
            }
        }
    }
    
    closedir(dir);
    
    // Sort documents by doc_id
    qsort(project->documents, project->documents_count, sizeof(Document), compare_documents);
    
    logger_log(logger, LOG_SUCCESS, "DOCUMENT", 
        "Processed %d documents with %d total pages", 
        project->documents_count, project->total_pages);
    logger_log(logger, LOG_SUCCESS, "DOCUMENT", 
        "Identified %d oversized pages in %d documents", 
        project->total_oversized, project->documents_with_oversized);
    
    return error;
}

static MicrofilmError process_single_document(Project *project, const char *folder_path, 
    const char *filename, Logger *logger) {
    
    MicrofilmError error = {false, ""};
    
    // Extract document ID from filename
    char *doc_id = extract_doc_id_from_filename(filename);
    if (!doc_id) {
        error.has_error = true;
        strcpy(error.message, "Failed to extract document ID from filename");
        return error;
    }
    
    // Create full path
    char full_path[MAX_PATH_LENGTH];
    snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", folder_path, filename);
    
    // Create document
    Document *doc = &project->documents[project->documents_count];
    memset(doc, 0, sizeof(Document));
    
    strncpy(doc->doc_id, doc_id, MAX_DOC_ID_LENGTH - 1);
    strncpy(doc->path, full_path, MAX_PATH_LENGTH - 1);
    
    free(doc_id);
    
    // For now, we'll simulate PDF processing since we don't have a PDF library
    // In a real implementation, you would use a PDF library like mupdf or poppler
    
    // Simulate page count (random for demo)
    doc->pages = 10 + (rand() % 50); // Random between 10-60 pages
    project->total_pages += doc->pages;
    
    // Simulate oversized page detection (random for demo)
    int oversized_count = rand() % 5; // 0-4 oversized pages
    if (oversized_count > 0) {
        doc->has_oversized = true;
        doc->total_oversized = oversized_count;
        project->total_oversized += oversized_count;
        project->documents_with_oversized++;
        project->has_oversized = true;
        
        // Allocate dimensions array
        doc->dimensions = calloc(oversized_count, sizeof(PageDimension));
        doc->dimensions_count = oversized_count;
        
        // Allocate ranges array (simplified - assume each oversized page is separate)
        doc->ranges = calloc(oversized_count, sizeof(PageRange));
        doc->ranges_count = oversized_count;
        
        for (int i = 0; i < oversized_count; i++) {
            // Simulate oversized page dimensions
            doc->dimensions[i].width = OVERSIZE_THRESHOLD_WIDTH + (rand() % 200);
            doc->dimensions[i].height = OVERSIZE_THRESHOLD_HEIGHT + (rand() % 200);
            doc->dimensions[i].page_index = rand() % doc->pages;
            doc->dimensions[i].percent_over = 10.0 + (rand() % 20);
            
            // Create range for this page
            doc->ranges[i].start = doc->dimensions[i].page_index + 1; // 1-based
            doc->ranges[i].end = doc->ranges[i].start;
        }
        
        // Group consecutive pages
        group_consecutive_pages(doc);
        
        logger_log(logger, LOG_INFO, "DOCUMENT", 
            "Document %s has %d oversized pages", doc->doc_id, doc->total_oversized);
    }
    
    doc->is_split = false;
    doc->roll_count = 1;
    doc->com_id = -1;
    
    project->documents_count++;
    
    return error;
}

static bool is_oversized_page(double width, double height) {
    return ((width > OVERSIZE_THRESHOLD_WIDTH && height > OVERSIZE_THRESHOLD_HEIGHT) ||
            (width > OVERSIZE_THRESHOLD_HEIGHT && height > OVERSIZE_THRESHOLD_WIDTH));
}

static char* extract_doc_id_from_filename(const char *filename) {
    if (!filename) return NULL;
    
    // Look for leading digits
    const char *start = filename;
    const char *end = start;
    
    // Find first digit
    while (*start && !isdigit(*start)) {
        start++;
    }
    
    if (!*start) {
        // No digits found, use filename without extension
        const char *dot = strrchr(filename, '.');
        size_t len = dot ? (dot - filename) : strlen(filename);
        char *doc_id = malloc(len + 1);
        if (doc_id) {
            strncpy(doc_id, filename, len);
            doc_id[len] = '\0';
        }
        return doc_id;
    }
    
    // Find end of digits
    end = start;
    while (*end && isdigit(*end)) {
        end++;
    }
    
    size_t len = end - start;
    char *doc_id = malloc(len + 1);
    if (doc_id) {
        strncpy(doc_id, start, len);
        doc_id[len] = '\0';
    }
    
    return doc_id;
}

static int compare_documents(const void *a, const void *b) {
    const Document *doc_a = (const Document *)a;
    const Document *doc_b = (const Document *)b;
    
    // Convert doc_id to integer for proper numeric sorting
    int id_a = atoi(doc_a->doc_id);
    int id_b = atoi(doc_b->doc_id);
    
    if (id_a == id_b) {
        // Fallback to string comparison
        return strcmp(doc_a->doc_id, doc_b->doc_id);
    }
    
    return id_a - id_b;
}

static void group_consecutive_pages(Document *document) {
    if (!document || !document->ranges || document->ranges_count <= 1) {
        return;
    }
    
    // Sort ranges by start page
    for (int i = 0; i < document->ranges_count - 1; i++) {
        for (int j = i + 1; j < document->ranges_count; j++) {
            if (document->ranges[i].start > document->ranges[j].start) {
                PageRange temp = document->ranges[i];
                document->ranges[i] = document->ranges[j];
                document->ranges[j] = temp;
            }
        }
    }
    
    // Group consecutive pages
    int new_count = 0;
    for (int i = 0; i < document->ranges_count; i++) {
        if (i == 0 || document->ranges[i].start > document->ranges[new_count - 1].end + 1) {
            // Start a new range
            document->ranges[new_count] = document->ranges[i];
            new_count++;
        } else {
            // Extend the previous range
            if (document->ranges[i].end > document->ranges[new_count - 1].end) {
                document->ranges[new_count - 1].end = document->ranges[i].end;
            }
        }
    }
    
    document->ranges_count = new_count;
}

MicrofilmError document_calculate_references(Project *project, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project) {
        error.has_error = true;
        strcpy(error.message, "Project is NULL");
        return error;
    }
    
    if (!project->has_oversized) {
        logger_log(logger, LOG_INFO, "DOCUMENT", "No oversized pages found, skipping reference calculation");
        return error;
    }
    
    logger_log(logger, LOG_INFO, "DOCUMENT", "Calculating reference page positions");
    
    int total_references = 0;
    
    for (int i = 0; i < project->documents_count; i++) {
        Document *doc = &project->documents[i];
        
        if (!doc->has_oversized || doc->ranges_count == 0) {
            doc->total_references = 0;
            continue;
        }
        
        // Calculate reference pages (one before each range)
        doc->reference_pages_count = doc->ranges_count;
        doc->reference_pages = calloc(doc->reference_pages_count, sizeof(int));
        
        if (!doc->reference_pages) {
            error.has_error = true;
            strcpy(error.message, "Failed to allocate memory for reference pages");
            return error;
        }
        
        for (int j = 0; j < doc->ranges_count; j++) {
            doc->reference_pages[j] = doc->ranges[j].start;
        }
        
        doc->total_references = doc->reference_pages_count;
        total_references += doc->total_references;
        
        logger_log(logger, LOG_DEBUG, "DOCUMENT", 
            "Added %d reference pages for document %s", 
            doc->total_references, doc->doc_id);
    }
    
    // Update project total
    project->total_pages_with_refs = project->total_pages + total_references;
    
    logger_log(logger, LOG_SUCCESS, "DOCUMENT", 
        "Added %d reference pages across all documents", total_references);
    
    return error;
}
