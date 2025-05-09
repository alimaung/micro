"""
Reference manager service for microfilm processing.

This service handles the generation of reference sheets for oversized documents,
extraction of oversized pages, and insertion of reference sheets into documents.
"""

import os
import logging
from pathlib import Path
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.db import transaction
from io import BytesIO
import datetime

from django.conf import settings
from microapp.models import (
    Project, Document, DocumentRange, ReferenceSheet, RangeReferenceInfo,
    DocumentReferenceInfo, ReadablePageDescription, AdjustedRange, ProcessedDocument
)

logger = logging.getLogger(__name__)

class ReferenceManager:
    """
    Service for generating and managing reference sheets for oversized documents.
    
    This service handles the creation of reference sheets, insertion of reference sheets
    into documents, and extraction of oversized pages for 35mm film processing.
    """
    
    def __init__(self, film_number_manager=None, logger=None):
        """
        Initialize the reference manager.
        
        Args:
            film_number_manager: Optional film number manager instance
            logger: Optional logger instance
        """
        self.film_number_manager = film_number_manager
        self.logger = logger or logging.getLogger(__name__)
        
    @transaction.atomic
    def generate_reference_sheets(self, project_id, active_roll=None):
        """
        Generate all reference sheets for a project with oversized documents.
        Only creates reference sheets in the references directory.
        
        Args:
            project_id: ID of the project
            active_roll: Optional active roll for specific processing
            
        Returns:
            Dictionary mapping document IDs to lists of reference sheet paths
        """
        # Get the project
        project = Project.objects.get(pk=project_id)
        
        if not project.has_oversized:
            self.logger.info("No oversized documents found, skipping reference sheet generation")
            return {}
        
        self.logger.info(f"Generating reference sheets for {project.archive_id}")
        
        # Create temp directory structure
        temp_dir = Path(project.project_path) / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Results dictionary to track reference sheets
        reference_sheets = {}
        
        # Get blip data from film number service
        if self.film_number_manager:
            blip_data = self.film_number_manager.prepare_reference_sheet_data(project)
        else:
            # If no film number manager provided, try to import it
            from .film_number_manager import FilmNumberManager
            film_number_manager = FilmNumberManager(logger=self.logger)
            blip_data = film_number_manager.prepare_reference_sheet_data(project)
        
        # Get all documents with oversized pages
        documents = Document.objects.filter(
            project=project,
            has_oversized=True
        ).prefetch_related('ranges', 'dimensions', 'readable_page_descriptions')
        
        # Process each document with oversized pages
        for document in documents:
            if not document.has_oversized or not document.ranges.exists():
                continue
            
            # Get document ranges
            ranges = list(document.ranges.all().order_by('start_page'))
            if not ranges:
                continue
                
            # Get or generate readable pages
            readable_pages = self.get_readable_pages(document)
            if not readable_pages:
                readable_pages = self.generate_readable_pages(document)
                
            doc_id = document.doc_id
            reference_sheets[doc_id] = []
            
            # Get blip data for this document
            doc_blip_data = blip_data.get(doc_id, [])
            
            # Process each oversized range
            for i, range_obj in enumerate(ranges):
                # Get the range
                range_start = range_obj.start_page
                range_end = range_obj.end_page
                
                # Get human-readable page range
                human_range = ""
                if i < len(readable_pages):
                    human_range = readable_pages[i]
                else:
                    human_range = f"Pages {range_start}-{range_end}"
                
                # Get blip information for this range
                range_blip = None
                film_number_35mm = None
                
                # Try to find matching blip data
                for blip_entry in doc_blip_data:
                    if blip_entry.get('range') == (range_start, range_end):
                        range_blip = blip_entry.get('blip_35mm')
                        film_number_35mm = blip_entry.get('film_number_35mm')
                        break
                
                if not range_blip or not film_number_35mm:
                    self.logger.warning(f"No 35mm blip found for document {doc_id}, range {range_start}-{range_end}")
                    continue
                
                # Create reference sheet
                try:
                    reference_sheet = self.create_reference_sheet(
                        document_name=doc_id,
                        film_number=film_number_35mm,
                        archive_id=project.archive_id,
                        blip=range_blip,
                        doc_type=project.doc_type,
                        human_ranges=human_range,
                        barcode=doc_id
                    )
                    
                    # Generate path for reference sheet
                    ref_sheet_path = self.get_reference_sheet_path(project, doc_id, range_start, range_end)
                    
                    # Save reference sheet
                    with open(ref_sheet_path, "wb") as f:
                        f.write(reference_sheet)
                    
                    # Create ReferenceSheet model
                    ref_sheet = ReferenceSheet.objects.create(
                        document=document,
                        document_range=range_obj,
                        range_start=range_start,
                        range_end=range_end,
                        path=str(ref_sheet_path),
                        blip_35mm=range_blip,
                        film_number_35mm=film_number_35mm,
                        human_range=human_range
                    )
                    
                    # Add to results
                    reference_sheets[doc_id].append({
                        'path': str(ref_sheet_path),
                        'range': (range_start, range_end),
                        'blip_35mm': range_blip,
                        'film_number_35mm': film_number_35mm,
                        'id': ref_sheet.id
                    })
                    
                    self.logger.info(f"Generated reference sheet for {doc_id}, range {range_start}-{range_end}")
                    
                except Exception as e:
                    self.logger.error(f"Error creating reference sheet for {doc_id}, range {range_start}-{range_end}: {str(e)}")
        
        # Calculate totals
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        self.logger.info(f"Generated {total_sheets} reference sheets for {len(reference_sheets)} documents")
        
        return reference_sheets
        
    def create_reference_sheet(self, document_name, film_number, archive_id, blip, 
                              doc_type, human_ranges, barcode):
        """
        Create a single reference sheet with the given metadata.
        
        Args:
            document_name: Name of the document
            film_number: Film number from 35mm roll
            archive_id: Archive ID from project
            blip: 35mm blip for the oversized content
            doc_type: Document type from project
            human_ranges: Human-readable page ranges string
            barcode: Document barcode/ID
            
        Returns:
            bytes: The PDF content as bytes
        """
        # Log the exact value being used for human ranges
        self.logger.debug(f"Creating reference sheet with human range: '{human_ranges}'")
        
        # Create a BytesIO buffer to store the PDF
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=20
        )
        field_style = ParagraphStyle(
            'FieldStyle',
            parent=styles['Normal'],
            fontSize=12,
            leading=18,
            spaceAfter=10
        )
        
        # Create the content
        elements = []
        
        # Add title
        elements.append(Paragraph("REFERENCE SHEET - OVERSIZED DOCUMENT", title_style))
        elements.append(Spacer(1, 20))
        
        # Add document information
        elements.append(Paragraph(f"<b>Document:</b> {document_name}", field_style))
        elements.append(Paragraph(f"<b>Film Number:</b> {film_number}", field_style))
        elements.append(Paragraph(f"<b>Archive ID:</b> {archive_id}", field_style))
        elements.append(Paragraph(f"<b>Blip:</b> {blip}", field_style))
        elements.append(Paragraph(f"<b>Document Type:</b> {doc_type}", field_style))
        
        self.logger.debug(f"Blip for {document_name}: {blip}")
        
        # Use original label and add the human-readable format directly
        elements.append(Paragraph(f"<b>Oversized Pages:</b> {human_ranges}", field_style))
        
        elements.append(Paragraph(f"<b>Barcode:</b> {barcode}", field_style))
        
        # Add note
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            "This reference sheet points to oversized content stored on 35mm microfilm. "
            "Use the blip information above to locate the content.", field_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        self.logger.info(f"Created reference sheet for document {document_name}, range {human_ranges}")
        
        return pdf_content
    
    def get_reference_sheet_path(self, project, doc_id, range_start, range_end):
        """
        Get the path where a reference sheet should be stored.
        
        Args:
            project: Project object
            doc_id: Document ID
            range_start: Start of page range
            range_end: End of page range
            
        Returns:
            Path object for the reference sheet
        """
        # Create temporary directory structure if it doesn't exist
        temp_dir = Path(project.project_path) / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories if they don't exist
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename for reference sheet
        filename = f"{doc_id}_ref_{range_start}-{range_end}.pdf"
        
        return references_dir / filename
    
    def get_readable_pages(self, document):
        """
        Get the human-readable page descriptions for a document.
        
        Args:
            document: Document object
            
        Returns:
            List of human-readable page descriptions
        """
        # Try to get from database
        readable_pages = list(ReadablePageDescription.objects.filter(
            document=document
        ).order_by('range_index').values_list('description', flat=True))
        
        if readable_pages:
            return readable_pages
        
        return []
        
    def generate_readable_pages(self, document):
        """
        Generate human-readable page descriptions following the original format.
        
        Args:
            document: Document with oversized ranges
            
        Returns:
            List of human-readable page descriptions
        """
        readable_pages = []
        current_count = 1
        doc_oversized = document.total_oversized
        
        self.logger.debug(f"Generating readable pages for document {document.doc_id}")
        self.logger.debug(f"Total oversized pages: {doc_oversized}")
        
        # Get ranges from document
        ranges = list(document.ranges.all().order_by('start_page'))
        
        for i, range_obj in enumerate(ranges):
            start = range_obj.start_page
            end = range_obj.end_page
            range_size = end - start + 1
            
            self.logger.debug(f"Range {i}: ({start}, {end}) has size {range_size}")
            
            if range_size == 1:
                # Single page format: "X von Y"
                human_range = f"{current_count} von {doc_oversized}"
                self.logger.debug(f"Single page format for range {i}: {human_range}")
            else:
                # Range format: "X bis Y von Z"
                human_range = f"{current_count} bis {current_count + range_size - 1} von {doc_oversized}"
                self.logger.debug(f"Multiple page format for range {i}: {human_range}")
            
            # Create or update ReadablePageDescription in database
            ReadablePageDescription.objects.update_or_create(
                document=document,
                range_index=i,
                defaults={'description': human_range}
            )
            
            readable_pages.append(human_range)
            current_count += range_size
        
        self.logger.debug(f"Final readable pages: {readable_pages}")
        return readable_pages
        
    @transaction.atomic
    def insert_reference_sheets(self, project_id, document_id, reference_sheets_data, output_dir=None):
        """
        Insert reference sheets into a document at the appropriate positions.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            reference_sheets_data: List of reference sheet information
            output_dir: Optional output directory override
            
        Returns:
            Path to the document with reference sheets inserted
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.error(f"Invalid document path: {doc_path}")
            return None
        
        # Get reference page insertion points
        reference_pages = list(document.reference_pages.all().values_list('position', flat=True))
        
        # Get adjusted ranges for correct frame positioning
        adjusted_ranges = self.get_adjusted_ranges(document)
        if not adjusted_ranges:
            adjusted_ranges = self.calculate_adjusted_ranges(document)
        
        # Sort reference sheets by range_start (ascending)
        sorted_refs = sorted(reference_sheets_data, key=lambda x: x['range'][0])
        
        # Open the original document
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Current position in the document
            current_page = 0
            
            # Process each reference sheet
            for ref_data in sorted_refs:
                range_start, range_end = ref_data['range']
                ref_path = ref_data['path']
                
                # Add pages before the reference sheet
                while current_page < range_start - 1:
                    writer.add_page(reader.pages[current_page])
                    current_page += 1
                
                # Insert the reference sheet
                with open(ref_path, 'rb') as ref_file:
                    ref_reader = PyPDF2.PdfReader(ref_file)
                    for i in range(len(ref_reader.pages)):
                        writer.add_page(ref_reader.pages[i])
                
                # Continue with regular pages
                # Don't increment current_page as we want to include the oversized pages
            
            # Add remaining pages
            while current_page < len(reader.pages):
                writer.add_page(reader.pages[current_page])
                current_page += 1
        
        # Create the output directory if it doesn't exist
        if output_dir:
            processed_dir = Path(output_dir)
        else:
            processed_dir = Path(project.project_path) / ".temp" / "processed"
        
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the new document
        output_path = processed_dir / doc_path.name
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Create a ProcessedDocument record
        processed_doc = ProcessedDocument.objects.create(
            document=document,
            path=str(output_path),
            processing_type='16mm_with_refs'
        )
        
        self.logger.info(f"Inserted {len(sorted_refs)} reference sheets into {document.doc_id}")
        
        return output_path
    
    def extract_oversized_pages(self, project_id, document_id, range_start, range_end):
        """
        Extract only the oversized pages from a specific range in a document.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            range_start: Start page (1-indexed)
            range_end: End page (1-indexed)
            
        Returns:
            Path to the extracted oversized pages
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the oversized directory if it doesn't exist
        oversized_dir = Path(project.project_path) / ".temp" / "oversized"
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized_{range_start}-{range_end}.pdf"
        output_path = oversized_dir / output_filename
        
        # Extract only the oversized pages within the specified range
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Get oversized page indices (0-based) from document dimensions
            oversized_indices = []
            dimensions = document.dimensions.all()
            if dimensions:
                # dimensions contains (width, height, page_idx, percent_over) tuples
                oversized_indices = [dim.page_idx for dim in dimensions]
            
            # Count pages added for logging
            added_pages = 0
            
            # PDF pages are 0-indexed, but our page ranges are 1-indexed
            for page_idx in range(range_start - 1, min(range_end, len(reader.pages))):
                # Check if this page is in the oversized indices
                if page_idx in oversized_indices:
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
        
        # Only save if we found any oversized pages
        if added_pages > 0:
            # Save the extracted pages
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Create a ProcessedDocument record
            processed_doc = ProcessedDocument.objects.create(
                document=document,
                path=str(output_path),
                processing_type='extracted_oversized',
                start_page=range_start,
                end_page=range_end
            )
            
            self.logger.info(f"Extracted {added_pages} oversized pages from range {range_start}-{range_end} in {document.doc_id}")
            return output_path
        else:
            self.logger.warning(f"No oversized pages found in range {range_start}-{range_end} for {document.doc_id}")
            return None
    
    def get_adjusted_ranges(self, document):
        """
        Get adjusted ranges from database.
        
        Args:
            document: Document object
            
        Returns:
            List of adjusted ranges or None if not found
        """
        adjusted_ranges = list(AdjustedRange.objects.filter(document=document))
        if adjusted_ranges:
            return [
                [adj_range.adjusted_start, adj_range.adjusted_end] 
                for adj_range in adjusted_ranges
            ]
        return None
    
    def calculate_adjusted_ranges(self, document):
        """
        Calculate adjusted page ranges after reference sheet insertion.
        
        Args:
            document: Document with oversized ranges
            
        Returns:
            List of adjusted page ranges accounting for reference sheet shifts
        """
        # Get ranges
        ranges = list(document.ranges.all().order_by('start_page'))
        if not ranges:
            return []
        
        # Get reference pages
        reference_pages = list(document.reference_pages.all().values_list('position', flat=True))
        
        # Sort reference pages
        reference_pages = sorted(reference_pages)
        
        # Calculate adjusted ranges
        adjusted_ranges = []
        shift = 0
        
        for i, range_obj in enumerate(ranges):
            range_start = range_obj.start_page
            range_end = range_obj.end_page
            
            # Calculate shift based on reference sheets inserted before this range
            if reference_pages:
                shift = sum(1 for ref_page in reference_pages if ref_page <= range_start)
            
            # Apply shift to range
            adjusted_start = range_start + shift
            adjusted_end = range_end + shift
            
            # Store adjusted range in database
            AdjustedRange.objects.update_or_create(
                document=document,
                original_start=range_start,
                original_end=range_end,
                defaults={
                    'adjusted_start': adjusted_start,
                    'adjusted_end': adjusted_end
                }
            )
            
            adjusted_ranges.append([adjusted_start, adjusted_end])
        
        return adjusted_ranges
    
    def extract_all_oversized_pages(self, project_id, document_id, output_dir=None):
        """
        Extract all oversized pages from a document.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            output_dir: Optional output directory override
            
        Returns:
            Path to the extracted oversized pages
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the output directory if it doesn't exist
        if output_dir:
            oversized_dir = Path(output_dir)
        else:
            oversized_dir = Path(project.project_path) / ".temp" / "oversized35"
        
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized.pdf"
        output_path = oversized_dir / output_filename
        
        # Extract only the oversized pages
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Get oversized page indices (0-based) from document dimensions
            oversized_indices = []
            dimensions = document.dimensions.all()
            if dimensions:
                # dimensions contains (width, height, page_idx, percent_over) fields
                oversized_indices = [dim.page_idx for dim in dimensions]
            
            # Count pages added for logging
            added_pages = 0
            
            # Add only the oversized pages
            for page_idx in oversized_indices:
                if 0 <= page_idx < len(reader.pages):
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
                    self.logger.debug(f"Added oversized page at index {page_idx} (page {page_idx+1})")
        
        # Only save if we found any oversized pages
        if added_pages > 0:
            # Save the extracted pages
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Create a ProcessedDocument record
            processed_doc = ProcessedDocument.objects.create(
                document=document,
                path=str(output_path),
                processing_type='extracted_oversized'
            )
            
            self.logger.info(f"Extracted {added_pages} oversized pages from {document.doc_id}")
            return output_path
        else:
            self.logger.warning(f"No oversized pages found in {document.doc_id}")
            return None
    
    def insert_reference_sheets_for_35mm(self, project_id, document_id, reference_sheets_data, oversized_path):
        """
        Insert reference sheets into an extracted oversized document for 35mm film.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            reference_sheets_data: List of reference sheet information
            oversized_path: Path to the extracted oversized pages
            
        Returns:
            Path to the document with reference sheets inserted
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        oversized_path = Path(oversized_path)
        if not oversized_path.exists() or oversized_path.suffix.lower() != '.pdf':
            self.logger.error(f"Invalid oversized document path: {oversized_path}")
            return None
        
        # Get the original oversized page indices (0-based) from document
        original_oversized_indices = []
        dimensions = document.dimensions.all()
        if dimensions:
            # dimensions contains (width, height, page_idx, percent_over) fields
            original_oversized_indices = [dim.page_idx for dim in dimensions]
        
        # Create a mapping from original page indices to positions in the extracted document
        original_oversized_indices.sort()
        page_mapping = {}
        for new_idx, orig_idx in enumerate(original_oversized_indices):
            # Convert 0-indexed to 1-indexed for easier comparison with ranges
            orig_page = orig_idx + 1
            page_mapping[orig_page] = new_idx
        
        self.logger.debug(f"Original oversized pages: {original_oversized_indices}")
        self.logger.debug(f"Page mapping: {page_mapping}")
        
        # Create output directory
        processed_dir = Path(project.project_path) / ".temp" / "processed35"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Output filename
        output_filename = f"{document.doc_id}_with_refs.pdf"
        output_path = processed_dir / output_filename
        
        # Sort reference sheets by their range start to ensure proper order
        sorted_refs = sorted(reference_sheets_data, key=lambda x: x['range'][0])
        
        # Open the extracted oversized document
        with open(oversized_path, 'rb') as file:
            oversized_reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # We need to track where to insert each reference sheet in the new document
            current_index = 0
            current_output_index = 0
            
            # Process each reference sheet
            for ref_data in sorted_refs:
                range_start, range_end = ref_data['range']
                ref_path = ref_data['path']
                
                # Find the position in the extracted document where this reference sheet should go
                insert_pos = None
                
                for orig_page, new_pos in page_mapping.items():
                    if range_start <= orig_page <= range_end:
                        # This oversized page falls within the range for this reference sheet
                        insert_pos = new_pos
                        break
                
                if insert_pos is None:
                    self.logger.warning(f"Could not determine insertion position for reference sheet {range_start}-{range_end}")
                    continue
                
                self.logger.debug(f"Inserting reference sheet for range {range_start}-{range_end} before position {insert_pos} in extracted document")
                
                # Add pages up to the insert position
                while current_index < insert_pos:
                    writer.add_page(oversized_reader.pages[current_index])
                    current_index += 1
                    current_output_index += 1
                
                # Insert the reference sheet at this position
                with open(ref_path, 'rb') as ref_file:
                    ref_reader = PyPDF2.PdfReader(ref_file)
                    for i in range(len(ref_reader.pages)):
                        writer.add_page(ref_reader.pages[i])
                        current_output_index += 1
                
                # Note: We don't increment current_index since we haven't yet added the oversized page
                # that should follow this reference sheet
            
            # Add any remaining pages
            while current_index < len(oversized_reader.pages):
                writer.add_page(oversized_reader.pages[current_index])
                current_index += 1
                current_output_index += 1
        
        # Save the new document
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Create a ProcessedDocument record
        processed_doc = ProcessedDocument.objects.create(
            document=document,
            path=str(output_path),
            processing_type='35mm_with_refs'
        )
        
        self.logger.info(f"Inserted {len(sorted_refs)} reference sheets into extracted oversized document for {document.doc_id}")
        
        return output_path
    
    def calculate_range_specific_blip(self, document, base_blip, range_index, oversized_positions):
        """
        Calculate a range-specific blip that accounts for:
        1. Extracting only oversized pages
        2. Renumbering them sequentially
        3. Inserting reference sheets
        
        Args:
            document: Document object
            base_blip: Base blip for the document (e.g., 10000002-0001.00001)
            range_index: Index of the current range
            oversized_positions: List of positions of oversized pages in original document
            
        Returns:
            String with adjusted blip
        """
        try:
            # Parse base blip
            parts = base_blip.split('-')
            film_num = parts[0]
            rest = parts[1].split('.')
            doc_index = rest[0]
            base_frame = int(rest[1])
            
            # Get all oversized page positions
            if not oversized_positions:
                oversized_positions = []
                dimensions = document.dimensions.all()
                if dimensions:
                    oversized_positions = [dim.page_idx + 1 for dim in dimensions]  # Convert from 0-indexed to 1-indexed
            
            # Sort the positions
            oversized_positions = sorted(oversized_positions)
            
            # Count oversized pages and reference sheets before this range
            os_count = 0
            ref_count = 0
            
            # Get ranges from database
            ranges = list(document.ranges.all().order_by('start_page'))
            
            if range_index >= len(ranges):
                self.logger.warning(f"Range index {range_index} out of bounds for document {document.doc_id}")
                return base_blip
                
            current_range = ranges[range_index]
            range_start = current_range.start_page
            
            # Count oversized pages before this range
            for os_pos in oversized_positions:
                if os_pos < range_start:
                    os_count += 1
            
            # Count reference sheets (1 per range) before this range
            ref_count = range_index
            
            # Calculate frame position: base + oversized pages + reference sheets before this range
            target_frame = base_frame + os_count + ref_count
            
            # Create range-specific blip
            range_blip = f"{film_num}-{doc_index}.{target_frame:05d}"
            
            self.logger.debug(f"Calculated range-specific blip: base={base_blip}, result={range_blip} (os_count={os_count}, ref_count={ref_count})")
            
            return range_blip
            
        except Exception as e:
            self.logger.warning(f"Error calculating range blip: {str(e)}")
            return base_blip
    
    def extract_oversized_pages_with_references(self, project_id, document_id, range_start, range_end, processed_path=None):
        """
        Extract ONLY oversized pages and their reference sheets for the 35mm film.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            range_start: Start page (1-indexed)
            range_end: End page (1-indexed)
            processed_path: Optional path to a document with reference sheets already inserted
            
        Returns:
            Path to the extracted pages with reference sheets
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        # Use the processed document if provided, otherwise use the original document
        doc_path = Path(processed_path) if processed_path else Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the oversized directory if it doesn't exist
        oversized_dir = Path(project.project_path) / ".temp" / "oversized35"
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized_with_refs_{range_start}-{range_end}.pdf"
        output_path = oversized_dir / output_filename
        
        # Get oversized page indices (0-based)
        oversized_indices = []
        dimensions = document.dimensions.all()
        if dimensions:
            # dimensions contains (width, height, page_idx, percent_over) tuples
            oversized_indices = [dim.page_idx for dim in dimensions]
        
        # Get reference page indices (1-indexed)
        reference_pages = list(document.reference_pages.all().values_list('position', flat=True))
        
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Track added pages for logging
            added_pages = 0
            added_refs = 0
            added_oversized = 0
            
            # When using processed document, we need to extract ONLY reference sheets and oversized pages
            for page_idx in range(range_start - 1, min(range_end, len(reader.pages))):
                # 0-indexed page_idx+1 gives us the 1-indexed page number
                page_num = page_idx + 1
                
                # Include reference sheets
                if page_num in reference_pages:
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
                    added_refs += 1
                    self.logger.debug(f"Added reference sheet at page {page_num}")
                
                # Include oversized pages
                elif page_idx in oversized_indices:
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
                    added_oversized += 1
                    self.logger.debug(f"Added oversized page at index {page_idx} (page {page_num})")
        
        # Only save if we found any pages to extract
        if added_pages > 0:
            # Save the extracted pages
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Create a ProcessedDocument record
            processed_doc = ProcessedDocument.objects.create(
                document=document,
                path=str(output_path),
                processing_type='35mm_with_refs',
                start_page=range_start,
                end_page=range_end
            )
            
            self.logger.info(f"Extracted {added_pages} pages with references from range {range_start}-{range_end} in {document.doc_id} ({added_refs} reference sheets, {added_oversized} oversized pages)")
            return output_path
        else:
            self.logger.warning(f"No pages to extract from range {range_start}-{range_end} for {document.doc_id}")
            return None
    
    def copy_to_output(self, source_path, destination_dir, doc_id):
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
            self.logger.error(f"Source file not found: {source_path}")
            return False
        
        # Create destination directory if it doesn't exist
        destination_dir = Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        
        # Use the document ID as the filename
        if doc_id.lower().endswith('.pdf'):
            dest_filename = doc_id
        else:
            dest_filename = f"{doc_id}.pdf"
        dest_path = destination_dir / dest_filename
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            self.logger.debug(f"Copied {source_path} to {dest_path}")
            
            # Update the ProcessedDocument record if it exists
            try:
                processed_doc = ProcessedDocument.objects.get(path=str(source_path))
                processed_doc.copied_to_output = True
                processed_doc.output_path = str(dest_path)
                processed_doc.save()
            except ProcessedDocument.DoesNotExist:
                # No record exists, that's okay
                pass
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy file: {str(e)}")
            return False
    
    def clean_temporary_files(self, project_id):
        """
        Clean up temporary files for a project after processing.
        Marks files as deleted in the database but doesn't actually remove them.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Number of records cleaned up
        """
        # Update all ProcessedDocument records for this project
        try:
            project = Project.objects.get(pk=project_id)
            processed_docs = ProcessedDocument.objects.filter(
                document__project=project,
                copied_to_output=True  # Only clean up documents that have been copied to output
            )
            
            cleaned_count = processed_docs.count()
            
            # Mark as cleaned
            processed_docs.update(cleaned=True)
            
            self.logger.info(f"Marked {cleaned_count} temporary files as cleaned for project {project.archive_id}")
            
            return cleaned_count
        except Exception as e:
            self.logger.error(f"Error cleaning temporary files: {str(e)}")
            return 0
            
    def prepare_document_for_distribution(self, project_id, document_id, is_35mm=False):
        """
        Prepare a document for distribution by generating reference sheets and processing it accordingly.
        This is a high-level method used by the distribution service.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            is_35mm: Whether to process for 35mm distribution
            
        Returns:
            Dictionary with information about the processed document
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        if not document.has_oversized:
            self.logger.info(f"Document {document.doc_id} has no oversized pages, no special processing needed")
            return {
                'document_id': document_id,
                'processed': False,
                'reason': 'no_oversized_pages'
            }
        
        try:
            # Generate reference sheets
            reference_sheets = self.generate_reference_sheets_for_document(project_id, document_id)
            
            if not reference_sheets:
                self.logger.warning(f"No reference sheets generated for document {document_id}")
                return {
                    'document_id': document_id,
                    'processed': False,
                    'reason': 'no_reference_sheets_generated'
                }
            
            # Process document based on destination film type
            if is_35mm:
                # Extract oversized pages for 35mm film
                oversized_path = self.extract_all_oversized_pages(project_id, document_id)
                
                if not oversized_path:
                    self.logger.warning(f"Failed to extract oversized pages for document {document_id}")
                    return {
                        'document_id': document_id,
                        'processed': False,
                        'reason': 'failed_to_extract_oversized'
                    }
                
                # Insert reference sheets into extracted oversized pages
                processed_path = self.insert_reference_sheets_for_35mm(
                    project_id, document_id, reference_sheets[document_id], oversized_path
                )
                
                if not processed_path:
                    self.logger.warning(f"Failed to insert reference sheets into 35mm document {document_id}")
                    return {
                        'document_id': document_id,
                        'processed': False,
                        'reason': 'failed_to_insert_references_35mm'
                    }
                
                return {
                    'document_id': document_id,
                    'processed': True,
                    'path': str(processed_path),
                    'film_type': '35mm',
                    'reference_count': len(reference_sheets[document_id])
                }
            else:
                # Insert reference sheets into the document for 16mm film
                processed_path = self.insert_reference_sheets(
                    project_id, document_id, reference_sheets[document_id]
                )
                
                if not processed_path:
                    self.logger.warning(f"Failed to insert reference sheets into 16mm document {document_id}")
                    return {
                        'document_id': document_id,
                        'processed': False,
                        'reason': 'failed_to_insert_references_16mm'
                    }
                
                return {
                    'document_id': document_id,
                    'processed': True,
                    'path': str(processed_path),
                    'film_type': '16mm',
                    'reference_count': len(reference_sheets[document_id])
                }
                
        except Exception as e:
            self.logger.error(f"Error preparing document {document_id} for distribution: {str(e)}")
            return {
                'document_id': document_id,
                'processed': False,
                'reason': 'error',
                'error': str(e)
            }
    
    def generate_reference_sheets_for_document(self, project_id, document_id):
        """
        Generate reference sheets for a specific document.
        
        Args:
            project_id: Project ID
            document_id: Document ID
            
        Returns:
            Dictionary with reference sheet data for the document
        """
        # Get project and document
        project = Project.objects.get(pk=project_id)
        document = Document.objects.get(project=project, doc_id=document_id)
        
        if not document.has_oversized:
            self.logger.info(f"Document {document.doc_id} has no oversized pages, no reference sheets needed")
            return {}
        
        # Check if reference sheets already exist
        existing_reference_sheets = ReferenceSheet.objects.filter(document=document)
        if existing_reference_sheets.exists():
            # Convert to the expected format
            reference_data = {}
            reference_data[document.doc_id] = []
            
            for ref_sheet in existing_reference_sheets:
                reference_data[document.doc_id].append({
                    'path': ref_sheet.path,
                    'range': (ref_sheet.range_start, ref_sheet.range_end),
                    'blip_35mm': ref_sheet.blip_35mm,
                    'film_number_35mm': ref_sheet.film_number_35mm,
                    'id': ref_sheet.id
                })
            
            self.logger.info(f"Using {len(reference_data[document.doc_id])} existing reference sheets for document {document.doc_id}")
            return reference_data
        
        # Generate new reference sheets for just this document
        temp_dir = Path(project.project_path) / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Results dictionary to track reference sheets
        reference_sheets = {}
        reference_sheets[document.doc_id] = []
        
        # Get blip data from film number service
        if self.film_number_manager:
            blip_data = self.film_number_manager.prepare_reference_sheet_data(project)
        else:
            # If no film number manager provided, try to import it
            from .film_number_manager import FilmNumberManager
            film_number_manager = FilmNumberManager(logger=self.logger)
            blip_data = film_number_manager.prepare_reference_sheet_data(project)
        
        # Get document ranges
        ranges = list(document.ranges.all().order_by('start_page'))
        if not ranges:
            self.logger.warning(f"No ranges found for document {document.doc_id}")
            return {}
            
        # Get or generate readable pages
        readable_pages = self.get_readable_pages(document)
        if not readable_pages:
            readable_pages = self.generate_readable_pages(document)
            
        doc_id = document.doc_id
        
        # Get blip data for this document
        doc_blip_data = blip_data.get(doc_id, [])
        
        # Process each oversized range
        for i, range_obj in enumerate(ranges):
            # Get the range
            range_start = range_obj.start_page
            range_end = range_obj.end_page
            
            # Get human-readable page range
            human_range = ""
            if i < len(readable_pages):
                human_range = readable_pages[i]
            else:
                human_range = f"Pages {range_start}-{range_end}"
            
            # Get blip information for this range
            range_blip = None
            film_number_35mm = None
            
            # Try to find matching blip data
            for blip_entry in doc_blip_data:
                if blip_entry.get('range') == (range_start, range_end):
                    range_blip = blip_entry.get('blip_35mm')
                    film_number_35mm = blip_entry.get('film_number_35mm')
                    break
            
            if not range_blip or not film_number_35mm:
                self.logger.warning(f"No 35mm blip found for document {doc_id}, range {range_start}-{range_end}")
                continue
            
            # Create reference sheet
            try:
                reference_sheet = self.create_reference_sheet(
                    document_name=doc_id,
                    film_number=film_number_35mm,
                    archive_id=project.archive_id,
                    blip=range_blip,
                    doc_type=project.doc_type,
                    human_ranges=human_range,
                    barcode=doc_id
                )
                
                # Generate path for reference sheet
                ref_sheet_path = self.get_reference_sheet_path(project, doc_id, range_start, range_end)
                
                # Save reference sheet
                with open(ref_sheet_path, "wb") as f:
                    f.write(reference_sheet)
                
                # Create ReferenceSheet model
                ref_sheet = ReferenceSheet.objects.create(
                    document=document,
                    document_range=range_obj,
                    range_start=range_start,
                    range_end=range_end,
                    path=str(ref_sheet_path),
                    blip_35mm=range_blip,
                    film_number_35mm=film_number_35mm,
                    human_range=human_range
                )
                
                # Add to results
                reference_sheets[doc_id].append({
                    'path': str(ref_sheet_path),
                    'range': (range_start, range_end),
                    'blip_35mm': range_blip,
                    'film_number_35mm': film_number_35mm,
                    'id': ref_sheet.id
                })
                
                self.logger.info(f"Generated reference sheet for {doc_id}, range {range_start}-{range_end}")
                
            except Exception as e:
                self.logger.error(f"Error creating reference sheet for {doc_id}, range {range_start}-{range_end}: {str(e)}")
        
        return reference_sheets

    @transaction.atomic
    def generate_reference_sheets_with_frontend_data(self, project_id, project_data=None, analysis_data=None, allocation_data=None, film_number_results=None):
        """
        Generate reference sheets for a project using frontend data instead of database queries.
        
        Args:
            project_id: ID of the project (used for database reference)
            project_data: Project data from frontend
            analysis_data: Document analysis data from frontend
            allocation_data: Film allocation data from frontend
            film_number_results: Film number results from frontend
            
        Returns:
            Dictionary mapping document IDs to lists of reference sheet paths
        """
        # Log what data was received from frontend
        self.logger.info(f"Received frontend data:")
        self.logger.info(f"- project_data: {type(project_data).__name__}, available: {project_data is not None}")
        self.logger.info(f"- analysis_data: {type(analysis_data).__name__}, available: {analysis_data is not None}")
        self.logger.info(f"- allocation_data: {type(allocation_data).__name__}, available: {allocation_data is not None}")
        self.logger.info(f"- film_number_results: {type(film_number_results).__name__}, available: {film_number_results is not None}")
        
        # Additional debug logging for keys in data structures
        if project_data:
            self.logger.info(f"project_data keys: {list(project_data.keys())}")
        if analysis_data:
            self.logger.info(f"analysis_data keys: {list(analysis_data.keys())}")
        if allocation_data:
            self.logger.info(f"allocation_data keys: {list(allocation_data.keys())}")
        if film_number_results:
            self.logger.info(f"film_number_results keys: {list(film_number_results.keys())}")
        
        # Get the basic project from database (we still need this for the project path)
        project = Project.objects.get(pk=project_id)
        
        # Early return if no analysis data or project has no oversized documents
        if not analysis_data or not analysis_data.get('analysisResults', {}).get('hasOversized', False):
            self.logger.info("No oversized documents found, skipping reference sheet generation")
            return {}
        
        self.logger.info(f"Generating reference sheets for {project.archive_id} using frontend data")
        
        # Create temp directory structure
        temp_dir = Path(project.project_path) / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Results dictionary to track reference sheets
        reference_sheets = {}
        
        # Extract needed data from frontend
        archive_id = project_data.get('projectInfo', {}).get('archiveId', project.archive_id)
        doc_type = project_data.get('projectInfo', {}).get('documentType', 'DOCUMENT')
        
        # Use film_number_manager to get blip data with proper range-specific blips
        if self.film_number_manager:
            blip_data = self.film_number_manager.prepare_reference_sheet_data_with_frontend(
                project, film_number_results
            )
        else:
            # If no film number manager provided, try to import it
            from .film_number_manager import FilmNumberManager
            film_number_manager = FilmNumberManager(logger=self.logger)
            blip_data = film_number_manager.prepare_reference_sheet_data_with_frontend(
                project, film_number_results
            )
        
        # Process documents from analysis data
        documents_data = analysis_data.get('analysisResults', {}).get('documents', [])
        
        # For each document with oversized pages
        for doc_data in documents_data:
            doc_id = doc_data.get('name')
            
            # Skip if document has no oversized pages
            if not doc_data.get('hasOversized', False) or not doc_data.get('oversizedPages'):
                continue
            
            # Get or create document and document range records so we can use ReferenceSheet model
            document, _ = Document.objects.get_or_create(
                project=project,
                doc_id=doc_id,
                defaults={
                    'path': doc_data.get('path', ''),
                    'has_oversized': True
                }
            )
            
            # Prepare ranges from oversized pages
            # Group consecutive page numbers into ranges
            oversized_pages = sorted(doc_data.get('oversizedPages', []))
            ranges = []
            
            if oversized_pages:
                start = oversized_pages[0]
                end = start
                
                for page in oversized_pages[1:]:
                    if page == end + 1:
                        # Consecutive page, extend the range
                        end = page
                    else:
                        # Non-consecutive, start a new range
                        ranges.append((start, end))
                        start = page
                        end = page
                
                # Add the final range
                ranges.append((start, end))
            
            # Create DocumentRange records for each range
            range_objects = []
            for range_start, range_end in ranges:
                range_obj, _ = DocumentRange.objects.get_or_create(
                    document=document,
                    start_page=range_start,
                    end_page=range_end
                )
                range_objects.append(range_obj)
            
            # Generate human-readable page descriptions
            total_oversized = len(oversized_pages)
            readable_pages = []
            current_count = 1
            
            for i, (start, end) in enumerate(ranges):
                range_size = end - start + 1
                
                if range_size == 1:
                    # Single page format: "X von Y"
                    human_range = f"{current_count} von {total_oversized}"
                else:
                    # Range format: "X bis Y von Z"
                    human_range = f"{current_count} bis {current_count + range_size - 1} von {total_oversized}"
                
                # Create or update ReadablePageDescription
                ReadablePageDescription.objects.update_or_create(
                    document=document,
                    range_index=i,
                    defaults={'description': human_range}
                )
                
                readable_pages.append(human_range)
                current_count += range_size
            
            # Prepare for reference sheet generation
            reference_sheets[doc_id] = []
            
            # Get blip data for this document
            doc_blip_data = blip_data.get(doc_id, [])
            
            # Process each range
            for i, ((range_start, range_end), range_obj) in enumerate(zip(ranges, range_objects)):
                # Get human-readable description
                human_range = readable_pages[i] if i < len(readable_pages) else f"Pages {range_start}-{range_end}"
                
                # Find matching blip data for this range
                range_blip = None
                film_number_35mm = None
                
                # Try to find matching blip data
                for blip_entry in doc_blip_data:
                    entry_range = blip_entry.get('range')
                    if entry_range and entry_range[0] == range_start and entry_range[1] == range_end:
                        range_blip = blip_entry.get('blip_35mm')
                        film_number_35mm = blip_entry.get('film_number_35mm')
                        break
                
                # Skip if no blip found
                if not range_blip or not film_number_35mm:
                    self.logger.warning(f"No 35mm blip found for document {doc_id}, range {range_start}-{range_end}")
                    continue
                
                # Create reference sheet
                try:
                    reference_sheet = self.create_reference_sheet(
                        document_name=doc_id,
                        film_number=film_number_35mm,
                        archive_id=archive_id,
                        blip=range_blip,
                        doc_type=doc_type,
                        human_ranges=human_range,
                        barcode=doc_id
                    )
                    
                    # Generate path for reference sheet
                    ref_sheet_path = self.get_reference_sheet_path(project, doc_id, range_start, range_end)
                    
                    # Save reference sheet
                    with open(ref_sheet_path, "wb") as f:
                        f.write(reference_sheet)
                    
                    # Create ReferenceSheet model
                    ref_sheet = ReferenceSheet.objects.create(
                        document=document,
                        document_range=range_obj,
                        range_start=range_start,
                        range_end=range_end,
                        path=str(ref_sheet_path),
                        blip_35mm=range_blip,
                        film_number_35mm=film_number_35mm,
                        human_range=human_range
                    )
                    
                    # Add to results
                    reference_sheets[doc_id].append({
                        'path': str(ref_sheet_path),
                        'range': (range_start, range_end),
                        'blip_35mm': range_blip,
                        'film_number_35mm': film_number_35mm,
                        'id': ref_sheet.id
                    })
                    
                    self.logger.info(f"Generated reference sheet for {doc_id}, range {range_start}-{range_end}")
                    
                except Exception as e:
                    self.logger.error(f"Error creating reference sheet for {doc_id}, range {range_start}-{range_end}: {str(e)}")
        
        # Calculate totals
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        self.logger.info(f"Generated {total_sheets} reference sheets for {len(reference_sheets)} documents")
        
        # At the end, build a more detailed response
        detailed_response = {
            "project_id": project_id,
            "project_type": project.doc_type,
            "archive_id": project.archive_id,
            "reference_sheets": reference_sheets,
            "statistics": {
                "total_documents": len(reference_sheets),
                "total_sheets": sum(len(sheets) for sheets in reference_sheets.values()),
                "documents_with_sheets": list(reference_sheets.keys())
            },
            "documents_details": {},
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        print(f"\033[32mDetailed response: {detailed_response}\033[0m")
        
        # Add detailed information for each document
        for doc_id, sheets in reference_sheets.items():
            detailed_response["documents_details"][doc_id] = {
                "sheet_count": len(sheets),
                "ranges": [(sheet['range'][0], sheet['range'][1]) for sheet in sheets],
                "blips": [sheet['blip_35mm'] for sheet in sheets],
                "film_numbers": [sheet['film_number_35mm'] for sheet in sheets],
                "sheet_ids": [sheet['id'] for sheet in sheets],
                "file_paths": [sheet['path'] for sheet in sheets],
                "human_readable_ranges": []
            }
            
            # Try to get human-readable ranges
            try:
                doc = Document.objects.get(project=project, doc_id=doc_id)
                readable_ranges = ReadablePageDescription.objects.filter(document=doc).order_by('range_index')
                detailed_response["documents_details"][doc_id]["human_readable_ranges"] = [r.description for r in readable_ranges]
            except Exception as e:
                self.logger.error(f"Error fetching readable ranges for {doc_id}: {str(e)}")
        
        self.logger.info(f"Completed reference sheet generation with {detailed_response['statistics']['total_sheets']} sheets")
        return detailed_response
