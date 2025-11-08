#!/usr/bin/env python3
"""
Image Orientation and Alignment Module

Detects and corrects rotation differences between original and microfilm images.
Uses a two-stage approach: coarse rotation detection (90° increments) followed by
fine angle adjustment (sub-degree precision).

For white pages, uses PDF metadata (dimensions, rotation) instead of image-based detection.
"""

import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from typing import Tuple, Dict, Any, Optional
import fitz  # PyMuPDF for PDF metadata extraction


class ImageAligner:
    """Aligns images by detecting and correcting rotation differences."""
    
    def __init__(self):
        """Initialize image aligner."""
        pass
    
    def get_pdf_orientation(self, orig_pdf_path: str, film_pdf_path: str,
                           orig_page_index: int, film_page_index: int) -> Dict[str, Any]:
        """
        Get orientation difference between original and film pages using PDF metadata.
        
        For white pages, this method uses PDF page dimensions and rotation metadata
        to determine the coarse rotation needed (0, 90, 180, or 270 degrees).
        
        Priority:
        1. PDF rotation field (if present and reliable)
        2. Dimension comparison (portrait vs landscape)
        3. Fallback: assume 0° if unclear
        
        Args:
            orig_pdf_path (str): Path to original PDF
            film_pdf_path (str): Path to film PDF
            orig_page_index (int): Zero-based page index in original PDF
            film_page_index (int): Zero-based page index in film PDF
            
        Returns:
            Dict[str, Any]: Alignment information with:
                - coarse_rotation: Rotation angle in degrees (0, 90, 180, 270)
                - fine_angle: Always 0.0 for white pages
                - method: 'pdf_metadata'
                - orig_dimensions: (width, height) in points
                - film_dimensions: (width, height) in points
                - orig_rotation: PDF rotation field value
                - film_rotation: PDF rotation field value
        """
        print(f"Getting PDF orientation for white pages (orig page {orig_page_index + 1}, film page {film_page_index + 1})...")
        
        try:
            # Open PDFs
            orig_doc = fitz.open(orig_pdf_path)
            film_doc = fitz.open(film_pdf_path)
            
            # Get original page info
            orig_page = orig_doc[orig_page_index]
            orig_rect = orig_page.rect
            orig_width = orig_rect.width
            orig_height = orig_rect.height
            orig_rotation = orig_page.rotation  # PDF rotation metadata (0, 90, 180, 270)
            
            # Get film page info
            film_page = film_doc[film_page_index]
            film_rect = film_page.rect
            film_width = film_rect.width
            film_height = film_rect.height
            film_rotation = film_page.rotation  # PDF rotation metadata
            
            # Close PDFs
            orig_doc.close()
            film_doc.close()
            
            # Determine orientation using PDF rotation field first
            rotation_needed = None
            
            # Try PDF rotation field first (if both have valid rotation metadata)
            if orig_rotation is not None and film_rotation is not None:
                # Calculate rotation difference
                rotation_diff = (film_rotation - orig_rotation) % 360
                # Normalize to 0, 90, 180, 270
                if rotation_diff <= 45 or rotation_diff >= 315:
                    rotation_needed = 0
                elif 45 < rotation_diff <= 135:
                    rotation_needed = 90
                elif 135 < rotation_diff <= 225:
                    rotation_needed = 180
                else:  # 225 < rotation_diff < 315
                    rotation_needed = 270
                print(f"  Using PDF rotation field: orig={orig_rotation}°, film={film_rotation}° → {rotation_needed}°")
            
            # Fall back to dimension comparison if rotation field didn't work
            if rotation_needed is None:
                orig_is_portrait = orig_height > orig_width
                film_is_portrait = film_height > film_width
                
                if orig_is_portrait == film_is_portrait:
                    # Same orientation - check if dimensions match
                    # If dimensions are very different, might be rotated
                    orig_ratio = orig_height / orig_width if orig_width > 0 else 1.0
                    film_ratio = film_height / film_width if film_width > 0 else 1.0
                    
                    # If ratios are similar, likely same orientation (0°)
                    # If ratios are inverse, likely 90° rotation
                    if abs(orig_ratio - film_ratio) < 0.1:
                        rotation_needed = 0
                    elif abs(orig_ratio - (1.0 / film_ratio)) < 0.1:
                        rotation_needed = 90
                    else:
                        rotation_needed = 0  # Default fallback
                else:
                    # Different orientations - need 90° or 270° rotation
                    # Determine which based on dimension comparison
                    # If orig is portrait and film is landscape, need 90° or 270°
                    # Check which rotation makes dimensions match better
                    if orig_is_portrait:
                        # Original portrait, film landscape
                        # 90° rotation: orig height → film width, orig width → film height
                        if abs(orig_height - film_width) < abs(orig_width - film_height):
                            rotation_needed = 90
                        else:
                            rotation_needed = 270
                    else:
                        # Original landscape, film portrait
                        # 90° rotation: orig width → film height, orig height → film width
                        if abs(orig_width - film_height) < abs(orig_height - film_width):
                            rotation_needed = 90
                        else:
                            rotation_needed = 270
                
                print(f"  Using dimension comparison: orig={orig_width:.1f}x{orig_height:.1f} ({'portrait' if orig_is_portrait else 'landscape'}), "
                      f"film={film_width:.1f}x{film_height:.1f} ({'portrait' if film_is_portrait else 'landscape'}) → {rotation_needed}°")
            
            alignment_info = {
                'coarse_rotation': rotation_needed,
                'fine_angle': 0.0,
                'total_rotation': float(rotation_needed),
                'method': 'pdf_metadata',
                'orig_dimensions': (float(orig_width), float(orig_height)),
                'film_dimensions': (float(film_width), float(film_height)),
                'orig_rotation': orig_rotation,
                'film_rotation': film_rotation
            }
            
            print(f"PDF orientation determined: {rotation_needed}° (coarse only, no fine adjustment)")
            return alignment_info
            
        except Exception as e:
            print(f"Error getting PDF orientation: {e}")
            # Fallback: return 0° rotation
            return {
                'coarse_rotation': 0,
                'fine_angle': 0.0,
                'total_rotation': 0.0,
                'method': 'pdf_metadata_fallback',
                'error': str(e)
            }
    
    def detect_rotation(self, orig_img: np.ndarray, film_img: np.ndarray) -> int:
        """
        Detect the rotation angle between original and film (0, 90, 180, 270 degrees).
        
        Uses edge detection and SSIM scoring to find the best coarse rotation.
        
        Args:
            orig_img (np.ndarray): Original image (grayscale)
            film_img (np.ndarray): Film image to align (grayscale)
            
        Returns:
            int: Best rotation angle in degrees (0, 90, 180, or 270)
        """
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
        """
        Find fine angle adjustment after coarse rotation.
        
        Tests angles from -10° to +10° in 0.5° increments to find optimal alignment.
        
        Args:
            orig_img (np.ndarray): Original image (grayscale)
            film_img (np.ndarray): Film image to align (grayscale)
            coarse_rotation (int): Coarse rotation angle already applied (0, 90, 180, 270)
            
        Returns:
            float: Best fine angle adjustment in degrees
        """
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
    
    def align_images(self, orig_img: np.ndarray, film_img: np.ndarray,
                    orig_is_white: bool = False,
                    orig_pdf_path: Optional[str] = None,
                    film_pdf_path: Optional[str] = None,
                    orig_page_index: Optional[int] = None,
                    film_page_index: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Align film image to original image using rotation detection.
        
        For white pages, uses PDF metadata for coarse rotation only.
        For non-white pages, performs full two-stage alignment:
        1. Coarse rotation detection (90° increments)
        2. Fine angle adjustment (sub-degree precision)
        
        Args:
            orig_img (np.ndarray): Original image (grayscale)
            film_img (np.ndarray): Film image to align (grayscale)
            orig_is_white (bool): Whether original page is white (default: False)
            orig_pdf_path (Optional[str]): Path to original PDF (required if orig_is_white=True)
            film_pdf_path (Optional[str]): Path to film PDF (required if orig_is_white=True)
            orig_page_index (Optional[int]): Zero-based page index in original PDF (required if orig_is_white=True)
            film_page_index (Optional[int]): Zero-based page index in film PDF (required if orig_is_white=True)
            
        Returns:
            Tuple[np.ndarray, np.ndarray, Dict]: (original_img, aligned_film_img, alignment_info)
                - original_img: Unchanged original image
                - aligned_film_img: Film image after rotation correction
                - alignment_info: Dictionary with rotation details
        """
        if orig_is_white:
            # Use PDF metadata for white pages (coarse rotation only)
            if orig_pdf_path is None or film_pdf_path is None or orig_page_index is None or film_page_index is None:
                raise ValueError("PDF paths and page indexes required for white page orientation detection")
            
            print("Aligning white pages using PDF metadata...")
            alignment_info = self.get_pdf_orientation(
                orig_pdf_path, film_pdf_path, orig_page_index, film_page_index
            )
            
            # Apply rotation to film image
            aligned_film = film_img.copy()
            coarse_rotation = alignment_info['coarse_rotation']
            
            if coarse_rotation == 90:
                aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif coarse_rotation == 180:
                aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_180)
            elif coarse_rotation == 270:
                aligned_film = cv2.rotate(aligned_film, cv2.ROTATE_90_CLOCKWISE)
            # else: 0° - no rotation needed
            
            # Resize to match original dimensions
            if aligned_film.shape != orig_img.shape:
                aligned_film = cv2.resize(aligned_film, (orig_img.shape[1], orig_img.shape[0]))
            
            print(f"White page alignment complete: {coarse_rotation}° (coarse only)")
            return orig_img, aligned_film, alignment_info
        
        else:
            # Use full image-based detection for non-white pages
            print("Aligning images using image-based detection...")
            
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
                'total_rotation': coarse_rotation + fine_angle,
                'method': 'image_based'
            }
            
            print(f"Alignment complete: {coarse_rotation}° + {fine_angle:.1f}° = {coarse_rotation + fine_angle:.1f}°")
            return orig_img, aligned_film, alignment_info

