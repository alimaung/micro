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
from pdf2image import convert_from_path
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template
import pytesseract
import difflib
from typing import List, Tuple, Dict, Any
import json
from datetime import datetime
from scipy import ndimage
from decimal import Decimal, getcontext
import fitz  # PyMuPDF for rendering PDF pages to images
from PIL import Image
import io

# Set high precision for decimal calculations
getcontext().prec = 50


class DocumentComparator:
    """Main class for comparing original and microfilm documents."""
    
    def __init__(self, dpi: int = 300, output_dir: str = "results", 
                 white_threshold: float = 0.9999, white_pixel_threshold: int = 254):
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
    
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to grayscale numpy arrays."""
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
    
    def _render_page_to_image_for_white_detection(self, pdf_path: str, page_index: int) -> Image.Image:
        """Render a PDF page to a PIL Image for white page detection."""
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
            img = self._render_page_to_image_for_white_detection(pdf_path, page_index)
            
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
    
    def detect_rotation(self, orig_img: np.ndarray, film_img: np.ndarray) -> int:
        """Detect the rotation angle between original and film (0, 90, 180, 270 degrees)."""
        
        print("Detecting rotation between original and film...")
        
        # Resize images to smaller size for faster processing
        height, width = orig_img.shape
        scale_factor = min(1.0, 800 / max(height, width))
        
        if scale_factor < 1.0:
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            orig_small = cv2.resize(orig_img, (new_width, new_height))
            film_small = cv2.resize(film_img, (new_width, new_height))
        else:
            orig_small = orig_img.copy()
            film_small = film_img.copy()
        
        # Apply edge detection for better matching
        orig_edges = cv2.Canny(orig_small, 50, 150)
        film_edges = cv2.Canny(film_small, 50, 150)
        
        # Test different rotations (0, 90, 180, 270 degrees)
        rotations = [0, 90, 180, 270]
        best_score = -1
        best_rotation = 0
        
        for rotation in rotations:
            # Rotate the film image
            if rotation == 90:
                rotated_film = cv2.rotate(film_edges, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif rotation == 180:
                rotated_film = cv2.rotate(film_edges, cv2.ROTATE_180)
            elif rotation == 270:
                rotated_film = cv2.rotate(film_edges, cv2.ROTATE_90_CLOCKWISE)
            else:
                rotated_film = film_edges.copy()
            
            # Resize rotated image to match original if needed
            if rotated_film.shape != orig_edges.shape:
                rotated_film = cv2.resize(rotated_film, (orig_edges.shape[1], orig_edges.shape[0]))
            
            # Calculate correlation score
            try:
                score, _ = ssim(orig_edges, rotated_film, full=True)
                print(f"Rotation {rotation}°: SSIM score = {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_rotation = rotation
            except Exception as e:
                print(f"Error calculating SSIM for rotation {rotation}°: {e}")
                continue
        
        print(f"Best rotation detected: {best_rotation}° (score: {best_score:.3f})")
        return best_rotation
    
    def find_fine_angle(self, orig_img: np.ndarray, film_img: np.ndarray, 
                       coarse_rotation: int) -> float:
        """Find fine angle adjustment after coarse rotation."""
        
        print("Finding fine angle adjustment...")
        
        # Apply coarse rotation first
        if coarse_rotation == 90:
            rotated_film = cv2.rotate(film_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif coarse_rotation == 180:
            rotated_film = cv2.rotate(film_img, cv2.ROTATE_180)
        elif coarse_rotation == 270:
            rotated_film = cv2.rotate(film_img, cv2.ROTATE_90_CLOCKWISE)
        else:
            rotated_film = film_img.copy()
        
        # Resize to match original
        if rotated_film.shape != orig_img.shape:
            rotated_film = cv2.resize(rotated_film, (orig_img.shape[1], orig_img.shape[0]))
        
        # Test fine angles from -10 to +10 degrees
        angles = np.arange(-10, 11, 0.5)
        best_score = -1
        best_angle = 0
        
        # Use smaller images for faster processing
        height, width = orig_img.shape
        scale_factor = min(1.0, 600 / max(height, width))
        
        if scale_factor < 1.0:
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            orig_small = cv2.resize(orig_img, (new_width, new_height))
            film_small = cv2.resize(rotated_film, (new_width, new_height))
        else:
            orig_small = orig_img.copy()
            film_small = rotated_film.copy()
        
        # Apply edge detection
        orig_edges = cv2.Canny(orig_small, 50, 150)
        
        for angle in angles:
            # Rotate the film image by fine angle
            center = (film_small.shape[1] // 2, film_small.shape[0] // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            fine_rotated = cv2.warpAffine(film_small, rotation_matrix, 
                                        (film_small.shape[1], film_small.shape[0]))
            
            # Apply edge detection
            fine_edges = cv2.Canny(fine_rotated, 50, 150)
            
            # Calculate correlation score
            try:
                score, _ = ssim(orig_edges, fine_edges, full=True)
                
                if score > best_score:
                    best_score = score
                    best_angle = angle
            except Exception as e:
                continue
        
        print(f"Best fine angle: {best_angle:.1f}° (score: {best_score:.3f})")
        return best_angle
    
    def align_images(self, orig_img: np.ndarray, film_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Align film image to original image using rotation detection."""
        
        print("Aligning images...")
        
        # Step 1: Detect coarse rotation (90-degree increments)
        coarse_rotation = self.detect_rotation(orig_img, film_img)
        
        # Step 2: Find fine angle adjustment
        fine_angle = self.find_fine_angle(orig_img, film_img, coarse_rotation)
        
        # Step 3: Apply transformations to film image
        aligned_film = film_img.copy()
        
        # Apply coarse rotation
        if coarse_rotation == 90:
            aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif coarse_rotation == 180:
            aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_180)
        elif coarse_rotation == 270:
            aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_90_CLOCKWISE)
        
        # Apply fine rotation
        if abs(fine_angle) > 0.1:  # Only apply if significant
            center = (aligned_film.shape[1] // 2, aligned_film.shape[0] // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, fine_angle, 1.0)
            aligned_film = cv2.warpAffine(aligned_film, rotation_matrix, 
                                        (aligned_film.shape[1], aligned_film.shape[0]))
        
        # Resize to match original dimensions
        if aligned_film.shape != orig_img.shape:
            aligned_film = cv2.resize(aligned_film, (orig_img.shape[1], orig_img.shape[0]))
        
        # Store alignment info
        alignment_info = {
            'coarse_rotation': coarse_rotation,
            'fine_angle': fine_angle,
            'total_rotation': coarse_rotation + fine_angle
        }
        
        print(f"Alignment complete: {coarse_rotation}° + {fine_angle:.1f}° = {coarse_rotation + fine_angle:.1f}°")
        
        return orig_img, aligned_film, alignment_info
    
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
                    page_num: int) -> Dict[str, Any]:
        """Compare a single page and return metrics."""
        
        print(f"Comparing page {page_num}...")
        
        # Step 1: Align images (rotation detection and correction)
        aligned_orig, aligned_film, alignment_info = self.align_images(orig_img, film_img)
        
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
        
        # Convert PDFs to images
        orig_images = self.pdf_to_images(original_path)
        film_images = self.pdf_to_images(microfilm_path)
        
        if not orig_images or not film_images:
            raise ValueError("Failed to convert one or both PDFs to images")
        
        if len(orig_images) != len(film_images):
            print(f"Warning: Page count mismatch - Original: {len(orig_images)}, "
                  f"Microfilm: {len(film_images)}")
        
        # Compare each page with white page detection
        page_results = []
        white_pages_orig = []
        white_pages_film = []
        skipped_pages = []
        min_pages = min(len(orig_images), len(film_images))
        
        print(f"\nAnalyzing {min_pages} pages...")
        
        for i in range(min_pages):
            page_num = i + 1
            print(f"\nProcessing page {page_num}...")
            
            # Check if either page is white
            orig_is_white, orig_white_info = self.is_white_page(original_path, i)
            film_is_white, film_white_info = self.is_white_page(microfilm_path, i)
            
            if orig_is_white:
                white_pages_orig.append(page_num)
                print(f"  Original page {page_num} is white ({orig_white_info['white_percentage']:.4f}% white)")
            
            if film_is_white:
                white_pages_film.append(page_num)
                print(f"  Film page {page_num} is white ({film_white_info['white_percentage']:.4f}% white)")
            
            # Skip comparison if either page is white
            if orig_is_white or film_is_white:
                skipped_pages.append(page_num)
                skip_reason = []
                if orig_is_white:
                    skip_reason.append("original_white")
                if film_is_white:
                    skip_reason.append("film_white")
                
                page_result = {
                    'page': page_num,
                    'skipped': True,
                    'skip_reason': skip_reason,
                    'original_white_info': orig_white_info,
                    'film_white_info': film_white_info,
                    'ssim': None,
                    'text_similarity': None,
                    'layout_similarity': None,
                    'quality_score': None,
                    'alignment_info': None
                }
                page_results.append(page_result)
                print(f"  Skipping page {page_num} comparison (white page detected)")
                continue
            
            # Perform normal comparison for non-white pages
            print(f"  Comparing page {page_num} (both pages have content)")
            page_metrics = self.compare_page(orig_images[i], film_images[i], page_num)
            page_metrics['skipped'] = False
            page_metrics['original_white_info'] = orig_white_info
            page_metrics['film_white_info'] = film_white_info
            page_results.append(page_metrics)
        
        # Calculate overall document metrics (excluding skipped pages)
        compared_pages = [p for p in page_results if not p['skipped']]
        overall_metrics = self.calculate_overall_metrics(compared_pages)
        
        # Add white page statistics to overall metrics
        overall_metrics.update({
            'total_pages_processed': min_pages,
            'pages_compared': len(compared_pages),
            'pages_skipped': len(skipped_pages),
            'white_pages_original': len(white_pages_orig),
            'white_pages_film': len(white_pages_film),
            'white_pages_original_list': white_pages_orig,
            'white_pages_film_list': white_pages_film,
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
    parser.add_argument('--white-threshold', type=float, default=0.9999, 
                       help='White page threshold (0.0-1.0, default: 0.9999)')
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
