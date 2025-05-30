#!/usr/bin/env python3
"""
Batch White Page Detection Script

Scans every page of all PDF files in a folder to detect completely white pages.
Renders each PDF page as an image first, then analyzes pixels.
Uses the actual DPI from the PDF for accurate rendering.
"""

import io
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import numpy as np
from PIL import Image
from tqdm import tqdm
import fitz  # PyMuPDF for rendering PDF pages to images
import json
import csv
from datetime import datetime


def detect_pdf_dpi(pdf_doc) -> float:
    """
    Detect the DPI of a PDF document by analyzing embedded images.
    
    Args:
        pdf_doc: PyMuPDF document object
        
    Returns:
        float: Average DPI of the PDF (defaults to 150 if no images found)
    """
    image_dpis = []
    
    try:
        for page_num in range(min(5, len(pdf_doc))):  # Check first 5 pages for efficiency
            page = pdf_doc.load_page(page_num)
            image_list = page.get_images()
            
            for img in image_list:
                try:
                    xref = img[0]
                    base_image = pdf_doc.extract_image(xref)
                    image_width = base_image["width"]
                    image_height = base_image["height"]
                    
                    # Get image rectangle on page
                    image_rects = page.get_image_rects(img)
                    if image_rects:
                        img_rect = image_rects[0]
                        display_width = img_rect.width
                        display_height = img_rect.height
                        
                        if display_width > 0 and display_height > 0:
                            dpi_x = (image_width / display_width) * 72
                            dpi_y = (image_height / display_height) * 72
                            avg_dpi = (dpi_x + dpi_y) / 2
                            image_dpis.append(avg_dpi)
                            
                            # If we found a good DPI, we can break early
                            if len(image_dpis) >= 3:
                                break
                except:
                    continue
            
            if len(image_dpis) >= 3:
                break
    except:
        pass
    
    if image_dpis:
        return sum(image_dpis) / len(image_dpis)
    else:
        return 150  # Default fallback DPI


class WhitePageDetector:
    """
    Detects completely white pages in PDF files by rendering pages to images and scanning pixel data.
    Uses actual PDF DPI for accurate rendering.
    """
    
    def __init__(self, white_threshold: float = 0.99, fallback_dpi: int = 150):
        """
        Initialize the white page detector.
        
        Args:
            white_threshold (float): Threshold for considering a page "white" (0.0-1.0)
                                   1.0 = completely white, 0.99 = 99% white pixels
            fallback_dpi (int): Fallback DPI if PDF DPI cannot be detected
        """
        self.white_threshold = white_threshold
        self.fallback_dpi = fallback_dpi
    
    def _render_page_to_image(self, page, page_index: int, dpi: float) -> Optional[Image.Image]:
        """
        Render a PDF page to a PIL Image using the specified DPI.
        
        Args:
            page: PyMuPDF page object
            page_index (int): Zero-based page index
            dpi (float): DPI to use for rendering
            
        Returns:
            Optional[Image.Image]: Rendered page image or None if rendering failed
        """
        try:
            # Create transformation matrix for desired DPI
            # Default is 72 DPI, so scale factor is dpi/72
            scale = dpi / 72.0
            mat = fitz.Matrix(scale, scale)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            return img
            
        except Exception as e:
            return None
    
    def _analyze_page_whiteness(self, page, page_index: int, dpi: float) -> Tuple[bool, dict]:
        """
        Analyze a single page to determine if it's completely white.
        
        Args:
            page: PyMuPDF page object
            page_index (int): Zero-based page index
            dpi (float): DPI to use for rendering
            
        Returns:
            Tuple[bool, dict]: (is_white, analysis_info)
        """
        analysis = {
            'page_number': page_index + 1,
            'rendered': False,
            'rendering_dpi': dpi,
            'image_size': None,
            'total_pixels': 0,
            'white_pixels': 0,
            'white_percentage': 0.0,
            'is_white': False,
            'error': None
        }
        
        try:
            # Render page to image
            img = self._render_page_to_image(page, page_index, dpi)
            
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
    
    def detect_white_pages_in_pdf(self, pdf_path: Path) -> Dict:
        """
        Detect all white pages in a single PDF file.
        
        Args:
            pdf_path (Path): Path to the PDF file
            
        Returns:
            Dict: Analysis results for the PDF file
        """
        pdf_result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'file_size': 0,
            'total_pages': 0,
            'detected_dpi': 0,
            'dpi_source': 'fallback',
            'white_pages': [],
            'white_page_count': 0,
            'pages_analyzed': 0,
            'pages_with_errors': 0,
            'processing_time': 0,
            'error': None,
            'page_details': []
        }
        
        start_time = datetime.now()
        
        try:
            # Get file size
            pdf_result['file_size'] = pdf_path.stat().st_size
            
            # Open PDF
            pdf_doc = fitz.open(str(pdf_path))
            pdf_result['total_pages'] = len(pdf_doc)
            
            # Detect PDF DPI once for the entire document
            detected_dpi = detect_pdf_dpi(pdf_doc)
            pdf_result['detected_dpi'] = detected_dpi
            
            # Determine DPI source
            if detected_dpi != self.fallback_dpi:
                pdf_result['dpi_source'] = 'detected_from_images'
            else:
                pdf_result['dpi_source'] = 'fallback_default'
            
            # Analyze each page using the detected DPI
            for page_index in range(len(pdf_doc)):
                page = pdf_doc[page_index]
                is_white, analysis = self._analyze_page_whiteness(page, page_index, detected_dpi)
                
                pdf_result['page_details'].append(analysis)
                pdf_result['pages_analyzed'] += 1
                
                if analysis['error']:
                    pdf_result['pages_with_errors'] += 1
                
                if is_white:
                    pdf_result['white_pages'].append(analysis['page_number'])
                    pdf_result['white_page_count'] += 1
            
            pdf_doc.close()
            
        except Exception as e:
            pdf_result['error'] = str(e)
        
        pdf_result['processing_time'] = (datetime.now() - start_time).total_seconds()
        return pdf_result


