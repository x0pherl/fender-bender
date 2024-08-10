"""
Generates the part for the filament bracket of our filament bank design
"""
from shapely import Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Align, Cylinder, GeomType, Axis,
                offset, Rectangle, Sketch, GridLocations, PolarLocations,
                Compound, export_stl, Sphere, Locations)
from ocp_vscode import show, Camera
from bank_config import BankConfig
from geometry_utils import find_related_point_by_x
from basic_shapes import rounded_cylinder
from filament_channels import (curved_filament_path_solid,
                straight_filament_path_solid,
                straight_filament_connector_threads,curved_filament_connector_threads,
                curved_filament_path, straight_filament_path)

config = BankConfig()

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
        #     Cylinder(radius=config.wheel_radius/2+config.bearing_shelf_diameter,
        #         height=config.wheel_radius*.8,
        #         align=(Align.CENTER, Align.CENTER, Align.MIN))
        #     Cylinder(radius=config.wheel_radius/2, height=config.wheel_radius*.8,
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
    The outer ring responsible for guiding the filament wheel and keeping it straight
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

def top_cut_shape(inset:float=0) -> Sketch:
    """
    returns a 2d scetch of the basic shape used for the top cutout
    of the filament bracket
    """
    base_outer_radius = config.wheel_radius + \
                    config.wheel_radial_tolerance + \
                    config.wheel_support_height - inset
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
            add(top_cut_shape(-tolerance))
        with BuildSketch(Plane.XY.offset(config.wheel_support_height)):
            add(top_cut_shape(-tolerance-config.wheel_support_height))
        loft()
    return cut.part

def bracket_clip(inset=0) -> Part:
    """
    the part for locking the frame bracket into the frame
    arguments:
    inset: the amount to push the boundries to the interior of the clip,
    a positive inset results in a larger part, a negative inset is smaller
    """
    clip_height = find_related_point_by_x(Point(0,0),
                        config.frame_bracket_exterior_radius,angle=config.frame_click_arc).y - inset
    with BuildPart(mode=Mode.PRIVATE) as rails:
        with BuildPart(Plane.XZ):
            Cylinder(radius=config.frame_bracket_exterior_radius-config.fillet_radius,
                height=config.bracket_depth+config.wall_thickness*.75,arc_size=config.frame_click_arc,
                align=(Align.MIN,Align.MIN,Align.CENTER),rotation=(0,0,-config.frame_click_arc/2))
        with BuildPart(Location((config.frame_bracket_exterior_radius - \
                            config.wall_thickness-config.bracket_depth-inset,0,0)),
                            mode=Mode.INTERSECT):
            with GridLocations(0,config.bracket_depth+config.wall_thickness*.75-inset,1,2):
                Cylinder(radius=clip_height/2+inset,height=config.bracket_depth,
                         align=(Align.CENTER,Align.CENTER,Align.MAX), rotation = (0,-90,0))
                Sphere(radius=clip_height/2+inset)
    with BuildPart(Plane.XZ) as clip:
        Cylinder(radius=config.frame_bracket_exterior_radius,
                height=config.bracket_depth+config.wall_thickness*.75,arc_size=config.frame_click_arc,
                align=(Align.MIN,Align.MIN,Align.CENTER))
        fillet(clip.edges().filter_by(GeomType.CIRCLE), config.fillet_radius)
        extrude(clip.faces().sort_by(Axis.X)[-1],amount=10,dir=(1,0,1.5))
        edge_set = clip.faces().sort_by(Axis.X)[-1].edges().filter_by(GeomType.CIRCLE)
        fillet(edge_set, clip.part.max_fillet(edge_set, max_iterations=100))
        with BuildPart(Plane.XZ,mode=Mode.SUBTRACT) as cut:
            Cylinder(radius=config.frame_bracket_exterior_radius - \
                    config.wall_thickness-inset,
                    height=config.bracket_depth-config.wall_thickness-inset,arc_size=config.frame_click_arc,
                    align=(Align.MIN,Align.MIN,Align.CENTER))
            fillet(cut.edges().filter_by(GeomType.CIRCLE), config.fillet_radius)
            Cylinder(radius=config.frame_bracket_exterior_radius-config.fillet_radius,
                    height=config.bracket_depth+config.wall_thickness*.75,arc_size=config.frame_click_arc,
                    align=(Align.MIN,Align.MIN,Align.CENTER))
        add(rails.part.rotate(Axis.X,90).rotate(Axis.Z,config.frame_click_arc/2))
    part = clip.part
    part.label = "Bracket Clip"
    return part

