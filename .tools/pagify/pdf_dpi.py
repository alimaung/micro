# detect dpi of a pdf

import fitz  # PyMuPDF
import os
from typing import Dict, List, Optional


def detect_dpi(pdf_path: str) -> Dict[str, any]:
    """
    Detect DPI information from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        Dict containing DPI information:
        - page_dpi: List of DPI values for each page
        - image_dpi: List of DPI values for images found in the PDF
        - page_avg_dpi: Average DPI for pages
        - image_avg_dpi: Average DPI for images
        - average_dpi: Average DPI across all pages/images
        - max_dpi: Maximum DPI found
        - min_dpi: Minimum DPI found
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        page_dpis = []
        image_dpis = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Calculate page DPI (assuming standard page size)
            # PDF points: 1 inch = 72 points
            page_dpi_x = (page_width / 72) * 72  # This gives us the resolution
            page_dpi_y = (page_height / 72) * 72
            
            # For a more accurate page DPI, we'll use a standard approach
            # Most PDFs are created at 72 DPI by default, but we can estimate based on content
            estimated_page_dpi = 72  # Default PDF DPI
            page_dpis.append(estimated_page_dpi)
            
            # Extract images and their DPI
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_width = base_image["width"]
                    image_height = base_image["height"]
                    
                    # Get image rectangle on page
                    image_rects = page.get_image_rects(img)
                    if image_rects:
                        img_rect = image_rects[0]
                        # Calculate DPI based on image size vs display size
                        display_width = img_rect.width
                        display_height = img_rect.height
                        
                        if display_width > 0 and display_height > 0:
                            dpi_x = (image_width / display_width) * 72
                            dpi_y = (image_height / display_height) * 72
                            avg_dpi = (dpi_x + dpi_y) / 2
                            image_dpis.append(avg_dpi)
                
                except Exception as e:
                    print(f"Error processing image {img_index} on page {page_num}: {e}")
                    continue
        
        doc.close()
        
        # Calculate separate averages
        page_avg_dpi = sum(page_dpis) / len(page_dpis) if page_dpis else 0
        image_avg_dpi = sum(image_dpis) / len(image_dpis) if image_dpis else 0
        
        # For overall average, prioritize image DPI if available, otherwise use page DPI
        if image_dpis:
            overall_avg_dpi = image_avg_dpi  # Images are more meaningful for DPI
            all_dpis = image_dpis  # Use only image DPIs for min/max
        else:
            overall_avg_dpi = page_avg_dpi
            all_dpis = page_dpis
        
        if not all_dpis:
            return {
                "page_dpi": page_dpis,
                "image_dpi": image_dpis,
                "page_avg_dpi": 72,
                "image_avg_dpi": None,
                "average_dpi": 72,  # Default PDF DPI
                "max_dpi": 72,
                "min_dpi": 72,
                "total_pages": len(page_dpis),
                "total_images": len(image_dpis)
            }
        
        return {
            "page_dpi": page_dpis,
            "image_dpi": image_dpis,
            "page_avg_dpi": page_avg_dpi,
            "image_avg_dpi": image_avg_dpi,
            "average_dpi": overall_avg_dpi,
            "max_dpi": max(all_dpis),
            "min_dpi": min(all_dpis),
            "total_pages": len(page_dpis),
            "total_images": len(image_dpis)
        }
        
    except Exception as e:
        raise Exception(f"Error processing PDF: {e}")


def detect_dpi_simple(pdf_path: str) -> float:
    """
    Simple function to get average DPI of a PDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        float: Average DPI value
    """
    result = detect_dpi(pdf_path)
    return result["average_dpi"]


if __name__ == "__main__":
    pdf_file = "1427004500463500.pdf"
    
    try:
        result = detect_dpi(pdf_file)
        print(f"DPI Analysis for: {pdf_file}")
        print("=" * 50)
        print(f"Total Pages: {result['total_pages']}")
        print(f"Total Images: {result['total_images']}")
        print(f"Page Average DPI: {result['page_avg_dpi']:.2f}")
        if result['image_avg_dpi']:
            print(f"Image Average DPI: {result['image_avg_dpi']:.2f}")
        else:
            print(f"Image Average DPI: No images found")
        print(f"Overall Average DPI: {result['average_dpi']:.2f} (prioritizes images if available)")
        print(f"Maximum DPI: {result['max_dpi']:.2f}")
        print(f"Minimum DPI: {result['min_dpi']:.2f}")
        
        if result['image_dpi']:
            print(f"\nFirst 10 Image DPIs: {[f'{dpi:.2f}' for dpi in result['image_dpi'][:10]]}")
            if len(result['image_dpi']) > 10:
                print(f"... and {len(result['image_dpi']) - 10} more images")
        
        print(f"\nSimple DPI (average): {detect_dpi_simple(pdf_file):.2f}")
        
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_file}' not found.")
        print("Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
