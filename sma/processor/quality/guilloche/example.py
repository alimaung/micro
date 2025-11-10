"""
Example usage of the Guilloche Pattern Generator

This script demonstrates how to generate guilloche patterns programmatically.
"""

from guilloche_generator import GuillocheGenerator, GuillocheParams, create_fine_mesh_pattern
from PIL import Image, ImageDraw
import numpy as np


def example_fine_mesh():
    """Generate a fine mesh pattern (currency-like)."""
    print("Generating fine mesh pattern...")
    
    width, height = 2000, 2000
    params = create_fine_mesh_pattern(width, height, density=1.0)
    generator = GuillocheGenerator(params)
    patterns = generator.generate_pattern()
    
    # Create image
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw patterns
    for x_arr, y_arr in patterns:
        points = []
        for i in range(len(x_arr)):
            x = float(x_arr[i])
            y = float(y_arr[i])
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            points.append((x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=(0, 0, 0), width=1)
    
    img.save("fine_mesh_example.png", "PNG")
    print("Saved to fine_mesh_example.png")


def example_custom_pattern():
    """Generate a custom epitrochoid pattern."""
    print("Generating custom epitrochoid pattern...")
    
    params = GuillocheParams(
        pattern_type='epitrochoid',
        center_x=1000,
        center_y=1000,
        R=100.0,
        r=30.0,
        d=50.0,
        scale=2.0,
        num_points=3000,
        num_layers=3,
        layer_rotation=30.0,
        layer_scale=0.9,
        line_width=0.5
    )
    
    generator = GuillocheGenerator(params)
    patterns = generator.generate_pattern()
    
    width, height = 2000, 2000
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    for x_arr, y_arr in patterns:
        points = []
        for i in range(len(x_arr)):
            x = float(x_arr[i])
            y = float(y_arr[i])
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            points.append((x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=(0, 0, 0), width=1)
    
    img.save("custom_pattern_example.png", "PNG")
    print("Saved to custom_pattern_example.png")


if __name__ == "__main__":
    example_fine_mesh()
    example_custom_pattern()
    print("\nExamples complete! Run 'python guilloche_gui.py' for interactive GUI.")

