"""
Generates filament ingress and egress shapes
"""

from math import sqrt

from bd_warehouse.thread import TrapezoidalThread
from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    Compound,
    Cylinder,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    add,
    extrude,
    fillet,
    loft,
    sweep,
)
from ocp_vscode import Camera, show

from bank_config import BankConfig

_config = BankConfig()

ingress_connector_location = Location(
    (-_config.wheel_radius, _config.bracket_height, _config.bracket_depth / 2),
    (90, 0, 0),
)


def connector_threads() -> Part:
    """
    returns the threads for the connector
    """
    with BuildPart() as threads:
        TrapezoidalThread(
            diameter=_config.connector_diameter,
            pitch=_config.connector_thread_pitch,
            length=_config.connector_length - _config.minimum_thickness / 2,
            thread_angle=_config.connector_thread_angle,
            external=False,
            interference=_config.connector_thread_interference,
            hand="right",
            align=(Align.CENTER, Align.CENTER, Align.MIN),
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
                Circle(radius=_config.tube_outer_diameter * 0.75)
                Rectangle(
                    width=_config.tube_outer_diameter * 2,
                    height=_config.bearing_depth
                    + _config.wheel_lateral_tolerance,
                    mode=Mode.INTERSECT,
                )
            with BuildSketch(Plane.XY.offset(_config.filament_funnel_height)):
                Circle(radius=_config.tube_inner_radius)
            loft()
        with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
            Cylinder(
                radius=_config.tube_outer_radius,
                height=_config.bracket_height
                - _config.filament_funnel_height
                - _config.connector_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(tube.faces().sort_by(Axis.Z)[-1]):
            Cylinder(
                radius=_config.connector_radius,
                height=_config.connector_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildSketch(
            Plane.XY.offset(
                _config.bracket_height - _config.minimum_thickness / 2
            )
        ):
            Circle(radius=_config.connector_radius)
        with BuildSketch(Plane.XY.offset(_config.bracket_height)):
            Circle(
                radius=_config.connector_radius + _config.minimum_thickness / 2
            )
        loft()

        # Cylinder(radius=_config.tube_outer_radius,
        #          height=_config.bracket_height-_config.bracket_depth,
        #             align=(Align.CENTER, Align.CENTER, Align.MIN))

    with BuildPart(
        Location((0, 0, _config.bracket_depth / 2), (-90, 0, 0))
    ) as cut:
        add(tube)
    part = cut.part
    part.label = "tube cut"
    return part


def straight_filament_path_solid() -> Part:
    """
    builds the solid reinforcement for the filaement ingress channel
    """
    with BuildPart(Location((0, 0, 0), (-90, 0, 0))) as ingress:
        Box(
            _config.bracket_depth,
            _config.bracket_depth,
            _config.bracket_height,
            align=(Align.CENTER, Align.MAX, Align.MIN),
        )
        fillet(
            ingress.edges().filter_by(Axis.Y)
            + ingress.faces().sort_by(Axis.Y)[0].edges().filter_by(Axis.X),
            _config.fillet_radius,
        )
    return ingress.part


def straight_filament_connector_threads() -> Part:
    """
    the threads for the ingress connector
    """
    with BuildPart(
        Location(
            (
                0,
                _config.bracket_height - _config.minimum_thickness / 2,
                _config.bracket_depth / 2,
            ),
            (90, 0, 0),
        )
    ) as threads:
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
    straight_distance = (
        _config.connector_length / 2 + _config.minimum_structural_thickness
    ) / sqrt(2)

    with BuildLine(mode=Mode.PRIVATE):
        funnel = Line((0, 0), (0, _config.filament_funnel_height))
        bridge = Line(
            funnel @ 1,
            (
                0,
                _config.filament_funnel_height
                + _config.minimum_structural_thickness,
            ),
        )
        curve = CenterArc(
            center=(_config.wheel_radius, (bridge @ 1).Y),
            radius=_config.wheel_radius,
            start_angle=180,
            arc_size=-45,
        )
        output = Line(
            curve @ 1,
            (
                (curve @ 1).X + straight_distance,
                (curve @ 1).Y + straight_distance,
            ),
        )
        bridge.label = "input"
        bridge.color = "RED"
        curve.label = "curve"
        curve.color = "BLUE"
        output.label = "output"
        output.color = "GREEN"
    lines = Compound(children=(funnel, bridge, curve, output))
    return lines


with BuildSketch() as outline:
    Rectangle(
        _config.bracket_width,
        _config.bracket_height,
        align=(Align.CENTER, Align.MIN),
    )
    Circle(radius=_config.wheel_radius + _config.minimum_structural_thickness)


def curved_filament_path_cut() -> Compound:
    """
    returns the shape to be cut out of a curved filament path
    allowing for the PTFE tube and the connector
    """
    path = curved_filament_line()
    with BuildPart() as inlet:
        with BuildLine() as intake:
            add(path.children[0])
        with BuildSketch(Plane(origin=intake.line @ 0, z_dir=intake.line % 0)):
            Circle(radius=_config.tube_outer_diameter * 0.75)
            Rectangle(
                height=_config.tube_outer_diameter * 2,
                width=_config.bearing_depth + _config.wheel_lateral_tolerance,
                mode=Mode.INTERSECT,
            )
        with BuildSketch(Plane(origin=intake.line @ 1, z_dir=intake.line % 1)):
            Circle(_config.tube_inner_radius)
        loft()
        extrude(inlet.faces().sort_by(Axis.Y)[0], _config.bracket_depth)
    with BuildPart() as tube:
        with BuildLine() as tube_path:
            add(path.children[1])
        with BuildSketch(
            Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
        ):
            Circle(_config.tube_outer_radius)
        sweep()
    with BuildPart() as tube_curve:
        with BuildLine() as tube_path:
            add(path.children[2])
        with BuildSketch(
            Plane(origin=tube_path.line @ 0, z_dir=tube_path.line % 0)
        ):
            Circle(_config.tube_outer_radius)
        sweep()
    with BuildPart() as connector:
        with BuildLine() as connector_path:
            add(path.children[3])
        with BuildSketch(
            Plane(
                origin=connector_path.line @ 0, z_dir=connector_path.line % 0
            )
        ):
            Circle(_config.connector_radius)
        sweep()
    with BuildPart() as connector_chamfer:
        with BuildSketch(
            Plane(
                origin=connector_path.line @ 1, z_dir=connector_path.line % 1
            )
        ):
            Circle(_config.connector_radius + _config.minimum_thickness / 2)
        with BuildSketch(
            Plane(
                origin=connector_path.line @ 1, z_dir=connector_path.line % 1
            ).offset(-_config.minimum_thickness / 2)
        ):
            Circle(_config.connector_radius)
        loft()
        extrude(
            connector_chamfer.faces().sort_by(Axis.X)[-1], _config.bracket_depth
        )
    complete = Compound(
        label="curved filament path cut",
        children=(
            inlet.part,
            tube.part,
            tube_curve.part,
            connector.part,
            connector_chamfer.part,
        ),
    ).move(Location((0, 0, _config.bracket_depth / 2)))
    return complete


def curved_filament_path_solid(top_exit_fillet=True) -> Part:
    """ "
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
        with BuildSketch(
            Plane(origin=curve.line @ 0, z_dir=curve.line % 0)
        ) as path_face:
            Rectangle(_config.bracket_depth, _config.bracket_depth)
            fillet(path_face.vertices(), _config.fillet_radius)
        sweep()
        if not top_exit_fillet:
            with BuildLine() as curve2:
                add(curved_filament_line().children[1])
                add(curved_filament_line().children[2])
            with BuildSketch(
                Plane(origin=curve2.line @ 0, z_dir=curve2.line % 0)
            ) as path_face:
                Rectangle(
                    _config.bracket_depth,
                    _config.bracket_depth / 2,
                    align=(Align.CENTER, Align.MAX),
                )
            sweep()
        fillet(
            solid_path.faces().sort_by(Axis.Y)[0].edges().filter_by(Axis.X),
            _config.fillet_radius,
        )
    part = solid_path.part.move(Location((0, 0, _config.bracket_depth / 2)))
    part.label = "curved filament path"
    return part


def curved_filament_connector_threads() -> Part:
    """
    places the threads for the curved filament connector
    """
    with BuildLine() as path:
        add(curved_filament_line())
    offset = (_config.minimum_thickness / 4) / sqrt(2)
    with BuildPart(
        Location(
            (
                (path.line @ 1).X - offset,
                (path.line @ 1).Y - offset,
                _config.bracket_depth / 2,
            ),
            (90, -45, 0),
        )
    ) as threads:
        add(connector_threads())
    part = threads.part
    part.label = "connector threads"
    return part


def curved_filament_path(top_exit_fillet=False, draft=True) -> Part:
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


if __name__ == "__main__":
    show(
        curved_filament_path(top_exit_fillet=True, draft=False).move(
            Location((_config.wheel_radius, 0, 0))
        ),
        straight_filament_path(draft=False).move(
            Location((-_config.wheel_radius, 0, 0))
        ),
        reset_camera=Camera.KEEP,
    )
