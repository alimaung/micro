#!/usr/bin/env python3
"""
Page Dimension Scanner
Scans PDF files and collects detailed page dimension data to analyze oversized page detection logic.

This scanner helps answer:
1. What are the actual page dimensions in our documents?
2. How do different detection algorithms perform on real data?
3. What edge cases exist in our document set?
"""

import os
import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import fitz  # PyMuPDF
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows color support
colorama.init()

# Paper size definitions (in points, 1 inch = 72 points)
PAPER_SIZES = {
    'A0': (2384, 3370),
    'A1': (1684, 2384),
    'A2': (1191, 1684),
    'A3': (842, 1191),    # 11.7" × 16.5"
    'A4': (595, 842),     # 8.27" × 11.69"
    'A5': (420, 595),
    'A6': (297, 420),
    'Letter': (612, 792),  # 8.5" × 11"
    'Legal': (612, 1008),  # 8.5" × 14"
    'Tabloid': (792, 1224), # 11" × 17"
    'Ledger': (1224, 792),  # 17" × 11"
}

# A3 threshold for oversized detection
A3_WIDTH = 842   # 11.7 inches
A3_HEIGHT = 1191  # 16.5 inches

# Tolerance for paper size matching (in points)
SIZE_TOLERANCE = 10


def should_skip_folder(folder_path: Path) -> bool:
    """Check if a folder should be skipped."""
    folder_name = folder_path.name
    folder_name_upper = folder_name.upper()
    folder_path_str = str(folder_path).upper()
    
    if folder_name.startswith("."):
        return True
    if "SYSTEM VOLUME INFORMATION" in folder_name_upper or "SYSTEM VOLUME INFORMATION" in folder_path_str:
        return True
    if "RECYCLE.BIN" in folder_name_upper or "$RECYCLE.BIN" in folder_name_upper:
        return True
    if "RECYCLE.BIN" in folder_path_str or "$RECYCLE.BIN" in folder_path_str:
        return True
    
    for parent in folder_path.parents:
        parent_name = parent.name.upper()
        if parent_name.startswith("."):
            return True
        if "SYSTEM VOLUME INFORMATION" in parent_name or "RECYCLE.BIN" in parent_name:
            return True
    
    return False


def find_project_folders(root_path: Path) -> List[Path]:
    """Find all first-level folders in root_path."""
    project_folders = []
    
    print(f"🔍 Scanning for PROJECT folders in: {root_path}")
    
    for item in root_path.iterdir():
        if not item.is_dir():
            continue
        if should_skip_folder(item):
            continue
        project_folders.append(item)
    
    return sorted(project_folders, key=lambda p: p.name)


def count_pdfs_in_folder(folder: Path) -> int:
    """Count PDF files directly in a folder."""
    count = 0
    try:
        for item in folder.iterdir():
            if item.is_file() and item.suffix.lower() == ".pdf":
                count += 1
    except (PermissionError, OSError):
        pass
    return count


def find_pdf_folder(project_folder: Path) -> Tuple[Optional[Path], List[str]]:
    """Find the PDF folder within a PROJECT folder."""
    warnings = []
    candidate_folders = []
    
    for item in project_folder.iterdir():
        if not item.is_dir():
            continue
        if should_skip_folder(item):
            continue
        
        pdf_count = count_pdfs_in_folder(item)
        
        if pdf_count > 0:
            total_files = sum(1 for f in item.iterdir() if f.is_file())
            candidate_folders.append({
                "path": item,
                "pdf_count": pdf_count,
                "total_files": total_files,
                "is_pdf_only": total_files == pdf_count
            })
    
    if not candidate_folders:
        return None, warnings
    
    candidate_folders.sort(key=lambda x: (not x["is_pdf_only"], -x["pdf_count"]))
    pdf_folder = candidate_folders[0]["path"]
    
    return pdf_folder, warnings


