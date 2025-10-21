/**
 * @file database.c
 * @brief Implementation of database operations for the microfilm system
 */

#include "microfilm.h"

static MicrofilmError create_database_schema(sqlite3 *db);
static int register_project(sqlite3 *db, const Project *project);
static MicrofilmError save_rolls(sqlite3 *db, const FilmAllocation *allocation, int project_id);
static MicrofilmError save_documents(sqlite3 *db, const FilmAllocation *allocation, int project_id);
static char* generate_film_number(const char *location_code, int sequence_number);
static int get_next_film_number_sequence(sqlite3 *db, const char *location_code);

MicrofilmError database_init(const char *db_path) {
    MicrofilmError error = {false, ""};
    
    if (!db_path) {
        error.has_error = true;
        strcpy(error.message, "Database path is NULL");
        return error;
    }
    
    sqlite3 *db;
    int rc = sqlite3_open(db_path, &db);
    
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Cannot open database: %s", sqlite3_errmsg(db));
        sqlite3_close(db);
        return error;
    }
    
    // Create schema
    error = create_database_schema(db);
    
    sqlite3_close(db);
    return error;
}

static MicrofilmError create_database_schema(sqlite3 *db) {
    MicrofilmError error = {false, ""};
    char *err_msg = NULL;
    
    // Create Projects table
    const char *projects_sql = 
        "CREATE TABLE IF NOT EXISTS Projects ("
        "project_id INTEGER PRIMARY KEY,"
        "archive_id TEXT NOT NULL,"
        "location TEXT,"
        "doc_type TEXT,"
        "path TEXT,"
        "folderName TEXT,"
        "oversized BOOLEAN,"
        "total_pages INTEGER,"
        "total_pages_with_refs INTEGER,"
        "date_created TEXT,"
        "data_dir TEXT,"
        "index_path TEXT"
        ");";
    
    int rc = sqlite3_exec(db, projects_sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to create Projects table: %s", err_msg);
        sqlite3_free(err_msg);
        return error;
    }
    
    // Create Rolls table
    const char *rolls_sql = 
        "CREATE TABLE IF NOT EXISTS Rolls ("
        "roll_id INTEGER PRIMARY KEY,"
        "film_number TEXT,"
        "film_type TEXT,"
        "capacity INTEGER,"
        "pages_used INTEGER,"
        "pages_remaining INTEGER,"
        "status TEXT,"
        "project_id INTEGER,"
        "creation_date TEXT,"
        "source_temp_roll_id INTEGER NULL,"
        "created_temp_roll_id INTEGER NULL,"
        "film_number_source TEXT NULL,"
        "FOREIGN KEY (project_id) REFERENCES Projects(project_id)"
        ");";
    
    rc = sqlite3_exec(db, rolls_sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to create Rolls table: %s", err_msg);
        sqlite3_free(err_msg);
        return error;
    }
    
    // Create TempRolls table
    const char *temp_rolls_sql = 
        "CREATE TABLE IF NOT EXISTS TempRolls ("
        "temp_roll_id INTEGER PRIMARY KEY,"
        "film_type TEXT,"
        "capacity INTEGER,"
        "usable_capacity INTEGER,"
        "status TEXT,"
        "creation_date TEXT,"
        "source_roll_id INTEGER,"
        "used_by_roll_id INTEGER NULL,"
        "FOREIGN KEY (source_roll_id) REFERENCES Rolls(roll_id),"
        "FOREIGN KEY (used_by_roll_id) REFERENCES Rolls(roll_id)"
        ");";
    
    rc = sqlite3_exec(db, temp_rolls_sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to create TempRolls table: %s", err_msg);
        sqlite3_free(err_msg);
        return error;
    }
    
    // Create Documents table
    const char *documents_sql = 
        "CREATE TABLE IF NOT EXISTS Documents ("
        "document_id INTEGER PRIMARY KEY,"
        "document_name TEXT,"
        "com_id TEXT,"
        "roll_id INTEGER,"
        "page_range_start INTEGER,"
        "page_range_end INTEGER,"
        "is_oversized BOOLEAN,"
        "filepath TEXT,"
        "blip TEXT,"
        "blipend TEXT,"
        "blip_type TEXT DEFAULT '16mm',"
        "FOREIGN KEY (roll_id) REFERENCES Rolls(roll_id)"
        ");";
    
    rc = sqlite3_exec(db, documents_sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to create Documents table: %s", err_msg);
        sqlite3_free(err_msg);
        return error;
    }
    
    // Create index for performance
    const char *index_sql = 
        "CREATE INDEX IF NOT EXISTS idx_documents_blip_type "
        "ON Documents (blip_type);";
    
    rc = sqlite3_exec(db, index_sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to create index: %s", err_msg);
        sqlite3_free(err_msg);
        return error;
    }
    
    return error;
}

