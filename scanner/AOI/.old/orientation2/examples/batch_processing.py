#!/usr/bin/env python3
"""
Batch Processing Example for Automated Optical Inspection (AOI) Orientation Detection

This example demonstrates how to process multiple pages/documents
in batch mode with comprehensive reporting and visualization.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import json

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from orientation_detector import OrientationDetector, OrientationConfig
from orientation_visualizer import create_batch_visualization


def main():
    """Demonstrate batch processing workflow."""
    
    print("Automated Optical Inspection (AOI) Orientation Detection - Batch Processing Example")
    print("=" * 60)
    
    # Step 1: Create test document set
    print("1. Creating test document set...")
    
    # Create multiple pages with different orientations
    test_cases = [
        ("Page 1", 0),      # No rotation
        ("Page 2", 90),     # 90-degree rotation
        ("Page 3", 180),    # 180-degree rotation
        ("Page 4", 270),    # 270-degree rotation
        ("Page 5", 45),     # 45-degree rotation
        ("Page 6", -30),    # -30-degree rotation
        ("Page 7", 92.5),   # 90 + 2.5 degrees
        ("Page 8", 183.7),  # 180 + 3.7 degrees
    ]
    
    original_images = []
    reproduction_images = []
    page_numbers = []
    expected_rotations = []
    
    for i, (page_name, rotation) in enumerate(test_cases):
        print(f"   Creating {page_name} (rotation: {rotation}°)")
        
        # Create original document
        original = create_test_page(page_name, i + 1)
        original_images.append(original)
        
        # Create rotated reproduction
        reproduction = rotate_image(original, rotation)
        reproduction_images.append(reproduction)
        
        page_numbers.append(i + 1)
        expected_rotations.append(rotation)
    
    print(f"   Created {len(test_cases)} test pages")
    
    # Step 2: Configure detector for batch processing
    print("\n2. Configuring detector for batch processing...")
    
    # Use a configuration optimized for batch processing
    config = OrientationConfig(
        resize_for_speed=True,      # Enable speed optimization
        max_dimension=600,          # Smaller images for faster processing
        fine_angle_range=(-8.0, 8.0),  # Slightly narrower range
        fine_angle_step=0.5,        # Good balance of speed vs accuracy
        weights={                   # Balanced weights
            'ssim': 0.4,
            'feature_matching': 0.3,
            'edge_correlation': 0.2,
            'template_matching': 0.1
        }
    )
    
    detector = OrientationDetector(config)
    print(f"   Configured for {len(config.test_rotations)} coarse rotations")
    print(f"   Fine angle range: {config.fine_angle_range}")
    print(f"   Max processing dimension: {config.max_dimension}")
    
    # Step 3: Process all pages
    print("\n3. Processing all pages...")
    
    results = []
    processing_stats = {
        'total_pages': len(test_cases),
        'successful_detections': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0,
        'total_error': 0.0
    }
    
    for i, (original, reproduction) in enumerate(zip(original_images, reproduction_images)):
        page_num = page_numbers[i]
        expected_rotation = expected_rotations[i]
        
        print(f"   Processing page {page_num}...")
        
        # Detect orientation
        result = detector.detect_orientation(original, reproduction)
        results.append(result)
        
        # Calculate accuracy
        detected_rotation = result['final_rotation']
        error = calculate_rotation_error(expected_rotation, detected_rotation)
        processing_stats['total_error'] += error
        
        # Count confidence levels
        confidence = result['final_confidence']
        if confidence >= config.high_confidence:
            processing_stats['high_confidence'] += 1
        elif confidence >= config.min_confidence:
            processing_stats['medium_confidence'] += 1
        else:
            processing_stats['low_confidence'] += 1
        
        # Count successful detections (error < 10 degrees)
        if error < 10.0:
            processing_stats['successful_detections'] += 1
        
        print(f"      Expected: {expected_rotation:6.1f}°, "
              f"Detected: {detected_rotation:6.1f}°, "
              f"Error: {error:5.1f}°, "
              f"Confidence: {confidence:.3f}")
    
    # Step 4: Generate comprehensive visualizations
    print("\n4. Generating comprehensive visualizations...")
    
    output_dir = "batch_processing_results"
    created_files = create_batch_visualization(
        original_images,
        reproduction_images,
        results,
        page_numbers,
        document_name="Batch Processing Test",
        output_dir=output_dir
    )
    
    print(f"   Created {len(created_files)} visualization files:")
    for file_type, file_path in created_files.items():
        print(f"      {file_type}: {Path(file_path).name}")
    
    # Step 5: Generate detailed statistics
    print("\n5. Processing statistics...")
    
    processing_stats['average_error'] = processing_stats['total_error'] / processing_stats['total_pages']
    processing_stats['success_rate'] = processing_stats['successful_detections'] / processing_stats['total_pages']
    
    print(f"   Total pages processed: {processing_stats['total_pages']}")
    print(f"   Successful detections: {processing_stats['successful_detections']} "
          f"({processing_stats['success_rate']:.1%})")
    print(f"   Average error: {processing_stats['average_error']:.1f}°")
    print(f"   Confidence distribution:")
    print(f"      High: {processing_stats['high_confidence']} pages")
    print(f"      Medium: {processing_stats['medium_confidence']} pages")
    print(f"      Low: {processing_stats['low_confidence']} pages")
    
    # Step 6: Save detailed results
    print("\n6. Saving detailed results...")
    
    # Create detailed report
    detailed_report = {
        'test_configuration': {
            'test_cases': len(test_cases),
            'detector_config': config.__dict__,
            'processing_date': str(Path(__file__).stat().st_mtime)
        },
        'processing_statistics': processing_stats,
        'individual_results': []
    }
    
    for i, (result, expected) in enumerate(zip(results, expected_rotations)):
        page_report = {
            'page_number': page_numbers[i],
            'expected_rotation': expected,
            'detected_rotation': result['final_rotation'],
            'error': calculate_rotation_error(expected, result['final_rotation']),
            'confidence': result['final_confidence'],
            'quality': result['quality'],
            'coarse_rotation': result['coarse_result']['best_rotation'],
            'fine_angle': result.get('fine_result', {}).get('best_fine_angle', 0.0)
        }
        detailed_report['individual_results'].append(page_report)
    
    # Save report
    report_path = Path(output_dir) / "detailed_batch_report.json"
    with open(report_path, 'w') as f:
        json.dump(detailed_report, f, indent=2, default=str)
    
    print(f"   Detailed report saved to: {report_path}")
    
    # Step 7: Performance analysis
    print("\n7. Performance analysis...")
    
    # Analyze by rotation type
    rotation_analysis = analyze_by_rotation_type(results, expected_rotations)
    
    print("   Performance by rotation type:")
    for rotation_type, stats in rotation_analysis.items():
        print(f"      {rotation_type}: {stats['count']} pages, "
              f"avg error: {stats['avg_error']:.1f}°, "
              f"avg confidence: {stats['avg_confidence']:.3f}")
    
    print("\n" + "=" * 60)
    print("Batch processing example completed!")
    print(f"Results saved to: {output_dir}/")
    print(f"Overall success rate: {processing_stats['success_rate']:.1%}")
    
    if processing_stats['success_rate'] >= 0.8:
        print("✓ Excellent batch processing performance!")
    elif processing_stats['success_rate'] >= 0.6:
        print("⚠ Good batch processing performance")
    else:
        print("✗ Batch processing may need optimization")


def create_test_page(page_name: str, page_number: int, 
                    width: int = 500, height: int = 700) -> np.ndarray:
    """Create a test page with unique content."""
    
    # Create white background
    img = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add page header
    cv2.rectangle(img, (30, 30), (width-30, 80), 0, 2)
    cv2.putText(img, page_name, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
    
    # Add page number
    cv2.putText(img, f'Page {page_number}', (width-100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    
    # Add unique content based on page number
    content_y = 120
    
    # Text content
    text_lines = [
        f"This is {page_name} of the batch processing test.",
        "Each page has unique content to ensure proper",
        "orientation detection across different layouts.",
        "",
        f"Page-specific identifier: {page_number:04d}",
        f"Content hash: {hash(page_name) % 10000:04d}"
    ]
    
    for line in text_lines:
        if line:
            cv2.putText(img, line, (50, content_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
        content_y += 25
    
    # Add unique geometric pattern based on page number
    pattern_y = content_y + 50
    
    if page_number % 4 == 1:
        # Rectangles
        for i in range(3):
            cv2.rectangle(img, (80 + i*100, pattern_y), (130 + i*100, pattern_y + 50), 0, 2)
    elif page_number % 4 == 2:
        # Circles
        for i in range(3):
            cv2.circle(img, (105 + i*100, pattern_y + 25), 25, 0, 2)
    elif page_number % 4 == 3:
        # Triangles
        for i in range(3):
            pts = np.array([[80 + i*100, pattern_y + 50], 
                           [105 + i*100, pattern_y], 
                           [130 + i*100, pattern_y + 50]], np.int32)
            cv2.polylines(img, [pts], True, 0, 2)
    else:
        # Mixed shapes
        cv2.rectangle(img, (80, pattern_y), (130, pattern_y + 50), 0, 2)
        cv2.circle(img, (205, pattern_y + 25), 25, 0, 2)
        pts = np.array([[280, pattern_y + 50], [305, pattern_y], [330, pattern_y + 50]], np.int32)
        cv2.polylines(img, [pts], True, 0, 2)
    
    # Add footer
    cv2.line(img, (30, height-60), (width-30, height-60), 0, 1)
    cv2.putText(img, f'Batch Test - {page_name}', 
               (50, height-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    return img


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotate an image by the specified angle."""
    height, width = img.shape
    center = (width // 2, height // 2)
    
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (width, height), 
                           borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    
    return rotated


def calculate_rotation_error(expected: float, detected: float) -> float:
    """Calculate the error between expected and detected rotation angles."""
    error = abs(detected - expected)
    
    # Handle angle wrapping (e.g., 270° vs -90°)
    if error > 180:
        error = 360 - error
    
    return error


def analyze_by_rotation_type(results: List, expected_rotations: List) -> dict:
    """Analyze results by rotation type (0°, 90°, 180°, 270°, other)."""
    
    analysis = {
        '0° (No rotation)': {'errors': [], 'confidences': [], 'count': 0},
        '90° rotations': {'errors': [], 'confidences': [], 'count': 0},
        '180° rotations': {'errors': [], 'confidences': [], 'count': 0},
        '270° rotations': {'errors': [], 'confidences': [], 'count': 0},
        'Other angles': {'errors': [], 'confidences': [], 'count': 0}
    }
    
    for result, expected in zip(results, expected_rotations):
        detected = result['final_rotation']
        confidence = result['final_confidence']
        error = calculate_rotation_error(expected, detected)
        
        # Categorize by expected rotation
        if abs(expected) < 5:
            category = '0° (No rotation)'
        elif abs(expected - 90) < 5 or abs(expected + 270) < 5:
            category = '90° rotations'
        elif abs(expected - 180) < 5 or abs(expected + 180) < 5:
            category = '180° rotations'
        elif abs(expected - 270) < 5 or abs(expected + 90) < 5:
            category = '270° rotations'
        else:
            category = 'Other angles'
        
        analysis[category]['errors'].append(error)
        analysis[category]['confidences'].append(confidence)
        analysis[category]['count'] += 1
    
    # Calculate averages
    for category, data in analysis.items():
        if data['count'] > 0:
            data['avg_error'] = sum(data['errors']) / data['count']
            data['avg_confidence'] = sum(data['confidences']) / data['count']
        else:
            data['avg_error'] = 0.0
            data['avg_confidence'] = 0.0
    
    return analysis


if __name__ == "__main__":
    main()