def get_closest_paper_size(width: float, height: float, tolerance: float = SIZE_TOLERANCE) -> Optional[str]:
    """
    Find the closest standard paper size for given dimensions.
    Checks both portrait and landscape orientations.
    """
    min_dim = min(width, height)
    max_dim = max(width, height)
    
    best_match = None
    best_distance = float('inf')
    
    for size_name, (size_w, size_h) in PAPER_SIZES.items():
        size_min = min(size_w, size_h)
        size_max = max(size_w, size_h)
        
        # Calculate Euclidean distance
        distance = ((min_dim - size_min) ** 2 + (max_dim - size_max) ** 2) ** 0.5
        
        if distance < best_distance:
            best_distance = distance
            best_match = size_name
    
    # Only return match if within tolerance
    if best_distance <= tolerance:
        return best_match
    
    return None


def classify_oversized(width: float, height: float) -> Dict[str, bool]:
    """
    Classify a page as oversized using all four detection methods.
    
    Returns dict with results from each method:
    - edge_based: AND logic (current implementation)
    - area_based: Area comparison
    - max_dimension: Maximum dimension check
    - smart_fit: Optimal rotation check
    """
    min_dim = min(width, height)
    max_dim = max(width, height)
    
    # Option 1: Edge-Based (AND logic) - Current implementation
    edge_based = (
        (width > A3_WIDTH and height > A3_HEIGHT) or
        (width > A3_HEIGHT and height > A3_WIDTH)
    )
    
    # Option 2: Area-Based
    A3_AREA = A3_WIDTH * A3_HEIGHT
    page_area = width * height
    area_based = page_area > A3_AREA
    
    # Option 3: Max-Dimension-Based
    max_dimension = max_dim > A3_HEIGHT
    
    # Option 4: Smart-Fit (recommended)
    smart_fit = (min_dim > A3_WIDTH or max_dim > A3_HEIGHT)
    
    return {
        'edge_based': edge_based,
        'area_based': area_based,
        'max_dimension': max_dimension,
        'smart_fit': smart_fit
    }


def export_to_csv(pdf_analyses: List[Dict], csv_path: Path) -> None:
    """
    Export page dimension data to CSV for easy analysis in Excel/Python/R.
    Creates a flat table with one row per page.
    """
    print(f"{Fore.CYAN}📊 Exporting to CSV: {csv_path}{Style.RESET_ALL}")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'pdf_filename',
            'project',
            'page_num',
            'width_points',
            'height_points',
            'width_inches',
            'height_inches',
            'area_sq_inches',
            'paper_size',
            'oversized_edge_based',
            'oversized_area_based',
            'oversized_max_dimension',
            'oversized_smart_fit'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_rows = 0
        for pdf_analysis in pdf_analyses:
            filename = pdf_analysis['filename']
            project = pdf_analysis['project']
            
            for page in pdf_analysis['pages']:
                writer.writerow({
                    'pdf_filename': filename,
                    'project': project,
                    'page_num': page['page_num'],
                    'width_points': page['width_points'],
                    'height_points': page['height_points'],
                    'width_inches': page['width_inches'],
                    'height_inches': page['height_inches'],
                    'area_sq_inches': page['area_sq_inches'],
                    'paper_size': page['paper_size'] or 'Custom',
                    'oversized_edge_based': page['oversized']['edge_based'],
                    'oversized_area_based': page['oversized']['area_based'],
                    'oversized_max_dimension': page['oversized']['max_dimension'],
                    'oversized_smart_fit': page['oversized']['smart_fit']
                })
                total_rows += 1
        
    print(f"{Fore.GREEN}✅ Exported {total_rows} rows to CSV{Style.RESET_ALL}")


