"""
utility for creating a bar with a zig-zag shape
"""
from build123d import (BuildPart, BuildSketch, BuildLine, Polyline,
                       make_face, fillet, extrude, Axis)
from geometry_utils import find_angle_intersection

def curvebar(length, bar_width, depth, climb, angle=45):
    """
    returns a zig-zag ish line
    """
    with BuildPart() as curve_part:
        with BuildSketch() as sketch:
            x_distance = find_angle_intersection(climb/2, angle)
            angled_bar_width = find_angle_intersection(bar_width/2, angle)/2
            with BuildLine():
                Polyline(
                    (length/2,-climb/2+bar_width/2),
                    (length/2,-climb/2-bar_width/2),
                    (x_distance+angled_bar_width-bar_width/2,-climb/2-bar_width/2),
                    (-x_distance+angled_bar_width-bar_width/2,climb/2-bar_width/2),
                    (-length/2,climb/2-bar_width/2),
                    (-length/2,climb/2+bar_width/2),
                    (-x_distance-angled_bar_width+bar_width/2,climb/2+bar_width/2),
                    (x_distance-angled_bar_width+bar_width/2, -climb/2+bar_width/2),
                    (length/2,-climb/2+bar_width/2),
                )
            make_face()
            fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                    minimum=-length/2,
                    maximum=length/2,
                    inclusive=(False, False)), bar_width/2)
        extrude(amount=depth)
    curve = curve_part.part
    curve.label = "curvebar"
    return curve