#!/usr/bin/env python3
"""
Integration Module for Automated Optical Inspection (AOI) Orientation Detection

This module provides integration utilities to incorporate the AOI orientation
detection system into existing document comparison workflows.
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import logging

from orientation_detector import OrientationDetector, OrientationConfig
from orientation_visualizer import OrientationVisualizer

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedDocumentComparator:
    """
    Enhanced version of DocumentComparator with AOI orientation detection.
    
    This class extends the existing document comparison functionality with
    advanced orientation detection capabilities.
    """
    
    def __init__(self, dpi: int = 300, output_dir: str = "results",
                 orientation_config: Optional[OrientationConfig] = None,
                 enable_orientation_visualization: bool = True):
        """
        Initialize enhanced document comparator.
        
        Args:
            dpi: DPI for PDF conversion
            output_dir: Output directory for results
            orientation_config: Configuration for orientation detection
            enable_orientation_visualization: Whether to create orientation visualizations
        """
        # Initialize base comparator functionality
        self.dpi = dpi
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Automated Optical Inspection (AOI) orientation detection
        self.orientation_detector = OrientationDetector(orientation_config)
        self.orientation_visualizer = OrientationVisualizer(
            output_dir=str(self.output_dir / "orientation_analysis")
        ) if enable_orientation_visualization else None
        
        # Quality thresholds
        self.ssim_threshold = 0.7
        self.text_sim_threshold = 0.8
        
        # Weights for final score calculation
        self.weights = {
            'ssim': 0.5,
            'text_similarity': 0.3,
            'layout_similarity': 0.2
        }
        
        logger.info(f"Enhanced DocumentComparator initialized with Automated Optical Inspection (AOI) orientation detection")
    
    def align_images_with_aoi(self, orig_img: np.ndarray, film_img: np.ndarray, 
                             page_num: int = 1) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Align images using Automated Optical Inspection (AOI) orientation detection.
        
        Args:
            orig_img: Original document image
            film_img: Film/reproduction image
            page_num: Page number for visualization
            
        Returns:
            Tuple of (aligned_original, aligned_film, alignment_info)
        """
        logger.info(f"Aligning images for page {page_num} using Automated Optical Inspection (AOI) orientation detection...")
        
        # Detect orientation using AOI system
        orientation_result = self.orientation_detector.detect_orientation(orig_img, film_img)
        
        # Apply detected orientation to film image
        aligned_film = self.orientation_detector.apply_detected_orientation(film_img, orientation_result)
        
        # Ensure images have the same dimensions
        if aligned_film.shape != orig_img.shape:
            aligned_film = cv2.resize(aligned_film, (orig_img.shape[1], orig_img.shape[0]))
        
        # Create visualization if enabled
        if self.orientation_visualizer:
            try:
                comparison_path = self.orientation_visualizer.create_orientation_comparison(
                    orig_img, film_img, orientation_result, page_num
                )
                orientation_result['visualization_path'] = comparison_path
            except Exception as e:
                logger.warning(f"Failed to create orientation visualization: {e}")
        
        # Prepare alignment info for compatibility with existing system
        alignment_info = {
            'method': 'aoi_orientation_detection',
            'final_rotation': orientation_result['final_rotation'],
            'confidence': orientation_result['final_confidence'],
            'quality': orientation_result['quality'],
            'coarse_rotation': orientation_result['coarse_result']['best_rotation'],
            'fine_angle': orientation_result.get('fine_result', {}).get('best_fine_angle', 0.0),
            'aoi_result': orientation_result  # Full AOI result for detailed analysis
        }
        
        logger.info(f"Image alignment complete: {orientation_result['final_rotation']:.1f}° "
                   f"(confidence: {orientation_result['final_confidence']:.3f})")
        
        return orig_img, aligned_film, alignment_info
    
    def compare_page_enhanced(self, orig_img: np.ndarray, film_img: np.ndarray, 
                            page_num: int) -> Dict[str, Any]:
        """
        Enhanced page comparison with Automated Optical Inspection (AOI) orientation detection.
        
        Args:
            orig_img: Original document image
            film_img: Film/reproduction image
            page_num: Page number
            
        Returns:
            Dictionary with enhanced comparison metrics
        """
        logger.info(f"Enhanced comparison for page {page_num}...")
        
        # Step 1: Align images using Automated Optical Inspection (AOI) orientation detection
        aligned_orig, aligned_film, alignment_info = self.align_images_with_aoi(
            orig_img, film_img, page_num
        )
        
        # Step 2: Calculate comparison metrics on aligned images
        from skimage.metrics import structural_similarity as ssim
        
        # SSIM calculation
        ssim_score, diff_map = ssim(aligned_orig, aligned_film, full=True)
        diff_map = (diff_map * 255).astype(np.uint8)
        
        # Text similarity (placeholder - would use OCR in full implementation)
        text_similarity = 0.9  # Placeholder value
        
        # Layout similarity using edge correlation
        orig_edges = cv2.Canny(aligned_orig, 50, 150)
        film_edges = cv2.Canny(aligned_film, 50, 150)
        layout_similarity, _ = ssim(orig_edges, film_edges, full=True)
        
        # Calculate weighted quality score
        quality_score = (
            self.weights['ssim'] * ssim_score +
            self.weights['text_similarity'] * text_similarity +
            self.weights['layout_similarity'] * layout_similarity
        )
        
        # Enhanced metrics including orientation analysis
        metrics = {
            'page': page_num,
            'ssim': ssim_score,
            'text_similarity': text_similarity,
            'layout_similarity': layout_similarity,
            'quality_score': quality_score,
            'alignment_info': alignment_info,
            'orientation_confidence': alignment_info['confidence'],
            'orientation_quality': alignment_info['quality'],
            'rotation_applied': alignment_info['final_rotation'],
            'method': 'enhanced_with_aoi'
        }
        
        return metrics


