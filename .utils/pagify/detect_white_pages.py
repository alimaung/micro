#!/usr/bin/env python3
"""
White Page Detection Script

Scans every page of a PDF to detect completely white pages by analyzing pixel data.
Renders each PDF page as an image first, then analyzes pixels.
"""

import io
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from decimal import Decimal, getcontext
import numpy as np
from PIL import Image
import pypdf
from tqdm import tqdm
import fitz  # PyMuPDF for rendering PDF pages to images

# Set high precision for decimal calculations
getcontext().prec = 50


class WhitePageDetector:
    """
    Detects completely white pages in PDF files by rendering pages to images and scanning pixel data.
    """
    
    def __init__(self, pdf_path: str, white_threshold: float = 0.9999, dpi: int = 150, white_pixel_threshold: int = 254):
        """
        Initialize the white page detector.
        
        Args:
            pdf_path (str): Path to the PDF file
            white_threshold (float): Threshold for considering a page "white" (0.0-1.0)
                                   1.0 = completely white, 0.9999 = 99.99% white pixels
            dpi (int): DPI for rendering PDF pages (higher = more accurate but slower)
            white_pixel_threshold (int): Pixel value threshold for considering a pixel "white" (0-255)
                                       255 = only pure white, 254 = very strict, 250 = lenient
        """
        self.pdf_path = Path(pdf_path)
        self.white_threshold = white_threshold
        self.dpi = dpi
        self.white_pixel_threshold = white_pixel_threshold
        
        if not self.pdf_path.exists():
            raise ValueError(f"PDF file does not exist: {pdf_path}")
        
        # Load PDF with PyMuPDF for rendering
        self.pdf_doc = fitz.open(str(self.pdf_path))
        self.total_pages = len(self.pdf_doc)
    
    def _render_page_to_image(self, page_index: int) -> Optional[Image.Image]:
        """
        Render a PDF page to a PIL Image.
        
        Args:
            page_index (int): Zero-based page index
            
        Returns:
            Optional[Image.Image]: Rendered page image or None if rendering failed
        """
        try:
            if page_index >= len(self.pdf_doc):
                return None
            
            # Get the page
            page = self.pdf_doc[page_index]
            
            # Create transformation matrix for desired DPI
            # Default is 72 DPI, so scale factor is dpi/72
            scale = self.dpi / 72.0
            mat = fitz.Matrix(scale, scale)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            return img
            
        except Exception as e:
            print(f"Error rendering page {page_index + 1}: {e}")
            return None
    
    def _analyze_page_whiteness(self, page_index: int) -> Tuple[bool, dict]:
        """
        Analyze a single page to determine if it's completely white.
        
        Args:
            page_index (int): Zero-based page index
            
        Returns:
            Tuple[bool, dict]: (is_white, analysis_info)
        """
        analysis = {
            'page_number': page_index + 1,
            'rendered': False,
            'image_size': None,
            'total_pixels': 0,
            'white_pixels': 0,
            'white_percentage': Decimal('0.0'),
            'white_percentage_float': 0.0,
            'is_white': False,
            'error': None
        }
        
        try:
            # Render page to image
            img = self._render_page_to_image(page_index)
            
            if img is None:
                analysis['error'] = 'Failed to render page'
                return False, analysis
            
            analysis['rendered'] = True
            analysis['image_size'] = img.size
            
            # Convert image to numpy array for efficient processing
            img_array = np.array(img)
            
            # Count white pixels based on image mode - using configurable white detection
            if img.mode == 'L':  # Grayscale
                white_pixels = np.sum(img_array >= self.white_pixel_threshold)
                total_pixels = img_array.size
            elif img.mode == 'RGB':
                # All channels must be >= threshold for white
                white_pixels = np.sum(np.all(img_array >= self.white_pixel_threshold, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            elif img.mode == 'RGBA':
                # All RGB channels must be >= threshold for white (ignore alpha for white detection)
                white_pixels = np.sum(np.all(img_array[:, :, :3] >= self.white_pixel_threshold, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            elif img.mode == '1':  # 1-bit
                white_pixels = np.sum(img_array == 1)
                total_pixels = img_array.size
            else:
                # Convert to RGB and analyze
                img_rgb = img.convert('RGB')
                img_array = np.array(img_rgb)
                white_pixels = np.sum(np.all(img_array >= self.white_pixel_threshold, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            
            analysis['white_pixels'] = int(white_pixels)
            analysis['total_pixels'] = total_pixels
            
            # Calculate precise percentage using Decimal for high precision
            if total_pixels > 0:
                white_decimal = Decimal(str(white_pixels))
                total_decimal = Decimal(str(total_pixels))
                percentage_decimal = (white_decimal / total_decimal) * Decimal('100')
                analysis['white_percentage'] = percentage_decimal
                analysis['white_percentage_float'] = float(percentage_decimal)
            else:
                analysis['white_percentage'] = Decimal('0.0')
                analysis['white_percentage_float'] = 0.0
            
            # Determine if page is white based on threshold
            threshold_decimal = Decimal(str(self.white_threshold)) * Decimal('100')
            analysis['is_white'] = analysis['white_percentage'] >= threshold_decimal
            
            return analysis['is_white'], analysis
            
        except Exception as e:
            analysis['error'] = str(e)
            return False, analysis
    
    def detect_white_pages(self) -> List[dict]:
        """
        Detect all white pages in the PDF.
        
        Returns:
            List[dict]: List of analysis results for each page
        """
        results = []
        white_pages = []
        
        print(f"Analyzing {self.total_pages} pages in {self.pdf_path.name}")
        print(f"White threshold: {self.white_threshold * 100:.6f}%")
        print(f"White pixel threshold: {self.white_pixel_threshold}/255 (stricter = higher)")
        print(f"Rendering DPI: {self.dpi}")
        print("-" * 80)
        
        # Analyze each page with progress bar
        for page_index in tqdm(range(self.total_pages), desc="Scanning pages"):
            is_white, analysis = self._analyze_page_whiteness(page_index)
            results.append(analysis)
            
            if is_white:
                white_pages.append(analysis['page_number'])
        
        # Print detailed results
        print("\n" + "=" * 80)
        print("WHITE PAGE DETECTION RESULTS")
        print("=" * 80)
        
        for result in results:
            page_num = result['page_number']
            if result['error']:
                print(f"Page {page_num:2d}: ERROR - {result['error']}")
            elif not result['rendered']:
                print(f"Page {page_num:2d}: RENDER FAILED")
            else:
                status = "WHITE" if result['is_white'] else "NOT WHITE"
                # Display with high precision (6 decimal places)
                percentage_str = f"{result['white_percentage']:.6f}"
                print(f"Page {page_num:2d}: {status:9s} - {percentage_str:>12s}% white "
                      f"({result['white_pixels']:,}/{result['total_pixels']:,} pixels) "
                      f"[{result['image_size'][0]}x{result['image_size'][1]}]")
        
        # Calculate and display summary statistics
        print("-" * 80)
        
        # Count successful analyses
        successful_results = [r for r in results if r['rendered'] and not r['error']]
        white_count = len(white_pages)
        not_white_count = len(successful_results) - white_count
        total_successful = len(successful_results)
        
        if white_pages:
            print(f"WHITE PAGES FOUND: {white_count} pages")
            print(f"Page numbers: {', '.join(map(str, white_pages))}")
        else:
            print("NO WHITE PAGES FOUND")
        
        print(f"Total pages analyzed: {len(results)}")
        print(f"Pages rendered successfully: {sum(1 for r in results if r['rendered'])}")
        print(f"Pages with errors: {sum(1 for r in results if r['error'])}")
        
        # Summary percentages
        if total_successful > 0:
            white_page_percentage = Decimal(str(white_count)) / Decimal(str(total_successful)) * Decimal('100')
            not_white_page_percentage = Decimal(str(not_white_count)) / Decimal(str(total_successful)) * Decimal('100')
            
            print("\n" + "=" * 80)
            print("SUMMARY BREAKDOWN")
            print("=" * 80)
            print(f"White pages:     {white_count:3d} / {total_successful:3d} = {white_page_percentage:.6f}%")
            print(f"Non-white pages: {not_white_count:3d} / {total_successful:3d} = {not_white_page_percentage:.6f}%")
            print(f"Total analyzed:  {total_successful:3d} pages")
            
            if len(results) != total_successful:
                failed_count = len(results) - total_successful
                print(f"Failed to analyze: {failed_count} pages")
        
        # Close the PDF document
        self.pdf_doc.close()
        
        return results


def main():
    """Main function to run white page detection."""
    if len(sys.argv) < 2:
        print("Usage: python detect_white_pages.py <pdf_path> [white_threshold] [dpi] [white_pixel_threshold]")
        print("  pdf_path: Path to the PDF file to analyze")
        print("  white_threshold: Threshold for white detection (0.0-1.0, default: 0.9999)")
        print("  dpi: DPI for rendering pages (default: 150)")
        print("  white_pixel_threshold: Pixel value threshold for white (0-255, default: 254)")
        print("    255 = only pure white pixels, 254 = very strict, 250 = lenient")
        print("\nExample:")
        print("  python detect_white_pages.py document.pdf")
        print("  python detect_white_pages.py document.pdf 0.95")
        print("  python detect_white_pages.py document.pdf 0.9999 200")
        print("  python detect_white_pages.py document.pdf 0.9999 150 255")
        return 1
    
    pdf_path = sys.argv[1]
    white_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9999
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    white_pixel_threshold = int(sys.argv[4]) if len(sys.argv) > 4 else 254
    
    try:
        detector = WhitePageDetector(pdf_path, white_threshold, dpi, white_pixel_threshold)
        results = detector.detect_white_pages()
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 