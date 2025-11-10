# Guilloche Pattern Generator

A Python library and GUI application for generating intricate guilloche patterns based on mathematical principles, similar to the fine mesh patterns found on currency (dollar/euro bills).

## Features

- **Multiple Pattern Types**: Epitrochoids, Hypotrochoids, Lissajous curves, Rose curves, and Combined patterns
- **Interactive GUI**: Real-time preview with parameter adjustment
- **Fine Mesh Preset**: One-click preset for currency-like patterns
- **Export Options**: Export to PNG (high-resolution) or PDF
- **Layered Patterns**: Support for multiple pattern layers with rotation and scaling
- **Tiling**: Generate seamless tiled patterns

## Mathematical Principles

Guilloche patterns are based on parametric curves:

- **Epitrochoid**: Curve traced by a point on a circle rolling around the outside of another circle
- **Hypotrochoid**: Curve traced by a point on a circle rolling inside another circle
- **Lissajous**: Curves formed by combining two perpendicular sinusoidal oscillations
- **Rose (Rhodonea)**: Curves defined by polar equations r = a·cos(k·θ)

## Installation

Required dependencies:
```bash
pip install numpy pillow reportlab
```

For GUI (Tkinter is usually included with Python):
- Windows: Usually pre-installed
- Linux: `sudo apt-get install python3-tk`
- macOS: Usually pre-installed

## Usage

### GUI Application

Run the interactive GUI:
```bash
python guilloche_gui.py
```

Features:
- Adjust parameters in real-time with sliders
- Preview updates automatically
- Use "Fine Mesh Preset" for currency-like patterns
- Export to PNG or PDF

### Programmatic Usage

```python
from guilloche_generator import GuillocheGenerator, GuillocheParams, create_fine_mesh_pattern

# Create fine mesh pattern (currency-like)
params = create_fine_mesh_pattern(width=2000, height=2000, density=1.0)
generator = GuillocheGenerator(params)
patterns = generator.generate_pattern()

# Custom pattern
params = GuillocheParams(
    pattern_type='epitrochoid',
    R=100.0,  # Fixed circle radius
    r=30.0,   # Rolling circle radius
    d=50.0,   # Distance from rolling circle center
    num_points=2000,
    num_layers=3,
    layer_rotation=30.0
)
generator = GuillocheGenerator(params)
patterns = generator.generate_pattern()
```

## Parameters

### Pattern Type
- `epitrochoid`: Classic guilloche pattern
- `hypotrochoid`: Inward rolling pattern
- `lissajous`: Sinusoidal interference pattern
- `rose`: Petal-like patterns
- `combined`: Multiple patterns overlaid

### Epitrochoid/Hypotrochoid Parameters
- `R`: Fixed circle radius
- `r`: Rolling circle radius
- `d`: Distance from rolling circle center to drawing point

### Lissajous Parameters
- `a`: X-axis frequency ratio
- `b`: Y-axis frequency ratio
- `phase`: Phase shift in degrees

### Rose Parameters
- `k`: Number of petals (if integer) or pattern complexity

### Visual Parameters
- `scale`: Overall pattern scale
- `line_width`: Line thickness
- `num_points`: Number of points in curve (higher = smoother)
- `num_layers`: Number of pattern layers
- `layer_rotation`: Rotation between layers (degrees)
- `layer_scale`: Scale factor between layers

## Examples

### Fine Mesh Pattern (Currency-like)
```python
params = create_fine_mesh_pattern(2000, 2000, density=1.0)
generator = GuillocheGenerator(params)
patterns = generator.generate_pattern()
```

### Dense Security Pattern
```python
params = GuillocheParams(
    pattern_type='combined',
    R=50.0,
    r=15.0,
    d=25.0,
    num_layers=5,
    layer_rotation=20.0,
    layer_scale=0.95,
    num_points=5000,
    line_width=0.2
)
```

## Integration with PDF Generation

The guilloche patterns can be integrated into PDF generation (e.g., for microfilm calibration sheets) by replacing the grey circles background with guilloche patterns.

## License

Part of the micro project.