MicrofilmError database_save_project(const Project *project, const char *db_path) {
    MicrofilmError error = {false, ""};
    
    if (!project || !db_path) {
        error.has_error = true;
        strcpy(error.message, "Invalid parameters");
        return error;
    }
    
    sqlite3 *db;
    int rc = sqlite3_open(db_path, &db);
    
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Cannot open database: %s", sqlite3_errmsg(db));
        sqlite3_close(db);
        return error;
    }
    
    // Begin transaction
    rc = sqlite3_exec(db, "BEGIN TRANSACTION", 0, 0, 0);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to begin transaction: %s", sqlite3_errmsg(db));
        sqlite3_close(db);
        return error;
    }
    
    // Register project and get project ID
    int project_id = register_project(db, project);
    if (project_id < 0) {
        error.has_error = true;
        strcpy(error.message, "Failed to register project");
        sqlite3_exec(db, "ROLLBACK", 0, 0, 0);
        sqlite3_close(db);
        return error;
    }
    
    // Save film allocation if present
    if (project->film_allocation) {
        error = save_rolls(db, project->film_allocation, project_id);
        if (error.has_error) {
            sqlite3_exec(db, "ROLLBACK", 0, 0, 0);
            sqlite3_close(db);
            return error;
        }
        
        error = save_documents(db, project->film_allocation, project_id);
        if (error.has_error) {
            sqlite3_exec(db, "ROLLBACK", 0, 0, 0);
            sqlite3_close(db);
            return error;
        }
    }
    
    // Commit transaction
    rc = sqlite3_exec(db, "COMMIT", 0, 0, 0);
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to commit transaction: %s", sqlite3_errmsg(db));
        sqlite3_exec(db, "ROLLBACK", 0, 0, 0);
    }
    
    sqlite3_close(db);
    return error;
}

static int register_project(sqlite3 *db, const Project *project) {
    const char *sql = 
        "INSERT INTO Projects (archive_id, location, doc_type, path, folderName, "
        "oversized, total_pages, total_pages_with_refs, date_created) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));";
    
    sqlite3_stmt *stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, project->archive_id, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, project->location, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, project->doc_type, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 4, project->project_path, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 5, project->project_folder_name, -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 6, project->has_oversized ? 1 : 0);
    sqlite3_bind_int(stmt, 7, project->total_pages);
    sqlite3_bind_int(stmt, 8, project->total_pages_with_refs);
    
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    if (rc != SQLITE_DONE) {
        return -1;
    }
    
    return (int)sqlite3_last_insert_rowid(db);
}

