#!/usr/bin/env python3
"""
PDF Corruption Scanner using qpdf
Recursively scans a directory for PDF files, checks if they're readable using qpdf --check,
and exports a list of corrupt files to a JSON file with progress tracking.

Requires qpdf to be installed and available in PATH.
"""

import os
import json
import argparse
import subprocess
import shutil
import re
import gc
from pathlib import Path
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows color support
colorama.init()


def check_qpdf_available() -> bool:
    """Check if qpdf is available in the system PATH."""
    return shutil.which("qpdf") is not None


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
    Only scans folders that contain 'pdf' in name or have 8-digit numbers.
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


def check_pdf_with_qpdf(pdf_path: Path) -> Dict[str, Any]:
    """
    Check if a PDF file is corrupt using qpdf --check.
    Returns a dictionary with corruption status and error details.
    
    qpdf exit codes:
    0 - no errors or warnings (file is good)
    2 - errors found, file not processed (file is corrupt)
    3 - warnings found without errors (file has issues but readable)
    """
    result = {
        "path": str(pdf_path),
        "filename": pdf_path.name,
        "is_corrupt": False,
        "has_warnings": False,
        "error": None,
        "return_code": None,
        "status": "unknown"
    }
    
    try:
        # Run qpdf --check on the file
        cmd = ["qpdf", "--check", str(pdf_path)]
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout per file
        )
        
        result["return_code"] = process.returncode
        # Note: We don't store qpdf output to save memory - only the return code is used for analysis
        
        # Interpret qpdf exit codes
        if process.returncode == 0:
            # No errors or warnings - file is perfect
            result["status"] = "good"
            result["error"] = None
        elif process.returncode == 2:
            # Errors found - file is corrupt
            result["is_corrupt"] = True
            result["status"] = "corrupt"
            result["error"] = "qpdf found errors - file is corrupt"
        elif process.returncode == 3:
            # Warnings only - file has issues but is readable
            result["has_warnings"] = True
            result["status"] = "warnings"
            result["error"] = "qpdf found warnings - file has issues but may be readable"
        else:
            # Unexpected exit code
            result["is_corrupt"] = True
            result["status"] = "unknown_error"
            result["error"] = f"qpdf returned unexpected exit code {process.returncode}"
        
        return result
        
    except subprocess.TimeoutExpired:
        result["is_corrupt"] = True
        result["error"] = "qpdf check timed out (30s)"
        result["return_code"] = -1
        result["status"] = "timeout"
        return result
    except FileNotFoundError:
        result["is_corrupt"] = True
        result["error"] = "qpdf command not found"
        result["return_code"] = -2
        result["status"] = "qpdf_missing"
        return result
    except Exception as e:
        result["is_corrupt"] = True
        result["error"] = f"Unexpected error running qpdf: {str(e)}"
        result["return_code"] = -3
        result["status"] = "exception"
        return result


