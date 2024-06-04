"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt, radians, cos, sin, hypot, atan2, degrees, tan
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Axis, Box, Align, Cylinder,
                export_stl, offset, Polyline)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig

bracket_configuration = BankConfig()

def find_angle_intersection(known_distance, angle):
    """
    given an angle and the length along the adjascent axis, 
    calculates the distance along the opposite axis
    """
    return known_distance * tan(radians(angle))

def find_related_point(origin:tuple, distance:float, angle:float):
    """
    from a given origin, find the point along a given angle and distance
    """
    x,y = origin
    return ((x + (distance * cos(radians(angle)))),
            (y + (distance * sin(radians(angle)))))

def point_distance(p1, p2):
    """
    returns the distance between two points
    """
    x1,y1 = p1
    x2,y2 = p2
    return hypot(x2-x1, y2-y1)

def x_point_to_angle(radius, x_position):
    """
    for a circle with a given radius, given an x axis position,
    returns the angle at which an intersection will occur with the
    circle's edge
    """
    y_position = distance_to_circle_edge(radius, (x_position, 0), 90)
    return degrees(atan2(y_position, x_position))

def y_point_to_angle(radius, y_position):
    """
    for a circle with a given radius, given a y axis position,
    returns the angle at which an intersection will occur with the
    circle's edge
    """
    x_position = distance_to_circle_edge(radius, (0, y_position), 90)
    return degrees(atan2(y_position, x_position))

def distance_to_circle_edge(radius, point, angle):
    """
    for a circle with the given radius, find the distance from the
    given point to the edge of the circle in the direction determined
    by the given angle
    """
    x1, y1 = point
    theta = radians(angle)  # Convert angle to radians if it's given in degrees

    # Coefficients of the quadratic equation
    a = 1
    b = 2 * (x1 * cos(theta) + y1 * sin(theta))
    c = x1**2 + y1**2 - radius**2

    # Calculate the discriminant
    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return None  # No real intersection, should not happen as point is within the circle

    # Solve the quadratic equation for t
    t1 = (-b + sqrt(discriminant)) / (2 * a)
    t2 = (-b - sqrt(discriminant)) / (2 * a)

    # We need the positive t, as we are extending outwards
    t = max(t1, t2)

    return t

connector_distance = bracket_configuration.connector_radius+bracket_configuration.minimum_thickness
inner_edge_distance = bracket_configuration.wheel_radius-connector_distance
outer_edge_distance = bracket_configuration.wheel_radius+connector_distance
inner_angled_distance = inner_edge_distance*sqrt(2)/2
outer_angled_distance = outer_edge_distance*sqrt(2)/2

tube_length = distance_to_circle_edge(bracket_configuration.bracket_width/2,
                (inner_angled_distance,-inner_angled_distance), 45)
inner_bottom_corner =  (inner_angled_distance, -inner_angled_distance)
outer_bottom_corner =  (outer_angled_distance, -outer_angled_distance)
inner_top_corner= find_related_point(inner_bottom_corner, tube_length, 45)
outer_top_corner = find_related_point(outer_bottom_corner, tube_length, 45)
bracket_width = abs(inner_bottom_corner[1]) - abs(inner_top_corner[1])


angled_distance = bracket_configuration.wheel_radius*sqrt(2)/2
bottom_outlet_origin = (angled_distance, -angled_distance)
top_outlet_origin = find_related_point((angled_distance, -angled_distance), tube_length, 45)

right_connnector_location = Location((top_outlet_origin[0], top_outlet_origin[1],
                                    bracket_configuration.bracket_depth/2),
                                    (90,-45,0))
left_connector_location = Location((-bracket_configuration.wheel_radius, 
                                    bracket_configuration.bracket_height,
                                    bracket_configuration.bracket_depth/2), (90,0,0))

