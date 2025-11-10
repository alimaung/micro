"""
Microfilm Density Calibration PDF Generator

This module generates calibration PDFs for microfilm density checkpoints.
The PDFs include a large white center area for densitometer readings,
density reference patches, technical drawing elements, and measurement scales.
"""

import os
from datetime import datetime
from io import BytesIO
from typing import Optional, List, Tuple

from reportlab.lib.pagesizes import A4, letter, A3
from reportlab.lib.colors import black, white, gray, HexColor, Color
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas


class MicrofilmCalibrationPDF:
    """
    Generator for microfilm density calibration PDFs.
    
    Features:
    - Large white center area for densitometer readings
    - Density reference patches (multiple gray levels)
    - Technical drawing elements (circles, lines, grids)
    - Measurement scales (rulers)
    - Border and registration marks
    - Metadata and annotations
    """
    
    # Standard density levels (as percentages: 0 = white, 100 = black)
    DEFAULT_DENSITY_LEVELS = [20, 30, 40, 50, 60, 70, 80]
    
    def __init__(
        self,
        page_size: Tuple[float, float] = A4,
        center_area_ratio: float = 0.45,
        density_levels: Optional[List[int]] = None,
        include_grid: bool = True,
        include_rulers: bool = True,
        include_circles: bool = True,
        include_crosshairs: bool = True
    ):
        """
        Initialize the calibration PDF generator.
        
        Args:
            page_size: Page size tuple (width, height) in points. Default: A4
            center_area_ratio: Ratio of center white area to page size (0.0-1.0). Default: 0.45
            density_levels: List of density percentages (0-100). Default: [10, 20, ..., 90]
            include_grid: Whether to include subtle grid in center area. Default: True
            include_rulers: Whether to include measurement rulers. Default: True
            include_circles: Whether to include concentric circles. Default: True
            include_crosshairs: Whether to include crosshair patterns. Default: True
        """
        self.page_size = page_size
        self.page_width, self.page_height = page_size
        self.center_area_ratio = center_area_ratio
        self.density_levels = density_levels or self.DEFAULT_DENSITY_LEVELS
        self.include_grid = include_grid
        self.include_rulers = include_rulers
        self.include_circles = include_circles
        self.include_crosshairs = include_crosshairs
        
        # Calculate center area dimensions
        self.center_width = self.page_width * center_area_ratio
        self.center_height = self.page_height * center_area_ratio
        self.center_x = (self.page_width - self.center_width) / 2
        self.center_y = (self.page_height - self.center_height) / 2
        
        # Margins
        self.margin = 20 * mm
        
    def _draw_border(self, c: canvas.Canvas):
        """Draw border and registration marks."""
        # Outer border
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(
            self.margin,
            self.margin,
            self.page_width - 2 * self.margin,
            self.page_height - 2 * self.margin
        )
        
        # Corner registration marks (L-shaped)
        mark_length = 15 * mm
        mark_width = 2
        
        # Top-left
        c.setLineWidth(mark_width)
        c.line(self.margin, self.margin, self.margin + mark_length, self.margin)
        c.line(self.margin, self.margin, self.margin, self.margin + mark_length)
        
        # Top-right
        c.line(self.page_width - self.margin, self.margin,
               self.page_width - self.margin - mark_length, self.margin)
        c.line(self.page_width - self.margin, self.margin,
               self.page_width - self.margin, self.margin + mark_length)
        
        # Bottom-left
        c.line(self.margin, self.page_height - self.margin,
               self.margin + mark_length, self.page_height - self.margin)
        c.line(self.margin, self.page_height - self.margin,
               self.margin, self.page_height - self.margin - mark_length)
        
        # Bottom-right
        c.line(self.page_width - self.margin, self.page_height - self.margin,
               self.page_width - self.margin - mark_length, self.page_height - self.margin)
        c.line(self.page_width - self.margin, self.page_height - self.margin,
               self.page_width - self.margin, self.page_height - self.margin - mark_length)
        
        # Center point marker (small cross)
        center_x = self.page_width / 2
        center_y = self.page_height / 2
        cross_size = 5 * mm
        c.setLineWidth(1)
        c.line(center_x - cross_size, center_y, center_x + cross_size, center_y)
        c.line(center_x, center_y - cross_size, center_x, center_y + cross_size)
        
        # Draw circle around center point
        c.circle(center_x, center_y, cross_size * 1.5, stroke=1, fill=0)
        
    def _draw_center_area(self, c: canvas.Canvas):
        """Draw the large white center area for densitometer readings."""
        # White rectangle (background)
        c.setFillColor(white)
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(
            self.center_x,
            self.center_y,
            self.center_width,
            self.center_height,
            fill=1,
            stroke=1
        )
        
        # Corner markers in center area
        corner_mark_size = 3 * mm
        c.setStrokeColor(black)
        c.setLineWidth(1)
        
        # Top-left corner
        c.line(self.center_x, self.center_y,
               self.center_x + corner_mark_size, self.center_y)
        c.line(self.center_x, self.center_y,
               self.center_x, self.center_y + corner_mark_size)
        
        # Top-right corner
        c.line(self.center_x + self.center_width, self.center_y,
               self.center_x + self.center_width - corner_mark_size, self.center_y)
        c.line(self.center_x + self.center_width, self.center_y,
               self.center_x + self.center_width, self.center_y + corner_mark_size)
        
        # Bottom-left corner
        c.line(self.center_x, self.center_y + self.center_height,
               self.center_x + corner_mark_size, self.center_y + self.center_height)
        c.line(self.center_x, self.center_y + self.center_height,
               self.center_x, self.center_y + self.center_height - corner_mark_size)
        
        # Bottom-right corner
        c.line(self.center_x + self.center_width, self.center_y + self.center_height,
               self.center_x + self.center_width - corner_mark_size,
               self.center_y + self.center_height)
        c.line(self.center_x + self.center_width, self.center_y + self.center_height,
               self.center_x + self.center_width,
               self.center_y + self.center_height - corner_mark_size)
        
    def _draw_density_patches(self, c: canvas.Canvas):
        """Draw density reference patches around the center area."""
        patch_size = 20 * mm
        patch_spacing = 5 * mm
        label_height = 5 * mm
        
        # Calculate positions for patches
        # Place patches above and below center area
        num_patches = len(self.density_levels)
        total_width = num_patches * patch_size + (num_patches - 1) * patch_spacing
        start_x = (self.page_width - total_width) / 2
        
        # Top row of patches (moved up to avoid crosshairs)
        top_y = self.center_y + self.center_height + 25 * mm
        for i, density in enumerate(self.density_levels):
            x = start_x + i * (patch_size + patch_spacing)
            
            # Calculate gray value (0 = white, 1 = black)
            gray_value = density / 100.0
            patch_color = Color(gray_value, gray_value, gray_value)
            
            # Draw patch
            c.setFillColor(patch_color)
            c.setStrokeColor(black)
            c.setLineWidth(1)
            c.rect(x, top_y, patch_size, patch_size, fill=1, stroke=1)
            
            # Label
            c.setFillColor(black)
            c.setFont("Helvetica", 8)
            text_width = c.stringWidth(f"{density}%", "Helvetica", 8)
            c.drawString(x + (patch_size - text_width) / 2, top_y - label_height, f"{density}%")
        
        # Bottom row of patches (moved down to avoid crosshairs)
        bottom_y = self.center_y - patch_size - 25 * mm - label_height
        for i, density in enumerate(self.density_levels):
            x = start_x + i * (patch_size + patch_spacing)
            
            gray_value = density / 100.0
            patch_color = Color(gray_value, gray_value, gray_value)
            
            c.setFillColor(patch_color)
            c.setStrokeColor(black)
            c.setLineWidth(1)
            c.rect(x, bottom_y, patch_size, patch_size, fill=1, stroke=1)
            
            c.setFillColor(black)
            c.setFont("Helvetica", 8)
            text_width = c.stringWidth(f"{density}%", "Helvetica", 8)
            c.drawString(x + (patch_size - text_width) / 2,
                        bottom_y + patch_size + 2, f"{density}%")
    
    def _draw_circles(self, c: canvas.Canvas):
        """Draw the largest circle outline."""
        if not self.include_circles:
            return
        
        center_x = self.page_width / 2
        center_y = self.page_height / 2
        
        # Calculate the largest circle radius (80% of center area)
        max_radius = min(self.center_width, self.center_height) / 2 * 0.8
        
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        
        # Draw only the biggest circle outline
        c.circle(center_x, center_y, max_radius, stroke=1, fill=0)
    
    def _draw_white_circle_overlay(self, c: canvas.Canvas):
        """Draw white circle overlay to create white center (subtract effect)."""
        if not self.include_circles:
            return
        
        center_x = self.page_width / 2
        center_y = self.page_height / 2
        
        # Calculate the largest circle radius (80% of center area)
        max_radius = min(self.center_width, self.center_height) / 2 * 0.8
        
        # Overlay white circle to make center white (subtract effect)
        c.setFillColor(white)
        c.setStrokeColor(white)
        c.circle(center_x, center_y, max_radius, stroke=0, fill=1)
    
    def _draw_crosshairs(self, c: canvas.Canvas):
        """Draw crosshair patterns at key points."""
        if not self.include_crosshairs:
            return
        
        crosshair_size = 8 * mm
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        
        # Crosshairs at quarter points
        positions = [
            (self.page_width * 0.25, self.page_height * 0.25),
            (self.page_width * 0.75, self.page_height * 0.25),
            (self.page_width * 0.25, self.page_height * 0.75),
            (self.page_width * 0.75, self.page_height * 0.75),
        ]
        
        for x, y in positions:
            # Horizontal line
            c.line(x - crosshair_size, y, x + crosshair_size, y)
            # Vertical line
            c.line(x, y - crosshair_size, x, y + crosshair_size)
            # Circle around crosshair
            c.circle(x, y, crosshair_size * 0.7, stroke=1, fill=0)
    
    def _draw_rulers(self, c: canvas.Canvas):
        """Draw measurement scales (rulers) along edges."""
        if not self.include_rulers:
            return
        
        ruler_length = self.page_width - 2 * self.margin - 40 * mm
        ruler_y = self.margin - 15 * mm
        tick_height = 3 * mm
        major_tick_height = 5 * mm
        
        c.setStrokeColor(black)
        c.setFillColor(black)
        c.setFont("Helvetica", 6)
        
        # Top ruler (millimeters)
        start_x = self.margin + 20 * mm
        c.line(start_x, ruler_y, start_x + ruler_length, ruler_y)
        
        # Major ticks every 10mm (no labels)
        for mm_val in range(0, int(ruler_length / mm) + 1, 10):
            x = start_x + mm_val * mm
            if x <= start_x + ruler_length:
                c.line(x, ruler_y, x, ruler_y + major_tick_height)
        
        # Minor ticks every 5mm
        for mm_val in range(0, int(ruler_length / mm) + 1, 5):
            x = start_x + mm_val * mm
            if x <= start_x + ruler_length and mm_val % 10 != 0:
                c.line(x, ruler_y, x, ruler_y + tick_height)
        
        # Bottom ruler
        bottom_ruler_y = self.page_height - self.margin + 15 * mm
        c.line(start_x, bottom_ruler_y, start_x + ruler_length, bottom_ruler_y)
        
        for mm_val in range(0, int(ruler_length / mm) + 1, 10):
            x = start_x + mm_val * mm
            if x <= start_x + ruler_length:
                c.line(x, bottom_ruler_y, x, bottom_ruler_y - major_tick_height)
        
        for mm_val in range(0, int(ruler_length / mm) + 1, 5):
            x = start_x + mm_val * mm
            if x <= start_x + ruler_length and mm_val % 10 != 0:
                c.line(x, bottom_ruler_y, x, bottom_ruler_y - tick_height)
        
        # Left ruler (vertical)
        left_ruler_x = self.margin - 15 * mm
        ruler_height = self.page_height - 2 * self.margin - 40 * mm
        start_y = self.margin + 20 * mm
        c.line(left_ruler_x, start_y, left_ruler_x, start_y + ruler_height)
        
        for mm_val in range(0, int(ruler_height / mm) + 1, 10):
            y = start_y + mm_val * mm
            if y <= start_y + ruler_height:
                c.line(left_ruler_x, y, left_ruler_x + major_tick_height, y)
        
        for mm_val in range(0, int(ruler_height / mm) + 1, 5):
            y = start_y + mm_val * mm
            if y <= start_y + ruler_height and mm_val % 10 != 0:
                c.line(left_ruler_x, y, left_ruler_x + tick_height, y)
        
        # Right ruler (vertical)
        right_ruler_x = self.page_width - self.margin + 15 * mm
        c.line(right_ruler_x, start_y, right_ruler_x, start_y + ruler_height)
        
        for mm_val in range(0, int(ruler_height / mm) + 1, 10):
            y = start_y + mm_val * mm
            if y <= start_y + ruler_height:
                c.line(right_ruler_x, y, right_ruler_x - major_tick_height, y)
        
        for mm_val in range(0, int(ruler_height / mm) + 1, 5):
            y = start_y + mm_val * mm
            if y <= start_y + ruler_height and mm_val % 10 != 0:
                c.line(right_ruler_x, y, right_ruler_x - tick_height, y)
    
    def _draw_parallel_lines(self, c: canvas.Canvas):
        """Draw parallel line sets for resolution testing."""
        # Draw in corners
        line_length = 15 * mm
        line_spacing = 2 * mm
        num_lines = 5
        
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        
        # Top-left corner
        corner_x = self.margin + 30 * mm
        corner_y = self.page_height - self.margin - 30 * mm
        for i in range(num_lines):
            y = corner_y - i * line_spacing
            c.line(corner_x, y, corner_x + line_length, y)
        
        # Top-right corner
        corner_x = self.page_width - self.margin - 30 * mm - line_length
        for i in range(num_lines):
            y = corner_y - i * line_spacing
            c.line(corner_x, y, corner_x + line_length, y)
        
        # Bottom-left corner
        corner_y = self.margin + 30 * mm
        for i in range(num_lines):
            y = corner_y + i * line_spacing
            c.line(corner_x, y, corner_x + line_length, y)
        
        # Bottom-right corner
        corner_x = self.page_width - self.margin - 30 * mm - line_length
        for i in range(num_lines):
            y = corner_y + i * line_spacing
            c.line(corner_x, y, corner_x + line_length, y)
    
    def _draw_metadata(self, c: canvas.Canvas, serial_number: Optional[str] = None):
        """Draw metadata and annotations."""
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 16)
        
        # Title (moved up)
        title = "Microfilm Density Calibration Sheet"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        title_x = (self.page_width - title_width) / 2
        title_y = self.page_height - self.margin - 5 * mm
        c.drawString(title_x, title_y, title)
        
        # Serial number or batch ID
        if serial_number:
            c.setFont("Helvetica-Bold", 10)
            serial_text = f"Serial: {serial_number}"
            serial_width = c.stringWidth(serial_text, "Helvetica-Bold", 10)
            serial_x = (self.page_width - serial_width) / 2
            c.drawString(serial_x, title_y - 8 * mm, serial_text)
        
        # Page size information
        page_size_text = f"Page Size: {self.page_width / mm:.1f} × {self.page_height / mm:.1f} mm"
        c.setFont("Helvetica", 8)
        c.drawString(self.margin, self.margin + 5 * mm, page_size_text)
        
        # Center area information
        center_info = (f"Center Area: {self.center_width / mm:.1f} × "
                      f"{self.center_height / mm:.1f} mm")
        c.drawString(self.margin, self.margin + 2 * mm, center_info)
        
        # Density levels info
        density_info = f"Density Levels: {', '.join(f'{d}%' for d in self.density_levels)}"
        c.drawString(self.margin, self.margin - 1 * mm, density_info)
    
    def generate(
        self,
        output_path: Optional[str] = None,
        serial_number: Optional[str] = None
    ) -> bytes:
        """
        Generate the calibration PDF.
        
        Args:
            output_path: Optional file path to save the PDF. If None, returns bytes only.
            serial_number: Optional serial number or batch ID to include in metadata.
        
        Returns:
            bytes: The PDF content as bytes.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=self.page_size)
        
        # Draw all elements
        self._draw_border(c)
        self._draw_center_area(c)
        self._draw_density_patches(c)
        
        if self.include_circles:
            self._draw_circles(c)
        
        if self.include_crosshairs:
            self._draw_crosshairs(c)
        
        self._draw_parallel_lines(c)
        
        if self.include_rulers:
            self._draw_rulers(c)
        
        # Draw white circle overlay last to create white center
        if self.include_circles:
            self._draw_white_circle_overlay(c)
        
        self._draw_metadata(c, serial_number)
        
        # Finalize PDF
        c.showPage()
        c.save()
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes


def generate_calibration_pdf(
    output_path: str,
    page_size: Tuple[float, float] = A4,
    center_area_ratio: float = 0.45,
    density_levels: Optional[List[int]] = None,
    serial_number: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function to generate a calibration PDF.
    
    Args:
        output_path: File path to save the PDF.
        page_size: Page size tuple (width, height) in points. Default: A4
        center_area_ratio: Ratio of center white area to page size. Default: 0.45
        density_levels: List of density percentages (0-100). Default: [10, 20, ..., 90]
        serial_number: Optional serial number or batch ID.
        **kwargs: Additional arguments passed to MicrofilmCalibrationPDF constructor.
    
    Returns:
        str: Path to the generated PDF file.
    
    Example:
        >>> generate_calibration_pdf("calibration.pdf", serial_number="CAL-2024-001")
        'calibration.pdf'
    """
    generator = MicrofilmCalibrationPDF(
        page_size=page_size,
        center_area_ratio=center_area_ratio,
        density_levels=density_levels,
        **kwargs
    )
    
    generator.generate(output_path=output_path, serial_number=serial_number)
    return output_path


if __name__ == "__main__":
    # Example usage
    import sys
    
    output_file = "microfilm_calibration.pdf"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    print(f"Generating calibration PDF: {output_file}")
    
    generator = MicrofilmCalibrationPDF(
        page_size=A4,
        center_area_ratio=0.45,
        density_levels=[20, 30, 40, 50, 60, 70, 80],
        include_grid=False,
        include_rulers=True,
        include_circles=True,
        include_crosshairs=True
    )
    
    generator.generate(
        output_path=output_file,
        serial_number=f"CAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    print(f"Calibration PDF generated successfully: {output_file}")

