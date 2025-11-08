#!/usr/bin/env python3
"""
Automated Optical Inspection (AOI) Orientation Detection Module

This module provides robust orientation detection for comparing original PDFs 
with scanned microfilm reproductions. It handles different orientations between
documents to enable accurate overlapping and comparison.

Key Features:
- Multi-method orientation detection (SIFT, ORB, Edge-based, Template matching)
- Coarse rotation detection (0°, 90°, 180°, 270°)
- Fine angle adjustment (-10° to +10°)
- Confidence scoring and validation
- Visualization of detected orientations
- Configuration management
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
from skimage.feature import match_template
from scipy import ndimage
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OrientationConfig:
    """Configuration for orientation detection parameters."""
    
    # Coarse rotation angles to test
    test_rotations: List[int] = None
    
    # Fine angle adjustment range
    fine_angle_range: Tuple[float, float] = (-10.0, 10.0)
    fine_angle_step: float = 0.5
    
    # Image preprocessing
    resize_for_speed: bool = True
    max_dimension: int = 800
    gaussian_blur_kernel: int = 3
    
    # Edge detection parameters
    canny_low_threshold: int = 50
    canny_high_threshold: int = 150
    
    # Feature detection parameters
    sift_n_features: int = 1000
    orb_n_features: int = 1000
    feature_match_ratio: float = 0.75
    
    # Scoring weights
    weights: Dict[str, float] = None
    
    # Confidence thresholds
    min_confidence: float = 0.3
    high_confidence: float = 0.7
    
    def __post_init__(self):
        if self.test_rotations is None:
            self.test_rotations = [0, 90, 180, 270]
        
        if self.weights is None:
            self.weights = {
                'ssim': 0.4,
                'feature_matching': 0.3,
                'edge_correlation': 0.2,
                'template_matching': 0.1
            }


class OrientationDetector:
    """
    Advanced orientation detection for document comparison.
    
    This class provides multiple methods for detecting the orientation
    difference between an original document and its microfilm reproduction.
    """
    
    def __init__(self, config: Optional[OrientationConfig] = None):
        """
        Initialize the orientation detector.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or OrientationConfig()
        
        # Initialize feature detectors
        try:
            self.sift = cv2.SIFT_create(nfeatures=self.config.sift_n_features)
        except AttributeError:
            # Fallback for older OpenCV versions
            self.sift = cv2.xfeatures2d.SIFT_create(nfeatures=self.config.sift_n_features)
        
        self.orb = cv2.ORB_create(nfeatures=self.config.orb_n_features)
        
        # Initialize matcher for feature matching
        self.matcher = cv2.BFMatcher()
        
        logger.info(f"OrientationDetector initialized with config: {self.config}")
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for orientation detection.
        
        Args:
            img: Input grayscale image
            
        Returns:
            Preprocessed image
        """
        processed = img.copy()
        
        # Resize for speed if needed
        if self.config.resize_for_speed:
            height, width = processed.shape
            max_dim = max(height, width)
            
            if max_dim > self.config.max_dimension:
                scale_factor = self.config.max_dimension / max_dim
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                processed = cv2.resize(processed, (new_width, new_height))
        
        # Apply Gaussian blur to reduce noise
        if self.config.gaussian_blur_kernel > 0:
            processed = cv2.GaussianBlur(
                processed, 
                (self.config.gaussian_blur_kernel, self.config.gaussian_blur_kernel), 
                0
            )
        
        # Normalize histogram
        processed = cv2.equalizeHist(processed)
        
        return processed
    
    def rotate_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by given angle.
        
        Args:
            img: Input image
            angle: Rotation angle in degrees (positive = counterclockwise)
            
        Returns:
            Rotated image
        """
        if angle == 0:
            return img.copy()
        
        # Handle 90-degree rotations efficiently
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270 or angle == -90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        
        # General rotation for fine angles
        height, width = img.shape
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height))
        
        return rotated
    
    def calculate_ssim_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate SSIM score between two images.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            SSIM score (0-1, higher is better)
        """
        try:
            # Ensure images have the same dimensions
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            score, _ = ssim(img1, img2, full=True)
            return max(0.0, score)  # Ensure non-negative
        except Exception as e:
            logger.warning(f"SSIM calculation failed: {e}")
            return 0.0
    
    def calculate_feature_matching_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate feature matching score using SIFT and ORB.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Feature matching score (0-1, higher is better)
        """
        try:
            # Ensure images have the same dimensions
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # SIFT feature matching
            sift_score = self._calculate_sift_score(img1, img2)
            
            # ORB feature matching
            orb_score = self._calculate_orb_score(img1, img2)
            
            # Combine scores
            combined_score = (sift_score + orb_score) / 2.0
            return combined_score
            
        except Exception as e:
            logger.warning(f"Feature matching failed: {e}")
            return 0.0
    
    def _calculate_sift_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate SIFT-based matching score."""
        try:
            # Detect keypoints and descriptors
            kp1, desc1 = self.sift.detectAndCompute(img1, None)
            kp2, desc2 = self.sift.detectAndCompute(img2, None)
            
            if desc1 is None or desc2 is None or len(desc1) < 10 or len(desc2) < 10:
                return 0.0
            
            # Match features
            matches = self.matcher.knnMatch(desc1, desc2, k=2)
            
            # Apply ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < self.config.feature_match_ratio * n.distance:
                        good_matches.append(m)
            
            # Calculate score based on number of good matches
            if len(kp1) > 0 and len(kp2) > 0:
                score = len(good_matches) / min(len(kp1), len(kp2))
                return min(1.0, score)  # Cap at 1.0
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"SIFT matching failed: {e}")
            return 0.0
    
    def _calculate_orb_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate ORB-based matching score."""
        try:
            # Detect keypoints and descriptors
            kp1, desc1 = self.orb.detectAndCompute(img1, None)
            kp2, desc2 = self.orb.detectAndCompute(img2, None)
            
            if desc1 is None or desc2 is None or len(desc1) < 10 or len(desc2) < 10:
                return 0.0
            
            # Match features using Hamming distance
            matches = self.matcher.match(desc1, desc2)
            
            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Take top matches and calculate score
            num_good_matches = len([m for m in matches if m.distance < 50])  # Hamming distance threshold
            
            if len(kp1) > 0 and len(kp2) > 0:
                score = num_good_matches / min(len(kp1), len(kp2))
                return min(1.0, score)  # Cap at 1.0
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"ORB matching failed: {e}")
            return 0.0
    
    def calculate_edge_correlation_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate edge correlation score.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Edge correlation score (0-1, higher is better)
        """
        try:
            # Ensure images have the same dimensions
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Apply edge detection
            edges1 = cv2.Canny(
                img1, 
                self.config.canny_low_threshold, 
                self.config.canny_high_threshold
            )
            edges2 = cv2.Canny(
                img2, 
                self.config.canny_low_threshold, 
                self.config.canny_high_threshold
            )
            
            # Calculate correlation coefficient
            correlation = cv2.matchTemplate(edges1, edges2, cv2.TM_CCOEFF_NORMED)[0, 0]
            
            # Normalize to 0-1 range
            score = (correlation + 1.0) / 2.0
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Edge correlation calculation failed: {e}")
            return 0.0
    
    def calculate_template_matching_score(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate template matching score using multiple methods.
        
        Args:
            img1: First image (template)
            img2: Second image (target)
            
        Returns:
            Template matching score (0-1, higher is better)
        """
        try:
            # Ensure images have the same dimensions
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Try different template matching methods
            methods = [
                cv2.TM_CCOEFF_NORMED,
                cv2.TM_CCORR_NORMED,
                cv2.TM_SQDIFF_NORMED
            ]
            
            scores = []
            for method in methods:
                result = cv2.matchTemplate(img1, img2, method)
                
                if method == cv2.TM_SQDIFF_NORMED:
                    # For SQDIFF, lower is better, so invert
                    score = 1.0 - result[0, 0]
                else:
                    score = result[0, 0]
                
                scores.append(max(0.0, min(1.0, score)))
            
            # Return average of all methods
            return np.mean(scores)
            
        except Exception as e:
            logger.warning(f"Template matching failed: {e}")
            return 0.0
    
    def calculate_combined_score(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, float]:
        """
        Calculate combined orientation score using all methods.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Dictionary with individual scores and combined score
        """
        scores = {}
        
        # Calculate individual scores
        scores['ssim'] = self.calculate_ssim_score(img1, img2)
        scores['feature_matching'] = self.calculate_feature_matching_score(img1, img2)
        scores['edge_correlation'] = self.calculate_edge_correlation_score(img1, img2)
        scores['template_matching'] = self.calculate_template_matching_score(img1, img2)
        
        # Calculate weighted combined score
        combined_score = 0.0
        for method, score in scores.items():
            weight = self.config.weights.get(method, 0.0)
            combined_score += weight * score
        
        scores['combined'] = combined_score
        
        return scores
    
    def detect_coarse_orientation(self, original_img: np.ndarray, 
                                reproduction_img: np.ndarray) -> Dict[str, Any]:
        """
        Detect coarse orientation (0°, 90°, 180°, 270°).
        
        Args:
            original_img: Original document image
            reproduction_img: Reproduction/scan image
            
        Returns:
            Dictionary with coarse orientation results
        """
        logger.info("Detecting coarse orientation...")
        
        # Preprocess images
        orig_processed = self.preprocess_image(original_img)
        repro_processed = self.preprocess_image(reproduction_img)
        
        best_score = -1.0
        best_rotation = 0
        rotation_results = {}
        
        for rotation in self.config.test_rotations:
            logger.info(f"Testing rotation: {rotation}°")
            
            # Rotate reproduction image
            rotated_repro = self.rotate_image(repro_processed, rotation)
            
            # Calculate combined score
            scores = self.calculate_combined_score(orig_processed, rotated_repro)
            combined_score = scores['combined']
            
            rotation_results[rotation] = {
                'combined_score': combined_score,
                'individual_scores': scores
            }
            
            logger.info(f"  Rotation {rotation:3d}°: Combined score = {combined_score:.4f}")
            
            if combined_score > best_score:
                best_score = combined_score
                best_rotation = rotation
        
        # Calculate confidence
        scores_list = [result['combined_score'] for result in rotation_results.values()]
        scores_array = np.array(scores_list)
        
        # Confidence based on score separation
        if len(scores_array) > 1:
            sorted_scores = np.sort(scores_array)[::-1]  # Descending order
            confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0] if sorted_scores[0] > 0 else 0.0
        else:
            confidence = best_score
        
        result = {
            'best_rotation': best_rotation,
            'best_score': best_score,
            'confidence': confidence,
            'all_results': rotation_results,
            'method': 'coarse_detection'
        }
        
        logger.info(f"Best coarse rotation: {best_rotation}° (score: {best_score:.4f}, confidence: {confidence:.4f})")
        
        return result
    
    def detect_fine_orientation(self, original_img: np.ndarray, 
                              reproduction_img: np.ndarray, 
                              coarse_rotation: int) -> Dict[str, Any]:
        """
        Detect fine orientation adjustment after coarse rotation.
        
        Args:
            original_img: Original document image
            reproduction_img: Reproduction/scan image
            coarse_rotation: Coarse rotation angle from previous step
            
        Returns:
            Dictionary with fine orientation results
        """
        logger.info(f"Detecting fine orientation after {coarse_rotation}° coarse rotation...")
        
        # Preprocess images
        orig_processed = self.preprocess_image(original_img)
        repro_processed = self.preprocess_image(reproduction_img)
        
        # Apply coarse rotation first
        coarse_rotated = self.rotate_image(repro_processed, coarse_rotation)
        
        # Test fine angles
        min_angle, max_angle = self.config.fine_angle_range
        angles = np.arange(min_angle, max_angle + self.config.fine_angle_step, 
                          self.config.fine_angle_step)
        
        best_score = -1.0
        best_angle = 0.0
        angle_results = {}
        
        for angle in angles:
            # Apply fine rotation
            fine_rotated = self.rotate_image(coarse_rotated, angle)
            
            # Calculate combined score (use faster methods for fine tuning)
            scores = {
                'ssim': self.calculate_ssim_score(orig_processed, fine_rotated),
                'edge_correlation': self.calculate_edge_correlation_score(orig_processed, fine_rotated)
            }
            
            # Weighted score for fine tuning (focus on SSIM and edge correlation)
            combined_score = 0.7 * scores['ssim'] + 0.3 * scores['edge_correlation']
            
            angle_results[angle] = {
                'combined_score': combined_score,
                'individual_scores': scores
            }
            
            if combined_score > best_score:
                best_score = combined_score
                best_angle = angle
        
        # Calculate confidence
        scores_list = [result['combined_score'] for result in angle_results.values()]
        scores_array = np.array(scores_list)
        
        if len(scores_array) > 1:
            sorted_scores = np.sort(scores_array)[::-1]
            confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0] if sorted_scores[0] > 0 else 0.0
        else:
            confidence = best_score
        
        result = {
            'best_fine_angle': best_angle,
            'best_score': best_score,
            'confidence': confidence,
            'total_rotation': coarse_rotation + best_angle,
            'all_results': angle_results,
            'method': 'fine_detection'
        }
        
        logger.info(f"Best fine angle: {best_angle:.1f}° (total: {coarse_rotation + best_angle:.1f}°, "
                   f"score: {best_score:.4f}, confidence: {confidence:.4f})")
        
        return result
    
    def detect_orientation(self, original_img: np.ndarray, 
                         reproduction_img: np.ndarray) -> Dict[str, Any]:
        """
        Complete orientation detection pipeline.
        
        Args:
            original_img: Original document image
            reproduction_img: Reproduction/scan image
            
        Returns:
            Dictionary with complete orientation detection results
        """
        logger.info("Starting complete orientation detection...")
        
        # Step 1: Coarse orientation detection
        coarse_result = self.detect_coarse_orientation(original_img, reproduction_img)
        
        # Step 2: Fine orientation detection (only if coarse detection is confident enough)
        fine_result = None
        if coarse_result['confidence'] >= self.config.min_confidence:
            fine_result = self.detect_fine_orientation(
                original_img, 
                reproduction_img, 
                coarse_result['best_rotation']
            )
        else:
            logger.warning(f"Coarse detection confidence too low ({coarse_result['confidence']:.3f}), "
                          f"skipping fine detection")
        
        # Combine results
        if fine_result:
            final_rotation = fine_result['total_rotation']
            final_confidence = min(coarse_result['confidence'], fine_result['confidence'])
        else:
            final_rotation = coarse_result['best_rotation']
            final_confidence = coarse_result['confidence']
        
        # Determine quality level
        if final_confidence >= self.config.high_confidence:
            quality = 'high'
        elif final_confidence >= self.config.min_confidence:
            quality = 'medium'
        else:
            quality = 'low'
        
        complete_result = {
            'final_rotation': final_rotation,
            'final_confidence': final_confidence,
            'quality': quality,
            'coarse_result': coarse_result,
            'fine_result': fine_result,
            'timestamp': datetime.now().isoformat(),
            'config': asdict(self.config)
        }
        
        logger.info(f"Orientation detection complete: {final_rotation:.1f}° "
                   f"(confidence: {final_confidence:.3f}, quality: {quality})")
        
        return complete_result
    
    def apply_detected_orientation(self, img: np.ndarray, 
                                 orientation_result: Dict[str, Any]) -> np.ndarray:
        """
        Apply detected orientation to an image.
        
        Args:
            img: Input image
            orientation_result: Result from detect_orientation()
            
        Returns:
            Oriented image
        """
        rotation_angle = orientation_result['final_rotation']
        return self.rotate_image(img, rotation_angle)
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save orientation detection results to JSON file.
        
        Args:
            results: Results from detect_orientation()
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_path}")


def create_default_config() -> OrientationConfig:
    """Create a default configuration for orientation detection."""
    return OrientationConfig()


def load_config(config_path: str) -> OrientationConfig:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration JSON file
        
    Returns:
        OrientationConfig object
    """
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    return OrientationConfig(**config_dict)


def save_config(config: OrientationConfig, config_path: str):
    """
    Save configuration to JSON file.
    
    Args:
        config: OrientationConfig object
        config_path: Path to save configuration
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
    
    logger.info(f"Configuration saved to: {config_path}")