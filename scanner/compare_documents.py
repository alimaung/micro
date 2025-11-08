#!/usr/bin/env python3
"""
Microfilm Quality Comparison Tool

Compares original PDF documents with microfilm scans to assess quality.
Provides visual difference maps, SSIM scores, and OCR text comparison.
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.metrics import structural_similarity as ssim
import pytesseract
import difflib
from typing import List, Tuple, Dict, Any
import json
from datetime import datetime
from decimal import Decimal, getcontext

# Import AOI modules
from scanner.AOI.conversion import PDFConverter
from scanner.AOI.whiteness import WhitePageDetector
from scanner.AOI.orientation import ImageAligner

# Set high precision for decimal calculations
getcontext().prec = 50


class DocumentComparator:
    """Main class for comparing original and microfilm documents."""
    
    def __init__(self, dpi: int = 300, output_dir: str = "results", 
                 white_threshold: float = 0.997, white_pixel_threshold: int = 254):
        self.dpi = dpi
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Quality thresholds
        self.ssim_threshold = 0.7
        self.text_sim_threshold = 0.8
        
        # White page detection settings
        self.white_threshold = white_threshold
        self.white_pixel_threshold = white_pixel_threshold
        
        # Weights for final score calculation
        self.weights = {
            'ssim': 0.5,
            'text_similarity': 0.3,
            'layout_similarity': 0.2
        }
        
        # Initialize AOI modules
        self.pdf_converter = PDFConverter(dpi=self.dpi)
        self.white_detector = WhitePageDetector(
            dpi=self.dpi,
            white_threshold=self.white_threshold,
            white_pixel_threshold=self.white_pixel_threshold
        )
        self.image_aligner = ImageAligner()
    
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to grayscale numpy arrays."""
        return self.pdf_converter.pdf_to_images(pdf_path)
    
    def normalize_images(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Normalize two images to same size and apply preprocessing."""
        
        # Resize img2 to match img1 dimensions
        if img1.shape != img2.shape:
            img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        else:
            img2_resized = img2.copy()
        
        # Apply histogram equalization for better comparison
        img1_eq = cv2.equalizeHist(img1)
        img2_eq = cv2.equalizeHist(img2_resized)
        
        # Optional: Apply slight Gaussian blur to reduce noise
        img1_blur = cv2.GaussianBlur(img1_eq, (3, 3), 0)
        img2_blur = cv2.GaussianBlur(img2_eq, (3, 3), 0)
        
        return img1_blur, img2_blur
    
    def is_white_page(self, pdf_path: str, page_index: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a page is completely white.
        
        Args:
            pdf_path (str): Path to the PDF file
            page_index (int): Zero-based page index
            
        Returns:
            Tuple[bool, Dict]: (is_white, analysis_info)
        """
        return self.white_detector.is_white_page(pdf_path, page_index)
    
    def align_images(self, orig_img: np.ndarray, film_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Align film image to original image using rotation detection."""
        return self.image_aligner.align_images(orig_img, film_img)
    
    def calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[float, np.ndarray]:
        """Calculate SSIM score and difference map."""
        
        # Normalize images
        norm_img1, norm_img2 = self.normalize_images(img1, img2)
        
        # Calculate SSIM
        ssim_score, diff_map = ssim(norm_img1, norm_img2, full=True)
        
        # Convert difference map to 0-255 range
        diff_map = (diff_map * 255).astype(np.uint8)
        
        return ssim_score, diff_map
    
    def extract_text_ocr(self, img: np.ndarray) -> str:
        """Extract text from image using OCR."""
        try:
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(img, config=custom_config)
            return text.strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching."""
        
        # Normalize texts (remove extra whitespace, convert to lowercase)
        norm_text1 = ' '.join(text1.lower().split())
        norm_text2 = ' '.join(text2.lower().split())
        
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, norm_text1, norm_text2).ratio()
        
        return similarity
    
    def calculate_layout_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate layout similarity based on edge detection."""
        
        # Normalize images
        norm_img1, norm_img2 = self.normalize_images(img1, img2)
        
        # Apply edge detection
        edges1 = cv2.Canny(norm_img1, 50, 150)
        edges2 = cv2.Canny(norm_img2, 50, 150)
        
        # Calculate similarity of edge maps
        edge_similarity, _ = ssim(edges1, edges2, full=True)
        
        return edge_similarity
    
    def create_visual_comparison(self, orig_img: np.ndarray, film_img: np.ndarray, 
                               diff_map: np.ndarray, page_num: int, 
                               metrics: Dict[str, float]) -> str:
        """Create visual comparison plot and save to file."""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Page {page_num} Comparison - Quality Score: {metrics["quality_score"]:.3f}', 
                     fontsize=16, fontweight='bold')
        
        # Original image
        axes[0, 0].imshow(orig_img, cmap='gray')
        axes[0, 0].set_title('Original Document')
        axes[0, 0].axis('off')
        
        # Microfilm scan
        axes[0, 1].imshow(film_img, cmap='gray')
        axes[0, 1].set_title('Microfilm Scan')
        axes[0, 1].axis('off')
        
        # Difference map
        axes[1, 0].imshow(diff_map, cmap='hot')
        axes[1, 0].set_title('Difference Map (SSIM)')
        axes[1, 0].axis('off')
        
        # Metrics summary
        axes[1, 1].axis('off')
        
        # Get alignment info if available
        alignment_info = metrics.get('alignment_info', {})
        coarse_rot = alignment_info.get('coarse_rotation', 0)
        fine_angle = alignment_info.get('fine_angle', 0)
        total_rot = alignment_info.get('total_rotation', 0)
        
        metrics_text = f"""
Quality Metrics:

SSIM Score: {metrics['ssim']:.3f}
Text Similarity: {metrics['text_similarity']:.3f}
Layout Similarity: {metrics['layout_similarity']:.3f}

Final Quality Score: {metrics['quality_score']:.3f}

Alignment Applied:
Coarse Rotation: {coarse_rot}°
Fine Adjustment: {fine_angle:.1f}°
Total Rotation: {total_rot:.1f}°

Status: {'PASS' if metrics['quality_score'] > 0.7 else 'FAIL'}
        """
        axes[1, 1].text(0.1, 0.5, metrics_text, fontsize=10, 
                        verticalalignment='center', fontfamily='monospace')
        
        # Add colored border based on quality
        color = 'green' if metrics['quality_score'] > 0.7 else 'red'
        rect = patches.Rectangle((0, 0), 1, 1, linewidth=3, edgecolor=color, 
                               facecolor='none', transform=axes[1, 1].transAxes)
        axes[1, 1].add_patch(rect)
        
        plt.tight_layout()
        
        # Save the plot
        output_path = self.output_dir / f"page_{page_num:03d}_comparison.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def compare_page(self, orig_img: np.ndarray, film_img: np.ndarray, 
                    page_num: int, orig_is_white: bool = False,
                    orig_pdf_path: str = None, film_pdf_path: str = None,
                    orig_page_index: int = None, film_page_index: int = None) -> Dict[str, Any]:
        """Compare a single page and return metrics."""
        
        print(f"Comparing page {page_num}...")
        
        # Step 1: Align images (rotation detection and correction)
        aligned_orig, aligned_film, alignment_info = self.align_images(
            orig_img, film_img,
            orig_is_white=orig_is_white,
            orig_pdf_path=orig_pdf_path,
            film_pdf_path=film_pdf_path,
            orig_page_index=orig_page_index,
            film_page_index=film_page_index
        )
        
        # Step 2: Calculate SSIM on aligned images
        ssim_score, diff_map = self.calculate_ssim(aligned_orig, aligned_film)
        
        # Step 3: Extract and compare text from aligned images
        orig_text = self.extract_text_ocr(aligned_orig)
        film_text = self.extract_text_ocr(aligned_film)
        text_similarity = self.calculate_text_similarity(orig_text, film_text)
        
        # Step 4: Calculate layout similarity on aligned images
        layout_similarity = self.calculate_layout_similarity(aligned_orig, aligned_film)
        
        # Step 5: Calculate weighted quality score
        quality_score = (
            self.weights['ssim'] * ssim_score +
            self.weights['text_similarity'] * text_similarity +
            self.weights['layout_similarity'] * layout_similarity
        )
        
        metrics = {
            'page': page_num,
            'ssim': ssim_score,
            'text_similarity': text_similarity,
            'layout_similarity': layout_similarity,
            'quality_score': quality_score,
            'original_text_length': len(orig_text),
            'film_text_length': len(film_text),
            'alignment_info': alignment_info
        }
        
        # Create visual comparison using aligned images
        visual_path = self.create_visual_comparison(aligned_orig, aligned_film, diff_map, 
                                                  page_num, metrics)
        metrics['visual_path'] = visual_path
        
        return metrics
    
    def compare_documents(self, original_path: str, microfilm_path: str) -> Dict[str, Any]:
        """Compare two documents and return comprehensive results."""
        
        print(f"Starting document comparison...")
        print(f"Original: {original_path}")
        print(f"Microfilm: {microfilm_path}")
        print(f"White page threshold: {self.white_threshold * 100:.4f}%")
        print(f"White pixel threshold: {self.white_pixel_threshold}/255")
        
        # Step 1: Check original pages for whiteness (only original, since repro has same page order)
        print(f"\n{'='*70}")
        print("Step 1: Checking original pages for whiteness...")
        print(f"{'='*70}")
        skip_list = self.white_detector.check_original_pages(original_path)
        skip_set = set(skip_list)  # For faster lookup
        
        # Step 2: Convert PDFs to images (all pages)
        print(f"\n{'='*70}")
        print("Step 2: Converting PDFs to images...")
        print(f"{'='*70}")
        orig_images = self.pdf_to_images(original_path)
        film_images = self.pdf_to_images(microfilm_path)
        
        if not orig_images or not film_images:
            raise ValueError("Failed to convert one or both PDFs to images")
        
        if len(orig_images) != len(film_images):
            print(f"Warning: Page count mismatch - Original: {len(orig_images)}, "
                  f"Microfilm: {len(film_images)}")
        
        # Step 3: Process each page
        print(f"\n{'='*70}")
        print("Step 3: Processing pages...")
        print(f"{'='*70}")
        page_results = []
        skipped_pages = []
        min_pages = min(len(orig_images), len(film_images))
        
        for i in range(min_pages):
            page_num = i + 1
            print(f"\nProcessing page {page_num}...")
            
            if i in skip_set:
                # White page - use PDF metadata for orientation only, skip comparison
                print(f"  Page {page_num} is white - using PDF metadata for orientation, skipping comparison")
                
                # Get orientation using PDF metadata
                alignment_info = self.image_aligner.get_pdf_orientation(
                    original_path, microfilm_path, i, i
                )
                
                # Get white page info for reporting
                _, orig_white_info = self.is_white_page(original_path, i)
                
                page_result = {
                    'page': page_num,
                    'skipped': True,
                    'skip_reason': ['original_white'],
                    'original_white_info': orig_white_info,
                    'film_white_info': None,  # Not checked for film pages
                    'ssim': None,
                    'text_similarity': None,
                    'layout_similarity': None,
                    'quality_score': None,
                    'alignment_info': alignment_info  # Orientation info from PDF metadata
                }
                page_results.append(page_result)
                skipped_pages.append(page_num)
                continue
            
            # Non-white page - full processing
            print(f"  Page {page_num} has content - performing full comparison")
            page_metrics = self.compare_page(
                orig_images[i], film_images[i], page_num,
                orig_is_white=False,
                orig_pdf_path=original_path,
                film_pdf_path=microfilm_path,
                orig_page_index=i,
                film_page_index=i
            )
            page_metrics['skipped'] = False
            # Get white page info for reporting (even though not white, for consistency)
            _, orig_white_info = self.is_white_page(original_path, i)
            page_metrics['original_white_info'] = orig_white_info
            page_metrics['film_white_info'] = None  # Not checked for film pages
            page_results.append(page_metrics)
        
        # Calculate overall document metrics (excluding skipped pages)
        compared_pages = [p for p in page_results if not p['skipped']]
        overall_metrics = self.calculate_overall_metrics(compared_pages)
        
        # Add white page statistics to overall metrics
        overall_metrics.update({
            'total_pages_processed': min_pages,
            'pages_compared': len(compared_pages),
            'pages_skipped': len(skipped_pages),
            'white_pages_original': len(skip_list),
            'white_pages_film': 0,  # Not checked
            'white_pages_original_list': [i + 1 for i in skip_list],
            'white_pages_film_list': [],
            'skipped_pages_list': skipped_pages
        })
        
        # Generate summary report
        report = {
            'timestamp': datetime.now().isoformat(),
            'original_document': original_path,
            'microfilm_document': microfilm_path,
            'total_pages': min_pages,
            'overall_metrics': overall_metrics,
            'page_results': page_results,
            'settings': {
                'dpi': self.dpi,
                'weights': self.weights,
                'thresholds': {
                    'ssim': self.ssim_threshold,
                    'text_similarity': self.text_sim_threshold
                },
                'white_page_detection': {
                    'white_threshold': self.white_threshold,
                    'white_pixel_threshold': self.white_pixel_threshold
                }
            }
        }
        
        # Save report to JSON (ensure all values are JSON serializable)
        def json_serializer(obj):
            """Custom JSON serializer for numpy and other non-serializable types."""
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            else:
                return str(obj)
        
        report_path = self.output_dir / "comparison_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=json_serializer)
        
        print(f"\nComparison complete! Report saved to: {report_path}")
        
        return report
    
    def calculate_overall_metrics(self, page_results: List[Dict]) -> Dict[str, float]:
        """Calculate overall document quality metrics."""
        
        if not page_results:
            return {}
        
        # Calculate averages
        avg_ssim = np.mean([p['ssim'] for p in page_results])
        avg_text_sim = np.mean([p['text_similarity'] for p in page_results])
        avg_layout_sim = np.mean([p['layout_similarity'] for p in page_results])
        avg_quality = np.mean([p['quality_score'] for p in page_results])
        
        # Calculate pass/fail counts
        pass_count = sum(1 for p in page_results if p['quality_score'] > 0.7)
        fail_count = len(page_results) - pass_count
        
        return {
            'average_ssim': avg_ssim,
            'average_text_similarity': avg_text_sim,
            'average_layout_similarity': avg_layout_sim,
            'average_quality_score': avg_quality,
            'pages_passed': pass_count,
            'pages_failed': fail_count,
            'pass_rate': pass_count / len(page_results)
        }
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the comparison results."""
        
        overall = report['overall_metrics']
        
        print("\n" + "="*70)
        print("MICROFILM QUALITY COMPARISON SUMMARY")
        print("="*70)
        print(f"Total Pages Processed: {overall.get('total_pages_processed', report['total_pages'])}")
        print(f"Pages Compared: {overall.get('pages_compared', 0)}")
        print(f"Pages Skipped (White): {overall.get('pages_skipped', 0)}")
        
        # White page details
        if overall.get('pages_skipped', 0) > 0:
            print(f"\nWhite Page Detection:")
            print(f"  Original white pages: {overall.get('white_pages_original', 0)}")
            if overall.get('white_pages_original_list'):
                print(f"    Pages: {', '.join(map(str, overall['white_pages_original_list']))}")
            print(f"  Film white pages: {overall.get('white_pages_film', 0)}")
            if overall.get('white_pages_film_list'):
                print(f"    Pages: {', '.join(map(str, overall['white_pages_film_list']))}")
            if overall.get('skipped_pages_list'):
                print(f"  All skipped pages: {', '.join(map(str, overall['skipped_pages_list']))}")
        
        # Quality metrics (only for compared pages)
        if overall.get('pages_compared', 0) > 0:
            print(f"\nQuality Analysis (Compared Pages Only):")
            print(f"Overall Quality Score: {overall['average_quality_score']:.3f}")
            print(f"Pass Rate: {overall['pass_rate']:.1%}")
            print(f"Pages Passed: {overall['pages_passed']}")
            print(f"Pages Failed: {overall['pages_failed']}")
            print("\nDetailed Metrics:")
            print(f"  Average SSIM: {overall['average_ssim']:.3f}")
            print(f"  Average Text Similarity: {overall['average_text_similarity']:.3f}")
            print(f"  Average Layout Similarity: {overall['average_layout_similarity']:.3f}")
        else:
            print(f"\nNo pages were compared (all pages were white or skipped)")
        
        print(f"\nResults saved to: {self.output_dir}")
        print("="*70)


def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description='Compare original and microfilm documents with rotation alignment and white page detection')
    parser.add_argument('--original', required=True, help='Path to original PDF')
    parser.add_argument('--microfilm', required=True, help='Path to microfilm PDF')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF conversion (default: 300)')
    parser.add_argument('--output', default='results', help='Output directory (default: results)')
    parser.add_argument('--white-threshold', type=float, default=0.997, 
                       help='White page threshold (0.0-1.0, default: 0.997 = 99.7%%)')
    parser.add_argument('--white-pixel-threshold', type=int, default=254,
                       help='White pixel threshold (0-255, default: 254)')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original):
        print(f"Error: Original file not found: {args.original}")
        sys.exit(1)
    
    if not os.path.exists(args.microfilm):
        print(f"Error: Microfilm file not found: {args.microfilm}")
        sys.exit(1)
    
    # Validate thresholds
    if not 0.0 <= args.white_threshold <= 1.0:
        print(f"Error: White threshold must be between 0.0 and 1.0")
        sys.exit(1)
    
    if not 0 <= args.white_pixel_threshold <= 255:
        print(f"Error: White pixel threshold must be between 0 and 255")
        sys.exit(1)
    
    try:
        # Create comparator and run comparison
        comparator = DocumentComparator(
            dpi=args.dpi, 
            output_dir=args.output,
            white_threshold=args.white_threshold,
            white_pixel_threshold=args.white_pixel_threshold
        )
        report = comparator.compare_documents(args.original, args.microfilm)
        comparator.print_summary(report)
        
    except Exception as e:
        print(f"Error during comparison: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
