import os
import random
from reportlab.lib.pagesizes import A4, A2
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
    
    def generate_pdf(self, num_pages, filename=None, oversized_percentage=0.1):
        """
        Generate a PDF with the specified number of pages, with a mix of A4 and A2 pages.
        
        Args:
            num_pages: Number of pages to generate
            filename: Name of the output file (default: generated timestamp)
            oversized_percentage: Percentage of pages that should be A2 (default: 10%)
            
        Returns:
            Path to the generated PDF file and list of page dimensions
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate how many oversized pages to create
        num_oversized = int(num_pages * oversized_percentage)
        num_regular = num_pages - num_oversized
        
        if self.logger:
            print(f"Generating PDF with {num_pages} pages ({num_oversized} oversized)")
        
        # Determine which pages will be oversized
        oversized_indices = random.sample(range(num_pages), num_oversized)
        
        # Create the PDF
        c = canvas.Canvas(filepath)
        
        # Track dimensions for each page
        page_dimensions = []
        
        for i in range(num_pages):
            # Determine page size
            if i in oversized_indices:
                pagesize = A2
                page_type = "A2 (oversized)"
                is_oversized = True
            else:
                pagesize = A4
                page_type = "A4 (regular)"
                is_oversized = False
            
            # Store page dimensions (width, height, page_index, is_oversized)
            page_dimensions.append((pagesize[0], pagesize[1], i, is_oversized))
            
            # Set page size
            c.setPageSize(pagesize)
            
            # Draw page content with big page number
            c.setFont("Helvetica-Bold", 72)
            c.drawString(pagesize[0]/2 - 100, pagesize[1]/2, f"PAGE {i+1}")
            
            # Add A2 label in big letters for oversized pages
            if is_oversized:
                c.setFillColor(red)
                c.setFont("Helvetica-Bold", 100)
                c.drawString(pagesize[0]/2 - 80, pagesize[1]/2 - 100, "A2")
                c.setFillColor(black)
            
            # Add additional page information
            c.setFont("Helvetica", 14)
            c.drawString(72, pagesize[1] - 72, f"Page {i+1} of {num_pages}")
            c.drawString(72, pagesize[1] - 100, f"Page Size: {page_type}")
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

    def generate_multiple_pdfs(self, count, pages_range=(5, 20), oversized_percentage=0.1):
        """
        Generate multiple PDFs with random page counts.
        
        Args:
            count: Number of PDFs to generate
            pages_range: Tuple of (min_pages, max_pages)
            oversized_percentage: Percentage of pages that should be A2
            
        Returns:
            List of paths to generated PDFs
        """
        generated_files = []
        
        for i in range(count):
            # Generate random page count within range
            num_pages = random.randint(pages_range[0], pages_range[1])
            
            # Generate filename
            filename = f"document_{i+1:03d}.pdf"
            
            # Generate PDF
            filepath, _ = self.generate_pdf(
                num_pages=num_pages,
                filename=filename,
                oversized_percentage=oversized_percentage
            )
            
            generated_files.append(filepath)
        
        return generated_files


# 3000 pages no oversizes
pdf = PDFGenerator()

pdf.generate_pdf(3500, oversized_percentage=0.4)

