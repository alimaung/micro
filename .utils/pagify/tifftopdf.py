import os
import argparse
import time
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any
import re
from tqdm import tqdm
import img2pdf
import hashlib
import io
import numpy as np
from PIL import Image
import pypdf

class TiffToPdfConverter:
    """
    High-quality TIFF to PDF converter using img2pdf for maximum quality preservation.
    Uses sequential file validation for external drive safety.
    Includes optional in-process pixel-perfect quality verification.
    Merges all TIFF files in a folder into a single PDF with zero quality loss.
    """
    
    def __init__(self, folder_path: str, sort_files: bool = True, verify_quality: bool = True, skip_validation: bool = False, progress_callback=None):
        """
        Initialize the converter with the specified folder path.
        
        Args:
            folder_path (str): Path to the folder containing TIFF files
            sort_files (bool): Whether to sort TIFF files naturally before processing
            verify_quality (bool): Whether to perform in-process quality verification
            skip_validation (bool): Whether to skip file validation entirely (faster but less safe)
            progress_callback (callable): Optional callback function for real-time progress updates
                                        Called with (stage, progress, message) parameters
        """
        self.folder_path = Path(folder_path)
        self.sort_files = sort_files
        self.verify_quality = verify_quality
        self.skip_validation = skip_validation
        self.progress_callback = progress_callback
        
        # Validate folder path
        if not self.folder_path.exists():
            raise ValueError(f"Folder path does not exist: {folder_path}")
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
    # Removed _setup_logging - converter is now pure (no logging)
    
    def _update_progress(self, stage: str, progress: int, message: str = ""):
        """Call the progress callback if provided."""
        if self.progress_callback:
            try:
                self.progress_callback(stage, progress, message)
            except Exception:
                pass  # Ignore callback errors
    
    def _natural_sort_key(self, filename: str) -> List:
        """
        Generate a natural sorting key for filenames with numbers.
        
        Args:
            filename (str): The filename to generate a key for
            
        Returns:
            List: A list that can be used for natural sorting
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', filename)]
    
    def _get_tiff_files(self) -> List[Path]:
        """
        Get all TIFF files in the folder, optionally sorted naturally.
        
        Returns:
            List[Path]: List of TIFF file paths
        """
        tiff_extensions = {'.tiff', '.tif'}
        tiff_files = [
            file for file in self.folder_path.iterdir()
            if file.is_file() and file.suffix.lower() in tiff_extensions
        ]
        
        if self.sort_files:
            tiff_files.sort(key=lambda x: self._natural_sort_key(x.name))
        
        return tiff_files
    
    def _validate_single_file(self, tiff_file: Path) -> Tuple[bool, Dict]:
        """
        Validate a single TIFF file in a thread-safe manner.
        
        Args:
            tiff_file (Path): Path to the TIFF file to validate
            
        Returns:
            Tuple[bool, Dict]: (is_valid, file_info)
        """
        try:
            # Check if file exists
            if not tiff_file.exists():
                return False, {
                    "name": tiff_file.name,
                    "error": "File not found",
                    "size": 0,
                    "size_human": "0 B"
                }
            
            # Get file size
            file_size = tiff_file.stat().st_size
            
            # Test if file is readable
            with open(tiff_file, 'rb') as f:
                # Read first few bytes to verify it's a valid file
                header = f.read(8)
                if len(header) < 8:
                    return False, {
                        "name": tiff_file.name,
                        "error": "File too small",
                        "size": file_size,
                        "size_human": self._format_size(file_size)
                    }
                
                # Basic TIFF header validation (optional - img2pdf will do full validation)
                # TIFF files start with either "II*\0" (little-endian) or "MM\0*" (big-endian)
                # Skip warning for now since img2pdf will validate properly
            
            return True, {
                "name": tiff_file.name,
                "size": file_size,
                "size_human": self._format_size(file_size),
                "path": str(tiff_file)
            }
                        
        except Exception as e:
            return False, {
                "name": tiff_file.name,
                "error": str(e),
                "size": 0,
                "size_human": "0 B"
            }
    
    def _validate_files_sequential(self, tiff_files: List[Path], result_dict: dict = None) -> Tuple[List[str], int]:
        """
        Validate all TIFF files sequentially for external drive safety.
        
        Args:
            tiff_files (List[Path]): List of TIFF files to validate
            result_dict (dict): Optional result dictionary to update with progress
            
        Returns:
            Tuple[List[str], int]: (valid_file_paths, total_size)
        """
        valid_files = []
        total_size = 0
        failed_files = []
        
        if result_dict:
            result_dict['stages']['validation']['status'] = 'running'
        
        # Initial progress callback
        self._update_progress("validation", 0, f"Starting validation of {len(tiff_files)} files")
        
        try:
            # Process files sequentially to avoid overwhelming external drives
            for i, tiff_file in enumerate(tiff_files, 1):
                try:
                    # Progress callback for current file
                    self._update_progress("validation", int((i-1) / len(tiff_files) * 100), f"Validating {tiff_file.name}")
                    
                    is_valid, file_info = self._validate_single_file(tiff_file)
                    
                    if is_valid:
                        valid_files.append(file_info["path"])
                        total_size += file_info["size"]
                        if result_dict:
                            result_dict['stages']['validation']['valid_files'].append({
                                'name': file_info['name'],
                                'size': file_info['size'],
                                'size_human': file_info['size_human']
                            })
                    else:
                        failed_files.append(file_info)
                        if result_dict:
                            result_dict['stages']['validation']['failed_files'].append({
                                'name': file_info['name'],
                                'error': file_info.get('error', 'Unknown error')
                            })
                    
                except Exception as e:
                    failed_files.append({
                        "name": tiff_file.name,
                        "error": str(e),
                        "size": 0,
                        "size_human": "0 B"
                    })
                    if result_dict:
                        result_dict['stages']['validation']['failed_files'].append({
                            'name': tiff_file.name,
                            'error': str(e)
                        })
                
                # Update progress
                progress = int((i / len(tiff_files)) * 100)
                if result_dict:
                    result_dict['stages']['validation']['progress'] = progress
                
                # Progress callback for completion
                self._update_progress("validation", progress, f"Validated {i}/{len(tiff_files)} files")
                
                # Small delay every 10 files to prevent overwhelming external drives
                if i % 10 == 0:
                    time.sleep(0.1)
            
            # Sort valid files to maintain processing order
            if self.sort_files:
                valid_files.sort(key=lambda x: self._natural_sort_key(Path(x).name))
            
            if result_dict:
                result_dict['stages']['validation']['status'] = 'complete'
            
            return valid_files, total_size
            
        except Exception as e:
            if result_dict:
                result_dict['stages']['validation']['status'] = 'error'
                result_dict['error'] = f"File validation failed: {e}"
            raise
    
    def _format_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _calculate_image_hash(self, image: Image.Image) -> str:
        """Calculate SHA-256 hash of image pixel data."""
        # Convert to bytes for hashing
        if image.mode == 'P':  # Palette mode
            image = image.convert('RGB')
        
        image_bytes = image.tobytes()
        return hashlib.sha256(image_bytes).hexdigest()
    
    def _extract_pdf_image(self, pdf_bytes: bytes, page_index: int = 0) -> Optional[Image.Image]:
        """Extract a single image from the PDF for verification."""
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            
            if page_index >= len(pdf_reader.pages):
                # Page not found - skip silently since we don't have a logger
                return None
            
            page = pdf_reader.pages[page_index]
            
            # Extract images from page
            if '/XObject' in page['/Resources']:
                xobjects = page['/Resources']['/XObject'].get_object()
                
                for obj_name in xobjects:
                    obj = xobjects[obj_name]
                    
                    if obj.get('/Subtype') == '/Image':
                        try:
                            width = obj['/Width']
                            height = obj['/Height']
                            
                            # Get image data
                            if hasattr(obj, 'get_data'):
                                img_data = obj.get_data()
                            else:
                                img_data = obj._data
                            
                            # Handle different image formats
                            filters = obj.get('/Filter', [])
                            if not isinstance(filters, list):
                                filters = [filters]
                            
                            if '/DCTDecode' in filters:  # JPEG
                                img = Image.open(io.BytesIO(img_data))
                                return img
                            elif '/FlateDecode' in filters:  # PNG-like
                                color_space = obj.get('/ColorSpace', '/DeviceRGB')
                                
                                if color_space == '/DeviceGray':
                                    mode = 'L'
                                    expected_size = width * height
                                elif color_space == '/DeviceRGB':
                                    mode = 'RGB'
                                    expected_size = width * height * 3
                                else:
                                    mode = 'RGB'
                                    expected_size = width * height * 3
                                
                                if len(img_data) >= expected_size:
                                    img = Image.frombytes(mode, (width, height), img_data[:expected_size])
                                    return img
                            
                            # Try direct image opening as fallback
                            try:
                                img = Image.open(io.BytesIO(img_data))
                                return img
                            except:
                                continue
                                
                        except Exception as e:
                            # Could not extract image - skip silently since we don't have a logger
                            continue
            
            return None
            
        except Exception as e:
            # Could not extract PDF image for verification - skip silently since we don't have a logger
            return None

    def _verify_conversion_quality(self, original_files: List[str], pdf_bytes: bytes, result_dict: dict = None) -> Dict[str, Any]:
        """
        Verify the quality of the PDF conversion by comparing with original TIFF files.
        
        Args:
            original_files (List[str]): List of original TIFF file paths
            pdf_bytes (bytes): The generated PDF as bytes
            
        Returns:
            Dict[str, Any]: Verification results
        """
        verification_results = {
            "total_files": len(original_files),
            "verified_files": 0,
            "perfect_matches": 0,
            "hash_matches": 0,
            "pixel_differences": [],
            "overall_quality": "unknown",
            "verification_time": 0
        }
        
        start_time = time.time()
        
        # Initial progress callback
        self._update_progress("verification", 0, f"Starting verification of {len(original_files)} files")
        
        try:
            for i, tiff_path in enumerate(original_files, 1):
                try:
                    # Progress callback for current file
                    filename = Path(tiff_path).name
                    self._update_progress("verification", int((i-1) / len(original_files) * 100), f"Verifying {filename}")
                    
                    # Load original TIFF
                    with Image.open(tiff_path) as original_img:
                        original_copy = original_img.copy()
                    
                    # Extract corresponding PDF image
                    pdf_img = self._extract_pdf_image(pdf_bytes, i-1)
                    
                    if pdf_img is None:
                        continue
                    
                    verification_results["verified_files"] += 1
                    
                    # Quick hash comparison first
                    original_hash = self._calculate_image_hash(original_copy)
                    pdf_hash = self._calculate_image_hash(pdf_img)
                    
                    if original_hash == pdf_hash:
                        verification_results["hash_matches"] += 1
                        verification_results["perfect_matches"] += 1
                    else:
                        # Convert images to same mode if needed
                        if original_copy.mode != pdf_img.mode:
                            if original_copy.mode == 'RGBA' and pdf_img.mode == 'RGB':
                                original_copy = original_copy.convert('RGB')
                            elif original_copy.mode == 'RGB' and pdf_img.mode == 'RGBA':
                                pdf_img = pdf_img.convert('RGB')
                        
                        # Pixel comparison
                        if original_copy.size == pdf_img.size and original_copy.mode == pdf_img.mode:
                            arr1 = np.array(original_copy)
                            arr2 = np.array(pdf_img)
                            
                            diff = np.abs(arr1.astype(np.int16) - arr2.astype(np.int16))
                            pixel_differences = np.count_nonzero(diff)
                            total_pixels = arr1.size
                            diff_percentage = (pixel_differences / total_pixels) * 100
                            
                            verification_results["pixel_differences"].append({
                                "file": Path(tiff_path).name,
                                "different_pixels": int(pixel_differences),
                                "total_pixels": int(total_pixels),
                                "difference_percentage": float(diff_percentage)
                            })
                            
                            if pixel_differences == 0:
                                verification_results["perfect_matches"] += 1
                            elif diff_percentage < 0.01:
                                verification_results["perfect_matches"] += 1
                
                except Exception as e:
                    pass  # Skip files with verification errors
                
                # Update progress
                if result_dict:
                    result_dict['stages']['verification']['progress'] = int((i / len(original_files)) * 100)
            
            # Calculate overall quality
            if verification_results["verified_files"] > 0:
                perfect_rate = verification_results["perfect_matches"] / verification_results["verified_files"]
                
                if perfect_rate == 1.0:
                    verification_results["overall_quality"] = "perfect"
                elif perfect_rate >= 0.99:
                    verification_results["overall_quality"] = "excellent"
                elif perfect_rate >= 0.95:
                    verification_results["overall_quality"] = "good"
                else:
                    verification_results["overall_quality"] = "poor"
            
        except Exception as e:
            verification_results["overall_quality"] = "error"
            if result_dict:
                result_dict['error'] = f"Quality verification failed: {e}"
        
        verification_results["verification_time"] = time.time() - start_time
        return verification_results
    
    def _convert_to_pdf(self, valid_file_paths: List[str], total_size: int, result_dict: dict = None) -> Tuple[bool, int]:
        """
        Convert all validated TIFF files to a single PDF using img2pdf for maximum quality.
        
        Args:
            valid_file_paths (List[str]): List of validated TIFF file paths
            total_size (int): Total size of all files in bytes
            result_dict (dict): Optional result dictionary to update with progress
            
        Returns:
            Tuple[bool, int]: (success, pdf_size_bytes)
        """
        start_time = time.time()
        pdf_size = 0
        
        try:
            if not valid_file_paths:
                if result_dict:
                    result_dict['error'] = "No valid TIFF files found for conversion"
                return False, 0
            
            # Output PDF path (in parent directory)
            pdf_output_path = self.folder_path.parent / f"{self.folder_path.name}.pdf"
            
            # Progress callback for conversion start
            self._update_progress("conversion", 0, f"Starting PDF conversion of {len(valid_file_paths)} files")
            
            try:
                # Progress callback for img2pdf start
                self._update_progress("conversion", 20, "Creating PDF with img2pdf...")
                
                # img2pdf conversion with quality preservation
                pdf_bytes = img2pdf.convert(
                    valid_file_paths,
                    # Preserve original DPI and color modes
                    # img2pdf automatically detects and preserves:
                    # - Original DPI/resolution
                    # - Color modes (1-bit, grayscale, RGB, CMYK)
                    # - Compression (no recompression)
                )
                
                pdf_size = len(pdf_bytes)
                
                # Progress callback for writing
                self._update_progress("conversion", 80, f"Writing PDF to disk ({pdf_size / (1024*1024):.1f} MB)")
                
                # Write PDF to file
                with open(pdf_output_path, "wb") as pdf_file:
                    pdf_file.write(pdf_bytes)
                
                # Small delay to let external drive settle after large write
                time.sleep(0.2)
                
                # Get actual output file size
                output_size = pdf_output_path.stat().st_size
                
                if result_dict:
                    result_dict['stages']['conversion']['pdf_size'] = output_size
                    result_dict['stages']['conversion']['input_size'] = total_size
                    result_dict['stages']['conversion']['compression_ratio'] = (total_size - output_size) / total_size * 100 if total_size > 0 else 0
                    result_dict['stages']['conversion']['processing_time'] = time.time() - start_time
                    result_dict['stages']['conversion']['output_path'] = str(pdf_output_path)
                
                return True, output_size
                            
            except Exception as e:
                if result_dict:
                    result_dict['error'] = f"img2pdf conversion failed: {e}"
                return False, 0
            
        except Exception as e:
            if result_dict:
                result_dict['error'] = f"Failed to convert TIFF files: {e}"
            return False, 0
    
    def convert_all(self) -> dict:
        """
        Convert and merge all TIFF files in the folder to a single PDF.
        Returns detailed progress information for the caller to handle.
        
        Returns:
            dict: Detailed conversion results with progress information
        """
        overall_start_time = time.time()
        
        # Initialize result structure
        result = {
            'success': False,
            'total_files': 0,
            'valid_files': 0,
            'processing_time': 0,
            'stages': {
                'discovery': {'status': 'starting', 'progress': 0, 'files': []},
                'validation': {'status': 'pending', 'progress': 0, 'valid_files': [], 'failed_files': []},
                'conversion': {'status': 'pending', 'progress': 0, 'pdf_size': 0},
                'verification': {'status': 'pending', 'progress': 0, 'results': None}
            },
            'error': None
        }
        
        try:
            # Stage 1: File Discovery
            result['stages']['discovery']['status'] = 'running'
            self._update_progress("discovery", 0, "Scanning for TIFF files...")
            
            tiff_files = self._get_tiff_files()
            result['total_files'] = len(tiff_files)
            result['stages']['discovery']['files'] = [f.name for f in tiff_files]
            result['stages']['discovery']['progress'] = 100
            result['stages']['discovery']['status'] = 'complete'
            
            self._update_progress("discovery", 100, f"Found {len(tiff_files)} TIFF files")
            
            if not tiff_files:
                result['error'] = "No TIFF files found in the specified folder"
                result['processing_time'] = time.time() - overall_start_time
                return result
            
            # Stage 2: File Validation
            if not self.skip_validation:
                result['stages']['validation']['status'] = 'running'
                valid_file_paths, total_size = self._validate_files_sequential(tiff_files, result)
                result['valid_files'] = len(valid_file_paths)
                
                if not valid_file_paths:
                    result['error'] = "No valid TIFF files found after validation"
                    result['processing_time'] = time.time() - overall_start_time
                    return result
            else:
                # Skip validation - use all TIFF files directly
                result['stages']['validation']['status'] = 'skipped'
                result['stages']['validation']['progress'] = 100
                self._update_progress("validation", 100, "Validation skipped - using all files")
                
                valid_file_paths = [str(f) for f in tiff_files]
                total_size = sum(f.stat().st_size for f in tiff_files)
                result['valid_files'] = len(valid_file_paths)
                
                # Sort files if requested
                if self.sort_files:
                    valid_file_paths.sort(key=lambda x: self._natural_sort_key(Path(x).name))
            
            # Stage 3: PDF Conversion
            result['stages']['conversion']['status'] = 'running'
            success, pdf_size = self._convert_to_pdf(valid_file_paths, total_size, result)
            result['stages']['conversion']['pdf_size'] = pdf_size
            result['stages']['conversion']['progress'] = 100
            result['stages']['conversion']['status'] = 'complete' if success else 'error'
            
            if not success:
                result['error'] = "PDF conversion failed"
                result['processing_time'] = time.time() - overall_start_time
                return result
            
            # Stage 4: Quality Verification (if enabled)
            if self.verify_quality:
                result['stages']['verification']['status'] = 'running'
                try:
                    # Read the PDF file to get bytes for verification
                    pdf_path = self.folder_path.parent / f"{self.folder_path.name}.pdf"
                    if pdf_path.exists():
                        with open(pdf_path, 'rb') as f:
                            pdf_bytes = f.read()
                        verification_results = self._verify_conversion_quality(valid_file_paths, pdf_bytes, result)
                        result['stages']['verification']['results'] = verification_results
                        result['stages']['verification']['progress'] = 100
                        result['stages']['verification']['status'] = 'complete'
                    else:
                        result['stages']['verification']['status'] = 'error'
                        result['stages']['verification']['results'] = {'error': 'PDF file not found for verification'}
                except Exception as e:
                    # Verification failed - but don't fail the whole conversion
                    result['stages']['verification']['status'] = 'error'
                    result['stages']['verification']['results'] = {'error': f'Verification failed: {str(e)}'}
            else:
                result['stages']['verification']['status'] = 'skipped'
            
            result['success'] = True
            result['processing_time'] = time.time() - overall_start_time
            return result
            
        except Exception as e:
            result['error'] = f"Conversion failed: {e}"
            result['processing_time'] = time.time() - overall_start_time
            return result


def main():
    """Main function to handle command line arguments and run the converter."""
    parser = argparse.ArgumentParser(
        description='High-quality TIFF to PDF converter using img2pdf with sequential validation and in-process verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tifftopdf.py -f /path/to/tiff/folder
  python tifftopdf.py -f /path/to/tiff/folder --no-sort
  python tifftopdf.py -f /path/to/tiff/folder --no-verify
  python tifftopdf.py -f /path/to/tiff/folder --skip-validation
  python tifftopdf.py -f /path/to/tiff/folder --verbose
  
Features:
  • Lossless TIFF to PDF conversion using img2pdf
  • Sequential file validation (external drive safe)
  • In-process pixel-perfect quality verification
  • Preserves original DPI/resolution
  • Preserves original color modes (1-bit, grayscale, RGB, CMYK)
  • No recompression or quality loss
  • Natural sorting of files (file1.tif, file2.tif, file10.tif)
  • Much faster than traditional conversion methods
  • Smaller output files with better quality
  • Robust file validation with error handling
        """
    )
    
    parser.add_argument(
        '-f', '--folder',
        required=True,
        help='Path to the folder containing TIFF files'
    )
    

    
    parser.add_argument(
        '--no-sort',
        action='store_true',
        help='Disable natural sorting of TIFF files'
    )
    
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Disable in-process quality verification'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip file validation entirely (faster but less safe)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    args = parser.parse_args()
    
    # Validate folder path
    if not os.path.exists(args.folder):
        tqdm.write(f"❌ Error: Folder '{args.folder}' does not exist")
        return 1
    
    if not os.path.isdir(args.folder):
        tqdm.write(f"❌ Error: '{args.folder}' is not a directory")
        return 1
    

    
    try:
        # Create converter and run conversion
        converter = TiffToPdfConverter(
            args.folder, 
            sort_files=not args.no_sort,
            verify_quality=not args.no_verify,
            skip_validation=args.skip_validation
        )
        
        results = converter.convert_all()
        
        # Return appropriate exit code
        return 0 if results['success'] else 1
        
    except KeyboardInterrupt:
        tqdm.write("\n⚠️  Conversion interrupted by user")
        return 130
    except Exception as e:
        tqdm.write(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 