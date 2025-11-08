#!/usr/bin/env python3
"""
Complete Alignment Test Script

Tests the full pipeline: PDF conversion → Orientation detection → Image alignment
Provides properly aligned image pairs ready for AOI analysis.
"""

import os
import sys
from pathlib import Path
from pdf_converter import PDFConverter
from orientation_detector import OrientationDetector
from image_aligner import ImageAligner


def test_complete_alignment_pipeline(original_pdf: str, reproduction_pdf: str, 
                                   case_name: str, output_base: str = "complete_alignment_test"):
    """
    Test complete alignment pipeline for a single case.
    
    Args:
        original_pdf: Path to original PDF
        reproduction_pdf: Path to reproduction PDF
        case_name: Name of test case (e.g., "OK", "NG", "BK")
        output_base: Base output directory
        
    Returns:
        Dictionary with complete results including aligned image pairs
    """
    
    print(f"\n{'='*80}")
    print(f"COMPLETE ALIGNMENT PIPELINE: {case_name}")
    print(f"{'='*80}")
    
    # Create case-specific output directory
    case_dir = Path(output_base) / f"case_{case_name.lower()}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Convert PDFs to images
        print("\n1. CONVERTING PDFs TO IMAGES")
        print("-" * 40)
        
        conversion_dir = case_dir / "01_conversion"
        converter = PDFConverter(dpi=300, output_dir=str(conversion_dir))
        orig_images, repro_images, conversion_info = converter.convert_document_pair(
            original_pdf, reproduction_pdf
        )
        
        if not orig_images or not repro_images:
            raise ValueError("Failed to convert PDFs to images")
        
        print(f"✓ Converted {len(orig_images)} original and {len(repro_images)} reproduction pages")
        
        # Step 2: Detect orientation
        print("\n2. DETECTING ORIENTATION")
        print("-" * 40)
        
        orientation_dir = case_dir / "02_orientation_detection"
        detector = OrientationDetector(output_dir=str(orientation_dir))
        orientation_results = detector.analyze_document_orientation(orig_images, repro_images)
        
        overall_orientation = orientation_results['overall_analysis']
        print(f"✓ Most common rotation: {overall_orientation['most_common_coarse_rotation']}°")
        print(f"✓ Average confidence: {overall_orientation['average_confidence']:.3f}")
        print(f"✓ Average fine adjustment: {overall_orientation['average_fine_adjustment']:.1f}°")
        
        # Step 3: Align images
        print("\n3. ALIGNING IMAGES")
        print("-" * 40)
        
        alignment_dir = case_dir / "03_aligned_images"
        aligner = ImageAligner(output_dir=str(alignment_dir))
        aligner.target_size_method = "original"  # Use original size as reference
        alignment_results = aligner.align_document_pair(orig_images, repro_images, orientation_results)
        
        overall_alignment = alignment_results['overall_statistics']
        print(f"✓ Pages aligned: {alignment_results['total_pages']}")
        print(f"✓ Average SSIM after alignment: {overall_alignment['average_ssim']:.4f}")
        print(f"✓ Average correlation after alignment: {overall_alignment['average_correlation']:.4f}")
        
        # Step 4: Prepare results
        print("\n4. PREPARING RESULTS")
        print("-" * 40)
        
        aligned_pairs = alignment_results['aligned_image_pairs']
        print(f"✓ {len(aligned_pairs)} aligned image pairs ready for AOI analysis")
        
        # Create summary visualization
        summary_path = create_pipeline_summary(case_dir, case_name, conversion_info, 
                                             orientation_results, alignment_results)
        print(f"✓ Pipeline summary saved: {summary_path}")
        
        return {
            'success': True,
            'case_name': case_name,
            'output_directory': str(case_dir),
            'conversion_info': conversion_info,
            'orientation_results': orientation_results,
            'alignment_results': alignment_results,
            'aligned_image_pairs': aligned_pairs,
            'summary_visualization': summary_path
        }
        
    except Exception as e:
        print(f"✗ Error in pipeline: {e}")
        return {
            'success': False,
            'case_name': case_name,
            'error': str(e)
        }


