"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt
from shapely import Point
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Locations, Plane, loft, fillet, Axis, Box, Align, Cylinder,
                export_stl, offset, Polyline, Rectangle, Sphere, sweep,
                GridLocations)
from bd_warehouse.thread import TrapezoidalThread
from bank_config import BankConfig
from geometry_utils import (find_related_point_by_distance, x_point_to_angle, point_distance, y_point_to_angle)
from curvebar import curvebar

bracket_configuration = BankConfig()

#connector_distance = bracket_configuration.bracket_depth/2 #bracket_configuration.connector_radius+bracket_configuration.minimum_thickness
inner_edge_distance = bracket_configuration.wheel_radius - \
    bracket_configuration.connection_foundation_mid
outer_edge_distance = bracket_configuration.wheel_radius + \
    bracket_configuration.connection_foundation_mid
inner_angled_distance = inner_edge_distance*sqrt(2)/2
outer_angled_distance = outer_edge_distance*sqrt(2)/2

inner_bottom_corner =  Point(inner_angled_distance, -inner_angled_distance)
outer_bottom_corner =  Point(outer_angled_distance, -outer_angled_distance)
inner_top_corner= find_related_point_by_distance(inner_bottom_corner,
                                bracket_configuration.tube_length, 45)
outer_top_corner = find_related_point_by_distance(outer_bottom_corner,
                                bracket_configuration.tube_length, 45)
bracket_width = abs(inner_bottom_corner.y) - abs(inner_top_corner.y)

right_connector_location = Location((bracket_configuration.exit_tube_exit_point.x,
                                    bracket_configuration.exit_tube_exit_point.y,
                                    bracket_configuration.bracket_depth/2),
                                    (90,-45,0))
left_connector_location = Location((-bracket_configuration.wheel_radius,
                                    bracket_configuration.bracket_height,
                                    bracket_configuration.bracket_depth/2), (90,0,0))

def cut_spokes() -> Part:
    """
    returns the wheel spokes cut down to the correct size
    """
    with BuildPart() as spokes:
        add(curvebar(bracket_configuration.spoke_length,
              bracket_configuration.spoke_bar_height,
              bracket_configuration.wheel_support_height,
              bracket_configuration.spoke_climb, bracket_configuration.spoke_angle))
        fillet(spokes.edges(), bracket_configuration.wheel_support_height/4)
        with BuildPart(mode=Mode.INTERSECT):
            add(wheel_guide_cut())
    return spokes.part

