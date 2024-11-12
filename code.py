
import FreeCAD
import Part
import Sketcher
import Import
import Mesh
import importDXF
import math

def create_gear_sketch(doc, module, teeth, pressure_angle=20, bore_diameter=5):
    """
    Create a gear sketch.

    Parameters:
    - doc: FreeCAD document object.
    - module: Gear module.
    - teeth: Number of teeth.
    - pressure_angle: Pressure angle (default is 20 degrees).
    - bore_diameter: Diameter of the gear center hole (default is 5mm).
    """
    # Create a new sketch
    sketch = doc.addObject("Sketcher::SketchObject", "GearSketch")

    # Calculate basic gear parameters
    teeth *= 2
    pitch_diameter = module * teeth
    pitch_radius = pitch_diameter / 2
    addendum = module
    dedendum = 1.25 * module
    outer_radius = pitch_radius + addendum
    root_radius = pitch_radius - dedendum

    # Create the center hole of the gear
    sketch.addGeometry(Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), bore_diameter / 2), False)

    # Create each tooth as a trapezoid
    tooth_angle = 360 / teeth
    first_p1 = None
    prev_p4 = None
    for i in range(teeth):
        if i % 2 == 1:  # Skip every other tooth to create a gap
            continue
        angle = i * tooth_angle
        next_angle = angle + tooth_angle

        # Calculate the four points of the tooth (simplified as a trapezoid)
        p1 = FreeCAD.Vector(root_radius * math.cos(math.radians(angle)), root_radius * math.sin(math.radians(angle)), 0)
        p2 = FreeCAD.Vector(outer_radius * math.cos(math.radians(angle)), outer_radius * math.sin(math.radians(angle)), 0)
        p3 = FreeCAD.Vector(outer_radius * math.cos(math.radians(next_angle)), outer_radius * math.sin(math.radians(next_angle)), 0)
        p4 = FreeCAD.Vector(root_radius * math.cos(math.radians(next_angle)), root_radius * math.sin(math.radians(next_angle)), 0)

        if first_p1 is None:
            first_p1 = p1

        # Create three edges of the tooth (do not connect the inner edge)
        sketch.addGeometry(Part.LineSegment(p1, p2), False)
        sketch.addGeometry(Part.LineSegment(p2, p3), False)
        sketch.addGeometry(Part.LineSegment(p3, p4), False)

        # Connect the inner edges between adjacent teeth
        if prev_p4 is not None:
            if prev_p4 != p1:
                sketch.addGeometry(Part.LineSegment(prev_p4, p1), False)
        prev_p4 = p4

    # Connect the last inner edge to the first tooth
    if prev_p4 != first_p1:
        sketch.addGeometry(Part.LineSegment(prev_p4, first_p1), False)

    # Recompute the document
    doc.recompute()

    return sketch

def create_gear(doc, sketch, width):
    """
    Create a gear solid by extruding the sketch.

    Parameters:
    - doc: FreeCAD document object.
    - sketch: Gear sketch object.
    - width: Width of the gear.
    """
    # Extrude the sketch using Part's Extrusion feature
    extrude = doc.addObject("Part::Extrusion", "GearExtrude")
    extrude.Base = sketch  # Set the sketch to be extruded
    extrude.Dir = FreeCAD.Vector(0, 0, width)  # Set the extrusion direction and width
    extrude.Solid = True  # Create a solid
    extrude.TaperAngle = 0.0  # No taper

    # Recompute the document
    doc.recompute()

    return extrude

# Create a new document
doc = FreeCAD.newDocument("GearExample")

# Create first gear sketch
module = 2
teeth = 20
width = 10
sketch1 = create_gear_sketch(doc, module, teeth)

# Create first gear solid from the sketch
gear1 = create_gear(doc, sketch1, width)

# Calculate spacing based on the radius
pitch_diameter = module * teeth * 2
spacing = pitch_diameter

# Create second gear sketch with translation
sketch2 = create_gear_sketch(doc, module, teeth)
sketch2.Placement.Base = FreeCAD.Vector(spacing, 0, 0)

# Create second gear solid from the sketch
gear2 = create_gear(doc, sketch2, width)

# Save as FCStd file
doc.saveAs("output.FCStd")
# Export sketch and STL files
importDXF.export([sketch1, sketch2], "output.dxf")
Mesh.export([gear1, gear2], "output.stl")
