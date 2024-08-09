"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt
from shapely import Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Align, Cylinder, GeomType, Box, Axis,
                offset, Rectangle, Sketch, GridLocations, PolarLocations,
                sweep, Compound, export_stl, Sphere, Locations)
from ocp_vscode import show, Camera
from bank_config import BankConfig
from geometry_utils import point_distance,find_related_point_by_x
from basic_shapes import rounded_cylinder, top_rounded_cylinder
from filament_channels import (curved_filament_path_solid,
                straight_filament_path_solid,
                straight_filament_connector_threads,curved_filament_connector_threads,
                curved_filament_path, straight_filament_path)

config = BankConfig()

# inner_edge_distance = config.wheel_radius - \
#     config.connection_foundation_mid
# outer_edge_distance = config.wheel_radius + \
#     config.connection_foundation_mid
# inner_angled_distance = inner_edge_distance*sqrt(2)/2
# outer_angled_distance = outer_edge_distance*sqrt(2)/2

# inner_bottom_corner =  Point(inner_angled_distance, -inner_angled_distance)
# outer_bottom_corner =  Point(outer_angled_distance, -outer_angled_distance)
# inner_top_corner= find_related_point_by_distance(inner_bottom_corner,
#                                 config.tube_length, 45)
# outer_top_corner = find_related_point_by_distance(outer_bottom_corner,
#                                 config.tube_length, 45)
# bracket_width = abs(inner_bottom_corner.y) - abs(inner_top_corner.y)

def wheel_guide_cut() -> Part:
    """
    the cutout shape for a wheel guide
    """
    with BuildPart() as wheelcut:
        base_radius=config.wheel_radius + \
                config.wheel_radial_tolerance
        with BuildSketch():
            Circle(base_radius*.8)
            offset(amount=config.wheel_support_height)
        with BuildSketch(Plane.XY.offset(config.wheel_support_height)):
            Circle(base_radius*.8)
        loft()
    return wheelcut.part

def bracket_spoke() -> Part:
    """
    returns the spoke Sketch for the filament wheel
    """
    spoke_outer_radius = (config.wheel_radius+config.bearing_shelf_radius+ \
                          config.wheel_support_height)/2+config.wheel_radial_tolerance+1
    spoke_shift = config.wheel_radius-config.bearing_shelf_diameter*2
    with BuildPart() as spoke:
        with BuildSketch() as sketch:
            with BuildLine():
                l1=CenterArc(center=((spoke_shift,0)), radius=spoke_outer_radius,
                            start_angle=0, arc_size=180)
                l2=CenterArc(center=((spoke_shift,0)),
                            radius=spoke_outer_radius-config.bearing_shelf_diameter,
                            start_angle=0, arc_size=180)
                Line(l1 @ 0, l2 @ 0)
                Line(l1 @ 1, l2 @ 1)
            make_face()
        extrude(sketch.sketch,config.wheel_support_height)
    return spoke.part

def cut_spokes() -> Part:
    """
    returns the wheel spokes cut down to the correct size
    """
    with BuildPart() as spokes:
        #design A
        # with PolarLocations(config.wheel_radius/2+config.bearing_shelf_radius,2):
        #     Cylinder(radius=config.wheel_radius/2+config.bearing_shelf_diameter, height=config.spoke_depth,
        #         align=(Align.CENTER, Align.CENTER, Align.MIN))
        #     Cylinder(radius=config.wheel_radius/2, height=config.spoke_depth,
        #         align=(Align.CENTER, Align.CENTER, Align.MIN),
        #         mode=Mode.SUBTRACT)
        #design B
        with PolarLocations(0,3,start_angle=45):
            add(bracket_spoke())
        with BuildPart(mode=Mode.INTERSECT):
           add(wheel_guide_cut())
    return spokes.part

