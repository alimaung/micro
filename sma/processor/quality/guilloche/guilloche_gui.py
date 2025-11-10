"""
Guilloche Pattern Visualizer and Control GUI

Interactive application for designing and previewing guilloche patterns
with real-time parameter adjustment.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import math
from typing import Optional
import os

try:
    from .guilloche_generator import GuillocheGenerator, GuillocheParams, create_fine_mesh_pattern
except ImportError:
    from guilloche_generator import GuillocheGenerator, GuillocheParams, create_fine_mesh_pattern


class GuillocheGUI:
    """GUI application for guilloche pattern design."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Guilloche Pattern Designer")
        self.root.geometry("1200x800")
        
        # Pattern generator
        self.generator = GuillocheGenerator()
        self.preview_size = (600, 600)
        self.background_color = (255, 255, 255)  # White
        self.pattern_color = (0, 0, 0)  # Black
        
        # Create UI
        self._create_ui()
        
        # Initial pattern
        self.update_preview()
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Left panel: Controls
        control_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        main_frame.columnconfigure(0, weight=0)
        main_frame.rowconfigure(0, weight=1)
        
        # Right panel: Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        self._create_controls(control_frame)
        self._create_preview(preview_frame)
    
    def _create_controls(self, parent: ttk.Frame):
        """Create control widgets."""
        # Initialize parameter variables dictionary first
        self.param_vars = {}
        
        # Pattern type
        ttk.Label(parent, text="Pattern Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pattern_type_var = tk.StringVar(value="epitrochoid")
        pattern_types = ['epitrochoid', 'hypotrochoid', 'lissajous', 'rose', 'combined']
        pattern_combo = ttk.Combobox(parent, textvariable=self.pattern_type_var, 
                                    values=pattern_types, state="readonly", width=15)
        pattern_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        pattern_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Epitrochoid/Hypotrochoid parameters
        self._create_param_control(parent, "R (Fixed radius):", "R", 1, 100.0, 0.0, 500.0)
        self._create_param_control(parent, "r (Rolling radius):", "r", 2, 30.0, 0.0, 200.0)
        self._create_param_control(parent, "d (Distance):", "d", 3, 50.0, 0.0, 200.0)
        
        # Lissajous parameters
        self._create_param_control(parent, "a (X frequency):", "a", 4, 3.0, 0.1, 10.0)
        self._create_param_control(parent, "b (Y frequency):", "b", 5, 2.0, 0.1, 10.0)
        self._create_param_control(parent, "Phase (degrees):", "phase", 6, 0.0, -180.0, 180.0)
        
        # Rose parameters
        self._create_param_control(parent, "k (Petals/complexity):", "k", 7, 5.0, 0.1, 20.0)
        
        # General parameters
        self._create_param_control(parent, "Amplitude:", "amplitude", 8, 100.0, 10.0, 500.0)
        self._create_param_control(parent, "Scale:", "scale", 9, 1.0, 0.1, 5.0)
        self._create_param_control(parent, "Line Width:", "line_width", 10, 0.5, 0.1, 5.0)
        self._create_param_control(parent, "Points:", "num_points", 11, 2000, 100, 10000)
        
        # Layer parameters
        self._create_param_control(parent, "Layers:", "num_layers", 12, 1, 1, 10)
        self._create_param_control(parent, "Layer Rotation (deg):", "layer_rotation", 13, 0.0, -180.0, 180.0)
        self._create_param_control(parent, "Layer Scale:", "layer_scale", 14, 1.0, 0.1, 2.0)
        
        # Tiling
        self._create_param_control(parent, "Tile X:", "tile_x", 15, 1, 1, 10)
        self._create_param_control(parent, "Tile Y:", "tile_y", 16, 1, 1, 10)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=17, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Fine Mesh Preset", 
                  command=self.load_fine_mesh_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Preview", 
                  command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export PNG", 
                  command=self.export_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export PDF", 
                  command=self.export_pdf).pack(side=tk.LEFT, padx=5)
    
    def _create_param_control(self, parent: ttk.Frame, label: str, param_name: str, 
                             row: int, default: float, min_val: float, max_val: float):
        """Create a parameter control (label + scale)."""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
        
        var = tk.DoubleVar(value=default)
        self.param_vars[param_name] = var
        
        scale = ttk.Scale(parent, from_=min_val, to=max_val, variable=var, 
                         orient=tk.HORIZONTAL, length=200, command=lambda v: self.update_preview())
        scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        value_label = ttk.Label(parent, text=f"{default:.2f}", width=8)
        value_label.grid(row=row, column=2, sticky=tk.W, padx=5)
        
        # Update label when scale changes
        def update_label(v):
            value_label.config(text=f"{float(v):.2f}")
        var.trace_add('write', lambda *args: update_label(var.get()))
    
    def _create_preview(self, parent: ttk.Frame):
        """Create preview canvas."""
        self.preview_canvas = tk.Canvas(parent, width=self.preview_size[0], 
                                       height=self.preview_size[1], bg="white")
        self.preview_canvas.pack()
    
    def _get_params_from_ui(self) -> GuillocheParams:
        """Get current parameters from UI controls."""
        params = GuillocheParams()
        
        params.pattern_type = self.pattern_type_var.get()
        params.R = self.param_vars.get("R", tk.DoubleVar(value=100.0)).get()
        params.r = self.param_vars.get("r", tk.DoubleVar(value=30.0)).get()
        params.d = self.param_vars.get("d", tk.DoubleVar(value=50.0)).get()
        params.a = self.param_vars.get("a", tk.DoubleVar(value=3.0)).get()
        params.b = self.param_vars.get("b", tk.DoubleVar(value=2.0)).get()
        params.phase = self.param_vars.get("phase", tk.DoubleVar(value=0.0)).get()
        params.k = self.param_vars.get("k", tk.DoubleVar(value=5.0)).get()
        params.amplitude = self.param_vars.get("amplitude", tk.DoubleVar(value=100.0)).get()
        params.scale = self.param_vars.get("scale", tk.DoubleVar(value=1.0)).get()
        params.line_width = self.param_vars.get("line_width", tk.DoubleVar(value=0.5)).get()
        params.num_points = int(self.param_vars.get("num_points", tk.DoubleVar(value=2000)).get())
        params.num_layers = int(self.param_vars.get("num_layers", tk.DoubleVar(value=1)).get())
        params.layer_rotation = self.param_vars.get("layer_rotation", tk.DoubleVar(value=0.0)).get()
        params.layer_scale = self.param_vars.get("layer_scale", tk.DoubleVar(value=1.0)).get()
        params.tile_x = int(self.param_vars.get("tile_x", tk.DoubleVar(value=1)).get())
        params.tile_y = int(self.param_vars.get("tile_y", tk.DoubleVar(value=1)).get())
        
        # Center in preview
        params.center_x = self.preview_size[0] / 2
        params.center_y = self.preview_size[1] / 2
        
        return params
    
    def update_preview(self):
        """Update the preview canvas with current pattern."""
        try:
            # Get parameters
            params = self._get_params_from_ui()
            self.generator.params = params
            
            # Generate pattern
            if params.tile_x > 1 or params.tile_y > 1:
                patterns = self.generator.generate_tiled_pattern(
                    self.preview_size[0], self.preview_size[1])
            else:
                patterns = self.generator.generate_pattern()
            
            # Create image
            img = Image.new('RGB', self.preview_size, self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw patterns
            for x_arr, y_arr in patterns:
                points = []
                for i in range(len(x_arr)):
                    x = float(x_arr[i])
                    y = float(y_arr[i])
                    # Clamp to image bounds
                    x = max(0, min(self.preview_size[0] - 1, x))
                    y = max(0, min(self.preview_size[1] - 1, y))
                    points.append((x, y))
                
                # Draw as connected lines
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        draw.line([points[i], points[i + 1]], 
                                 fill=self.pattern_color, 
                                 width=int(max(1, params.line_width)))
            
            # Update canvas
            photo = ImageTk.PhotoImage(img)
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.preview_canvas.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate pattern: {str(e)}")
    
    def load_fine_mesh_preset(self):
        """Load fine mesh preset (currency-like pattern)."""
        params = create_fine_mesh_pattern(self.preview_size[0], self.preview_size[1])
        
        # Update UI controls
        self.pattern_type_var.set(params.pattern_type)
        self.param_vars["R"].set(params.R)
        self.param_vars["r"].set(params.r)
        self.param_vars["d"].set(params.d)
        self.param_vars["amplitude"].set(params.amplitude)
        self.param_vars["scale"].set(params.scale)
        self.param_vars["line_width"].set(params.line_width)
        self.param_vars["num_points"].set(params.num_points)
        self.param_vars["num_layers"].set(params.num_layers)
        self.param_vars["layer_rotation"].set(params.layer_rotation)
        self.param_vars["layer_scale"].set(params.layer_scale)
        self.param_vars["tile_x"].set(params.tile_x)
        self.param_vars["tile_y"].set(params.tile_y)
        
        self.update_preview()
    
    def export_png(self):
        """Export pattern as PNG image."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Get parameters
            params = self._get_params_from_ui()
            
            # Ask for export size
            size_dialog = tk.Toplevel(self.root)
            size_dialog.title("Export Size")
            size_dialog.geometry("300x150")
            
            ttk.Label(size_dialog, text="Width:").grid(row=0, column=0, padx=10, pady=10)
            width_var = tk.IntVar(value=2000)
            ttk.Entry(size_dialog, textvariable=width_var, width=10).grid(row=0, column=1, padx=10, pady=10)
            
            ttk.Label(size_dialog, text="Height:").grid(row=1, column=0, padx=10, pady=10)
            height_var = tk.IntVar(value=2000)
            ttk.Entry(size_dialog, textvariable=height_var, width=10).grid(row=1, column=1, padx=10, pady=10)
            
            export_size = None
            
            def do_export():
                nonlocal export_size
                export_size = (width_var.get(), height_var.get())
                size_dialog.destroy()
            
            ttk.Button(size_dialog, text="Export", command=do_export).grid(row=2, column=0, columnspan=2, pady=10)
            
            size_dialog.wait_window()
            
            if export_size is None:
                return
            
            # Generate pattern at export size
            params.center_x = export_size[0] / 2
            params.center_y = export_size[1] / 2
            self.generator.params = params
            
            if params.tile_x > 1 or params.tile_y > 1:
                patterns = self.generator.generate_tiled_pattern(export_size[0], export_size[1])
            else:
                patterns = self.generator.generate_pattern()
            
            # Create image
            img = Image.new('RGB', export_size, self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw patterns
            for x_arr, y_arr in patterns:
                points = []
                for i in range(len(x_arr)):
                    x = float(x_arr[i])
                    y = float(y_arr[i])
                    x = max(0, min(export_size[0] - 1, x))
                    y = max(0, min(export_size[1] - 1, y))
                    points.append((x, y))
                
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        draw.line([points[i], points[i + 1]], 
                                 fill=self.pattern_color, 
                                 width=int(max(1, params.line_width)))
            
            img.save(filepath, "PNG", dpi=(300, 300))
            messagebox.showinfo("Success", f"Pattern exported to {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_pdf(self):
        """Export pattern as PDF."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.colors import black, white
        except ImportError:
            messagebox.showerror("Error", "reportlab not installed. Install with: pip install reportlab")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Get parameters
            params = self._get_params_from_ui()
            
            # Generate pattern
            width, height = A4
            params.center_x = width / 2
            params.center_y = height / 2
            params.scale = min(width, height) / 400.0
            self.generator.params = params
            
            if params.tile_x > 1 or params.tile_y > 1:
                patterns = self.generator.generate_tiled_pattern(width, height)
            else:
                patterns = self.generator.generate_pattern()
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            c.setFillColor(white)
            c.rect(0, 0, width, height, fill=1, stroke=0)
            
            c.setStrokeColor(black)
            c.setLineWidth(params.line_width)
            
            # Draw patterns
            for x_arr, y_arr in patterns:
                if len(x_arr) > 1:
                    path = c.beginPath()
                    path.moveTo(float(x_arr[0]), float(y_arr[0]))
                    for i in range(1, len(x_arr)):
                        path.lineTo(float(x_arr[i]), float(y_arr[i]))
                    c.drawPath(path)
            
            c.showPage()
            c.save()
            
            messagebox.showinfo("Success", f"Pattern exported to {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = GuillocheGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

