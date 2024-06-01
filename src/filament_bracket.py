"""
Generates the part for the filament bracket of our filament bank design
"""
from math import sqrt, radians, cos, sin, hypot
from build123d import (BuildPart, BuildSketch, Part, Circle, CenterArc,
                extrude, Mode, BuildLine, Line, make_face, add, Location,
                Plane, loft, fillet, Axis, Box, Align, Cylinder,
                export_stl)
from bd_warehouse.thread import TrapezoidalThread
from ocp_vscode import show
from bank_config import BankConfig

def connector_guide(tube_radius: float, length: float, 
                    connector_radius: float, connector_length: float, 
                    box_width:float, thread_pitch: float=1, thread_angle: float=30) -> Part:
    # threads = TrapezoidalThread(
    #             diameter=connector_radius*2,
    #             pitch=thread_pitch,
    #             length=connector_length,
    #             thread_angle = thread_angle,
    #             external=False,
    #             hand="right",
    #             align=(Align.CENTER, Align.CENTER, Align.MAX)
    #             )
    with BuildPart() as guide:
        with BuildPart() as post:
            Box(length=box_width, width=box_width,
                height=length,
                align=(Align.CENTER, Align.CENTER, Align.MAX))
            fillet(post.faces().sort_by(Axis.X)[0].edges().filter_by(Axis.Z), box_width/4)
        with BuildPart(mode=Mode.SUBTRACT) as cut:
            Cylinder(radius=tube_radius, height=length, 
                        align=(Align.CENTER, Align.CENTER, Align.MAX))
            Cylinder(radius=connector_radius, height=connector_length,
                        align=(Align.CENTER, Align.CENTER, Align.MAX))
    # return Part(label="connector guide", children=[guide.part, threads])
    return guide.part

def wheel_cut(inner_radius:float, outer_radius: float, arc_size: float, depth: float) -> Part:
    """
    returns the shape of the cut from the wheel support
    """
    with BuildPart() as cut:
        with BuildSketch(Plane(origin=(0,0,0), z_dir=(0,0,1))) as base:
            with BuildLine():
                l1=CenterArc(center=((0,0)), radius=outer_radius,
                            start_angle=90-arc_size/2, arc_size=arc_size)
                l2=CenterArc(center=((0,0)),
                            radius=inner_radius,
                            start_angle=90-arc_size/2, arc_size=arc_size)
                Line(l1 @ 0, l2 @ 0)
                Line(l1 @ 1, l2 @ 1)
            make_face()
            fillet(base.vertices(), l1.length/16)
        with BuildSketch(Plane(origin=(0,0,depth), z_dir=(0,0,1))) as top:
            with BuildLine():
                l1=CenterArc(center=((0,-depth)), radius=outer_radius,
                            start_angle=90-arc_size/2, arc_size=arc_size)
                l2=CenterArc(center=((0,-depth)),
                            radius=inner_radius,
                            start_angle=90-arc_size/2, arc_size=arc_size)
                Line(l1 @ 0, l2 @ 0)
                Line(l1 @ 1, l2 @ 1)
            make_face()
            fillet(top.vertices(), l1.length/16)
        loft()
    return cut

bracket_configuration = BankConfig()

def find_related_point(origin:tuple, distance:float, angle:float):
    x,y = origin
    return ((x + (distance * cos(radians(angle)))),
            (y + (distance * sin(radians(angle)))))

def point_distance(p1, p2):
    x1,y1 = p1
    x2,y2 = p2
    return hypot(x2-x1, y2-y1)

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

tube_length = distance_to_circle_edge(bracket_configuration.wheel_radius,
                (inner_angled_distance,-inner_angled_distance), 45) \
                    + bracket_configuration.connector_length \
                    + bracket_configuration.minimum_thickness
inner_bottom_corner =  (inner_angled_distance, -inner_angled_distance)
outer_bottom_corner =  (outer_angled_distance, -outer_angled_distance)
inner_top_corner= find_related_point(inner_bottom_corner, tube_length, 45)
outer_top_corner = find_related_point(outer_bottom_corner, tube_length, 45)
bracket_width = abs(inner_bottom_corner[1]) - abs(inner_top_corner[1])