def scan_pdfs_qpdf(root_path: str, output_file: str = "corrupt_pdfs_qpdf.json", use_cache: bool = True, cache_file: str = "pdf_paths_cache.json") -> None:
    """
    Main function to scan PDFs using qpdf and export corrupt files list.
    """
    # Check if qpdf is available
    if not check_qpdf_available():
        print("Error: qpdf is not installed or not available in PATH.")
        print("Please install qpdf first:")
        print("  - Windows: Download from https://qpdf.sourceforge.io/")
        print("  - macOS: brew install qpdf")
        print("  - Linux: sudo apt-get install qpdf (Ubuntu/Debian) or sudo yum install qpdf (RHEL/CentOS)")
        return
    
    print(f"Scanning for PDF files in: {root_path}")
    print("Using qpdf --check for validation")
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
    
    # Counters for summary (instead of storing all results in memory)
    corrupt_count = 0
    warning_count = 0
    healthy_count = 0
    
    # Lists for final summary display (only store problematic files)
    corrupt_files_summary = []
    warning_files_summary = []
    
    # Open output file for streaming results
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write JSON header
            f.write('{\n')
            f.write('  "scan_summary": {\n')
            f.write(f'    "total_files": {len(pdf_files)},\n')
            f.write(f'    "scan_path": "{root_path}",\n')
            f.write('    "validation_method": "qpdf --check"\n')
            f.write('  },\n')
            f.write('  "results": [\n')
            
            # Create progress bar with sticky positioning
            with tqdm(total=len(pdf_files), 
                      desc="Checking PDFs", 
                      unit="file",
                      position=0,
                      leave=True,
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                for i, pdf_file in enumerate(pdf_files):
                    try:
                        # Update progress bar description with current file
                        pbar.set_description(f"qpdf check: {pdf_file.name[:25]}...")
                        
                        result = check_pdf_with_qpdf(pdf_file)
                        
                        # Write result immediately to file
                        if i > 0:
                            f.write(',\n')
                        f.write('    ')
                        json.dump(result, f, ensure_ascii=False)
                        f.flush()  # Ensure data is written immediately
                        
                        # Update counters and summary lists
                        clean_path = str(pdf_file).replace(chr(92), '/')
                        if result["is_corrupt"]:
                            corrupt_count += 1
                            corrupt_files_summary.append({"filename": result["filename"], "path": clean_path})
                            pbar.write(f"{Fore.RED}NG: {clean_path}{Style.RESET_ALL}")
                        elif result["has_warnings"]:
                            warning_count += 1
                            warning_files_summary.append({"filename": result["filename"], "path": clean_path})
                            pbar.write(f"{Fore.YELLOW}WN: {clean_path}{Style.RESET_ALL}")
                        else:
                            healthy_count += 1
                            pbar.write(f"{Fore.GREEN}OK: {clean_path}{Style.RESET_ALL}")
                        
                    except Exception as e:
                        # Handle unexpected errors
                        error_result = {
                            "path": str(pdf_file),
                            "filename": pdf_file.name,
                            "is_corrupt": True,
                            "error": f"Unexpected error: {str(e)}",
                            "return_code": -999,
                            "status": "exception"
                        }
                        
                        # Write error result to file
                        if i > 0:
                            f.write(',\n')
                        f.write('    ')
                        json.dump(error_result, f, ensure_ascii=False)
                        f.flush()
                        
                        corrupt_count += 1
                        clean_path = str(pdf_file).replace(chr(92), '/')
                        corrupt_files_summary.append({"filename": pdf_file.name, "path": clean_path})
                        pbar.write(f"{Fore.RED}NG: {clean_path} - {str(e)}{Style.RESET_ALL}")
                    
                    # Periodic garbage collection to manage memory
                    if (i + 1) % 1000 == 0:
                        gc.collect()
                    
                    pbar.update(1)
            
            # Close JSON array and file
            f.write('\n  ]\n')
            f.write('}\n')
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        return
    
    print(f"\nResults exported to: {output_file}")
    
    # Print summary
    print(f"\n{Style.BRIGHT}Scan Summary:{Style.RESET_ALL}")
    print(f"Total PDF files: {len(pdf_files):,}")
    print(f"{Fore.GREEN}OK files (exit code 0): {healthy_count:,}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}WN files (exit code 3): {warning_count:,}{Style.RESET_ALL}")
    print(f"{Fore.RED}NG files (exit code 2): {corrupt_count:,}{Style.RESET_ALL}")
    
    if corrupt_files_summary:
        print(f"\n{Fore.RED}NG files found:{Style.RESET_ALL}")
        for corrupt_file in corrupt_files_summary:
            print(f"  {Fore.RED}NG: {corrupt_file['filename']} ({corrupt_file['path']}){Style.RESET_ALL}")
    
    if warning_files_summary and len(warning_files_summary) <= 10:
        print(f"\n{Fore.YELLOW}Sample WN files:{Style.RESET_ALL}")
        for warning_file in warning_files_summary[:10]:
            print(f"  {Fore.YELLOW}WN: {warning_file['filename']} ({warning_file['path']}){Style.RESET_ALL}")
    elif warning_files_summary:
        print(f"\n{Fore.YELLOW}{len(warning_files_summary):,} WN files found{Style.RESET_ALL}")


def test_qpdf_installation() -> None:
    """Test qpdf installation and show version info."""
    if not check_qpdf_available():
        print("qpdf is not installed or not available in PATH.")
        return
    
    try:
        # Get qpdf version
        result = subprocess.run(["qpdf", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"qpdf is available: {result.stdout.strip()}")
        else:
            print("qpdf is available but version check failed")
    except Exception as e:
        print(f"Error checking qpdf version: {e}")


def main():
    """Command line interface for the PDF scanner."""
    parser = argparse.ArgumentParser(description="Scan directory for corrupt PDF files using qpdf")
    parser.add_argument("path", nargs='?', default="X:", 
                       help="Root directory to scan (default: X:)")
    parser.add_argument("-o", "--output", default="corrupt_pdfs_qpdf.json",
                       help="Output JSON file (default: corrupt_pdfs_qpdf.json)")
    parser.add_argument("-c", "--cache", default="pdf_paths_cache.json",
                       help="PDF paths cache file (default: pdf_paths_cache.json)")
    parser.add_argument("--no-cache", action="store_true",
                       help="Skip cache and scan directory directly")
    parser.add_argument("--test", action="store_true",
                       help="Test qpdf installation and exit")
    
    args = parser.parse_args()
    
    if args.test:
        test_qpdf_installation()
        return
    
    use_cache = not args.no_cache
    scan_pdfs_qpdf(args.path, args.output, use_cache, args.cache)


if __name__ == "__main__":
    main()

