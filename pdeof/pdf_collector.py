#!/usr/bin/env python3
"""
PDF Path Collector
Recursively scans a directory for PDF files in qualifying folders and exports paths to JSON.
Only scans folders that contain 'pdf' in name or have 8-digit numbers.

This creates a cached file that can be used by the main scanner to avoid re-scanning the filesystem.
"""

import os
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from datetime import datetime


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


def collect_pdf_paths(root_path: str) -> List[Dict[str, Any]]:
    """
    Recursively find all PDF files in qualifying folders.
    Returns list of dictionaries with file info.
    """
    root = Path(root_path)
    
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")
    
    pdf_files = []
    scanned_folders = set()
    skipped_folders = set()
    
    print(f"Scanning directory structure in: {root_path}")
    print("Collecting PDFs where parent folder contains 'pdf' or is exactly 8 digits...")
    
    # Collect PDFs based on their direct parent folder
    print("Scanning for PDF files...")
    
    for current_path in root.rglob("*.pdf"):
        if current_path.is_file():
            if should_include_pdf(current_path):
                try:
                    stat = current_path.stat()
                    # Use forward slashes for cleaner JSON storage
                    full_path = str(current_path).replace('\\', '/')
                    if full_path.startswith('X:') and not full_path.startswith('X:/'):
                        full_path = full_path.replace('X:', 'X:/', 1)
                    
                    parent_path = str(current_path.parent).replace('\\', '/')
                    if parent_path.startswith('X:') and not parent_path.startswith('X:/'):
                        parent_path = parent_path.replace('X:', 'X:/', 1)
                    
                    pdf_info = {
                        "path": full_path,
                        "filename": current_path.name,
                        "size_bytes": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "parent_folder": current_path.parent.name,
                        "parent_folder_path": parent_path,
                        "relative_path": str(current_path.relative_to(root)).replace('\\', '/')
                    }
                    pdf_files.append(pdf_info)
                except (OSError, ValueError) as e:
                    # Handle files that can't be accessed
                    # Use forward slashes for cleaner JSON storage
                    full_path = str(current_path).replace('\\', '/')
                    if full_path.startswith('X:') and not full_path.startswith('X:/'):
                        full_path = full_path.replace('X:', 'X:/', 1)
                    
                    parent_path = str(current_path.parent).replace('\\', '/')
                    if parent_path.startswith('X:') and not parent_path.startswith('X:/'):
                        parent_path = parent_path.replace('X:', 'X:/', 1)
                    
                    pdf_info = {
                        "path": full_path,
                        "filename": current_path.name,
                        "size_bytes": -1,
                        "modified_time": None,
                        "parent_folder": current_path.parent.name,
                        "parent_folder_path": parent_path,
                        "relative_path": str(current_path.relative_to(root)).replace('\\', '/'),
                        "access_error": str(e)
                    }
                    pdf_files.append(pdf_info)
    
    return pdf_files


def export_pdf_paths(root_path: str, output_file: str = "pdf_paths_cache.json") -> None:
    """
    Main function to collect PDF paths and export to JSON cache file.
    """
    print(f"PDF Path Collector - Starting scan of: {root_path}")
    print("=" * 60)
    
    try:
        pdf_files = collect_pdf_paths(root_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    if not pdf_files:
        print("No PDF files found in qualifying folders.")
        return
    
    # Calculate total size
    total_size = sum(pdf['size_bytes'] for pdf in pdf_files if pdf['size_bytes'] > 0)
    total_size_mb = total_size / (1024 * 1024)
    
    # Create output data
    output_data = {
        "collection_info": {
            "scan_timestamp": datetime.now().isoformat(),
            "root_path": root_path,
            "total_pdf_files": len(pdf_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size_mb, 2),
            "filter_criteria": [
                "PDFs where parent folder contains 'pdf' in name (case insensitive)",
                "PDFs where parent folder is exactly 8 digits (e.g., 00000001, 20000001)",
                "EXCLUDES: RECYCLE.BIN, $RECYCLE.BIN, .management folders"
            ]
        },
        "pdf_files": pdf_files
    }
    
    # Export to JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ PDF paths exported to: {output_file}")
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return
    
    # Print summary
    print(f"\n📊 Collection Summary:")
    print(f"   Total PDF files found: {len(pdf_files):,}")
    print(f"   Total size: {total_size_mb:.2f} MB ({total_size:,} bytes)")
    print(f"   Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show some example files
    print(f"\n📁 Sample files found:")
    for i, pdf in enumerate(pdf_files[:5]):
        # Convert backslashes to forward slashes for clean display
        clean_path = pdf['path'].replace('\\', '/')
        
        size_mb = pdf['size_bytes'] / (1024 * 1024) if pdf['size_bytes'] > 0 else 0
        print(f"   {i+1}. {pdf['filename']} ({size_mb:.2f} MB)")
        print(f"      {clean_path}")
    
    if len(pdf_files) > 5:
        print(f"   ... and {len(pdf_files) - 5:,} more files")


def load_pdf_cache(cache_file: str = "pdf_paths_cache.json") -> Dict[str, Any]:
    """
    Load PDF paths from cache file.
    Returns the cache data or None if file doesn't exist/is invalid.
    """
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Cache file error: {e}")
        return None


def show_cache_info(cache_file: str = "pdf_paths_cache.json") -> None:
    """Show information about the cached PDF paths."""
    cache_data = load_pdf_cache(cache_file)
    
    if not cache_data:
        print(f"No valid cache file found: {cache_file}")
        return
    
    info = cache_data.get('collection_info', {})
    pdf_files = cache_data.get('pdf_files', [])
    
    print(f"📋 Cache File Information: {cache_file}")
    print(f"   Created: {info.get('scan_timestamp', 'Unknown')}")
    print(f"   Root path: {info.get('root_path', 'Unknown')}")
    print(f"   PDF files: {info.get('total_pdf_files', len(pdf_files)):,}")
    print(f"   Total size: {info.get('total_size_mb', 0):.2f} MB")
    
    if pdf_files:
        print(f"\n📁 First few files:")
        for i, pdf in enumerate(pdf_files[:3]):
            clean_path = pdf['path'].replace(chr(92), '/')
            print(f"   {i+1}. {pdf['filename']}")
            print(f"      {clean_path}")


def main():
    """Command line interface for the PDF path collector."""
    parser = argparse.ArgumentParser(description="Collect PDF file paths and cache them")
    parser.add_argument("path", nargs='?', default="X:", 
                       help="Root directory to scan (default: X:)")
    parser.add_argument("-o", "--output", default="pdf_paths_cache.json",
                       help="Output JSON cache file (default: pdf_paths_cache.json)")
    parser.add_argument("--info", action="store_true",
                       help="Show information about existing cache file")
    
    args = parser.parse_args()
    
    if args.info:
        show_cache_info(args.output)
        return
    
    export_pdf_paths(args.path, args.output)


if __name__ == "__main__":
    main()