with BuildPart() as brace:
    with BuildSketch() as sketch:
        with BuildLine() as line:
            l1 = Line((abs(inner_bottom_corner[1])-bracket_width,inner_bottom_corner[1]),
                    inner_bottom_corner)
            l2 = Line(l1 @ 1, inner_top_corner)
            l3 = Line(l2 @ 1, (abs(inner_top_corner[1])+bracket_width/2,inner_top_corner[1]))

            l4 = Line((-abs(inner_top_corner[1])-bracket_width/2,abs(inner_top_corner[1])),
                    (-bracket_configuration.wheel_radius, abs(inner_top_corner[1])))
            l5 = Line(l4 @ 1,
                    (-bracket_configuration.wheel_radius+connector_distance, abs(inner_bottom_corner[1])))
            l6 = Line(l5 @ 1, (-abs(inner_bottom_corner[1])+bracket_width, abs(inner_bottom_corner[1])))

            Line(l4 @0, l1 @ 0)
            Line(l6@1, l3@1)

        make_face()
        fillet(sketch.vertices().filter_by_position(axis=Axis.X, minimum=-inner_bottom_corner[0], maximum=inner_bottom_corner[0], inclusive=(False, False)), bracket_width/2)
    extrude(sketch.face(), amount=bracket_configuration.minimum_structural_thickness)
    fillet(brace.edges(), bracket_configuration.minimum_structural_thickness/4)
    
    with BuildPart(mode=Mode.ADD):
        with BuildPart(Location((-bracket_configuration.wheel_radius,
                                 abs(inner_bottom_corner[1])+bracket_configuration.connector_length,
                                 bracket_configuration.bracket_depth/2), (-90,0,0))) as left_connector:
            add(connector_guide(bracket_configuration.tube_outer_radius, bracket_width+bracket_configuration.connector_length,
                                bracket_configuration.connector_radius, bracket_configuration.connector_length,
                                bracket_configuration.bracket_depth))
        top_center_x, top_center_y = find_related_point(outer_top_corner, connector_distance, 135)
        with BuildPart(Location((inner_top_corner[0], inner_top_corner[1],
                                 bracket_configuration.bracket_depth/2), (-90,45,180))) as right_connector:
            add(connector_guide(bracket_configuration.tube_outer_radius, tube_length,
                                bracket_configuration.connector_radius, bracket_configuration.connector_length,
                                bracket_configuration.bracket_depth).move(Location((0,0,bracket_configuration.bracket_height/4))))

    with BuildPart(Plane(origin=(0,0,bracket_configuration.minimum_structural_thickness),
                                z_dir=(0,0,1)), mode=Mode.SUBTRACT) as wheel_cut:
        Cylinder(radius=bracket_configuration.wheel_radius, 
                 height=bracket_configuration.bracket_depth,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))

with BuildPart() as wheel_brace:
    with BuildPart() as outer:
        with BuildSketch() as base:
            Circle(radius=bracket_configuration.wheel_radius).face() \
                .offset(bracket_configuration.minimum_structural_thickness)
            #Circle(radius=bracket_configuration.wheel_radius + \
            #       bracket_configuration.minimum_structural_thickness)
        with BuildSketch(Plane(origin=(0,0,bracket_configuration.minimum_structural_thickness),
                            z_dir=(0,0,1))) as lofted:
            Circle(radius=bracket_configuration.wheel_radius)
        loft()
    with BuildPart(mode=Mode.SUBTRACT) as wheel_cut:
        with BuildSketch():
            Circle(radius=bracket_configuration.wheel_radius * .8).face() \
                .offset(bracket_configuration.minimum_structural_thickness)
        with BuildSketch(Plane(origin=(0,0,bracket_configuration.minimum_structural_thickness),
                                z_dir=(0,0,1))):
            Circle(radius=bracket_configuration.wheel_radius*.8)
        loft()


combo = Part(label="wheel brace", children=[wheel_brace.part, brace.part])
show(combo)
export_stl(combo, '../stl/bottom_bracket.stl')
#show(wheel_brace, brace, base)
