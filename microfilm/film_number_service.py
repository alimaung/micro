"""
Film number service module for managing microfilm number allocation.

This module provides a service layer for film number operations,
including assigning film numbers to rolls and updating index data.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import uuid

from models import Project, FilmNumber, TempRoll, FilmType, FilmRoll, FilmAllocation, DocumentBlip, Document, RollReferenceInfo, DocumentReferenceInfo, RangeReferenceInfo

# Constants for roll capacities and padding
CAPACITY_16MM = 2900
CAPACITY_35MM = 110
TEMP_ROLL_PADDING_16MM = 100
TEMP_ROLL_PADDING_35MM = 100
TEMP_ROLL_MIN_USABLE_PAGES = 150

class FilmNumberService:
    """
    Service for handling film number allocation operations.
    
    This service is responsible for assigning film numbers to rolls
    and updating index data with film numbers and blips.
    """
    
    def __init__(self, db_path=None, logger=None):
        """
        Initialize the film number service.
        
        Args:
            db_path: Path to the SQLite database file
            logger: Optional logger instance
        """
        self.db_path = db_path or 'film_allocation.sqlite3'
        self.logger = logger
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the database file exists and has the correct schema."""
        # Check if database file exists
        if not os.path.exists(self.db_path):
            # Create database and initialize schema
            self._init_database()
    
    def _init_database(self):
        """Initialize the database with the required schema."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Create Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Projects (
                    project_id INTEGER PRIMARY KEY,
                    archive_id TEXT NOT NULL, 
                    location TEXT,
                    doc_type TEXT,
                    path TEXT,
                    folderName TEXT,
                    oversized BOOLEAN,
                    total_pages INTEGER,
                    total_pages_with_refs INTEGER,
                    date_created TEXT,
                    data_dir TEXT,
                    index_path TEXT
                )
            ''')
            
            # Create Rolls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Rolls (
                    roll_id INTEGER PRIMARY KEY,
                    film_number TEXT,
                    film_type TEXT,
                    capacity INTEGER,
                    pages_used INTEGER,
                    pages_remaining INTEGER,
                    status TEXT,
                    project_id INTEGER,
                    creation_date TEXT,
                    source_temp_roll_id INTEGER NULL,
                    created_temp_roll_id INTEGER NULL,
                    film_number_source TEXT NULL,
                    FOREIGN KEY (project_id) REFERENCES Projects(project_id),
                    FOREIGN KEY (source_temp_roll_id) REFERENCES TempRolls(temp_roll_id),
                    FOREIGN KEY (created_temp_roll_id) REFERENCES TempRolls(temp_roll_id)
                )
            ''')
            
            # Create TempRolls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TempRolls (
                    temp_roll_id INTEGER PRIMARY KEY,
                    film_type TEXT,
                    capacity INTEGER,
                    usable_capacity INTEGER,
                    status TEXT,
                    creation_date TEXT,
                    source_roll_id INTEGER,
                    used_by_roll_id INTEGER NULL,
                    FOREIGN KEY (source_roll_id) REFERENCES Rolls(roll_id),
                    FOREIGN KEY (used_by_roll_id) REFERENCES Rolls(roll_id)
                )
            ''')
            
            # Create Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Documents (
                    document_id INTEGER PRIMARY KEY,
                    document_name TEXT,
                    com_id TEXT,
                    roll_id INTEGER,
                    page_range_start INTEGER,
                    page_range_end INTEGER,
                    is_oversized BOOLEAN,
                    filepath TEXT,
                    blip TEXT,
                    blipend TEXT,
                    blip_type TEXT DEFAULT '16mm',
                    FOREIGN KEY (roll_id) REFERENCES Rolls(roll_id)
                )
            ''')
            
            # Create an index to improve query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_documents_blip_type 
                ON Documents (blip_type);
            ''')
            # Commit changes
            conn.commit()
            
            if self.logger:
                self.logger.section("Database Initialization")
                self.logger.film_success("Database schema initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _get_connection(self):
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)
    
    def allocate_film_numbers(self, project: Project, index_data: Dict[str, Any]) -> Tuple[Project, Dict[str, Any]]:
        """
        Allocate film numbers to all rolls in the project.
        
        Args:
            project: Project with film allocation
            index_data: Index data for the project
            
        Returns:
            Updated project and index data
        """
        if self.logger:
            self.logger.section("Film Number Allocation")
            self.logger.film_info("Starting film number allocation")
        
        if not project.film_allocation:
            if self.logger:
                self.logger.film_error("No film allocation found in project")
            return project, index_data
            
        # Store current project for document lookups
        self.current_project = project
        
        # Create database connection
        conn = self._get_connection()
        try:
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            
            # Insert project into database
            project_id = self._register_project(cursor, project)
            
            # Process 16mm rolls
            self._process_16mm_rolls(cursor, project, project_id)
            
            # Process 35mm rolls if project has oversized pages
            if project.has_oversized:
                self._process_35mm_rolls(cursor, project, project_id)
            
            # Update index data with film numbers
            updated_index = self._update_index(index_data, project.film_allocation)
            
            # Update project record with index path if available
            if index_data and "metadata" in index_data and project.output_dir:
                # Create a standard index path
                index_path = project.output_dir / f"{project.archive_id}_index.json"
                cursor.execute(
                    "UPDATE Projects SET index_path = ? WHERE project_id = ?",
                    (str(index_path), project_id)
                )
                if self.logger:
                    self.logger.film_debug(f"Updated project with index path: {index_path}")
            
            # Commit transaction
            conn.commit()
            
            if self.logger:
                self.logger.film_success("Film number allocation completed successfully")
            
            return project, updated_index
            
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            if self.logger:
                self.logger.film_error(f"Error allocating film numbers: {str(e)}")
            raise
        finally:
            # Clear current project reference
            self.current_project = None
            # Close connection
            conn.close()
    
    def _register_project(self, cursor: sqlite3.Cursor, project: Project) -> int:
        """
        Register project in the database.
        
        Args:
            cursor: Database cursor
            project: Project to register
            
        Returns:
            Project ID in the database
        """
        
        # Create data directory if it doesn't exist
        data_dir = project.project_path / ".data"
        data_dir.mkdir(exist_ok=True)
        
        if self.logger:
            self.logger.film_debug(f"Setting project data directory: {data_dir}")
            
        # Set project output directory if not already set
        if not project.output_dir:
            project.output_dir = data_dir
        
        # Insert new project with incremental run ID
        cursor.execute(
            """INSERT INTO Projects 
               (archive_id, location, doc_type, path, folderName, oversized, 
               total_pages, total_pages_with_refs, date_created, data_dir, index_path) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project.archive_id,
                project.location,
                project.doc_type,
                str(project.project_path),
                project.project_folder_name,
                project.has_oversized,
                project.total_pages,
                project.total_pages_with_refs or 0,  # Ensure not None
                datetime.now().isoformat(),
                str(data_dir),  # Use the created data directory
                "",  # We'll update this later when we have the index path
            )
        )
        project_id = cursor.lastrowid
        
        if self.logger:
            self.logger.film_info(f"Created new project with ID {project_id}")
        
        return project_id
    
    def _process_16mm_rolls(self, cursor: sqlite3.Cursor, project: Project, project_id: int) -> None:
        """
        Process 16mm rolls for film number assignment.
        
        Args:
            cursor: Database cursor
            project: Project with film allocation
            project_id: ID of the project in the database
        """
        if not project.film_allocation or not project.film_allocation.rolls_16mm:
            if self.logger:
                self.logger.film_info("No 16mm rolls to process")
            return
        
        rolls_16mm = project.film_allocation.rolls_16mm
        
        # Log statistics
        if self.logger:
            self.logger.film_info(f"Processing {len(rolls_16mm)} 16mm rolls")
            
        # Process each 16mm roll
        for roll in rolls_16mm:
            self._process_roll(cursor, roll, project_id, project.location_code)
    
    def _process_35mm_rolls(self, cursor: sqlite3.Cursor, project: Project, project_id: int) -> None:
        """
        Process 35mm document allocation requests in strict alphabetical order.
        Tries to place each document on an existing roll if it fits.
        
        Args:
            cursor: Database cursor
            project: Project with film allocation
            project_id: ID of the project in the database
        """
        if not project.film_allocation or not hasattr(project.film_allocation, 'doc_allocation_requests_35mm') or not project.film_allocation.doc_allocation_requests_35mm:
            if self.logger:
                self.logger.film_info("No 35mm document allocation requests to process")
            return
        
        # Log statistics
        if self.logger:
            self.logger.film_info(f"Processing {len(project.film_allocation.doc_allocation_requests_35mm)} document requests for 35mm film")
            
        # Get location for finding existing rolls
        location = project.location
        
        # Initialize reference info container in project
        project.reference_info = {
            'rolls': {},  # Map of roll_id to RollReferenceInfo
            'documents': {}  # Map of doc_id to DocumentReferenceInfo
        }
        
        # Dictionary to track rolls by film number for reuse
        film_number_to_roll = {}
        
        # Create a list for tracking the 35mm rolls we create
        project_rolls_35mm = []
        
        # Create a lookup to track which docs belong to which rolls (for split docs)
        doc_to_rolls = {}
        
        # Track document indices within rolls for frame numbers
        roll_doc_indices = {}
        
        # Track frame start positions for each roll
        roll_frame_positions = {}

        # Track frame end positions for each roll
        roll_frame_end_positions = {}
        
        # Use the module-level constants instead of instance attributes
        capacity_35mm = CAPACITY_35MM
        
        # Process each document allocation request in order
        # This preserves the alphabetical ordering created in FilmService
        for doc_request in project.film_allocation.doc_allocation_requests_35mm:
            doc_id = doc_request["doc_id"]
            doc_pages = doc_request["pages"]
            doc_path = doc_request["path"]
            page_range = doc_request["page_range"]
            
            if self.logger:
                self.logger.film_debug(f"Processing allocation request for document {doc_id} with {doc_pages} pages")
            
            # First try to find an active roll with enough capacity
            active_roll = self._find_active_35mm_roll(cursor, doc_pages, location)
            
            if active_roll:
                # We found an existing roll with enough space
                roll_db_id, film_number, remaining_capacity = active_roll
                
                # Get the next document index for this roll
                doc_index = self._get_last_document_index(cursor, roll_db_id) + 1
                
                # Check if we already have a project roll for this film number
                if film_number in film_number_to_roll:
                    # Reuse existing roll object
                    project_roll = film_number_to_roll[film_number]
                else:
                    # Create a new roll object for this project
                    next_roll_id = len(project_rolls_35mm) + 1
                    project_roll = FilmRoll(
                        roll_id=next_roll_id,
                        film_type=FilmType.FILM_35MM,
                        capacity=capacity_35mm,  # Use module-level constant
                        pages_remaining=remaining_capacity - doc_pages  # Update remaining space
                    )
                    project_roll.film_number = film_number
                    project_roll.db_roll_id = roll_db_id  # Store DB roll ID for reference
                    
                    # Add to tracking structures
                    film_number_to_roll[film_number] = project_roll
                    project_rolls_35mm.append(project_roll)
                
                # Add document to the project roll
                project_roll.add_document_segment(
                    doc_id=doc_id,
                    path=doc_path,
                    pages=doc_pages,
                    page_range=page_range,
                    has_oversized=True
                )
                
                # Update project roll's remaining pages
                project_roll.pages_remaining -= doc_pages
                
                # Get or initialize frame start position
                if roll_db_id not in roll_frame_positions:
                    # First try to find the highest blip and its page count
                    cursor.execute(
                        """SELECT d.blip, d.page_range_start, d.page_range_end 
                           FROM Documents d 
                           WHERE d.roll_id = ? 
                           ORDER BY d.document_id DESC LIMIT 1""",
                        (roll_db_id,)
                    )
                    result = cursor.fetchone()
                    
                    if result and result[0]:
                        try:
                            # Get the blip, page range start and end
                            highest_blip, page_start, page_end = result
                            
                            # Extract start frame from blip (format: XXXXXXX-XXXX.XXXXX)
                            frame_start_str = highest_blip.split('.')[-1]
                            frame_start = int(frame_start_str)
                            
                            # Calculate page count of last document
                            page_count = (page_end - page_start) + 1
                            
                            # Calculate next starting position by adding the page count to the start frame
                            next_frame_start = frame_start + page_count

                            if self.logger:
                                self.logger.film_debug(f"Found highest blip on roll {roll_db_id}: {highest_blip}")
                                self.logger.film_debug(f"Last document page range: {page_start}-{page_end} ({page_count} pages)")
                                self.logger.film_debug(f"Last document started at frame: {frame_start}")
                                self.logger.film_debug(f"Next document should start at frame: {next_frame_start}")
                            
                            roll_frame_positions[roll_db_id] = next_frame_start
                            # No need to set end position here as it will be calculated per document
                        except (ValueError, IndexError) as e:
                            if self.logger:
                                self.logger.film_warning(f"Error calculating next frame position: {e}, defaulting to frame 1")
                            roll_frame_positions[roll_db_id] = 1
                    else:
                        if self.logger:
                            self.logger.film_debug(f"No existing blips found for roll {roll_db_id}, starting at frame 1")
                        roll_frame_positions[roll_db_id] = 1
                
                frame_start = roll_frame_positions[roll_db_id]
                # Calculate frame_end as the last frame of this document
                frame_end = frame_start + doc_pages - 1  # Subtract 1 because end frame is inclusive

                if self.logger:
                    self.logger.film_debug(f"Using frame position: start={frame_start}, end={frame_end} for document {doc_id}")
                
                # Generate blip with correct frame start
                blip = self._generate_blip(film_number, doc_index, frame_start)
                if self.logger:
                    self.logger.film_debug(f"Generated start blip: {blip}")
                
                # Generate blip with frame end
                blipend = self._generate_blip(film_number, doc_index, frame_end)
                if self.logger:
                    self.logger.film_debug(f"Generated end blip: {blipend}")
                
                # Store blip info in reference model
                doc_info = project.reference_info['documents'].setdefault(
                    doc_id, DocumentReferenceInfo(doc_id, roll_db_id)
                )
                
                range_info = RangeReferenceInfo(page_range[0], page_range[1], len(doc_info.ranges))
                range_info.frame_start = frame_start
                range_info.blip = blip
                range_info.blipend = blipend
                doc_info.ranges.append(range_info)
                
                # Update roll usage in database
                self._update_35mm_roll_usage(cursor, roll_db_id, doc_pages)
                
                # Track which roll this doc segment is on
                if doc_id not in doc_to_rolls:
                    doc_to_rolls[doc_id] = []
                doc_to_rolls[doc_id].append((project_roll.roll_id, page_range))
                
                if self.logger:
                    self.logger.film_info(f"Added document {doc_id} with {doc_pages} pages to existing 35mm roll {film_number}")
                
                # Update frame position for next document
                old_position = roll_frame_positions[roll_db_id]
                roll_frame_positions[roll_db_id] = frame_start + doc_pages
                if self.logger:
                    self.logger.film_debug(f"Updated frame position for roll {roll_db_id}: {old_position} → {roll_frame_positions[roll_db_id]} (added {doc_pages} pages)")
                
                # After generating blip and blipend, and before updating roll usage
                # Add document to database with this roll
                cursor.execute(
                    """INSERT INTO Documents 
                       (document_name, com_id, roll_id, page_range_start, page_range_end, 
                       is_oversized, filepath, blip, blipend, blip_type) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        doc_id,
                        self._get_com_id(doc_id),
                        roll_db_id,
                        page_range[0],
                        page_range[1],
                        True,
                        str(doc_path),
                        blip,
                        blipend,
                        "35mm"  # Explicitly set as 35mm
                    )
                )
                
                # Register the roll in reference_info if not already there
                if roll_db_id not in project.reference_info['rolls']:
                    roll_info = RollReferenceInfo(roll_db_id, film_number)
                    
                    # Check if this roll was created in this project
                    cursor.execute("SELECT project_id FROM Rolls WHERE roll_id = ?", (roll_db_id,))
                    result = cursor.fetchone()
                    if result and result[0] == project_id:
                        roll_info.is_new_roll = True
                    
                    project.reference_info['rolls'][roll_db_id] = roll_info
                    if self.logger:
                        self.logger.film_debug(f"Added existing roll ID {roll_db_id} to reference_info with film number {film_number}")
            else:
                # No existing roll with enough space, create a new roll
                if self.logger:
                    self.logger.film_info(f"No active roll found for document {doc_id}, creating new roll")
                
                # Get a new film number
                film_number = self._get_next_film_number(cursor, project.location_code)
                
                # Create a new roll in database
                cursor.execute(
                    """INSERT INTO Rolls 
                       (film_number, film_type, capacity, pages_used, pages_remaining, 
                       status, project_id, creation_date) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        film_number,
                        "35mm",
                        capacity_35mm,  # Use module-level constant
                        doc_pages,
                        capacity_35mm - doc_pages,  # Use module-level constant
                        "active",
                        project_id,
                        datetime.now().isoformat()
                    )
                )
                roll_db_id = cursor.lastrowid
                
                # Initialize doc index for this new roll
                roll_doc_indices[film_number] = 1
                doc_index = 1
                
                # Create a new roll for project
                next_roll_id = len(project_rolls_35mm) + 1
                project_roll = FilmRoll(
                    roll_id=next_roll_id,
                    film_type=FilmType.FILM_35MM,
                    capacity=capacity_35mm,  # Use module-level constant
                    pages_remaining=capacity_35mm - doc_pages  # Use module-level constant
                )
                project_roll.film_number = film_number
                project_roll.db_roll_id = roll_db_id  # Store DB roll ID for reference
                
                # Add document to the project roll
                project_roll.add_document_segment(
                    doc_id=doc_id,
                    path=doc_path,
                    pages=doc_pages,
                    page_range=page_range,
                    has_oversized=True
                )
                
                # Add roll to tracking structures
                film_number_to_roll[film_number] = project_roll
                project_rolls_35mm.append(project_roll)
                
                # Add document to database
                # Get or initialize frame start position
                if roll_db_id not in roll_frame_positions:
                    # First try to find the highest blip and its page count
                    cursor.execute(
                        """SELECT d.blip, d.page_range_start, d.page_range_end 
                           FROM Documents d 
                           WHERE d.roll_id = ? 
                           ORDER BY d.document_id DESC LIMIT 1""",
                        (roll_db_id,)
                    )
                    result = cursor.fetchone()
                    
                    if result and result[0]:
                        try:
                            # Get the blip, page range start and end
                            highest_blip, page_start, page_end = result
                            
                            # Extract start frame from blip (format: XXXXXXX-XXXX.XXXXX)
                            frame_start_str = highest_blip.split('.')[-1]
                            frame_start = int(frame_start_str)
                            
                            # Calculate page count of last document
                            page_count = (page_end - page_start) + 1
                            
                            # Calculate next starting position by adding the page count to the start frame
                            next_frame_start = frame_start + page_count
                            
                            if self.logger:
                                self.logger.film_debug(f"Found highest blip on roll {roll_db_id}: {highest_blip}")
                                self.logger.film_debug(f"Last document page range: {page_start}-{page_end} ({page_count} pages)")
                                self.logger.film_debug(f"Last document started at frame: {frame_start}")
                                self.logger.film_debug(f"Next document should start at frame: {next_frame_start}")
                            
                            roll_frame_positions[roll_db_id] = next_frame_start
                        except (ValueError, IndexError) as e:
                            if self.logger:
                                self.logger.film_warning(f"Error calculating next frame position: {e}, defaulting to frame 1")
                            roll_frame_positions[roll_db_id] = 1
                    else:
                        if self.logger:
                            self.logger.film_debug(f"No existing blips found for roll {roll_db_id}, starting at frame 1")
                        roll_frame_positions[roll_db_id] = 1
                
                frame_start = roll_frame_positions[roll_db_id]
                # Calculate frame_end as the last frame of this document
                frame_end = frame_start + doc_pages - 1  # Subtract 1 because end frame is inclusive

                if self.logger:
                    self.logger.film_debug(f"Using frame position: start={frame_start}, end={frame_end} for document {doc_id}")
                
                # Generate blip with correct frame start
                blip = self._generate_blip(film_number, doc_index, frame_start)
                if self.logger:
                    self.logger.film_debug(f"Generated start blip: {blip}")
                
                # Generate blip with frame end
                blipend = self._generate_blip(film_number, doc_index, frame_end)
                if self.logger:
                    self.logger.film_debug(f"Generated end blip: {blipend}")
                
                # Store blip info in reference model
                doc_info = project.reference_info['documents'].setdefault(
                    doc_id, DocumentReferenceInfo(doc_id, roll_db_id)
                )
                
                range_info = RangeReferenceInfo(page_range[0], page_range[1], len(doc_info.ranges))
                range_info.frame_start = frame_start
                range_info.blip = blip
                range_info.blipend = blipend
                doc_info.ranges.append(range_info)
                
                cursor.execute(
                    """INSERT INTO Documents 
                       (document_name, com_id, roll_id, page_range_start, page_range_end, 
                       is_oversized, filepath, blip, blipend, blip_type) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        doc_id,
                        self._get_com_id(doc_id),
                        roll_db_id,
                        page_range[0],
                        page_range[1],
                        True,
                        str(doc_path),
                        blip,
                        blipend,
                        "35mm"  # Explicitly set as 35mm
                    )
                )
                
                # Track which roll this doc segment is on
                if doc_id not in doc_to_rolls:
                    doc_to_rolls[doc_id] = []
                doc_to_rolls[doc_id].append((project_roll.roll_id, page_range))
                
                if self.logger:
                    self.logger.film_info(f"Created new 35mm roll {film_number} and added document {doc_id}")
                
                # Update frame position for next document
                old_position = roll_frame_positions[roll_db_id]
                roll_frame_positions[roll_db_id] = frame_start + doc_pages
                if self.logger:
                    self.logger.film_debug(f"Updated frame position for roll {roll_db_id}: {old_position} → {roll_frame_positions[roll_db_id]} (added {doc_pages} pages)")
                
                # Register the new roll in reference_info
                if roll_db_id not in project.reference_info['rolls']:
                    roll_info = RollReferenceInfo(roll_db_id, film_number)
                    roll_info.is_new_roll = True  # This is a new roll created in this project
                    project.reference_info['rolls'][roll_db_id] = roll_info
                    if self.logger:
                        self.logger.film_debug(f"Added new roll ID {roll_db_id} to reference_info with film number {film_number}")
        
        # Set the 35mm rolls for the project
        project.film_allocation.rolls_35mm = project_rolls_35mm
        
        # Process split documents
        for doc_id, roll_info in doc_to_rolls.items():
            if len(roll_info) > 1:
                # This document is split across rolls
                if self.logger:
                    self.logger.film_info(f"Document {doc_id} is split across {len(roll_info)} 35mm rolls")
                
                project.film_allocation.split_documents_35mm[doc_id] = []
                
                for roll_id, page_range in roll_info:
                    # Find the roll in our project rolls
                    for roll in project_rolls_35mm:
                        if roll.roll_id == roll_id:
                            # Find the segment in this roll
                            segments = [s for s in roll.document_segments if s.doc_id == doc_id]
                            if segments:
                                segment = segments[0]
                                frame_range = None
                                if hasattr(segment, 'frame_range'):
                                    frame_range = segment.frame_range
                                
                                project.film_allocation.split_documents_35mm[doc_id].append({
                                    "roll": roll_id,
                                    "pageRange": page_range,
                                    "frameRange": frame_range
                                })
        
        # Update film allocation statistics
        if project.film_allocation:
            project.film_allocation.update_statistics()
            
            if self.logger:
                self.logger.film_success(f"35mm allocation complete")
                self.logger.film_info(f"Total 35mm rolls: {project.film_allocation.total_rolls_35mm}")
                self.logger.film_info(f"Total 35mm pages: {project.film_allocation.total_pages_35mm}")
                self.logger.film_info(f"Total split documents on 35mm: {len(project.film_allocation.split_documents_35mm)}")
        
    def _process_roll(self, cursor: sqlite3.Cursor, roll: FilmRoll, project_id: int, location_code: str) -> None:
        """
        Process a single roll for film number assignment.
        Used only for 16mm rolls now, as 35mm are handled separately.
        
        Args:
            cursor: Database cursor
            roll: Film roll to process
            project_id: Project ID in the database
            location_code: Location code for film number
        """
        # Skip if film number already assigned
        if roll.film_number is not None:
            if self.logger:
                self.logger.film_debug(f"Roll {roll.roll_id} already has film number {roll.film_number}")
            return
        
        # Skip 35mm rolls as they are now handled in _process_35mm_rolls
        if roll.film_type == FilmType.FILM_35MM:
            if self.logger:
                self.logger.film_debug(f"Skipping 35mm roll {roll.roll_id} - handled separately")
            return
        
        # Check if this is a partial roll
        if roll.is_partial:
            # Try to find a suitable temp roll
            temp_roll = self._find_suitable_temp_roll(cursor, roll.pages_used, str(roll.film_type.value))
            
            if temp_roll:
                temp_roll_id, source_roll_id, usable_capacity = temp_roll
                
                # Get new film number
                film_number = self._get_next_film_number(cursor, location_code)
                
                # Update roll with film number
                roll.film_number = film_number
                
                # Calculate remaining capacity
                remaining_capacity = usable_capacity - roll.pages_used
                
                # Insert roll record
                cursor.execute(
                    """INSERT INTO Rolls 
                       (film_number, film_type, capacity, pages_used, pages_remaining, 
                       status, project_id, creation_date, source_temp_roll_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        film_number,
                        str(roll.film_type.value),
                        usable_capacity,
                        roll.pages_used,
                        remaining_capacity,
                        "active",
                        project_id,
                        roll.creation_date,
                        temp_roll_id
                    )
                )
                roll_db_id = cursor.lastrowid
                
                # Mark temp roll as used
                self._mark_temp_roll_used(cursor, temp_roll_id, roll_db_id)
                
                # If enough remaining capacity, create new temp roll
                if roll.film_type == FilmType.FILM_16MM:
                    padding = TEMP_ROLL_PADDING_16MM
                else:
                    padding = TEMP_ROLL_PADDING_35MM
                
                usable_remainder = remaining_capacity - padding
                
                if usable_remainder >= TEMP_ROLL_MIN_USABLE_PAGES:
                    # Create new temp roll
                    new_temp_roll_id = self._create_temp_roll_from_remainder(
                        cursor, 
                        temp_roll_id, 
                        remaining_capacity, 
                        usable_remainder,
                        roll_db_id
                    )
                    
                    if new_temp_roll_id:
                        # Update roll with created temp roll ID
                        cursor.execute(
                            "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                            (new_temp_roll_id, roll_db_id)
                        )
            else:
                # No suitable temp roll, assign new film number
                film_number = self._get_next_film_number(cursor, location_code)
                roll.film_number = film_number
                
                # Add to database
                cursor.execute(
                    """INSERT INTO Rolls 
                       (film_number, film_type, capacity, pages_used, pages_remaining, 
                       status, project_id, creation_date) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        film_number,
                        str(roll.film_type.value),
                        roll.capacity,
                        roll.pages_used,
                        roll.pages_remaining,
                        "active",
                        project_id,
                        roll.creation_date
                    )
                )
                roll_db_id = cursor.lastrowid
                
                # If partial roll with enough capacity, create temp roll
                if roll.is_partial and roll.usable_capacity >= TEMP_ROLL_MIN_USABLE_PAGES:
                    new_temp_roll_id = self._create_temp_roll(
                        cursor,
                        str(roll.film_type.value),
                        roll.remaining_capacity,
                        roll.usable_capacity,
                        roll_db_id
                    )
                    
                    if new_temp_roll_id:
                        # Update roll with created temp roll ID
                        cursor.execute(
                            "UPDATE Rolls SET created_temp_roll_id = ? WHERE roll_id = ?",
                            (new_temp_roll_id, roll_db_id)
                        )
        else:
            # Full roll, assign new film number
            film_number = self._get_next_film_number(cursor, location_code)
            roll.film_number = film_number
            
            # Add to database
            cursor.execute(
                """INSERT INTO Rolls 
                   (film_number, film_type, capacity, pages_used, pages_remaining, 
                   status, project_id, creation_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    film_number,
                    str(roll.film_type.value),
                    roll.capacity,
                    roll.pages_used,
                    roll.pages_remaining,
                    "active",
                    project_id,
                    roll.creation_date
                )
            )
            roll_db_id = cursor.lastrowid
        
        # Add document segments to Documents table
        for segment in roll.document_segments:
            # Use adjusted ranges when generating blips
            # If this document has adjusted ranges, we should use them instead of the original ranges
            doc = self._find_document_by_id(segment.doc_id)
            if doc and hasattr(doc, 'references') and 'adjusted_ranges' in doc.references:
                # Map the original page range to adjusted page range
                original_start, original_end = segment.start_page, segment.end_page
                adjusted_range = None
                
                # Find matching adjusted range
                for original_range, adjusted_range_info in doc.references['adjusted_ranges'].items():
                    orig_start, orig_end = map(int, original_range.split('-'))
                    if orig_start <= original_start and orig_end >= original_end:
                        adjusted_start = adjusted_range_info['adjusted_start']
                        adjusted_pages = adjusted_range_info['adjusted_pages']
                        adjusted_end = adjusted_start + (original_end - original_start)
                        segment.start_frame = adjusted_start  # Update starting frame
                        break
            
            # Generate blip with potentially updated start_frame
            blip = self._generate_blip(film_number, segment.document_index, segment.start_frame)
            
            # Calculate page count for this segment
            page_count = (segment.end_page - segment.start_page) + 1
            
            # Generate end blip
            frame_end = segment.start_frame + page_count - 1  # Subtract 1 because end frame is inclusive
            blipend = self._generate_blip(film_number, segment.document_index, frame_end)
            
            if self.logger:
                self.logger.film_debug(f"Generated start blip: {blip} for document {segment.doc_id}")
                self.logger.film_debug(f"Generated end blip: {blipend} for document {segment.doc_id}")
            
            # Find the document in the project to get COM ID
            com_id = ""
            doc = self._find_document_by_id(segment.doc_id)
            if doc and doc.com_id:
                com_id = str(doc.com_id)  # Convert to string for DB storage
            
            # Add document to database
            cursor.execute(
                """INSERT INTO Documents 
                (document_name, com_id, roll_id, page_range_start, page_range_end, 
                is_oversized, filepath, blip, blipend, blip_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    segment.doc_id,
                    com_id,  # Use actual COM ID if found
                    roll_db_id,
                    segment.start_page,
                    segment.end_page,
                    segment.has_oversized,
                    str(segment.path),
                    blip,
                    blipend,
                    str(roll.film_type.value)  # Store film type as blip type
                )
            )
    
    def _generate_blip(self, film_number: str, doc_index: int, frame_start: int) -> str:
        """
        Generate a blip string for a document.
        
        Args:
            film_number: Film number
            doc_index: Document index on roll
            frame_start: Starting frame
            
        Returns:
            Blip string
        """
        blip = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
        if self.logger:
            self.logger.film_debug(f"_generate_blip: {film_number}-{doc_index:04d}.{frame_start:05d} (doc_index={doc_index}, frame={frame_start})")
        return blip
    
    def _get_next_film_number(self, cursor: sqlite3.Cursor, location_code: str) -> str:
        """
        Get the next available film number.
        
        Args:
            cursor: Database cursor
            location_code: Location code
            
        Returns:
            Next film number
        """
        # Default prefix based on location
        prefix = location_code
        
        # Get the highest existing number with this prefix
        cursor.execute(
            "SELECT film_number FROM Rolls WHERE film_number LIKE ? ORDER BY film_number DESC LIMIT 1",
            (f"{prefix}%",)
        )
        result = cursor.fetchone()
        
        if result:
            # Extract sequence number and increment
            current_number = result[0]
            try:
                sequence = int(current_number[1:])  # Skip prefix
                next_sequence = sequence + 1
            except (ValueError, IndexError):
                # If parsing fails, start from 1
                next_sequence = 1
        else:
            # No existing numbers, start from 1
            next_sequence = 1
        
        # Format new film number
        film_number = f"{prefix}{next_sequence:07d}"
        
        if self.logger:
            self.logger.film_debug(f"Generated next film number: {film_number}")
        
        return film_number
    
    def _find_suitable_temp_roll(self, cursor: sqlite3.Cursor, pages_needed: int, film_type: str) -> Optional[Tuple[int, int, int]]:
        """
        Find a suitable temporary roll with enough capacity.
        
        Args:
            cursor: Database cursor
            pages_needed: Number of pages needed
            film_type: Type of film
            
        Returns:
            Tuple of (temp_roll_id, source_roll_id, usable_capacity) if found, None otherwise
        """
        cursor.execute(
            """SELECT temp_roll_id, source_roll_id, usable_capacity 
               FROM TempRolls 
               WHERE film_type = ? AND status = 'available' AND usable_capacity >= ? 
               ORDER BY usable_capacity ASC 
               LIMIT 1""",
            (film_type, pages_needed)
        )
        result = cursor.fetchone()
        
        if result:
            temp_roll_id, source_roll_id, usable_capacity = result
            
            if self.logger:
                self.logger.film_debug(f"Found suitable temp roll: ID={temp_roll_id}, capacity={usable_capacity}")
            
            return temp_roll_id, source_roll_id, usable_capacity
        
        return None
    
    def _mark_temp_roll_used(self, cursor: sqlite3.Cursor, temp_roll_id: int, used_by_roll_id: int) -> None:
        """
        Mark a temporary roll as used.
        
        Args:
            cursor: Database cursor
            temp_roll_id: ID of the temp roll
            used_by_roll_id: ID of the roll that used this temp roll
        """
        cursor.execute(
            "UPDATE TempRolls SET status = 'used', used_by_roll_id = ? WHERE temp_roll_id = ?",
            (used_by_roll_id, temp_roll_id)
        )
        
        if self.logger:
            self.logger.film_debug(f"Marked temp roll {temp_roll_id} as used by roll {used_by_roll_id}")
    
    def _create_temp_roll_from_remainder(self, cursor: sqlite3.Cursor, original_temp_roll_id: int, 
                                 remaining_capacity: int, usable_capacity: int,
                                 roll_id: int) -> Optional[int]:
        """
        Create a new temporary roll from the remainder of another temp roll.
        
        Args:
            cursor: Database cursor
            original_temp_roll_id: ID of the original temp roll
            remaining_capacity: Total remaining capacity
            usable_capacity: Usable capacity (after padding)
            roll_id: ID of the roll that used the original temp roll
            
        Returns:
            ID of the new temp roll if created, None otherwise
        """
        try:
            # Get original temp roll info
            cursor.execute(
                "SELECT film_type FROM TempRolls WHERE temp_roll_id = ?",
                (original_temp_roll_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                if self.logger:
                    self.logger.film_warning(f"Original temp roll {original_temp_roll_id} not found")
                return None
            
            film_type = result[0]
            
            # Create new temp roll
            cursor.execute(
                """INSERT INTO TempRolls 
                   (film_type, capacity, usable_capacity, status, creation_date, source_roll_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    film_type,
                    remaining_capacity,
                    usable_capacity,
                    "available",
                    datetime.now().isoformat(),
                    roll_id
                )
            )
            new_temp_roll_id = cursor.lastrowid
            
            if self.logger:
                self.logger.film_debug(f"Created new temp roll {new_temp_roll_id} with {usable_capacity} usable capacity")
            
            return new_temp_roll_id
            
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error creating temp roll from remainder: {str(e)}")
            return None
    
    def _create_temp_roll(self, cursor: sqlite3.Cursor, film_type: str, capacity: int, 
                  usable_capacity: int, source_roll_id: int) -> Optional[int]:
        """
        Create a new temporary roll.
        
        Args:
            cursor: Database cursor
            film_type: Type of film
            capacity: Total capacity
            usable_capacity: Usable capacity (after padding)
            source_roll_id: ID of the source roll
            
        Returns:
            ID of the new temp roll if created, None otherwise
        """
        try:
            cursor.execute(
                """INSERT INTO TempRolls 
                   (film_type, capacity, usable_capacity, status, creation_date, source_roll_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    film_type,
                    capacity,
                    usable_capacity,
                    "available",
                    datetime.now().isoformat(),
                    source_roll_id
                )
            )
            temp_roll_id = cursor.lastrowid
            
            if self.logger:
                self.logger.film_debug(f"Created temp roll {temp_roll_id} with {usable_capacity} usable capacity")
            
            return temp_roll_id
            
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error creating temp roll: {str(e)}")
            return None
    
    def _find_active_35mm_roll(self, cursor: sqlite3.Cursor, pages_needed: int, location: str = None) -> Optional[Tuple[int, str, int]]:
        """
        Find an active 35mm roll with enough capacity across all projects.
        
        Args:
            cursor: Database cursor
            pages_needed: Number of pages needed
            location: Optional location filter (can be None to search all locations)
            
        Returns:
            Tuple of (roll_id, film_number, remaining_capacity) if found, None otherwise
        """
        query = """
            SELECT r.roll_id, r.film_number, r.pages_remaining
            FROM Rolls r
            JOIN Projects p ON r.project_id = p.project_id
            WHERE r.film_type = '35mm' 
            AND r.status = 'active' 
            AND r.pages_remaining >= ?
        """
        
        params = [pages_needed]
        
        # Only filter by location if specified
        if location:
            query += " AND p.location = ?"
            params.append(location)
        
        query += " ORDER BY r.creation_date DESC LIMIT 1"
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            roll_id, film_number, remaining_capacity = result
            
            if self.logger:
                self.logger.film_debug(f"Found active 35mm roll across projects: ID={roll_id}, film_number={film_number}, remaining={remaining_capacity}")
            
                # Add this to debug roll history and document assignments
                cursor.execute(
                    """SELECT d.document_name, d.blip, d.page_range_start, d.page_range_end 
                       FROM Documents d 
                       WHERE d.roll_id = ? 
                       ORDER BY d.blip""",
                    (roll_id,)
                )
                docs = cursor.fetchall()
                self.logger.film_debug(f"Roll {roll_id} (film {film_number}) has {len(docs)} existing documents:")
                for doc in docs:
                    doc_name, doc_blip, page_start, page_end = doc
                    self.logger.film_debug(f"  - {doc_name}: {doc_blip} (pages {page_start}-{page_end})")
            
            return roll_id, film_number, remaining_capacity
        
        return None
    
    def _update_35mm_roll_usage(self, cursor: sqlite3.Cursor, roll_id: int, pages_used: int) -> None:
        """
        Update usage statistics for an active 35mm roll.
        
        Args:
            cursor: Database cursor
            roll_id: ID of the roll
            pages_used: Number of pages used
        """
        # Get current usage
        cursor.execute(
            "SELECT pages_used, pages_remaining FROM Rolls WHERE roll_id = ?",
            (roll_id,)
        )
        result = cursor.fetchone()
        
        if result:
            current_used, current_remaining = result
            
            # Update usage
            new_used = current_used + pages_used
            new_remaining = current_remaining - pages_used
            
            cursor.execute(
                "UPDATE Rolls SET pages_used = ?, pages_remaining = ? WHERE roll_id = ?",
                (new_used, new_remaining, roll_id)
            )
            
            if self.logger:
                self.logger.film_debug(f"Updated 35mm roll {roll_id}: used={new_used}, remaining={new_remaining}")
    
    def _update_index(self, index_data: Dict[str, Any], film_allocation: FilmAllocation) -> Dict[str, Any]:
        """
        Update index data with film numbers.
        
        Args:
            index_data: Index data to update
            film_allocation: Film allocation with film numbers
            
        Returns:
            Updated index data
        """
        if self.logger:
            self.logger.film_info("Updating index data with film numbers")
        
        if not index_data or "index" not in index_data:
            if self.logger:
                self.logger.film_error("Invalid index data structure")
            return index_data
        
        # Map roll_id to film_number
        roll_film_numbers = {}
        
        # Extract film numbers from 16mm rolls
        for roll in film_allocation.rolls_16mm:
            if roll.film_number:
                roll_film_numbers[str(roll.roll_id)] = roll.film_number
        
        # Extract film numbers from 35mm rolls
        for roll in film_allocation.rolls_35mm:
            if roll.film_number:
                roll_film_numbers[str(roll.roll_id)] = roll.film_number
        
        if self.logger:
            self.logger.film_debug(f"Extracted {len(roll_film_numbers)} film numbers from rolls")
        
        # Update each index entry
        updated_count = 0
        missing_count = 0
        
        for entry_idx, entry in enumerate(index_data["index"]):
            if len(entry) >= 4 and entry[2]:
                roll_id, frame_start, frame_end = entry[2]
                roll_id_str = str(roll_id)
                
                # Get document index (use 5th element if available, default to 1)
                doc_index = entry[4] if len(entry) >= 5 else 1
                
                # Find corresponding film_number
                if roll_id_str in roll_film_numbers:
                    film_number = roll_film_numbers[roll_id_str]
                    
                    # Update the final_index with blip
                    blip = self._generate_blip(film_number, doc_index, frame_start)
                    entry[3] = blip
                    updated_count += 1
                else:
                    if self.logger:
                        self.logger.film_warning(f"No film number found for roll {roll_id_str}")
                    missing_count += 1
        
        if self.logger:
            self.logger.film_success(f"Updated {updated_count} index entries with film numbers")
            if missing_count > 0:
                self.logger.film_warning(f"Could not update {missing_count} index entries due to missing film numbers")
        
        return index_data
    
    def _find_document_by_id(self, doc_id: str) -> Optional[Document]:
        """
        Find a document by its ID in the current project.
        
        Args:
            doc_id: Document ID to search for
            
        Returns:
            Document object if found, None otherwise
        """
        if not hasattr(self, 'current_project') or not self.current_project:
            return None
            
        for doc in self.current_project.documents:
            if doc.doc_id == doc_id:
                return doc
                
        return None

    def _get_com_id(self, doc_id: str) -> str:
        """Get COM ID for a document if available."""
        doc = self._find_document_by_id(doc_id)
        if doc and doc.com_id:
            return str(doc.com_id)
        return ""

    def find_35mm_document_for_range(self, cursor: sqlite3.Cursor, doc_id: str, range_start: int, range_end: int) -> Optional[Dict[str, Any]]:
        """
        Find a document on 35mm roll that matches the specified page range.
        
        Args:
            cursor: Database cursor
            doc_id: Document ID
            range_start: Start of the page range
            range_end: End of the page range
            
        Returns:
            Dictionary with document info if found, None otherwise
        """
        cursor.execute(
            """SELECT d.document_id, d.blip, r.film_number, r.roll_id
            FROM Documents d
            JOIN Rolls r ON d.roll_id = r.roll_id
            WHERE d.document_name = ?
            AND d.blip_type = '35mm'
            AND d.page_range_start <= ?
            AND d.page_range_end >= ?
            ORDER BY ABS(d.page_range_start - ?) + ABS(d.page_range_end - ?) ASC
            LIMIT 1""",
            (doc_id, range_start, range_end, range_start, range_end)
        )
        result = cursor.fetchone()
        
        if result:
            doc_id, blip, film_number, roll_id = result
            
            # Parse the original blip to get components
            # Format: XXXXXXX-XXXX.XXXXX (film_number-doc_index.frame_start)
            try:
                # Extract the parts (film_number, doc_index, frame_start)
                parts = blip.split('-')
                film_num = parts[0]
                rest = parts[1].split('.')
                doc_index = rest[0]
                frame_start = int(rest[1])
                
                # Calculate frame for this specific range
                # We need to compute a new frame_start based on the range position
                cursor.execute(
                    """SELECT page_range_start, page_range_end FROM Documents 
                    WHERE document_name = ? AND blip_type = '35mm'
                    ORDER BY page_range_start ASC""",
                    (doc_id,)
                )
                all_ranges = cursor.fetchall()
                
                # Find where this range is in the sequence and calculate a new frame
                frame_offset = 0
                for idx, (db_start, db_end) in enumerate(all_ranges):
                    if db_start <= range_start and db_end >= range_end:
                        # This is our range - calculate frame based on position in document
                        new_frame = frame_start + frame_offset
                        # Create a new range-specific blip
                        range_blip = f"{film_num}-{doc_index}.{new_frame:05d}"
                        
                        if self.logger:
                            self.logger.film_debug(f"Generated range-specific blip {range_blip} for range {range_start}-{range_end}")
                        
                        return {
                            "document_id": doc_id,
                            "blip": range_blip,  # Use the range-specific blip
                            "film_number": film_number,
                            "roll_id": roll_id
                        }
                
                # If we didn't find a specific match, use the original blip
                return {
                    "document_id": doc_id,
                    "blip": blip,
                    "film_number": film_number,
                    "roll_id": roll_id
                }
                
            except Exception as e:
                if self.logger:
                    self.logger.film_warning(f"Error parsing blip {blip}: {str(e)}")
                
                # Return original info if parsing fails
                return {
                    "document_id": doc_id,
                    "blip": blip,
                    "film_number": film_number,
                    "roll_id": roll_id
                }
        
        return None

    def get_blip_for_document_range(self, cursor: sqlite3.Cursor, doc_id: str, range_start: int, range_end: int) -> Optional[Dict[str, Any]]:
        """
        Get the blip information for a specific document range, with frame position 
        calculated based on the position of the oversized page within the document.
        """
        # Find the basic document information first
        cursor.execute(
            """SELECT d.document_id, d.blip, r.film_number, r.roll_id
            FROM Documents d
            JOIN Rolls r ON d.roll_id = r.roll_id
            WHERE d.document_name = ?
            AND d.blip_type = '35mm'
            LIMIT 1""",
            (doc_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            if self.logger:
                self.logger.film_warning(f"No 35mm document found for document {doc_id}")
            return None
        
        doc_id_db, base_blip, film_number, roll_id = result
        
        # Parse the base blip
        try:
            parts = base_blip.split('-')
            film_num = parts[0]
            rest = parts[1].split('.')
            doc_index = rest[0]
            base_frame = int(rest[1])
            
            # Find the document to get its oversized page information
            document = self._find_document_by_id(doc_id)
            if not document or not hasattr(document, 'dimensions'):
                return {
                    "blip_35mm": base_blip,
                    "film_number_35mm": film_number,
                    "roll_id_35mm": roll_id
                }
            
            # Get all the oversized page indices in this document
            oversized_pages = [dim[2]+1 for dim in document.dimensions]  # +1 to convert to 1-indexed
            
            # Find how many oversized pages come before our target range
            pages_before = sum(1 for p in oversized_pages if p < range_start)
            
            # Calculate the frame position based on the base frame plus offset
            target_frame = base_frame + pages_before
            
            # Generate the range-specific blip
            range_blip = f"{film_num}-{doc_index}.{target_frame:05d}"
            
            if self.logger:
                self.logger.film_debug(f"Calculated range-specific blip {range_blip} for document {doc_id} range {range_start}-{range_end}")
                self.logger.film_debug(f"  Base blip: {base_blip}, Pages before: {pages_before}")
            
            return {
                "blip_35mm": range_blip,
                "film_number_35mm": film_number,
                "roll_id_35mm": roll_id
            }
        except Exception as e:
            if self.logger:
                self.logger.film_warning(f"Error calculating range-specific blip: {str(e)}")
            
            # Return the base blip if calculation fails
            return {
                "blip_35mm": base_blip,
                "film_number_35mm": film_number,
                "roll_id_35mm": roll_id
            }

    def prepare_reference_sheet_data(self, project):
        """Prepare data for reference sheets using accurate roll information."""
        results = {}
        
        # Use reference info if available
        if hasattr(project, 'reference_info') and project.reference_info and project.reference_info['documents']:
            if self.logger:
                self.logger.film_info(f"Using reference info model with {len(project.reference_info['documents'])} documents")
                
            for doc_id, doc_info in project.reference_info['documents'].items():
                results[doc_id] = []
                
                # Get the roll info
                roll_info = project.reference_info['rolls'].get(doc_info.roll_id)
                if not roll_info:
                    if self.logger:
                        self.logger.film_warning(f"No roll info found for document {doc_id} roll {doc_info.roll_id}")
                    continue
                    
                # Add each range with its precise blip
                for range_info in doc_info.ranges:
                    results[doc_id].append({
                        'range': (range_info.range_start, range_info.range_end),
                        'blip_35mm': range_info.blip,
                        'film_number_35mm': roll_info.film_number,
                        'reference_position': range_info.position + 1
                    })
        else:
            # If no reference info, query database directly
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                
                if self.logger:
                    self.logger.film_info("No reference info model found, querying database directly")
                    
                for document in project.documents:
                    if not document.has_oversized or not document.ranges:
                        continue
                        
                    doc_id = document.doc_id
                    results[doc_id] = []
                    
                    # Process each range
                    for i, (range_start, range_end) in enumerate(document.ranges):
                        # Query for accurate blip information
                        cursor.execute(
                            """SELECT r.film_number, d.blip
                            FROM Documents d
                            JOIN Rolls r ON d.roll_id = r.roll_id
                            WHERE d.document_name = ?
                            AND d.blip_type = '35mm'
                            LIMIT 1""",
                            (doc_id,)
                        )
                        result = cursor.fetchone()
                        
                        if result:
                            film_number, blip = result
                            results[doc_id].append({
                                'range': (range_start, range_end),
                                'blip_35mm': blip,
                                'film_number_35mm': film_number,
                                'reference_position': i + 1
                            })
                        else:
                            if self.logger:
                                self.logger.film_warning(f"No entry found in database for document {doc_id}")
            finally:
                conn.close()
                
        return results

    def _get_last_document_index(self, cursor: sqlite3.Cursor, roll_id: int) -> int:
        """
        Get the highest document index used on a roll.
        
        Args:
            cursor: Database cursor
            roll_id: Roll ID
            
        Returns:
            The highest document index found, or 0 if none
        """
        # Count documents on this roll to get a simple increasing index
        cursor.execute(
            "SELECT COUNT(*) FROM Documents WHERE roll_id = ?",
            (roll_id,)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    
    def get_35mm_blip_for_range(self, doc_id: str, range_start: int, range_end: int) -> Optional[Dict[str, Any]]:
        """
        Get the 35mm blip for a specific document range.
        
        Args:
            doc_id: Document ID
            range_start: Start of the page range
            range_end: End of the page range
            
        Returns:
            Dictionary with blip info if found, None otherwise
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            return self.find_35mm_document_for_range(cursor, doc_id, range_start, range_end)
        finally:
            conn.close()

    def _calculate_frame_position(self, document, roll, document_index):
        """
        Calculate the frame position for a document on a roll,
        accounting for reference sheets and adjusted page ranges.
        """
        # Get current frame position on roll
        current_frame = roll.current_frame_position if hasattr(roll, 'current_frame_position') else 1
        
        # Store the starting frame position for this document
        start_frame = current_frame
        
        # Get document page count, including reference sheets if available
        page_count = document.pages
        if hasattr(document, 'total_pages_with_refs'):
            page_count = document.total_pages_with_refs
        
        # Update frame position on roll
        new_frame = current_frame + page_count
        roll.current_frame_position = new_frame
        
        self.logger.film_debug(f"Using frame start position: {start_frame} for document {document.doc_id}")
        
        return start_frame