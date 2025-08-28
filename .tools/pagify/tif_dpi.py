# detect dpi of a tiff file

from PIL import Image
from PIL.ExifTags import TAGS
import os
from typing import Dict, Tuple, Optional


def detect_dpi(tif_path: str) -> Dict[str, any]:
    """
    Detect DPI information from a TIFF file.
    
    Args:
        tif_path (str): Path to the TIFF file
        
    Returns:
        Dict containing DPI information:
        - dpi: Tuple of (x_dpi, y_dpi) or None if not found
        - dpi_x: X-axis DPI
        - dpi_y: Y-axis DPI
        - average_dpi: Average of X and Y DPI
        - resolution_unit: Unit of resolution (1=None, 2=inches, 3=cm)
        - dimensions: Image dimensions (width, height)
        - file_size: File size in bytes
        - format: Image format
        - mode: Image mode (RGB, RGBA, etc.)
    """
    if not os.path.exists(tif_path):
        raise FileNotFoundError(f"TIFF file not found: {tif_path}")
    
    try:
        with Image.open(tif_path) as img:
            # Get basic image info
            width, height = img.size
            file_size = os.path.getsize(tif_path)
            
            # Get DPI from image info
            dpi = img.info.get('dpi')
            
            # Try to get DPI from EXIF data if not in info
            if not dpi:
                try:
                    exif_data = img._getexif()
                    if exif_data:
                        # Look for resolution tags
                        x_resolution = exif_data.get(282)  # XResolution
                        y_resolution = exif_data.get(283)  # YResolution
                        resolution_unit = exif_data.get(296, 2)  # ResolutionUnit (default to inches)
                        
                        if x_resolution and y_resolution:
                            # Convert from fraction to float if needed
                            if isinstance(x_resolution, tuple):
                                x_dpi = x_resolution[0] / x_resolution[1]
                            else:
                                x_dpi = float(x_resolution)
                                
                            if isinstance(y_resolution, tuple):
                                y_dpi = y_resolution[0] / y_resolution[1]
                            else:
                                y_dpi = float(y_resolution)
                                
                            dpi = (x_dpi, y_dpi)
                except:
                    pass
            
            # Get resolution unit
            resolution_unit = 2  # Default to inches
            try:
                if hasattr(img, 'tag_v2'):
                    resolution_unit = img.tag_v2.get(296, 2)
                elif hasattr(img, 'tag'):
                    resolution_unit = img.tag.get(296, 2)
            except:
                pass
            
            # Parse DPI values
            if dpi:
                if isinstance(dpi, (tuple, list)) and len(dpi) >= 2:
                    dpi_x, dpi_y = float(dpi[0]), float(dpi[1])
                else:
                    dpi_x = dpi_y = float(dpi)
            else:
                # Try alternative method using image resolution
                try:
                    # Some TIFF files store resolution differently
                    info = img.info
                    if 'resolution' in info:
                        res = info['resolution']
                        if isinstance(res, (tuple, list)):
                            dpi_x, dpi_y = res[0], res[1]
                        else:
                            dpi_x = dpi_y = res
                    else:
                        dpi_x = dpi_y = None
                except:
                    dpi_x = dpi_y = None
            
            # Calculate average DPI
            if dpi_x is not None and dpi_y is not None:
                average_dpi = (dpi_x + dpi_y) / 2
                dpi_tuple = (dpi_x, dpi_y)
            else:
                average_dpi = None
                dpi_tuple = None
            
            # Resolution unit meanings
            unit_names = {1: "None", 2: "inches", 3: "centimeters"}
            unit_name = unit_names.get(resolution_unit, "unknown")
            
            return {
                "dpi": dpi_tuple,
                "dpi_x": dpi_x,
                "dpi_y": dpi_y,
                "average_dpi": average_dpi,
                "resolution_unit": resolution_unit,
                "resolution_unit_name": unit_name,
                "dimensions": (width, height),
                "file_size": file_size,
                "format": img.format,
                "mode": img.mode,
                "has_dpi": dpi_tuple is not None
            }
            
    except Exception as e:
        raise Exception(f"Error processing TIFF file: {e}")


def detect_dpi_simple(tif_path: str) -> Optional[float]:
    """
    Simple function to get average DPI of a TIFF file.
    
    Args:
        tif_path (str): Path to the TIFF file
        
    Returns:
        float: Average DPI value or None if not found
    """
    result = detect_dpi(tif_path)
    return result["average_dpi"]


def get_detailed_metadata(tif_path: str) -> Dict[str, any]:
    """
    Get detailed metadata from a TIFF file including EXIF data.
    
    Args:
        tif_path (str): Path to the TIFF file
        
    Returns:
        Dict containing detailed metadata
    """
    if not os.path.exists(tif_path):
        raise FileNotFoundError(f"TIFF file not found: {tif_path}")
    
    try:
        with Image.open(tif_path) as img:
            metadata = {
                "basic_info": {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "file_size": os.path.getsize(tif_path)
                },
                "image_info": dict(img.info),
                "exif_data": {}
            }
            
            # Get EXIF data
            try:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        metadata["exif_data"][tag_name] = value
            except:
                pass
            
            return metadata
            
    except Exception as e:
        raise Exception(f"Error reading TIFF metadata: {e}")


if __name__ == "__main__":
    # You can change this to your TIFF file
    tif_file = "1427004500463500/00000001.tif"  # Change this to your actual TIFF file
    
    try:
        result = detect_dpi(tif_file)
        print(f"DPI Analysis for: {tif_file}")
        print("=" * 50)
        print(f"File Format: {result['format']}")
        print(f"Image Mode: {result['mode']}")
        print(f"Dimensions: {result['dimensions'][0]} x {result['dimensions'][1]} pixels")
        print(f"File Size: {result['file_size']:,} bytes")
        print(f"Has DPI Info: {result['has_dpi']}")
        
        if result['has_dpi']:
            print(f"DPI (X, Y): {result['dpi']}")
            print(f"X DPI: {result['dpi_x']:.2f}")
            print(f"Y DPI: {result['dpi_y']:.2f}")
            print(f"Average DPI: {result['average_dpi']:.2f}")
            print(f"Resolution Unit: {result['resolution_unit_name']}")
        else:
            print("No DPI information found in the file")
        
        print(f"\nSimple DPI (average): {detect_dpi_simple(tif_file)}")
        
        # Show detailed metadata
        print(f"\n" + "=" * 50)
        print("DETAILED METADATA:")
        print("=" * 50)
        metadata = get_detailed_metadata(tif_file)
        
        print("\nImage Info:")
        for key, value in metadata["image_info"].items():
            print(f"  {key}: {value}")
        
        if metadata["exif_data"]:
            print("\nEXIF Data:")
            for key, value in metadata["exif_data"].items():
                print(f"  {key}: {value}")
        
    except FileNotFoundError:
        print(f"Error: TIFF file '{tif_file}' not found.")
        print("Please make sure the file exists in the current directory.")
        print("You can change the filename in the script or provide the correct path.")
    except Exception as e:
        print(f"Error analyzing TIFF: {e}") 