static MicrofilmError save_rolls(sqlite3 *db, const FilmAllocation *allocation, int project_id) {
    MicrofilmError error = {false, ""};
    
    const char *sql = 
        "INSERT INTO Rolls (film_number, film_type, capacity, pages_used, "
        "pages_remaining, status, project_id, creation_date, film_number_source) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);";
    
    sqlite3_stmt *stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to prepare roll insert statement: %s", sqlite3_errmsg(db));
        return error;
    }
    
    // Save 16mm rolls
    for (int i = 0; i < allocation->rolls_16mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_16mm[i];
        
        sqlite3_bind_text(stmt, 1, roll->film_number, -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, "16mm", -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 3, roll->capacity);
        sqlite3_bind_int(stmt, 4, roll->pages_used);
        sqlite3_bind_int(stmt, 5, roll->pages_remaining);
        sqlite3_bind_text(stmt, 6, roll->status, -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 7, project_id);
        sqlite3_bind_text(stmt, 8, roll->creation_date, -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 9, "new", -1, SQLITE_STATIC);
        
        rc = sqlite3_step(stmt);
        if (rc != SQLITE_DONE) {
            error.has_error = true;
            snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
                "Failed to insert 16mm roll: %s", sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            return error;
        }
        
        sqlite3_reset(stmt);
    }
    
    // Save 35mm rolls
    for (int i = 0; i < allocation->rolls_35mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_35mm[i];
        
        sqlite3_bind_text(stmt, 1, roll->film_number, -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, "35mm", -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 3, roll->capacity);
        sqlite3_bind_int(stmt, 4, roll->pages_used);
        sqlite3_bind_int(stmt, 5, roll->pages_remaining);
        sqlite3_bind_text(stmt, 6, roll->status, -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 7, project_id);
        sqlite3_bind_text(stmt, 8, roll->creation_date, -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 9, "new", -1, SQLITE_STATIC);
        
        rc = sqlite3_step(stmt);
        if (rc != SQLITE_DONE) {
            error.has_error = true;
            snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
                "Failed to insert 35mm roll: %s", sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            return error;
        }
        
        sqlite3_reset(stmt);
    }
    
    sqlite3_finalize(stmt);
    return error;
}

static MicrofilmError save_documents(sqlite3 *db, const FilmAllocation *allocation, int project_id) {
    MicrofilmError error = {false, ""};
    
    const char *sql = 
        "INSERT INTO Documents (document_name, roll_id, page_range_start, "
        "page_range_end, is_oversized, filepath, blip_type) "
        "VALUES (?, ?, ?, ?, ?, ?, ?);";
    
    sqlite3_stmt *stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Failed to prepare document insert statement: %s", sqlite3_errmsg(db));
        return error;
    }
    
    // Save documents from 16mm rolls
    for (int i = 0; i < allocation->rolls_16mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_16mm[i];
        
        for (int j = 0; j < roll->segments_count; j++) {
            const DocumentSegment *segment = &roll->document_segments[j];
            
            sqlite3_bind_text(stmt, 1, segment->doc_id, -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 2, roll->roll_id);
            sqlite3_bind_int(stmt, 3, segment->page_range.start);
            sqlite3_bind_int(stmt, 4, segment->page_range.end);
            sqlite3_bind_int(stmt, 5, segment->has_oversized ? 1 : 0);
            sqlite3_bind_text(stmt, 6, segment->path, -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 7, "16mm", -1, SQLITE_STATIC);
            
            rc = sqlite3_step(stmt);
            if (rc != SQLITE_DONE) {
                error.has_error = true;
                snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
                    "Failed to insert 16mm document: %s", sqlite3_errmsg(db));
                sqlite3_finalize(stmt);
                return error;
            }
            
            sqlite3_reset(stmt);
        }
    }
    
    // Save documents from 35mm rolls
    for (int i = 0; i < allocation->rolls_35mm_count; i++) {
        const FilmRoll *roll = &allocation->rolls_35mm[i];
        
        for (int j = 0; j < roll->segments_count; j++) {
            const DocumentSegment *segment = &roll->document_segments[j];
            
            sqlite3_bind_text(stmt, 1, segment->doc_id, -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 2, roll->roll_id);
            sqlite3_bind_int(stmt, 3, segment->page_range.start);
            sqlite3_bind_int(stmt, 4, segment->page_range.end);
            sqlite3_bind_int(stmt, 5, segment->has_oversized ? 1 : 0);
            sqlite3_bind_text(stmt, 6, segment->path, -1, SQLITE_STATIC);
            sqlite3_bind_text(stmt, 7, "35mm", -1, SQLITE_STATIC);
            
            rc = sqlite3_step(stmt);
            if (rc != SQLITE_DONE) {
                error.has_error = true;
                snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
                    "Failed to insert 35mm document: %s", sqlite3_errmsg(db));
                sqlite3_finalize(stmt);
                return error;
            }
            
            sqlite3_reset(stmt);
        }
    }
    
    sqlite3_finalize(stmt);
    return error;
}

