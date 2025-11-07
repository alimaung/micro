#!/usr/bin/env python3
"""
PDF Corruption Scanner
Recursively scans a directory for PDF files, checks if they're readable,
and exports a list of corrupt files to a JSON file with progress tracking.
"""

import os
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import PyPDF2
import fitz  # PyMuPDF as fallback


def is_excluded_folder(folder_path: Path) -> bool:
    """
    Check if a folder should be excluded from scanning.
    Excludes:
    - RECYCLE.BIN and $RECYCLE.BIN folders
    - .management folders
    - Any folder inside excluded folders
    """
    folder_str = str(folder_path).upper()
    
    # Check for recycle bin patterns
    if 'RECYCLE.BIN' in folder_str or '$RECYCLE.BIN' in folder_str:
        return True
    
    # Check for .management folders
    if '.management' in str(folder_path).lower():
        return True
    
    # Check if any parent folder is excluded
    for parent in folder_path.parents:
        parent_str = str(parent).upper()
        if 'RECYCLE.BIN' in parent_str or '$RECYCLE.BIN' in parent_str:
            return True
        if '.management' in str(parent).lower():
            return True
    
    return False


def has_exact_8_digits(folder_name: str) -> bool:
    """
    Check if folder name is exactly 8 digits (like 00000001, 20000001).
    """
    return bool(re.match(r'^\d{8}$', folder_name))


def should_include_pdf(pdf_path: Path) -> bool:
    """
    Check if a PDF should be included based on its direct parent folder:
    - Parent folder contains 'pdf' in name (case insensitive), OR
    - Parent folder is exactly 8 digits (like 00000001, 20000001)
    - NOT in excluded folders (RECYCLE.BIN, .management)
    """
    # First check if PDF or any parent is in excluded folders
    if is_excluded_folder(pdf_path) or is_excluded_folder(pdf_path.parent):
        return False
    
    # Check the direct parent folder
    parent_folder = pdf_path.parent
    parent_name = parent_folder.name.lower()
    
    # Check if parent folder contains 'pdf'
    if 'pdf' in parent_name:
        return True
    
    # Check if parent folder is exactly 8 digits
    if has_exact_8_digits(parent_folder.name):
        return True
    
    return False


def load_pdf_cache(cache_file: str = "pdf_paths_cache.json") -> List[Path]:
    """
    Load PDF paths from cache file.
    Returns list of Path objects or None if cache is invalid.
    """
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pdf_files = []
        for pdf_info in data.get('pdf_files', []):
            pdf_path = Path(pdf_info['path'])
            # Verify file still exists
            if pdf_path.exists():
                pdf_files.append(pdf_path)
        
        return pdf_files
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Cache file error: {e}")
        return None


def find_pdf_files(root_path: str, use_cache: bool = True, cache_file: str = "pdf_paths_cache.json") -> List[Path]:
    """
    Find PDF files either from cache or by scanning directory.
    Only scans PDFs where parent folder contains 'pdf' or is exactly 8 digits.
    """
    # Try to use cache first
    if use_cache:
        print(f"Attempting to load PDF paths from cache: {cache_file}")
        cached_files = load_pdf_cache(cache_file)
        if cached_files is not None:
            print(f"✅ Loaded {len(cached_files)} PDF paths from cache")
            return cached_files
        else:
            print("❌ Cache not available, falling back to directory scan")
    
    # Fallback to directory scanning
    root = Path(root_path)
    
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")
    
    print("🔍 Scanning directory structure...")
    pdf_files = []
    
    # Walk through directory tree looking for PDFs
    for current_path in root.rglob("*.pdf"):
        if current_path.is_file():
            if should_include_pdf(current_path):
                pdf_files.append(current_path)
    
    return pdf_files


def check_pdf_corruption(pdf_path: Path) -> Dict[str, Any]:
    """
    Check if a PDF file is corrupt by attempting to read it.
    Returns a dictionary with corruption status and error details.
    """
    result = {
        "path": str(pdf_path),
        "filename": pdf_path.name,
        "is_corrupt": False,
        "error": None,
        "method_used": None
    }
    
    # First try with PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Try to access the first page to ensure it's readable
            if len(reader.pages) > 0:
                _ = reader.pages[0]
            result["method_used"] = "PyPDF2"
            return result
    except Exception as e:
        # Try with PyMuPDF as fallback
        try:
            doc = fitz.open(str(pdf_path))
            # Try to access the first page
            if doc.page_count > 0:
                _ = doc[0]
            doc.close()
            result["method_used"] = "PyMuPDF"
            return result
        except Exception as e2:
            result["is_corrupt"] = True
            result["error"] = f"PyPDF2: {str(e)}, PyMuPDF: {str(e2)}"
            result["method_used"] = "both_failed"
            return result


