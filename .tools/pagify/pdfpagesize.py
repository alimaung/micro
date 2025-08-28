#!/usr/bin/env python
import os
import sys
import math
from PyPDF2 import PdfReader
from collections import Counter

# ISO A series paper sizes in points (1 pt = 1/72 inch)
# Dimensions are in portrait orientation (width, height)
ISO_A_SIZES = {
    "A0": (2384, 3370),
    "A1": (1684, 2384),
    "A2": (1191, 1684),
    "A3": (842, 1191),
    "A4": (595, 842),
    "A5": (420, 595),
    "A6": (298, 420),
    "A7": (210, 298),
    "A8": (147, 210),
    "A9": (105, 147),
    "A10": (74, 105),
}

def get_closest_iso_a(width, height):
    """Find the closest ISO A series paper size for given dimensions.
    Considers both portrait and landscape orientations."""
    # Don't swap dimensions - use as provided to determine orientation later
    original_width, original_height = width, height
    
    min_diff = float('inf')
    closest_size = None
    orientation = None
    
    for size_name, (iso_width, iso_height) in ISO_A_SIZES.items():
        # Check portrait orientation (ISO sizes are stored as portrait)
        diff_portrait = math.sqrt((width - iso_width)**2 + (height - iso_height)**2)
        
        # Check landscape orientation
        diff_landscape = math.sqrt((width - iso_height)**2 + (height - iso_width)**2)
        
        if diff_portrait < min_diff:
            min_diff = diff_portrait
            closest_size = size_name
            # If original width < height, it's portrait, otherwise landscape
            orientation = "portrait" if original_width < original_height else "landscape"
            
        if diff_landscape < min_diff:
            min_diff = diff_landscape
            closest_size = size_name
            # If original width > height, it's portrait, otherwise landscape
            orientation = "landscape" if original_width < original_height else "portrait"
    
    return closest_size, orientation, min_diff

def analyze_pdf(pdf_path):
    """Analyze a PDF file and determine the closest ISO A size for each page."""
    try:
        reader = PdfReader(pdf_path)
        results = []
        
        print(f"Analyzing PDF: {os.path.basename(pdf_path)}")
        print(f"Total pages: {len(reader.pages)}")
        print("-" * 60)
        print("Page | Actual Size (pts)     | Closest ISO | Orientation | Difference")
        print("-" * 60)
        
        for i, page in enumerate(reader.pages):
            # Get page dimensions in points
            width = page.mediabox.width
            height = page.mediabox.height
            
            closest_size, orientation, diff = get_closest_iso_a(width, height)
            
            print(f"{i+1:4d} | {width:.1f} x {height:.1f} pts | {closest_size:9s} | {orientation:10s} | {diff:.2f}")
            
            results.append({
                'page': i+1,
                'width': width,
                'height': height,
                'closest_iso': closest_size,
                'orientation': orientation,
                'difference': diff
            })
        
        # Summarize results
        size_counter = Counter([(r['closest_iso'], r['orientation']) for r in results])
        print("\nSummary:")
        for (size, orientation), count in size_counter.most_common():
            percentage = (count / len(results)) * 100
            print(f"{size} ({orientation}): {count} pages ({percentage:.1f}%)")
        
        return results
    
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdfpagesize.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)
    
    analyze_pdf(pdf_path)

if __name__ == "__main__":
    main()
