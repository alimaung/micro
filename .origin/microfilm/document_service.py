"""
Document processing service module for handling document operations.

This module provides a service layer for document-related operations,
including scanning PDFs, detecting oversized pages, and calculating references.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from itertools import groupby
from operator import itemgetter

# Use PyPDF2 for PDF operations
from PyPDF2 import PdfReader

from models import Project, Document

class DocumentProcessingService:
    """
    Service for processing documents and detecting oversized pages.
    
    This service handles all operations related to document processing,
    especially focusing on detecting oversized pages and calculating
    reference sheet positions.
    """
    
    # Constants for oversized page detection
    OVERSIZE_THRESHOLD_WIDTH = 842  # A3 width in points
    OVERSIZE_THRESHOLD_HEIGHT = 1191  # A3 height in points
    
    def __init__(self, logger=None):
        """
        Initialize the document processing service.
        
        Args:
            logger: Optional logger instance. If None, logging will be disabled.
        """
        self.logger = logger
    
    def process_documents(self, project: Project) -> Project:
        """
        Process all documents in a project to detect oversized pages.
        
        This method scans all PDF documents in the project folder,
        identifies oversized pages, and updates the project with
        the processing results.
        
        Args:
            project: The project to process
            
        Returns:
            Updated project with processed documents
        """
        self.logger.section("Processing Documents")

        # Get the folder path containing documents
        folder_path = project.documents_path
        
        # Log the documents path
        self.logger.document_info(f"Looking for documents in: {folder_path}")
        
        # Check if the folder exists
        if not folder_path.exists():
            self.logger.document_error(f"Documents path does not exist: {folder_path}")
            return project
            
        # Check if the folder is a directory
        if not folder_path.is_dir():
            self.logger.document_error(f"Documents path is not a directory: {folder_path}")
            return project
        
        # Find PDF files in the folder
        pdf_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')],
                          key=lambda x: x.lower())
        
        self.logger.document_info(f"Found {len(pdf_files)} PDF documents to process")
        
        # If no documents found, log warning
        if not pdf_files:
            self.logger.document_warning(f"No PDF documents found in {folder_path}")
            return project
        
        # Clear existing documents
        project.documents = []
        
        # Track project-level statistics
        project.total_pages = 0
        project.total_oversized = 0
        project.documents_with_oversized = 0
        project.has_oversized = False
        
        # Process each document
        for document_file in pdf_files:
            self.logger.document_info(f"Processing document: {document_file}")
            document = self._process_document(folder_path, document_file)
            
            # Update project statistics
            project.total_pages += document.pages
            project.total_oversized += document.total_oversized
            
            if document.has_oversized:
                project.documents_with_oversized += 1
                project.has_oversized = True
            
            # Add document to the project
            project.documents.append(document)
        
        self.logger.document_success(f"Processed {len(project.documents)} documents with {project.total_pages} total pages")
        self.logger.document_success(f"Identified {project.total_oversized} oversized pages in {project.documents_with_oversized} documents")
        
        return project
    
    def _process_document(self, folder_path: Path, document_file: str) -> Document:
        """
        Process a single PDF document to extract metadata and detect oversized pages.
        
        Args:
            folder_path: Path to the folder containing the document
            document_file: Filename of the document
            
        Returns:
            Processed Document object
        """
        doc_path = folder_path / document_file
        
        try:
            # Extract document ID from file name or use the file name itself
            doc_id_match = re.search(r'^\d+', document_file)
            doc_id = doc_id_match.group(0) if doc_id_match else document_file.replace('.pdf', '')
            
            # Create new Document instance
            document = Document(
                doc_id=doc_id,
                path=doc_path
            )
            
            # Open the PDF file
            pdf_reader = PdfReader(str(doc_path))
            document.pages = len(pdf_reader.pages)
            
            self.logger.document_debug(f"Processing document {doc_id} with {document.pages} pages")
            
            # Check each page for oversized dimensions
            for index, page in enumerate(pdf_reader.pages):
                # Get page dimensions from mediabox
                mediabox = page.mediabox
                width, height = float(mediabox[2]), float(mediabox[3])
                
                # Check if page is oversized
                is_oversized = ((width > self.OVERSIZE_THRESHOLD_WIDTH and height > self.OVERSIZE_THRESHOLD_HEIGHT) or
                                (width > self.OVERSIZE_THRESHOLD_HEIGHT and height > self.OVERSIZE_THRESHOLD_WIDTH))
                
                # Mark oversized pages and collect their dimensions
                if is_oversized:
                    # Calculate percentage over threshold
                    width_percent = (width / self.OVERSIZE_THRESHOLD_WIDTH - 1) * 100
                    height_percent = (height / self.OVERSIZE_THRESHOLD_HEIGHT - 1) * 100
                    max_percent = max(width_percent, height_percent)
                    
                    self.logger.document_debug(f"Found oversized page in {doc_id}, page {index+1}, " 
                                           f"dimensions: {width}x{height}, {max_percent:.2f}% over threshold")
                    
                    document.has_oversized = True
                    document.dimensions.append((width, height, index, max_percent))
                    document.total_oversized += 1
            
            # If document has oversized pages, create page ranges
            if document.has_oversized:
                self.logger.document_info(f"Document {doc_id} has {document.total_oversized} oversized pages")
                
                # Create page ranges for oversized pages
                page_indices = [page_idx for _, _, page_idx, _ in document.dimensions]
                page_numbers = [idx + 1 for idx in page_indices]  # Convert to 1-based page numbers
                
                # Group consecutive page numbers into ranges
                ranges = []
                for k, g in groupby(enumerate(sorted(page_numbers)), lambda x: x[0] - x[1]):
                    group = list(map(itemgetter(1), g))
                    if group:
                        ranges.append((group[0], group[-1]))
                
                # Store the ranges
                document.ranges = ranges
                
                self.logger.document_debug(f"Created ranges for oversized pages in {doc_id}: {ranges}")
            
            return document
            
        except Exception as e:
            self.logger.document_error(f"Error processing {document_file}: {str(e)}")
            
            # Return a minimal document with error information
            return Document(
                doc_id=document_file.replace('.pdf', ''),
                path=doc_path,
                pages=0
            )
    
    def calculate_references(self, project: Project) -> Project:
        """
        Calculate reference page positions for documents with oversized pages.
        
        Args:
            project: Project with processed documents
            
        Returns:
            Updated project with reference page positions
        """
        if not project.has_oversized:
            self.logger.document_info("No oversized pages found, skipping reference calculation")
            return project
        
        self.logger.document_info("Calculating reference page positions")
        
        total_references = 0
        
        for document in project.documents:
            # Skip documents with no oversized pages
            if not document.has_oversized or not document.ranges:
                document.reference_pages = []
                document.total_references = 0
                continue
            
            # Calculate reference page positions (one before each range)
            reference_pages = []
            
            for range_start, _ in document.ranges:
                reference_pages.append(range_start)
            
            # Store reference page information
            document.reference_pages = reference_pages
            document.total_references = len(reference_pages)
            
            document.references = {
                "pages": document.reference_pages,
                "totalReferences": document.total_references,
                "adjusted_ranges": document.adjusted_ranges
            }
            
            # Store readable page descriptions 
            document.readable_pages = [
                f"{i+1} von {len(document.ranges)}" for i in range(len(document.ranges))
            ]
                        
            total_references += document.total_references
            
            self.logger.document_debug(f"Added {document.total_references} reference pages for document {document.doc_id}")
        
        # Update project with total references
        project.total_pages_with_refs = project.total_pages + total_references
        
        self.logger.document_success(f"Added {total_references} reference pages across all documents")
        
        return project