class BatchWhitePageDetector:
    """
    Batch processor for detecting white pages in multiple PDF files.
    """
    
    def __init__(self, folder_path: str, white_threshold: float = 0.99, fallback_dpi: int = 150, 
                 output_format: str = 'console', output_file: str = None):
        """
        Initialize the batch detector.
        
        Args:
            folder_path (str): Path to folder containing PDF files
            white_threshold (float): Threshold for white detection
            fallback_dpi (int): Fallback DPI if PDF DPI cannot be detected
            output_format (str): Output format ('console', 'json', 'csv')
            output_file (str): Output file path (optional)
        """
        self.folder_path = Path(folder_path)
        self.white_threshold = white_threshold
        self.fallback_dpi = fallback_dpi
        self.output_format = output_format
        self.output_file = output_file
        
        if not self.folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        self.detector = WhitePageDetector(white_threshold, fallback_dpi)
    
    def _get_pdf_files(self) -> List[Path]:
        """Get all PDF files in the folder."""
        pdf_files = list(self.folder_path.glob("*.pdf"))
        pdf_files.extend(self.folder_path.glob("*.PDF"))
        return sorted(pdf_files)
    
    def _format_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _print_console_results(self, results: List[Dict]):
        """Print results to console."""
        print("\n" + "=" * 80)
        print("BATCH WHITE PAGE DETECTION RESULTS")
        print("=" * 80)
        print(f"Folder: {self.folder_path}")
        print(f"White threshold: {self.white_threshold * 100:.1f}%")
        print(f"Fallback DPI: {self.fallback_dpi}")
        print(f"Files processed: {len(results)}")
        print("-" * 80)
        
        total_files_with_white_pages = 0
        total_white_pages = 0
        total_pages = 0
        
        for result in results:
            if result['error']:
                print(f"\n❌ {result['file_name']}")
                print(f"   ERROR: {result['error']}")
                continue
            
            total_pages += result['total_pages']
            total_white_pages += result['white_page_count']
            
            if result['white_page_count'] > 0:
                total_files_with_white_pages += 1
                status_icon = "⚠️ "
            else:
                status_icon = "✅ "
            
            print(f"\n{status_icon}{result['file_name']}")
            print(f"   Size: {self._format_size(result['file_size'])}")
            print(f"   Pages: {result['total_pages']}")
            print(f"   DPI: {result['detected_dpi']:.1f} ({result['dpi_source']})")
            print(f"   White pages: {result['white_page_count']}")
            
            if result['white_page_count'] > 0:
                print(f"   White page numbers: {', '.join(map(str, result['white_pages']))}")
            
            if result['pages_with_errors'] > 0:
                print(f"   Pages with errors: {result['pages_with_errors']}")
            
            print(f"   Processing time: {result['processing_time']:.2f}s")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {len(results)}")
        print(f"Files with white pages: {total_files_with_white_pages}")
        print(f"Total pages analyzed: {total_pages}")
        print(f"Total white pages found: {total_white_pages}")
        if total_pages > 0:
            print(f"White page percentage: {(total_white_pages / total_pages) * 100:.2f}%")
    
    def _save_json_results(self, results: List[Dict]):
        """Save results to JSON file."""
        output_path = self.output_file or f"white_pages_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'scan_info': {
                'folder': str(self.folder_path),
                'white_threshold': self.white_threshold,
                'fallback_dpi': self.fallback_dpi,
                'scan_date': datetime.now().isoformat(),
                'total_files': len(results)
            },
            'results': results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Results saved to: {output_path}")
    
    def _save_csv_results(self, results: List[Dict]):
        """Save results to CSV file."""
        output_path = self.output_file or f"white_pages_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'File Name', 'File Path', 'File Size (bytes)', 'File Size (human)',
                'Total Pages', 'Detected DPI', 'DPI Source', 'White Pages Count', 'White Page Numbers',
                'Pages with Errors', 'Processing Time (s)', 'Error'
            ])
            
            # Write data
            for result in results:
                white_pages_str = ', '.join(map(str, result['white_pages'])) if result['white_pages'] else ''
                
                writer.writerow([
                    result['file_name'],
                    result['file_path'],
                    result['file_size'],
                    self._format_size(result['file_size']),
                    result['total_pages'],
                    f"{result['detected_dpi']:.1f}",
                    result['dpi_source'],
                    result['white_page_count'],
                    white_pages_str,
                    result['pages_with_errors'],
                    f"{result['processing_time']:.2f}",
                    result['error'] or ''
                ])
        
        print(f"Results saved to: {output_path}")
    
    def process_all_pdfs(self) -> List[Dict]:
        """
        Process all PDF files in the folder.
        
        Returns:
            List[Dict]: Results for all processed files
        """
        pdf_files = self._get_pdf_files()
        
        if not pdf_files:
            print(f"No PDF files found in {self.folder_path}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files in {self.folder_path}")
        print(f"White threshold: {self.white_threshold * 100:.1f}%")
        print(f"DPI detection: Auto-detect from each PDF (fallback: {self.fallback_dpi})")
        
        results = []
        
        # Process each PDF with progress bar
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            tqdm.write(f"Processing: {pdf_file.name}")
            result = self.detector.detect_white_pages_in_pdf(pdf_file)
            results.append(result)
        
        # Output results
        if self.output_format == 'console':
            self._print_console_results(results)
        elif self.output_format == 'json':
            self._save_json_results(results)
        elif self.output_format == 'csv':
            self._save_csv_results(results)
        
        return results


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description='Batch white page detection for PDF files with auto-DPI detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect_white_pages_batch.py -f /path/to/pdf/folder
  python detect_white_pages_batch.py -f /path/to/pdf/folder --threshold 0.95
  python detect_white_pages_batch.py -f /path/to/pdf/folder --fallback-dpi 200
  python detect_white_pages_batch.py -f /path/to/pdf/folder --output json --file report.json
  python detect_white_pages_batch.py -f /path/to/pdf/folder --output csv --file report.csv

Features:
  - Auto-detects DPI from each PDF's embedded images for accurate rendering
  - Falls back to specified DPI if no images found or DPI cannot be detected
  - Analyzes pixel data to detect white pages with configurable threshold
  - Supports multiple output formats (console, JSON, CSV)

Output formats:
  console: Print results to console (default)
  json: Save detailed results to JSON file
  csv: Save summary results to CSV file
        """
    )
    
    parser.add_argument(
        '-f', '--folder',
        required=True,
        help='Path to folder containing PDF files'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.99,
        help='White detection threshold (0.0-1.0, default: 0.99)'
    )
    
    parser.add_argument(
        '--fallback-dpi',
        type=int,
        default=150,
        help='Fallback DPI if PDF DPI cannot be detected (default: 150)'
    )
    
    parser.add_argument(
        '--output',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Output format (default: console)'
    )
    
    parser.add_argument(
        '--file',
        help='Output file path (optional, auto-generated if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        batch_detector = BatchWhitePageDetector(
            args.folder,
            args.threshold,
            args.fallback_dpi,
            args.output,
            args.file
        )
        
        results = batch_detector.process_all_pdfs()
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 