MicrofilmError database_allocate_film_numbers(Project *project, const char *db_path, Logger *logger) {
    MicrofilmError error = {false, ""};
    
    if (!project || !project->film_allocation || !db_path) {
        error.has_error = true;
        strcpy(error.message, "Invalid parameters");
        return error;
    }
    
    logger_section(logger, "Film Number Allocation");
    logger_log(logger, LOG_INFO, "DATABASE", "Starting film number allocation");
    
    sqlite3 *db;
    int rc = sqlite3_open(db_path, &db);
    
    if (rc != SQLITE_OK) {
        error.has_error = true;
        snprintf(error.message, MAX_ERROR_MESSAGE_LENGTH,
            "Cannot open database: %s", sqlite3_errmsg(db));
        sqlite3_close(db);
        return error;
    }
    
    const char *location_code = project_get_location_code(project);
    
    // Allocate film numbers for 16mm rolls
    for (int i = 0; i < project->film_allocation->rolls_16mm_count; i++) {
        FilmRoll *roll = &project->film_allocation->rolls_16mm[i];
        
        if (strlen(roll->film_number) == 0) {
            int sequence = get_next_film_number_sequence(db, location_code);
            char *film_number = generate_film_number(location_code, sequence);
            
            if (film_number) {
                strncpy(roll->film_number, film_number, MAX_FILM_NUMBER_LENGTH - 1);
                free(film_number);
                
                logger_log(logger, LOG_INFO, "DATABASE", 
                    "Assigned film number %s to 16mm roll %d", roll->film_number, roll->roll_id);
            } else {
                error.has_error = true;
                strcpy(error.message, "Failed to generate film number");
                sqlite3_close(db);
                return error;
            }
        }
    }
    
    // Allocate film numbers for 35mm rolls
    for (int i = 0; i < project->film_allocation->rolls_35mm_count; i++) {
        FilmRoll *roll = &project->film_allocation->rolls_35mm[i];
        
        if (strlen(roll->film_number) == 0) {
            int sequence = get_next_film_number_sequence(db, location_code);
            char *film_number = generate_film_number(location_code, sequence);
            
            if (film_number) {
                strncpy(roll->film_number, film_number, MAX_FILM_NUMBER_LENGTH - 1);
                free(film_number);
                
                logger_log(logger, LOG_INFO, "DATABASE", 
                    "Assigned film number %s to 35mm roll %d", roll->film_number, roll->roll_id);
            } else {
                error.has_error = true;
                strcpy(error.message, "Failed to generate film number");
                sqlite3_close(db);
                return error;
            }
        }
    }
    
    sqlite3_close(db);
    
    logger_log(logger, LOG_SUCCESS, "DATABASE", "Film number allocation completed");
    
    return error;
}

static char* generate_film_number(const char *location_code, int sequence_number) {
    char *film_number = malloc(MAX_FILM_NUMBER_LENGTH);
    if (!film_number) return NULL;
    
    snprintf(film_number, MAX_FILM_NUMBER_LENGTH, "%s%07d", location_code, sequence_number);
    
    return film_number;
}

static int get_next_film_number_sequence(sqlite3 *db, const char *location_code) {
    const char *sql = 
        "SELECT MAX(CAST(SUBSTR(film_number, 2) AS INTEGER)) "
        "FROM Rolls WHERE film_number LIKE ? || '%';";
    
    sqlite3_stmt *stmt;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        return 1; // Default to first number
    }
    
    sqlite3_bind_text(stmt, 1, location_code, -1, SQLITE_STATIC);
    
    int max_sequence = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        max_sequence = sqlite3_column_int(stmt, 0);
    }
    
    sqlite3_finalize(stmt);
    
    return max_sequence + 1;
}

