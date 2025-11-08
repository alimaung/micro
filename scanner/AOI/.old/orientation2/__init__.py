"""
Automated Optical Inspection (AOI) Orientation Detection Package

This package provides comprehensive orientation detection capabilities for 
comparing original documents with their microfilm reproductions.

Main Components:
- OrientationDetector: Core detection algorithms
- OrientationVisualizer: Visualization and reporting tools
- OrientationConfig: Configuration management
- Test suite and examples

Usage:
    from scanner.AOI.orientation import OrientationDetector, OrientationVisualizer
    
    detector = OrientationDetector()
    result = detector.detect_orientation(original_img, reproduction_img)
    
    visualizer = OrientationVisualizer()
    visualizer.create_orientation_comparison(original_img, reproduction_img, result)
"""

from orientation_detector import (
    OrientationDetector,
    OrientationConfig,
    create_default_config,
    load_config,
    save_config
)

from orientation_visualizer import (
    OrientationVisualizer,
    create_batch_visualization
)

__version__ = "1.0.0"
__author__ = "Microfilm Quality Assessment Team"

__all__ = [
    'OrientationDetector',
    'OrientationConfig', 
    'OrientationVisualizer',
    'create_default_config',
    'load_config',
    'save_config',
    'create_batch_visualization'
]
