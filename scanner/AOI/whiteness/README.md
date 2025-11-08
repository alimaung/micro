# Whiteness Detection Module

Detects completely white pages in PDF documents to optimize processing by skipping unnecessary comparisons.

## Purpose

This module identifies blank or white pages in PDF documents. White pages are common in scanned documents (cover pages, blank pages, etc.) and don't need to be processed for quality comparison, saving computational resources.

## Usage

```python
from scanner.AOI.whiteness.whiteness import WhitePageDetector

# Initialize detector with thresholds
detector = WhitePageDetector(
    dpi=300,
    white_threshold=0.9999,  # 99.99% white pixels required
    white_pixel_threshold=254  # Pixel value >= 254 considered white
)

# Check if a page is white
is_white, analysis = detector.is_white_page("path/to/document.pdf", page_index=0)

if is_white:
    print(f"Page {analysis['page_number']} is white ({analysis['white_percentage']:.2%} white pixels)")
    # Skip processing this page
else:
    # Process normally
    pass
```

## Configuration

- **white_threshold**: Percentage of white pixels required to consider a page "white" (0.0-1.0)
  - Default: 0.9999 (99.99%)
  - Higher values = stricter detection (fewer false positives)
  
- **white_pixel_threshold**: Pixel intensity value considered "white" (0-255)
  - Default: 254
  - Higher values = stricter white detection

- **dpi**: Resolution for rendering PDF pages for analysis
  - Default: 300
  - Higher DPI = more accurate but slower

## Features

- Supports multiple image modes (grayscale, RGB, RGBA, 1-bit)
- Detailed analysis information including pixel counts and percentages
- Error handling for invalid PDFs or pages
- JSON-serializable results for reporting

## Dependencies

- `PyMuPDF` (fitz) - PDF rendering
- `PIL` (Pillow) - Image handling
- `numpy` - Array operations

