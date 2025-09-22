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
            self.logger.project_error(f"Validation error during project initialization: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Error initializing project: {str(e)}"
            self.logger.project_error(error_msg)
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
        Find the document subfolder using enhanced two-layer detection strategy.
        
        Layer 1: String detection (pdf|archive_id -> importiert -> any folder)
        Layer 2: File validation for confirmation and conflict resolution
        
        Args:
            project_path: Path to the project folder
            archive_id: Archive ID like "RRD018-2024"
            
        Returns:
            Path to the document subfolder if found, None otherwise
        """
        if self.logger:
            self.logger.project_info("Starting enhanced document folder detection")
        
        # Get all subdirectories (excluding hidden folders)
        subdirs = [item for item in project_path.iterdir() 
                  if item.is_dir() and not item.name.startswith('.')]
        
        if not subdirs:
            if self.logger:
                self.logger.project_warning("No subdirectories found in project folder")
            return None
        
        # === LAYER 1: STRING DETECTION ===
        
        # First priority: PDF patterns or Archive ID
        pdf_or_archive_candidates = []
        for folder in subdirs:
            folder_name = folder.name.lower()
            
            # Check for PDF patterns (case-insensitive)
            if re.search(r'pdf[s]?[\s_-]*(zu|zum|für|verfilmung)?', folder_name):
                pdf_or_archive_candidates.append(folder)
            # Check for archive ID
            elif archive_id.lower() in folder_name:
                pdf_or_archive_candidates.append(folder)
        
        # Second priority: importiert pattern
        importiert_candidates = []
        for folder in subdirs:
            if re.search(r'importiert', folder.name, re.IGNORECASE):
                importiert_candidates.append(folder)
        
        # Final fallback: any remaining folders
        other_candidates = [f for f in subdirs 
                          if f not in pdf_or_archive_candidates + importiert_candidates]
        
        if self.logger:
            self.logger.project_info(f"String detection found: "
                                   f"{len(pdf_or_archive_candidates)} PDF/Archive, "
                                   f"{len(importiert_candidates)} importiert, "
                                   f"{len(other_candidates)} other folders")
        
        # === LAYER 2: FILE VALIDATION ===
        
        def analyze_folder_contents(folder_path: Path) -> dict:
            """Analyze folder contents and return file statistics"""
            try:
                all_files = [f for f in folder_path.iterdir() if f.is_file()]
                pdf_files = [f for f in all_files if f.suffix.lower() == '.pdf']
                
                return {
                    'path': folder_path,
                    'total_files': len(all_files),
                    'pdf_files': len(pdf_files),
                    'only_pdfs': len(pdf_files) == len(all_files) and len(all_files) > 0,
                    'has_pdfs': len(pdf_files) > 0,
                    'non_pdf_files': len(all_files) - len(pdf_files),
                    'is_empty': len(all_files) == 0
                }
            except (PermissionError, OSError) as e:
                if self.logger:
                    self.logger.project_warning(f"Cannot access folder {folder_path}: {e}")
                return {
                    'path': folder_path,
                    'total_files': 0,
                    'pdf_files': 0,
                    'only_pdfs': False,
                    'has_pdfs': False,
                    'non_pdf_files': 0,
                    'is_empty': True,
                    'access_error': True
                }
        
        # Analyze all candidates
        all_candidates = pdf_or_archive_candidates + importiert_candidates + other_candidates
        folder_analysis = {folder: analyze_folder_contents(folder) for folder in all_candidates}
        
        # === DECISION LOGIC ===
        
        # First priority: PDF/Archive candidates
        if pdf_or_archive_candidates:
            valid_pdf_archive = []
            
            for folder in pdf_or_archive_candidates:
                analysis = folder_analysis[folder]
                
                # Skip empty folders (FAIL condition)
                if analysis['is_empty']:
                    if self.logger:
                        self.logger.project_warning(f"Skipping empty PDF/Archive folder: {folder.name}")
                    continue
                
                # OK conditions:
                # - Only PDFs
                # - Has PDFs + other files (but non-PDF files < 5)
                if analysis['only_pdfs'] or (analysis['has_pdfs'] and analysis['non_pdf_files'] < 5):
                    valid_pdf_archive.append((folder, analysis))
            
            if valid_pdf_archive:
                # Conflict resolution: prefer folders with only PDFs
                only_pdf_folders = [(f, a) for f, a in valid_pdf_archive if a['only_pdfs']]
                
                if only_pdf_folders:
                    # Return the first folder with only PDFs
                    chosen_folder = only_pdf_folders[0][0]
                    if self.logger:
                        self.logger.project_success(f"Selected PDF/Archive folder with only PDFs: {chosen_folder.name}")
                    return chosen_folder
                else:
                    # Return the first valid folder (has PDFs + few other files)
                    chosen_folder = valid_pdf_archive[0][0]
                    analysis = valid_pdf_archive[0][1]
                    if self.logger:
                        self.logger.project_success(f"Selected PDF/Archive folder: {chosen_folder.name} "
                                                   f"({analysis['pdf_files']} PDFs, {analysis['non_pdf_files']} other files)")
                    return chosen_folder
        
        # Second priority: importiert candidates (only if no valid PDF/Archive found)
        if importiert_candidates:
            for folder in importiert_candidates:
                analysis = folder_analysis[folder]
                
                # Skip empty folders (FAIL condition)
                if analysis['is_empty']:
                    if self.logger:
                        self.logger.project_warning(f"Skipping empty importiert folder: {folder.name}")
                    continue
                
                # OK if has PDFs (same rules as PDF/Archive)
                if analysis['only_pdfs'] or (analysis['has_pdfs'] and analysis['non_pdf_files'] < 5):
                    if self.logger:
                        self.logger.project_success(f"Selected importiert folder: {folder.name} "
                                                   f"({analysis['pdf_files']} PDFs, {analysis['non_pdf_files']} other files)")
                    return folder
        
        # Final fallback: any folder with only PDFs (if no other valid options)
        if other_candidates:
            only_pdf_others = []
            
            for folder in other_candidates:
                analysis = folder_analysis[folder]
                
                if analysis['only_pdfs']:
                    only_pdf_others.append((folder, analysis))
            
            # OK if exactly one folder with only PDFs exists
            if len(only_pdf_others) == 1:
                chosen_folder = only_pdf_others[0][0]
                if self.logger:
                    self.logger.project_success(f"Selected fallback folder with only PDFs: {chosen_folder.name}")
                return chosen_folder
        
        # No valid document folder found
        if self.logger:
            self.logger.project_error("No valid document folder found using enhanced detection")
            
            # Log detailed analysis for debugging
            for folder, analysis in folder_analysis.items():
                status = "EMPTY" if analysis['is_empty'] else f"{analysis['pdf_files']}PDF/{analysis['non_pdf_files']}OTHER"
                self.logger.project_info(f"  {folder.name}: {status}")
        
        return None
    
    def _find_comlist_file(self, folder_path: Path, archive_id: str) -> Optional[Path]:
        """
        Find the COM list Excel file in the given folder using enhanced detection.
        
        Requirements:
        1. Must contain both "com" and "list" keywords (case-insensitive)
        2. Nice to have: contains the archive ID (RRD pattern)
        3. Must be Excel file (.xls, .xlsx, .xlsb, .xlsm)
        
        Args:
            folder_path: Path to the folder to search in
            archive_id: Archive ID to look for in filenames
            
        Returns:
            Path to the COM list file if found, None otherwise
        """
        try:
            # Look for Excel files in the folder (strict extensions)
            excel_extensions = ['*.xls', '*.xlsx', '*.xlsb', '*.xlsm']
            excel_files = []
            for ext in excel_extensions:
                excel_files.extend(folder_path.glob(ext))
            
            if not excel_files:
                if self.logger:
                    self.logger.project_warning(f"No Excel files found in {folder_path}")
                return None
            
            if self.logger:
                self.logger.project_info(f"Found {len(excel_files)} Excel files to analyze")
            
            # === ENHANCED COM LIST DETECTION ===
            # Priority order: "com" > "list" > archive_id
            # Accept files containing ANY of these keywords
            
            # Step 1: Categorize files by keyword priority
            com_files = []
            list_files = []
            archive_files = []
            
            archive_id_pattern = re.compile(re.escape(archive_id), re.IGNORECASE)
            
            for excel_file in excel_files:
                filename_lower = excel_file.name.lower()
                
                # Check for keywords in priority order
                if 'com' in filename_lower:
                    com_files.append(excel_file)
                    if self.logger:
                        self.logger.project_info(f"COM keyword found: {excel_file.name}")
                elif 'list' in filename_lower:
                    list_files.append(excel_file)
                    if self.logger:
                        self.logger.project_info(f"LIST keyword found: {excel_file.name}")
                elif archive_id_pattern.search(excel_file.name):
                    archive_files.append(excel_file)
                    if self.logger:
                        self.logger.project_info(f"Archive ID found: {excel_file.name}")
            
            # Step 2: Select best match based on priority
            if com_files:
                selected_file = com_files[0]
                if self.logger:
                    self.logger.project_success(f"Found COM list file (priority: COM): {selected_file.name}")
                    if len(com_files) > 1:
                        self.logger.project_info(f"Multiple COM files found, using first: {selected_file.name}")
                return selected_file
            
            elif list_files:
                selected_file = list_files[0]
                if self.logger:
                    self.logger.project_success(f"Found COM list file (priority: LIST): {selected_file.name}")
                    if len(list_files) > 1:
                        self.logger.project_info(f"Multiple LIST files found, using first: {selected_file.name}")
                return selected_file
            
            elif archive_files:
                selected_file = archive_files[0]
                if self.logger:
                    self.logger.project_success(f"Found COM list file (priority: ARCHIVE_ID): {selected_file.name}")
                    if len(archive_files) > 1:
                        self.logger.project_info(f"Multiple archive ID files found, using first: {selected_file.name}")
                return selected_file
            
            else:
                # No matching files found
                if self.logger:
                    self.logger.project_error(f"No Excel files found containing 'com', 'list', or archive ID '{archive_id}' in project {archive_id}")
                    self.logger.project_info("Available Excel files:")
                    for f in excel_files:
                        self.logger.project_info(f"  - {f.name}")
                return None
            
        except Exception as e:
            if self.logger:
                self.logger.project_error(f"Error finding COM list file: {str(e)}")
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
