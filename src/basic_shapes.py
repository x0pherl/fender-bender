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

def top_rounded_cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.CENTER)) -> Part:
    """
    creates a cylinder with a rounded off top
    """
    with BuildPart() as cylinder:
        Cylinder(radius=radius, height=height,align=align)
        fillet(cylinder.faces().sort_by(Axis.Z)[-1].edges(),
               radius = radius)
    return cylinder.part

def sidewall_shape(inset=0, length=config.sidewall_section_depth, straignt_inset=0) -> Sketch:
    """
    the shape of the sidewall at the defined length
    """
    with BuildSketch(mode=Mode.PRIVATE) as wall:
        Rectangle(width=config.sidewall_width-inset*2-straignt_inset*2,
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

def frame_flat_sidewall_cut(thickness=config.wall_thickness) -> Part:
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


def frame_arched_sidewall_cut(thickness=config.wall_thickness) -> Part:
    """
    a template to subtract in order to create the groove for fitting the side wall
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
    # show(frame_arched_sidewall_cut(thickness=config.wall_thickness), reset_camera=Camera.KEEP)
