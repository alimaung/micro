# Orientation Module

Detects and corrects rotation differences between original and microfilm images using a two-stage alignment approach.

## Purpose

This module handles the critical task of aligning images that may be rotated relative to each other. Microfilm scans often have orientation issues due to scanning setup, film placement, or digitization processes. This module automatically detects and corrects these rotations to enable accurate quality comparison.

## Usage

```python
from scanner.AOI.orientation.orientation import ImageAligner
import numpy as np

# Initialize aligner
aligner = ImageAligner()

# Align images (orig_img and film_img are grayscale numpy arrays)
aligned_orig, aligned_film, alignment_info = aligner.align_images(orig_img, film_img)

print(f"Applied rotation: {alignment_info['total_rotation']:.1f}°")
print(f"  - Coarse: {alignment_info['coarse_rotation']}°")
print(f"  - Fine: {alignment_info['fine_angle']:.1f}°")

# Use aligned images for comparison
# ...
```

## Two-Stage Alignment Process

### Stage 1: Coarse Rotation Detection
- Tests rotations: 0°, 90°, 180°, 270°
- Uses Canny edge detection for robust matching
- Scores each rotation using SSIM (Structural Similarity Index)
- Selects best rotation based on highest score

### Stage 2: Fine Angle Adjustment
- Tests fine angles from -10° to +10° in 0.5° increments
- Applied after coarse rotation is determined
- Handles slight skew and misalignment
- Uses same edge-based SSIM scoring

## Algorithm Details

1. **Edge Detection**: Uses Canny edge detection to focus on structural features rather than pixel intensity, making matching more robust to brightness/contrast differences

2. **SSIM Scoring**: Structural Similarity Index provides perceptual similarity scoring that's more accurate than pixel-wise comparison

3. **Downsampling**: Works on downsampled images (800px max for coarse, 600px for fine) for speed, then applies transformations to full-resolution images

4. **Image Resizing**: Automatically handles dimension mismatches after rotation

## Features

- Automatic rotation detection (no manual input required)
- Handles both 90° increments and sub-degree adjustments
- Robust to brightness/contrast differences
- Fast processing through intelligent downsampling
- Detailed alignment information for reporting

## Dependencies

- `opencv-python` (cv2) - Image processing and rotation
- `numpy` - Array operations
- `scikit-image` - SSIM calculation

## Performance

- Coarse detection: ~4 rotations tested on downsampled images
- Fine detection: ~40 angles tested (0.5° increments from -10° to +10°)
- Typical processing time: <1 second per page pair (depending on image size)