def spoke_assembly() -> Part:
    """
    adds the axle for the filament wall bearing, along with the spokes
    """
    with BuildPart() as constructed_brace:
        add(cut_spokes())
        Cylinder(radius=bracket_configuration.bearing_shelf_radius,
                        height=bracket_configuration.bearing_shelf_height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(radius=bracket_configuration.bearing_inner_radius,
                        height=bracket_configuration.bracket_depth/2 - \
                            bracket_configuration.wheel_lateral_tolerance,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = constructed_brace.part
    part.label = "spoke assembly"
    return part

def wheel_guide_cut() -> Part:
    """
    the cutout shape for a wheel guide
    """
    with BuildPart() as wheelcut:
        base_radius=bracket_configuration.wheel_radius + \
                bracket_configuration.wheel_radial_tolerance
        with BuildSketch():
            Circle(base_radius*.8)
            offset(amount=bracket_configuration.wheel_support_height)
        with BuildSketch(Plane.XY.offset(bracket_configuration.wheel_support_height)):
            Circle(base_radius*.8)
        loft()
    return wheelcut.part

def wheel_guide() -> Part:
    """
    The part responsible for guiding the filament wheel and keeping it straight
    """
    base_radius=bracket_configuration.wheel_radius + \
                    bracket_configuration.wheel_radial_tolerance

    with BuildPart() as wheel_brace:
        with BuildPart():
            with BuildSketch():
                Circle(base_radius)
                offset(amount=bracket_configuration.wheel_support_height)
            with BuildSketch(Plane.XY.offset(bracket_configuration.wheel_support_height)):
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
                diameter=bracket_configuration.connector_diameter,
                pitch=bracket_configuration.connector_thread_pitch,
                length=bracket_configuration.connector_length,
                thread_angle = bracket_configuration.connector_thread_angle,
                external=False,
                interference=bracket_configuration.connector_thread_interference,
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
                diameter=bracket_configuration.connector_radius*2,
                pitch=bracket_configuration.connector_thread_pitch,
                length=bracket_configuration.connector_length,
                thread_angle = bracket_configuration.connector_thread_angle,
                interference=bracket_configuration.connector_thread_interference,
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
        Cylinder(radius=bracket_configuration.connector_radius,
                 height=bracket_configuration.connector_length*2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER))
        Cylinder(radius=bracket_configuration.tube_outer_radius,
                 height=length-bracket_configuration.tube_outer_diameter*3,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

        with BuildPart():
            with BuildSketch(Plane.XY.offset(length-bracket_configuration.tube_outer_diameter*3)):
                Circle(radius=bracket_configuration.tube_inner_radius)
            with BuildSketch(Plane.XY.offset(length)):
                Circle(radius=bracket_configuration.tube_outer_diameter*.75)
                Rectangle(width=bracket_configuration.tube_outer_diameter*2,
                          height=bracket_configuration.bearing_depth + \
                            bracket_configuration.wheel_lateral_tolerance,
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
    # arc_radius = point_distance(bracket_configuration.frame_click_sphere_point,
    #             bracket_configuration.frame_clip_point)
    # x_distance = bracket_configuration.frame_clip_point.x + \
    #     abs(bracket_configuration.frame_click_sphere_point.x)
    # top_angle = 180-x_point_to_angle(radius=arc_radius, x_position=x_distance)
    # bottom_angle = 180-y_point_to_angle(radius=arc_radius,
    # y_position=abs(bracket_configuration.frame_clip_point.y))

    with BuildPart(mode=Mode.PRIVATE) as cut:
        with BuildLine():
            ln=bracket_configuration.sweep_cut_arc
        with BuildSketch(Plane(origin=ln @ 0, z_dir=ln % 0)):
            Circle(bracket_configuration.sweep_cut_width/2)
        sweep()

    return cut.part

def top_cut_template(tolerance:float=0) -> Part:
    """
    returns the shape defining the top cut of the bracket
    (the part that slides into place to hold the filament wheel in place)
    provide a tolerance for the actual part to make it easier to assemble
    """
    base_outer_radius = bracket_configuration.wheel_radius + \
                    bracket_configuration.wheel_radial_tolerance + \
                    bracket_configuration.wheel_support_height
    base_rectangle_width = bracket_configuration.bracket_width - \
        (bracket_configuration.fillet_radius + \
         bracket_configuration.connector_diameter + \
            bracket_configuration.wheel_support_height*4)*2
    with BuildPart() as template:
        with BuildSketch():
            with BuildLine():
                start_angle = x_point_to_angle(base_outer_radius-tolerance,
                                               base_rectangle_width/2-tolerance)
                inner_rcurve = CenterArc((0,0), base_outer_radius-tolerance, 0, start_angle)
                inner_lcurve = CenterArc((0,0), base_outer_radius-tolerance, 180-start_angle,
                                         start_angle)
                inner_left_up = Line(inner_rcurve @ 1, (base_rectangle_width/2-tolerance,
                                                        bracket_configuration.bracket_height))
                inner_topline = Line(inner_left_up @ 1, (-base_rectangle_width/2+tolerance,
                                                         bracket_configuration.bracket_height))
                Line(inner_topline @ 1, inner_lcurve @0)
                inner_downl = Line(inner_lcurve @1, (-base_outer_radius+tolerance,
                                                     -bracket_configuration.bracket_height))
                inner_downr = Line(inner_rcurve @0, (base_outer_radius-tolerance,
                                                     -bracket_configuration.bracket_height))
                Line(inner_downl @1, inner_downr @ 1)
            make_face()
        with BuildSketch(Plane.XY.offset(bracket_configuration.wheel_support_height)):
            with BuildLine():
                start_angle = x_point_to_angle(base_outer_radius + \
                                    bracket_configuration.wheel_support_height-tolerance,
                                    base_rectangle_width/2 + \
                                    bracket_configuration.wheel_support_height - \
                                    tolerance)
                outer_rcurve = CenterArc((0,0),
                                base_outer_radius+bracket_configuration.wheel_support_height - \
                                tolerance, 0, start_angle)
                outer_lcurve = CenterArc((0,0),
                                base_outer_radius+bracket_configuration.wheel_support_height - \
                                tolerance, 180-start_angle, start_angle)
                outer_left_up = Line(outer_rcurve @ 1,
                                    (base_rectangle_width/2-tolerance + \
                                    bracket_configuration.wheel_support_height,
                                    bracket_configuration.bracket_height))
                outer_topline = Line(outer_left_up @ 1,
                                    (-base_rectangle_width/2-tolerance - \
                                    bracket_configuration.wheel_support_height,
                                    bracket_configuration.bracket_height))
                Line(outer_topline @ 1, outer_lcurve @0)
                outer_downl = Line(outer_lcurve @1,
                                   (-base_outer_radius - \
                                    bracket_configuration.wheel_support_height + \
                                    tolerance,
                                    -bracket_configuration.bracket_height))
                outer_downr = Line(outer_rcurve @0,
                                    (base_outer_radius + \
                                    bracket_configuration.wheel_support_height - \
                                    tolerance,
                                    -bracket_configuration.bracket_height))
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
                arc=CenterArc((float(bracket_configuration.frame_clip_point.x), float(bracket_configuration.frame_clip_point.y)),
                                radius=bracket_configuration.clip_length,
                                start_angle=45, arc_size=90)
                Line(arc @ 1, (float(bracket_configuration.frame_clip_point.x), float(bracket_configuration.frame_clip_point.y)))
                Line(arc @ 0, (float(bracket_configuration.frame_clip_point.x), float(bracket_configuration.frame_clip_point.y)))
            make_face()
        extrude(amount=bracket_configuration.bracket_depth)
    part =clip_cut
    clip_cut.label = "clip cut"
    return part


def bottom_bracket_frame() -> Part:
    """
    returns the outer frame for the bottom bracket
    """
    with BuildPart() as constructed_bracket:
        with BuildPart() as left_bracket:
            with BuildSketch() as block:
                with BuildLine():
                    Polyline((0,0),
                            (-bracket_configuration.bracket_width/2, 0),
                            (-bracket_configuration.bracket_width/2,
                             bracket_configuration.bracket_height),
                            (bracket_configuration.bracket_width/2,
                             bracket_configuration.bracket_height),
                            (bracket_configuration.bracket_width/2,outer_top_corner.y),
                            (inner_bottom_corner.x,inner_bottom_corner.y),
                            (0,0)
                            )
                make_face()
            extrude(block.face(), bracket_configuration.bracket_depth)
            with BuildPart(right_connector_location, mode=Mode.ADD):
                Box(bracket_configuration.bracket_depth, bracket_configuration.bracket_depth,
                    bracket_configuration.tube_length, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(left_bracket.faces().sort_by(Axis.Y)[-1].edges() + \
               left_bracket.faces().sort_by(Axis.X, reverse=True)[0:-1].edges(),
               bracket_configuration.fillet_radius)
        with BuildPart(left_connector_location) as cut_foundation:
            Box(bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                align=(Align.CENTER,Align.CENTER, Align.MIN)
            )
            fillet(cut_foundation.faces().filter_by(Axis.X).edges().filter_by(Axis.Y),
                   bracket_configuration.fillet_radius)
        with BuildPart(right_connector_location) as right_cut_foundation:
            Box(bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                align=(Align.CENTER,Align.CENTER, Align.MIN)
            )
            fillet(right_cut_foundation.faces().sort_by_distance((0,0,
                        bracket_configuration.bracket_depth/2))[-1].edges() \
                        .group_by(Axis.X, reverse=True)[-2], bracket_configuration.fillet_radius)

        with BuildPart(mode=Mode.SUBTRACT):
            add(support_cut())
            with Locations(Location((0,0,0)), Location((0,0,bracket_configuration.bracket_depth))):
                add(sweep_cut())
        with BuildPart():
            with bracket_configuration.sweep_cut_break_channel_locations:
                Cylinder(radius=(bracket_configuration.sweep_cut_width/2)*.9,
                        height=bracket_configuration.sweep_cut_width*2)

        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Location((bracket_configuration.frame_click_sphere_point.x,
                        bracket_configuration.frame_click_sphere_point.y,
                        0)), Location((bracket_configuration.frame_click_sphere_point.x,
                        bracket_configuration.frame_click_sphere_point.y,
                        bracket_configuration.bracket_depth))):
                Sphere(radius=bracket_configuration.sweep_cut_width/2)

        with BuildPart(right_connector_location, mode=Mode.SUBTRACT):
            add(tube_cut(bracket_configuration.tube_length))
        with BuildPart(left_connector_location, mode=Mode.SUBTRACT):
            add(tube_cut(bracket_configuration.bracket_height))
        with BuildPart(mode=Mode.SUBTRACT):
            Cylinder(radius=bracket_configuration.wheel_radius + \
                     bracket_configuration.wheel_radial_tolerance,
                     height=bracket_configuration.bracket_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            add(top_cut_template().mirror().move(
                Location((0,0,bracket_configuration.bracket_depth))))
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
    if not draft:
        child_list.extend([right_connector_threads(),
                           left_connector_threads()])

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

def main(draft:bool = False):
    """
    shows and saves the parts
    """
    from ocp_vscode import show
    bottom = bottom_bracket(draft=draft)
    top = top_bracket()
    show(bottom.move(Location((bracket_configuration.bracket_width/2+5,0,0))),
         top.move(Location((-bracket_configuration.bracket_width/2+5,0,0))))
    export_stl(bottom, '../stl/bottom_bracket.stl')
    export_stl(top, '../stl/top_bracket.stl')

#main(draft=False)
