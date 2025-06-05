"""
Document processing service module.

This module provides services for processing documents, calculating references,
and distributing documents to roll directories based on film allocation.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import PyPDF2

from models import Project, Document, FilmType, FilmRoll

class DocumentDistributionService :
    """
    Service for processing documents and distributing them according to film allocation.
    
    This service handles document analysis, reference calculation, and file distribution
    to appropriate roll directories based on film allocation.
    """
    
    def __init__(self, logger=None, film_number_service=None, reference_service=None):
        """
        Initialize the document processing service.
        
        Args:
            logger: Optional logger instance
            film_number_service: Optional film number service instance
            reference_service: Optional reference sheet service instance
        """
        self.logger = logger
        self.film_number_service = film_number_service
        self.reference_service = reference_service
    
    def process_documents(self, project: Project) -> Project:
        """
        Process all documents in the project to identify oversized pages.
        
        Args:
            project: Project to process
            
        Returns:
            Updated project with document information
        """
        self.logger.section("Document Processing")
        self.logger.distribution_info(f"Processing {len(project.documents)} documents")
        
        # Implementation of document processing to identify oversized pages
        # (This part should already be implemented in your codebase)
        
        return project
    
    def calculate_references(self, project: Project) -> Project:
        """
        Calculate reference sheets needed for oversized documents.
        
        Args:
            project: Project with oversized documents
            
        Returns:
            Updated project with reference information
        """
        if not project.has_oversized:
            return project
            
            self.logger.section("Reference Sheet Calculation")
        self.logger.distribution_info(f"Calculating references for {project.documents_with_oversized} documents")
        
        # Implementation for calculating reference sheet needs
        # (This part should already be implemented in your codebase)
        
        return project
    
    def distribute_documents(self, project: Project, film_number_service=None, reference_service=None, active_roll=None) -> Project:
        """
        Distribute all documents to roll directories based on film allocation.
        Chooses the appropriate method based on whether the project has oversized pages.
        
        Args:
            project: Project with film allocation
            film_number_service: Optional film number service for oversized documents
            reference_service: Optional reference service for oversized documents
            
        Returns:
            Updated project with distribution information
        """
        if not project.film_allocation:
            self.logger.distribution_error("No film allocation found in project")
            return project
        
        # Choose distribution method based on project type
        if project.has_oversized:
            return self._distribute_oversized_documents(project, film_number_service, reference_service, active_roll)
        else:
            return self._distribute_standard_documents(project)
    
    def _distribute_standard_documents(self, project: Project) -> Project:
        """
        Distribute standard documents (no oversized pages) to roll directories.
        
        Args:
            project: Project with film allocation
            
        Returns:
            Updated project with distribution information
        """
        self.logger.section("Document Distribution (No Oversized)")
        self.logger.distribution_info(f"Distributing {len(project.documents)} documents to roll directories")
        
        # Create output directory if needed
        output_dir = self._get_output_dir(project)
        if not output_dir:
            return project
        
        processed_count = 0
        error_count = 0
        
        # Process 16mm rolls
        if project.film_allocation.rolls_16mm:
            self.logger.distribution_info(f"Processing {len(project.film_allocation.rolls_16mm)} 16mm rolls")
            
            for roll in project.film_allocation.rolls_16mm:
                if not roll.film_number:
                    self.logger.distribution_warning(f"Roll {roll.roll_id} has no film number, skipping")
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    error_count += 1
                    continue
                
                # Check if this roll has split documents
                roll_has_splits = False
                if hasattr(roll, 'has_split_documents'):
                    roll_has_splits = roll.has_split_documents
                
                if roll_has_splits:
                    self.logger.distribution_info(f"Roll {roll.roll_id} contains split documents")
                
                # Get split document information from the roll if available
                split_docs_info = {}
                if hasattr(roll, 'split_documents') and roll.split_documents:
                    split_docs_info = roll.split_documents
                    self.logger.distribution_debug(f"Roll {roll.roll_id} has {len(split_docs_info)} split documents defined")
                
                # Process documents on this roll
                doc_count = len(roll.document_segments)
                self.logger.distribution_info(f"Processing {doc_count} documents on roll {roll.film_number}")
                
                # Sort document segments by document index for consistent ordering
                sorted_segments = sorted(roll.document_segments, key=lambda x: x.document_index)
                
                for segment in sorted_segments:
                    doc_id = segment.doc_id
                    
                    # Find corresponding document object
                    document = self._find_document(project, doc_id)
                    if not document:
                        self.logger.distribution_error(f"Document {doc_id} not found in project")
                        error_count += 1
                        continue
                    
                    # Check if this document is in the split_docs_info
                    is_split = doc_id in split_docs_info
                    
                    # Get page range either from split_docs_info or from segment
                    page_range = None
                    if is_split and doc_id in split_docs_info:
                        # Find the entry for this roll
                        for split_entry in split_docs_info[doc_id]:
                            if split_entry.get('roll') == roll.roll_id:
                                page_range = split_entry.get('pageRange')
                                break
                    
                    # Fallback to segment's page_range if available
                    if not page_range and hasattr(segment, 'page_range'):
                        page_range = segment.page_range
                    
                    try:
                        if is_split and page_range:
                            # This is a split document with a defined page range
                            self.logger.distribution_info(f"Extracting pages {page_range[0]}-{page_range[1]} from split document {doc_id}")
                            
                            # Update segment's page_range if needed
                            if not hasattr(segment, 'page_range') or segment.page_range != page_range:
                                segment.page_range = page_range
                            
                            # Split and copy this segment
                            result = self._split_and_copy_document(document, segment, roll_dir)
                            if result:
                                processed_count += 1
                            else:
                                error_count += 1
                        else:
                            # Regular document or split with no page range info, just copy it
                            self.logger.distribution_info(f"Copying document {doc_id}")
                            
                            result = self._copy_document(document, segment, roll_dir)
                            if result:
                                processed_count += 1
                            else:
                                error_count += 1
                    except Exception as e:
                        self.logger.distribution_error(f"Error processing document {doc_id}: {str(e)}")
                        error_count += 1
        
        # Store results in project
        project.distribution_results = {
            "processed_count": processed_count,
            "error_count": error_count,
            "output_dir": str(output_dir)
        }
        
        self.logger.distribution_success(f"Document distribution completed: {processed_count} documents processed, {error_count} errors")
        
        return project
    
    def _distribute_oversized_documents(self, project: Project, film_number_service=None, reference_service=None, active_roll=None) -> Project:
        """
        Distribution workflow that generates reference sheets, processes documents,
        and copies them to output directories based on film allocation.
        
        Args:
            project: Project with film allocation
            film_number_service: Optional film number service
            reference_service: Optional reference service
            
        Returns:
            Updated project with distributed documents
        """
        self.logger.section("Document Distribution (With Oversized)")
        self.logger.distribution_warning(f"Preparing and distributing oversized documents")
        
        # Initialize services if needed
        if not film_number_service:
            from film_number_service import FilmNumberService
            film_number_service = FilmNumberService(logger=self.logger)
        
        if not reference_service:
            from reference_service import ReferenceSheetService
            reference_service = ReferenceSheetService(film_number_service, logger=self.logger)
        
        # Create output directory
        output_dir = self._get_output_dir(project)
        if not output_dir:
            project.distribution_results = {"error": "Failed to create output directory"}
            return project
        
        # Step 1: Generate reference sheets
        self.logger.distribution_warning("Generating reference sheets")
        reference_sheets = reference_service.generate_reference_sheets(project, active_roll)
        
        if not reference_sheets:
            self.logger.distribution_warning("No reference sheets were generated")
            project.distribution_results = {}
            return project
        
        # Store reference sheet data in project
        project.reference_sheets = reference_sheets
        
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        self.logger.distribution_info(f"Generated {total_sheets} reference sheets for {len(reference_sheets)} documents")
        
        # Step 2: Extract and process oversized pages for 35mm
        extracted_count = 0
        processed_35mm = 0
        copied_35mm = 0
        
        # Initialize tracking dictionaries
        processed_paths_35mm = {}  # doc_id -> processed_path
        
        if project.film_allocation.rolls_35mm:
            for document in project.documents:
                if not document.has_oversized or not document.ranges:
                    continue
                    
                # Extract only the oversized pages to oversized35 directory
                oversized_path = self._extract_oversized_pages(project, document, reference_service)
                if oversized_path:
                    extracted_count += 1
                    
                    # Insert reference sheets into the extracted oversized pages
                    if document.doc_id in reference_sheets:
                        processed_path = reference_service.insert_reference_sheets_for_35mm(
                            project, document, reference_sheets[document.doc_id], oversized_path
                        )
                        
                        if processed_path:
                            processed_35mm += 1
                            processed_paths_35mm[document.doc_id] = processed_path
                            self.logger.distribution_success(f"Inserted reference sheets into extracted oversized pages for {document.doc_id}")
                        else:
                            self.logger.distribution_warning(f"Failed to insert reference sheets for 35mm document {document.doc_id}")
        
        # Step 3: Copy processed 35mm documents to output directories
        if project.film_allocation.rolls_35mm:
            self.logger.distribution_info(f"Copying processed 35mm documents to output directories")
            
            for roll in project.film_allocation.rolls_35mm:
                if not roll.film_number:
                    self.logger.distribution_warning(f"Roll {roll.roll_id} has no film number, skipping")
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    continue
                
                # Sort document segments by document index for consistent ordering
                sorted_segments = sorted(roll.document_segments, key=lambda x: x.document_index)
                
                for segment in sorted_segments:
                    doc_id = segment.doc_id
                    
                    # Check if we have a processed document for this ID
                    if doc_id in processed_paths_35mm:
                        # Copy the processed document to the roll directory
                        result = self._copy_to_output(
                            processed_paths_35mm[doc_id], 
                            roll_dir, 
                            doc_id
                        )
                        
                        if result:
                            copied_35mm += 1
                            self.logger.distribution_success(f"Copied processed 35mm document for {doc_id} to {roll.film_number}")
                        else:
                            self.logger.distribution_error(f"Failed to copy processed 35mm document for {doc_id}")
        
        # Step 4: Process 16mm documents (insert reference sheets and copy)
        processed_16mm = 0
        copied_16mm = 0
        
        # Initialize tracking dictionaries
        processed_paths_16mm = {}  # doc_id -> processed_path
        
        if project.film_allocation.rolls_16mm:
            self.logger.distribution_info(f"Processing 16mm documents")
            
            # Create directory for processed 16mm documents
            processed_16mm_dir = project.project_path / ".temp" / "processed16"
            processed_16mm_dir.mkdir(parents=True, exist_ok=True)
            
            for document in project.documents:
                if not document.has_oversized or document.doc_id not in reference_sheets:
                    continue
                
                # Insert reference sheets into original document
                processed_path = reference_service.insert_reference_sheets(
                    project, document, reference_sheets[document.doc_id], processed_16mm_dir
                )
                
                if processed_path:
                    processed_16mm += 1
                    processed_paths_16mm[document.doc_id] = processed_path
                    self.logger.distribution_success(f"Inserted reference sheets into 16mm document for {document.doc_id}")
                else:
                    self.logger.distribution_warning(f"Failed to insert reference sheets for 16mm document {document.doc_id}")
            
            # Copy processed 16mm documents to output directories
            self.logger.distribution_info(f"Copying processed 16mm documents to output directories")
            
            for roll in project.film_allocation.rolls_16mm:
                if not roll.film_number:
                    self.logger.distribution_warning(f"Roll {roll.roll_id} has no film number, skipping")
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    continue
                
                # Sort document segments by document index for consistent ordering
                sorted_segments = sorted(roll.document_segments, key=lambda x: x.document_index)
                
                for segment in sorted_segments:
                    doc_id = segment.doc_id
                    
                    # Check if this is a document that needs processing
                    if doc_id in processed_paths_16mm:
                        # Copy the processed document to the roll directory
                        result = self._copy_to_output(
                            processed_paths_16mm[doc_id], 
                            roll_dir, 
                            doc_id
                        )
                        
                        if result:
                            copied_16mm += 1
                            self.logger.distribution_success(f"Copied processed 16mm document for {doc_id} to {roll.film_number}")
                        else:
                            self.logger.distribution_error(f"Failed to copy processed 16mm document for {doc_id}")
                    else:
                        # Regular document without oversized pages, just copy it
                        document = self._find_document(project, doc_id)
                        if document:
                            result = self._copy_document(document, segment, roll_dir)
                            if result:
                                self.logger.distribution_debug(f"Copied regular document {doc_id} to {roll.film_number}")
                            else:
                                self.logger.distribution_error(f"Failed to copy regular document {doc_id}")
        
        # Initialize distribution_results if it doesn't exist or is None
        if not hasattr(project, 'distribution_results') or project.distribution_results is None:
            project.distribution_results = {}
        
        # Create a new dictionary with our results and set it on the project
        project.distribution_results = {
            "reference_sheets": total_sheets,
            "documents_with_references": len(reference_sheets),
            "oversized_documents_extracted": extracted_count,
            "processed_35mm_documents": processed_35mm,
            "copied_35mm_documents": copied_35mm,
            "processed_16mm_documents": processed_16mm,
            "copied_16mm_documents": copied_16mm,
            "output_dir": str(output_dir)
        }
        
        # End processing here
        self.logger.distribution_success(
            f"Document distribution completed: "
            f"generated {total_sheets} reference sheets, "
            f"processed and copied {copied_35mm} 35mm documents, "
            f"processed and copied {copied_16mm} 16mm documents"
        )
        
        return project

    def _extract_oversized_pages(self, project, document, reference_service):
        """
        Extract only the oversized pages from a document to the oversized35 directory.
        No references are inserted at this stage.
        
        Returns:
            Path to extracted oversized pages if successful, None otherwise
        """
        # Create the oversized35 directory if it doesn't exist
        oversized_dir = project.project_path / ".temp" / "oversized35"
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        doc_id = document.doc_id
        
        # Extract all oversized pages from the document
        oversized_path = reference_service.extract_all_oversized_pages(
            project, document, output_dir=oversized_dir
        )
        
        if oversized_path:
            self.logger.distribution_success(f"Extracted oversized pages from {doc_id}")
            return oversized_path  # Return the path on success
        else:
            self.logger.distribution_warning(f"Failed to extract oversized pages from {doc_id}")
            return None  # Return None on failure
    
    def _get_output_dir(self, project: Project) -> Optional[Path]:
        """
        Get or create the output directory for the project.
        
        Creates a .output directory inside the project folder
        at the same level as .data, with roll directories inside.
        """
        # Create the .output directory inside the project folder at the same level as .data
        output_dir = project.project_path / ".output"
        
        try:
            # Create the main output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.distribution_debug(f"Using output directory: {output_dir}")
            return output_dir
        except Exception as e:
            self.logger.distribution_error(f"Failed to create output directory: {str(e)}")
            return None
    
    def _create_roll_directory(self, output_dir: Path, film_number: str) -> Optional[Path]:
        """Create a directory for a film roll."""
        roll_dir = output_dir / film_number
        try:
            roll_dir.mkdir(parents=True, exist_ok=True)
            return roll_dir
        except Exception as e:
            self.logger.distribution_error(f"Failed to create roll directory for {film_number}: {str(e)}")
            return None
    
    def _find_document(self, project: Project, doc_id: str) -> Optional[Document]:
        """Find a document in the project by its ID."""
        for doc in project.documents:
            if doc.doc_id == doc_id:
                # Log available attributes for debugging
                attrs = [attr for attr in dir(doc) if not attr.startswith('_')]
                self.logger.distribution_debug(f"Found document {doc_id} with attributes: {attrs}")
                return doc
        
        self.logger.distribution_error(f"Document {doc_id} not found in project (has {len(project.documents)} documents)")
        return None
    
    def _copy_document(self, document: Document, segment: Any, destination_dir: Path) -> bool:
        """Copy a document to a roll directory."""
        source_path = Path(document.path)
        if not source_path.exists():
            self.logger.distribution_error(f"Source document not found: {source_path}")
            return False
        
        # Generate blip information if available
        blip = getattr(segment, 'blip', None)
        if not blip and hasattr(segment, 'roll') and hasattr(segment.roll, 'film_number'):
            # Generate blip if not already present
            doc_index = getattr(segment, 'document_index', 1)
            frame_start = getattr(segment, 'start_frame', 1)
            blip = f"{segment.roll.film_number}-{doc_index:04d}.{frame_start:05d}"
        
        # Create destination filename (same as source)
        dest_path = destination_dir / source_path.name
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Store blip information in document
            document.blip = blip
            
            if blip:
                self.logger.distribution_debug(f"Copied {source_path.name} to {destination_dir} with blip {blip}")
            else:
                self.logger.distribution_debug(f"Copied {source_path.name} to {destination_dir}")
            
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to copy {source_path.name}: {str(e)}")
            return False
    
    def _split_and_copy_document(self, document: Document, segment: Any, destination_dir: Path) -> bool:
        """Split a document by page range and copy to roll directory."""
        source_path = Path(document.path)
        if not source_path.exists():
            self.logger.distribution_error(f"Source document not found: {source_path}")
            return False
        
        # Get page range to extract
        if not hasattr(segment, 'page_range') or not segment.page_range:
            self.logger.distribution_error(f"No page range specified for document segment {document.doc_id}")
            return False
        
        start_page, end_page = segment.page_range
        
        # Check file type
        if source_path.suffix.lower() != '.pdf':
            self.logger.distribution_error(f"Cannot split non-PDF document: {source_path}")
            return False
        
        try:
            # Create a filename for the split document
            split_filename = f"{source_path.stem}_p{start_page}-{end_page}{source_path.suffix}"
            dest_path = destination_dir / split_filename
            
            # Split the PDF
            with open(source_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()
                
                # PDF pages are 0-indexed, but our page ranges are 1-indexed
                for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
                    writer.add_page(reader.pages[page_num])
                
                # Save the split PDF
                with open(dest_path, 'wb') as out_file:
                    writer.write(out_file)
            
            # Generate blip information if available
            blip = getattr(segment, 'blip', None)
            if not blip and hasattr(segment, 'roll') and hasattr(segment.roll, 'film_number'):
                # Generate blip if not already present
                doc_index = getattr(segment, 'document_index', 1)
                frame_start = getattr(segment, 'start_frame', 1)
                blip = f"{segment.roll.film_number}-{doc_index:04d}.{frame_start:05d}"
            
            # Store blip information
            if not hasattr(document, 'split_segments'):
                document.split_segments = []
            
            document.split_segments.append({
                'page_range': (start_page, end_page),
                'output_path': str(dest_path),
                'blip': blip
            })
            
            if blip:
                self.logger.distribution_debug(f"Split and copied {split_filename} to {destination_dir} with blip {blip}")
            else:
                self.logger.distribution_debug(f"Split and copied {split_filename} to {destination_dir}")
            
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to split document {document.doc_id}: {str(e)}")
            return False

    def _copy_processed_document(self, processed_path, segment, destination_dir):
        """
        Copy a processed document (with reference sheets) to a roll directory.
        Uses the original document name in the destination.
        """
        import shutil
        from pathlib import Path
        
        source_path = Path(processed_path)
        if not source_path.exists():
            self.logger.distribution_error(f"Processed document not found: {source_path}")
            return False
        
        # Get the original document name - use the document ID from the segment
        # rather than the processed filename which might include page ranges
        doc_id = segment.doc_id
        
        # Generate blip information if available
        blip = getattr(segment, 'blip', None)
        if not blip and hasattr(segment, 'roll') and hasattr(segment.roll, 'film_number'):
            # Generate blip if not already present
            doc_index = getattr(segment, 'document_index', 1)
            frame_start = getattr(segment, 'start_frame', 1)
            blip = f"{segment.roll.film_number}-{doc_index:04d}.{frame_start:05d}"
        
        # Create destination path with the original filename (doc_id + .pdf)
        original_filename = f"{doc_id}.pdf"
        dest_path = destination_dir / original_filename
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            self.logger.distribution_debug(f"Copied processed document to {destination_dir}/{original_filename}")
            
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to copy processed document: {str(e)}")
            return False

    def _split_document_with_references(self, processed_path, segment, destination_dir):
        """
        Split a document that already has reference sheets inserted.
        Uses the original document name in the destination.
        """
        import PyPDF2
        from pathlib import Path
        
        source_path = Path(processed_path)
        if not source_path.exists():
            self.logger.distribution_error(f"Processed document not found: {source_path}")
            return False
        
        # Get page range to extract
        if not hasattr(segment, 'page_range') or not segment.page_range:
            self.logger.distribution_error(f"No page range specified for document segment")
            return False
        
        start_page, end_page = segment.page_range
        doc_id = segment.doc_id
        
        try:
            # Use original document name for the output file
            original_filename = f"{doc_id}.pdf"
            dest_path = destination_dir / original_filename
            
            # For logging, keep track of page range
            temp_filename = f"{doc_id}_p{start_page}-{end_page}.pdf"
            
            # Split the PDF
            with open(source_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()
                
                # PDF pages are 0-indexed, but our page ranges are 1-indexed
                for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
                    writer.add_page(reader.pages[page_num])
                
                # Save the split PDF
                with open(dest_path, 'wb') as out_file:
                    writer.write(out_file)
            
            # Generate blip information if available
            blip = getattr(segment, 'blip', None)
            if not blip and hasattr(segment, 'roll') and hasattr(segment.roll, 'film_number'):
                # Generate blip if not already present
                doc_index = getattr(segment, 'document_index', 1)
                frame_start = getattr(segment, 'start_frame', 1)
                blip = f"{segment.roll.film_number}-{doc_index:04d}.{frame_start:05d}"
            
            self.logger.distribution_debug(f"Split document with references (pages {start_page}-{end_page}) and saved as {original_filename}")
            
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to split document with references: {str(e)}")
            return False

    def _copy_extracted_pages(self, oversized_path, segment, destination_dir):
        """
        Copy extracted oversized pages to a 35mm roll directory.
        Uses the original document name in the destination.
        """
        import shutil
        from pathlib import Path
        
        source_path = Path(oversized_path)
        if not source_path.exists():
            self.logger.distribution_error(f"Extracted pages not found: {source_path}")
            return False
        
        # Get document ID from segment
        doc_id = segment.doc_id
        
        # Generate blip information if available
        blip = getattr(segment, 'blip', None)
        if not blip and hasattr(segment, 'roll') and hasattr(segment.roll, 'film_number'):
            # Generate blip if not already present
            doc_index = getattr(segment, 'document_index', 1)
            frame_start = getattr(segment, 'start_frame', 1)
            blip = f"{segment.roll.film_number}-{doc_index:04d}.{frame_start:05d}"
        
        # Use original document name for the destination
        original_filename = f"{doc_id}.pdf"
        dest_path = destination_dir / original_filename
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            self.logger.distribution_debug(f"Copied oversized pages to {destination_dir}/{original_filename}")
            
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to copy oversized pages: {str(e)}")
            return False

    def _copy_to_output(self, source_path, destination_dir, doc_id):
        """
        Copy a processed document to the output directory with the document ID as filename.
        
        Args:
            source_path: Path to the source document
            destination_dir: Directory to copy to
            doc_id: Document ID to use as filename
            
        Returns:
            True if successful, False otherwise
        """
        import shutil
        from pathlib import Path
        
        source_path = Path(source_path)
        if not source_path.exists():
            self.logger.distribution_error(f"Source file not found: {source_path}")
            return False
        
        # Use the document ID as the filename
        dest_filename = f"{doc_id}.pdf"
        dest_path = destination_dir / dest_filename
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.distribution_debug(f"Copied {source_path} to {dest_path}")
            return True
        except Exception as e:
            self.logger.distribution_error(f"Failed to copy file: {str(e)}")
            return False