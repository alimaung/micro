# Conversion Module

Converts PDF documents to grayscale numpy arrays for image processing and analysis.

## Purpose

This module handles the conversion of PDF pages into image format suitable for computer vision operations. It provides a clean interface for converting PDF documents to grayscale numpy arrays that can be used by other AOI modules.

## Usage

```python
from scanner.AOI.conversion.conversion import PDFConverter

# Initialize converter with desired DPI
converter = PDFConverter(dpi=300)

# Convert PDF to images
images = converter.pdf_to_images("path/to/document.pdf")

# images is a list of numpy arrays (grayscale)
for i, img in enumerate(images):
    print(f"Page {i+1}: shape {img.shape}")
```

## Features

- Converts PDF pages to grayscale numpy arrays
- Configurable DPI for conversion quality
- Handles both color and grayscale PDFs
- Error handling for invalid PDFs

## Dependencies

- `pdf2image` - PDF to image conversion
- `opencv-python` (cv2) - Image processing
- `numpy` - Array operations
- `PIL` (Pillow) - Image handling

