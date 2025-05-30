# PDF DPI Detection Tool

This tool detects the DPI (Dots Per Inch) of PDF files by analyzing both page dimensions and embedded images.

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

### As a Script

Run the script directly:

```bash
python pdf_dpi.py
```

This will analyze the default PDF file `1427003101157580.pdf` if it exists in the current directory.

### As a Module

Import and use the functions in your own code:

```python
from pdf_dpi import detect_dpi, detect_dpi_simple

# Get detailed DPI information
result = detect_dpi("your_file.pdf")
print(f"Average DPI: {result['average_dpi']}")
print(f"Image DPIs: {result['image_dpi']}")

# Get simple average DPI
avg_dpi = detect_dpi_simple("your_file.pdf")
print(f"DPI: {avg_dpi}")
```

## Functions

### `detect_dpi(pdf_path: str) -> Dict`

Returns detailed DPI information:
- `page_dpi`: List of DPI values for each page
- `image_dpi`: List of DPI values for images found in the PDF
- `average_dpi`: Average DPI across all pages/images
- `max_dpi`: Maximum DPI found
- `min_dpi`: Minimum DPI found
- `total_pages`: Number of pages in the PDF
- `total_images`: Number of images found

### `detect_dpi_simple(pdf_path: str) -> float`

Returns just the average DPI as a float value.

## How it Works

1. **Page Analysis**: Analyzes PDF page dimensions (defaults to 72 DPI for standard PDF pages)
2. **Image Analysis**: Extracts embedded images and calculates their DPI based on:
   - Original image dimensions (width × height in pixels)
   - Display size on the PDF page
   - Conversion factor (72 points per inch)

## Notes

- PDF pages typically default to 72 DPI
- Image DPI is calculated based on how images are scaled when displayed in the PDF
- Higher DPI values indicate better quality/resolution
- The tool handles errors gracefully and continues processing even if some images can't be analyzed 