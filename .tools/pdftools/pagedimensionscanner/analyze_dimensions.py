#!/usr/bin/env python3
"""
Dimension Analysis Helper
Performs calculations and analysis on page dimension scan results.

Usage:
    python analyze_dimensions.py page_dimensions.json
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics


def load_scan_data(json_path: str):
    """Load scan results from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_detection_differences(data):
    """
    Compare detection methods and show which pages differ.
    """
    print("=" * 70)
    print("DETECTION METHOD COMPARISON")
    print("=" * 70)
    
    methods = ['edge_based', 'area_based', 'max_dimension', 'smart_fit']
    method_names = {
        'edge_based': 'Edge-Based (AND) [Current]',
        'area_based': 'Area-Based',
        'max_dimension': 'Max-Dimension',
        'smart_fit': 'Smart-Fit [Recommended]'
    }
    
    comparison = data['statistics']['detection_method_comparison']
    
    print(f"\n{'Method':<35} {'Pages':<10} {'%':<8} {'Difference from Current'}")
    print("-" * 70)
    
    current_count = comparison['edge_based']['total_oversized_pages']
    
    for method in methods:
        stats = comparison[method]
        count = stats['total_oversized_pages']
        pct = stats['percentage']
        diff = count - current_count
        diff_str = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "baseline"
        
        marker = " ★" if method == 'smart_fit' else " ◆" if method == 'edge_based' else ""
        print(f"{method_names[method]:<35} {count:<10} {pct:>6.2f}%  {diff_str}{marker}")
    
    print(f"\n★ = Recommended approach")
    print(f"◆ = Current implementation")
    
    # Calculate impact
    print(f"\n{'Impact of Switching to Smart-Fit:'}")
    print("-" * 70)
    
    smart_count = comparison['smart_fit']['total_oversized_pages']
    additional_pages = smart_count - current_count
    percentage_increase = (additional_pages / current_count * 100) if current_count > 0 else 0
    
    print(f"Additional pages flagged as oversized: {additional_pages:,}")
    print(f"Percentage increase: {percentage_increase:.1f}%")
    
    # 35mm film impact
    PAGES_PER_35MM_ROLL = 690
    additional_rolls = additional_pages / PAGES_PER_35MM_ROLL
    print(f"Estimated additional 35mm rolls needed: {additional_rolls:.1f}")
    
    return additional_pages, percentage_increase