def integrate_with_existing_comparator(comparator_class):
    """
    Decorator to integrate Automated Optical Inspection (AOI) orientation detection with existing DocumentComparator.
    
    Args:
        comparator_class: Existing DocumentComparator class
        
    Returns:
        Enhanced comparator class with AOI integration
    """
    
    class AOIIntegratedComparator(comparator_class):
        """DocumentComparator enhanced with Automated Optical Inspection (AOI) orientation detection."""
        
        def __init__(self, *args, orientation_config: Optional[OrientationConfig] = None, 
                     enable_aoi_visualization: bool = True, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Add Automated Optical Inspection (AOI) orientation detection
            self.aoi_detector = OrientationDetector(orientation_config)
            self.aoi_visualizer = OrientationVisualizer(
                output_dir=str(self.output_dir / "aoi_orientation")
            ) if enable_aoi_visualization else None
            
            logger.info("Integrated Automated Optical Inspection (AOI) orientation detection with existing DocumentComparator")
        
        def align_images(self, orig_img: np.ndarray, film_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
            """Override align_images to use Automated Optical Inspection (AOI) orientation detection."""
            
            # Use Automated Optical Inspection (AOI) orientation detection instead of basic rotation detection
            orientation_result = self.aoi_detector.detect_orientation(orig_img, film_img)
            aligned_film = self.aoi_detector.apply_detected_orientation(film_img, orientation_result)
            
            # Ensure same dimensions
            if aligned_film.shape != orig_img.shape:
                aligned_film = cv2.resize(aligned_film, (orig_img.shape[1], orig_img.shape[0]))
            
            # Convert AOI result to format expected by existing system
            alignment_info = {
                'coarse_rotation': orientation_result['coarse_result']['best_rotation'],
                'fine_angle': orientation_result.get('fine_result', {}).get('best_fine_angle', 0.0),
                'total_rotation': orientation_result['final_rotation'],
                'method': 'aoi_enhanced',
                'confidence': orientation_result['final_confidence'],
                'quality': orientation_result['quality'],
                'aoi_full_result': orientation_result
            }
            
            return orig_img, aligned_film, alignment_info
    
    return AOIIntegratedComparator


def create_pdf_orientation_processor(pdf_path_original: str, pdf_path_reproduction: str,
                                   output_dir: str = "pdf_orientation_results",
                                   dpi: int = 300) -> Dict[str, Any]:
    """
    Process complete PDFs for orientation detection and correction.
    
    Args:
        pdf_path_original: Path to original PDF
        pdf_path_reproduction: Path to reproduction PDF
        output_dir: Output directory for results
        dpi: DPI for PDF to image conversion
        
    Returns:
        Dictionary with processing results
    """
    from pdf2image import convert_from_path
    
    logger.info(f"Processing PDFs for orientation detection...")
    logger.info(f"Original: {pdf_path_original}")
    logger.info(f"Reproduction: {pdf_path_reproduction}")
    
    # Convert PDFs to images
    original_images = convert_from_path(pdf_path_original, dpi=dpi)
    reproduction_images = convert_from_path(pdf_path_reproduction, dpi=dpi)
    
    if len(original_images) != len(reproduction_images):
        logger.warning(f"Page count mismatch: Original={len(original_images)}, "
                      f"Reproduction={len(reproduction_images)}")
    
    # Initialize detector and visualizer
    detector = OrientationDetector()
    visualizer = OrientationVisualizer(output_dir=output_dir)
    
    # Process each page
    results = []
    page_numbers = []
    original_arrays = []
    reproduction_arrays = []
    
    min_pages = min(len(original_images), len(reproduction_images))
    
    for i in range(min_pages):
        page_num = i + 1
        logger.info(f"Processing page {page_num}...")
        
        # Convert PIL images to numpy arrays
        orig_array = np.array(original_images[i].convert('L'))
        repro_array = np.array(reproduction_images[i].convert('L'))
        
        # Detect orientation
        result = detector.detect_orientation(orig_array, repro_array)
        
        results.append(result)
        page_numbers.append(page_num)
        original_arrays.append(orig_array)
        reproduction_arrays.append(repro_array)
        
        logger.info(f"Page {page_num}: {result['final_rotation']:.1f}° "
                   f"(confidence: {result['final_confidence']:.3f})")
    
    # Create comprehensive visualizations
    if len(results) > 0:
        from .orientation_visualizer import create_batch_visualization
        
        document_name = Path(pdf_path_original).stem
        created_files = create_batch_visualization(
            original_arrays,
            reproduction_arrays,
            results,
            page_numbers,
            document_name=document_name,
            output_dir=output_dir
        )
    else:
        created_files = {}
    
    # Compile summary results
    processing_summary = {
        'original_pdf': pdf_path_original,
        'reproduction_pdf': pdf_path_reproduction,
        'pages_processed': len(results),
        'output_directory': output_dir,
        'created_files': created_files,
        'page_results': results,
        'processing_statistics': calculate_processing_statistics(results)
    }
    
    logger.info(f"PDF orientation processing complete. Processed {len(results)} pages.")
    
    return processing_summary


def calculate_processing_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from orientation detection results."""
    
    if not results:
        return {}
    
    rotations = [r['final_rotation'] for r in results]
    confidences = [r['final_confidence'] for r in results]
    qualities = [r['quality'] for r in results]
    
    # Count quality levels
    quality_counts = {'high': 0, 'medium': 0, 'low': 0}
    for quality in qualities:
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    # Count rotation patterns
    rotation_counts = {}
    for rotation in rotations:
        # Round to nearest 45 degrees for pattern analysis
        rounded = round(rotation / 45) * 45
        rotation_counts[rounded] = rotation_counts.get(rounded, 0) + 1
    
    statistics = {
        'total_pages': len(results),
        'average_confidence': np.mean(confidences),
        'confidence_std': np.std(confidences),
        'min_confidence': min(confidences),
        'max_confidence': max(confidences),
        'quality_distribution': quality_counts,
        'rotation_patterns': rotation_counts,
        'most_common_rotation': max(rotation_counts, key=rotation_counts.get) if rotation_counts else 0,
        'high_confidence_pages': sum(1 for c in confidences if c >= 0.7),
        'low_confidence_pages': sum(1 for c in confidences if c < 0.3)
    }
    
    return statistics


# Example usage functions for common integration scenarios

def quick_orientation_check(original_img: np.ndarray, reproduction_img: np.ndarray) -> Dict[str, Any]:
    """
    Quick orientation check for single page comparison.
    
    Args:
        original_img: Original document image (grayscale numpy array)
        reproduction_img: Reproduction image (grayscale numpy array)
        
    Returns:
        Simple orientation result dictionary
    """
    detector = OrientationDetector()
    result = detector.detect_orientation(original_img, reproduction_img)
    
    return {
        'rotation_degrees': result['final_rotation'],
        'confidence': result['final_confidence'],
        'quality': result['quality'],
        'recommended_action': 'apply_rotation' if result['final_confidence'] > 0.3 else 'manual_review'
    }


def batch_orientation_correction(image_pairs: List[Tuple[np.ndarray, np.ndarray]],
                               output_dir: str = "batch_orientation_results") -> List[np.ndarray]:
    """
    Apply orientation correction to a batch of image pairs.
    
    Args:
        image_pairs: List of (original, reproduction) image pairs
        output_dir: Output directory for results
        
    Returns:
        List of corrected reproduction images
    """
    detector = OrientationDetector()
    corrected_images = []
    
    for i, (original, reproduction) in enumerate(image_pairs):
        logger.info(f"Processing image pair {i+1}/{len(image_pairs)}")
        
        # Detect orientation
        result = detector.detect_orientation(original, reproduction)
        
        # Apply correction
        corrected = detector.apply_detected_orientation(reproduction, result)
        corrected_images.append(corrected)
        
        logger.info(f"Applied {result['final_rotation']:.1f}° rotation "
                   f"(confidence: {result['final_confidence']:.3f})")
    
    return corrected_images
