#!/usr/bin/env python3
"""
Large Oversized Range Scanner
Scans X:\ drive where first-level folders are PROJECTS, finds PDF folders within them,
analyzes PDFs for oversized pages, groups them into ranges, and identifies ranges exceeding 690 pages.

This scanner helps identify edge cases where a single oversized range would exceed 35mm roll capacity.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import fitz  # PyMuPDF
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows color support
colorama.init()

# Oversized page thresholds (in points, 1 inch = 72 points)
OVERSIZE_THRESHOLD_WIDTH = 11.7 * 72  # A4 width: 8.27 inches = ~595 points, we use 11.7 inches
OVERSIZE_THRESHOLD_HEIGHT = 16.5 * 72  # A4 height: 11.69 inches = ~842 points, we use 16.5 inches

# 35mm film capacity
CAPACITY_35MM = 690


def should_skip_folder(folder_path: Path) -> bool:
    """
    Check if a folder should be skipped.
    Skips:
    - Folders starting with "." (like .output)
    - System Volume Information folders (case-insensitive)
    - RECYCLE.BIN and $RECYCLE.BIN folders (case-insensitive)
    - Any folder inside excluded folders
    """
    folder_name = folder_path.name
    folder_name_upper = folder_name.upper()
    folder_path_str = str(folder_path).upper()
    
    # Skip folders starting with "."
    if folder_name.startswith("."):
        return True
    
    # Skip System Volume Information folders
    if "SYSTEM VOLUME INFORMATION" in folder_name_upper or "SYSTEM VOLUME INFORMATION" in folder_path_str:
        return True
    
    # Skip recycle bin folders
    if "RECYCLE.BIN" in folder_name_upper or "$RECYCLE.BIN" in folder_name_upper:
        return True
    if "RECYCLE.BIN" in folder_path_str or "$RECYCLE.BIN" in folder_path_str:
        return True
    
    # Check if any parent folder is excluded
    for parent in folder_path.parents:
        parent_name = parent.name.upper()
        parent_path_str = str(parent).upper()
        
        if parent_name.startswith("."):
            return True
        if "SYSTEM VOLUME INFORMATION" in parent_name or "SYSTEM VOLUME INFORMATION" in parent_path_str:
            return True
        if "RECYCLE.BIN" in parent_name or "$RECYCLE.BIN" in parent_name:
            return True
        if "RECYCLE.BIN" in parent_path_str or "$RECYCLE.BIN" in parent_path_str:
            return True
    
    return False


def find_project_folders(root_path: Path) -> List[Path]:
    """
    Find all first-level folders in root_path - these are the PROJECT folders.
    Skips folders starting with "."
    """
    project_folders = []
    
    print(f"🔍 Scanning for PROJECT folders (first-level) in: {root_path}")
    
    # Get all first-level directories (these are the PROJECTS)
    for item in root_path.iterdir():
        if not item.is_dir():
            continue
        
        # Skip folders starting with "."
        if should_skip_folder(item):
            continue
        
        project_folders.append(item)
    
    return project_folders


def count_pdfs_in_folder(folder: Path) -> int:
    """
    Count PDF files directly in a folder (not recursive).
    """
    count = 0
    try:
        for item in folder.iterdir():
            if item.is_file() and item.suffix.lower() == ".pdf":
                count += 1
    except (PermissionError, OSError):
        pass
    return count


def find_pdf_folder(project_folder: Path) -> Tuple[Optional[Path], List[str]]:
    """
    Find the PDF folder within a PROJECT folder.
    The PDF folder is the second-level folder that contains only PDF files.
    Also checks one level deeper for PDFs.
    
    Returns:
        tuple: (pdf_folder_path, warnings_list)
    """
    warnings = []
    candidate_folders = []
    
    # Look for all second-level folders (direct children of PROJECT)
    for item in project_folder.iterdir():
        if not item.is_dir():
            continue
        
        # Skip folders starting with "."
        if should_skip_folder(item):
            continue
        
        # Count PDFs directly in this folder
        pdf_count = count_pdfs_in_folder(item)
        
        if pdf_count > 0:
            # Count total files to check if folder contains only PDFs
            total_files = sum(1 for f in item.iterdir() if f.is_file())
            candidate_folders.append({
                "path": item,
                "pdf_count": pdf_count,
                "total_files": total_files,
                "is_pdf_only": total_files == pdf_count
            })
    
    if not candidate_folders:
        warnings.append(f"No folders with PDFs found in {project_folder.name}")
        return None, warnings
    
    # Sort by: 1) PDF-only folders first, 2) then by PDF count
    candidate_folders.sort(key=lambda x: (not x["is_pdf_only"], -x["pdf_count"]))
    
    # Check for multiple candidates
    pdf_only_folders = [c for c in candidate_folders if c["is_pdf_only"]]
    
    if len(pdf_only_folders) > 1:
        warnings.append(
            f"Multiple PDF-only folders found in {project_folder.name}: "
            f"{', '.join([c['path'].name for c in pdf_only_folders])}"
        )
    elif len(pdf_only_folders) == 0:
        # No PDF-only folder, use the one with most PDFs
        warnings.append(
            f"No PDF-only folder found in {project_folder.name}, "
            f"using folder with most PDFs: {candidate_folders[0]['path'].name} "
            f"({candidate_folders[0]['pdf_count']} PDFs, {candidate_folders[0]['total_files']} total files)"
        )
    
    # Use the best candidate
    pdf_folder = candidate_folders[0]["path"]
    
    # Check one level deeper for PDFs
    deeper_pdfs = []
    for subfolder in pdf_folder.iterdir():
        if not subfolder.is_dir():
            continue
        if should_skip_folder(subfolder):
            continue
        
        deeper_pdf_count = count_pdfs_in_folder(subfolder)
        if deeper_pdf_count > 0:
            deeper_pdfs.append((subfolder, deeper_pdf_count))
    
    if deeper_pdfs:
        warnings.append(
            f"Found PDFs one level deeper in {project_folder.name}/{pdf_folder.name}: "
            f"{', '.join([f'{sf.name} ({count} PDFs)' for sf, count in deeper_pdfs])}"
        )
    
    return pdf_folder, warnings


def is_oversized_page(page) -> bool:
    """
    Check if a page is oversized based on dimensions.
    A page is oversized if its width or height exceeds the thresholds.
    """
    rect = page.rect
    width = rect.width
    height = rect.height
    
    # Check both orientations (portrait and landscape)
    return (
        (width > OVERSIZE_THRESHOLD_WIDTH and height > OVERSIZE_THRESHOLD_HEIGHT) or
        (width > OVERSIZE_THRESHOLD_HEIGHT and height > OVERSIZE_THRESHOLD_WIDTH)
    )


def analyze_pdf_oversized_pages(pdf_path: Path) -> Dict[str, Any]:
    """
    Analyze a PDF for oversized pages and group them into ranges.
    
    Returns:
        dict: Analysis results including oversized pages, ranges, and statistics
    """
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        
        # Find all oversized pages
        oversized_pages = []
        for page_num in range(total_pages):
            page = doc[page_num]
            if is_oversized_page(page):
                oversized_pages.append(page_num + 1)  # 1-based indexing
        
        doc.close()
        
        # Group consecutive oversized pages into ranges
        ranges = []
        if oversized_pages:
            start = oversized_pages[0]
            end = start
            
            for page in oversized_pages[1:]:
                if page == end + 1:
                    # Consecutive page, extend the range
                    end = page
                else:
                    # Non-consecutive, start a new range
                    ranges.append({
                        "start": start,
                        "end": end,
                        "oversized_pages": end - start + 1,
                        "total_pages_35mm": end - start + 1 + 1  # oversized pages + 1 reference sheet
                    })
                    start = page
                    end = page
            
            # Add the final range
            ranges.append({
                "start": start,
                "end": end,
                "oversized_pages": end - start + 1,
                "total_pages_35mm": end - start + 1 + 1  # oversized pages + 1 reference sheet
            })
        
        # Calculate statistics
        total_oversized = len(oversized_pages)
        total_ranges = len(ranges)
        total_reference_sheets = total_ranges  # One reference sheet per range
        total_pages_35mm = total_oversized + total_reference_sheets
        
        # Find large ranges (exceeding 35mm capacity)
        large_ranges = [r for r in ranges if r["total_pages_35mm"] > CAPACITY_35MM]
        
        return {
            "success": True,
            "total_pages": total_pages,
            "oversized_pages": oversized_pages,
            "total_oversized": total_oversized,
            "ranges": ranges,
            "total_ranges": total_ranges,
            "total_reference_sheets": total_reference_sheets,
            "total_pages_35mm": total_pages_35mm,
            "has_oversized": total_oversized > 0,
            "has_large_ranges": len(large_ranges) > 0,
            "large_ranges": large_ranges,
            "large_ranges_count": len(large_ranges)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def scan_large_ranges(root_path: str, output_file: str = "large_ranges.json", threshold: int = CAPACITY_35MM, 
                      quick_scan: bool = False, sample_size: int = None) -> None:
    """
    Main function to scan for PDFs with large oversized ranges.
    
    Args:
        root_path: Root directory to scan (e.g., "X:\\")
        output_file: Output JSON file path
        threshold: Page count threshold for large ranges (default: 690)
        quick_scan: If True, stop after finding first PDF with large ranges
        sample_size: If set, only scan this many PDFs (for quick testing)
    """
    root = Path(root_path)
    
    if not root.exists():
        print(f"{Fore.RED}❌ Error: Directory not found: {root_path}{Style.RESET_ALL}")
        return
    
    if not root.is_dir():
        print(f"{Fore.RED}❌ Error: Path is not a directory: {root_path}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📂 Starting scan from: {root_path}{Style.RESET_ALL}")
    print(f"📐 Oversized threshold: {OVERSIZE_THRESHOLD_WIDTH/72:.1f}\" x {OVERSIZE_THRESHOLD_HEIGHT/72:.1f}\"")
    print(f"📄 Looking for ranges with more than {threshold} pages (35mm capacity)")
    if quick_scan:
        print(f"⚡ Quick scan mode: Will stop after finding first large range")
    if sample_size:
        print(f"📊 Sample mode: Will scan up to {sample_size} PDFs")
    print(f"🚫 Ignoring: folders starting with '.', System Volume Information, RECYCLE.BIN\n")
    
    # Step 1: Find all first-level folders (these are the PROJECTS)
    project_folders = find_project_folders(root)
    
    if not project_folders:
        print(f"{Fore.YELLOW}⚠ No PROJECT folders (first-level folders) found in {root_path}{Style.RESET_ALL}")
        return
    
    # Sort project folders by name for consistent processing order
    project_folders = sorted(project_folders, key=lambda p: p.name)
    
    print(f"{Fore.GREEN}✅ Found {len(project_folders)} PROJECT folder(s){Style.RESET_ALL}\n")
    
    # Step 2: Find PDF folders within each PROJECT folder and collect PDFs
    # Optimization: Collect PDFs with metadata for smarter sorting
    pdf_files_with_meta = []
    all_warnings = []
    pdf_folders_found = 0
    
    for project_folder in project_folders:
        pdf_folder, warnings = find_pdf_folder(project_folder)
        
        if warnings:
            all_warnings.extend(warnings)
        
        if pdf_folder is None:
            continue
        
        pdf_folders_found += 1
        
        # Collect PDFs directly in the PDF folder
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
                    # If we can't get file size, add with size 0
                    pdf_files_with_meta.append({
                        'path': pdf_file,
                        'size': 0,
                        'project': project_folder.name
                    })
        
        # Also check one level deeper for PDFs
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
    
    # Optimization: Sort PDFs by size (descending) - larger files more likely to have large ranges
    # This helps us find edge cases faster
    pdf_files_with_meta.sort(key=lambda x: x['size'], reverse=True)
    
    # Apply sample size limit if specified
    if sample_size and sample_size < len(pdf_files_with_meta):
        print(f"{Fore.YELLOW}📊 Limiting scan to {sample_size} largest PDFs (out of {len(pdf_files_with_meta)} total){Style.RESET_ALL}\n")
        pdf_files_with_meta = pdf_files_with_meta[:sample_size]
    
    # Extract just the paths for processing
    pdf_files = [item['path'] for item in pdf_files_with_meta]
    
    # Print warnings if any
    if all_warnings:
        print(f"{Fore.YELLOW}⚠ Warnings:{Style.RESET_ALL}")
        for warning in all_warnings:
            print(f"  {Fore.YELLOW}⚠ {warning}{Style.RESET_ALL}")
        print()
    
    if pdf_folders_found == 0:
        print(f"{Fore.YELLOW}⚠ No PDF folders found in PROJECT folders{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Found {pdf_folders_found} PDF folder(s) in {len(project_folders)} PROJECT folder(s){Style.RESET_ALL}")
    
    if not pdf_files:
        print(f"{Fore.YELLOW}⚠ No PDF files found in PDF folders{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Found {len(pdf_files)} PDF file(s) to check{Style.RESET_ALL}\n")
    
    # Step 3: Analyze PDFs for oversized pages and ranges
    pdfs_with_oversized = []
    pdfs_with_large_ranges = []
    errors = []
    found_large_range = False
    
    print(f"{Fore.CYAN}📊 Analyzing oversized pages and ranges...{Style.RESET_ALL}\n")
    
    for pdf_path in tqdm(pdf_files, desc="Scanning PDFs", unit="file"):
        # Quick scan mode: stop after finding first large range
        if quick_scan and found_large_range:
            print(f"\n{Fore.YELLOW}⚡ Quick scan: Stopping after finding large range{Style.RESET_ALL}")
            break
        
        analysis = analyze_pdf_oversized_pages(pdf_path)
        
        if not analysis["success"]:
            errors.append({
                "path": str(pdf_path),
                "filename": pdf_path.name,
                "error": analysis.get("error", "Unknown error")
            })
            continue
        
        # Skip PDFs without oversized pages
        if not analysis["has_oversized"]:
            continue
        
        # Calculate project folder and PDF folder paths
        try:
            path_depth_from_root = len(pdf_path.relative_to(root).parts)
            
            if path_depth_from_root == 3:
                # Direct: root/PROJECT/PDF/file.pdf
                pdf_folder = pdf_path.parent
                project_folder = pdf_path.parent.parent
                relative_depth = "direct"
            elif path_depth_from_root == 4:
                # One level deeper: root/PROJECT/PDF/SUBFOLDER/file.pdf
                pdf_folder = pdf_path.parent.parent
                project_folder = pdf_path.parent.parent.parent
                relative_depth = "one_level_deeper"
            else:
                # Fallback: use parent relationships
                pdf_folder = pdf_path.parent
                project_folder = pdf_path.parent.parent
                relative_depth = "unknown"
        except ValueError:
            # Paths are not relative (different drives, etc.) - use parent relationships
            pdf_folder = pdf_path.parent
            project_folder = pdf_path.parent.parent
            relative_depth = "unknown"
        
        file_size = pdf_path.stat().st_size
        
        pdf_info = {
            "path": str(pdf_path),
            "filename": pdf_path.name,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "project_folder": str(project_folder),
            "project_name": project_folder.name,
            "pdf_folder": str(pdf_folder),
            "relative_depth": relative_depth,
            "total_pages": analysis["total_pages"],
            "total_oversized": analysis["total_oversized"],
            "total_ranges": analysis["total_ranges"],
            "total_reference_sheets": analysis["total_reference_sheets"],
            "total_pages_35mm": analysis["total_pages_35mm"],
            "ranges": analysis["ranges"],
            "large_ranges": analysis["large_ranges"],
            "large_ranges_count": analysis["large_ranges_count"]
        }
        
        pdfs_with_oversized.append(pdf_info)
        
        # Check if this PDF has large ranges
        if analysis["has_large_ranges"]:
            pdfs_with_large_ranges.append(pdf_info)
            found_large_range = True
    
    # Step 4: Generate statistics
    total_pdfs_with_oversized = len(pdfs_with_oversized)
    total_pdfs_with_large_ranges = len(pdfs_with_large_ranges)
    
    # Aggregate statistics
    total_oversized_pages = sum(p["total_oversized"] for p in pdfs_with_oversized)
    total_ranges = sum(p["total_ranges"] for p in pdfs_with_oversized)
    total_large_ranges = sum(p["large_ranges_count"] for p in pdfs_with_oversized)
    
    # Range size distribution
    all_ranges = []
    for pdf in pdfs_with_oversized:
        all_ranges.extend(pdf["ranges"])
    
    range_size_distribution = {
        "0-100": 0,
        "101-200": 0,
        "201-300": 0,
        "301-400": 0,
        "401-500": 0,
        "501-600": 0,
        "601-690": 0,
        "691+": 0  # Large ranges
    }
    
    for r in all_ranges:
        pages = r["total_pages_35mm"]
        if pages <= 100:
            range_size_distribution["0-100"] += 1
        elif pages <= 200:
            range_size_distribution["101-200"] += 1
        elif pages <= 300:
            range_size_distribution["201-300"] += 1
        elif pages <= 400:
            range_size_distribution["301-400"] += 1
        elif pages <= 500:
            range_size_distribution["401-500"] += 1
        elif pages <= 600:
            range_size_distribution["501-600"] += 1
        elif pages <= 690:
            range_size_distribution["601-690"] += 1
        else:
            range_size_distribution["691+"] += 1
    
    # Step 5: Export results to JSON
    results = {
        "scan_date": datetime.now().isoformat(),
        "root_path": str(root_path),
        "threshold_35mm": threshold,
        "oversize_threshold_inches": {
            "width": round(OVERSIZE_THRESHOLD_WIDTH / 72, 2),
            "height": round(OVERSIZE_THRESHOLD_HEIGHT / 72, 2)
        },
        "statistics": {
            "total_pdfs_scanned": len(pdf_files),
            "pdfs_with_oversized": total_pdfs_with_oversized,
            "pdfs_with_large_ranges": total_pdfs_with_large_ranges,
            "total_oversized_pages": total_oversized_pages,
            "total_ranges": total_ranges,
            "total_large_ranges": total_large_ranges,
            "range_size_distribution": range_size_distribution,
            "errors_count": len(errors)
        },
        "warnings": all_warnings,
        "pdfs_with_large_ranges": sorted(
            pdfs_with_large_ranges, 
            key=lambda x: x["large_ranges_count"], 
            reverse=True
        ),
        "pdfs_with_oversized": sorted(
            pdfs_with_oversized,
            key=lambda x: x["total_pages_35mm"],
            reverse=True
        ),
        "errors": errors
    }
    
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Scan Complete!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"📊 Total PDFs scanned: {len(pdf_files)}")
    print(f"📐 PDFs with oversized pages: {Fore.YELLOW}{total_pdfs_with_oversized}{Style.RESET_ALL}")
    print(f"📄 Total oversized pages found: {total_oversized_pages}")
    print(f"📋 Total ranges found: {total_ranges}")
    print(f"⚠️  Large ranges (>{threshold} pages): {Fore.RED}{total_large_ranges}{Style.RESET_ALL}")
    print(f"🚨 PDFs with large ranges: {Fore.RED}{total_pdfs_with_large_ranges}{Style.RESET_ALL}")
    print(f"❌ Errors: {len(errors)}")
    print(f"💾 Results saved to: {output_path.absolute()}")
    
    # Range size distribution
    print(f"\n{Fore.CYAN}Range Size Distribution (35mm pages including reference sheet):{Style.RESET_ALL}")
    for size_range, count in range_size_distribution.items():
        if size_range == "691+":
            print(f"  {Fore.RED}{size_range:>10}: {count:>6} ranges (EXCEEDS CAPACITY){Style.RESET_ALL}")
        else:
            print(f"  {size_range:>10}: {count:>6} ranges")
    
    if pdfs_with_large_ranges:
        print(f"\n{Fore.RED}⚠️  PDFs with Large Ranges (>{threshold} pages):{Style.RESET_ALL}")
        for i, pdf in enumerate(pdfs_with_large_ranges[:10], 1):
            print(f"  {i}. {pdf['filename']}")
            print(f"     Project: {pdf['project_name']}")
            print(f"     Large ranges: {pdf['large_ranges_count']}")
            for lr in pdf['large_ranges']:
                print(f"       - Pages {lr['start']}-{lr['end']}: {lr['total_pages_35mm']} pages on 35mm")
        
        if len(pdfs_with_large_ranges) > 10:
            print(f"     ... and {len(pdfs_with_large_ranges) - 10} more (see JSON output)")
    else:
        print(f"\n{Fore.GREEN}✅ No large ranges found! All ranges fit within 35mm capacity.{Style.RESET_ALL}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Scan for PDFs with large oversized ranges in PROJECT/PDF folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python large_range_scanner.py X:\\
  python large_range_scanner.py X:\\ --threshold 690 --output results.json
        """
    )
    
    parser.add_argument(
        "root_path",
        type=str,
        help="Root directory to scan (e.g., X:\\)"
    )
    
    parser.add_argument(
        "--threshold",
        type=int,
        default=CAPACITY_35MM,
        help=f"Range size threshold in 35mm pages (default: {CAPACITY_35MM})"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="large_ranges.json",
        help="Output JSON file path (default: large_ranges.json)"
    )
    
    args = parser.parse_args()
    
    scan_large_ranges(args.root_path, args.output, args.threshold)


if __name__ == "__main__":
    main()

