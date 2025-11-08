# Automated Optical Inspection (AOI) Orientation Detection System

## Overview

The Automated Optical Inspection (AOI) Orientation Detection System provides robust orientation detection for comparing original PDFs with scanned microfilm reproductions. This system addresses the challenge of different orientations between documents to enable accurate overlapping and comparison.

## Problem Statement

When comparing original digital documents with their microfilm reproductions, the documents often have different orientations due to:

- Different scanning orientations during microfilm creation
- Rotation during the digitization process
- Inconsistent document placement during scanning
- Historical archival practices

This system automatically detects and corrects these orientation differences to enable accurate document comparison and quality assessment.

## Key Features

### Multi-Method Detection
- **SIFT Feature Matching**: Scale-Invariant Feature Transform for robust feature detection
- **ORB Feature Matching**: Oriented FAST and Rotated BRIEF for fast feature matching
- **Edge-based Correlation**: Canny edge detection with correlation analysis
- **Template Matching**: Multiple template matching algorithms
- **SSIM Analysis**: Structural Similarity Index for perceptual comparison

### Two-Stage Detection Process
1. **Coarse Detection**: Detects 90-degree rotations (0°, 90°, 180°, 270°)
2. **Fine Detection**: Adjusts orientation within ±10 degrees for precise alignment

### Confidence Scoring
- Individual method confidence scores
- Weighted combined confidence
- Quality assessment (High/Medium/Low)
- Automatic validation and error detection

### Comprehensive Visualization
- Side-by-side comparison views
- Overlay visualizations with difference maps
- Score progression charts
- Batch processing reports
- Confidence heatmaps

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          Automated Optical Inspection (AOI) Orientation    │
│                        Detection                            │
├─────────────────────────────────────────────────────────────┤
│  Input: Original PDF + Reproduction PDF                    │
│         ↓                                                   │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │ PDF to Images   │    │ Image           │               │
│  │ Conversion      │    │ Preprocessing   │               │
│  └─────────────────┘    └─────────────────┘               │
│         ↓                        ↓                         │
│  ┌─────────────────────────────────────────┐               │
│  │        Coarse Orientation Detection      │               │
│  │  • Test 0°, 90°, 180°, 270° rotations  │               │
│  │  • Multi-method scoring                 │               │
│  │  • Best rotation selection              │               │
│  └─────────────────────────────────────────┘               │
│         ↓                                                   │
│  ┌─────────────────────────────────────────┐               │
│  │        Fine Orientation Detection        │               │
│  │  • Test ±10° around coarse result      │               │
│  │  • High-precision alignment            │               │
│  │  • Confidence validation               │               │
│  └─────────────────────────────────────────┘               │
│         ↓                                                   │
│  ┌─────────────────────────────────────────┐               │
│  │         Visualization & Reporting        │               │
│  │  • Comparison visualizations           │               │
│  │  • Confidence analysis                 │               │
│  │  • JSON/PNG output                     │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Installation and Setup

### Prerequisites

```bash
# Core dependencies
pip install numpy opencv-python scikit-image scipy matplotlib seaborn
pip install pdf2image PyMuPDF pillow pytesseract

# System dependencies (Windows)
# Download and install Tesseract OCR from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Download and install Poppler for PDF processing:
# https://github.com/oschwartz10612/poppler-windows
```

### Directory Structure

```
scanner/AOI/orientation/
├── orientation_detector.py      # Core detection algorithms
├── orientation_visualizer.py    # Visualization and reporting
├── test_orientation.py         # Comprehensive test suite
├── README.md                   # This documentation
├── examples/                   # Usage examples
│   ├── basic_usage.py
│   ├── batch_processing.py
│   └── custom_config.py
└── configs/                    # Configuration templates
    ├── default_config.json
    ├── high_accuracy.json
    └── fast_processing.json
```

## Usage Examples

### Basic Usage

```python
from scanner.AOI.orientation import OrientationDetector, OrientationVisualizer
import cv2

# Initialize detector with default configuration
detector = OrientationDetector()

# Load images (grayscale)
original_img = cv2.imread('original.png', cv2.IMREAD_GRAYSCALE)
reproduction_img = cv2.imread('reproduction.png', cv2.IMREAD_GRAYSCALE)

# Detect orientation
result = detector.detect_orientation(original_img, reproduction_img)

print(f"Detected rotation: {result['final_rotation']:.1f}°")
print(f"Confidence: {result['final_confidence']:.3f}")
print(f"Quality: {result['quality']}")

# Apply detected orientation
aligned_img = detector.apply_detected_orientation(reproduction_img, result)

# Create visualization
visualizer = OrientationVisualizer()
comparison_path = visualizer.create_orientation_comparison(
    original_img, reproduction_img, result, page_num=1
)
```

### Batch Processing