def analyze_dimension_distribution(data):
    """Analyze the distribution of page dimensions."""
    print("\n" + "=" * 70)
    print("DIMENSION DISTRIBUTION")
    print("=" * 70)
    
    dim_histogram = data['dimension_histogram']
    total_pages = data['statistics']['total_pages_analyzed']
    
    # Sort by count
    sorted_dims = sorted(dim_histogram.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 15 Page Dimensions (inches):")
    print(f"{'Dimension':<15} {'Count':<10} {'Percentage':<12} {'Notes'}")
    print("-" * 70)
    
    for dim, count in sorted_dims[:15]:
        percentage = (count / total_pages * 100) if total_pages > 0 else 0
        
        # Add notes for known sizes
        notes = ""
        if "8.3×11.7" in dim:
            notes = "A4"
        elif "11.7×16.5" in dim:
            notes = "A3 (threshold)"
        elif "8.5×11.0" in dim:
            notes = "Letter"
        elif "11.0×17.0" in dim:
            notes = "Tabloid"
        
        print(f"{dim:<15} {count:<10} {percentage:>6.2f}%      {notes}")


def analyze_paper_sizes(data):
    """Analyze standard paper size distribution."""
    print("\n" + "=" * 70)
    print("PAPER SIZE DISTRIBUTION")
    print("=" * 70)
    
    paper_histogram = data['paper_size_histogram']
    total_pages = data['statistics']['total_pages_analyzed']
    
    # Sort by count
    sorted_sizes = sorted(paper_histogram.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Paper Size':<15} {'Count':<10} {'Percentage':<12} {'Status'}")
    print("-" * 70)
    
    for size, count in sorted_sizes:
        percentage = (count / total_pages * 100) if total_pages > 0 else 0
        
        # Determine status
        status = ""
        if size in ['A4', 'Letter', 'A5']:
            status = "✓ Standard (not oversized)"
        elif size == 'A3':
            status = "⚠ Threshold (not oversized)"
        elif size in ['Tabloid', 'A2', 'A1', 'A0']:
            status = "★ Oversized"
        elif size == 'Custom':
            status = "? Needs review"
        
        print(f"{size:<15} {count:<10} {percentage:>6.2f}%      {status}")


def find_edge_cases(data):
    """Find unusual page dimensions (edge cases)."""
    print("\n" + "=" * 70)
    print("EDGE CASES (Unusual Dimensions)")
    print("=" * 70)
    
    edge_cases = []
    
    # Analyze each PDF
    for pdf in data['pdf_analyses']:
        if not pdf.get('pages'):
            continue
        
        for page in pdf['pages']:
            width_in = page['width_inches']
            height_in = page['height_inches']
            min_dim = min(width_in, height_in)
            max_dim = max(width_in, height_in)
            
            # Define edge cases
            is_edge_case = False
            reason = ""
            
            # Very wide/narrow aspect ratio
            aspect_ratio = max_dim / min_dim if min_dim > 0 else 0
            if aspect_ratio > 2.0:
                is_edge_case = True
                reason = f"Extreme aspect ratio ({aspect_ratio:.1f}:1)"
            
            # One dimension very large
            if max_dim > 20:
                is_edge_case = True
                reason = f"Very large dimension ({max_dim:.1f}\")"
            
            # Detection method disagreement
            oversized = page['oversized']
            disagreement = sum([
                oversized['edge_based'],
                oversized['area_based'],
                oversized['max_dimension'],
                oversized['smart_fit']
            ])
            
            if 0 < disagreement < 4:  # Some methods say yes, some say no
                is_edge_case = True
                if not reason:
                    reason = "Detection method disagreement"
            
            if is_edge_case:
                edge_cases.append({
                    'pdf': pdf['filename'],
                    'page': page['page_num'],
                    'dimensions': f"{width_in:.1f}\" × {height_in:.1f}\"",
                    'reason': reason,
                    'edge_based': oversized['edge_based'],
                    'smart_fit': oversized['smart_fit']
                })
    
    if edge_cases:
        print(f"\nFound {len(edge_cases)} edge cases:")
        print(f"\n{'PDF':<30} {'Page':<6} {'Dimensions':<15} {'Edge':<6} {'Smart':<6} {'Reason'}")
        print("-" * 90)
        
        for case in edge_cases[:20]:  # Show first 20
            edge_mark = "✓" if case['edge_based'] else "✗"
            smart_mark = "✓" if case['smart_fit'] else "✗"
            print(f"{case['pdf']:<30} {case['page']:<6} {case['dimensions']:<15} {edge_mark:<6} {smart_mark:<6} {case['reason']}")
        
        if len(edge_cases) > 20:
            print(f"\n... and {len(edge_cases) - 20} more edge cases (see JSON for full list)")
    else:
        print("\nNo significant edge cases found.")


def generate_recommendations(data, additional_pages, percentage_increase):
    """Generate recommendations based on analysis."""
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    current_count = data['statistics']['detection_method_comparison']['edge_based']['total_oversized_pages']
    smart_count = data['statistics']['detection_method_comparison']['smart_fit']['total_oversized_pages']
    
    print("\nBased on the analysis:")
    print("-" * 70)
    
    # Recommendation logic
    if percentage_increase < 5:
        print("✓ MINIMAL IMPACT: Switching to Smart-Fit adds <5% more oversized pages")
        print("  Recommendation: SWITCH to Smart-Fit for better edge case handling")
        print("  Risk: Low - minimal cost increase")
    elif percentage_increase < 20:
        print("⚠ MODERATE IMPACT: Switching to Smart-Fit adds 5-20% more oversized pages")
        print("  Recommendation: CONSIDER switching to Smart-Fit")
        print("  Action: Review edge cases manually before deciding")
    else:
        print("⚠ HIGH IMPACT: Switching to Smart-Fit adds >20% more oversized pages")
        print("  Recommendation: REVIEW CAREFULLY before switching")
        print("  Action: Analyze cost-benefit and review sample edge cases")
    
    print(f"\nKey Metrics:")
    print(f"  Current (Edge-Based): {current_count:,} pages → 35mm")
    print(f"  Proposed (Smart-Fit): {smart_count:,} pages → 35mm")
    print(f"  Additional 35mm usage: {additional_pages:,} pages ({percentage_increase:.1f}% increase)")
    
    # Check for edge cases
    custom_count = data['paper_size_histogram'].get('Custom', 0)
    total_pages = data['statistics']['total_pages_analyzed']
    custom_pct = (custom_count / total_pages * 100) if total_pages > 0 else 0
    
    if custom_pct > 5:
        print(f"\n⚠ ALERT: {custom_pct:.1f}% of pages have custom (non-standard) dimensions")
        print(f"  Action: Review these pages manually - they may need special handling")


def main():
    """Main analysis function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_dimensions.py <page_dimensions.json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    
    if not Path(json_path).exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)
    
    print("\nLoading scan data...")
    data = load_scan_data(json_path)
    
    print(f"\nAnalyzing {data['statistics']['total_pages_analyzed']:,} pages from {data['statistics']['total_pdfs_scanned']} PDFs")
    print(f"Scan date: {data['scan_date']}")
    
    # Run analyses
    additional_pages, percentage_increase = analyze_detection_differences(data)
    analyze_dimension_distribution(data)
    analyze_paper_sizes(data)
    find_edge_cases(data)
    generate_recommendations(data, additional_pages, percentage_increase)
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()