def spoke_assembly() -> Part:
    """
    adds the axle for the filament wall bearing, along with the spokes
    """
    with BuildPart() as constructed_brace:
        add(cut_spokes())
        Cylinder(radius=config.bearing_shelf_radius,
                        height=config.bearing_shelf_height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(radius=config.bearing_inner_radius,
                        height=config.bracket_depth/2 - \
                            config.wheel_lateral_tolerance,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = constructed_brace.part
    part.label = "spoke assembly"
    return part


def wheel_guide() -> Part:
    """
    The part responsible for guiding the filament wheel and keeping it straight
    """
    base_radius=config.wheel_radius + \
                    config.wheel_radial_tolerance

    with BuildPart() as wheel_brace:
        with BuildPart():
            with BuildSketch():
                Circle(base_radius)
                offset(amount=config.wheel_support_height)
            with BuildSketch(Plane.XY.offset(config.wheel_support_height)):
                Circle(base_radius)
            loft()
        with BuildPart(mode=Mode.SUBTRACT):
            add(wheel_guide_cut())
    part = wheel_brace.part
    part.label = "rim"
    return part

def sweep_cut() -> Part:
    """
    the cut for the clip point on the back of the top frame
    to easily slide through
    """
    # arc_radius = point_distance(config.frame_click_sphere_point,
    #             config.frame_clip_point)
    # x_distance = config.frame_clip_point.x + \
    #     abs(config.frame_click_sphere_point.x)
    # top_angle = 180-x_point_to_angle(radius=arc_radius, x_position=x_distance)
    # bottom_angle = 180-y_point_to_angle(radius=arc_radius,
    # y_position=abs(config.frame_clip_point.y))

    with BuildPart(mode=Mode.PRIVATE) as cut:
        with BuildLine():
            ln=config.sweep_cut_arc
        with BuildSketch(Plane(origin=ln @ 0, z_dir=ln % 0)):
            Circle(config.sweep_cut_width/2)
        sweep()

    return cut.part

def top_cut_shape(offset:float=0) -> Sketch:
    """
    returns a 2d scetch of the basic shape used for the top cutout
    of the filament bracket
    """
    base_outer_radius = config.wheel_radius + \
                    config.wheel_radial_tolerance + \
                    config.wheel_support_height + offset
    with BuildSketch(mode=Mode.PRIVATE) as base_template:
        Circle(base_outer_radius)
        Rectangle(base_outer_radius*2,config.bracket_height*2,
                  align=(Align.CENTER,Align.MAX,Align.MIN))
        Rectangle(base_outer_radius,config.bracket_height*2,
                  align=(Align.CENTER,Align.MIN,Align.MIN))
    return base_template.sketch

def top_cut_template(tolerance:float=0) -> Part:
    """
    returns the shape defining the top cut of the bracket
    (the part that slides into place to hold the filament wheel in place)
    provide a tolerance for the actual part to make it easier to assemble
    """
    with BuildPart() as cut:
        with BuildSketch():
            add(top_cut_shape(tolerance))
        with BuildSketch(Plane.XY.offset(config.wheel_support_height)) as base:
            add(top_cut_shape(tolerance+config.wheel_support_height))
        loft()
    return cut.part

def bracket_clip() -> Part:
    """
    the part for locking the frame bracket into the frame
    """
    clip_height = find_related_point_by_x(Point(0,0), config.frame_bracket_exterior_radius,angle=5).y
    with BuildPart(mode=Mode.PRIVATE) as rails:
        with BuildPart(Plane.XZ):
            Cylinder(radius=config.frame_bracket_exterior_radius-config.fillet_radius, height=config.bracket_depth+config.wall_thickness*.75,arc_size=5,
                align=(Align.MIN,Align.MIN,Align.CENTER),rotation=(0,0,-2.5))
        with BuildPart(Location((config.frame_bracket_exterior_radius-config.wall_thickness-config.bracket_depth,0,0)),mode=Mode.INTERSECT):
            with GridLocations(0,config.bracket_depth+config.wall_thickness*.75,1,2):
                Cylinder(radius=clip_height*.5,height=config.bracket_depth,
                         align=(Align.CENTER,Align.CENTER,Align.MAX), rotation = (0,-90,0))
                Sphere(radius=clip_height/2)
    with BuildPart(Plane.XZ, mode=Mode.PRIVATE) as clip:
        Cylinder(radius=config.frame_bracket_exterior_radius, height=config.bracket_depth+config.wall_thickness*.75,arc_size=5,
                align=(Align.MIN,Align.MIN,Align.CENTER))
        fillet(clip.edges().filter_by(GeomType.CIRCLE), config.fillet_radius)
        with BuildPart(Plane.XZ,mode=Mode.SUBTRACT) as cut:
            Cylinder(radius=config.frame_bracket_exterior_radius-config.wall_thickness, height=config.bracket_depth-config.wall_thickness,arc_size=5,
                    align=(Align.MIN,Align.MIN,Align.CENTER))
            fillet(cut.edges().filter_by(GeomType.CIRCLE), config.fillet_radius)
            Cylinder(radius=config.frame_bracket_exterior_radius-config.fillet_radius, height=config.bracket_depth+config.wall_thickness*.75,arc_size=5,
                    align=(Align.MIN,Align.MIN,Align.CENTER))
        add(rails.part.rotate(Axis.X,90).rotate(Axis.Z,2.5))
    part = clip.part
    part.label = "Bracket Clip"
    return part

def bottom_bracket_block(offset=0) -> Part:
    with BuildPart() as arch:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((0,0), config.frame_bracket_exterior_radius+offset, start_angle=0, arc_size=180)
                Line(arc@0,arc@1)
            make_face()
        extrude(amount=config.bracket_depth+offset*2)
        fillet(arch.edges(),
            config.fillet_radius)
    with BuildPart(Location((config.wheel_radius,0,0))) as egresspath:
        add(curved_filament_path_solid(top_exit_fillet=True))
    with BuildPart(Location((-config.wheel_radius,0,0))) as ingresspath:
        add(straight_filament_path_solid())

    part = Compound(label = "bracket_block", children=[arch.part, egresspath.part, ingresspath.part])
    return part

def pin_channel() -> Part:
    """
    the channel to lock the filament bracket into the back of the top frame
    """
    base_unit = (config.wall_thickness+config.frame_bracket_tolerance)
    with BuildPart() as channel:
        add(rounded_cylinder(radius=base_unit, height=config.bracket_depth,align=
                                (Align.CENTER, Align.CENTER, Align.MIN)))
        with BuildPart(Location((0,0,-config.bracket_depth/2))) as guide:
            Cylinder(radius=config.bracket_depth, height=base_unit*2,rotation=(0,90,0))
            fillet(guide.edges(), base_unit-config.frame_bracket_tolerance/2)
    return channel.part

def bottom_bracket(draft:bool = False) -> Part:
    """
    returns the bottom (main) portion of the filament
    """
    bracket_radius = point_distance(Point(0,0), Point(config.wheel_radius-config.bracket_depth/2, config.bracket_height))
    with BuildPart() as constructed_bracket:
        add(bottom_bracket_block())
        with BuildPart(mode=Mode.SUBTRACT):
            with BuildPart(Location((config.wheel_radius,0,0))):
                add(curved_filament_path_solid(top_exit_fillet=True))
            with BuildPart(Location((-config.wheel_radius,0,0))):
                add(straight_filament_path_solid())
        with BuildPart(Location((config.wheel_radius,0,0)), mode=Mode.ADD):
            add(curved_filament_path(top_exit_fillet=True))
        with BuildPart(Location((-config.wheel_radius,0,0)), mode=Mode.ADD):
            add(straight_filament_path())
        with BuildPart(mode=Mode.SUBTRACT):
            add(top_cut_template(config.frame_bracket_tolerance).mirror().move(
            Location((0,0,config.bracket_depth))))
            Cylinder(radius=config.wheel_radius + \
                     config.wheel_radial_tolerance,
                     height=config.bracket_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildPart(Location((-config.frame_bracket_exterior_radius,config.bracket_depth,config.bracket_depth/2),(0,90,0))):
                with GridLocations(config.bracket_depth,0,2,1):
                    add(pin_channel())
            with Locations(Location((config.frame_click_sphere_point.x, config.frame_click_sphere_point.y,config.bracket_depth)),
                            Location((config.frame_click_sphere_point.x, config.frame_click_sphere_point.y,0))):
                Sphere(config.frame_click_sphere_radius)
            with BuildPart(Location((0,0,config.bracket_depth/2),(90,config.frame_clip_angle,0))):
                add(bracket_clip())
        add(wheel_guide())
        add(spoke_assembly())
        if not draft:
            add(straight_filament_connector_threads().move(Location((-config.wheel_radius,0,0)))),
            add(curved_filament_connector_threads().move(Location((config.wheel_radius,0,0))))
    part = constructed_bracket.part
    part.label = "bottom bracket"
    return part

def top_bracket(tolerance:float=0) -> Part:
    """
    returns the top slide-in part for the filament bracket
    """
    with BuildPart() as frame:
        add(top_cut_template(tolerance))
        with BuildPart(mode=Mode.INTERSECT):
            add(bottom_bracket(draft=True).mirror(Plane.YZ))
        add(wheel_guide())
        add(spoke_assembly().mirror(Plane.YZ))
        with BuildPart(Location((0,0,config.bracket_depth/2),(90,180-config.frame_clip_angle,0)), mode=Mode.SUBTRACT):
            add(bracket_clip())

    part = frame.part
    part.label = "top bracket"
    return part

if __name__ == '__main__':
    bottom = bottom_bracket(draft=False)
    top = top_bracket()
    show(bottom.move(Location((config.bracket_width/2+5,0,0))),
         top.move(Location((-config.bracket_width/2+5,0,0))),
         reset_camera=Camera.KEEP)
    export_stl(bottom, '../stl/filament_bracket_bottom.stl')
    export_stl(top, '../stl/filament_bracket_top.stl')