```python
from scanner.AOI.orientation import create_batch_visualization
from pdf2image import convert_from_path

# Convert PDFs to images
original_images = convert_from_path('original.pdf', dpi=300)
reproduction_images = convert_from_path('reproduction.pdf', dpi=300)

# Process all pages
detector = OrientationDetector()
results = []

for orig, repro in zip(original_images, reproduction_images):
    # Convert PIL to numpy arrays
    orig_np = np.array(orig.convert('L'))
    repro_np = np.array(repro.convert('L'))
    
    # Detect orientation
    result = detector.detect_orientation(orig_np, repro_np)
    results.append(result)

# Create comprehensive visualizations
page_numbers = list(range(1, len(results) + 1))
created_files = create_batch_visualization(
    [np.array(img.convert('L')) for img in original_images],
    [np.array(img.convert('L')) for img in reproduction_images],
    results,
    page_numbers,
    document_name="Sample Document",
    output_dir="orientation_results"
)

print(f"Created {len(created_files)} visualization files")
```

### Custom Configuration

```python
from scanner.AOI.orientation import OrientationDetector, OrientationConfig

# Create custom configuration
config = OrientationConfig(
    test_rotations=[0, 90, 180, 270],  # Test angles
    fine_angle_range=(-5.0, 5.0),     # Narrower fine range
    fine_angle_step=0.25,             # Higher precision
    max_dimension=1200,               # Higher resolution processing
    weights={                         # Custom scoring weights
        'ssim': 0.5,
        'feature_matching': 0.3,
        'edge_correlation': 0.15,
        'template_matching': 0.05
    },
    min_confidence=0.4,               # Lower confidence threshold
    high_confidence=0.8               # Higher quality threshold
)

# Initialize detector with custom config
detector = OrientationDetector(config)

# Use as normal
result = detector.detect_orientation(original_img, reproduction_img)
```

## Configuration Options

### OrientationConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `test_rotations` | List[int] | [0, 90, 180, 270] | Coarse rotation angles to test |
| `fine_angle_range` | Tuple[float, float] | (-10.0, 10.0) | Fine adjustment range in degrees |
| `fine_angle_step` | float | 0.5 | Step size for fine angle testing |
| `resize_for_speed` | bool | True | Resize images for faster processing |
| `max_dimension` | int | 800 | Maximum image dimension for processing |
| `gaussian_blur_kernel` | int | 3 | Gaussian blur kernel size |
| `canny_low_threshold` | int | 50 | Canny edge detection low threshold |
| `canny_high_threshold` | int | 150 | Canny edge detection high threshold |
| `sift_n_features` | int | 1000 | Maximum SIFT features to detect |
| `orb_n_features` | int | 1000 | Maximum ORB features to detect |
| `feature_match_ratio` | float | 0.75 | Feature matching ratio test threshold |
| `weights` | Dict[str, float] | See below | Scoring method weights |
| `min_confidence` | float | 0.3 | Minimum acceptable confidence |
| `high_confidence` | float | 0.7 | High quality confidence threshold |

### Default Scoring Weights

```python
weights = {
    'ssim': 0.4,                # Structural similarity
    'feature_matching': 0.3,    # SIFT/ORB feature matching
    'edge_correlation': 0.2,    # Edge-based correlation
    'template_matching': 0.1    # Template matching
}
```

## Output Formats

### Detection Results

```python
{
    'final_rotation': 90.5,           # Final detected rotation in degrees
    'final_confidence': 0.85,         # Combined confidence score (0-1)
    'quality': 'high',                # Quality level: 'high'/'medium'/'low'
    'coarse_result': {                # Coarse detection details
        'best_rotation': 90,
        'best_score': 0.9,
        'confidence': 0.85,
        'all_results': {              # Scores for all tested rotations
            0: {'combined_score': 0.3, 'individual_scores': {...}},
            90: {'combined_score': 0.9, 'individual_scores': {...}},
            # ...
        }
    },
    'fine_result': {                  # Fine detection details (if performed)
        'best_fine_angle': 0.5,
        'best_score': 0.92,
        'confidence': 0.8,
        'total_rotation': 90.5,
        'all_results': {...}
    },
    'timestamp': '2024-01-01T12:00:00',
    'config': {...}                   # Configuration used
}
```

### Visualization Outputs

1. **Individual Page Comparison** (`page_XXX_orientation_analysis.png`)
   - Side-by-side original and rotated images
   - Edge detection comparison
   - Overlay visualization with difference maps
   - Detailed metrics and scores

2. **Fine Angle Analysis** (`page_XXX_fine_angle_analysis.png`)
   - Score vs. angle progression chart
   - Individual method performance
   - Best angle highlighting

3. **Confidence Heatmap** (`confidence_heatmap.png`)
   - Cross-page confidence visualization
   - Rotation angle performance matrix
   - Quality assessment overview

4. **Summary Report** (`Document_Name_summary_report.png`)
   - Overall statistics and distributions
   - Quality breakdown
   - Recommendations and insights

5. **JSON Export** (`Document_Name_orientation_results.json`)
   - Machine-readable results
   - Complete detection data
   - Processing metadata

## Performance Considerations

### Speed Optimization

