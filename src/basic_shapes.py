"""
utility for creating a bar with a zig-zag shape
"""
from build123d import (BuildPart, BuildSketch, BuildLine, Polyline, extrude, make_face,
                       fillet, Axis, Circle, add, Plane, Cylinder, Part, loft, Sketch,
                       Align, Rectangle, Location, Mode, offset, Kind)
from ocp_vscode import show, Camera
from geometry_utils import find_angle_intersection
from bank_config import BankConfig

config = BankConfig()

def rounded_cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.CENTER)) -> Part:
    """
    creates a rounded off cylinder
    """
    with BuildPart() as cylinder:
        Cylinder(radius=radius, height=height,align=align)
        fillet(cylinder.faces().sort_by(Axis.Z)[-1].edges()+
               cylinder.faces().sort_by(Axis.Z)[0].edges(),
               radius = radius)
    return cylinder.part

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

def side_line(bottom_adjust=0,right_adjust=0) -> Sketch:
    """
    creates the sketch for the shape of the sides of the frame
    arguments:
    bottom_adjust: adjusts the bottom line up or down to create a thinner bar
    right_adjust: extends the right angle bar out by this value
    """

    right_bottom_intersection = config.find_point_along_right(
            -config.spoke_height/2)
    right_top_intersection = config.find_point_along_right(
                    -config.spoke_height/2 + config.spoke_bar_height)
    with BuildSketch() as sketch:
        x_distance = find_angle_intersection(config.spoke_depth/2, config.spoke_angle)
        angled_bar_width = find_angle_intersection(config.spoke_bar_height/2, config.spoke_angle)/2
        with BuildLine():
            Polyline(
                (right_top_intersection.x+config.minimum_structural_thickness+right_adjust,
                    right_top_intersection.y),
                (right_bottom_intersection.x+config.minimum_structural_thickness+right_adjust+bottom_adjust,
                    right_bottom_intersection.y+bottom_adjust),
                (x_distance+angled_bar_width-config.spoke_bar_height/2,
                    -config.spoke_depth/2-config.spoke_bar_height/2+bottom_adjust),
                (-x_distance+angled_bar_width-config.spoke_bar_height/2,
                    config.spoke_depth/2-config.spoke_bar_height/2+bottom_adjust),
                (-x_distance+angled_bar_width-config.spoke_bar_height/2-config.minimum_structural_thickness*2,
                    config.spoke_depth/2-config.spoke_bar_height/2+bottom_adjust),
                (-config.spoke_length/2+config.spoke_bar_height,
                    bottom_adjust-config.frame_tongue_depth),
                (-config.spoke_length/2,
                    bottom_adjust-config.frame_tongue_depth),
                (-config.spoke_length/2,
                    config.spoke_depth/2+config.spoke_bar_height/2),
                (-x_distance-angled_bar_width+config.spoke_bar_height/2,
                    config.spoke_depth/2+config.spoke_bar_height/2),
                (x_distance-angled_bar_width+config.spoke_bar_height/2,
                    -config.spoke_depth/2+config.spoke_bar_height/2),
                (right_top_intersection.x+config.minimum_structural_thickness+right_adjust,
                    right_top_intersection.y)
            )
        make_face()
        fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                minimum=-config.spoke_length/4,
                maximum=config.spoke_length/4,
                inclusive=(False, False)), config.spoke_bar_height/2)

        fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                minimum=-config.spoke_length/2+1,
                maximum=-config.spoke_length/4,
                inclusive=(False, False)), config.spoke_bar_height/3)
    return sketch.sketch