def analyze_page_dimensions(pdf_path: Path, sample_pages: int = None) -> Dict[str, Any]:
    """
    Analyze all pages in a PDF and collect dimension data.
    
    Args:
        pdf_path: Path to PDF file
        sample_pages: If set, only analyze first N pages (for speed)
    
    Returns:
        Dictionary with page dimension analysis
    """
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        pages_to_analyze = total_pages
        if sample_pages and sample_pages < total_pages:
            pages_to_analyze = sample_pages
        
        # Collect page dimension data
        page_data = []
        dimension_histogram = defaultdict(int)  # Count pages by dimension
        paper_size_histogram = defaultdict(int)  # Count pages by paper size
        
        oversized_counts = {
            'edge_based': 0,
            'area_based': 0,
            'max_dimension': 0,
            'smart_fit': 0
        }
        
        for page_num in range(pages_to_analyze):
            page = doc[page_num]
            rect = page.rect
            width = rect.width
            height = rect.height
            
            # Classify page
            oversized_results = classify_oversized(width, height)
            
            # Update counts
            for method, is_oversized in oversized_results.items():
                if is_oversized:
                    oversized_counts[method] += 1
            
            # Get closest paper size
            paper_size = get_closest_paper_size(width, height)
            if paper_size:
                paper_size_histogram[paper_size] += 1
            else:
                paper_size_histogram['Custom'] += 1
            
            # Create dimension key (rounded to nearest inch for grouping)
            width_inches = round(width / 72, 1)
            height_inches = round(height / 72, 1)
            min_inch = min(width_inches, height_inches)
            max_inch = max(width_inches, height_inches)
            dimension_key = f"{min_inch}×{max_inch}"
            dimension_histogram[dimension_key] += 1
            
            # Store page data
            page_data.append({
                'page_num': page_num + 1,
                'width_points': round(width, 2),
                'height_points': round(height, 2),
                'width_inches': round(width / 72, 2),
                'height_inches': round(height / 72, 2),
                'area_sq_inches': round((width * height) / (72 * 72), 2),
                'paper_size': paper_size,
                'oversized': oversized_results
            })
        
        doc.close()
        
        # Calculate statistics
        any_oversized = any(count > 0 for count in oversized_counts.values())
        
        return {
            'success': True,
            'total_pages': total_pages,
            'analyzed_pages': pages_to_analyze,
            'page_data': page_data,
            'oversized_counts': oversized_counts,
            'dimension_histogram': dict(dimension_histogram),
            'paper_size_histogram': dict(paper_size_histogram),
            'has_oversized': any_oversized
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def scan_page_dimensions(root_path: str, output_file: str = "page_dimensions.json", 
                        sample_pdfs: int = None, sample_pages: int = None, export_csv: bool = False) -> None:
    """
    Main function to scan page dimensions across all PDFs.
    
    Args:
        root_path: Root directory to scan
        output_file: Output JSON file path
        sample_pdfs: If set, only scan first N PDFs (for testing)
        sample_pages: If set, only analyze first N pages per PDF (for speed)
    """
    root = Path(root_path)
    
    if not root.exists():
        print(f"{Fore.RED}❌ Error: Directory not found: {root_path}{Style.RESET_ALL}")
        return
    
    if not root.is_dir():
        print(f"{Fore.RED}❌ Error: Path is not a directory: {root_path}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📂 Starting dimension scan from: {root_path}{Style.RESET_ALL}")
    print(f"📐 A3 threshold: {A3_WIDTH/72:.1f}\" × {A3_HEIGHT/72:.1f}\"")
    if sample_pdfs:
        print(f"📊 Sample mode: Scanning up to {sample_pdfs} PDFs")
    if sample_pages:
        print(f"📄 Page sampling: Analyzing first {sample_pages} pages per PDF")
    print(f"🚫 Ignoring: folders starting with '.', System Volume Information, RECYCLE.BIN\n")
    
    # Find project folders
    project_folders = find_project_folders(root)
    
    if not project_folders:
        print(f"{Fore.YELLOW}⚠ No PROJECT folders found in {root_path}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Found {len(project_folders)} PROJECT folder(s){Style.RESET_ALL}\n")
    
    # Collect PDFs with metadata
    pdf_files_with_meta = []
    all_warnings = []
    
    for project_folder in project_folders:
        pdf_folder, warnings = find_pdf_folder(project_folder)
        
        if warnings:
            all_warnings.extend(warnings)
        
        if pdf_folder is None:
            continue
        
        # Collect PDFs
        for pdf_file in pdf_folder.glob("*.pdf"):
            if pdf_file.is_file():
                try:
                    file_size = pdf_file.stat().st_size
                    pdf_files_with_meta.append({
                        'path': pdf_file,
                        'size': file_size,
                        'project': project_folder.name
                    })
                except (OSError, PermissionError):
                    pdf_files_with_meta.append({
                        'path': pdf_file,
                        'size': 0,
                        'project': project_folder.name
                    })
        
        # Check subfolders
        for subfolder in pdf_folder.iterdir():
            if not subfolder.is_dir():
                continue
            if should_skip_folder(subfolder):
                continue
            
            for pdf_file in subfolder.glob("*.pdf"):
                if pdf_file.is_file():
                    try:
                        file_size = pdf_file.stat().st_size
                        pdf_files_with_meta.append({
                            'path': pdf_file,
                            'size': file_size,
                            'project': project_folder.name
                        })
                    except (OSError, PermissionError):
                        pdf_files_with_meta.append({
                            'path': pdf_file,
                            'size': 0,
                            'project': project_folder.name
                        })
    
    # Apply sample limit
    if sample_pdfs and sample_pdfs < len(pdf_files_with_meta):
        print(f"{Fore.YELLOW}📊 Limiting to {sample_pdfs} PDFs (out of {len(pdf_files_with_meta)} total){Style.RESET_ALL}\n")
        pdf_files_with_meta = pdf_files_with_meta[:sample_pdfs]
    
    pdf_files = [item['path'] for item in pdf_files_with_meta]
    
    if not pdf_files:
        print(f"{Fore.YELLOW}⚠ No PDF files found{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Found {len(pdf_files)} PDF file(s) to analyze{Style.RESET_ALL}\n")
    
    # Analyze PDFs
    pdf_analyses = []
    errors = []
    
    # Global statistics
    global_oversized_counts = {
        'edge_based': 0,
        'area_based': 0,
        'max_dimension': 0,
        'smart_fit': 0
    }
    
    global_dimension_histogram = defaultdict(int)
    global_paper_size_histogram = defaultdict(int)
    total_pages_analyzed = 0
    
    print(f"{Fore.CYAN}📊 Analyzing page dimensions...{Style.RESET_ALL}\n")
    
    for pdf_path in tqdm(pdf_files, desc="Scanning PDFs", unit="file"):
        analysis = analyze_page_dimensions(pdf_path, sample_pages)
        
        if not analysis['success']:
            errors.append({
                'path': str(pdf_path),
                'filename': pdf_path.name,
                'error': analysis.get('error', 'Unknown error')
            })
            continue
        
        # Update global statistics
        for method in global_oversized_counts:
            global_oversized_counts[method] += analysis['oversized_counts'][method]
        
        for dim_key, count in analysis['dimension_histogram'].items():
            global_dimension_histogram[dim_key] += count
        
        for size_key, count in analysis['paper_size_histogram'].items():
            global_paper_size_histogram[size_key] += count
        
        total_pages_analyzed += analysis['analyzed_pages']
        
        # Store complete PDF analysis with ALL page data
        pdf_analyses.append({
            'path': str(pdf_path),
            'filename': pdf_path.name,
            'project': pdf_path.parent.parent.name,
            'file_size_bytes': pdf_path.stat().st_size if pdf_path.exists() else 0,
            'total_pages': analysis['total_pages'],
            'analyzed_pages': analysis['analyzed_pages'],
            'oversized_counts': analysis['oversized_counts'],
            'dimension_histogram': analysis['dimension_histogram'],
            'paper_size_histogram': analysis['paper_size_histogram'],
            'has_oversized': analysis['has_oversized'],
            'pages': analysis['page_data']  # Include complete page-by-page data
        })
    
    # Calculate detection method comparison
    detection_comparison = {}
    for method in global_oversized_counts:
        detection_comparison[method] = {
            'total_oversized_pages': global_oversized_counts[method],
            'percentage': round((global_oversized_counts[method] / total_pages_analyzed * 100), 2) if total_pages_analyzed > 0 else 0
        }
    
    # Sort histograms
    sorted_dimensions = sorted(global_dimension_histogram.items(), key=lambda x: x[1], reverse=True)
    sorted_paper_sizes = sorted(global_paper_size_histogram.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare results
    results = {
        'scan_date': datetime.now().isoformat(),
        'root_path': str(root_path),
        'a3_threshold': {
            'width_inches': round(A3_WIDTH / 72, 2),
            'height_inches': round(A3_HEIGHT / 72, 2),
            'width_points': A3_WIDTH,
            'height_points': A3_HEIGHT
        },
        'statistics': {
            'total_pdfs_scanned': len(pdf_files),
            'total_pages_analyzed': total_pages_analyzed,
            'total_errors': len(errors),
            'detection_method_comparison': detection_comparison
        },
        'dimension_histogram': dict(sorted_dimensions[:50]),  # Top 50 dimensions
        'paper_size_histogram': dict(sorted_paper_sizes),
        'pdf_analyses': pdf_analyses,
        'errors': errors,
        'warnings': all_warnings
    }
    
    # Save JSON results
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Export CSV if requested
    csv_path = None
    if export_csv:
        csv_path = output_path.with_suffix('.csv')
        export_to_csv(pdf_analyses, csv_path)
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Scan Complete!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"📊 Total PDFs scanned: {len(pdf_files)}")
    print(f"📄 Total pages analyzed: {total_pages_analyzed}")
    print(f"❌ Errors: {len(errors)}")
    print(f"💾 JSON results: {output_path.absolute()}")
    if csv_path:
        print(f"📊 CSV export: {csv_path.absolute()}")
    
    # Detection method comparison
    print(f"\n{Fore.CYAN}Detection Method Comparison:{Style.RESET_ALL}")
    print(f"{'Method':<20} {'Oversized Pages':<20} {'Percentage':<15}")
    print(f"{'-'*55}")
    
    methods_display = {
        'edge_based': 'Edge-Based (AND)',
        'area_based': 'Area-Based',
        'max_dimension': 'Max-Dimension',
        'smart_fit': 'Smart-Fit'
    }
    
    for method, display_name in methods_display.items():
        stats = detection_comparison[method]
        color = Fore.YELLOW if method == 'edge_based' else Fore.WHITE
        print(f"{color}{display_name:<20} {stats['total_oversized_pages']:<20} {stats['percentage']:.2f}%{Style.RESET_ALL}")
    
    # Top paper sizes
    print(f"\n{Fore.CYAN}Top 10 Paper Sizes Found:{Style.RESET_ALL}")
    for size, count in sorted_paper_sizes[:10]:
        percentage = (count / total_pages_analyzed * 100) if total_pages_analyzed > 0 else 0
        print(f"  {size:<12}: {count:>6} pages ({percentage:>5.2f}%)")
    
    # Top dimensions
    print(f"\n{Fore.CYAN}Top 10 Page Dimensions (inches):{Style.RESET_ALL}")
    for dim, count in sorted_dimensions[:10]:
        percentage = (count / total_pages_analyzed * 100) if total_pages_analyzed > 0 else 0
        print(f"  {dim:<12}: {count:>6} pages ({percentage:>5.2f}%)")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Scan PDF page dimensions and analyze oversized detection methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python page_dimension_scanner.py X:\\
  python page_dimension_scanner.py X:\\ --sample-pdfs 100 --sample-pages 50
  python page_dimension_scanner.py X:\\ --output dimensions.json
        """
    )
    
    parser.add_argument(
        "root_path",
        type=str,
        help="Root directory to scan (e.g., X:\\)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="page_dimensions.json",
        help="Output JSON file path (default: page_dimensions.json)"
    )
    
    parser.add_argument(
        "--sample-pdfs",
        type=int,
        default=None,
        help="Limit scan to first N PDFs (for testing)"
    )
    
    parser.add_argument(
        "--sample-pages",
        type=int,
        default=None,
        help="Limit analysis to first N pages per PDF (for speed)"
    )
    
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Export page-level data to CSV (in addition to JSON)"
    )
    
    args = parser.parse_args()
    
    scan_page_dimensions(args.root_path, args.output, args.sample_pdfs, args.sample_pages, args.csv)


if __name__ == "__main__":
    main()

