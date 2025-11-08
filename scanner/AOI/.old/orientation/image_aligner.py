#!/usr/bin/env python3
"""
Image Alignment Module

Applies orientation corrections to align reproduction images with originals.
Provides aligned image pairs for subsequent AOI analysis.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
import matplotlib.pyplot as plt
import json
from datetime import datetime
from pdf_converter import PDFConverter
from orientation_detector import OrientationDetector


class ImageAligner:
    """
    Applies orientation corrections to align images for AOI analysis.
    """
    
    def __init__(self, output_dir: str = "aligned_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Alignment parameters
        self.save_aligned_images = True  # Save aligned images to disk
        self.create_comparison_plots = True  # Create before/after comparison plots
        
        # Size normalization options
        self.normalize_sizes = True
        self.target_size_method = "original"  # "original", "reproduction", "largest", "custom"
        self.custom_size = None  # (width, height) if using custom
        
    def rotate_image(self, img: np.ndarray, angle: float, 
                    maintain_size: bool = False) -> np.ndarray:
        """
        Rotate image by specified angle.
        
        Args:
            img: Input image
            angle: Rotation angle in degrees (positive = counterclockwise)
            maintain_size: If True, keeps original image dimensions (may crop)
                          If False, expands canvas to fit rotated image
            
        Returns:
            Rotated image
        """
        if abs(angle) < 0.01:  # No rotation needed
            return img.copy()
        
        h, w = img.shape[:2]
        
        # Handle 90-degree increments efficiently
        if abs(angle - 90) < 0.01:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif abs(angle - 180) < 0.01:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif abs(angle - 270) < 0.01 or abs(angle + 90) < 0.01:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        
        # Fine rotation using affine transformation
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        if maintain_size:
            # Keep original dimensions (may crop content)
            rotated = cv2.warpAffine(img, rotation_matrix, (w, h))
        else:
            # Expand canvas to fit rotated image (no cropping)
            cos_angle = abs(rotation_matrix[0, 0])
            sin_angle = abs(rotation_matrix[0, 1])
            new_w = int((h * sin_angle) + (w * cos_angle))
            new_h = int((h * cos_angle) + (w * sin_angle))
            
            # Adjust rotation matrix for new dimensions
            rotation_matrix[0, 2] += (new_w / 2) - center[0]
            rotation_matrix[1, 2] += (new_h / 2) - center[1]
            
            rotated = cv2.warpAffine(img, rotation_matrix, (new_w, new_h))
        
        return rotated
    
    def normalize_image_sizes(self, img1: np.ndarray, img2: np.ndarray, 
                            method: str = "original") -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalize sizes of two images.
        
        Args:
            img1: First image (typically original)
            img2: Second image (typically reproduction)
            method: Size normalization method
                   - "original": Use img1 size
                   - "reproduction": Use img2 size  
                   - "largest": Use largest dimensions
                   - "custom": Use self.custom_size
                   
        Returns:
            Tuple of size-normalized images
        """
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        if method == "original":
            target_size = (w1, h1)
        elif method == "reproduction":
            target_size = (w2, h2)
        elif method == "largest":
            target_size = (max(w1, w2), max(h1, h2))
        elif method == "custom" and self.custom_size:
            target_size = self.custom_size
        else:
            # Default to original size
            target_size = (w1, h1)
        
        # Resize images if needed
        if (h1, w1) != (target_size[1], target_size[0]):
            img1_resized = cv2.resize(img1, target_size)
        else:
            img1_resized = img1.copy()
            
        if (h2, w2) != (target_size[1], target_size[0]):
            img2_resized = cv2.resize(img2, target_size)
        else:
            img2_resized = img2.copy()
        
        return img1_resized, img2_resized
    
    def align_single_page(self, original_img: np.ndarray, reproduction_img: np.ndarray,
                         rotation_angle: float, page_num: int) -> Dict[str, Any]:
        """
        Align a single page pair.
        
        Args:
            original_img: Original page image
            reproduction_img: Reproduction page image
            rotation_angle: Rotation angle to apply to reproduction
            page_num: Page number for naming/tracking
            
        Returns:
            Dictionary with alignment results
        """
        print(f"Aligning page {page_num} (rotation: {rotation_angle:.1f}°)...")
        
        # Step 1: Apply rotation correction
        aligned_reproduction = self.rotate_image(reproduction_img, rotation_angle, 
                                               maintain_size=False)
        
        # Step 2: Normalize sizes if requested
        if self.normalize_sizes:
            original_normalized, aligned_normalized = self.normalize_image_sizes(
                original_img, aligned_reproduction, method=self.target_size_method
            )
        else:
            original_normalized = original_img.copy()
            aligned_normalized = aligned_reproduction.copy()
        
        # Step 3: Calculate alignment quality metrics
        alignment_metrics = self._calculate_alignment_metrics(original_normalized, 
                                                            aligned_normalized)
        
        # Step 4: Save aligned images if requested
        saved_paths = {}
        if self.save_aligned_images:
            saved_paths = self._save_aligned_images(original_normalized, aligned_normalized,
                                                  reproduction_img, page_num, rotation_angle)
        
        # Step 5: Create comparison visualization if requested
        comparison_path = None
        if self.create_comparison_plots:
            comparison_path = self._create_alignment_comparison(
                original_img, reproduction_img, original_normalized, aligned_normalized,
                page_num, rotation_angle, alignment_metrics
            )
        
        result = {
            'page': page_num,
            'rotation_applied': rotation_angle,
            'original_shape': original_img.shape,
            'reproduction_original_shape': reproduction_img.shape,
            'aligned_shape': aligned_normalized.shape,
            'size_normalized': self.normalize_sizes,
            'alignment_metrics': alignment_metrics,
            'saved_paths': saved_paths,
            'comparison_visualization': comparison_path,
            'aligned_images': {
                'original': original_normalized,
                'reproduction': aligned_normalized
            }
        }
        
        return result
    
    def _calculate_alignment_metrics(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, float]:
        """Calculate metrics to assess alignment quality."""
        
        from skimage.metrics import structural_similarity as ssim
        
        metrics = {}
        
        try:
            # SSIM score
            ssim_score, _ = ssim(img1, img2, full=True)
            metrics['ssim'] = float(ssim_score)
        except Exception:
            metrics['ssim'] = 0.0
        
        try:
            # Normalized cross-correlation
            img1_norm = cv2.normalize(img1.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            img2_norm = cv2.normalize(img2.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            correlation = cv2.matchTemplate(img1_norm, img2_norm, cv2.TM_CCOEFF_NORMED)[0, 0]
            metrics['correlation'] = float(correlation)
        except Exception:
            metrics['correlation'] = 0.0
        
        try:
            # Mean squared error (lower is better)
            mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
            metrics['mse'] = float(mse)
        except Exception:
            metrics['mse'] = float('inf')
        
        try:
            # Peak signal-to-noise ratio
            if metrics['mse'] > 0:
                psnr = 20 * np.log10(255.0 / np.sqrt(metrics['mse']))
                metrics['psnr'] = float(psnr)
            else:
                metrics['psnr'] = float('inf')
        except Exception:
            metrics['psnr'] = 0.0
        
        return metrics
    
    def _save_aligned_images(self, original: np.ndarray, aligned_repro: np.ndarray,
                           original_repro: np.ndarray, page_num: int, 
                           rotation: float) -> Dict[str, str]:
        """Save aligned images to disk."""
        
        saved_paths = {}
        
        # Create page-specific directory
        page_dir = self.output_dir / f"page_{page_num:03d}"
        page_dir.mkdir(exist_ok=True)
        
        # Save original (normalized)
        orig_path = page_dir / f"original_normalized.png"
        cv2.imwrite(str(orig_path), original)
        saved_paths['original_normalized'] = str(orig_path)
        
        # Save aligned reproduction
        aligned_path = page_dir / f"reproduction_aligned_{rotation:.1f}deg.png"
        cv2.imwrite(str(aligned_path), aligned_repro)
        saved_paths['reproduction_aligned'] = str(aligned_path)
        
        # Save original reproduction (before alignment)
        orig_repro_path = page_dir / f"reproduction_original.png"
        cv2.imwrite(str(orig_repro_path), original_repro)
        saved_paths['reproduction_original'] = str(orig_repro_path)
        
        return saved_paths
    
    def _create_alignment_comparison(self, original_img: np.ndarray, reproduction_img: np.ndarray,
                                   aligned_original: np.ndarray, aligned_reproduction: np.ndarray,
                                   page_num: int, rotation: float, 
                                   metrics: Dict[str, float]) -> str:
        """Create before/after alignment comparison visualization."""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Page {page_num} Alignment Results (Rotation: {rotation:.1f}°)', 
                     fontsize=16, fontweight='bold')
        
        # Before alignment
        axes[0, 0].imshow(original_img, cmap='gray')
        axes[0, 0].set_title('Original')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(reproduction_img, cmap='gray')
        axes[0, 1].set_title('Reproduction (Before)')
        axes[0, 1].axis('off')
        
        # Difference before alignment (if same size)
        if original_img.shape == reproduction_img.shape:
            diff_before = cv2.absdiff(original_img, reproduction_img)
            axes[0, 2].imshow(diff_before, cmap='hot')
            axes[0, 2].set_title('Difference (Before)')
        else:
            axes[0, 2].text(0.5, 0.5, 'Size Mismatch\nCannot Show Difference', 
                           ha='center', va='center', transform=axes[0, 2].transAxes)
            axes[0, 2].set_title('Difference (Before)')
        axes[0, 2].axis('off')
        
        # After alignment
        axes[1, 0].imshow(aligned_original, cmap='gray')
        axes[1, 0].set_title('Original (Normalized)')
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(aligned_reproduction, cmap='gray')
        axes[1, 1].set_title('Reproduction (Aligned)')
        axes[1, 1].axis('off')
        
        # Difference after alignment
        diff_after = cv2.absdiff(aligned_original, aligned_reproduction)
        axes[1, 2].imshow(diff_after, cmap='hot')
        axes[1, 2].set_title('Difference (After)')
        axes[1, 2].axis('off')
        
        # Add metrics text
        metrics_text = f"""
Alignment Quality Metrics:

SSIM: {metrics.get('ssim', 0):.4f}
Correlation: {metrics.get('correlation', 0):.4f}
MSE: {metrics.get('mse', 0):.2f}
PSNR: {metrics.get('psnr', 0):.2f} dB

Rotation Applied: {rotation:.1f}°
Size Normalization: {'Yes' if self.normalize_sizes else 'No'}
Target Size Method: {self.target_size_method}
        """
        
        # Add text box with metrics
        fig.text(0.02, 0.02, metrics_text, fontsize=10, fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        
        # Save comparison
        comparison_path = self.output_dir / f"page_{page_num:03d}_alignment_comparison.png"
        plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(comparison_path)
    
    def align_document_pair(self, original_images: List[np.ndarray], 
                          reproduction_images: List[np.ndarray],
                          orientation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Align entire document pair using orientation detection results.
        
        Args:
            original_images: List of original page images
            reproduction_images: List of reproduction page images
            orientation_results: Results from orientation detection
            
        Returns:
            Complete alignment results with aligned image pairs
        """
        print(f"\n{'='*70}")
        print("DOCUMENT ALIGNMENT")
        print(f"{'='*70}")
        
        min_pages = min(len(original_images), len(reproduction_images))
        page_results = []
        aligned_pairs = []
        
        # Extract rotation angles from orientation results
        page_orientations = {}
        if 'page_results' in orientation_results:
            for page_result in orientation_results['page_results']:
                page_num = page_result['page']
                rotation = page_result['final_rotation']
                page_orientations[page_num] = rotation
        
        for i in range(min_pages):
            page_num = i + 1
            
            # Get rotation angle for this page
            rotation_angle = page_orientations.get(page_num, 0.0)
            
            # Align this page
            alignment_result = self.align_single_page(
                original_images[i], reproduction_images[i], rotation_angle, page_num
            )
            
            page_results.append(alignment_result)
            
            # Store aligned image pair
            aligned_pairs.append({
                'page': page_num,
                'original': alignment_result['aligned_images']['original'],
                'reproduction': alignment_result['aligned_images']['reproduction'],
                'rotation_applied': rotation_angle,
                'alignment_quality': alignment_result['alignment_metrics']
            })
        
        # Calculate overall alignment statistics
        overall_stats = self._calculate_overall_alignment_stats(page_results)
        
        # Generate alignment report
        alignment_report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'image_alignment',
            'total_pages': min_pages,
            'alignment_settings': {
                'normalize_sizes': self.normalize_sizes,
                'target_size_method': self.target_size_method,
                'save_aligned_images': self.save_aligned_images,
                'create_comparison_plots': self.create_comparison_plots
            },
            'page_results': page_results,
            'overall_statistics': overall_stats,
            'aligned_image_pairs': len(aligned_pairs)
        }
        
        # Save alignment report
        report_path = self.output_dir / "alignment_report.json"
        
        # Remove numpy arrays before JSON serialization
        report_for_json = alignment_report.copy()
        for page_result in report_for_json['page_results']:
            if 'aligned_images' in page_result:
                del page_result['aligned_images']  # Remove numpy arrays
        
        with open(report_path, 'w') as f:
            json.dump(report_for_json, f, indent=2)
        
        print(f"\nAlignment complete!")
        print(f"Pages aligned: {len(aligned_pairs)}")
        print(f"Average SSIM: {overall_stats['average_ssim']:.4f}")
        print(f"Average correlation: {overall_stats['average_correlation']:.4f}")
        print(f"Report saved: {report_path}")
        
        # Return results with aligned image pairs
        alignment_report['aligned_image_pairs'] = aligned_pairs
        return alignment_report
    
    def _calculate_overall_alignment_stats(self, page_results: List[Dict]) -> Dict[str, float]:
        """Calculate overall alignment statistics."""
        
        if not page_results:
            return {}
        
        ssim_scores = [p['alignment_metrics']['ssim'] for p in page_results]
        correlation_scores = [p['alignment_metrics']['correlation'] for p in page_results]
        mse_scores = [p['alignment_metrics']['mse'] for p in page_results if p['alignment_metrics']['mse'] != float('inf')]
        psnr_scores = [p['alignment_metrics']['psnr'] for p in page_results if p['alignment_metrics']['psnr'] != float('inf')]
        
        stats = {
            'average_ssim': float(np.mean(ssim_scores)) if ssim_scores else 0.0,
            'std_ssim': float(np.std(ssim_scores)) if ssim_scores else 0.0,
            'average_correlation': float(np.mean(correlation_scores)) if correlation_scores else 0.0,
            'std_correlation': float(np.std(correlation_scores)) if correlation_scores else 0.0,
            'average_mse': float(np.mean(mse_scores)) if mse_scores else 0.0,
            'average_psnr': float(np.mean(psnr_scores)) if psnr_scores else 0.0,
            'pages_processed': len(page_results)
        }
        
        return stats


def main():
    """Main function for testing image alignment."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Align document images using orientation detection')
    parser.add_argument('--original', required=True, help='Path to original PDF')
    parser.add_argument('--reproduction', required=True, help='Path to reproduction PDF')
    parser.add_argument('--output', default='alignment_test', help='Output directory')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF conversion')
    parser.add_argument('--size-method', default='original', 
                       choices=['original', 'reproduction', 'largest'],
                       help='Size normalization method')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original):
        print(f"Error: Original file not found: {args.original}")
        sys.exit(1)
    
    if not os.path.exists(args.reproduction):
        print(f"Error: Reproduction file not found: {args.reproduction}")
        sys.exit(1)
    
    try:
        output_dir = Path(args.output)
        
        # Step 1: Convert PDFs to images
        print("Step 1: Converting PDFs to images...")
        converter = PDFConverter(dpi=args.dpi, output_dir=str(output_dir / "conversion"))
        orig_images, repro_images, conversion_info = converter.convert_document_pair(
            args.original, args.reproduction
        )
        
        if not orig_images or not repro_images:
            print("Error: Failed to convert PDFs to images")
            sys.exit(1)
        
        # Step 2: Detect orientation
        print("Step 2: Detecting orientation...")
        detector = OrientationDetector(output_dir=str(output_dir / "orientation"))
        orientation_results = detector.analyze_document_orientation(orig_images, repro_images)
        
        # Step 3: Align images
        print("Step 3: Aligning images...")
        aligner = ImageAligner(output_dir=str(output_dir / "aligned"))
        aligner.target_size_method = args.size_method
        alignment_results = aligner.align_document_pair(orig_images, repro_images, orientation_results)
        
        # Print summary
        print(f"\n{'='*70}")
        print("ALIGNMENT SUMMARY")
        print(f"{'='*70}")
        print(f"Pages processed: {alignment_results['total_pages']}")
        print(f"Average SSIM after alignment: {alignment_results['overall_statistics']['average_ssim']:.4f}")
        print(f"Average correlation after alignment: {alignment_results['overall_statistics']['average_correlation']:.4f}")
        print(f"Size normalization method: {args.size_method}")
        print(f"Results saved to: {args.output}")
        
        # The aligned image pairs are now available in:
        # alignment_results['aligned_image_pairs']
        print(f"\nAligned image pairs ready for further AOI analysis!")
        
    except Exception as e:
        print(f"Error during alignment: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
