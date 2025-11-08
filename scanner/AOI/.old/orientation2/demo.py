#!/usr/bin/env python3
"""
Automated Optical Inspection (AOI) Orientation Detection - Complete Demonstration

This script demonstrates the complete Automated Optical Inspection (AOI) orientation detection system
with real-world usage scenarios and integration examples.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
import argparse
import json

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from orientation_detector import OrientationDetector, OrientationConfig
from orientation_visualizer import OrientationVisualizer, create_batch_visualization
from integration import (
    EnhancedDocumentComparator, 
    create_pdf_orientation_processor,
    quick_orientation_check,
    batch_orientation_correction
)


def main():
    """Main demonstration function."""
    
    parser = argparse.ArgumentParser(description='AOI Orientation Detection Demonstration')
    parser.add_argument('--mode', choices=['basic', 'batch', 'pdf', 'integration'], 
                       default='basic', help='Demonstration mode')
    parser.add_argument('--original', help='Path to original PDF/image')
    parser.add_argument('--reproduction', help='Path to reproduction PDF/image')
    parser.add_argument('--output', default='demo_results', help='Output directory')
    parser.add_argument('--config', help='Path to configuration JSON file')
    
    args = parser.parse_args()
    
    print("Automated Optical Inspection (AOI) Orientation Detection System - Demonstration")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Output directory: {args.output}")
    
    if args.mode == 'basic':
        demo_basic_detection(args.output, args.config)
    elif args.mode == 'batch':
        demo_batch_processing(args.output, args.config)
    elif args.mode == 'pdf':
        if not args.original or not args.reproduction:
            print("Error: PDF mode requires --original and --reproduction arguments")
            return
        demo_pdf_processing(args.original, args.reproduction, args.output, args.config)
    elif args.mode == 'integration':
        demo_integration_examples(args.output, args.config)
    
    print("\nDemonstration completed!")
    print(f"Results saved to: {args.output}")


def demo_basic_detection(output_dir: str, config_path: str = None):
    """Demonstrate basic orientation detection."""
    
    print("\n1. BASIC ORIENTATION DETECTION")
    print("-" * 40)
    
    # Load or create configuration
    if config_path and Path(config_path).exists():
        from orientation_detector import load_config
        config = load_config(config_path)
        print(f"Loaded configuration from: {config_path}")
    else:
        config = OrientationConfig()
        print("Using default configuration")
    
    # Create test images
    print("Creating test document...")
    original = create_demo_document()
    
    # Test different rotation scenarios
    test_rotations = [0, 45, 90, 135, 180, 225, 270, 315, 92.5, -87.3]
    
    detector = OrientationDetector(config)
    visualizer = OrientationVisualizer(output_dir=output_dir)
    
    results = []
    
    for i, rotation in enumerate(test_rotations):
        print(f"\nTesting rotation: {rotation}°")
        
        # Create rotated reproduction
        reproduction = rotate_image(original, rotation)
        
        # Detect orientation
        result = detector.detect_orientation(original, reproduction)
        
        detected = result['final_rotation']
        confidence = result['final_confidence']
        quality = result['quality']
        
        # Calculate error
        error = calculate_angle_error(rotation, detected)
        
        print(f"  Expected: {rotation:6.1f}°")
        print(f"  Detected: {detected:6.1f}°")
        print(f"  Error:    {error:6.1f}°")
        print(f"  Confidence: {confidence:.3f} ({quality})")
        
        # Create visualization
        comparison_path = visualizer.create_orientation_comparison(
            original, reproduction, result, page_num=i+1
        )
        
        results.append({
            'test_rotation': rotation,
            'detected_rotation': detected,
            'error': error,
            'confidence': confidence,
            'quality': quality,
            'result': result
        })
    
    # Summary statistics
    errors = [r['error'] for r in results]
    confidences = [r['confidence'] for r in results]
    
    print(f"\nSUMMARY STATISTICS:")
    print(f"  Average error: {np.mean(errors):.1f}°")
    print(f"  Max error: {max(errors):.1f}°")
    print(f"  Average confidence: {np.mean(confidences):.3f}")
    print(f"  Success rate (error < 5°): {sum(1 for e in errors if e < 5.0) / len(errors):.1%}")
    
    # Save results
    with open(Path(output_dir) / "basic_demo_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)


def demo_batch_processing(output_dir: str, config_path: str = None):
    """Demonstrate batch processing capabilities."""
    
    print("\n2. BATCH PROCESSING DEMONSTRATION")
    print("-" * 40)
    
    # Create a set of different document types
    document_types = [
        ("Text Document", create_text_document),
        ("Technical Drawing", create_technical_drawing),
        ("Mixed Content", create_mixed_content),
        ("Table Document", create_table_document)
    ]
    
    # Test rotations for each document type
    test_rotations = [0, 90, 180, 270, 45, -30]
    
    all_originals = []
    all_reproductions = []
    all_results = []
    page_numbers = []
    
    detector = OrientationDetector()
    page_counter = 1
    
    for doc_name, create_func in document_types:
        print(f"\nProcessing {doc_name}...")
        
        # Create base document
        base_doc = create_func()
        
        for rotation in test_rotations:
            print(f"  Testing {rotation}° rotation...")
            
            # Create rotated version
            rotated = rotate_image(base_doc, rotation)
            
            # Detect orientation
            result = detector.detect_orientation(base_doc, rotated)
            
            all_originals.append(base_doc)
            all_reproductions.append(rotated)
            all_results.append(result)
            page_numbers.append(page_counter)
            
            page_counter += 1
    
    # Create batch visualizations
    print(f"\nCreating batch visualizations for {len(all_results)} test cases...")
    
    created_files = create_batch_visualization(
        all_originals,
        all_reproductions,
        all_results,
        page_numbers,
        document_name="Batch Processing Demo",
        output_dir=output_dir
    )
    
    print(f"Created {len(created_files)} visualization files")
    
    # Calculate batch statistics
    rotations = [r['final_rotation'] for r in all_results]
    confidences = [r['final_confidence'] for r in all_results]
    qualities = [r['quality'] for r in all_results]
    
    quality_counts = {'high': 0, 'medium': 0, 'low': 0}
    for q in qualities:
        quality_counts[q] += 1
    
    print(f"\nBATCH PROCESSING STATISTICS:")
    print(f"  Total test cases: {len(all_results)}")
    print(f"  Average confidence: {np.mean(confidences):.3f}")
    print(f"  Quality distribution:")
    for quality, count in quality_counts.items():
        print(f"    {quality.capitalize()}: {count} ({count/len(qualities):.1%})")


def demo_pdf_processing(original_pdf: str, reproduction_pdf: str, 
                       output_dir: str, config_path: str = None):
    """Demonstrate PDF processing capabilities."""
    
    print("\n3. PDF PROCESSING DEMONSTRATION")
    print("-" * 40)
    print(f"Original PDF: {original_pdf}")
    print(f"Reproduction PDF: {reproduction_pdf}")
    
    # Process PDFs
    try:
        processing_result = create_pdf_orientation_processor(
            original_pdf, 
            reproduction_pdf, 
            output_dir=output_dir,
            dpi=200  # Lower DPI for demo speed
        )
        
        stats = processing_result['processing_statistics']
        
        print(f"\nPDF PROCESSING RESULTS:")
        print(f"  Pages processed: {processing_result['pages_processed']}")
        print(f"  Average confidence: {stats['average_confidence']:.3f}")
        print(f"  Most common rotation: {stats['most_common_rotation']}°")
        print(f"  High confidence pages: {stats['high_confidence_pages']}")
        print(f"  Low confidence pages: {stats['low_confidence_pages']}")
        
        print(f"\nCreated files:")
        for file_type, file_path in processing_result['created_files'].items():
            print(f"  {file_type}: {Path(file_path).name}")
        
    except Exception as e:
        print(f"Error processing PDFs: {e}")
        print("Make sure pdf2image and poppler are properly installed")


def demo_integration_examples(output_dir: str, config_path: str = None):
    """Demonstrate integration with existing systems."""
    
    print("\n4. INTEGRATION EXAMPLES")
    print("-" * 40)
    
    # Create test images
    original = create_demo_document()
    reproduction = rotate_image(original, 95.5)  # 90° + 5.5° fine adjustment
    
    # Example 1: Quick orientation check
    print("Example 1: Quick orientation check")
    quick_result = quick_orientation_check(original, reproduction)
    print(f"  Rotation: {quick_result['rotation_degrees']:.1f}°")
    print(f"  Confidence: {quick_result['confidence']:.3f}")
    print(f"  Recommended action: {quick_result['recommended_action']}")
    
    # Example 2: Enhanced document comparator
    print("\nExample 2: Enhanced document comparator")
    comparator = EnhancedDocumentComparator(output_dir=output_dir)
    
    # Align images
    aligned_orig, aligned_repro, alignment_info = comparator.align_images_with_aoi(
        original, reproduction, page_num=1
    )
    
    print(f"  Alignment method: {alignment_info['method']}")
    print(f"  Applied rotation: {alignment_info['final_rotation']:.1f}°")
    print(f"  Confidence: {alignment_info['confidence']:.3f}")
    print(f"  Quality: {alignment_info['quality']}")
    
    # Example 3: Batch correction
    print("\nExample 3: Batch orientation correction")
    
    # Create multiple test pairs
    test_pairs = []
    for rotation in [0, 90, 180, 270]:
        rotated = rotate_image(original, rotation)
        test_pairs.append((original, rotated))
    
    corrected_images = batch_orientation_correction(test_pairs, output_dir)
    print(f"  Corrected {len(corrected_images)} images")
    
    # Save corrected images for inspection
    for i, corrected in enumerate(corrected_images):
        output_path = Path(output_dir) / f"corrected_image_{i+1}.png"
        cv2.imwrite(str(output_path), corrected)
    
    print(f"  Saved corrected images to {output_dir}")


# Helper functions for creating test documents

def create_demo_document(width: int = 600, height: int = 800) -> np.ndarray:
    """Create a comprehensive demo document."""
    img = np.ones((height, width), dtype=np.uint8) * 255
    
    # Header
    cv2.rectangle(img, (50, 50), (width-50, 120), 0, 2)
    cv2.putText(img, 'AOI ORIENTATION DEMO', (70, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
    
    # Content sections
    y = 160
    sections = [
        "This document demonstrates the AOI orientation detection system.",
        "It contains various elements that provide features for detection:",
        "",
        "• Text content with different formatting",
        "• Geometric shapes and patterns", 
        "• Structured layout elements",
        "• Clear boundaries and reference points"
    ]
    
    for section in sections:
        if section:
            cv2.putText(img, section, (80, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
        y += 30
    
    # Geometric elements
    # Rectangle
    cv2.rectangle(img, (100, 400), (200, 480), 0, 2)
    cv2.putText(img, 'RECT', (130, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)
    
    # Circle
    cv2.circle(img, (350, 440), 40, 0, 2)
    cv2.putText(img, 'CIRCLE', (315, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Triangle
    pts = np.array([[450, 480], [500, 400], [550, 480]], np.int32)
    cv2.fillPoly(img, [pts], 128)
    cv2.putText(img, 'TRI', (475, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)
    
    # Footer
    cv2.line(img, (50, height-80), (width-50, height-80), 0, 2)
    cv2.putText(img, 'Automated Optical Inspection (AOI) v1.0', 
               (80, height-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    
    return img


def create_text_document() -> np.ndarray:
    """Create a text-heavy document."""
    img = np.ones((600, 500), dtype=np.uint8) * 255
    
    cv2.putText(img, 'TEXT DOCUMENT', (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
    
    text_lines = [
        "Lorem ipsum dolor sit amet, consectetur",
        "adipiscing elit. Sed do eiusmod tempor",
        "incididunt ut labore et dolore magna",
        "aliqua. Ut enim ad minim veniam, quis",
        "nostrud exercitation ullamco laboris.",
        "",
        "Duis aute irure dolor in reprehenderit",
        "in voluptate velit esse cillum dolore",
        "eu fugiat nulla pariatur. Excepteur",
        "sint occaecat cupidatat non proident."
    ]
    
    y = 100
    for line in text_lines:
        if line:
            cv2.putText(img, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
        y += 25
    
    return img


def create_technical_drawing() -> np.ndarray:
    """Create a technical drawing-style document."""
    img = np.ones((600, 500), dtype=np.uint8) * 255
    
    cv2.putText(img, 'TECHNICAL DRAWING', (120, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
    
    # Draw technical elements
    # Main rectangle with dimensions
    cv2.rectangle(img, (100, 100), (400, 300), 0, 2)
    cv2.putText(img, '300mm', (220, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    cv2.putText(img, '200mm', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Internal elements
    cv2.circle(img, (200, 200), 30, 0, 2)
    cv2.circle(img, (300, 200), 30, 0, 2)
    
    # Dimension lines
    cv2.line(img, (200, 320), (300, 320), 0, 1)
    cv2.putText(img, '100mm', (230, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)
    
    return img


def create_mixed_content() -> np.ndarray:
    """Create a document with mixed content types."""
    img = np.ones((700, 600), dtype=np.uint8) * 255
    
    cv2.putText(img, 'MIXED CONTENT', (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
    
    # Text section
    cv2.putText(img, 'Text Section:', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
    cv2.putText(img, 'This section contains regular text content', (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # Diagram section
    cv2.putText(img, 'Diagram Section:', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
    cv2.rectangle(img, (50, 220), (150, 300), 0, 2)
    cv2.circle(img, (250, 260), 40, 0, 2)
    cv2.line(img, (150, 260), (210, 260), 0, 2)
    cv2.arrowedLine(img, (290, 260), (350, 260), 0, 2, tipLength=0.1)
    
    # Table section
    cv2.putText(img, 'Table Section:', (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
    for i in range(4):
        cv2.line(img, (50, 400 + i*30), (350, 400 + i*30), 0, 1)
    for i in range(4):
        cv2.line(img, (50 + i*100, 400), (50 + i*100, 490), 0, 1)
    
    return img


def create_table_document() -> np.ndarray:
    """Create a table-heavy document."""
    img = np.ones((600, 500), dtype=np.uint8) * 255
    
    cv2.putText(img, 'TABLE DOCUMENT', (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
    
    # Create table grid
    rows, cols = 8, 4
    cell_width, cell_height = 80, 30
    start_x, start_y = 80, 100
    
    # Draw grid
    for i in range(rows + 1):
        y = start_y + i * cell_height
        cv2.line(img, (start_x, y), (start_x + cols * cell_width, y), 0, 1)
    
    for j in range(cols + 1):
        x = start_x + j * cell_width
        cv2.line(img, (x, start_y), (x, start_y + rows * cell_height), 0, 1)
    
    # Add table content
    headers = ['Item', 'Qty', 'Price', 'Total']
    for j, header in enumerate(headers):
        x = start_x + j * cell_width + 10
        cv2.putText(img, header, (x, start_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)
    
    return img


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotate image by specified angle."""
    height, width = img.shape
    center = (width // 2, height // 2)
    
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (width, height), 
                           borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    
    return rotated


def calculate_angle_error(expected: float, detected: float) -> float:
    """Calculate error between expected and detected angles."""
    error = abs(detected - expected)
    
    # Handle angle wrapping
    if error > 180:
        error = 360 - error
    
    return error


if __name__ == "__main__":
    main()
