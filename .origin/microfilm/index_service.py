"""
Index service module for handling microfilm index operations.

This module provides a service layer for index-related operations,
including initializing and updating indexes for tracking document
locations on film rolls.
"""

import os
import math
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
import xlwings as xw
from pathlib import Path

from models import Project, FilmAllocation, FilmRoll, FilmType

class IndexService:
    """
    Service for handling all index-related operations.
    
    This service handles the initialization and updating of indexes
    for tracking document locations on film rolls.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the index service.
        
        Args:
            logger: Optional logger instance.
        """
        self.logger = logger
    
    def initialize_index(self, project: Project) -> Dict[str, Any]:
        """
        Initialize index for tracking document locations on film rolls.
        Only processes 16mm rolls (35mm rolls are intentionally excluded).
        
        Args:
            project: The project with film allocation
            
        Returns:
            dict: Index data
        """
        if self.logger:
            self.logger.section("Index Initialization")
            self.logger.film_info("Starting index initialization")
        
        # Check if the project has a film allocation
        if not project.film_allocation:
            if self.logger:
                self.logger.film_error("No film allocation found in project")
            return {
                "metadata": {
                    "creation_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "error": "No film allocation"
                },
                "index": []
            }
        
        # Initialize index data
        index_data = {
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "version": "1.0",
                "archive_id": project.archive_id,
                "project_name": project.project_folder_name
            },
            "index": []
        }
        
        try:
            # Create a dictionary to store doc_id to COM ID mappings
            doc_id_to_comid = {}
            
            # Try to read the COM list Excel file if available
            if project.comlist_path and os.path.exists(project.comlist_path):
                if self.logger:
                    self.logger.film_info(f"Reading COM list from {project.comlist_path}")
                
                try:
                    # Try to read the Excel file using xlwings
                    wb = None
                    try:
                        # Try to use already open workbook
                        wb = xw.books.active
                        if Path(wb.fullname).resolve() != Path(project.comlist_path).resolve():
                            wb = xw.Book(str(project.comlist_path))
                    except Exception:
                        # Open the workbook directly
                        wb = xw.Book(str(project.comlist_path))
                    
                    # Get the first worksheet
                    ws = wb.sheets[0]
                    
                    # Get data range with potential barcode and ComID values
                    used_range = ws.used_range
                    if used_range:
                        data = used_range.value
                        
                        # Skip header row if exists
                        start_row = 1 if isinstance(data[0][0], str) and not data[0][0].isdigit() else 0
                        
                        # Extract barcode and ComID pairs
                        for i in range(start_row, len(data)):
                            if i < len(data) and len(data[i]) >= 2:
                                barcode = str(data[i][0]) if data[i][0] is not None else None
                                com_id = data[i][1]
                                
                                # Convert ComID to integer if possible
                                if com_id is not None:
                                    try:
                                        # Handle case where Excel returns a float
                                        if isinstance(com_id, float) and com_id.is_integer():
                                            com_id = int(com_id)
                                        else:
                                            com_id = int(com_id)
                                        
                                        if barcode and com_id:
                                            doc_id_to_comid[barcode] = com_id
                                    except (ValueError, TypeError):
                                        if self.logger:
                                            self.logger.film_warning(f"Invalid ComID value for barcode {barcode}: {com_id}")
                    
                    if self.logger:
                        self.logger.film_success(f"Loaded {len(doc_id_to_comid)} barcode to COM ID mappings")
                    
                    # Close Excel if we opened it
                    if wb:
                        wb.app.quit()
                        
                except FileNotFoundError:
                    if self.logger:
                        self.logger.film_warning(f"COM list Excel file not found at {project.comlist_path}")
                except Exception as e:
                    if self.logger:
                        self.logger.film_error(f"Error reading COM list Excel file: {str(e)}")
                    # Try to close Excel if it was opened
                    if 'wb' in locals() and wb:
                        try:
                            wb.app.quit()
                        except:
                            pass
            else:
                if self.logger:
                    self.logger.film_warning("No COM list Excel file provided or file not found")
            
            # Process 16mm film rolls
            if self.logger:
                self.logger.film_info("Processing 16mm film rolls for index")
            
            # Iterate through 16mm film rolls
            for roll in project.film_allocation.rolls_16mm:
                roll_id = roll.roll_id
                
                # Iterate through document segments in this roll
                for segment in roll.document_segments:
                    doc_id = segment.doc_id
                    
                    # Get document index (position on this roll)
                    doc_index = segment.document_index
                    
                    # Get frame range for this segment
                    frame_range = segment.frame_range
                    
                    # Get COM ID from the mapping or use a placeholder
                    com_id = doc_id_to_comid.get(doc_id, None)
                    
                    # If COM ID is not found, generate a placeholder
                    if com_id is None:
                        # Log document not found in COM list
                        if self.logger:
                            self.logger.film_warning(f"Document {doc_id} not found in COM list Excel file")
                        # Use a placeholder COM ID (negative roll_id to avoid conflicts)
                        com_id = -roll_id
                    
                    # Update document COM ID if available
                    for doc in project.documents:
                        if doc.doc_id == doc_id and com_id is not None:
                            doc.com_id = com_id
                    
                    # Create initial index array with [roll_id, frameRange_start, frameRange_end]
                    initial_index = [roll_id, frame_range[0], frame_range[1]]
                    
                    # Create index entry with document index
                    index_entry = [
                        doc_id,                # Document ID
                        com_id,                # COM ID
                        initial_index,         # Initial index [roll_id, frameRange_start, frameRange_end]
                        None,                  # Final index (to be filled later)
                        doc_index              # Document index (position on roll)
                    ]
                    
                    # Add to index
                    index_data["index"].append(index_entry)
                    
                    if self.logger:
                        self.logger.film_debug(f"Added index entry for document {doc_id} with COM ID {com_id} and initial index {initial_index}")
            
            if self.logger:
                self.logger.film_success(f"Index initialization completed with {len(index_data['index'])} entries")
        
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error initializing index: {str(e)}")
            
            index_data = {
                "metadata": {
                    "creation_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "error": str(e)
                },
                "index": []
            }
        
        return index_data
    
    def update_index(self, project: Project, index_data: Dict[str, Any], film_numbers: Dict[str, str]) -> Dict[str, Any]:
        """
        Update index with final film numbers.
        
        Args:
            project: Project with film allocation
            index_data: Initial index data
            film_numbers: Dictionary mapping roll IDs to film numbers
            
        Returns:
            Updated index data
        """
        if self.logger:
            self.logger.section("Index Update")
            self.logger.film_info("Updating index with film numbers")
        
        updated_count = 0
        missing_count = 0
        
        try:
            # Create dictionary for roll sources if partial rolls were used
            roll_sources = {}
            
            # Process each index entry
            for entry_idx, entry in enumerate(index_data["index"]):
                if len(entry) >= 4 and entry[2]:
                    # Get roll_id and frame range from initial_index
                    roll_id, frame_start, frame_end = entry[2]
                    roll_id_str = str(roll_id)
                    
                    # Get document index (use 5th element if available, default to 1)
                    doc_index = entry[4] if len(entry) >= 5 else 1
                    
                    # Find corresponding film_number in film_numbers
                    if roll_id_str in film_numbers:
                        film_number = film_numbers[roll_id_str]
                        source_info = roll_sources.get(roll_id_str, "direct")
                        
                        # Update the final_index
                        if film_number:
                            # Use format: film_number-document_index(4 digits)-frame_start(5 digits)
                            entry[3] = f"{film_number}-{doc_index:04d}.{frame_start:05d}"
                            updated_count += 1
                            
                            if self.logger:
                                self.logger.film_debug(f"Updated index for document {entry[0]}: {entry[3]} (source: {source_info})")
                        else:
                            if self.logger:
                                self.logger.film_warning(f"No film number found for roll {roll_id_str} containing document {entry[0]}")
                            missing_count += 1
                    else:
                        if self.logger:
                            self.logger.film_warning(f"Roll {roll_id_str} not found in film_numbers for document {entry[0]}")
                        missing_count += 1
            
            # Update metadata
            index_data["metadata"]["update_date"] = datetime.now().isoformat()
            index_data["metadata"]["updated_count"] = updated_count
            index_data["metadata"]["missing_count"] = missing_count
            
            if self.logger:
                self.logger.film_success(f"Index update completed with {updated_count} entries updated, {missing_count} entries missing film numbers")
        
        except Exception as e:
            if self.logger:
                self.logger.film_error(f"Error updating index: {str(e)}")
            
            index_data["metadata"]["error"] = str(e)
        
        return index_data 