#!/usr/bin/env python3
"""
PDF to Image Conversion Module

Converts PDF documents to grayscale numpy arrays for image processing.
"""

import numpy as np
import cv2
from pdf2image import convert_from_path
from typing import List
from pathlib import Path


class PDFConverter:
    """Converts PDF pages to grayscale numpy arrays."""
    
    def __init__(self, dpi: int = 300):
        """
        Initialize PDF converter.
        
        Args:
            dpi (int): DPI for PDF conversion (default: 300)
        """
        self.dpi = dpi
    
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        Convert PDF pages to grayscale numpy arrays.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[np.ndarray]: List of grayscale images as numpy arrays
        """
        print(f"Converting PDF to images: {pdf_path}")
        
        try:
            # Convert PDF to PIL images
            pil_images = convert_from_path(pdf_path, dpi=self.dpi)
            
            # Convert to grayscale numpy arrays
            images = []
            for pil_img in pil_images:
                # Convert PIL to numpy array
                img_array = np.array(pil_img)
                
                # Convert to grayscale if needed
                if len(img_array.shape) == 3:
                    gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray_img = img_array
                
                images.append(gray_img)
            
            print(f"Converted {len(images)} pages")
            return images
            
        except Exception as e:
            print(f"Error converting PDF {pdf_path}: {e}")
            return []

