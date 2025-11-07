#!/usr/bin/env python3
"""
Simple test script for the microfilm comparison tool.
Uses the sample PDFs in the test directory.
"""

import os
import sys
from pathlib import Path

# Add current directory to path so we can import compare_documents
sys.path.insert(0, str(Path(__file__).parent))

try:
    from compare_documents import DocumentComparator
except ImportError as e:
    print(f"Error importing compare_documents: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Run a simple test comparison."""
    
    # Define paths
    script_dir = Path(__file__).parent
    test_dir = script_dir / "test"
    orig_pdf = test_dir / "orig" / "1427004500479387.pdf"
    scan_pdf = test_dir / "scan" / "1427004500479387_SCAN_BK.pdf"
    
    # Check if test files exist
    if not orig_pdf.exists():
        print(f"Original PDF not found: {orig_pdf}")
        return False
    
    if not scan_pdf.exists():
        print(f"Scan PDF not found: {scan_pdf}")
        return False
    
    print("Running microfilm quality comparison test...")
    print(f"Original: {orig_pdf}")
    print(f"Scan: {scan_pdf}")
    print("-" * 50)
    
    try:
        # Create comparator with test output directory
        output_dir = script_dir / "test_results"
        comparator = DocumentComparator(
            dpi=200,  # Lower DPI for faster testing
            output_dir=str(output_dir),
            white_threshold=0.9999,  # Detect pages that are 99.99% white
            white_pixel_threshold=254  # Very strict white detection
        )
        
        # Run comparison
        report = comparator.compare_documents(str(orig_pdf), str(scan_pdf))
        
        # Print summary
        comparator.print_summary(report)
        
        print(f"\nTest completed successfully!")
        print(f"Check the results in: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