- **Image Resizing**: Automatically resizes large images for faster processing
- **Efficient Rotations**: Uses OpenCV's optimized rotation functions for 90° increments
- **Selective Fine Detection**: Only performs fine detection when coarse confidence is sufficient
- **Caching**: Preprocessed images are reused across detection methods

### Accuracy Factors

- **Image Quality**: Higher resolution images generally provide better detection accuracy
- **Content Type**: Documents with clear geometric features work best
- **Noise Level**: Excessive noise can reduce detection confidence
- **Rotation Magnitude**: Large rotations (>45°) are detected more reliably than small ones

### Memory Usage

- **Batch Processing**: Process pages individually to manage memory usage
- **Image Scaling**: Automatic scaling reduces memory requirements
- **Cleanup**: Temporary images are automatically cleaned up

## Troubleshooting

### Common Issues

1. **Low Confidence Scores**
   - Increase image resolution (higher DPI)
   - Adjust preprocessing parameters
   - Check for image noise or artifacts
   - Verify sufficient image content

2. **Incorrect Rotation Detection**
   - Review individual method scores
   - Adjust scoring weights
   - Check for symmetric content that might confuse detection
   - Validate input image quality

3. **Performance Issues**
   - Reduce `max_dimension` for faster processing
   - Disable fine detection for speed
   - Use fewer SIFT/ORB features
   - Process smaller batches

4. **Visualization Errors**
   - Ensure sufficient disk space
   - Check output directory permissions
   - Verify matplotlib backend compatibility
   - Update visualization dependencies

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run detection with detailed logging
detector = OrientationDetector()
result = detector.detect_orientation(original_img, reproduction_img)
```

## Integration with Existing Systems

### Document Comparison Pipeline

The orientation detection system integrates seamlessly with the existing document comparison pipeline:

```python
from scanner.compare_documents import DocumentComparator
from scanner.AOI.orientation import OrientationDetector

# Enhanced comparator with Automated Optical Inspection (AOI) orientation detection
class EnhancedDocumentComparator(DocumentComparator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation_detector = OrientationDetector()
    
    def align_images(self, orig_img, film_img):
        # Use Automated Optical Inspection (AOI) orientation detection instead of basic rotation detection
        orientation_result = self.orientation_detector.detect_orientation(orig_img, film_img)
        aligned_film = self.orientation_detector.apply_detected_orientation(film_img, orientation_result)
        
        return orig_img, aligned_film, orientation_result
```

### API Integration

```python
# RESTful API endpoint example
from flask import Flask, request, jsonify
from scanner.AOI.orientation import OrientationDetector
import base64
import cv2
import numpy as np

app = Flask(__name__)
detector = OrientationDetector()

@app.route('/detect_orientation', methods=['POST'])
def detect_orientation_api():
    data = request.json
    
    # Decode base64 images
    original_data = base64.b64decode(data['original_image'])
    reproduction_data = base64.b64decode(data['reproduction_image'])
    
    # Convert to numpy arrays
    original_img = cv2.imdecode(np.frombuffer(original_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    reproduction_img = cv2.imdecode(np.frombuffer(reproduction_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    
    # Detect orientation
    result = detector.detect_orientation(original_img, reproduction_img)
    
    return jsonify({
        'rotation': result['final_rotation'],
        'confidence': result['final_confidence'],
        'quality': result['quality']
    })
```

## Testing

### Running Tests

```bash
# Run all tests
cd scanner/AOI/orientation
python test_orientation.py

# Run with specific verbosity
python test_orientation.py 2

# Run specific test class
python -m unittest test_orientation.TestOrientationDetector

# Run with coverage (if coverage.py is installed)
coverage run test_orientation.py
coverage report
```

### Test Coverage

The test suite includes:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Speed and memory usage validation
- **Edge Case Tests**: Handling of unusual inputs
- **Visualization Tests**: Output file generation and validation

### Validation Data

Test cases include:

- Synthetic document images with known rotations
- Real microfilm scan samples
- Various document types (text, diagrams, mixed content)
- Different image qualities and resolutions
- Edge cases (blank pages, very noisy images)

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository_url>
cd micro/scanner/AOI/orientation

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python test_orientation.py

# Run linting
flake8 *.py
black *.py
```

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Include comprehensive docstrings
- Write unit tests for new functionality
- Update documentation for API changes

### Submitting Changes

1. Create feature branch
2. Implement changes with tests
3. Run full test suite
4. Update documentation
5. Submit pull request with detailed description

## License and Credits

This orientation detection system is part of the microfilm quality assessment project. It builds upon established computer vision techniques and libraries:

- **OpenCV**: Computer vision and image processing
- **scikit-image**: Image analysis algorithms
- **NumPy/SciPy**: Numerical computing
- **Matplotlib**: Visualization and plotting

## Support and Contact

For questions, issues, or contributions:

- Create GitHub issues for bugs or feature requests
- Check existing documentation and examples
- Review test cases for usage patterns
- Contact the development team for integration support

---

*Last updated: November 2024*