def create_pipeline_summary(case_dir: Path, case_name: str, conversion_info: dict,
                          orientation_results: dict, alignment_results: dict) -> str:
    """Create a summary visualization of the complete pipeline."""
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Complete Alignment Pipeline Summary: {case_name}', 
                 fontsize=16, fontweight='bold')
    
    # Conversion summary
    axes[0, 0].axis('off')
    axes[0, 0].set_title('1. PDF Conversion', fontweight='bold')
    
    conv_text = f"""
PDF Conversion Results:

Method: {conversion_info.get('method', 'N/A')}
DPI: {conversion_info.get('dpi', 'N/A')}
Original Pages: {conversion_info.get('original_pages', 'N/A')}
Reproduction Pages: {conversion_info.get('reproduction_pages', 'N/A')}

Original Dimensions: {conversion_info.get('original_dimensions', {}).get('width', 'N/A')}x{conversion_info.get('original_dimensions', {}).get('height', 'N/A')}
Reproduction Dimensions: {conversion_info.get('reproduction_dimensions', {}).get('width', 'N/A')}x{conversion_info.get('reproduction_dimensions', {}).get('height', 'N/A')}

Dimension Mismatch: {'Yes' if conversion_info.get('dimension_mismatch', False) else 'No'}
    """
    
    axes[0, 0].text(0.05, 0.95, conv_text, fontsize=10, verticalalignment='top',
                   fontfamily='monospace', transform=axes[0, 0].transAxes)
    
    # Orientation detection summary
    axes[0, 1].axis('off')
    axes[0, 1].set_title('2. Orientation Detection', fontweight='bold')
    
    overall_orient = orientation_results['overall_analysis']
    orient_text = f"""
Orientation Detection Results:

Most Common Rotation: {overall_orient['most_common_coarse_rotation']}°
Rotation Consistency: {overall_orient['rotation_consistency']:.1%}
Average Confidence: {overall_orient['average_confidence']:.3f}
Average Fine Adjustment: {overall_orient['average_fine_adjustment']:.1f}°

Quality Distribution:
  HIGH: {overall_orient['quality_distribution']['HIGH']} pages
  MEDIUM: {overall_orient['quality_distribution']['MEDIUM']} pages
  LOW: {overall_orient['quality_distribution']['LOW']} pages

Pages with Warnings: {overall_orient['pages_with_warnings']}
    """
    
    axes[0, 1].text(0.05, 0.95, orient_text, fontsize=10, verticalalignment='top',
                   fontfamily='monospace', transform=axes[0, 1].transAxes)
    
    # Alignment summary
    axes[1, 0].axis('off')
    axes[1, 0].set_title('3. Image Alignment', fontweight='bold')
    
    overall_align = alignment_results['overall_statistics']
    align_text = f"""
Image Alignment Results:

Pages Processed: {overall_align['pages_processed']}
Size Normalization: {alignment_results['alignment_settings']['normalize_sizes']}
Target Size Method: {alignment_results['alignment_settings']['target_size_method']}

Quality Metrics (After Alignment):
  Average SSIM: {overall_align['average_ssim']:.4f}
  SSIM Std Dev: {overall_align['std_ssim']:.4f}
  Average Correlation: {overall_align['average_correlation']:.4f}
  Correlation Std Dev: {overall_align['std_correlation']:.4f}
  Average MSE: {overall_align['average_mse']:.2f}
  Average PSNR: {overall_align['average_psnr']:.2f} dB
    """
    
    axes[1, 0].text(0.05, 0.95, align_text, fontsize=10, verticalalignment='top',
                   fontfamily='monospace', transform=axes[1, 0].transAxes)
    
    # Overall assessment
    axes[1, 1].axis('off')
    axes[1, 1].set_title('4. Overall Assessment', fontweight='bold')
    
    # Determine overall quality
    ssim_quality = "EXCELLENT" if overall_align['average_ssim'] > 0.9 else \
                  "GOOD" if overall_align['average_ssim'] > 0.8 else \
                  "FAIR" if overall_align['average_ssim'] > 0.6 else "POOR"
    
    confidence_quality = "HIGH" if overall_orient['average_confidence'] > 0.8 else \
                        "MEDIUM" if overall_orient['average_confidence'] > 0.6 else "LOW"
    
    assessment_text = f"""
Pipeline Assessment:

Alignment Quality: {ssim_quality}
  (SSIM: {overall_align['average_ssim']:.4f})

Detection Confidence: {confidence_quality}
  (Score: {overall_orient['average_confidence']:.3f})

Consistency: {'GOOD' if overall_orient['rotation_consistency'] > 0.8 else 'POOR'}
  (Rotation: {overall_orient['rotation_consistency']:.1%})

Ready for AOI Analysis: {'YES' if overall_align['average_ssim'] > 0.6 else 'NO'}

Recommendations:
    """
    
    # Add recommendations
    recommendations = overall_orient.get('recommendations', [])
    if not recommendations:
        assessment_text += "\n  • No issues detected"
    else:
        for rec in recommendations[:3]:  # Show first 3 recommendations
            assessment_text += f"\n  • {rec}"
    
    axes[1, 1].text(0.05, 0.95, assessment_text, fontsize=10, verticalalignment='top',
                   fontfamily='monospace', transform=axes[1, 1].transAxes)
    
    # Add colored border based on overall quality
    if overall_align['average_ssim'] > 0.8:
        border_color = 'green'
    elif overall_align['average_ssim'] > 0.6:
        border_color = 'orange'
    else:
        border_color = 'red'
    
    rect = patches.Rectangle((0, 0), 1, 1, linewidth=4, edgecolor=border_color,
                           facecolor='none', transform=axes[1, 1].transAxes)
    axes[1, 1].add_patch(rect)
    
    plt.tight_layout()
    
    # Save summary
    summary_path = case_dir / f"pipeline_summary_{case_name.lower()}.png"
    plt.savefig(summary_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(summary_path)


def main():
    """Run complete alignment pipeline tests on all available test cases."""
    
    # Test file paths (relative to scanner root)
    test_dir = Path("../../test")
    original_pdf = test_dir / "orig" / "1427004500479387.pdf"
    
    test_cases = {
        "OK": test_dir / "scan" / "1427004500479387_SCAN_OK.pdf",
        "NG": test_dir / "scan" / "1427004500479387_SCAN_NG.pdf", 
        "BK": test_dir / "scan" / "1427004500479387_SCAN_BK.pdf"
    }
    
    # Verify files exist
    if not original_pdf.exists():
        print(f"Error: Original file not found: {original_pdf}")
        sys.exit(1)
    
    available_cases = {}
    for case_name, case_path in test_cases.items():
        if case_path.exists():
            available_cases[case_name] = case_path
        else:
            print(f"Warning: Test case {case_name} not found: {case_path}")
    
    if not available_cases:
        print("Error: No test cases found!")
        sys.exit(1)
    
    # Run complete pipeline for each test case
    results = {}
    
    for case_name, case_path in available_cases.items():
        result = test_complete_alignment_pipeline(
            str(original_pdf), str(case_path), case_name
        )
        results[case_name] = result
    
    # Print comparative summary
    print_final_summary(results)


def print_final_summary(results: dict):
    """Print final summary of all test cases."""
    
    print(f"\n{'='*100}")
    print("COMPLETE ALIGNMENT PIPELINE SUMMARY")
    print(f"{'='*100}")
    
    # Table header
    print(f"{'Case':<8} {'Success':<8} {'Pages':<6} {'Rotation':<9} {'SSIM':<8} {'Confidence':<11} {'Quality':<12}")
    print(f"{'-'*8} {'-'*8} {'-'*6} {'-'*9} {'-'*8} {'-'*11} {'-'*12}")
    
    successful_cases = []
    
    for case_name, result in results.items():
        if result['success']:
            alignment = result['alignment_results']['overall_statistics']
            orientation = result['orientation_results']['overall_analysis']
            
            pages = alignment['pages_processed']
            rotation = f"{orientation['most_common_coarse_rotation']}°"
            ssim = f"{alignment['average_ssim']:.3f}"
            confidence = f"{orientation['average_confidence']:.3f}"
            
            # Overall quality assessment
            if alignment['average_ssim'] > 0.8:
                quality = "EXCELLENT"
            elif alignment['average_ssim'] > 0.6:
                quality = "GOOD"
            else:
                quality = "POOR"
            
            print(f"{case_name:<8} {'✓':<8} {pages:<6} {rotation:<9} {ssim:<8} {confidence:<11} {quality:<12}")
            successful_cases.append((case_name, result))
        else:
            print(f"{case_name:<8} {'✗':<8} {'N/A':<6} {'N/A':<9} {'N/A':<8} {'N/A':<11} {'FAILED':<12}")
    
    if successful_cases:
        print(f"\n{'='*100}")
        print("ALIGNED IMAGE PAIRS READY FOR AOI ANALYSIS")
        print(f"{'='*100}")
        
        for case_name, result in successful_cases:
            aligned_pairs = result['aligned_image_pairs']
            print(f"\n{case_name} Case:")
            print(f"  • {len(aligned_pairs)} aligned image pairs available")
            print(f"  • Output directory: {result['output_directory']}")
            print(f"  • Aligned images saved in: {result['output_directory']}/03_aligned_images/")
            
            # Show per-page alignment quality
            for pair in aligned_pairs[:3]:  # Show first 3 pages
                page_num = pair['page']
                ssim = pair['alignment_quality']['ssim']
                rotation = pair['rotation_applied']
                print(f"    Page {page_num}: SSIM={ssim:.3f}, Rotation={rotation:.1f}°")
            
            if len(aligned_pairs) > 3:
                print(f"    ... and {len(aligned_pairs) - 3} more pages")
        
        print(f"\n{'='*100}")
        print("NEXT STEPS")
        print(f"{'='*100}")
        print("The aligned image pairs are now ready for:")
        print("• Brightness/contrast analysis")
        print("• Scratch and artifact detection") 
        print("• OCR readability assessment")
        print("• Any other AOI analysis modules")
        print("\nAccess aligned images via: result['aligned_image_pairs']")
        print("Each pair contains: 'original' and 'reproduction' numpy arrays")


if __name__ == "__main__":
    main()
