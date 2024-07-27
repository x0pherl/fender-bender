"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt
from shapely import Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Locations, Plane, loft, fillet, Axis, Box, Align, Cylinder,
                offset, Polyline, Rectangle, Sphere, SagittaArc,
                AngularDirection, EllipticalCenterArc, RadiusArc,
                sweep, export_stl)
from ocp_vscode import show
from bd_warehouse.thread import TrapezoidalThread
from bank_config import BankConfig
from geometry_utils import (find_related_point_by_distance, x_point_to_angle,
                            point_distance)
from curvebar import curvebar
from filament_channels import (curved_filament_path_solid, curved_filament_path_cut,
                straight_filament_path_cut, straight_filament_path_solid)

config = BankConfig()

#connector_distance = config.bracket_depth/2 #config.connector_radius+config.minimum_thickness
inner_edge_distance = config.wheel_radius - \
    config.connection_foundation_mid
outer_edge_distance = config.wheel_radius + \
    config.connection_foundation_mid
inner_angled_distance = inner_edge_distance*sqrt(2)/2
outer_angled_distance = outer_edge_distance*sqrt(2)/2

inner_bottom_corner =  Point(inner_angled_distance, -inner_angled_distance)
outer_bottom_corner =  Point(outer_angled_distance, -outer_angled_distance)
inner_top_corner= find_related_point_by_distance(inner_bottom_corner,
                                config.tube_length, 45)
outer_top_corner = find_related_point_by_distance(outer_bottom_corner,
                                config.tube_length, 45)
bracket_width = abs(inner_bottom_corner.y) - abs(inner_top_corner.y)

right_connector_location = Location((config.exit_tube_exit_point.x,
                                    config.exit_tube_exit_point.y,
                                    config.bracket_depth/2),
                                    (90,-45,0))
left_connector_location = Location((-config.wheel_radius,
                                    config.bracket_height,
                                    config.bracket_depth/2), (90,0,0))

def cut_spokes() -> Part:
    """
    returns the wheel spokes cut down to the correct size
    """
    with BuildPart() as spokes:
        add(curvebar(config.spoke_length,
              config.spoke_bar_height,
              config.wheel_support_height,
              config.spoke_depth, config.spoke_angle))
        fillet(spokes.edges(), config.wheel_support_height/4)
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