def curvebar(length, bar_width, depth, climb, angle):
    """
    returns a zig-zag ish line
    """
    with BuildPart() as curvebar:
        with BuildSketch() as sketch:
            x_distance = find_angle_intersection(climb/2, angle)
            angled_bar_width = find_angle_intersection(bar_width/2, angle)/2
            with BuildLine() as ln:
                Polyline(
                    (-length/2,-climb/2+bar_width/2),
                    (-length/2,-climb/2-bar_width/2),
                    (-x_distance-angled_bar_width+bar_width/2,-climb/2-bar_width/2),
                    (x_distance-angled_bar_width+bar_width/2,climb/2-bar_width/2),
                    (length/2,climb/2-bar_width/2),
                    (length/2,climb/2+bar_width/2),
                    (x_distance+angled_bar_width-bar_width/2,climb/2+bar_width/2),
                    (-x_distance+angled_bar_width-bar_width/2, -climb/2+bar_width/2),
                    (-length/2,-climb/2+bar_width/2),
                )
            make_face()
            fillet(sketch.vertices().filter_by_position(axis=Axis.X,
                    minimum=-length/2,
                    maximum=length/2,
                    inclusive=(False, False)), bar_width/2)
        extrude(amount=depth)
    bar = curvebar.part
    bar.label = "curvebar"
    return bar

def cut_spokes() -> Part:
    """
    returns the wheel spokes cut down to the correct size
    """
    with BuildPart() as spokes:
        add(curvebar(bracket_configuration.wheel_diameter,
              bracket_configuration.bracket_height/3,
              bracket_configuration.wheel_support_height,
              bracket_configuration.wheel_radius*.8, 45))
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
        with BuildSketch() as base:
            Circle(base_radius*.8)
            offset(amount=bracket_configuration.wheel_support_height)
        with BuildSketch(Plane.XY.offset(bracket_configuration.wheel_support_height)) as lofted:
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
    with BuildPart(right_connnector_location) as right_threads:
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
            loft()
    part = tube.part
    part.label = "tube cut"
    return part

def top_cut_template(tolerance:float=0) -> Part:
    """
    returns the shape defining the top cut of the bracket
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

def bottom_frame() -> Part:
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
                            (bracket_configuration.bracket_width/2,outer_top_corner[1]),
                            inner_bottom_corner,
                            (0,0)
                            )
                make_face()
            extrude(block.face(), bracket_configuration.bracket_depth)
            with BuildPart(right_connnector_location, mode=Mode.ADD):
                Box(bracket_configuration.bracket_depth, bracket_configuration.bracket_depth,
                    tube_length, align=(Align.CENTER, Align.CENTER, Align.MIN))
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
        with BuildPart(right_connnector_location) as right_cut_foundation:
            Box(bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                bracket_configuration.bracket_depth,
                align=(Align.CENTER,Align.CENTER, Align.MIN)
            )
            fillet(right_cut_foundation.faces().sort_by_distance((0,0,
                        bracket_configuration.bracket_depth/2))[-1].edges() \
                        .group_by(Axis.X, reverse=True)[-2], bracket_configuration.fillet_radius)

        with BuildPart(mode=Mode.SUBTRACT):
            with BuildSketch():
                with BuildLine():
                    arc=CenterArc((-bracket_configuration.bracket_width/2,
                                   bracket_configuration.bracket_height*.5),
                                   radius=bracket_configuration.clip_length,
                                   start_angle=270, arc_size=90)
                    Line(arc @ 1, (-bracket_configuration.bracket_width/2,
                                   bracket_configuration.bracket_height*.5))
                    Line(arc @ 0, (-bracket_configuration.bracket_width/2,
                                   bracket_configuration.bracket_height*.5))
                make_face()
            extrude(amount=bracket_configuration.bracket_depth)
        with BuildPart(right_connnector_location, mode=Mode.SUBTRACT):
            add(tube_cut(tube_length))
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
    with BuildPart() as top_bracket:
        add(top_cut_template(tolerance))
        with BuildPart(mode=Mode.INTERSECT):
            add(bottom_frame().mirror(Plane.YZ))
    part = top_bracket.part
    part.label = "frame"
    return part

def bottom_bracket(draft:bool = False) -> Part:
    """
    returns a complete bottom bracket
    """
    child_list = [spoke_assembly(),
                          bottom_frame(),
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
    bottom = bottom_bracket(draft=draft)
    top = top_bracket()
    show(bottom.move(Location((bracket_configuration.bracket_width/2+5,0,0))),
         top.move(Location((-bracket_configuration.bracket_width/2+5,0,0))))
    export_stl(bottom, '../stl/bottom_bracket.stl')
    export_stl(top, '../stl/top_bracket.stl')

main()