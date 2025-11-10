"""
Guilloche Pattern Generator

Generates intricate guilloche patterns based on mathematical principles,
similar to those found on currency (dollar/euro bills). These patterns
are created using epitrochoids, hypotrochoids, and other parametric curves.
"""

import numpy as np
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GuillocheParams:
    """Parameters for guilloche pattern generation."""
    # Pattern type: 'epitrochoid', 'hypotrochoid', 'lissajous', 'rose', 'combined'
    pattern_type: str = 'epitrochoid'
    
    # Base parameters
    center_x: float = 0.0
    center_y: float = 0.0
    scale: float = 1.0
    
    # Epitrochoid/Hypotrochoid parameters
    R: float = 100.0  # Fixed circle radius
    r: float = 30.0   # Rolling circle radius
    d: float = 50.0   # Distance from rolling circle center to drawing point
    
    # Lissajous parameters
    a: float = 3.0    # Frequency ratio x
    b: float = 2.0    # Frequency ratio y
    phase: float = 0.0  # Phase shift
    
    # Rose curve parameters
    k: float = 5.0    # Number of petals (if integer) or pattern complexity
    amplitude: float = 100.0
    
    # Visual parameters
    line_width: float = 0.5
    color: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # RGB 0-1
    num_points: int = 2000  # Number of points in curve
    
    # Pattern density/overlay
    num_layers: int = 1      # Number of pattern layers
    layer_rotation: float = 0.0  # Rotation between layers (degrees)
    layer_scale: float = 1.0     # Scale factor between layers
    
    # Tiling/repetition
    tile_x: int = 1
    tile_y: int = 1
    tile_spacing_x: float = 0.0
    tile_spacing_y: float = 0.0


