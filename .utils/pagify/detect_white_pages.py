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
import numpy as np
from PIL import Image
import pypdf
from tqdm import tqdm
import fitz  # PyMuPDF for rendering PDF pages to images


class WhitePageDetector:
    """
    Detects completely white pages in PDF files by rendering pages to images and scanning pixel data.
    """
    
    def __init__(self, pdf_path: str, white_threshold: float = 0.99, dpi: int = 150):
        """
        Initialize the white page detector.
        
        Args:
            pdf_path (str): Path to the PDF file
            white_threshold (float): Threshold for considering a page "white" (0.0-1.0)
                                   1.0 = completely white, 0.99 = 99% white pixels
            dpi (int): DPI for rendering PDF pages (higher = more accurate but slower)
        """
        self.pdf_path = Path(pdf_path)
        self.white_threshold = white_threshold
        self.dpi = dpi
        
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
            'white_percentage': 0.0,
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
            
            # Count white pixels based on image mode
            if img.mode == 'L':  # Grayscale
                white_pixels = np.sum(img_array >= 250)
                total_pixels = img_array.size
            elif img.mode == 'RGB':
                # All channels must be >= 250 for white
                white_pixels = np.sum(np.all(img_array >= 250, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            elif img.mode == 'RGBA':
                # All channels including alpha must be >= 250 for white
                white_pixels = np.sum(np.all(img_array >= 250, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            elif img.mode == '1':  # 1-bit
                white_pixels = np.sum(img_array == 1)
                total_pixels = img_array.size
            else:
                # Convert to RGB and analyze
                img_rgb = img.convert('RGB')
                img_array = np.array(img_rgb)
                white_pixels = np.sum(np.all(img_array >= 250, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            
            analysis['white_pixels'] = int(white_pixels)
            analysis['total_pixels'] = total_pixels
            analysis['white_percentage'] = (white_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            
            # Determine if page is white based on threshold
            analysis['is_white'] = analysis['white_percentage'] >= (self.white_threshold * 100)
            
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
        print(f"White threshold: {self.white_threshold * 100:.1f}%")
        print(f"Rendering DPI: {self.dpi}")
        print("-" * 60)
        
        # Analyze each page with progress bar
        for page_index in tqdm(range(self.total_pages), desc="Scanning pages"):
            is_white, analysis = self._analyze_page_whiteness(page_index)
            results.append(analysis)
            
            if is_white:
                white_pages.append(analysis['page_number'])
        
        # Print summary
        print("\n" + "=" * 60)
        print("WHITE PAGE DETECTION RESULTS")
        print("=" * 60)
        
        for result in results:
            page_num = result['page_number']
            if result['error']:
                print(f"Page {page_num:2d}: ERROR - {result['error']}")
            elif not result['rendered']:
                print(f"Page {page_num:2d}: RENDER FAILED")
            else:
                status = "WHITE" if result['is_white'] else "NOT WHITE"
                print(f"Page {page_num:2d}: {status:9s} - {result['white_percentage']:6.2f}% white "
                      f"({result['white_pixels']:,}/{result['total_pixels']:,} pixels) "
                      f"[{result['image_size'][0]}x{result['image_size'][1]}]")
        
        print("-" * 60)
        if white_pages:
            print(f"WHITE PAGES FOUND: {len(white_pages)} pages")
            print(f"Page numbers: {', '.join(map(str, white_pages))}")
        else:
            print("NO WHITE PAGES FOUND")
        
        print(f"Total pages analyzed: {len(results)}")
        print(f"Pages rendered successfully: {sum(1 for r in results if r['rendered'])}")
        print(f"Pages with errors: {sum(1 for r in results if r['error'])}")
        
        # Close the PDF document
        self.pdf_doc.close()
        
        return results


def main():
    """Main function to run white page detection."""
    if len(sys.argv) < 2:
        print("Usage: python detect_white_pages.py <pdf_path> [white_threshold] [dpi]")
        print("  pdf_path: Path to the PDF file to analyze")
        print("  white_threshold: Threshold for white detection (0.0-1.0, default: 0.99)")
        print("  dpi: DPI for rendering pages (default: 150)")
        print("\nExample:")
        print("  python detect_white_pages.py document.pdf")
        print("  python detect_white_pages.py document.pdf 0.95")
        print("  python detect_white_pages.py document.pdf 0.99 200")
        return 1
    
    pdf_path = sys.argv[1]
    white_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.99
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    
    try:
        detector = WhitePageDetector(pdf_path, white_threshold, dpi)
        results = detector.detect_white_pages()
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 