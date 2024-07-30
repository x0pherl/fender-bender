"""
Generates filament ingress and egress shapes
"""
from math import sqrt
from shapely import Point
from build123d import (BuildPart, BuildSketch, Part, Circle,
                Mode, BuildLine, Line, add, Location, GeomType,
                Locations, Plane, loft, fillet, Axis, Box, Align, Cylinder,
                Rectangle, sweep,chamfer,TangentArc, Spline,
                Torus, CenterArc,Compound, extrude)
from ocp_vscode import show, Camera
from bd_warehouse.thread import TrapezoidalThread
from bank_config import BankConfig
from geometry_utils import (find_related_point_by_distance, find_related_point_by_y)
from curvebar import curvebar

config = BankConfig()

ingress_connector_location = Location((-config.wheel_radius,
                                    config.bracket_height,
                                    config.bracket_depth/2), (90,0,0))

def connector_threads() -> Part:
    """
    returns the threads for the connector
    """
    with BuildPart() as threads:
        TrapezoidalThread(
                diameter=config.connector_diameter,
                pitch=config.connector_thread_pitch,
                length=config.connector_length-config.minimum_thickness/2,
                thread_angle = config.connector_thread_angle,
                external=False,
                interference=config.connector_thread_interference,
                hand="right",
                align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
    part = threads.part
    part.label = "connector threads"
    return part

def straight_filament_path_cut():
    """
    creates a cutout for a filament tube allowing for the connector, and
    a tube stop with a funnel entry
    """
    with BuildPart(mode=Mode.PRIVATE) as tube:
        with BuildPart():
            with BuildSketch(Plane.XY.offset(0)):
                Circle(radius=config.tube_outer_diameter*.75)
                Rectangle(width=config.tube_outer_diameter*2,
                          height=config.bearing_depth + \
                            config.wheel_lateral_tolerance,
                            mode=Mode.INTERSECT)
            with BuildSketch(Plane.XY.offset(config.filament_funnel_height)):
                Circle(radius=config.tube_inner_radius)
            loft()
        with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
            Cylinder(radius=config.tube_outer_radius,
                height=config.bracket_height-config.filament_funnel_height-config.connector_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
            Cylinder(radius=config.connector_radius,
                 height=config.connector_length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(config.bracket_height-config.minimum_thickness/2)):
            Circle(radius=config.connector_radius)
        with BuildSketch(Plane.XY.offset(config.bracket_height)):
            Circle(radius=config.connector_radius+config.minimum_thickness/2)
        loft()

        # Cylinder(radius=config.tube_outer_radius,
        #          height=config.bracket_height-config.bracket_depth,
        #             align=(Align.CENTER, Align.CENTER, Align.MIN))

    with BuildPart(Location((0,0,config.bracket_depth/2),(-90,0,0))) as cut:
        add(tube)
    part = cut.part
    part.label = "tube cut"
    return part

def straight_filament_path_solid() -> Part:
    """
    builds the solid reinforcement for the filaement ingress channel
    """
    with BuildPart(Location((0,0,0),(-90,0,0))) as ingress:
        Box(config.bracket_depth, config.bracket_depth,
                    config.bracket_height, align=(Align.CENTER, Align.MAX, Align.MIN))
        fillet(ingress.edges().filter_by(Axis.Y) + ingress.faces().sort_by(Axis.Y)[0].edges().filter_by(Axis.X),
               config.fillet_radius)
    return ingress.part

def straight_filament_connector_threads() -> Part:
    """
    the threads for the ingress connector
    """
    with BuildPart(Location((0,config.bracket_height-config.minimum_thickness/2,config.bracket_depth/2),(90,0,0))) as threads:
        add(connector_threads())
    part = threads.part
    part.label = "connector threads"
    return part

def straight_filament_path(draft=True) -> Part:
    """
    builds a straight filaement channel with the cut in place
    """
    with BuildPart() as path:
        add(straight_filament_path_solid())
        with BuildPart(mode=Mode.SUBTRACT):
            add(straight_filament_path_cut())
        if not draft:
            add(straight_filament_connector_threads())
    part = path.part
    part.label = "filament path"
    return part

def curved_filament_line() -> Compound:
    """
    returns a compund with three line segments representing the
    channel for the ingress funnel, the PTFE tube,
    and the connector
    """
    straight_distance = (config.bracket_depth/2)/sqrt(2)
    egress_point=(config.bracket_width-config.wheel_radius-straight_distance,config.bracket_height*2-straight_distance)
    connector_egress_point=(egress_point[0]-straight_distance, egress_point[1]-straight_distance)

    with BuildLine( mode=Mode.PRIVATE) as egress_line:
        funnel = Line((0,0), (0,config.filament_funnel_height))
        bridge = Line(funnel@1,(0,config.filament_funnel_height+config.minimum_structural_thickness))
        curve = CenterArc(center=(config.wheel_radius, (bridge@1).Y),
                             radius=config.wheel_radius, start_angle=180, arc_size=-45)
        output = Line(curve@1,((curve@1).X+straight_distance,
                               (curve@1).Y+straight_distance))
        bridge.label = "input"
        bridge.color = "RED"
        curve.label = "curve"
        curve.color= "BLUE"
        output.label = "output"
        output.color = "GREEN"
    lines = Compound(children=(funnel,bridge, curve, output))
    return lines

with BuildSketch() as outline:
    Rectangle(config.bracket_width, config.bracket_height,
              align=(Align.CENTER,Align.MIN))
    Circle(radius=config.wheel_radius+config.minimum_structural_thickness)

def curved_filament_path_cut() -> Compound:
    """
    returns the shape to be cut out of a curved filament path
    allowing for the PTFE tube and the connector
    """
    path = curved_filament_line()
    with BuildPart() as inlet:
        with BuildLine() as intake:
            add(path.children[0])
        with BuildSketch(Plane(origin=intake.line@0,z_dir=intake.line%0)):
            Circle(radius=config.tube_outer_diameter*.75)
            Rectangle(height=config.tube_outer_diameter*2,
                        width=config.bearing_depth + \
                        config.wheel_lateral_tolerance,
                        mode=Mode.INTERSECT)
        with BuildSketch(Plane(origin=intake.line@1,z_dir=intake.line%1)):
            Circle(config.tube_inner_radius)
        loft()
        extrude(inlet.faces().sort_by(Axis.Y)[0], config.bracket_depth)
    with BuildPart() as tube:
        with BuildLine() as tube_path:
            add(path.children[1])
        with BuildSketch(Plane(origin=tube_path.line@0,z_dir=tube_path.line%0)):
            Circle(config.tube_outer_radius)
        sweep()
    with BuildPart() as tube_curve:
        with BuildLine() as tube_path:
            add(path.children[2])
        with BuildSketch(Plane(origin=tube_path.line@0,z_dir=tube_path.line%0)):
            Circle(config.tube_outer_radius)
        sweep()
    with BuildPart() as connector:
        with BuildLine() as connector_path:
            add(path.children[3])
        with BuildSketch(Plane(origin=connector_path.line@0,z_dir=connector_path.line%0)):
            Circle(config.connector_radius)
        sweep()
    with BuildPart() as connector_chamfer:
        with BuildSketch(Plane(origin=connector_path.line@1,z_dir=connector_path.line%1)):
            Circle(config.connector_radius+config.minimum_thickness/2)
        with BuildSketch(Plane(origin=connector_path.line@1,z_dir=connector_path.line%1).offset(-config.minimum_thickness/2)):
            Circle(config.connector_radius)
        loft()
        extrude(connector_chamfer.faces().sort_by(Axis.X)[-1], config.bracket_depth)
    complete = Compound(label="curved filament path cut", children=(inlet.part,tube.part,tube_curve.part,connector.part,connector_chamfer.part)).move(Location((0,0,config.bracket_depth/2)))
    return complete

def curved_filament_path_solid(top_exit_fillet=True) -> Part:
    """"
    The solid shape for the channel around a curved filament path
    optionally
    -------
    arguments:
    top_exit_fillet: set to false to render a clean intersection with
    box immediately to the left of the exit
    """
    with BuildPart() as solid_path:
        with BuildLine() as curve:
            add(curved_filament_line())
        with BuildSketch(Plane(origin=curve.line@0,z_dir=curve.line%0)) as path_face:
            Rectangle(config.bracket_depth, config.bracket_depth)
            fillet(path_face.vertices(), config.fillet_radius)
        sweep()
        if not top_exit_fillet:
            with BuildLine() as curve2:
                add(curved_filament_line().children[1])
                add(curved_filament_line().children[2])
            with BuildSketch(Plane(origin=curve2.line@0,z_dir=curve2.line%0)) as path_face:
                Rectangle(config.bracket_depth, config.bracket_depth/2,
                        align=(Align.CENTER, Align.MAX))
            sweep()
        fillet(solid_path.faces().sort_by(Axis.Y)[0].edges().filter_by(Axis.X),
                config.fillet_radius)
    part = solid_path.part.move(Location((0,0,config.bracket_depth/2)))
    part.label = "curved filament path"
    return part

def curved_filament_connector_threads() -> Part:
    """
    places the threads for the curved filament connector
    """
    with BuildLine() as path:
        add(curved_filament_line())
    offset = (config.minimum_thickness/4)/sqrt(2)
    with BuildPart(Location(((path.line@1).X-offset,
                             (path.line@1).Y-offset,config.bracket_depth/2),
                             (90,-45,0))) as threads:
        add(connector_threads())
    part = threads.part
    part.label = "connector threads"
    return part

def curved_filament_path(top_exit_fillet=False,draft=True) -> Part:
    """
    builds a straight filaement channel with the cut in place
    """
    with BuildPart() as path:
        add(curved_filament_path_solid(top_exit_fillet))
        with BuildPart(mode=Mode.SUBTRACT):
            add(curved_filament_path_cut())
        if not draft:
            add(curved_filament_connector_threads())
    part = path.part
    part.label = "filament path"
    return part

if __name__ == '__main__':
    show(curved_filament_path(top_exit_fillet=True, draft=False).move(Location((config.wheel_radius,0,0))),
         straight_filament_path(draft=False).move(Location((-config.wheel_radius,0,0))),
         reset_camera=Camera.CENTER)