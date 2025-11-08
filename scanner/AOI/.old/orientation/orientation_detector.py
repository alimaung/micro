#!/usr/bin/env python3
"""
Orientation Detection Module

Detects and corrects orientation differences between original and reproduction images.
Works at the image level for maximum flexibility and accuracy.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template
import json
from datetime import datetime
from pdf_converter import PDFConverter


class OrientationDetector:
    """
    Detects orientation differences between original and reproduction images.
    """
    
    def __init__(self, output_dir: str = "orientation_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Detection parameters
        self.test_rotations = [0, 90, 180, 270]  # Coarse rotations to test
        self.fine_angle_range = 10  # ±10 degrees for fine adjustment
        self.fine_angle_step = 0.5  # 0.5 degree increments
        
        # Image processing parameters
        self.edge_detection_threshold = (50, 150)  # Canny edge detection thresholds
        self.resize_for_speed = True  # Resize images for faster processing
        self.max_dimension = 800  # Maximum dimension for speed optimization
        
        # Scoring parameters
        self.ssim_weight = 0.7
        self.correlation_weight = 0.3
    
    def preprocess_for_orientation(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for orientation detection.
        
        Args:
            img: Input grayscale image
            
        Returns:
            Preprocessed image optimized for orientation detection
        """
        # Resize for speed if needed
        if self.resize_for_speed:
            h, w = img.shape
            if max(h, w) > self.max_dimension:
                scale = self.max_dimension / max(h, w)
                new_h, new_w = int(h * scale), int(w * scale)
                img = cv2.resize(img, (new_w, new_h))
        
        # Apply edge detection for better orientation matching
        edges = cv2.Canny(img, self.edge_detection_threshold[0], self.edge_detection_threshold[1])
        
        # Optional: Apply morphological operations to strengthen edges
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        return edges
    
    def rotate_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle.
        
        Args:
            img: Input image
            angle: Rotation angle in degrees (positive = counterclockwise)
            
        Returns:
            Rotated image
        """
        if angle == 0:
            return img.copy()
        elif angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        else:
            # Fine rotation using affine transformation
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Calculate new dimensions to avoid cropping
            cos_angle = abs(rotation_matrix[0, 0])
            sin_angle = abs(rotation_matrix[0, 1])
            new_w = int((h * sin_angle) + (w * cos_angle))
            new_h = int((h * cos_angle) + (w * sin_angle))
            
            # Adjust rotation matrix for new dimensions
            rotation_matrix[0, 2] += (new_w / 2) - center[0]
            rotation_matrix[1, 2] += (new_h / 2) - center[1]
            
            return cv2.warpAffine(img, rotation_matrix, (new_w, new_h))
    
    def calculate_orientation_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate orientation matching score between two images.
        
        Args:
            img1: Reference image (original)
            img2: Test image (rotated reproduction)
            
        Returns:
            Orientation score (higher = better match)
        """
        # Ensure images are same size
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Calculate SSIM score
        try:
            ssim_score, _ = ssim(img1, img2, full=True)
        except Exception:
            ssim_score = 0.0
        
        # Calculate normalized cross-correlation
        try:
            # Normalize images
            img1_norm = cv2.normalize(img1.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            img2_norm = cv2.normalize(img2.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            
            # Calculate correlation coefficient
            correlation = cv2.matchTemplate(img1_norm, img2_norm, cv2.TM_CCOEFF_NORMED)[0, 0]
        except Exception:
            correlation = 0.0
        
        # Weighted combination
        combined_score = (self.ssim_weight * ssim_score + 
                         self.correlation_weight * correlation)
        
        return combined_score
    
    def detect_coarse_orientation(self, original_img: np.ndarray, reproduction_img: np.ndarray) -> Dict[str, Any]:
        """
        Detect coarse orientation (0, 90, 180, 270 degrees).
        
        Args:
            original_img: Original image
            reproduction_img: Reproduction image
            
        Returns:
            Dictionary with coarse orientation results
        """
        print("Detecting coarse orientation (0°, 90°, 180°, 270°)...")
        
        # Preprocess images for orientation detection
        orig_processed = self.preprocess_for_orientation(original_img)
        repro_processed = self.preprocess_for_orientation(reproduction_img)
        
        best_score = -1
        best_rotation = 0
        rotation_scores = {}
        
        for rotation in self.test_rotations:
            # Rotate reproduction image
            rotated_repro = self.rotate_image(repro_processed, rotation)
            
            # Calculate orientation score
            score = self.calculate_orientation_score(orig_processed, rotated_repro)
            rotation_scores[rotation] = score
            
            print(f"  Rotation {rotation:3d}°: Score = {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_rotation = rotation
        
        result = {
            'best_rotation': best_rotation,
            'best_score': best_score,
            'all_scores': rotation_scores,
            'confidence': best_score
        }
        
        print(f"  → Best coarse rotation: {best_rotation}° (score: {best_score:.4f})")
        return result
    
    def detect_fine_orientation(self, original_img: np.ndarray, reproduction_img: np.ndarray, 
                              coarse_rotation: int) -> Dict[str, Any]:
        """
        Detect fine orientation adjustment after coarse rotation.
        
        Args:
            original_img: Original image
            reproduction_img: Reproduction image
            coarse_rotation: Coarse rotation angle to apply first
            
        Returns:
            Dictionary with fine orientation results
        """
        print(f"Detecting fine orientation around {coarse_rotation}° (±{self.fine_angle_range}°)...")
        
        # Apply coarse rotation first
        coarse_rotated = self.rotate_image(reproduction_img, coarse_rotation)
        
        # Preprocess images
        orig_processed = self.preprocess_for_orientation(original_img)
        repro_processed = self.preprocess_for_orientation(coarse_rotated)
        
        # Test fine angles
        fine_angles = np.arange(-self.fine_angle_range, self.fine_angle_range + self.fine_angle_step, 
                               self.fine_angle_step)
        
        best_score = -1
        best_fine_angle = 0
        angle_scores = {}
        
        for fine_angle in fine_angles:
            # Apply fine rotation
            fine_rotated = self.rotate_image(repro_processed, fine_angle)
            
            # Calculate orientation score
            score = self.calculate_orientation_score(orig_processed, fine_rotated)
            angle_scores[fine_angle] = score
            
            if score > best_score:
                best_score = score
                best_fine_angle = fine_angle
        
        result = {
            'best_fine_angle': best_fine_angle,
            'best_score': best_score,
            'all_scores': angle_scores,
            'total_rotation': coarse_rotation + best_fine_angle,
            'confidence': best_score
        }
        
        print(f"  → Best fine adjustment: {best_fine_angle:.1f}° (score: {best_score:.4f})")
        print(f"  → Total rotation: {result['total_rotation']:.1f}°")
        return result
    
    def apply_orientation_correction(self, img: np.ndarray, total_rotation: float) -> np.ndarray:
        """
        Apply the detected orientation correction to an image.
        
        Args:
            img: Input image
            total_rotation: Total rotation angle to apply
            
        Returns:
            Corrected image
        """
        return self.rotate_image(img, total_rotation)
    
    def detect_orientation(self, original_img: np.ndarray, reproduction_img: np.ndarray) -> Dict[str, Any]:
        """
        Complete orientation detection pipeline.
        
        Args:
            original_img: Original image
            reproduction_img: Reproduction image
            
        Returns:
            Complete orientation detection results
        """
        print(f"\n{'='*60}")
        print("ORIENTATION DETECTION")
        print(f"{'='*60}")
        
        # Step 1: Detect coarse orientation
        coarse_result = self.detect_coarse_orientation(original_img, reproduction_img)
        
        # Step 2: Detect fine orientation
        fine_result = self.detect_fine_orientation(original_img, reproduction_img, 
                                                  coarse_result['best_rotation'])
        
        # Combine results
        orientation_result = {
            'timestamp': datetime.now().isoformat(),
            'coarse_detection': coarse_result,
            'fine_detection': fine_result,
            'final_rotation': fine_result['total_rotation'],
            'final_confidence': fine_result['confidence'],
            'detection_quality': self._assess_detection_quality(coarse_result, fine_result)
        }
        
        return orientation_result
    
    def _assess_detection_quality(self, coarse_result: Dict, fine_result: Dict) -> Dict[str, Any]:
        """Assess the quality of orientation detection."""
        
        coarse_confidence = coarse_result['confidence']
        fine_confidence = fine_result['confidence']
        
        # Check if there's a clear winner in coarse detection
        scores = list(coarse_result['all_scores'].values())
        scores.sort(reverse=True)
        coarse_clarity = scores[0] - scores[1] if len(scores) > 1 else scores[0]
        
        quality_assessment = {
            'coarse_confidence': coarse_confidence,
            'fine_confidence': fine_confidence,
            'coarse_clarity': coarse_clarity,
            'overall_confidence': (coarse_confidence + fine_confidence) / 2
        }
        
        # Determine quality level
        if quality_assessment['overall_confidence'] > 0.8:
            quality_assessment['quality_level'] = 'HIGH'
        elif quality_assessment['overall_confidence'] > 0.6:
            quality_assessment['quality_level'] = 'MEDIUM'
        else:
            quality_assessment['quality_level'] = 'LOW'
        
        # Add warnings
        warnings = []
        if coarse_clarity < 0.1:
            warnings.append("Low clarity in coarse detection - multiple orientations have similar scores")
        if fine_confidence < 0.5:
            warnings.append("Low confidence in fine adjustment")
        if abs(fine_result['best_fine_angle']) > 5:
            warnings.append(f"Large fine adjustment needed ({fine_result['best_fine_angle']:.1f}°)")
        
        quality_assessment['warnings'] = warnings
        
        return quality_assessment
    
    def create_orientation_visualization(self, original_img: np.ndarray, reproduction_img: np.ndarray,
                                       orientation_result: Dict, page_num: int) -> str:
        """
        Create visualization of orientation detection results.
        
        Args:
            original_img: Original image
            reproduction_img: Reproduction image
            orientation_result: Orientation detection results
            page_num: Page number for naming
            
        Returns:
            Path to saved visualization
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Page {page_num} Orientation Detection Results', fontsize=16, fontweight='bold')
        
        # Original image
        axes[0, 0].imshow(original_img, cmap='gray')
        axes[0, 0].set_title('Original Document')
        axes[0, 0].axis('off')
        
        # Original reproduction (before correction)
        axes[0, 1].imshow(reproduction_img, cmap='gray')
        axes[0, 1].set_title('Reproduction (Original)')
        axes[0, 1].axis('off')
        
        # Corrected reproduction
        corrected_repro = self.apply_orientation_correction(reproduction_img, 
                                                           orientation_result['final_rotation'])
        # Resize to match original for display
        if corrected_repro.shape != original_img.shape:
            corrected_repro = cv2.resize(corrected_repro, (original_img.shape[1], original_img.shape[0]))
        
        axes[0, 2].imshow(corrected_repro, cmap='gray')
        axes[0, 2].set_title(f'Corrected Reproduction\n(Rotated {orientation_result["final_rotation"]:.1f}°)')
        axes[0, 2].axis('off')
        
        # Coarse rotation scores
        coarse_scores = orientation_result['coarse_detection']['all_scores']
        rotations = list(coarse_scores.keys())
        scores = list(coarse_scores.values())
        
        axes[1, 0].bar(rotations, scores, color=['red' if r == orientation_result['coarse_detection']['best_rotation'] 
                                               else 'blue' for r in rotations])
        axes[1, 0].set_title('Coarse Rotation Scores')
        axes[1, 0].set_xlabel('Rotation (degrees)')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Fine angle scores (if available)
        if 'all_scores' in orientation_result['fine_detection']:
            fine_scores = orientation_result['fine_detection']['all_scores']
            fine_angles = list(fine_scores.keys())
            fine_score_values = list(fine_scores.values())
            
            axes[1, 1].plot(fine_angles, fine_score_values, 'b-', linewidth=2)
            best_fine = orientation_result['fine_detection']['best_fine_angle']
            best_score = orientation_result['fine_detection']['best_score']
            axes[1, 1].plot(best_fine, best_score, 'ro', markersize=8, label=f'Best: {best_fine:.1f}°')
            axes[1, 1].set_title('Fine Angle Adjustment')
            axes[1, 1].set_xlabel('Fine Angle (degrees)')
            axes[1, 1].set_ylabel('Score')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].legend()
        
        # Results summary
        axes[1, 2].axis('off')
        
        quality = orientation_result['detection_quality']
        summary_text = f"""
Orientation Detection Results:

Coarse Rotation: {orientation_result['coarse_detection']['best_rotation']}°
Fine Adjustment: {orientation_result['fine_detection']['best_fine_angle']:.1f}°
Total Rotation: {orientation_result['final_rotation']:.1f}°

Detection Quality: {quality['quality_level']}
Overall Confidence: {quality['overall_confidence']:.3f}
Coarse Confidence: {quality['coarse_confidence']:.3f}
Fine Confidence: {quality['fine_confidence']:.3f}

Warnings:
"""
        
        if quality['warnings']:
            for warning in quality['warnings']:
                summary_text += f"• {warning}\n"
        else:
            summary_text += "• No warnings\n"
        
        axes[1, 2].text(0.05, 0.95, summary_text, fontsize=10, verticalalignment='top',
                       fontfamily='monospace', transform=axes[1, 2].transAxes)
        
        # Add colored border based on quality
        color_map = {'HIGH': 'green', 'MEDIUM': 'orange', 'LOW': 'red'}
        color = color_map.get(quality['quality_level'], 'gray')
        rect = patches.Rectangle((0, 0), 1, 1, linewidth=4, edgecolor=color,
                               facecolor='none', transform=axes[1, 2].transAxes)
        axes[1, 2].add_patch(rect)
        
        plt.tight_layout()
        
        # Save visualization
        output_path = self.output_dir / f"page_{page_num:03d}_orientation_detection.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def analyze_document_orientation(self, original_images: List[np.ndarray], 
                                   reproduction_images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Analyze orientation for entire document.
        
        Args:
            original_images: List of original page images
            reproduction_images: List of reproduction page images
            
        Returns:
            Complete document orientation analysis
        """
        print(f"\n{'='*70}")
        print("DOCUMENT ORIENTATION ANALYSIS")
        print(f"{'='*70}")
        
        min_pages = min(len(original_images), len(reproduction_images))
        page_results = []
        
        for i in range(min_pages):
            page_num = i + 1
            print(f"\nAnalyzing page {page_num}...")
            
            # Detect orientation for this page
            orientation_result = self.detect_orientation(original_images[i], reproduction_images[i])
            orientation_result['page'] = page_num
            
            # Create visualization
            viz_path = self.create_orientation_visualization(original_images[i], reproduction_images[i],
                                                           orientation_result, page_num)
            orientation_result['visualization_path'] = viz_path
            
            page_results.append(orientation_result)
        
        # Analyze overall document orientation patterns
        overall_analysis = self._analyze_document_patterns(page_results)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'orientation_detection',
            'total_pages': min_pages,
            'page_results': page_results,
            'overall_analysis': overall_analysis,
            'settings': {
                'test_rotations': self.test_rotations,
                'fine_angle_range': self.fine_angle_range,
                'fine_angle_step': self.fine_angle_step,
                'edge_detection_threshold': self.edge_detection_threshold
            }
        }
        
        # Save report
        report_path = self.output_dir / "orientation_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nOrientation analysis complete! Report saved to: {report_path}")
        return report
    
    def _analyze_document_patterns(self, page_results: List[Dict]) -> Dict[str, Any]:
        """Analyze orientation patterns across the document."""
        
        rotations = [p['final_rotation'] for p in page_results]
        confidences = [p['final_confidence'] for p in page_results]
        
        # Find most common rotation
        from collections import Counter
        coarse_rotations = [p['coarse_detection']['best_rotation'] for p in page_results]
        rotation_counts = Counter(coarse_rotations)
        most_common_rotation = rotation_counts.most_common(1)[0][0]
        
        analysis = {
            'most_common_coarse_rotation': most_common_rotation,
            'rotation_consistency': rotation_counts[most_common_rotation] / len(page_results),
            'average_fine_adjustment': float(np.mean([p['fine_detection']['best_fine_angle'] for p in page_results])),
            'average_confidence': float(np.mean(confidences)),
            'confidence_consistency': float(np.std(confidences)),
            'pages_with_warnings': sum(1 for p in page_results if p['detection_quality']['warnings']),
            'quality_distribution': {
                'HIGH': sum(1 for p in page_results if p['detection_quality']['quality_level'] == 'HIGH'),
                'MEDIUM': sum(1 for p in page_results if p['detection_quality']['quality_level'] == 'MEDIUM'),
                'LOW': sum(1 for p in page_results if p['detection_quality']['quality_level'] == 'LOW')
            }
        }
        
        # Recommendations
        recommendations = []
        if analysis['rotation_consistency'] < 0.8:
            recommendations.append("Inconsistent rotation detected across pages - manual review recommended")
        if analysis['average_confidence'] < 0.6:
            recommendations.append("Low average confidence - consider manual orientation verification")
        if abs(analysis['average_fine_adjustment']) > 3:
            recommendations.append(f"Systematic skew detected ({analysis['average_fine_adjustment']:.1f}°) - check scanning alignment")
        
        analysis['recommendations'] = recommendations
        
        return analysis


def main():
    """Main function for testing orientation detection."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect and correct document orientation')
    parser.add_argument('--original', required=True, help='Path to original PDF')
    parser.add_argument('--reproduction', required=True, help='Path to reproduction PDF')
    parser.add_argument('--output', default='orientation_analysis', help='Output directory')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF conversion')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original):
        print(f"Error: Original file not found: {args.original}")
        sys.exit(1)
    
    if not os.path.exists(args.reproduction):
        print(f"Error: Reproduction file not found: {args.reproduction}")
        sys.exit(1)
    
    try:
        # Convert PDFs to images
        print("Converting PDFs to images...")
        converter = PDFConverter(dpi=args.dpi, output_dir=f"{args.output}/conversion")
        orig_images, repro_images, conversion_info = converter.convert_document_pair(
            args.original, args.reproduction
        )
        
        if not orig_images or not repro_images:
            print("Error: Failed to convert PDFs to images")
            sys.exit(1)
        
        # Detect orientation
        detector = OrientationDetector(output_dir=args.output)
        report = detector.analyze_document_orientation(orig_images, repro_images)
        
        # Print summary
        overall = report['overall_analysis']
        print(f"\n{'='*70}")
        print("ORIENTATION ANALYSIS SUMMARY")
        print(f"{'='*70}")
        print(f"Pages analyzed: {report['total_pages']}")
        print(f"Most common rotation: {overall['most_common_coarse_rotation']}°")
        print(f"Rotation consistency: {overall['rotation_consistency']:.1%}")
        print(f"Average confidence: {overall['average_confidence']:.3f}")
        print(f"Average fine adjustment: {overall['average_fine_adjustment']:.1f}°")
        
        if overall['recommendations']:
            print(f"\nRecommendations:")
            for rec in overall['recommendations']:
                print(f"• {rec}")
        
        print(f"\nResults saved to: {args.output}")
        
    except Exception as e:
        print(f"Error during orientation detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
