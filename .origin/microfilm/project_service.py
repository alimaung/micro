"""
Project service module for handling microfilm project operations.

This module provides a service layer for project-related operations, 
including initialization, detection, and management. It's designed to be 
reusable across different interfaces (CLI, web, etc.).
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from models import Project
from exceptions import (
    ProjectError, ProjectInitializationError, ProjectLoadError, 
    ProjectExportError, DirectoryError, FileError, ValidationError
)


class ProjectService:
    """
    Service for handling all project-related operations.
    
    This service abstracts all logic related to project initialization,
    detection, management, and serialization, making it reusable across
    different interfaces like CLI, web applications, etc.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the project service.
        
        Args:
            logger: Optional logger instance. If None, logging will be disabled.
                   Can be a standard logging.Logger or a FilmLogger instance.
        """
        self.logger = logger
    
    def initialize_project(self, path: Union[str, Path]) -> Project:
        """
        Initialize a project from a file system path.
        
        This method can handle both scenarios:
        1. User selects the project folder directly
        2. User selects the document subfolder
        
        Args:
            path: Path to either the project folder or document subfolder
            
        Returns:
            Initialized Project object
            
        Raises:
            ValidationError: If the project cannot be initialized
        """
        self.logger.section("Initializing Project")
        try:
            # Convert to Path object if string
            if isinstance(path, str):
                path = Path(path)
            
            # Validate the path
            if not path.exists():
                raise ValidationError(f"Path does not exist: {path}")
            if not path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")
            
            # Determine if path is project folder or document subfolder
            folder_name = path.name
            self.logger.project_info(f"Processing path: {path}, folder name: {folder_name}")
            
            # Try to extract metadata from the folder name
            project_metadata = self._try_extract_metadata(folder_name)
            
            if project_metadata:
                # This is likely a project folder
                self.logger.project_info(f"Path appears to be a project folder")
                archive_id, location, doc_type = project_metadata
                
                # Create project with this as project folder
                project = Project(
                    archive_id=archive_id,
                    location=location,
                    project_path=path,
                    project_folder_name=folder_name,
                    doc_type=doc_type
                )
                
                # Find document subfolder
                doc_folder = self._find_document_folder(path, archive_id)
                if doc_folder:
                    project.document_folder_path = doc_folder
                    project.document_folder_name = doc_folder.name
                    self.logger.project_info(f"Found document folder: {doc_folder.name}")
                else:
                    self.logger.project_warning(f"No document subfolder found in project folder")
            else:
                # This might be a document subfolder, check parent
                parent_path = path.parent
                parent_name = parent_path.name
                
                parent_metadata = self._try_extract_metadata(parent_name)
                if parent_metadata:
                    # This is a document subfolder
                    self.logger.project_info(f"Path appears to be a document subfolder")
                    archive_id, location, doc_type = parent_metadata
                    
                    # Create project
                    project = Project(
                        archive_id=archive_id,
                        location=location,
                        project_path=parent_path,
                        project_folder_name=parent_name,
                        document_folder_path=path,
                        document_folder_name=folder_name,
                        doc_type=doc_type
                    )
                else:
                    # Neither folder has metadata, can't initialize
                    raise ValidationError(
                        f"Could not extract project metadata from folder name: {folder_name} "
                        f"or parent folder: {parent_name}"
                    )
            
            # Find COM list file
            comlist_path = self._find_comlist_file(project.project_path, project.archive_id)
            if comlist_path:
                project.comlist_path = comlist_path
                self.logger.project_info(f"Found COM list file: {comlist_path.name}")
            
            self.logger.project_info(f"Project initialized: {project.archive_id} ({project.location})")
            return project
            
        except ValidationError as e:
            self.logger.error(f"Validation error during project initialization: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Error initializing project: {str(e)}"
            self.logger.error(error_msg)
            raise ProjectInitializationError(error_msg)
    
    def _try_extract_metadata(self, folder_name: str) -> Optional[Tuple[str, str, str]]:
        """
        Try to extract project metadata from a folder name.
        
        Args:
            folder_name: Name of the folder to extract metadata from
            
        Returns:
            Tuple of (archive_id, location, doc_type) if successful, None otherwise
        """
        try:
            return self._extract_metadata_from_folder_name(folder_name)
        except ValidationError:
            return None
    
    def _extract_metadata_from_folder_name(self, folder_name: str) -> Tuple[str, str, str]:
        """
        Extract archive ID, location, and document type from folder name.
        
        Expected format: RRDxxx-xxxx_Location_DocType
        Example: RRD018-2024_OU_FAIR
        
        Args:
            folder_name: Name of the folder to extract metadata from
            
        Returns:
            Tuple of (archive_id, location, doc_type)
            
        Raises:
            ValidationError: If the folder name doesn't match the expected format
        """
        # Regular expression to match the expected format
        pattern = r'^(RRD\d{3}-\d{4})_([A-Z]{2})_(.+)$'
        match = re.match(pattern, folder_name)
        
        if not match:
            # Try alternative pattern without document type
            alt_pattern = r'^(RRD\d{3}-\d{4})_([A-Z]{2})$'
            alt_match = re.match(alt_pattern, folder_name)
            
            if alt_match:
                archive_id, location = alt_match.groups()
                doc_type = ""
            else:
                raise ValidationError(f"Invalid folder name format: {folder_name}. "
                                f"Expected format: RRDxxx-xxxx_Location_DocType")
        else:
            archive_id, location, doc_type = match.groups()
        
        # Validate location
        if location not in ['OU', 'DW'] and self.logger:
            self.logger.project_warning(f"Unexpected location code: {location}. Expected 'OU' or 'DW'.")

        return archive_id, location, doc_type
    
    def _find_document_folder(self, project_path: Path, archive_id: str) -> Optional[Path]:
        """
        Find the document subfolder within a project folder using multiple detection strategies.
        
        Args:
            project_path: Path to the project folder
            archive_id: Archive ID like "RRD018-2024"
            
        Returns:
            Path to the document subfolder if found, None otherwise
        """
        # Strategy 1: Look for folder with "PDFs zu" in the name
        for item in project_path.iterdir():
            if item.is_dir() and "PDFs zu" in item.name:
                return item
        
        # Strategy 2: Look for folder containing the archive ID
        for item in project_path.iterdir():
            if item.is_dir() and archive_id in item.name:
                return item
        
        # Strategy 3: Look for a folder that contains PDF files
        pdf_folders = []
        for item in project_path.iterdir():
            if item.is_dir():
                # Check if this folder contains PDFs
                pdf_files = list(item.glob("*.pdf"))
                if pdf_files:
                    pdf_folders.append((item, len(pdf_files)))
        
        # If we found folders with PDFs, return the one with the most PDFs
        if pdf_folders:
            # Sort by number of PDFs (descending)
            pdf_folders.sort(key=lambda x: x[1], reverse=True)
            return pdf_folders[0][0]  # Return folder with most PDFs
        
        # No document folder found
        return None
    
    def _find_comlist_file(self, folder_path: Path, archive_id: str) -> Optional[Path]:
        """
        Find the COM list Excel file in the given folder.
        
        Args:
            folder_path: Path to the folder to search in
            archive_id: Archive ID to look for in filenames
            
        Returns:
            Path to the COM list file if found, None otherwise
        """
        try:
            # Look for Excel files in the folder
            excel_files = list(folder_path.glob("*.xls*"))
            
            if not excel_files:
                self.logger.project_warning(f"No Excel files found in {folder_path}")
                return None
            
            # Create regex pattern to match the archive ID
            pattern = re.compile(re.escape(archive_id), re.IGNORECASE)
            
            # Look for files containing the archive ID using regex
            matching_files = [f for f in excel_files if pattern.search(f.name)]
            
            if matching_files:
                self.logger.project_info(f"Found COM list file: {matching_files[0]}")
                return matching_files[0]
            
            # If no specific match, return the first Excel file
            if self.logger:
                self.logger.project_warning(f"No COM list file found with archive ID {archive_id}. "
                                       f"Using first Excel file: {excel_files[0]}")
            return excel_files[0]
            
        except Exception as e:
            self.logger.error(f"Error finding COM list file: {str(e)}")
            return None
        
    def configure_logger(self, project: Project, logger):
        """
        Configure the logger to save logs in the project directory.
        """
        if project.project_path:
            project_log_dir = os.path.join(str(project.project_path), '.logs')
            logger.parent_folder = project_log_dir
            logger.project_info(f"Logs will be saved to: {project_log_dir}")
            logger.save_log_file(archive_id=project.archive_id)
