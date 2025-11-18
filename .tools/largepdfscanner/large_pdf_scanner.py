#!/usr/bin/env python3
"""
Large PDF Scanner
Scans X:\ drive where first-level folders are PROJECTS, finds PDF folders within them,
checks PDFs for page counts exceeding 2900 pages, and exports results to JSON.

Ignores folders starting with "." (like .output)
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


def get_pdf_page_count(pdf_path: Path) -> int:
    """
    Get the page count of a PDF file using PyMuPDF.
    Returns -1 if there's an error reading the PDF.
    """
    try:
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as e:
        print(f"\n{Fore.YELLOW}⚠ Warning: Could not read {pdf_path}: {e}{Style.RESET_ALL}")
        return -1


def scan_large_pdfs(root_path: str, page_threshold: int = 2900, output_file: str = "large_pdfs.json") -> None:
    """
    Main function to scan for large PDFs.
    
    Args:
        root_path: Root directory to scan (e.g., "X:\\")
        page_threshold: Minimum page count to include in results (default: 2900)
        output_file: Output JSON file path
    """
    root = Path(root_path)
    
    if not root.exists():
        print(f"{Fore.RED}❌ Error: Directory not found: {root_path}{Style.RESET_ALL}")
        return
    
    if not root.is_dir():
        print(f"{Fore.RED}❌ Error: Path is not a directory: {root_path}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📂 Starting scan from: {root_path}{Style.RESET_ALL}")
    print(f"📄 Looking for PDFs with more than {page_threshold} pages")
    print(f"🚫 Ignoring: folders starting with '.', System Volume Information, RECYCLE.BIN\n")
    
    # Step 1: Find all first-level folders (these are the PROJECTS)
    project_folders = find_project_folders(root)
    
    if not project_folders:
        print(f"{Fore.YELLOW}⚠ No PROJECT folders (first-level folders) found in {root_path}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Found {len(project_folders)} PROJECT folder(s){Style.RESET_ALL}\n")
    
    # Step 2: Find PDF folders within each PROJECT folder and collect PDFs
    pdf_files = []
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
                pdf_files.append(pdf_file)
        
        # Also check one level deeper for PDFs
        for subfolder in pdf_folder.iterdir():
            if not subfolder.is_dir():
                continue
            if should_skip_folder(subfolder):
                continue
            
            for pdf_file in subfolder.glob("*.pdf"):
                if pdf_file.is_file():
                    pdf_files.append(pdf_file)
    
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
    
    # Step 4: Check page counts and collect large PDFs
    large_pdfs = []
    errors = []
    
    print(f"{Fore.CYAN}📊 Checking page counts...{Style.RESET_ALL}\n")
    
    for pdf_path in tqdm(pdf_files, desc="Scanning PDFs", unit="file"):
        page_count = get_pdf_page_count(pdf_path)
        
        if page_count == -1:
            errors.append({
                "path": str(pdf_path),
                "filename": pdf_path.name,
                "error": "Could not read PDF"
            })
            continue
        
        if page_count > page_threshold:
            file_size = pdf_path.stat().st_size
            
            # Calculate project folder and PDF folder paths
            # PDFs can be: PROJECT/PDF/file.pdf or PROJECT/PDF/SUBFOLDER/file.pdf
            # If PDF is directly in PDF folder: parent = PDF folder, parent.parent = PROJECT folder
            # If PDF is one level deeper: parent = subfolder, parent.parent = PDF folder, parent.parent.parent = PROJECT folder
            
            # Check if PDF is directly in PDF folder (by checking depth relative to root)
            # We'll determine this by checking the depth relative to root
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
            
            large_pdfs.append({
                "path": str(pdf_path),
                "filename": pdf_path.name,
                "page_count": page_count,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "project_folder": str(project_folder),
                "pdf_folder": str(pdf_folder),
                "relative_depth": relative_depth
            })
    
    # Step 5: Export results to JSON
    results = {
        "scan_date": datetime.now().isoformat(),
        "root_path": str(root_path),
        "page_threshold": page_threshold,
        "total_pdfs_scanned": len(pdf_files),
        "large_pdfs_count": len(large_pdfs),
        "errors_count": len(errors),
        "warnings": all_warnings,
        "large_pdfs": sorted(large_pdfs, key=lambda x: x["page_count"], reverse=True),
        "errors": errors
    }
    
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Scan Complete!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"📊 Total PDFs scanned: {len(pdf_files)}")
    print(f"📄 Large PDFs found (> {page_threshold} pages): {Fore.YELLOW}{len(large_pdfs)}{Style.RESET_ALL}")
    print(f"❌ Errors: {len(errors)}")
    print(f"💾 Results saved to: {output_path.absolute()}")
    
    if large_pdfs:
        print(f"\n{Fore.YELLOW}Top 5 largest PDFs:{Style.RESET_ALL}")
        for i, pdf in enumerate(large_pdfs[:5], 1):
            print(f"  {i}. {pdf['filename']} - {pdf['page_count']} pages ({pdf['file_size_mb']} MB)")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Scan for large PDFs in PROJECT/PDF folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python large_pdf_scanner.py X:\\
  python large_pdf_scanner.py X:\\ --threshold 5000 --output results.json
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
        default=2900,
        help="Page count threshold (default: 2900)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="large_pdfs.json",
        help="Output JSON file path (default: large_pdfs.json)"
    )
    
    args = parser.parse_args()
    
    scan_large_pdfs(args.root_path, args.threshold, args.output)


if __name__ == "__main__":
    main()