class GuillocheGenerator:
    """Generator for guilloche patterns."""
    
    def __init__(self, params: Optional[GuillocheParams] = None):
        """Initialize with parameters."""
        self.params = params or GuillocheParams()
    
    def generate_epitrochoid(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate epitrochoid curve.
        x = (R + r) * cos(t) - d * cos((R + r) / r * t)
        y = (R + r) * sin(t) - d * sin((R + r) / r * t)
        """
        R, r, d = self.params.R, self.params.r, self.params.d
        x = (R + r) * np.cos(t) - d * np.cos((R + r) / r * t)
        y = (R + r) * np.sin(t) - d * np.sin((R + r) / r * t)
        return x * self.params.scale, y * self.params.scale
    
    def generate_hypotrochoid(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate hypotrochoid curve.
        x = (R - r) * cos(t) + d * cos((R - r) / r * t)
        y = (R - r) * sin(t) - d * sin((R - r) / r * t)
        """
        R, r, d = self.params.R, self.params.r, self.params.d
        x = (R - r) * np.cos(t) + d * np.cos((R - r) / r * t)
        y = (R - r) * np.sin(t) - d * np.sin((R - r) / r * t)
        return x * self.params.scale, y * self.params.scale
    
    def generate_lissajous(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Lissajous curve.
        x = A * sin(a * t + phase)
        y = B * sin(b * t)
        """
        a, b = self.params.a, self.params.b
        phase = math.radians(self.params.phase)
        amplitude = self.params.amplitude * self.params.scale
        x = amplitude * np.sin(a * t + phase)
        y = amplitude * np.sin(b * t)
        return x, y
    
    def generate_rose(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate rose curve (rhodonea).
        r = A * cos(k * t)
        x = r * cos(t)
        y = r * sin(t)
        """
        k = self.params.k
        amplitude = self.params.amplitude * self.params.scale
        r = amplitude * np.cos(k * t)
        x = r * np.cos(t)
        y = r * np.sin(t)
        return x, y
    
    def generate_combined(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Generate combined pattern (epitrochoid + hypotrochoid overlay)."""
        x1, y1 = self.generate_epitrochoid(t)
        x2, y2 = self.generate_hypotrochoid(t * 1.5)  # Different frequency
        # Combine with offset
        x = (x1 + x2 * 0.5) * 0.7
        y = (y1 + y2 * 0.5) * 0.7
        return x, y
    
    def generate_pattern(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate the complete pattern based on current parameters.
        
        Returns:
            List of (x, y) coordinate arrays for each layer
        """
        # Generate parameter array
        t = np.linspace(0, 2 * np.pi * self.params.num_layers, 
                       self.params.num_points * self.params.num_layers)
        
        patterns = []
        
        for layer in range(self.params.num_layers):
            # Calculate rotation for this layer
            rotation = math.radians(self.params.layer_rotation * layer)
            scale_factor = self.params.layer_scale ** layer
            
            # Generate base pattern
            if self.params.pattern_type == 'epitrochoid':
                x, y = self.generate_epitrochoid(t)
            elif self.params.pattern_type == 'hypotrochoid':
                x, y = self.generate_hypotrochoid(t)
            elif self.params.pattern_type == 'lissajous':
                x, y = self.generate_lissajous(t)
            elif self.params.pattern_type == 'rose':
                x, y = self.generate_rose(t)
            elif self.params.pattern_type == 'combined':
                x, y = self.generate_combined(t)
            else:
                x, y = self.generate_epitrochoid(t)
            
            # Apply layer transformations
            if scale_factor != 1.0:
                x = x * scale_factor
                y = y * scale_factor
            
            if rotation != 0:
                cos_r = math.cos(rotation)
                sin_r = math.sin(rotation)
                x_rot = x * cos_r - y * sin_r
                y_rot = x * sin_r + y * cos_r
                x, y = x_rot, y_rot
            
            # Translate to center
            x = x + self.params.center_x
            y = y + self.params.center_y
            
            patterns.append((x, y))
        
        return patterns
    
    def generate_tiled_pattern(self, width: float, height: float) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate tiled pattern across specified dimensions.
        
        Args:
            width: Total width of tiled area
            height: Total height of tiled area
            
        Returns:
            List of (x, y) coordinate arrays for all tiles
        """
        all_patterns = []
        
        # Calculate tile dimensions
        tile_width = width / self.params.tile_x
        tile_height = height / self.params.tile_y
        
        # Adjust center for tiling
        original_center_x = self.params.center_x
        original_center_y = self.params.center_y
        
        for tile_y in range(self.params.tile_y):
            for tile_x in range(self.params.tile_x):
                # Calculate tile center
                self.params.center_x = (tile_x + 0.5) * tile_width + tile_x * self.params.tile_spacing_x
                self.params.center_y = (tile_y + 0.5) * tile_height + tile_y * self.params.tile_spacing_y
                
                # Generate pattern for this tile
                patterns = self.generate_pattern()
                all_patterns.extend(patterns)
        
        # Restore original center
        self.params.center_x = original_center_x
        self.params.center_y = original_center_y
        
        return all_patterns


def create_fine_mesh_pattern(width: float, height: float, 
                             density: float = 1.0) -> GuillocheParams:
    """
    Create parameters for a fine mesh pattern similar to currency.
    
    Args:
        width: Pattern width
        height: Pattern height
        density: Pattern density multiplier (0.5-2.0)
    
    Returns:
        GuillocheParams configured for fine mesh
    """
    params = GuillocheParams()
    params.pattern_type = 'combined'
    params.center_x = width / 2
    params.center_y = height / 2
    params.scale = min(width, height) / 400.0 * density
    
    # Fine mesh parameters
    params.R = 50.0 * density
    params.r = 15.0 * density
    params.d = 25.0 * density
    
    params.num_layers = 3
    params.layer_rotation = 30.0
    params.layer_scale = 0.9
    
    params.num_points = 3000
    params.line_width = 0.3
    
    # Tiling for seamless coverage
    params.tile_x = max(1, int(width / (params.R * 2)))
    params.tile_y = max(1, int(height / (params.R * 2)))
    
    return params

