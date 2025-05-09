"""
Document distribution manager for microfilm processing.

This service handles the distribution of documents based on film allocation,
including copying documents to roll directories and handling reference sheets.
"""

import os
import shutil
import logging
from pathlib import Path
import PyPDF2
from django.conf import settings
from django.db import transaction
from datetime import datetime

from microapp.models import (
    Project, Document, Roll, DocumentSegment, ProcessedDocument,
    FilmType, DistributionResult, ReferenceSheet,
    DocumentRange
)

from microapp.services.reference_manager import ReferenceManager

logger = logging.getLogger(__name__)

class DistributionManager:
    """
    Service for distributing documents according to film allocation.
    
    This service handles document distribution to film roll directories,
    including special handling for oversized documents with reference sheets.
    """
    
    def __init__(self, reference_manager=None, film_number_manager=None):
        """
        Initialize the distribution manager.
        
        Args:
            reference_manager: Optional reference manager for handling reference sheets
            film_number_manager: Optional film number manager for handling film numbers
        """
        self.reference_manager = reference_manager or ReferenceManager()
        self.film_number_manager = film_number_manager
        self.logger = logger
    
    def log_distribution(self, project, level, message, document=None, roll=None):
        """Add a log entry for the distribution process."""
        # Format a more detailed message
        detailed_message = message
        if document:
            detailed_message = f"[Document: {document.doc_id}] {message}"
        if roll:
            detailed_message = f"[Roll: {roll.film_number or roll.roll_id}] {detailed_message}"
            
        # Log to console/file logger only
        if level == 'ERROR':
            self.logger.error(f"[Project: {project.id}] {detailed_message}")
        elif level == 'WARNING':
            self.logger.warning(f"[Project: {project.id}] {detailed_message}")
        elif level == 'SUCCESS':
            self.logger.info(f"[Project: {project.id}] SUCCESS: {detailed_message}")
        else:
            self.logger.info(f"[Project: {project.id}] {detailed_message}")
    
    @transaction.atomic
    def distribute_documents(self, project_id, reference_data=None, active_roll=None):
        """
        Distribute documents to roll directories based on film allocation.
        
        Args:
            project_id: ID of the project
            reference_data: Optional pre-generated reference data
            active_roll: Optional active roll for specific processing
            
        Returns:
            Dictionary with distribution results
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            if not project.film_allocation_complete:
                self.log_distribution(project, 'ERROR', "Film allocation is not complete")
                return {"status": "error", "message": "Film allocation is not complete"}
            
            # Choose distribution method based on project type
            if project.has_oversized:
                return self._distribute_oversized_documents(project, reference_data, active_roll)
            else:
                return self._distribute_standard_documents(project)
                
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            return {"status": "error", "message": f"Project with ID {project_id} not found"}
        except Exception as e:
            self.logger.error(f"Error in distribute_documents: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _distribute_standard_documents(self, project):
        """
        Distribute standard documents (no oversized pages) to roll directories.
        
        Args:
            project: Project with film allocation
            
        Returns:
            Dictionary with distribution results
        """
        self.log_distribution(project, 'INFO', "Starting document distribution (No Oversized)")
        
        # Create output directory
        output_dir = self._get_output_dir(project)
        if not output_dir:
            return {"status": "error", "message": "Failed to create output directory"}
        
        processed_count = 0
        error_count = 0
        
        # Get 16mm rolls
        rolls_16mm = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_16MM
        ).prefetch_related('document_segments')
        
        if rolls_16mm.exists():
            self.log_distribution(project, 'INFO', f"Processing {rolls_16mm.count()} 16mm rolls")
            
            # Process each roll
            for roll in rolls_16mm:
                if not roll.film_number:
                    self.log_distribution(project, 'WARNING', f"Roll {roll.roll_id} has no film number, skipping", roll=roll)
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    error_count += 1
                    continue
                
                # Get all document segments for this roll
                segments = roll.document_segments.all().order_by('document_index')
                
                # Process documents on this roll
                doc_count = segments.count()
                self.log_distribution(project, 'INFO', f"Processing {doc_count} documents on roll {roll.film_number}", roll=roll)
                
                for segment in segments:
                    # Get the document for this segment
                    try:
                        document = segment.document
                        
                        # Check if this segment has page range (part of a split document)
                        if segment.start_page != 1 or segment.end_page != document.pages:
                            # This is a split document segment
                            result = self._split_and_copy_document(document, segment, roll_dir)
                            if result:
                                processed_count += 1
                            else:
                                error_count += 1
                        else:
                            # Regular document, just copy it
                            result = self._copy_document(document, segment, roll_dir)
                            if result:
                                processed_count += 1
                            else:
                                error_count += 1
                                
                    except Exception as e:
                        self.log_distribution(project, 'ERROR', f"Error processing segment: {str(e)}")
                        error_count += 1
        
        # Store results
        distribution_result, created = DistributionResult.objects.update_or_create(
            project=project,
            defaults={
                "processed_count": processed_count,
                "error_count": error_count,
                "output_dir": str(output_dir),
                "status": "success" if error_count == 0 else "partial",
            }
        )
        
        # Update project status
        project.distribution_complete = True
        project.output_dir = str(output_dir)
        project.save()
        
        self.log_distribution(
            project, 
            'SUCCESS', 
            f"Document distribution completed: {processed_count} documents processed, {error_count} errors"
        )
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "error_count": error_count,
            "output_dir": str(output_dir)
        }
    
    def _distribute_oversized_documents(self, project, reference_data=None, active_roll=None):
        """
        Distribution workflow for documents with oversized pages.
        
        Args:
            project: Project with film allocation
            reference_data: Optional pre-generated reference data
            active_roll: Optional active roll for specific processing
            
        Returns:
            Dictionary with distribution results
        """
        self.log_distribution(project, 'INFO', "Starting document distribution (With Oversized)")
        
        # Create output directory
        output_dir = self._get_output_dir(project)
        if not output_dir:
            return {"status": "error", "message": "Failed to create output directory"}
        
        # Use provided reference data or generate it
        if not reference_data:
            self.log_distribution(project, 'INFO', "Generating reference sheets")
            reference_data = self.reference_manager.generate_reference_sheets(project.id, active_roll)
            
            if not reference_data or not reference_data.get('reference_sheets'):
                self.log_distribution(project, 'WARNING', "No reference sheets were generated")
                reference_sheets = {}
            else:
                reference_sheets = reference_data.get('reference_sheets', {})
        else:
            # Extract reference sheets from provided data
            reference_sheets = reference_data.get('reference_sheets', {})
            self.log_distribution(project, 'INFO', f"Using provided reference data with {len(reference_sheets)} documents")
        
        if not reference_sheets:
            self.log_distribution(project, 'WARNING', "No reference sheets available")
        
        # Initialize counters
        extracted_count = 0
        processed_35mm = 0
        copied_35mm = 0
        processed_16mm = 0
        copied_16mm = 0
        
        # Initialize tracking dictionaries for processed documents
        processed_paths_35mm = {}  # doc_id -> processed_path
        processed_paths_16mm = {}  # doc_id -> processed_path
        
        # Process 35mm documents
        rolls_35mm = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_35MM
        ).prefetch_related('document_segments')
        
        if rolls_35mm.exists():
            # For each document with oversized pages, extract and process them
            documents_with_oversized = Document.objects.filter(
                project=project,
                has_oversized=True
            )
            
            for document in documents_with_oversized:
                if document.doc_id not in reference_sheets:
                    continue
                    
                # Extract oversized pages to the oversized35 directory
                oversized_path = self.reference_manager.extract_all_oversized_pages(project.id, document.doc_id)
                if oversized_path:
                    extracted_count += 1
                    
                    # Insert reference sheets into the extracted oversized pages
                    processed_path = self.reference_manager.insert_reference_sheets_for_35mm(
                        project.id, document.doc_id, reference_sheets[document.doc_id], oversized_path
                    )
                    
                    if processed_path:
                        processed_35mm += 1
                        processed_paths_35mm[document.doc_id] = processed_path
                        self.log_distribution(
                            project,
                            'SUCCESS',
                            f"Inserted reference sheets into extracted oversized pages for {document.doc_id}",
                            document=document
                        )
                    else:
                        self.log_distribution(
                            project,
                            'WARNING',
                            f"Failed to insert reference sheets for 35mm document {document.doc_id}",
                            document=document
                        )
            
            # Copy processed 35mm documents to output directories
            self.log_distribution(project, 'INFO', "Copying processed 35mm documents to output directories")
            
            for roll in rolls_35mm:
                if not roll.film_number:
                    self.log_distribution(project, 'WARNING', f"Roll {roll.roll_id} has no film number, skipping", roll=roll)
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    continue
                
                # Process documents on this roll
                segments = roll.document_segments.all().order_by('document_index')
                
                for segment in segments:
                    doc_id = segment.document.doc_id
                    
                    # Check if we have a processed document for this ID
                    if doc_id in processed_paths_35mm:
                        # Copy the processed document to the roll directory
                        dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                        output_file_path = roll_dir / dest_filename
                        result = self.reference_manager.copy_to_output(
                            processed_paths_35mm[doc_id], 
                            roll_dir, 
                            doc_id
                        )
                        
                        if result:
                            copied_35mm += 1
                            self.log_distribution(
                                project,
                                'SUCCESS',
                                f"Copied processed 35mm document for {doc_id} to {roll.film_number}",
                                document=segment.document,
                                roll=roll
                            )
                        else:
                            self.log_distribution(
                                project,
                                'ERROR',
                                f"Failed to copy processed 35mm document for {doc_id}",
                                document=segment.document,
                                roll=roll
                            )
        
        # Process 16mm documents
        rolls_16mm = Roll.objects.filter(
            project=project,
            film_type=FilmType.FILM_16MM
        ).prefetch_related('document_segments')
        
        if rolls_16mm.exists():
            self.log_distribution(project, 'INFO', "Processing 16mm documents")
            
            # Create directory for processed 16mm documents
            processed_16mm_dir = Path(project.project_path) / ".temp" / "processed16"
            processed_16mm_dir.mkdir(parents=True, exist_ok=True)
            
            # For each document with oversized pages, insert reference sheets
            documents_with_oversized = Document.objects.filter(
                project=project,
                has_oversized=True
            )
            
            for document in documents_with_oversized:
                if document.doc_id not in reference_sheets:
                    continue
                
                # Insert reference sheets into original document
                processed_path = self.reference_manager.insert_reference_sheets(
                    project.id, document.doc_id, reference_sheets[document.doc_id], processed_16mm_dir
                )
                
                if processed_path:
                    processed_16mm += 1
                    processed_paths_16mm[document.doc_id] = processed_path
                    self.log_distribution(
                        project,
                        'SUCCESS',
                        f"Inserted reference sheets into 16mm document for {document.doc_id}",
                        document=document
                    )
                else:
                    self.log_distribution(
                        project,
                        'WARNING',
                        f"Failed to insert reference sheets for 16mm document {document.doc_id}",
                        document=document
                    )
            
            # Copy processed 16mm documents to output directories
            self.log_distribution(project, 'INFO', "Copying processed 16mm documents to output directories")
            
            for roll in rolls_16mm:
                if not roll.film_number:
                    self.log_distribution(project, 'WARNING', f"Roll {roll.roll_id} has no film number, skipping", roll=roll)
                    continue
                
                # Create roll directory
                roll_dir = self._create_roll_directory(output_dir, roll.film_number)
                if not roll_dir:
                    continue
                
                # Process documents on this roll
                segments = roll.document_segments.all().order_by('document_index')
                
                for segment in segments:
                    doc_id = segment.document.doc_id
                    
                    # Check if this is a document that needs processing
                    if doc_id in processed_paths_16mm:
                        # Copy the processed document to the roll directory
                        dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                        output_file_path = roll_dir / dest_filename
                        result = self.reference_manager.copy_to_output(
                            processed_paths_16mm[doc_id], 
                            roll_dir, 
                            doc_id
                        )
                        
                        if result:
                            copied_16mm += 1
                            self.log_distribution(
                                project,
                                'SUCCESS',
                                f"Copied processed 16mm document for {doc_id} to {roll.film_number}",
                                document=segment.document,
                                roll=roll
                            )
                        else:
                            self.log_distribution(
                                project,
                                'ERROR',
                                f"Failed to copy processed 16mm document for {doc_id}",
                                document=segment.document,
                                roll=roll
                            )
                    else:
                        # Regular document without oversized pages, just copy it
                        if not segment.document.has_oversized:
                            result = self._copy_document(segment.document, segment, roll_dir)
                            if result:
                                self.log_distribution(
                                    project,
                                    'INFO',
                                    f"Copied regular document {doc_id} to {roll.film_number}",
                                    document=segment.document,
                                    roll=roll
                                )
                            else:
                                self.log_distribution(
                                    project,
                                    'ERROR',
                                    f"Failed to copy regular document {doc_id}",
                                    document=segment.document,
                                    roll=roll
                                )
        
        # Calculate total reference sheets
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        
        # Create or update distribution result
        distribution_result, created = DistributionResult.objects.update_or_create(
            project=project,
            defaults={
                "reference_sheets": total_sheets,
                "documents_with_references": len(reference_sheets),
                "oversized_documents_extracted": extracted_count,
                "processed_35mm_documents": processed_35mm,
                "copied_35mm_documents": copied_35mm,
                "processed_16mm_documents": processed_16mm,
                "copied_16mm_documents": copied_16mm,
                "output_dir": str(output_dir),
                "status": "success"
            }
        )
        
        # Update project status
        project.distribution_complete = True
        project.output_dir = str(output_dir)
        project.save()
        
        self.log_distribution(
            project,
            'SUCCESS',
            f"Document distribution completed: "
            f"generated {total_sheets} reference sheets, "
            f"processed and copied {copied_35mm} 35mm documents, "
            f"processed and copied {copied_16mm} 16mm documents"
        )
        
        return {
            "status": "success",
            "reference_sheets": total_sheets,
            "documents_with_references": len(reference_sheets),
            "oversized_documents_extracted": extracted_count,
            "processed_35mm_documents": processed_35mm,
            "copied_35mm_documents": copied_35mm,
            "processed_16mm_documents": processed_16mm,
            "copied_16mm_documents": copied_16mm,
            "output_dir": str(output_dir)
        }
    
    def _get_output_dir(self, project):
        """
        Get or create the output directory for the project.
        
        Creates a .output directory inside the project folder.
        """
        # Create the .output directory inside the project folder
        output_dir = Path(project.project_path) / ".output"
        
        try:
            # Create the main output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            self.log_distribution(project, 'INFO', f"Using output directory: {output_dir}")
            return output_dir
        except Exception as e:
            self.log_distribution(project, 'ERROR', f"Failed to create output directory: {str(e)}")
            return None
    
    def _create_roll_directory(self, output_dir, film_number):
        """Create a directory for a film roll."""
        roll_dir = output_dir / film_number
        try:
            roll_dir.mkdir(parents=True, exist_ok=True)
            return roll_dir
        except Exception as e:
            self.logger.error(f"Failed to create roll directory for {film_number}: {str(e)}")
            return None
    
    def _copy_document(self, document, segment, destination_dir):
        """Copy a document to a roll directory."""
        source_path = Path(document.path)
        if not source_path.exists():
            self.logger.error(f"Source document not found: {source_path}")
            return False
        
        # Generate blip information
        blip = segment.blip
        if not blip and segment.roll and segment.roll.film_number:
            # Generate blip if not already present
            blip = segment.roll.generate_blip(segment.document_index, segment.start_frame)
            segment.blip = blip
            segment.save()
        
        # Create destination filename (same as source)
        dest_path = destination_dir / source_path.name
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Create a ProcessedDocument record
            ProcessedDocument.objects.create(
                document=document,
                path=str(dest_path),
                processing_type='standard',
                roll=segment.roll,
                segment=segment,
                copied_to_output=True,
                output_path=str(dest_path)
            )
            
            if blip:
                self.logger.debug(f"Copied {source_path.name} to {destination_dir} with blip {blip}")
            else:
                self.logger.debug(f"Copied {source_path.name} to {destination_dir}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy {source_path.name}: {str(e)}")
            return False
    
    def _split_and_copy_document(self, document, segment, destination_dir):
        """Split a document by page range and copy to roll directory."""
        source_path = Path(document.path)
        if not source_path.exists():
            self.logger.error(f"Source document not found: {source_path}")
            return False
        
        # Get page range from segment
        start_page = segment.start_page
        end_page = segment.end_page
        
        # Check file type
        if source_path.suffix.lower() != '.pdf':
            self.logger.error(f"Cannot split non-PDF document: {source_path}")
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
            
            # Generate blip if not already present
            blip = segment.blip
            if not blip and segment.roll and segment.roll.film_number:
                blip = segment.roll.generate_blip(segment.document_index, segment.start_frame)
                segment.blip = blip
                segment.save()
            
            # Create a ProcessedDocument record
            ProcessedDocument.objects.create(
                document=document,
                path=str(dest_path),
                processing_type='split',
                start_page=start_page,
                end_page=end_page,
                roll=segment.roll,
                segment=segment,
                copied_to_output=True,
                output_path=str(dest_path)
            )
            
            if blip:
                self.logger.debug(f"Split and copied {split_filename} to {destination_dir} with blip {blip}")
            else:
                self.logger.debug(f"Split and copied {split_filename} to {destination_dir}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to split document {document.doc_id}: {str(e)}")
            return False
    
    @transaction.atomic
    def distribute_documents_with_frontend_data(self, project_id, project_data=None, reference_data=None, allocation_data=None, film_number_data=None):
        """
        Distribute documents using data provided from frontend.
        
        Args:
            project_id: ID of the project
            project_data: Project data from frontend
            reference_data: Pre-generated reference data from frontend
            allocation_data: Film allocation data from frontend
            film_number_data: Film number data from frontend
            
        Returns:
            Dictionary with distribution results and detailed file paths
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            # Log what data was received from frontend
            self.logger.info(f"Received frontend data for distribution:")
            self.logger.info(f"- project_data: {type(project_data).__name__}, available: {project_data is not None}")
            self.logger.info(f"- reference_data: {type(reference_data).__name__}, available: {reference_data is not None}")
            self.logger.info(f"- allocation_data: {type(allocation_data).__name__}, available: {allocation_data is not None}")
            self.logger.info(f"- film_number_data: {type(film_number_data).__name__}, available: {film_number_data is not None}")
            
            if not project.film_allocation_complete:
                self.log_distribution(project, 'ERROR', "Film allocation is not complete")
                return {"status": "error", "message": "Film allocation is not complete"}
            
            # Create output directory
            output_dir = self._get_output_dir(project)
            if not output_dir:
                return {"status": "error", "message": "Failed to create output directory"}
            
            # Check if project has oversized documents from frontend data or database
            has_oversized = False
            if allocation_data and 'allocationResults' in allocation_data:
                alloc_results = allocation_data.get('allocationResults', {})
                if 'hasOversized' in alloc_results:
                    has_oversized = alloc_results.get('hasOversized')
            else:
                has_oversized = project.has_oversized
            
            self.log_distribution(project, 'INFO', f"Processing project with oversized documents: {has_oversized}")
            
            # Extract document path prefix from project data
            doc_path_prefix = None
            if project_data and 'projectInfo' in project_data and 'pdfPath' in project_data['projectInfo']:
                doc_path_prefix = project_data['projectInfo']['pdfPath']
            else:
                # Use the project's document folder
                doc_path_prefix = project.documents_path
            
            # Get reference sheet data
            reference_sheets = {}
            documents_details = {}
            if reference_data:
                reference_sheets = reference_data.get('reference_sheets', {})
                documents_details = reference_data.get('documents_details', {})
                self.log_distribution(project, 'INFO', f"Using provided reference data with {len(reference_sheets)} documents")
            
            # Initialize counters
            extracted_count = 0
            processed_35mm = 0
            copied_35mm = 0
            processed_16mm = 0
            copied_16mm = 0
            
            # Create temp directories for processing
            temp_dir = Path(project.project_path) / ".temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            processed_16mm_dir = temp_dir / "processed16"
            processed_16mm_dir.mkdir(parents=True, exist_ok=True)
            
            oversized_35mm_dir = temp_dir / "oversized35"
            oversized_35mm_dir.mkdir(parents=True, exist_ok=True)
            
            # Track processed documents
            processed_paths_16mm = {}  # doc_id -> processed_path
            processed_paths_35mm = {}  # doc_id -> processed_path
            
            # Track detailed file information for response
            processed_file_details = []
            
            # STEP 1: Process 35mm rolls - Extract oversized pages and add reference sheets
            if film_number_data and 'results' in film_number_data and 'rolls_35mm' in film_number_data['results']:
                rolls_35mm = film_number_data['results']['rolls_35mm']
                self.log_distribution(project, 'INFO', f"Processing {len(rolls_35mm)} 35mm rolls from frontend data")
                
                # Process each 35mm roll
                for roll_data in rolls_35mm:
                    film_number = roll_data.get('film_number')
                    if not film_number:
                        self.log_distribution(project, 'WARNING', f"35mm roll has no film number, skipping")
                        continue
                    
                    # Create output roll directory
                    roll_dir = self._create_roll_directory(output_dir, film_number)
                    if not roll_dir:
                        continue
                    
                    # Process each document segment in this roll
                    segments = roll_data.get('document_segments', [])
                    for segment in segments:
                        doc_id = segment.get('doc_id')
                        if not doc_id or doc_id not in reference_sheets:
                            self.log_distribution(project, 'WARNING', f"Document {doc_id} has no reference sheets, skipping")
                            continue
                        
                        # Get document details - find document object or create from frontend data
                        document = self._get_or_create_document_from_frontend(project, doc_id, doc_path_prefix)
                        if not document:
                            self.log_distribution(project, 'ERROR', f"Failed to get document {doc_id}")
                            continue
                        
                        # Extract oversized pages if not already done
                        if doc_id not in processed_paths_35mm:
                            # Extract all oversized pages
                            oversized_path = self._extract_oversized_pages_from_frontend(
                                project, document, reference_data, oversized_35mm_dir
                            )
                            
                            if oversized_path:
                                extracted_count += 1
                                
                                # Insert reference sheets into extracted pages
                                processed_path = self._insert_reference_sheets_for_35mm_from_frontend(
                                    project, document, reference_data, oversized_path
                                )
                                
                                if processed_path:
                                    processed_35mm += 1
                                    processed_paths_35mm[doc_id] = processed_path
                                    self.log_distribution(
                                        project, 'SUCCESS', 
                                        f"Inserted reference sheets into extracted oversized pages for {doc_id}",
                                        document=document
                                    )
                                else:
                                    self.log_distribution(
                                        project, 'WARNING',
                                        f"Failed to insert reference sheets for 35mm document {doc_id}",
                                        document=document
                                    )
                        
                        # Copy the processed document to the roll directory
                        if doc_id in processed_paths_35mm:
                            dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                            output_file_path = roll_dir / dest_filename
                            result = self.reference_manager.copy_to_output(
                                processed_paths_35mm[doc_id], 
                                roll_dir, 
                                doc_id
                            )
                            
                            if result:
                                copied_35mm += 1
                                self.log_distribution(
                                    project, 'SUCCESS',
                                    f"Copied processed 35mm document for {doc_id} to {film_number}",
                                    document=document
                                )
                                
                                # Add file details for response
                                processed_file_details.append({
                                    "doc_id": doc_id,
                                    "roll_number": film_number,
                                    "film_type": "35mm",
                                    "original_path": str(document.path),
                                    "processed_path": str(processed_paths_35mm[doc_id]),
                                    "output_path": str(output_file_path),
                                    "has_references": True,
                                    "is_oversized": True
                                })
                            else:
                                self.log_distribution(
                                    project, 'ERROR',
                                    f"Failed to copy processed 35mm document for {doc_id}",
                                    document=document
                                )
            
            # STEP 2: Process 16mm rolls
            if film_number_data and 'results' in film_number_data and 'rolls_16mm' in film_number_data['results']:
                rolls_16mm = film_number_data['results']['rolls_16mm']
                self.log_distribution(project, 'INFO', f"Processing {len(rolls_16mm)} 16mm rolls from frontend data")
                
                # First, process documents with oversized pages to insert reference sheets
                for doc_id, ref_sheets in reference_sheets.items():
                    if not ref_sheets:
                        continue
                    
                    # Get document details
                    document = self._get_or_create_document_from_frontend(project, doc_id, doc_path_prefix)
                    if not document:
                        self.log_distribution(project, 'ERROR', f"Failed to get document {doc_id}")
                        continue
                    
                    # Insert reference sheets into original document (for 16mm)
                    processed_path = self._insert_reference_sheets_from_frontend(
                        project, document, reference_data, processed_16mm_dir
                    )
                    
                    if processed_path:
                        processed_16mm += 1
                        processed_paths_16mm[doc_id] = processed_path
                        self.log_distribution(
                            project, 'SUCCESS',
                            f"Inserted reference sheets into 16mm document for {doc_id}",
                            document=document
                        )
                    else:
                        self.log_distribution(
                            project, 'WARNING',
                            f"Failed to insert reference sheets for 16mm document {doc_id}",
                            document=document
                        )
                
                # Process each 16mm roll
                for roll_data in rolls_16mm:
                    film_number = roll_data.get('film_number')
                    if not film_number:
                        self.log_distribution(project, 'WARNING', f"16mm roll has no film number, skipping")
                        continue
                    
                    # Create roll directory
                    roll_dir = self._create_roll_directory(output_dir, film_number)
                    if not roll_dir:
                        continue
                    
                    # Process each document segment in this roll
                    segments = roll_data.get('document_segments', [])
                    for segment in segments:
                        doc_id = segment.get('doc_id')
                        if not doc_id:
                            continue
                        
                        # Get document details
                        document = self._get_or_create_document_from_frontend(project, doc_id, doc_path_prefix)
                        if not document:
                            self.log_distribution(project, 'ERROR', f"Failed to get document {doc_id}")
                            continue
                        
                        # Check if this is a document with reference sheets
                        if doc_id in processed_paths_16mm:
                            # Copy the processed document to the roll directory
                            dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                            output_file_path = roll_dir / dest_filename
                            result = self.reference_manager.copy_to_output(
                                processed_paths_16mm[doc_id], 
                                roll_dir, 
                                doc_id
                            )
                            
                            if result:
                                copied_16mm += 1
                                self.log_distribution(
                                    project, 'SUCCESS',
                                    f"Copied processed 16mm document for {doc_id} to {film_number}",
                                    document=document
                                )
                                
                                # Add file details for response
                                processed_file_details.append({
                                    "doc_id": doc_id,
                                    "roll_number": film_number,
                                    "film_type": "16mm",
                                    "original_path": str(document.path),
                                    "processed_path": str(processed_paths_16mm[doc_id]),
                                    "output_path": str(output_file_path),
                                    "has_references": True,
                                    "is_oversized": document.has_oversized
                                })
                            else:
                                self.log_distribution(
                                    project, 'ERROR',
                                    f"Failed to copy processed 16mm document for {doc_id}",
                                    document=document
                                )
                        else:
                            # Regular document without oversized pages, just copy it
                            # Check if we need to split the document based on page ranges
                            start_page = segment.get('start_page', 1)
                            end_page = segment.get('end_page', None)
                            
                            if start_page > 1 or (end_page and end_page < document.pages):
                                # This is a split document
                                # Create segment object with needed properties
                                segment_obj = type('Segment', (), {
                                    'document': document,
                                    'start_page': start_page,
                                    'end_page': end_page or document.pages,
                                    'blip': segment.get('blip'),
                                    'document_index': int(segment.get('document_index', 0)),
                                    'start_frame': int(segment.get('start_frame', 0)),
                                })
                                
                                # Split and copy
                                dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                                output_file_path = roll_dir / dest_filename
                                result = self._copy_file_directly(document.path, output_file_path)
                                
                                if result:
                                    self.log_distribution(
                                        project, 'INFO',
                                        f"Copied document {doc_id} to {film_number}",
                                        document=document
                                    )
                                    copied_16mm += 1
                                    
                                    # Add file details for response
                                    processed_file_details.append({
                                        "doc_id": doc_id,
                                        "roll_number": film_number,
                                        "film_type": "16mm",
                                        "original_path": str(document.path),
                                        "processed_path": None,
                                        "output_path": str(output_file_path),
                                        "has_references": False,
                                        "is_oversized": False,
                                        "is_split": True,
                                        "start_page": start_page,
                                        "end_page": end_page or document.pages
                                    })
                                else:
                                    self.log_distribution(
                                        project, 'ERROR',
                                        f"Failed to copy document {doc_id}",
                                        document=document
                                    )
                            else:
                                # Regular document, just copy it
                                dest_filename = doc_id if doc_id.lower().endswith('.pdf') else f"{doc_id}.pdf"
                                output_file_path = roll_dir / dest_filename
                                result = self._copy_file_directly(document.path, output_file_path)
                                
                                if result:
                                    self.log_distribution(
                                        project, 'INFO',
                                        f"Copied document {doc_id} to {film_number}",
                                        document=document
                                    )
                                    copied_16mm += 1
                                    
                                    # Add file details for response
                                    processed_file_details.append({
                                        "doc_id": doc_id,
                                        "roll_number": film_number,
                                        "film_type": "16mm",
                                        "original_path": str(document.path),
                                        "processed_path": None,
                                        "output_path": str(output_file_path),
                                        "has_references": False,
                                        "is_oversized": False
                                    })
                                else:
                                    self.log_distribution(
                                        project, 'ERROR',
                                        f"Failed to copy document {doc_id}",
                                        document=document
                                    )
            
            # Calculate total reference sheets
            total_sheets = 0
            if reference_sheets:
                total_sheets = sum(len(sheets) for doc_id, sheets in reference_sheets.items() if isinstance(sheets, list))
            
            # Create or update distribution result
            distribution_result, created = DistributionResult.objects.update_or_create(
                project=project,
                defaults={
                    "reference_sheets": total_sheets,
                    "documents_with_references": len(reference_sheets) if reference_sheets else 0,
                    "oversized_documents_extracted": extracted_count,
                    "processed_35mm_documents": processed_35mm,
                    "copied_35mm_documents": copied_35mm,
                    "processed_16mm_documents": processed_16mm,
                    "copied_16mm_documents": copied_16mm,
                    "output_dir": str(output_dir),
                    "status": "success"
                }
            )
            
            # Update project status
            project.distribution_complete = True
            project.output_dir = str(output_dir)
            project.save()
            
            self.log_distribution(
                project,
                'SUCCESS',
                f"Document distribution completed from frontend data: "
                f"generated {total_sheets} reference sheets, "
                f"processed and copied {copied_35mm} 35mm documents, "
                f"processed and copied {copied_16mm} 16mm documents"
            )
            
            return {
                "status": "success",
                "reference_sheets": total_sheets,
                "documents_with_references": len(reference_sheets) if reference_sheets else 0,
                "oversized_documents_extracted": extracted_count,
                "processed_35mm_documents": processed_35mm,
                "copied_35mm_documents": copied_35mm,
                "processed_16mm_documents": processed_16mm,
                "copied_16mm_documents": copied_16mm,
                "output_dir": str(output_dir),
                "processed_files": processed_file_details,
                "completed_at": datetime.now().isoformat()
            }
                
        except Project.DoesNotExist:
            self.logger.error(f"Project with ID {project_id} not found")
            return {"status": "error", "message": f"Project with ID {project_id} not found"}
        except Exception as e:
            self.logger.error(f"Error in distribute_documents_with_frontend_data: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def _copy_file_directly(self, source_path, dest_path):
        """
        Copy a file directly without using document models.
        
        Args:
            source_path: Path to source file
            dest_path: Path to destination file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                self.logger.error(f"Source file not found: {source_path}")
                return False
            
            # Add debug logs
            self.logger.debug(f"_copy_file_directly - Source path: '{source_path}'")
            self.logger.debug(f"_copy_file_directly - Destination path: '{dest_path}'")
            self.logger.debug(f"_copy_file_directly - Dest filename: '{dest_path.name}'")
            
            # Check if destination already has .pdf extension
            if dest_path.name.lower().endswith('.pdf.pdf'):
                self.logger.warning(f"Destination path has double .pdf extension: {dest_path}")
                # Fix double extension by removing one .pdf
                new_dest_path = dest_path.parent / dest_path.name.replace('.pdf.pdf', '.pdf')
                self.logger.debug(f"_copy_file_directly - Fixed destination path: '{new_dest_path}'")
                dest_path = new_dest_path
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.debug(f"Directly copied {source_path} to {dest_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to directly copy file: {str(e)}")
            return False

    def _get_or_create_document_from_frontend(self, project, doc_id, doc_path_prefix):
        """
        Get document from database or create a temporary document object with frontend data.
        
        Args:
            project: Project object
            doc_id: Document ID
            doc_path_prefix: Path prefix for document files
            
        Returns:
            Document object or a temporary object with necessary attributes
        """
        try:
            # First try to get document from database
            document = Document.objects.filter(project=project, doc_id=doc_id).first()
            if document:
                return document
            
            # If not found, create a temporary document object
            doc_path = Path(doc_path_prefix) / doc_id
            
            # Create a simple object with needed properties
            document = type('Document', (), {
                'doc_id': doc_id,
                'path': str(doc_path),
                'project': project,
                'has_oversized': True,  # Assume true if we can't find it
                'pages': 0  # Will be updated later if needed
            })
            
            # Try to get page count
            try:
                with open(doc_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    document.pages = len(reader.pages)
            except:
                self.logger.warning(f"Could not get page count for {doc_id}")
            
            return document
        except Exception as e:
            self.logger.error(f"Error getting document {doc_id}: {str(e)}")
            return None

    def _extract_oversized_pages_from_frontend(self, project, document, reference_data, output_dir):
        """
        Extract oversized pages from a document based on frontend reference data.
        
        Args:
            project: Project object
            document: Document object
            reference_data: Reference sheet data from frontend
            output_dir: Directory to save extracted pages
            
        Returns:
            Path to extracted oversized pages file
        """
        try:
            doc_id = document.doc_id
            
            # Get document details from reference data
            documents_details = reference_data.get('documents_details', {})
            if doc_id not in documents_details:
                self.logger.error(f"No reference details found for {doc_id}")
                return None
            
            doc_details = documents_details[doc_id]
            oversized_ranges = doc_details.get('ranges', [])
            
            if not oversized_ranges:
                self.logger.error(f"No oversized page ranges found for {doc_id}")
                return None
            
            # Output path for extracted pages
            output_path = output_dir / f"{doc_id}_oversized.pdf"
            
            # Open the original document
            with open(document.path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()
                
                # Extract all oversized pages
                for page_range in oversized_ranges:
                    start_page, end_page = page_range
                    
                    # PDF pages are 0-indexed, but our ranges are 1-indexed
                    for page_num in range(start_page - 1, end_page):
                        if page_num < len(reader.pages):
                            writer.add_page(reader.pages[page_num])
                
                # Save the extracted pages
                with open(output_path, 'wb') as out_file:
                    writer.write(out_file)
            
            self.logger.info(f"Extracted oversized pages from {doc_id} to {output_path}")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error extracting oversized pages for {document.doc_id}: {str(e)}")
            return None

    def _insert_reference_sheets_for_35mm_from_frontend(self, project, document, reference_data, oversized_path):
        """
        Insert reference sheets into extracted oversized pages for 35mm processing.
        
        Args:
            project: Project object
            document: Document object
            reference_data: Reference sheet data from frontend
            oversized_path: Path to extracted oversized pages
            
        Returns:
            Path to processed document with reference sheets
        """
        try:
            doc_id = document.doc_id
            
            # Get document details from reference data
            documents_details = reference_data.get('documents_details', {})
            if doc_id not in documents_details:
                self.logger.error(f"No reference details found for {doc_id}")
                return None
            
            doc_details = documents_details[doc_id]
            reference_paths = doc_details.get('file_paths', [])
            
            if not reference_paths:
                self.logger.error(f"No reference sheet paths found for {doc_id}")
                return None
            
            # Output path for processed document
            output_path = Path(str(oversized_path).replace('_oversized.pdf', '_processed_35mm.pdf'))
            
            # Open the oversized pages document
            with open(oversized_path, 'rb') as file:
                oversized_reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()
                
                # For 35mm, we need to insert each reference sheet before its corresponding oversized page
                for i, ref_path in enumerate(reference_paths):
                    # Add reference sheet
                    with open(ref_path, 'rb') as ref_file:
                        ref_reader = PyPDF2.PdfReader(ref_file)
                        for page in ref_reader.pages:
                            writer.add_page(page)
                    
                    # Add corresponding oversized page if available
                    if i < len(oversized_reader.pages):
                        writer.add_page(oversized_reader.pages[i])
                
                # Save the processed document
                with open(output_path, 'wb') as out_file:
                    writer.write(out_file)
            
            self.logger.info(f"Inserted reference sheets into oversized pages for {doc_id} (35mm)")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error inserting reference sheets for 35mm document {document.doc_id}: {str(e)}")
            return None

    def _insert_reference_sheets_from_frontend(self, project, document, reference_data, output_dir):
        """
        Insert reference sheets into original document for 16mm processing.
        
        Args:
            project: Project object
            document: Document object
            reference_data: Reference sheet data from frontend
            output_dir: Directory to save processed document
            
        Returns:
            Path to processed document with reference sheets
        """
        try:
            doc_id = document.doc_id
            
            # Get document details from reference data
            documents_details = reference_data.get('documents_details', {})
            if doc_id not in documents_details:
                self.logger.error(f"No reference details found for {doc_id}")
                return None
            
            doc_details = documents_details[doc_id]
            reference_paths = doc_details.get('file_paths', [])
            ranges = doc_details.get('ranges', [])
            
            if not reference_paths or not ranges:
                self.logger.error(f"Missing reference data for {doc_id}")
                return None
            
            # Output path for processed document
            output_path = output_dir / f"{doc_id}_with_refs.pdf"
            
            # Open the original document
            with open(document.path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()
                
                # Current position in the document
                current_page = 0
                
                # For each reference sheet and its corresponding oversized page range
                for ref_path, page_range in zip(reference_paths, ranges):
                    start_page, end_page = page_range
                    
                    # Add all pages up to the oversized page
                    while current_page < start_page - 1:
                        if current_page < len(reader.pages):
                            writer.add_page(reader.pages[current_page])
                        current_page += 1
                    
                    # Add reference sheet
                    with open(ref_path, 'rb') as ref_file:
                        ref_reader = PyPDF2.PdfReader(ref_file)
                        for page in ref_reader.pages:
                            writer.add_page(page)
                    
                    # Add the oversized pages
                    for page_num in range(start_page - 1, end_page):
                        if page_num < len(reader.pages):
                            writer.add_page(reader.pages[page_num])
                        current_page = page_num + 1
                
                # Add any remaining pages
                while current_page < len(reader.pages):
                    writer.add_page(reader.pages[current_page])
                    current_page += 1
                
                # Save the processed document
                with open(output_path, 'wb') as out_file:
                    writer.write(out_file)
            
            self.logger.info(f"Inserted reference sheets into document {doc_id} (16mm)")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error inserting reference sheets for 16mm document {document.doc_id}: {str(e)}")
            return None

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
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                self.logger.error(f"Source file not found: {source_path}")
                return False
            
            # Add debug logs
            self.logger.debug(f"_copy_to_output - Original doc_id: '{doc_id}'")
            self.logger.debug(f"_copy_to_output - doc_id ends with .pdf: {doc_id.lower().endswith('.pdf')}")
            
            # Use the document ID as the filename - remove .pdf if already present
            if doc_id.lower().endswith('.pdf'):
                dest_filename = doc_id
            else:
                dest_filename = f"{doc_id}.pdf"
                
            dest_path = destination_dir / dest_filename
            
            # Add more debug logs
            self.logger.debug(f"_copy_to_output - Final dest_filename: '{dest_filename}'")
            self.logger.debug(f"_copy_to_output - Full dest_path: '{dest_path}'")
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.debug(f"Copied {source_path} to {dest_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy file: {str(e)}")
            return False
