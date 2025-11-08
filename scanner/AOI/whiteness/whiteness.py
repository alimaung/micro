#!/usr/bin/env python3
"""
White Page Detection Module

Detects completely white pages in PDF documents to skip unnecessary processing.
"""

import numpy as np
import fitz  # PyMuPDF for rendering PDF pages to images
from PIL import Image
import io
from typing import Tuple, Dict, Any, List


class WhitePageDetector:
    """Detects white pages in PDF documents."""
    
    def __init__(self, dpi: int = 300, white_threshold: float = 0.997, 
                 white_pixel_threshold: int = 254):
        """
        Initialize white page detector.
        
        Args:
            dpi (int): DPI for rendering PDF pages (default: 300)
            white_threshold (float): Percentage threshold for white page detection (0.0-1.0, default: 0.997 = 99.7%)
            white_pixel_threshold (int): Pixel value threshold for white (0-255, default: 254)
        """
        self.dpi = dpi
        self.white_threshold = white_threshold
        self.white_pixel_threshold = white_pixel_threshold
    
    def _render_page_to_image(self, pdf_path: str, page_index: int) -> Image.Image:
        """
        Render a PDF page to a PIL Image for white page detection.
        
        Args:
            pdf_path (str): Path to the PDF file
            page_index (int): Zero-based page index
            
        Returns:
            Image.Image: PIL Image of the rendered page, or None if error
        """
        try:
            pdf_doc = fitz.open(pdf_path)
            if page_index >= len(pdf_doc):
                pdf_doc.close()
                return None
            
            # Get the page
            page = pdf_doc[page_index]
            
            # Create transformation matrix for desired DPI
            scale = self.dpi / 72.0
            mat = fitz.Matrix(scale, scale)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            pdf_doc.close()
            return img
        
        except Exception as e:
            print(f"Error rendering page {page_index + 1} for white detection: {e}")
            return None
    
    def is_white_page(self, pdf_path: str, page_index: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a page is completely white.
        
        Args:
            pdf_path (str): Path to the PDF file
            page_index (int): Zero-based page index
            
        Returns:
            Tuple[bool, Dict]: (is_white, analysis_info)
                - is_white: True if page is considered white
                - analysis_info: Dictionary with detailed analysis results
        """
        analysis = {
            'page_number': page_index + 1,
            'rendered': False,
            'total_pixels': 0,
            'white_pixels': 0,
            'white_percentage': 0.0,
            'is_white': False,
            'error': None
        }
        
        try:
            # Render page to image
            img = self._render_page_to_image(pdf_path, page_index)
            
            if img is None:
                analysis['error'] = 'Failed to render page'
                return False, analysis
            
            analysis['rendered'] = True
            
            # Convert image to numpy array for efficient processing
            img_array = np.array(img)
            
            # Count white pixels based on image mode
            if img.mode == 'L':  # Grayscale
                white_pixels = np.sum(img_array >= self.white_pixel_threshold)
                total_pixels = img_array.size
            elif img.mode == 'RGB':
                # All channels must be >= threshold for white
                white_pixels = np.sum(np.all(img_array >= self.white_pixel_threshold, axis=2))
                total_pixels = img_array.shape[0] * img_array.shape[1]
            elif img.mode == 'RGBA':
                # All RGB channels must be >= threshold for white (ignore alpha)
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
            
            # Ensure all values are standard Python types for JSON serialization
            analysis['white_pixels'] = int(white_pixels)
            analysis['total_pixels'] = int(total_pixels)
            
            # Calculate percentage
            if total_pixels > 0:
                white_percentage = float(white_pixels / total_pixels)
                analysis['white_percentage'] = white_percentage
            else:
                analysis['white_percentage'] = 0.0
            
            # Determine if page is white based on threshold
            analysis['is_white'] = bool(analysis['white_percentage'] >= self.white_threshold)
            
            return analysis['is_white'], analysis
            
        except Exception as e:
            analysis['error'] = str(e)
            return False, analysis
    
    def check_original_pages(self, pdf_path: str) -> List[int]:
        """
        Check all pages in a PDF and return list of page indexes that are white.
        
        This method is optimized for checking original documents to determine
        which pages should be skipped during processing.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[int]: Zero-based page indexes of white pages (pages to skip)
        """
        skip_list = []
        
        try:
            pdf_doc = fitz.open(pdf_path)
            total_pages = len(pdf_doc)
            pdf_doc.close()
            
            print(f"Checking {total_pages} pages for whiteness in: {pdf_path}")
            
            for page_index in range(total_pages):
                is_white, analysis = self.is_white_page(pdf_path, page_index)
                
                if is_white:
                    skip_list.append(page_index)
                    print(f"  Page {page_index + 1} is white ({analysis['white_percentage']:.4f}% white) - will skip")
                else:
                    print(f"  Page {page_index + 1} has content ({analysis['white_percentage']:.4f}% white)")
            
            print(f"Found {len(skip_list)} white pages to skip: {[i+1 for i in skip_list]}")
            return skip_list
            
        except Exception as e:
            print(f"Error checking pages for whiteness: {e}")
            return []

