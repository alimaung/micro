"""
Film label generator module for microfilm processing.

This module handles the generation of film labels for oversized documents.
"""

import os
import logging
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

logger = logging.getLogger(__name__)

class FilmLabelGenerator:
    """Service for generating film labels for oversized documents."""
    
    def __init__(self, logger=None, img_dir=None):
        """
        Initialize the film label generator.
        
        Args:
            logger: Optional logger instance
            img_dir: Optional path to images directory. If not provided, will use default path.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logo_path = r"Y:\micro\micro\microapp\static\microapp\img\branding\RR_TheBadge_Monochrome.png"

    def create_film_label(self, film_number, archive_id, doc_type):
        """
        Create a single film label with tables.
        
        Args:
            film_number: Film number from 35mm roll
            archive_id: Archive ID from project
            doc_type: Document type from project
            
        Returns:
            bytes: The PDF content as bytes
        """
        # Create a BytesIO buffer to store the PDF
        buffer = BytesIO()
        
        # Create the PDF canvas directly
        c = canvas.Canvas(buffer, pagesize=A6)
        
        # Define margins in mm
        margins = {
            'top': 12.5 * mm,     # 0.49 inches = ~12.5 mm
            'bottom': 5 * mm,     # 0.2 inches = 5 mm
            'left': 7 * mm,       # Increased by 2mm
            'right': 7 * mm,      # Increased by 2mm
            'gutter': 0 * mm      # Left gutter position
        }
        
        # Get page dimensions
        page_width, page_height = A6
        
        # Calculate available width and height for tables
        available_width = page_width - (margins['left'] + margins['right'])
        available_height = page_height - (margins['top'] + margins['bottom'])

        # Draw tables
        c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))  # Very light grey (RGB: 217,217,217)
        
        # Define common measurements
        padding = 4 * mm  # Increased padding for text
        
        # Starting position for first table (from top margin)
        current_y = page_height - margins['top']
        
        def draw_table_with_text(y_pos):
            """Helper function to draw table with text at given y position"""
            # Draw table with light grey border
            c.rect(margins['left'], y_pos - 20*mm, available_width, 20*mm, stroke=1, fill=0)
            
            # Set font sizes
            header_font_size = 16
            data_font_size = 14
            
            # Calculate text positions with increased padding
            left_x = margins['left'] + padding
            right_x = margins['left'] + available_width - padding
            
            # Top row with regular font
            top_y = y_pos - padding - 14  # Adjusted for larger font
            c.setFont("Helvetica", header_font_size)
            c.drawString(left_x, top_y, "Iron Mountain")
            
            # Right-aligned text
            top_right_text = "Original"
            top_right_width = c.stringWidth(top_right_text, "Helvetica", header_font_size)
            c.drawString(right_x - top_right_width, top_y, top_right_text)
            
            # Bottom row with bold font
            bottom_y = y_pos - 20*mm + padding + 3  # Adjusted for larger font
            c.setFont("Helvetica-Bold", data_font_size)
            c.drawString(left_x, bottom_y, archive_id)
            
            # Right-aligned text
            bottom_right_width = c.stringWidth(film_number, "Helvetica-Bold", data_font_size)
            c.drawString(right_x - bottom_right_width, bottom_y, film_number)
        
        # First table
        draw_table_with_text(current_y)
        current_y -= 20*mm
        
        # Second table
        draw_table_with_text(current_y)
        current_y -= 20*mm
        
        # Third table: 60mm height (increased from 55mm)
        c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))  # Very light grey
        c.rect(margins['left'], current_y - 60*mm, available_width, 60*mm, stroke=1, fill=0)
        
        # Add logo to top right of third table
        logo_width = 0  # Default value if logo fails to load
        try:
            if os.path.exists(self.logo_path):
                # Original logo dimensions
                logo_width, logo_height = 1317, 1772
                
                # Target height for logo (30mm)
                target_height = 25 * mm
                # Calculate width maintaining aspect ratio
                target_width = (logo_width / logo_height) * target_height
                logo_width = target_width  # Store for text wrapping
                
                # Position logo in top right of third table, with 1mm offset
                logo_x = margins['left'] + available_width - target_width - (1 * mm)
                logo_y = current_y - target_height - (1 * mm)
                
                c.drawImage(self.logo_path, logo_x, logo_y, width=target_width, height=target_height)
        except Exception as e:
            self.logger.warning(f"Could not add logo: {str(e)}")
        
        # Add "Inhalt:" at top of third table
        inhalt_font_size = 16
        c.setFont("Helvetica", inhalt_font_size)  # Same size as header in first table
        inhalt_y = current_y - padding - 14
        c.drawString(margins['left'] + padding, inhalt_y, "Inhalt:")
        
        # Add mock data in bold at bottom of table with reduced font size
        doc_type_font = "Helvetica-Bold"
        doc_type_base_size = 16  # Reduced from 18 by 4 points
        
        # Calculate available width for text (accounting for logo)
        text_width = available_width - logo_width - padding * 2
        
        # Calculate bottom_y position first (needed for collision detection)
        bottom_y = current_y - 60*mm  # Bottom of table (adjusted for new height)
        
        # Function to split text into lines based on available width
        def split_text_to_lines(text, available_width, canvas, font_name, font_size):
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                width = canvas.stringWidth(test_line, font_name, font_size)
                
                if width <= available_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
        
        def check_text_collision(text, font_size, start_y):
            """Check if text lines would collide with 'Inhalt:' text"""
            c.setFont(doc_type_font, font_size)
            lines = split_text_to_lines(text, text_width, c, doc_type_font, font_size)
            line_height = font_size * 1.2
            
            # Calculate top position of wrapped text
            text_top_y = bottom_y + padding + 35 + (len(lines) - 1) * line_height
            
            # Add a small buffer (2mm) to avoid text being too close
            buffer_space = 2 * mm
            
            # Check if top of text would overlap with "Inhalt:" (including buffer)
            return text_top_y + buffer_space > inhalt_y - inhalt_font_size
        
        # Function to find optimal font size
        def find_optimal_font_size(text, start_size, min_size=8):
            current_size = start_size
            while current_size > min_size and check_text_collision(text, current_size, inhalt_y):
                current_size -= 0.5
            return current_size
        
        # Get optimal font size
        doc_type_size = find_optimal_font_size(doc_type, doc_type_base_size)
        c.setFont(doc_type_font, doc_type_size)
        
        # Split doc_type text and draw it with optimal size
        doc_type_lines = split_text_to_lines(doc_type, text_width, c, doc_type_font, doc_type_size)
        
        # Draw doc_type lines with appropriate spacing
        line_height = doc_type_size * 1.2  # 1.2 is the line spacing factor
        for i, line in enumerate(doc_type_lines):
            y_position = bottom_y + padding + 35 + (len(doc_type_lines) - 1 - i) * line_height
            c.drawString(margins['left'] + padding, y_position, line)
        
        # Draw archive_id
        c.setFont("Helvetica-Bold", 20)
        c.drawString(margins['left'] + padding, bottom_y + padding + 5, archive_id)
        
        current_y -= 60*mm
        
        # Fourth table: 15mm height (decreased from 20mm)
        c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))  # Very light grey
        c.rect(margins['left'], current_y - 15*mm, available_width, 15*mm, stroke=1, fill=0)
        
        # Add centered text to fourth table
        c.setFont("Helvetica", 10)  # Smaller font for address
        
        # Calculate center positions
        center_x = margins['left'] + (available_width / 2)
        
        # Calculate vertical center of the table (15mm height)
        line_height = 10 * 1.2  # Font size * line spacing factor
        total_text_height = line_height * 2  # Two lines of text
        vertical_start = current_y - (15*mm/2) + (total_text_height/2)  # Center of table + half of text height
        
        # First line of address
        text1 = "Iron Mountain Deutschland Service GmbH"
        text1_width = c.stringWidth(text1, "Helvetica", 10)
        c.drawString(center_x - (text1_width / 2), current_y - 6*mm, text1)  # Adjusted y position for smaller table
        
        # Second line of address
        text2 = "Hohemarkstraße 60-70  –  61440 Oberursel"
        text2_width = c.stringWidth(text2, "Helvetica", 10)
        c.drawString(center_x - (text2_width / 2), vertical_start - (line_height * 2), text2)
        
        current_y -= 15*mm  # Adjusted for new table height
        
        # Save the page
        c.save()
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        self.logger.info(f"Created A6 reference sheet with tables")
        
        return pdf_content 

def get_mock_data():
    """Get mock data for testing the film label generator."""
    return [
        {
            'film_number': '10000002',
            'archive_id': 'RRD099-2099',
            'doc_type': 'Personalakte, FAIR, NC Programme'
        }
    ]

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create output directory in the same directory as the script
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    # Create generator
    generator = FilmLabelGenerator()
    
    # Get mock data
    mock_data = get_mock_data()
    
    # Generate film labels
    for i, data in enumerate(mock_data):
        try:
            # Generate the film label
            pdf_content = generator.create_film_label(**data)
            
            # Save to file
            output_path = output_dir / f'film_label_{i+1}.pdf'
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
            
            print(f"Generated film label {i+1}: {output_path}")
            
        except Exception as e:
            print(f"Error generating film label {i+1}: {str(e)}")
    
    print("\nDone! You can find the generated PDFs in:", output_dir) 