def scan_pdfs(root_path: str, output_file: str = "corrupt_pdfs.json", use_cache: bool = True, cache_file: str = "pdf_paths_cache.json") -> None:
    """
    Main function to scan PDFs and export corrupt files list.
    """
    print(f"Scanning for PDF files in: {root_path}")
    print("Using PyPDF2 and PyMuPDF for validation")
    print("Only scanning PDFs where parent folder contains 'pdf' or is exactly 8 digits")
    print("Excluding: RECYCLE.BIN, $RECYCLE.BIN, .management folders")
    
    # Find all PDF files
    try:
        pdf_files = find_pdf_files(root_path, use_cache, cache_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    if not pdf_files:
        print("No PDF files found in the specified directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to check")
    
    corrupt_files = []
    processed_files = []
    
    # Create progress bar with sticky positioning
    with tqdm(total=len(pdf_files), 
              desc="Checking PDFs", 
              unit="file",
              position=0,
              leave=True,
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        
        for pdf_file in pdf_files:
            try:
                # Update progress bar description with current file
                pbar.set_description(f"Checking: {pdf_file.name[:30]}...")
                
                result = check_pdf_corruption(pdf_file)
                processed_files.append(result)
                
                if result["is_corrupt"]:
                    corrupt_files.append(result)
                    pbar.write(f"CORRUPT: {str(pdf_file).replace(chr(92), '/')} - {result['error']}")
                else:
                    pbar.write(f"OK: {str(pdf_file).replace(chr(92), '/')}")
                
            except Exception as e:
                # Handle unexpected errors
                error_result = {
                    "path": str(pdf_file),
                    "filename": pdf_file.name,
                    "is_corrupt": True,
                    "error": f"Unexpected error: {str(e)}",
                    "method_used": "error"
                }
                corrupt_files.append(error_result)
                processed_files.append(error_result)
                pbar.write(f"ERROR: {str(pdf_file).replace(chr(92), '/')} - {str(e)}")
            
            pbar.update(1)
    
    # Export results to JSON
    output_data = {
        "scan_summary": {
            "total_files": len(pdf_files),
            "corrupt_files": len(corrupt_files),
            "healthy_files": len(pdf_files) - len(corrupt_files),
            "scan_path": root_path,
            "validation_method": "PyPDF2 + PyMuPDF"
        },
        "corrupt_files": corrupt_files,
        "all_files": processed_files
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults exported to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return
    
    # Print summary
    print(f"\nScan Summary:")
    print(f"Total PDF files: {len(pdf_files)}")
    print(f"Corrupt files: {len(corrupt_files)}")
    print(f"Healthy files: {len(pdf_files) - len(corrupt_files)}")
    
    if corrupt_files:
        print(f"\nCorrupt files found:")
        for corrupt_file in corrupt_files:
            clean_path = corrupt_file['path'].replace('\\', '/')
            print(f"  - {corrupt_file['filename']} ({clean_path})")
            if corrupt_file.get('method_used'):
                print(f"    Method: {corrupt_file['method_used']}")


def main():
    """Command line interface for the PDF scanner."""
    parser = argparse.ArgumentParser(description="Scan directory for corrupt PDF files using PyPDF2 + PyMuPDF")
    parser.add_argument("path", nargs='?', default="X:", 
                       help="Root directory to scan (default: X:)")
    parser.add_argument("-o", "--output", default="corrupt_pdfs.json",
                       help="Output JSON file (default: corrupt_pdfs.json)")
    parser.add_argument("-c", "--cache", default="pdf_paths_cache.json",
                       help="PDF paths cache file (default: pdf_paths_cache.json)")
    parser.add_argument("--no-cache", action="store_true",
                       help="Skip cache and scan directory directly")
    
    args = parser.parse_args()
    
    use_cache = not args.no_cache
    scan_pdfs(args.path, args.output, use_cache, args.cache)


if __name__ == "__main__":
    main()

