import os
import random
from reportlab.lib.pagesizes import A4, A3, A2
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red
from datetime import datetime

class PDFGenerator:
    def __init__(self, output_dir=None, logger=None):
        """
        Initialize the PDF Generator.
        
        Args:
            output_dir: Directory to save generated PDFs
            logger: Logger instance for logging
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "generated_pdfs")
        self.logger = logger
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            if self.logger:
                self.logger.info(f"Created output directory: {self.output_dir}")
    
    def generate_pdf(self, num_pages, filename=None, oversized_percentage=0, include_a3=False):
        """
        Generate a PDF with the specified number of pages and size distribution.
        
        Args:
            num_pages: Number of pages to generate
            filename: Name of the output file (default: generated timestamp)
            oversized_percentage: Percentage of pages that should be A2 (default: 0)
            include_a3: Whether to include A3 pages (15% of non-oversized pages)
            
        Returns:
            Path to the generated PDF file and list of page dimensions
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate number of each page type
        num_oversized = int(num_pages * oversized_percentage)
        num_regular = num_pages - num_oversized
        
        # Calculate A3 pages if included
        num_a3 = int(num_regular * 0.15) if include_a3 else 0
        num_a4 = num_regular - num_a3
        
        if self.logger:
            print(f"Generating PDF with {num_pages} pages:")
            print(f"  - A4: {num_a4}")
            print(f"  - A3: {num_a3}")
            print(f"  - A2: {num_oversized}")
        
        # Create page size list
        page_sizes = []
        # Add A4 pages
        page_sizes.extend([A4] * num_a4)
        # Add A3 pages
        page_sizes.extend([A3] * num_a3)
        # Add oversized pages
        page_sizes.extend([A2] * num_oversized)
        
        # Shuffle page sizes to distribute them randomly
        random.shuffle(page_sizes)
        
        # Create the PDF
        c = canvas.Canvas(filepath)
        
        # Track dimensions for each page
        page_dimensions = []
        
        for i, pagesize in enumerate(page_sizes):
            # Store page dimensions (width, height, page_index, is_oversized)
            is_oversized = pagesize == A2
            page_dimensions.append((pagesize[0], pagesize[1], i, is_oversized))
            
            # Set page size
            c.setPageSize(pagesize)
            
            # Draw page content with big page number
            c.setFont("Helvetica-Bold", 72)
            c.drawString(pagesize[0]/2 - 100, pagesize[1]/2, f"PAGE {i+1}")
            
            # Add page size label
            size_label = "A2" if pagesize == A2 else "A3" if pagesize == A3 else "A4"
            c.setFillColor(red)
            c.setFont("Helvetica-Bold", 100)
            c.drawString(pagesize[0]/2 - 80, pagesize[1]/2 - 100, size_label)
            c.setFillColor(black)
            
            # Add additional page information
            c.setFont("Helvetica", 14)
            c.drawString(72, pagesize[1] - 72, f"Page {i+1} of {num_pages}")
            c.drawString(72, pagesize[1] - 100, f"Page Size: {size_label}")
            c.drawString(72, pagesize[1] - 120, f"Dimensions: {pagesize[0]} x {pagesize[1]} points")
            
            # Draw page border
            c.rect(36, 36, pagesize[0] - 72, pagesize[1] - 72)
            
            # Add page number at bottom
            c.setFont("Helvetica", 10)
            c.drawString(pagesize[0] / 2, 20, f"{i+1}")
            
            # Move to next page
            c.showPage()
        
        # Save the PDF
        c.save()
        
        if self.logger:
            self.logger.info(f"Generated PDF saved to: {filepath}")
        
        return filepath, page_dimensions

    def generate_multiple_pdfs(self, count, pages_range=(10, 100), oversized_percentage=0, include_a3_ratio=0.2):
        """
        Generate multiple PDFs with random page counts.
        
        Args:
            count: Number of PDFs to generate
            pages_range: Tuple of (min_pages, max_pages)
            oversized_percentage: Percentage of pages that should be A2
            include_a3_ratio: Percentage of documents that should include A3 pages
            
        Returns:
            List of paths to generated PDFs
        """
        generated_files = []
        
        # Determine which documents will have A3 pages
        docs_with_a3 = random.sample(range(count), int(count * include_a3_ratio))
        
        for i in range(count):
            # Generate random page count within range
            num_pages = random.randint(pages_range[0], pages_range[1])
            
            # Generate filename
            filename = f"document_{i+1:03d}.pdf"
            
            # Generate PDF
            filepath, _ = self.generate_pdf(
                num_pages=num_pages,
                filename=filename,
                oversized_percentage=oversized_percentage,
                include_a3=(i in docs_with_a3)
            )
            
            generated_files.append(filepath)
        
        return generated_files


# 3000 pages no oversizes
pdf = PDFGenerator()

pdf.generate_pdf(3500, oversized_percentage=0.4)

