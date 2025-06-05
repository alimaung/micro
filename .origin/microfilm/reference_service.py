class ReferenceSheetService:
    def __init__(self, film_number_service, logger=None):
        self.film_number_service = film_number_service
        self.logger = logger
        
    def generate_reference_sheets(self, project, active_roll=None):
        """
        Generate all reference sheets for a project with oversized documents.
        Only creates reference sheets in the references directory.
        
        Args:
            project: Project object with oversized documents
            
        Returns:
            Dictionary mapping document IDs to lists of reference sheet paths
        """
        if not project.has_oversized:
            self.logger.reference_info("No oversized documents found, skipping reference sheet generation")
            return {}
        
        self.logger.section("Reference Sheet Generation")
        self.logger.reference_info(f"Generating reference sheets for {project.documents_with_oversized} documents")
        
        # Create temp directory structure
        temp_dir = project.project_path / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Results dictionary to track reference sheets
        reference_sheets = {}
        
        # Get 35mm blip data from film number service
        self.logger.reference_warning("Preparing reference sheet data")
        blip_data = self.film_number_service.prepare_reference_sheet_data(project)
        
        print(blip_data)
        
        # Process each document with oversized pages
        for document in project.documents:
            if not document.has_oversized or not document.ranges:
                continue
            
            # Calculate adjusted ranges if not already present
            if not hasattr(document, 'adjusted_ranges'):
                document.adjusted_ranges = self.calculate_adjusted_ranges(document)
            
            # Always regenerate human-readable page ranges to ensure they're correct
            if hasattr(document, 'readable_pages'):
                self.logger.reference_debug(f"Replacing existing readable pages for {document.doc_id}: {document.readable_pages}")
            
            document.readable_pages = self.generate_readable_pages(document)
            self.logger.reference_warning(f"Using generated readable pages for {document.doc_id}: {document.readable_pages}")
            
            doc_id = document.doc_id
            reference_sheets[doc_id] = []
            
            # Get the base 35mm blip for this document
            base_blip = None
            if doc_id in blip_data and blip_data[doc_id]:
                base_blip = blip_data[doc_id][0].get('blip_35mm')
                film_number_35mm = blip_data[doc_id][0].get('film_number_35mm')
            
            # Get all oversized positions from document dimensions
            oversized_positions = []
            if hasattr(document, 'dimensions') and document.dimensions:
                for dim in document.dimensions:
                    oversized_positions.append(dim[2] + 1)  # Convert 0-indexed to 1-indexed
            oversized_positions = sorted(oversized_positions)
            
            # Process each oversized range
            for i, (range_start, range_end) in enumerate(document.ranges):
                # Get human-readable page range
                human_range = f"Pages {range_start}-{range_end}"
                if hasattr(document, 'readable_pages') and i < len(document.readable_pages):
                    human_range = document.readable_pages[i]
                    self.logger.reference_debug(f"Using human range for index {i}: {human_range}")
                else:
                    self.logger.reference_warning(f"No readable page for index {i}, using default: {human_range}")
                
                # Calculate the specific blip for this reference sheet
                range_blip = None
                if base_blip:
                    range_blip = self.calculate_range_specific_blip(
                        document, base_blip, i, oversized_positions
                    )
                    self.logger.reference_warning(f"Calculated range-specific blip {range_blip} for range {range_start}-{range_end}")
                
                # If still no range blip, try to find one in the blip data
                if not range_blip and doc_id in blip_data:
                    for range_info in blip_data[doc_id]:
                        if range_info['range'] == (range_start, range_end):
                            range_blip = range_info['blip_35mm']
                            film_number_35mm = range_info['film_number_35mm']
                            break
                
                # Skip if still no blip
                if not range_blip or not film_number_35mm:
                    self.logger.reference_warning(f"No 35mm blip found for document {doc_id}, range {range_start}-{range_end}")
                    continue
                
                # Create reference sheet
                try:
                    reference_sheet = self.create_reference_sheet(
                        document_name=doc_id,
                        film_number=film_number_35mm,
                        archive_id=project.archive_id,
                        blip=range_blip,  # Use the range-specific blip
                        doc_type=project.doc_type,
                        human_ranges=human_range,
                        barcode=doc_id
                    )
                    
                    # Save reference sheet
                    ref_sheet_path = self.get_reference_sheet_path(project, doc_id, range_start, range_end)
                    with open(ref_sheet_path, "wb") as f:
                        f.write(reference_sheet)
                    
                    # Add to results
                    reference_sheets[doc_id].append({
                        'path': str(ref_sheet_path),
                        'range': (range_start, range_end),
                        'blip_35mm': range_blip,
                        'film_number_35mm': film_number_35mm
                    })
                    
                    self.logger.reference_success(f"Generated reference sheet for {doc_id}, range {range_start}-{range_end}")
                    
                except Exception as e:
                    self.logger.reference_error(f"Error creating reference sheet for {doc_id}, range {range_start}-{range_end}: {str(e)}")
        
        # Store reference sheet data in project
        project.reference_sheets = reference_sheets
        
        total_sheets = sum(len(sheets) for sheets in reference_sheets.values())
        self.logger.reference_success(f"Generated {total_sheets} reference sheets for {len(reference_sheets)} documents")
        
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
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        
        # Log the exact value being used for human ranges
        self.logger.reference_debug(f"Creating reference sheet with human range: '{human_ranges}'")
        
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
        
        self.logger.reference_warning(f"Blip for {document_name}: {blip}")
        
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
        
        self.logger.reference_info(f"Created reference sheet for document {document_name}, range {human_ranges}")
        
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
        temp_dir = project.project_path / ".temp"
        references_dir = temp_dir / "references"
        
        # Create directories if they don't exist
        references_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename for reference sheet
        filename = f"{doc_id}_ref_{range_start}-{range_end}.pdf"
        
        return references_dir / filename
    
    def insert_reference_sheets(self, project, document, reference_sheets_data, output_dir=None):
        """
        Insert reference sheets into a document at the appropriate positions.
        
        Args:
            project: Project object
            document: Document object
            reference_sheets_data: List of reference sheet information
            output_dir: Optional output directory override
            
        Returns:
            Path to the document with reference sheets inserted
        """
        import PyPDF2
        from pathlib import Path
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.reference_error(f"Invalid document path: {doc_path}")
            return None
        
        # Get reference page insertion points
        reference_pages = document.reference_pages if hasattr(document, 'reference_pages') else []
        
        # Get adjusted ranges for correct frame positioning
        adjusted_ranges = document.adjusted_ranges if hasattr(document, 'adjusted_ranges') else self.calculate_adjusted_ranges(document)
        
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
            processed_dir = output_dir
        else:
            processed_dir = project.project_path / ".temp" / "processed"
        
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the new document
        output_path = processed_dir / doc_path.name
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        self.logger.reference_success(f"Inserted {len(sorted_refs)} reference sheets into {document.doc_id}")
        
        return output_path
    
    def extract_oversized_pages(self, project, document, range_start, range_end):
        """
        Extract only the oversized pages from a specific range in a document.
        
        Args:
            project: Project object
            document: Document object
            range_start: Start page (1-indexed)
            range_end: End page (1-indexed)
            
        Returns:
            Path to the extracted oversized pages
        """
        import PyPDF2
        from pathlib import Path
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.reference_error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the oversized directory if it doesn't exist
        oversized_dir = project.project_path / ".temp" / "oversized"
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized_{range_start}-{range_end}.pdf"
        output_path = oversized_dir / output_filename
        
        # Extract only the oversized pages within the specified range
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Get oversized page indices (0-based)
            oversized_indices = []
            if hasattr(document, 'dimensions') and document.dimensions:
                # dimensions contains (width, height, page_index, percent_over) tuples
                oversized_indices = [dim[2] for dim in document.dimensions]
            
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
            
            self.logger.reference_success(f"Extracted {added_pages} oversized pages from range {range_start}-{range_end} in {document.doc_id}")
            return output_path
        else:
            self.logger.reference_warning(f"No oversized pages found in range {range_start}-{range_end} for {document.doc_id}")
            return None
    
    def calculate_adjusted_ranges(self, document):
        """
        Calculate adjusted page ranges after reference sheet insertion.
        
        Args:
            document: Document with oversized ranges
            
        Returns:
            List of adjusted page ranges accounting for reference sheet shifts
        """
        if not document.has_oversized or not document.ranges:
            return []
        
        # Get original ranges and reference pages
        original_ranges = document.ranges
        reference_pages = document.reference_pages if hasattr(document, 'reference_pages') else []
        
        # Sort reference pages
        reference_pages = sorted(reference_pages)
        
        # Calculate adjusted ranges
        adjusted_ranges = []
        shift = 0
        
        for i, (range_start, range_end) in enumerate(original_ranges):
            # Calculate shift based on reference sheets inserted before this range
            if reference_pages:
                shift = sum(1 for ref_page in reference_pages if ref_page <= range_start)
            
            # Apply shift to range
            adjusted_start = range_start + shift
            adjusted_end = range_end + shift
            
            adjusted_ranges.append([adjusted_start, adjusted_end])
        
        return adjusted_ranges
    
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
        
        self.logger.reference_debug(f"Generating readable pages for document {document.doc_id} with ranges: {document.ranges}")
        self.logger.reference_debug(f"Total oversized pages: {doc_oversized}")
        
        for i, (start, end) in enumerate(document.ranges):
            range_size = end - start + 1
            self.logger.reference_debug(f"Range {i}: ({start}, {end}) has size {range_size}")
            
            if range_size == 1:
                # Single page format: "X von Y"
                human_range = f"{current_count} von {doc_oversized}"
                self.logger.reference_debug(f"Single page format for range {i}: {human_range}")
            else:
                # Range format: "X bis Y von Z"
                human_range = f"{current_count} bis {current_count + range_size - 1} von {doc_oversized}"
                self.logger.reference_debug(f"Multiple page format for range {i}: {human_range}")
            
            readable_pages.append(human_range)
            current_count += range_size
        
        self.logger.reference_debug(f"Final readable pages: {readable_pages}")
        return readable_pages
    
    def extract_oversized_pages_with_references(self, project, document, range_start, range_end, processed_path=None):
        """
        Extract ONLY oversized pages and their reference sheets for the 35mm film.
        
        Args:
            project: Project object
            document: Document object
            range_start: Start page (1-indexed)
            range_end: End page (1-indexed)
            processed_path: Optional path to a document with reference sheets already inserted
            
        Returns:
            Path to the extracted pages with reference sheets
        """
        import PyPDF2
        from pathlib import Path
        
        # Use the processed document if provided, otherwise use the original document
        doc_path = Path(processed_path) if processed_path else Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.reference_error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the oversized directory if it doesn't exist
        oversized_dir = project.project_path / ".temp" / "oversized35"
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized_with_refs_{range_start}-{range_end}.pdf"
        output_path = oversized_dir / output_filename
        
        # Get oversized page indices (0-based)
        oversized_indices = []
        if hasattr(document, 'dimensions') and document.dimensions:
            # dimensions contains (width, height, page_index, percent_over) tuples
            oversized_indices = [dim[2] for dim in document.dimensions]
        
        # Get reference page indices (1-indexed)
        reference_pages = []
        if hasattr(document, 'reference_pages'):
            reference_pages = document.reference_pages
        
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
                    self.logger.reference_debug(f"Added reference sheet at page {page_num}")
                
                # Include oversized pages
                elif page_idx in oversized_indices:
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
                    added_oversized += 1
                    self.logger.reference_debug(f"Added oversized page at index {page_idx} (page {page_num})")
        
        # Only save if we found any pages to extract
        if added_pages > 0:
            # Save the extracted pages
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.logger.reference_success(f"Extracted {added_pages} pages with references from range {range_start}-{range_end} in {document.doc_id} ({added_refs} reference sheets, {added_oversized} oversized pages)")
            return output_path
        else:
            self.logger.reference_warning(f"No pages to extract from range {range_start}-{range_end} for {document.doc_id}")
            return None
    
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
                for dim in document.dimensions:
                    oversized_positions.append(dim[2] + 1)  # Convert from 0-indexed to 1-indexed
            
            # Sort the positions
            oversized_positions = sorted(oversized_positions)
            
            # Count oversized pages and reference sheets before this range
            os_count = 0
            ref_count = 0
            
            current_range = document.ranges[range_index]
            range_start = current_range[0]
            
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
            
            return range_blip
            
        except Exception as e:
            self.logger.reference_warning(f"Error calculating range blip: {str(e)}")
            return base_blip
    
    def extract_all_oversized_pages(self, project, document, output_dir=None):
        """
        Extract all oversized pages from a document.
        
        Args:
            project: Project object
            document: Document object
            output_dir: Optional output directory override
            
        Returns:
            Path to the extracted oversized pages
        """
        import PyPDF2
        from pathlib import Path
        
        doc_path = Path(document.path)
        if not doc_path.exists() or doc_path.suffix.lower() != '.pdf':
            self.logger.reference_error(f"Invalid document path: {doc_path}")
            return None
        
        # Create the output directory if it doesn't exist
        if output_dir:
            oversized_dir = output_dir
        else:
            oversized_dir = project.project_path / ".temp" / "oversized35"
        
        oversized_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_filename = f"{document.doc_id}_oversized.pdf"
        output_path = oversized_dir / output_filename
        
        # Extract only the oversized pages
        with open(doc_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            # Get oversized page indices (0-based)
            oversized_indices = []
            if hasattr(document, 'dimensions') and document.dimensions:
                # dimensions contains (width, height, page_index, percent_over) tuples
                oversized_indices = [dim[2] for dim in document.dimensions]
            
            # Count pages added for logging
            added_pages = 0
            
            # Add only the oversized pages
            for page_idx in oversized_indices:
                if 0 <= page_idx < len(reader.pages):
                    writer.add_page(reader.pages[page_idx])
                    added_pages += 1
                    self.logger.reference_debug(f"Added oversized page at index {page_idx} (page {page_idx+1})")
        
        # Only save if we found any oversized pages
        if added_pages > 0:
            # Save the extracted pages
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.logger.reference_success(f"Extracted {added_pages} oversized pages from {document.doc_id}")
            return output_path
        else:
            self.logger.reference_warning(f"No oversized pages found in {document.doc_id}")
            return None
    
    def insert_reference_sheets_for_35mm(self, project, document, reference_sheets_data, oversized_path):
        """
        Insert reference sheets into an extracted oversized document for 35mm film.
        
        Args:
            project: Project object
            document: Document object
            reference_sheets_data: List of reference sheet information
            oversized_path: Path to the extracted oversized pages
            
        Returns:
            Path to the document with reference sheets inserted
        """
        import PyPDF2
        from pathlib import Path
        
        oversized_path = Path(oversized_path)
        if not oversized_path.exists() or oversized_path.suffix.lower() != '.pdf':
            self.logger.reference_error(f"Invalid oversized document path: {oversized_path}")
            return None
        
        # Get the original oversized page indices (0-based) from document
        original_oversized_indices = []
        if hasattr(document, 'dimensions') and document.dimensions:
            # dimensions contains (width, height, page_index, percent_over) tuples
            original_oversized_indices = [dim[2] for dim in document.dimensions]
        
        # Create a mapping from original page indices to positions in the extracted document
        original_oversized_indices.sort()
        page_mapping = {}
        for new_idx, orig_idx in enumerate(original_oversized_indices):
            # Convert 0-indexed to 1-indexed for easier comparison with ranges
            orig_page = orig_idx + 1
            page_mapping[orig_page] = new_idx
        
        self.logger.reference_debug(f"Original oversized pages: {original_oversized_indices}")
        self.logger.reference_debug(f"Page mapping: {page_mapping}")
        
        # Create output directory
        processed_dir = project.project_path / ".temp" / "processed35"
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
                    self.logger.reference_warning(f"Could not determine insertion position for reference sheet {range_start}-{range_end}")
                    continue
                
                self.logger.reference_debug(f"Inserting reference sheet for range {range_start}-{range_end} before position {insert_pos} in extracted document")
                
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
        
        self.logger.reference_success(f"Inserted {len(sorted_refs)} reference sheets into extracted oversized document for {document.doc_id}")
        
        return output_path