def bottom_bracket_block(inset=0) -> Part:
    """
    the basic block shape of the bottom bracket
    """
    with BuildPart() as arch:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((0,0), config.frame_bracket_exterior_radius-inset,
                              start_angle=0, arc_size=180)
                Line(arc@0,arc@1)
            make_face()
        extrude(amount=config.bracket_depth-inset*2)
        fillet(arch.edges(),
            config.fillet_radius)
        with BuildPart(Location((0,0,config.bracket_depth/2),
                        (90,config.frame_clip_angle,0)), mode=Mode.SUBTRACT):
            add(bracket_clip(inset=config.frame_bracket_tolerance/2))
        with BuildPart(Location((config.wheel_radius,0,0)), mode=Mode.SUBTRACT):
            add(curved_filament_path_solid(top_exit_fillet=True))
        with BuildPart(Location((-config.wheel_radius,0,0)),mode=Mode.SUBTRACT):
            add(straight_filament_path_solid())
        with BuildPart(Location((config.wheel_radius,0,0))):
            add(curved_filament_path_solid(top_exit_fillet=True))
        with BuildPart(Location((-config.wheel_radius,0,0))):
            add(straight_filament_path_solid())

    part = arch.part
    part.label = "solid bracket block"
    return part

def pin_channel() -> Part:
    """
    the channel to lock the filament bracket into the back of the top frame
    """
    base_unit = config.wall_thickness+config.frame_bracket_tolerance
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
            with BuildPart(Location((
                            -config.frame_bracket_exterior_radius,
                            config.bracket_depth,config.bracket_depth/2),
                            (0,90,0))):
                with GridLocations(config.bracket_depth,0,2,1):
                    add(pin_channel())
            with Locations(
                    Location((config.frame_click_sphere_point.x,
                              config.frame_click_sphere_point.y,
                              config.bracket_depth)),
                    Location((config.frame_click_sphere_point.x,
                              config.frame_click_sphere_point.y,0))
                    ):
                Sphere(config.frame_click_sphere_radius)
        add(wheel_guide())
        add(spoke_assembly())
        with BuildPart(mode=Mode.SUBTRACT):
            with BuildPart(Location((0,0,config.bracket_depth/2),(90,config.frame_clip_angle,0))):
                add(bracket_clip(inset=config.frame_bracket_tolerance/2))
        if not draft:
            add(straight_filament_connector_threads().move(
                Location((-config.wheel_radius,0,0))))
            add(curved_filament_connector_threads().move(
                Location((config.wheel_radius,0,0))))
    part = constructed_bracket.part
    part.label = "bottom bracket"
    return part

def top_bracket(tolerance:float=0) -> Part:
    """
    returns the top slide-in part for the filament bracket
    """
    with BuildPart() as frame:
        add(bottom_bracket(draft=True).mirror(Plane.YZ))
        with BuildPart(mode=Mode.INTERSECT):
            add(top_cut_template(tolerance))
            Cylinder(radius=config.bearing_shelf_radius, height=config.bracket_depth/2,
                     align=(Align.CENTER,Align.CENTER,Align.MIN))

    part = frame.part
    part.label = "top bracket"
    return part

if __name__ == '__main__':
    bottom = bottom_bracket(draft=False)
    top = top_bracket()
    bracketclip = bracket_clip(inset=-config.frame_bracket_tolerance/2)
    show(bottom.move(Location((config.bracket_width/2+5,0,0))),
         top.move(Location((-config.bracket_width/2+5,0,0))),
         bracketclip.rotate(Axis.X,90).move(
            Location((config.bracket_depth,0,0))).rotate(
            Axis.Z,config.frame_clip_angle).move(
            Location((config.bracket_width/2+5,0,config.bracket_depth/2))),
         reset_camera=Camera.KEEP)
    export_stl(bottom, '../stl/filament-bracket-bottom.stl')
    export_stl(top, '../stl/filament-bracket-top.stl')
    export_stl(bracketclip, '../stl/filament-bracket-clip.stl')