def old_frame_side(thickness=config.wall_thickness, channel=False) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    channel: (boolean) -- determines whether to cut a channel in the bottom part of the frame
    """
    mid_adjustor = thickness/4 if channel else 0
    with BuildPart() as side:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(-thickness/2)):
                add(side_line(bottom_adjust=0))
            with BuildSketch(Plane.XY.offset(-thickness/4)):
                add(side_line(bottom_adjust=0))
            with BuildSketch():
                add(side_line(bottom_adjust=mid_adjustor))
            with BuildSketch(Plane.XY.offset(thickness/4)):
                add(side_line(bottom_adjust=0))
            with BuildSketch(Plane.XY.offset(thickness/2)):
                add(side_line(bottom_adjust=0))
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
    part.label = "Frame Side"
    return part

def sidewall_shape(inset=0, length=config.sidewall_section_depth) -> Sketch:
    """
    the shape of the sidewall at the defined length
    """
    with BuildSketch(mode=Mode.PRIVATE) as wall:
        Rectangle(width=config.sidewall_width-inset*2,
            height=length-config.wheel_radius-config.frame_base_depth-inset*2,
            align=(Align.CENTER, Align.MAX))
        if inset>0:
            Rectangle(width=config.wheel_diameter-inset*2, height=-inset,
                align=(Align.CENTER, Align.MIN))
    with BuildSketch() as side:
        Circle(radius=config.wheel_radius-inset)
        with BuildSketch(mode=Mode.SUBTRACT):
            Rectangle(config.wheel_diameter*2,config.wheel_diameter*2, align=(Align.CENTER,Align.MAX))
        Rectangle(width=config.wheel_diameter-inset*2, height=config.frame_base_depth,
                align=(Align.CENTER, Align.MAX))
        add(wall.sketch.move(Location((0,-config.frame_base_depth-inset))))
    return side.sketch.move(Location((0,config.frame_base_depth)))

#todo is this just a duplicate of the sidewall sketch? should it really be a separate thing?
def frame_cut_sketch(offset=0) -> Sketch:
    with BuildSketch(mode=Mode.PRIVATE) as wall:
        Rectangle(width=config.sidewall_width, height=1+offset*2,
            align=(Align.CENTER, Align.MAX))
    with BuildSketch() as side:
        Circle(radius=config.wheel_radius+offset)
        Rectangle(width=config.wheel_diameter+offset*2, height=config.frame_base_depth,
                align=(Align.CENTER, Align.MAX))
        add(wall.sketch.move(Location((0,-config.frame_base_depth+offset))))
    return side.sketch.move(Location((0,config.frame_base_depth)))

def frame_side_flat_cut(thickness=config.wall_thickness) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    """
    mid_adjustor = thickness/2
    with BuildPart() as side:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(-thickness/4)):
                Rectangle(width=config.sidewall_width, height=1,
                    align=(Align.CENTER, Align.MAX))
            with BuildSketch():
                Rectangle(width=config.sidewall_width, height=1+mid_adjustor,
                    align=(Align.CENTER, Align.MAX))
            with BuildSketch(Plane.XY.offset(thickness/4)):
                Rectangle(width=config.sidewall_width, height=1,
                    align=(Align.CENTER, Align.MAX))
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
    part.label = "Frame Side"
    return part


def frame_side_cut(thickness=config.wall_thickness) -> Part:
    """
    builds a side of the frame
    arguments:
    thickness: determines the depth of the wall
    """
    mid_adjustor = thickness/4
    with BuildPart() as side:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(-thickness/4)):
                add(frame_cut_sketch(offset=0))
            with BuildSketch():
                add(frame_cut_sketch(offset=mid_adjustor))
            with BuildSketch(Plane.XY.offset(thickness/4)):
                add(frame_cut_sketch(offset=0))
            loft(ruled=True)
    part = side.part.rotate(Axis.X, 90)
    part.label = "Frame Side"
    return part

if __name__ == '__main__':
    # show(side_line(), reset_camera=Camera.KEEP)
    show(sidewall_shape(), sidewall_shape(inset=9), sidewall_shape(inset=5), reset_camera=Camera.KEEP)
    # show(frame_side_cut(thickness=config.wall_thickness), reset_camera=Camera.KEEP)
