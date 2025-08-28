#!/usr/bin/env python3
"""
Test PDF Generator for White Page Detection

Creates a PDF with various page types to test the white page detection script:
- Fully white pages
- Pages with small black artifacts (scanning artifacts)
- Pages with lots of text
- Pages with minimal text (headers/footers)
- Pages with only page numbers
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import random
import sys
from pathlib import Path


class TestPDFGenerator:
    """Generates test PDFs for white page detection testing."""
    
    def __init__(self, output_path: str = "test_white_pages.pdf"):
        self.output_path = output_path
        self.page_width, self.page_height = letter  # 8.5 x 11 inches
        
    def create_test_pdf(self):
        """Create the complete test PDF with various page types."""
        c = canvas.Canvas(self.output_path, pagesize=letter)
        
        print(f"Creating test PDF: {self.output_path}")
        print("=" * 50)
        
        # Page 1: Completely white page
        print("Page 1: Completely white page")
        self._create_white_page(c)
        c.showPage()
        
        # Page 2: White page with tiny black dot (artifact simulation)
        print("Page 2: White page with tiny black artifact")
        self._create_artifact_page(c, num_artifacts=1, size=1)
        c.showPage()
        
        # Page 3: White page with multiple small artifacts
        print("Page 3: White page with multiple small artifacts")
        self._create_artifact_page(c, num_artifacts=5, size=2)
        c.showPage()
        
        # Page 4: Page with lots of text
        print("Page 4: Page with lots of text")
        self._create_text_heavy_page(c)
        c.showPage()
        
        # Page 5: Page with minimal header text
        print("Page 5: Page with minimal header text")
        self._create_minimal_header_page(c)
        c.showPage()
        
        # Page 6: Page with minimal footer text
        print("Page 6: Page with minimal footer text")
        self._create_minimal_footer_page(c)
        c.showPage()
        
        # Page 7: Page with only page number at bottom
        print("Page 7: Page with only page number")
        self._create_page_number_only(c, page_num=7)
        c.showPage()
        
        # Page 8: Completely white page again
        print("Page 8: Another completely white page")
        self._create_white_page(c)
        c.showPage()
        
        # Page 9: Page with very small text in corner
        print("Page 9: Page with tiny text in corner")
        self._create_tiny_corner_text(c)
        c.showPage()
        
        # Page 10: Page with medium artifacts (larger spots)
        print("Page 10: Page with medium-sized artifacts")
        self._create_artifact_page(c, num_artifacts=3, size=5)
        c.showPage()
        
        # Page 11: Page with single word in center
        print("Page 11: Page with single word in center")
        self._create_single_word_page(c)
        c.showPage()
        
        # Page 12: Final white page
        print("Page 12: Final white page")
        self._create_white_page(c)
        
        c.save()
        print(f"\nTest PDF created successfully: {self.output_path}")
        print(f"Total pages: 12")
        
    def _create_white_page(self, canvas_obj):
        """Create a completely white page."""
        # Just create a blank page - reportlab defaults to white background
        pass
    
    def _create_artifact_page(self, canvas_obj, num_artifacts: int = 1, size: int = 1):
        """Create a white page with small black artifacts (dots/spots)."""
        canvas_obj.setFillColor(black)
        
        for _ in range(num_artifacts):
            # Random position on page
            x = random.uniform(50, self.page_width - 50)
            y = random.uniform(50, self.page_height - 50)
            
            # Create small black circle (artifact)
            canvas_obj.circle(x, y, size, fill=1)
    
    def _create_text_heavy_page(self, canvas_obj):
        """Create a page with lots of text content."""
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.setFillColor(black)
        
        # Title
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(50, self.page_height - 50, "Sample Document with Heavy Text Content")
        
        # Body text
        canvas_obj.setFont("Helvetica", 11)
        y_position = self.page_height - 100
        
        paragraphs = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor",
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis",
            "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore",
            "eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,",
            "sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "",
            "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium",
            "doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore",
            "veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim",
            "ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia",
            "consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.",
            "",
            "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis",
            "praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias",
            "excepturi sint occaecati cupiditate non provident, similique sunt in culpa",
            "qui officia deserunt mollitia animi, id est laborum et dolorum fuga.",
        ]
        
        for paragraph in paragraphs:
            if paragraph:  # Skip empty lines
                canvas_obj.drawString(50, y_position, paragraph)
            y_position -= 20
            if y_position < 100:  # Don't go too close to bottom
                break
    
    def _create_minimal_header_page(self, canvas_obj):
        """Create a page with only a small header."""
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(black)
        canvas_obj.drawString(50, self.page_height - 30, "Document Header - Confidential")
    
    def _create_minimal_footer_page(self, canvas_obj):
        """Create a page with only a small footer."""
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(black)
        canvas_obj.drawString(50, 30, "© 2024 Test Document - All Rights Reserved")
    
    def _create_page_number_only(self, canvas_obj, page_num: int):
        """Create a page with only a page number at the bottom."""
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.setFillColor(black)
        # Center the page number
        page_text = str(page_num)
        text_width = canvas_obj.stringWidth(page_text, "Helvetica", 10)
        x_center = (self.page_width - text_width) / 2
        canvas_obj.drawString(x_center, 30, page_text)
    
    def _create_tiny_corner_text(self, canvas_obj):
        """Create a page with very small text in the corner."""
        canvas_obj.setFont("Helvetica", 6)
        canvas_obj.setFillColor(black)
        canvas_obj.drawString(self.page_width - 100, self.page_height - 20, "Draft v1.0")
    
    def _create_single_word_page(self, canvas_obj):
        """Create a page with a single word in the center."""
        canvas_obj.setFont("Helvetica", 14)
        canvas_obj.setFillColor(black)
        word = "SAMPLE"
        text_width = canvas_obj.stringWidth(word, "Helvetica", 14)
        x_center = (self.page_width - text_width) / 2
        y_center = self.page_height / 2
        canvas_obj.drawString(x_center, y_center, word)


def main():
    """Main function to create the test PDF."""
    output_file = sys.argv[1] if len(sys.argv) > 1 else "test_white_pages.pdf"
    
    # Set random seed for reproducible artifacts
    random.seed(42)
    
    try:
        generator = TestPDFGenerator(output_file)
        generator.create_test_pdf()
        
        print("\n" + "=" * 50)
        print("TEST PDF SUMMARY:")
        print("=" * 50)
        print("Page  1: Completely white")
        print("Page  2: White + 1 tiny artifact")
        print("Page  3: White + 5 small artifacts")
        print("Page  4: Heavy text content")
        print("Page  5: Minimal header only")
        print("Page  6: Minimal footer only")
        print("Page  7: Page number only")
        print("Page  8: Completely white")
        print("Page  9: Tiny corner text")
        print("Page 10: Medium artifacts")
        print("Page 11: Single word center")
        print("Page 12: Completely white")
        print("\nUse this PDF to test different white detection thresholds!")
        print(f"Example: python detect_white_pages.py {output_file} 0.99")
        
        return 0
        
    except Exception as e:
        print(f"Error creating test PDF: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 