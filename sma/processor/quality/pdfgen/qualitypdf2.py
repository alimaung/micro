from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
import math

def create_densitometer_calibration_sheet(filename="microfilm_densitometer_calibration.pdf"):
    width, height = A4
    c = canvas.Canvas(filename, pagesize=A4)
    
    # Layout parameters
    margin = 15 * mm
    center_x, center_y = width / 2, height / 2
    circle_diameter = width * 0.60
    circle_radius = circle_diameter / 2

    # --- Guidelines (radials, crosshairs, diagonals) ---
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.3)

    # Crosshairs (extend full page)
    c.line(margin, center_y, width - margin, center_y)
    c.line(center_x, margin, center_x, height - margin)

    # Extended diagonals (through full page, skipping center circle)
    def draw_diag(angle_deg):
        angle = math.radians(angle_deg)
        # top/bottom intersection points
        for direction in [1, -1]:
            x1 = center_x + circle_radius * math.cos(angle)
            y1 = center_y + circle_radius * math.sin(angle)
            x2 = center_x + direction * 2000 * math.cos(angle)
            y2 = center_y + direction * 2000 * math.sin(angle)
            c.line(x1, y1, x2, y2)

    for a in [45, -45, 90, 180]:  # added extra at 60°
        draw_diag(a)

    # Concentric circles every 10 mm beyond the white center circle
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.3)
    max_radius = radius = 2 * max(width, height)
    step = 10 * mm
    r = circle_radius + step
    while r < max_radius:
        c.circle(center_x, center_y, r)
        r += step

    # --- White center circle ---
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.6)
    c.circle(center_x, center_y, circle_radius, fill=1, stroke=1)

    # --- Density Patches (now square) ---
    patch_size = 25 * mm
    greys = [0.0, 0.25, 0.5, 0.75, 0.9]
    spacing = 5 * mm
    total_width = len(greys) * (patch_size + spacing) - spacing
    start_x = center_x - total_width / 2

    # Above circle
    y_above = center_y + circle_radius + 20 * mm
    for i, g in enumerate(greys):
        c.setFillColorRGB(g, g, g)
        x = start_x + i * (patch_size + spacing)
        c.rect(x, y_above, patch_size, patch_size, fill=1, stroke=1)

    # Below circle
    y_below = center_y - circle_radius - 20 * mm - patch_size
    for i, g in enumerate(greys):
        c.setFillColorRGB(g, g, g)
        x = start_x + i * (patch_size + spacing)
        c.rect(x, y_below, patch_size, patch_size, fill=1, stroke=1)

    # --- Registration marks (no overlap at corners) ---
    c.setStrokeColor(colors.black)
    reg_mark_size = 5 * mm
    for (x, y) in [(margin, margin), (margin, height - margin),
                   (width - margin, margin), (width - margin, height - margin)]:
        c.line(x - reg_mark_size, y, x + reg_mark_size, y)
        c.line(x, y - reg_mark_size, x, y + reg_mark_size)

        # --- Border ---
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.rect(margin, margin, width - 2*margin, height - 2*margin)

    # --- Scales (mm) ---
    c.setFont("Helvetica", 4)
    tick_length = 2 * mm

    # Horizontal scales
    for x in range(10, int(width/mm), 10):
        xpos = x * mm
        if margin <= xpos <= width - margin:
            # Top
            c.line(xpos, height - margin, xpos, height - margin - tick_length)
            # Bottom
            c.line(xpos, margin, xpos, margin + tick_length)
            if x % 20 == 0:
                label = str(x)
                c.drawCentredString(xpos, height - margin + 2, label)
                c.drawCentredString(xpos, margin - 6, label)

    # Vertical scales
    for y in range(10, int(height/mm), 10):
        ypos = y * mm
        if margin <= ypos <= height - margin:
            # Left
            c.line(margin, ypos, margin + tick_length, ypos)
            # Right
            c.line(width - margin, ypos, width - margin - tick_length, ypos)
            if y % 20 == 0:
                label = str(y)
                c.drawRightString(margin - 2, ypos - 1, label)
                c.drawString(width - margin + 2, ypos - 1, label)

    # --- Crosshair patterns on second radius circle ---
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.4)
    crosshair_length = 8 * mm
    
    # Second radius circle (first circle beyond the white center circle)
    second_radius = circle_radius + step  # circle_radius + 10mm
    
    # Define 10 crosshair positions (angles in degrees, measured from positive x-axis)
    # Left, Right, Top, Bottom, and 45°/90°/180° aligned with diagonals
    crosshair_angles = [
        180,    # Left (aligns with 180° diagonal)
        0,      # Right
        90,     # Top (aligns with 90° diagonal)
        270,    # Bottom
        45,     # 45° top-right (aligns with 45° diagonal)
        135,    # 135° top-left (180-45)
        -45,    # -45° bottom-right (aligns with -45° diagonal, same as 315°)
        225,    # 225° bottom-left (180+45)
        30,     # 30° additional position
        150     # 150° additional position
    ]
    
    # Draw crosshairs at each position on the second circle
    for angle_deg in crosshair_angles:
        angle_rad = math.radians(angle_deg)
        x = center_x + second_radius * math.cos(angle_rad)
        y = center_y + second_radius * math.sin(angle_rad)
        
        # Draw crosshair (horizontal and vertical lines)
        c.line(x - crosshair_length/2, y, x + crosshair_length/2, y)
        c.line(x, y - crosshair_length/2, x, y + crosshair_length/2)

    # --- Mirrored annotations (top and bottom) ---
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    annotation_text = "MICROFILM DENSITY TEST CHART"
    
    # Top annotation (normal orientation)
    c.drawCentredString(center_x, height - margin - 8 * mm, annotation_text)
    
    # Bottom annotation (rotated 180 degrees for mirror reading)
    c.saveState()
    c.translate(center_x, margin + 8 * mm)
    c.rotate(180)
    c.drawCentredString(0, 0, annotation_text)
    c.restoreState()

    # --- Finish ---
    c.showPage()
    c.save()
    print(f"PDF saved to {filename}")


if __name__ == "__main__":
    create_densitometer_calibration_sheet()
