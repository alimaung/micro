#!/usr/bin/env python3
"""
Test script for orientation detection on microfilm samples.

Tests orientation detection capabilities on the available test cases.
"""

import os
import sys
from pathlib import Path
from pdf_converter import PDFConverter
from orientation_detector import OrientationDetector


def main():
    """Run orientation detection tests on all available test cases."""
    
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
    
    # Run orientation detection for each test case
    results = {}
    
    for case_name, case_path in available_cases.items():
        print(f"\n{'='*80}")
        print(f"TESTING ORIENTATION DETECTION: {case_name}")
        print(f"{'='*80}")
        
        try:
            # Create case-specific output directories
            base_dir = Path(f"orientation_test_{case_name.lower()}")
            conversion_dir = base_dir / "conversion"
            analysis_dir = base_dir / "analysis"
            
            # Ensure directories exist
            conversion_dir.mkdir(parents=True, exist_ok=True)
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Convert PDFs to images
            print("Step 1: Converting PDFs to images...")
            converter = PDFConverter(dpi=300, output_dir=str(conversion_dir))
            orig_images, repro_images, conversion_info = converter.convert_document_pair(
                str(original_pdf), str(case_path)
            )
            
            if not orig_images or not repro_images:
                print(f"Error: Failed to convert PDFs for case {case_name}")
                continue
            
            print(f"Converted {len(orig_images)} original and {len(repro_images)} reproduction pages")
            
            # Step 2: Detect orientation
            print("Step 2: Detecting orientation...")
            detector = OrientationDetector(output_dir=str(analysis_dir))
            orientation_report = detector.analyze_document_orientation(orig_images, repro_images)
            
            # Store results
            results[case_name] = {
                'success': True,
                'conversion_info': conversion_info,
                'orientation_report': orientation_report,
                'output_directories': {
                    'conversion': str(conversion_dir),
                    'analysis': str(analysis_dir)
                }
            }
            
            # Print case summary
            overall = orientation_report['overall_analysis']
            print(f"\n{case_name} Case Summary:")
            print(f"  Pages analyzed: {orientation_report['total_pages']}")
            print(f"  Most common rotation: {overall['most_common_coarse_rotation']}°")
            print(f"  Average confidence: {overall['average_confidence']:.3f}")
            print(f"  Average fine adjustment: {overall['average_fine_adjustment']:.1f}°")
            
            if overall['recommendations']:
                print(f"  Recommendations:")
                for rec in overall['recommendations']:
                    print(f"    • {rec}")
            
        except Exception as e:
            print(f"Error testing case {case_name}: {e}")
            results[case_name] = {
                'success': False,
                'error': str(e)
            }
            continue
    
    # Print comparative analysis
    print_comparative_analysis(results)


def print_comparative_analysis(results: dict):
    """Print comparative analysis of all test cases."""
    
    print(f"\n{'='*100}")
    print("COMPARATIVE ORIENTATION ANALYSIS")
    print(f"{'='*100}")
    
    # Table header
    print(f"{'Case':<8} {'Success':<8} {'Pages':<6} {'Common Rot':<11} {'Avg Conf':<9} {'Fine Adj':<9} {'Quality':<15}")
    print(f"{'-'*8} {'-'*8} {'-'*6} {'-'*11} {'-'*9} {'-'*9} {'-'*15}")
    
    successful_cases = []
    
    for case_name, result in results.items():
        if result['success']:
            report = result['orientation_report']
            overall = report['overall_analysis']
            
            pages = report['total_pages']
            common_rot = f"{overall['most_common_coarse_rotation']}°"
            avg_conf = f"{overall['average_confidence']:.3f}"
            fine_adj = f"{overall['average_fine_adjustment']:.1f}°"
            
            # Quality summary
            quality_dist = overall['quality_distribution']
            quality_summary = f"H:{quality_dist['HIGH']} M:{quality_dist['MEDIUM']} L:{quality_dist['LOW']}"
            
            print(f"{case_name:<8} {'✓':<8} {pages:<6} {common_rot:<11} {avg_conf:<9} {fine_adj:<9} {quality_summary:<15}")
            successful_cases.append((case_name, overall))
        else:
            print(f"{case_name:<8} {'✗':<8} {'N/A':<6} {'N/A':<11} {'N/A':<9} {'N/A':<9} {'Failed':<15}")
    
    # Analysis insights
    if len(successful_cases) > 1:
        print(f"\n{'='*100}")
        print("ANALYSIS INSIGHTS")
        print(f"{'='*100}")
        
        # Compare rotation patterns
        rotations = [overall['most_common_coarse_rotation'] for _, overall in successful_cases]
        confidences = [overall['average_confidence'] for _, overall in successful_cases]
        fine_adjustments = [overall['average_fine_adjustment'] for _, overall in successful_cases]
        
        print(f"\nRotation Pattern Analysis:")
        rotation_set = set(rotations)
        if len(rotation_set) == 1:
            print(f"  ✓ Consistent rotation across all cases: {rotations[0]}°")
        else:
            print(f"  ⚠ Inconsistent rotations detected:")
            for case_name, overall in successful_cases:
                print(f"    {case_name}: {overall['most_common_coarse_rotation']}°")
        
        print(f"\nConfidence Analysis:")
        avg_confidence = sum(confidences) / len(confidences)
        print(f"  Average confidence across cases: {avg_confidence:.3f}")
        if avg_confidence > 0.8:
            print(f"  ✓ High confidence in orientation detection")
        elif avg_confidence > 0.6:
            print(f"  ⚠ Moderate confidence - some uncertainty in detection")
        else:
            print(f"  ✗ Low confidence - manual verification recommended")
        
        print(f"\nFine Adjustment Analysis:")
        avg_fine_adj = sum(fine_adjustments) / len(fine_adjustments)
        print(f"  Average fine adjustment: {avg_fine_adj:.1f}°")
        if abs(avg_fine_adj) < 1:
            print(f"  ✓ Minimal systematic skew")
        elif abs(avg_fine_adj) < 3:
            print(f"  ⚠ Small systematic skew detected")
        else:
            print(f"  ✗ Significant systematic skew - check scanning alignment")
        
        # Case-specific insights
        print(f"\nCase-Specific Insights:")
        for case_name, overall in successful_cases:
            insights = []
            
            if overall['rotation_consistency'] < 0.8:
                insights.append("inconsistent page rotations")
            if overall['average_confidence'] < 0.6:
                insights.append("low detection confidence")
            if abs(overall['average_fine_adjustment']) > 3:
                insights.append(f"systematic skew ({overall['average_fine_adjustment']:.1f}°)")
            if overall['pages_with_warnings'] > 0:
                insights.append(f"{overall['pages_with_warnings']} pages with warnings")
            
            if insights:
                print(f"  {case_name}: {', '.join(insights)}")
            else:
                print(f"  {case_name}: no significant issues detected")
    
    print(f"\n{'='*100}")
    print("RECOMMENDATIONS")
    print(f"{'='*100}")
    
    # Generate overall recommendations
    if successful_cases:
        all_recommendations = set()
        for _, overall in successful_cases:
            all_recommendations.update(overall.get('recommendations', []))
        
        if all_recommendations:
            for rec in all_recommendations:
                print(f"• {rec}")
        else:
            print("• No specific recommendations - orientation detection appears reliable")
    else:
        print("• No successful cases to analyze")
    
    print(f"\nDetailed results saved in respective orientation_test_* directories")


if __name__ == "__main__":
    main()