def left_connector_threads() -> Part:
    """
    returns the threads for the left connector
    """
    with BuildPart(left_connector_location) as left_threads:
        TrapezoidalThread(
                diameter=config.connector_diameter,
                pitch=config.connector_thread_pitch,
                length=config.connector_length,
                thread_angle = config.connector_thread_angle,
                external=False,
                interference=config.connector_thread_interference,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
    part = left_threads.part
    part.label = "left threads"
    return part


def right_connector_threads() -> Part:
    """
    returns the threads for the angled connector
    """
    with BuildPart(right_connector_location) as right_threads:
        TrapezoidalThread(
                diameter=config.connector_radius*2,
                pitch=config.connector_thread_pitch,
                length=config.connector_length,
                thread_angle = config.connector_thread_angle,
                interference=config.connector_thread_interference,
                external=False,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
    part = right_threads.part
    part.label = "right threads"
    return part

def tube_cut(length):
    """
    creates a cutout for a filament tube allowing for the connector, and
    a tube stop with a funnel entry
    """
    with BuildPart() as tube:
        Cylinder(radius=config.connector_radius,
                 height=config.connector_length*2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER))
        Cylinder(radius=config.tube_outer_radius,
                 height=length-config.tube_outer_diameter*3,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

        with BuildPart():
            with BuildSketch(Plane.XY.offset(length-config.tube_outer_diameter*3)):
                Circle(radius=config.tube_inner_radius)
            with BuildSketch(Plane.XY.offset(length)):
                Circle(radius=config.tube_outer_diameter*.75)
                Rectangle(width=config.tube_outer_diameter*2,
                          height=config.bearing_depth + \
                            config.wheel_lateral_tolerance,
                            mode=Mode.INTERSECT)
            loft()
    part = tube.part
    part.label = "tube cut"
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

def top_cut_template(tolerance:float=0) -> Part:
    """
    returns the shape defining the top cut of the bracket
    (the part that slides into place to hold the filament wheel in place)
    provide a tolerance for the actual part to make it easier to assemble
    """
    base_outer_radius = config.wheel_radius + \
                    config.wheel_radial_tolerance + \
                    config.wheel_support_height
    base_rectangle_width = config.bracket_width - \
        (config.fillet_radius + \
         config.connector_diameter + \
            config.wheel_support_height*4)*2
    with BuildPart() as template:
        with BuildSketch():
            with BuildLine():
                start_angle = x_point_to_angle(base_outer_radius-tolerance,
                                               base_rectangle_width/2-tolerance)
                inner_rcurve = CenterArc((0,0), base_outer_radius-tolerance, 0, start_angle)
                inner_lcurve = CenterArc((0,0), base_outer_radius-tolerance, 180-start_angle,
                                         start_angle)
                inner_left_up = Line(inner_rcurve @ 1, (base_rectangle_width/2-tolerance,
                                                        config.bracket_height))
                inner_topline = Line(inner_left_up @ 1, (-base_rectangle_width/2+tolerance,
                                                         config.bracket_height))
                Line(inner_topline @ 1, inner_lcurve @0)
                inner_downl = Line(inner_lcurve @1, (-base_outer_radius+tolerance,
                                                     -config.bracket_height))
                inner_downr = Line(inner_rcurve @0, (base_outer_radius-tolerance,
                                                     -config.bracket_height))
                Line(inner_downl @1, inner_downr @ 1)
            make_face()
        with BuildSketch(Plane.XY.offset(config.wheel_support_height)):
            with BuildLine():
                start_angle = x_point_to_angle(base_outer_radius + \
                                    config.wheel_support_height-tolerance,
                                    base_rectangle_width/2 + \
                                    config.wheel_support_height - \
                                    tolerance)
                outer_rcurve = CenterArc((0,0),
                                base_outer_radius+config.wheel_support_height - \
                                tolerance, 0, start_angle)
                outer_lcurve = CenterArc((0,0),
                                base_outer_radius+config.wheel_support_height - \
                                tolerance, 180-start_angle, start_angle)
                outer_left_up = Line(outer_rcurve @ 1,
                                    (base_rectangle_width/2-tolerance + \
                                    config.wheel_support_height,
                                    config.bracket_height))
                outer_topline = Line(outer_left_up @ 1,
                                    (-base_rectangle_width/2-tolerance - \
                                    config.wheel_support_height,
                                    config.bracket_height))
                Line(outer_topline @ 1, outer_lcurve @0)
                outer_downl = Line(outer_lcurve @1,
                                   (-base_outer_radius - \
                                    config.wheel_support_height + \
                                    tolerance,
                                    -config.bracket_height))
                outer_downr = Line(outer_rcurve @0,
                                    (base_outer_radius + \
                                    config.wheel_support_height - \
                                    tolerance,
                                    -config.bracket_height))
                Line(outer_downl @1, outer_downr @ 1)
            make_face()
        loft()
    return template.part

def support_cut() -> Part:
    """
    the cutout for the angled part tube box to clip into the front of the
    frame bracket
    """

    with BuildPart()as clip_cut:
        with BuildSketch():
            with BuildLine():
                arc=CenterArc((float(config.bracket_clip_point.x), float(config.bracket_clip_point.y)),
                                radius=config.clip_length,
                                start_angle=45, arc_size=90)
                Line(arc @ 1, (float(config.bracket_clip_point.x), float(config.bracket_clip_point.y)))
                Line(arc @ 0, (float(config.bracket_clip_point.x), float(config.bracket_clip_point.y)))
            make_face()
        extrude(amount=config.bracket_depth)
    part =clip_cut
    clip_cut.label = "clip cut"
    return part


def old_bottom_bracket_frame() -> Part:
    """
    returns the outer frame for the bottom bracket
    """
    with BuildPart() as constructed_bracket:
        with BuildPart() as left_bracket:
            with BuildSketch() as block:
                with BuildLine():
                    Polyline((0,0),
                            (-config.bracket_width/2, 0),
                            (-config.bracket_width/2,
                             config.bracket_height),
                            (config.bracket_width/2,
                             config.bracket_height),
                            (config.bracket_width/2,outer_top_corner.y),
                            (inner_bottom_corner.x,inner_bottom_corner.y),
                            (0,0)
                            )
                make_face()
            extrude(block.face(), config.bracket_depth)
            with BuildPart(right_connector_location, mode=Mode.ADD):
                Box(config.bracket_depth, config.bracket_depth,
                    config.tube_length, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(left_bracket.faces().sort_by(Axis.Y)[-1].edges() + \
               left_bracket.faces().sort_by(Axis.X, reverse=True)[0:-1].edges(),
               config.fillet_radius)
        with BuildPart(left_connector_location) as cut_foundation:
            Box(config.bracket_depth,
                config.bracket_depth,
                config.bracket_depth,
                align=(Align.CENTER,Align.CENTER, Align.MIN)
            )
            fillet(cut_foundation.faces().filter_by(Axis.X).edges().filter_by(Axis.Y),
                   config.fillet_radius)
        with BuildPart(right_connector_location) as right_cut_foundation:
            Box(config.bracket_depth,
                config.bracket_depth,
                config.bracket_depth,
                align=(Align.CENTER,Align.CENTER, Align.MIN)
            )
            fillet(right_cut_foundation.faces().sort_by_distance((0,0,
                        config.bracket_depth/2))[-1].edges() \
                        .group_by(Axis.X, reverse=True)[-2], config.fillet_radius)

        with BuildPart(mode=Mode.SUBTRACT):
            add(support_cut())
            with Locations(Location((0,0,0)), Location((0,0,config.bracket_depth))):
                add(sweep_cut())
        with BuildPart():
            with config.sweep_cut_break_channel_locations:
                Cylinder(radius=(config.sweep_cut_width/2)*.9,
                        height=config.sweep_cut_width*2)

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Location((config.frame_click_sphere_point.x,
                        config.frame_click_sphere_point.y,
                        0)), Location((config.frame_click_sphere_point.x,
                        config.frame_click_sphere_point.y,
                        config.bracket_depth))):
                Sphere(radius=config.sweep_cut_width/2)

        with BuildPart(right_connector_location, mode=Mode.SUBTRACT):
            add(tube_cut(config.tube_length))
        with BuildPart(left_connector_location, mode=Mode.SUBTRACT):
            add(tube_cut(config.bracket_height))
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(radius=config.wheel_radius + \
                     config.wheel_radial_tolerance,
                     height=config.bracket_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            add(top_cut_template().mirror().move(
                Location((0,0,config.bracket_depth))))
    part = constructed_bracket.part
    part.label = "bracket"
    return part

def bottom_bracket_frame() -> Part:
    """
    returns the outer frame for the bottom bracket
    """
    with BuildPart() as constructed_bracket:
        Box(config.bracket_width, config.bracket_height,
            config.bracket_depth,
            align=(Align.CENTER, Align.MIN, Align.MIN))
        # with BuildPart(Location((config.bracket_width/2,config.bracket_height,0))):
        #     Box(config.bracket_depth,config.bracket_depth,config.bracket_depth,
        #         align=(Align.MIN, Align.MAX, Align.MIN),rotation=(0,0,-45))
        fillet(constructed_bracket.edges() - \
               constructed_bracket.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z) +
               constructed_bracket.faces().sort_by(Axis.X)[0].edges(),
               config.fillet_radius)
        with BuildPart(Location((config.wheel_radius,0,0))):
            add(curved_filament_path_solid(top_exit_fillet=False))
        with BuildPart(Location((config.wheel_radius,0,0)), mode=Mode.SUBTRACT):
            add(curved_filament_path_cut())
        with BuildPart(Location((-config.wheel_radius,0,0))):
            add(straight_filament_path_solid())
        with BuildPart(Location((-config.wheel_radius,0,0)), mode=Mode.SUBTRACT):
            add(straight_filament_path_cut())
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(radius=config.wheel_radius + \
                     config.wheel_radial_tolerance,
                     height=config.bracket_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            add(top_cut_template().mirror().move(
                Location((0,0,config.bracket_depth))))
    part = constructed_bracket.part
    part.label = "bracket"
    return part

def top_frame(tolerance:float=0) -> Part:
    """
    returns the outer frame for the top bracket
    """
    with BuildPart() as frame:
        add(top_cut_template(tolerance))
        with BuildPart(mode=Mode.INTERSECT):
            add(bottom_bracket_frame().mirror(Plane.YZ))
    part = frame.part
    part.label = "frame"
    return part

def bottom_bracket(draft:bool = False) -> Part:
    """
    returns a complete bottom bracket
    """
    child_list = [spoke_assembly(),
                          bottom_bracket_frame(),
                          wheel_guide(),
                          ]
    #todo: get threads back
    # if not draft:
    #     child_list.extend([right_connector_threads(),
    #                        left_connector_threads()])

    return Part(label="bottom bracket",
                children=child_list)

def top_bracket() -> Part:
    """
    returns a complete top bracket
    """
    return Part(label="top bracket",
                children=[wheel_guide(),
                          top_frame(tolerance=0.1),
                          spoke_assembly().mirror(Plane.XZ)])

if __name__ == '__main__':
    bottom = bottom_bracket(draft=False)
    top = top_bracket()
    show(bottom.move(Location((config.bracket_width/2+5,0,0))),
         top.move(Location((-config.bracket_width/2+5,0,0))))
    export_stl(bottom, '../stl/bottom_bracket.stl')
    export_stl(top, '../stl/top_bracket.stl')
