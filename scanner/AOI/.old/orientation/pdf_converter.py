#!/usr/bin/env python3
"""
PDF to Image Conversion Module

Robust PDF conversion with orientation handling for microfilm AOI analysis.
Handles both original and reproduction PDFs regardless of their initial orientation.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from PIL import Image
import io
import json
from datetime import datetime


class PDFConverter:
    """
    Robust PDF to image converter with orientation detection capabilities.
    """
    
    def __init__(self, dpi: int = 300, output_dir: str = "conversion_output"):
        self.dpi = dpi
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Conversion settings
        self.grayscale = True
        self.normalize_size = True
        self.save_intermediate = True  # Save converted images for debugging
        
    def convert_pdf_to_images(self, pdf_path: str, method: str = "pdf2image") -> List[np.ndarray]:
        """
        Convert PDF to list of grayscale numpy arrays.
        
        Args:
            pdf_path: Path to PDF file
            method: Conversion method ("pdf2image" or "pymupdf")
            
        Returns:
            List of grayscale numpy arrays (one per page)
        """
        print(f"Converting PDF: {pdf_path}")
        print(f"Method: {method}, DPI: {self.dpi}")
        
        if method == "pdf2image":
            return self._convert_with_pdf2image(pdf_path)
        elif method == "pymupdf":
            return self._convert_with_pymupdf(pdf_path)
        else:
            raise ValueError(f"Unknown conversion method: {method}")
    
    def _convert_with_pdf2image(self, pdf_path: str) -> List[np.ndarray]:
        """Convert using pdf2image library."""
        try:
            # Convert PDF to PIL images
            pil_images = convert_from_path(pdf_path, dpi=self.dpi)
            
            images = []
            for i, pil_img in enumerate(pil_images):
                # Convert to numpy array
                img_array = np.array(pil_img)
                
                # Convert to grayscale if needed
                if len(img_array.shape) == 3:
                    if self.grayscale:
                        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    else:
                        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:
                    gray_img = img_array
                
                images.append(gray_img)
                
                # Save intermediate image if requested
                if self.save_intermediate:
                    self._save_intermediate_image(gray_img, pdf_path, i, "pdf2image")
            
            print(f"Successfully converted {len(images)} pages using pdf2image")
            return images
            
        except Exception as e:
            print(f"Error with pdf2image conversion: {e}")
            return []
    
    def _convert_with_pymupdf(self, pdf_path: str) -> List[np.ndarray]:
        """Convert using PyMuPDF library."""
        try:
            pdf_doc = fitz.open(pdf_path)
            images = []
            
            # Calculate scale factor for desired DPI
            scale = self.dpi / 72.0
            mat = fitz.Matrix(scale, scale)
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("ppm")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Convert to numpy array
                img_array = np.array(pil_img)
                
                # Convert to grayscale if needed
                if len(img_array.shape) == 3:
                    if self.grayscale:
                        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    else:
                        gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:
                    gray_img = img_array
                
                images.append(gray_img)
                
                # Save intermediate image if requested
                if self.save_intermediate:
                    self._save_intermediate_image(gray_img, pdf_path, page_num, "pymupdf")
            
            pdf_doc.close()
            print(f"Successfully converted {len(images)} pages using PyMuPDF")
            return images
            
        except Exception as e:
            print(f"Error with PyMuPDF conversion: {e}")
            return []
    
    def _save_intermediate_image(self, img: np.ndarray, pdf_path: str, page_num: int, method: str):
        """Save intermediate converted image for debugging."""
        pdf_name = Path(pdf_path).stem
        filename = f"{pdf_name}_page_{page_num+1:03d}_{method}.png"
        output_path = self.output_dir / filename
        
        cv2.imwrite(str(output_path), img)
    
    def convert_document_pair(self, original_pdf: str, reproduction_pdf: str, 
                            method: str = "pdf2image") -> Tuple[List[np.ndarray], List[np.ndarray], Dict[str, Any]]:
        """
        Convert both original and reproduction PDFs to images.
        
        Returns:
            Tuple of (original_images, reproduction_images, conversion_info)
        """
        print(f"\n{'='*60}")
        print("CONVERTING DOCUMENT PAIR")
        print(f"{'='*60}")
        
        conversion_info = {
            'timestamp': datetime.now().isoformat(),
            'original_pdf': original_pdf,
            'reproduction_pdf': reproduction_pdf,
            'method': method,
            'dpi': self.dpi,
            'grayscale': self.grayscale
        }
        
        # Convert original
        print(f"\n1. Converting Original Document:")
        original_images = self.convert_pdf_to_images(original_pdf, method)
        conversion_info['original_pages'] = len(original_images)
        
        if original_images:
            conversion_info['original_dimensions'] = {
                'height': int(original_images[0].shape[0]),
                'width': int(original_images[0].shape[1])
            }
        
        # Convert reproduction
        print(f"\n2. Converting Reproduction Document:")
        reproduction_images = self.convert_pdf_to_images(reproduction_pdf, method)
        conversion_info['reproduction_pages'] = len(reproduction_images)
        
        if reproduction_images:
            conversion_info['reproduction_dimensions'] = {
                'height': int(reproduction_images[0].shape[0]),
                'width': int(reproduction_images[0].shape[1])
            }
        
        # Check for dimension mismatches
        if original_images and reproduction_images:
            orig_shape = original_images[0].shape
            repro_shape = reproduction_images[0].shape
            
            if orig_shape != repro_shape:
                print(f"\nWarning: Dimension mismatch detected!")
                print(f"  Original: {orig_shape}")
                print(f"  Reproduction: {repro_shape}")
                conversion_info['dimension_mismatch'] = True
                conversion_info['size_normalization_needed'] = True
            else:
                conversion_info['dimension_mismatch'] = False
                conversion_info['size_normalization_needed'] = False
        
        # Save conversion report
        report_path = self.output_dir / "conversion_report.json"
        with open(report_path, 'w') as f:
            json.dump(conversion_info, f, indent=2)
        
        print(f"\nConversion complete!")
        print(f"Original pages: {len(original_images)}")
        print(f"Reproduction pages: {len(reproduction_images)}")
        print(f"Report saved: {report_path}")
        
        return original_images, reproduction_images, conversion_info
    
    def normalize_image_sizes(self, images1: List[np.ndarray], images2: List[np.ndarray], 
                            target_size: Optional[Tuple[int, int]] = None) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Normalize image sizes between two sets of images.
        
        Args:
            images1: First set of images
            images2: Second set of images  
            target_size: Optional target size (width, height). If None, uses size of first image in images1
            
        Returns:
            Tuple of normalized image lists
        """
        if not images1 or not images2:
            return images1, images2
        
        # Determine target size
        if target_size is None:
            target_size = (images1[0].shape[1], images1[0].shape[0])  # (width, height)
        
        print(f"Normalizing images to size: {target_size}")
        
        # Resize images1
        normalized_images1 = []
        for img in images1:
            if img.shape[:2] != (target_size[1], target_size[0]):  # OpenCV uses (height, width)
                resized = cv2.resize(img, target_size)
                normalized_images1.append(resized)
            else:
                normalized_images1.append(img.copy())
        
        # Resize images2
        normalized_images2 = []
        for img in images2:
            if img.shape[:2] != (target_size[1], target_size[0]):  # OpenCV uses (height, width)
                resized = cv2.resize(img, target_size)
                normalized_images2.append(resized)
            else:
                normalized_images2.append(img.copy())
        
        return normalized_images1, normalized_images2
    
    def get_conversion_quality_metrics(self, images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Analyze quality metrics of converted images.
        
        Returns:
            Dictionary with quality metrics
        """
        if not images:
            return {}
        
        metrics = {
            'total_pages': len(images),
            'dimensions': {
                'height': int(images[0].shape[0]),
                'width': int(images[0].shape[1])
            },
            'per_page_stats': []
        }
        
        for i, img in enumerate(images):
            page_stats = {
                'page': i + 1,
                'mean_brightness': float(np.mean(img)),
                'std_brightness': float(np.std(img)),
                'min_brightness': float(np.min(img)),
                'max_brightness': float(np.max(img)),
                'dynamic_range': float(np.max(img) - np.min(img))
            }
            metrics['per_page_stats'].append(page_stats)
        
        # Overall statistics
        all_means = [p['mean_brightness'] for p in metrics['per_page_stats']]
        all_stds = [p['std_brightness'] for p in metrics['per_page_stats']]
        all_ranges = [p['dynamic_range'] for p in metrics['per_page_stats']]
        
        metrics['overall_stats'] = {
            'avg_brightness': float(np.mean(all_means)),
            'avg_contrast': float(np.mean(all_stds)),
            'avg_dynamic_range': float(np.mean(all_ranges)),
            'brightness_consistency': float(np.std(all_means)),  # Lower is more consistent
            'contrast_consistency': float(np.std(all_stds))
        }
        
        return metrics


class ConversionTester:
    """Test conversion with different methods and settings."""
    
    def __init__(self, output_base_dir: str = "conversion_tests"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
    
    def test_conversion_methods(self, original_pdf: str, reproduction_pdf: str) -> Dict[str, Any]:
        """
        Test different conversion methods and compare results.
        """
        print(f"\n{'='*70}")
        print("TESTING CONVERSION METHODS")
        print(f"{'='*70}")
        
        methods = ["pdf2image", "pymupdf"]
        results = {}
        
        for method in methods:
            print(f"\nTesting method: {method}")
            
            # Create method-specific output directory
            method_dir = self.output_base_dir / f"test_{method}"
            
            try:
                converter = PDFConverter(dpi=300, output_dir=method_dir)
                orig_images, repro_images, conversion_info = converter.convert_document_pair(
                    original_pdf, reproduction_pdf, method=method
                )
                
                # Get quality metrics
                orig_metrics = converter.get_conversion_quality_metrics(orig_images)
                repro_metrics = converter.get_conversion_quality_metrics(repro_images)
                
                results[method] = {
                    'success': True,
                    'conversion_info': conversion_info,
                    'original_metrics': orig_metrics,
                    'reproduction_metrics': repro_metrics,
                    'output_directory': str(method_dir)
                }
                
                print(f"  ✓ Success: {len(orig_images)} original, {len(repro_images)} reproduction pages")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                results[method] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Save comparison report
        report_path = self.output_base_dir / "method_comparison_report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nMethod comparison report saved: {report_path}")
        return results
    
    def print_comparison_summary(self, results: Dict[str, Any]):
        """Print summary of method comparison."""
        
        print(f"\n{'='*70}")
        print("CONVERSION METHOD COMPARISON SUMMARY")
        print(f"{'='*70}")
        
        for method, result in results.items():
            print(f"\nMethod: {method.upper()}")
            print("-" * 20)
            
            if result['success']:
                orig_metrics = result['original_metrics']
                repro_metrics = result['reproduction_metrics']
                
                print(f"✓ Conversion successful")
                print(f"  Original pages: {orig_metrics['total_pages']}")
                print(f"  Reproduction pages: {repro_metrics['total_pages']}")
                print(f"  Image dimensions: {orig_metrics['dimensions']['width']}x{orig_metrics['dimensions']['height']}")
                print(f"  Avg brightness (orig): {orig_metrics['overall_stats']['avg_brightness']:.1f}")
                print(f"  Avg brightness (repro): {repro_metrics['overall_stats']['avg_brightness']:.1f}")
                print(f"  Output: {result['output_directory']}")
            else:
                print(f"✗ Conversion failed: {result['error']}")


def main():
    """Main function for testing conversion."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Test PDF to image conversion methods')
    parser.add_argument('--original', required=True, help='Path to original PDF')
    parser.add_argument('--reproduction', required=True, help='Path to reproduction PDF')
    parser.add_argument('--method', default='pdf2image', choices=['pdf2image', 'pymupdf'], 
                       help='Conversion method to use')
    parser.add_argument('--test-all', action='store_true', help='Test all conversion methods')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for conversion')
    parser.add_argument('--output', default='conversion_output', help='Output directory')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original):
        print(f"Error: Original file not found: {args.original}")
        sys.exit(1)
    
    if not os.path.exists(args.reproduction):
        print(f"Error: Reproduction file not found: {args.reproduction}")
        sys.exit(1)
    
    try:
        if args.test_all:
            # Test all methods
            tester = ConversionTester(args.output)
            results = tester.test_conversion_methods(args.original, args.reproduction)
            tester.print_comparison_summary(results)
        else:
            # Single method conversion
            converter = PDFConverter(dpi=args.dpi, output_dir=args.output)
            orig_images, repro_images, conversion_info = converter.convert_document_pair(
                args.original, args.reproduction, method=args.method
            )
            
            # Print summary
            print(f"\n{'='*50}")
            print("CONVERSION SUMMARY")
            print(f"{'='*50}")
            print(f"Method: {args.method}")
            print(f"Original pages: {len(orig_images)}")
            print(f"Reproduction pages: {len(repro_images)}")
            if orig_images:
                print(f"Image dimensions: {orig_images[0].shape}")
            print(f"Output directory: {args.output}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
