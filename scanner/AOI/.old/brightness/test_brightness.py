#!/usr/bin/env python3
"""
Test script for brightness analysis on microfilm samples.

Tests three cases:
- OK: Similar brightness, no faults
- NG: Wrong scanner settings, no faults  
- BK: Similar brightness, faulty (scratches)
"""

import os
import sys
from pathlib import Path
from brightness_analyzer import BrightnessAnalyzer


def main():
    """Run brightness analysis on all test cases."""
    
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
    
    for case_name, case_path in test_cases.items():
        if not case_path.exists():
            print(f"Warning: Test case {case_name} not found: {case_path}")
    
    # Run analysis for each test case
    results = {}
    
    for case_name, case_path in test_cases.items():
        if not case_path.exists():
            continue
            
        print(f"\n{'='*60}")
        print(f"ANALYZING CASE: {case_name}")
        print(f"{'='*60}")
        
        try:
            # Create analyzer with case-specific output directory
            output_dir = f"brightness_analysis_{case_name.lower()}"
            analyzer = BrightnessAnalyzer(dpi=300, output_dir=output_dir)
            
            # Run analysis
            report = analyzer.analyze_document(str(original_pdf), str(case_path))
            analyzer.print_summary(report)
            
            # Store results for comparison
            results[case_name] = report['overall_assessment']
            
        except Exception as e:
            print(f"Error analyzing case {case_name}: {e}")
            continue
    
    # Print comparative summary
    print(f"\n{'='*80}")
    print("COMPARATIVE BRIGHTNESS ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    print(f"{'Case':<8} {'Quality Score':<15} {'Issues':<50}")
    print(f"{'-'*8} {'-'*15} {'-'*50}")
    
    for case_name, assessment in results.items():
        quality_score = f"{assessment['average_quality_score']:.3f}"
        issues = ", ".join(assessment['unique_issues'][:2]) if assessment['unique_issues'] else "None"
        if len(issues) > 47:
            issues = issues[:44] + "..."
        print(f"{case_name:<8} {quality_score:<15} {issues:<50}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS INTERPRETATION:")
    print(f"{'='*80}")
    
    # Provide interpretation based on results
    if 'OK' in results and 'NG' in results:
        ok_score = results['OK']['average_quality_score']
        ng_score = results['NG']['average_quality_score']
        
        print(f"OK vs NG Comparison:")
        print(f"  OK Quality Score: {ok_score:.3f}")
        print(f"  NG Quality Score: {ng_score:.3f}")
        print(f"  Difference: {abs(ok_score - ng_score):.3f}")
        
        if ng_score < ok_score - 0.1:
            print(f"  → NG case shows significantly lower quality (likely scanner settings issue)")
        elif ng_score > ok_score + 0.1:
            print(f"  → NG case shows higher brightness (possible overexposure in scanning)")
        else:
            print(f"  → Both cases show similar quality scores")
    
    if 'BK' in results:
        bk_score = results['BK']['average_quality_score']
        print(f"\nBK (Faulty) Case:")
        print(f"  Quality Score: {bk_score:.3f}")
        if bk_score < 0.7:
            print(f"  → Low quality score suggests physical defects detected")
        print(f"  Issues: {', '.join(results['BK']['unique_issues'])}")
    
    print(f"\nDetailed results saved in respective brightness_analysis_* directories")


if __name__ == "__main__":
    main()
