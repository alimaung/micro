#!/usr/bin/env python3
"""
Basic Usage Example for Automated Optical Inspection (AOI) Orientation Detection

This example demonstrates the basic workflow for detecting orientation
between an original document and its microfilm reproduction.
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from orientation_detector import OrientationDetector, OrientationConfig
from orientation_visualizer import OrientationVisualizer


def main():
    """Demonstrate basic orientation detection workflow."""
    
    print("Automated Optical Inspection (AOI) Orientation Detection - Basic Usage Example")
    print("=" * 50)
    
    # Step 1: Create or load test images
    print("1. Creating test images...")
    
    # Create a simple test document
    original_img = create_test_document()
    
    # Create a rotated version to simulate microfilm reproduction
    rotation_angle = 92.5  # 90 degrees + 2.5 degrees fine adjustment
    reproduction_img = rotate_image(original_img, rotation_angle)
    
    print(f"   Original image shape: {original_img.shape}")
    print(f"   Reproduction rotated by: {rotation_angle}°")
    
    # Step 2: Initialize the orientation detector
    print("\n2. Initializing orientation detector...")
    
    # Use default configuration
    detector = OrientationDetector()
    print(f"   Using default configuration")
    print(f"   Test rotations: {detector.config.test_rotations}")
    print(f"   Fine angle range: {detector.config.fine_angle_range}")
    
    # Step 3: Detect orientation
    print("\n3. Detecting orientation...")
    
    result = detector.detect_orientation(original_img, reproduction_img)
    
    print(f"   Detected rotation: {result['final_rotation']:.1f}°")
    print(f"   Confidence: {result['final_confidence']:.3f}")
    print(f"   Quality: {result['quality']}")
    
    # Step 4: Apply detected orientation
    print("\n4. Applying detected orientation...")
    
    aligned_img = detector.apply_detected_orientation(reproduction_img, result)
    print(f"   Aligned image shape: {aligned_img.shape}")
    
    # Step 5: Create visualizations
    print("\n5. Creating visualizations...")
    
    visualizer = OrientationVisualizer(output_dir="basic_example_results")
    
    # Create comparison visualization
    comparison_path = visualizer.create_orientation_comparison(
        original_img, reproduction_img, result, page_num=1
    )
    print(f"   Comparison saved to: {comparison_path}")
    
    # Create fine angle plot (if fine detection was performed)
    if result.get('fine_result'):
        fine_plot_path = visualizer.create_fine_angle_plot(result, page_num=1)
        print(f"   Fine angle plot saved to: {fine_plot_path}")
    
    # Step 6: Validate results
    print("\n6. Validating results...")
    
    expected_rotation = rotation_angle
    detected_rotation = result['final_rotation']
    error = abs(detected_rotation - expected_rotation)
    
    # Handle angle wrapping (e.g., 270° vs -90°)
    if error > 180:
        error = 360 - error
    
    print(f"   Expected rotation: {expected_rotation:.1f}°")
    print(f"   Detected rotation: {detected_rotation:.1f}°")
    print(f"   Detection error: {error:.1f}°")
    
    if error < 5.0:
        print("   ✓ Detection successful (error < 5°)")
    else:
        print("   ⚠ Detection may need improvement (error >= 5°)")
    
    print("\n" + "=" * 50)
    print("Basic usage example completed!")
    print(f"Check the 'basic_example_results' directory for visualizations.")


def create_test_document(width: int = 600, height: int = 800) -> np.ndarray:
    """
    Create a test document image with various features.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Grayscale test document image
    """
    # Create white background
    img = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add document header
    cv2.rectangle(img, (50, 50), (width-50, 120), 0, 2)
    cv2.putText(img, 'TEST DOCUMENT', (70, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2, 0, 2)
    
    # Add text content lines
    line_height = 30
    start_y = 180
    
    text_lines = [
        "This is a sample document for testing orientation detection.",
        "It contains various text elements and geometric shapes",
        "that provide features for the detection algorithms.",
        "",
        "The document includes:",
        "• Text content with different fonts and sizes",
        "• Geometric shapes (rectangles, circles, lines)",
        "• Structured layout elements",
        "• Clear boundaries and edges"
    ]
    
    for i, line in enumerate(text_lines):
        y = start_y + i * line_height
        if line:  # Skip empty lines
            cv2.putText(img, line, (80, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    
    # Add geometric shapes for feature detection
    # Rectangle
    cv2.rectangle(img, (100, 450), (200, 520), 0, 2)
    cv2.putText(img, 'Rectangle', (110, 490), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Circle
    cv2.circle(img, (350, 485), 35, 0, 2)
    cv2.putText(img, 'Circle', (320, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Triangle
    pts = np.array([[450, 520], [500, 450], [550, 520]], np.int32)
    cv2.polylines(img, [pts], True, 0, 2)
    cv2.putText(img, 'Triangle', (460, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Add footer
    cv2.line(img, (50, height-80), (width-50, height-80), 0, 1)
    cv2.putText(img, 'Page 1 - Orientation Detection Test', 
               (width//2-120, height-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    
    return img


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate an image by the specified angle.
    
    Args:
        img: Input image
        angle: Rotation angle in degrees (positive = counterclockwise)
        
    Returns:
        Rotated image
    """
    height, width = img.shape
    center = (width // 2, height // 2)
    
    # Create rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Apply rotation
    rotated = cv2.warpAffine(img, rotation_matrix, (width, height), 
                           borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    
    return rotated


if __name__ == "__main__":
    main()
