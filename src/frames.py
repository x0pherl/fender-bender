"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Rectangle,
    Sketch,
    Sphere,
    add,
    export_stl,
    extrude,
    fillet,
    loft,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig, FrameStyle, LockStyle
from basic_shapes import rounded_cylinder
from filament_bracket import FilamentBracket
from lock_pin import LockPin
from partomatic import Partomatic
from wall_hanger_cut_template import wall_hanger_cut_template


class FrameSet(Partomatic):
    """The complete set of frames"""

    _config: BenderConfig = BenderConfig()
    hangingtopframe: Part
    standingtopframe: Part
    standingbottomframe: Part
    hangingbottomframe: Part
    hybridbottomframe: Part
    hybridconnectorframe: Part
    standingconnectorframe: Part
    wallbracket: Part
    bracketclip: Part
    _bracket = FilamentBracket(None)
    _lockpin = LockPin(None)

    def _frame_flat_sidewall_cut(
        self, thickness=_config.wall_thickness
    ) -> Part:
        """
        builds a side of the frame
        -------
        arguments:
            - thickness: determines the depth of the wall
        """
        mid_adjustor = thickness / 2
        with BuildPart() as side:
            with BuildPart():
                with BuildSketch(Plane.XY.offset(-thickness / 4)):
                    Rectangle(
                        width=self._config.sidewall_width,
                        height=1,
                        align=(Align.CENTER, Align.MAX),
                    )
                with BuildSketch():
                    Rectangle(
                        width=self._config.sidewall_width,
                        height=1 + mid_adjustor,
                        align=(Align.CENTER, Align.MAX),
                    )
                with BuildSketch(Plane.XY.offset(thickness / 4)):
                    Rectangle(
                        width=self._config.sidewall_width,
                        height=1,
                        align=(Align.CENTER, Align.MAX),
                    )
                loft(ruled=True)
        part = side.part.rotate(Axis.X, 90)
        part.label = "Frame Side"
        return part

    def _frame_cut_sketch(self, inset=0) -> Sketch:
        """
        the overall shape of the sidewall with the arch
        -------
        arguments:
            - inset: amount to inset the sketch
        """
        with BuildSketch(mode=Mode.PRIVATE) as wall:
            Rectangle(
                width=self._config.sidewall_width,
                height=1 - inset * 2,
                align=(Align.CENTER, Align.MAX),
            )
        with BuildSketch() as side:
            Circle(radius=self._config.wheel.radius - inset)
            Rectangle(
                width=self._config.wheel.diameter - inset * 2,
                height=self._config.frame_base_depth,
                align=(Align.CENTER, Align.MAX),
            )
            add(
                wall.sketch.move(
                    Location((0, -self._config.frame_base_depth - inset))
                )
            )
        return side.sketch.move(Location((0, self._config.frame_base_depth)))

    def _frame_arched_sidewall_cut(
        self, thickness=_config.wall_thickness
    ) -> Part:
        """
        a template to subtract in order to create the groove
        for fitting the side wall
        -------
        arguments:
            - thickness: determines the depth of the wall
        """
        mid_adjustor = thickness / 4
        with BuildPart() as side:
            with BuildPart():
                with BuildSketch(Plane.XY.offset(-thickness / 4)):
                    add(self._frame_cut_sketch(inset=0))
                with BuildSketch():
                    add(self._frame_cut_sketch(inset=-mid_adjustor))
                with BuildSketch(Plane.XY.offset(mid_adjustor)):
                    add(self._frame_cut_sketch(inset=0))
                loft(ruled=True)
        part = side.part.rotate(Axis.X, 90)
        part.label = "Frame Side"
        return part

    def straight_wall_grooves(self) -> Part:
        """
        creates the grooves in the frame peices for the front and back walls
        """
        with BuildPart(mode=Mode.PRIVATE) as groove:
            Box(
                self._config.wall_thickness + self._config.tolerance,
                self._config.top_frame_interior_width + self._config.tolerance,
                self._config.frame_tongue_depth
                - self._config.wall_thickness / 2
                + self._config.tolerance,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            extrude(
                groove.faces().sort_by(Axis.Z)[-1],
                amount=self._config.wall_thickness / 2,
                taper=44,
            )
            with BuildPart(groove.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
                with GridLocations(
                    0,
                    self._config.top_frame_interior_width
                    - self._config.bracket_depth,
                    1,
                    2,
                ):
                    Sphere(radius=self._config.frame_click_sphere_radius)
            with BuildPart(
                groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT
            ):
                with GridLocations(
                    0,
                    self._config.top_frame_interior_width
                    - self._config.bracket_depth,
                    1,
                    2,
                ):
                    Sphere(
                        radius=self._config.frame_click_sphere_radius * 0.75
                    )
            with BuildPart(mode=Mode.SUBTRACT):
                Box(
                    self._config.wall_thickness + self._config.tolerance,
                    self._config.wall_thickness / 2,
                    self._config.frame_tongue_depth + self._config.tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                with BuildPart(
                    Location((0, 0, self._config.wall_thickness * 0.75))
                ):
                    Sphere(radius=self._config.wall_thickness * 0.5)

        with BuildPart() as grooves:
            with PolarLocations(
                -self._config.sidewall_width / 2
                - self._config.wall_thickness / 2,
                2,
            ):
                add(groove.part.mirror())
        return grooves.part

    def bracket_cutblock(self) -> Part:
        """
        the block that needs to be cut for each filament bracket in the top frame
        """
        with BuildPart() as cutblock:
            with BuildPart(Location((0, 0, 0))) as curve:
                Cylinder(
                    radius=self._config.frame_bracket_exterior_radius,
                    height=self._config.bracket_depth
                    + self._config.tolerance * 2,
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                    rotation=(90, 0, 0),
                )
                fillet(curve.edges(), self._config.fillet_radius)
            with BuildPart(
                Location(
                    (
                        -self._config.wheel.radius
                        - self._config.bracket_depth / 2,
                        0,
                        0,
                    )
                )
            ) as top_block:
                Box(
                    self._config.frame_bracket_exterior_diameter,
                    self._config.bracket_depth + self._config.tolerance * 2,
                    self._config.bracket_width,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                )
                fillet(top_block.edges(), self._config.fillet_radius)
            # add(self.chamber_cut(height=self._config.frame_base_depth * 2))
            with BuildPart() as chambercut:
                Box(
                    self._config.chamber_cut_length,
                    self._config.bracket_depth
                    - self._config.fillet_radius * 2
                    + self._config.tolerance * 2,
                    self._config.frame_base_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )
                fillet(
                    chambercut.edges().filter_by(Axis.Z),
                    self._config.fillet_radius,
                )
                with BuildPart(
                    Location(
                        (
                            self._config.default_connector.tube.outer_diameter
                            * 0.375,
                            0,
                            0,
                        )
                    )
                ) as outer:
                    Box(
                        self._config.chamber_cut_length
                        - (
                            self._config.default_connector.tube.outer_diameter
                            * 0.75
                        ),
                        self._config.bracket_depth
                        + self._config.tolerance * 2,
                        self._config.frame_base_depth * 2,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    )
                    fillet(
                        outer.edges().filter_by(Axis.Z),
                        self._config.fillet_radius,
                    )

            if LockStyle.CLIP in self._config.frame_lock_style:
                add(
                    self._bracket.bracket_clip_rail_block(
                        inset=-self._config.tolerance / 2
                    )
                )

        part = cutblock.part.move(
            Location((0, 0, self._config.frame_base_depth))
        )
        part.label = "cut block"
        return part

    def _chamber_cut(self, height=_config.bracket_height * 3) -> Part:
        """
        a filleted box for each chamber in the lower connectors
        -------
        arguments:
            - height: the height of the chamber cut
        """
        with BuildPart() as cut:
            Box(
                self._config.chamber_cut_length,
                self._config.bracket_depth + self._config.tolerance * 2,
                height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            fillet(
                cut.edges().filter_by(Axis.Z),
                radius=self._config.fillet_radius,
            )
        return cut.part

    def connector_frame(self, frame_style=FrameStyle.HYBRID) -> Part:
        """
        the connecting frame for supporting the walls of the top and extension
        sections
        """
        with BuildPart() as cframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length(
                        frame_style=frame_style
                    ),
                    self._config.frame_exterior_width,
                    self._config.frame_connector_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            fillet(cframe.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                with Locations(
                    cframe.faces().sort_by(Axis.Z)[-1],
                    cframe.faces().sort_by(Axis.Z)[0],
                ):
                    add(self.straight_wall_grooves())
                    with GridLocations(
                        0,
                        self._config.frame_bracket_spacing,
                        1,
                        self._config.filament_count + 1,
                    ):
                        add(self._frame_flat_sidewall_cut())
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    add(self._chamber_cut())
        return cframe.part

    def _bottom_frame_stand_sectioncut(self) -> Part:
        """
        cuts along the side of the bottom frame stand;
        purely aesthetic.
        """
        with BuildPart(
            Location((0, 0, self._config.frame_base_depth))
        ) as sectioncut:
            Box(
                self._config.frame_bracket_exterior_diameter * 2,
                self._config.bracket_depth,
                self._config.frame_bracket_exterior_radius
                - self._config.fillet_radius,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            fillet(sectioncut.edges(), radius=self._config.fillet_radius)
        return sectioncut.part

    @property
    def _bottom_frame_stand_height(self) -> float:
        """The height of the bottom frame stand"""
        return (
            self._config.frame_bracket_exterior_radius
            + self._config.frame_base_depth
            + self._config.minimum_structural_thickness
        )

    def _bottom_frame_stand(self, frame_style=FrameStyle.STANDING) -> Part:
        """
        a stand for balancing the bottom bracket when sitting on a flat surface
        instead of hanging from a wall
        """

        with BuildPart() as stand:
            Box(
                self._config.frame_exterior_length(frame_style=frame_style),
                self._config.frame_exterior_width,
                self._bottom_frame_stand_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Location(
                    (
                        self._config.frame_hanger_offset,
                        0,
                        self._config.frame_base_depth,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.frame_bracket_exterior_diameter
                    - self._config.minimum_structural_thickness * 2,
                    self._config.frame_exterior_width,
                    self._config.frame_bracket_exterior_radius
                    - self._config.fillet_radius,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            fillet(stand.edges(), self._config.fillet_radius)
            with GridLocations(
                0,
                self._config.frame_bracket_spacing,
                1,
                self._config.filament_count,
            ):
                add(self._bottom_frame_stand_sectioncut(), mode=Mode.SUBTRACT)

        return stand.part

    def bottom_frame(self, frame_style=FrameStyle.HYBRID) -> Part:
        """
        the bottom frame for supporting the walls
        """

        with BuildPart() as bframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length(
                        frame_style=frame_style
                    ),
                    self._config.frame_exterior_width,
                    self._config.frame_base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location(
                    (
                        self._config.frame_hanger_offset,
                        0,
                        self._config.frame_base_depth,
                    )
                )
            ):
                Cylinder(
                    radius=self._config.frame_bracket_exterior_radius,
                    height=self._config.frame_exterior_width,
                    rotation=(90, 0, 0),
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                )
            edge_set = (
                bframe.edges()
                - bframe.edges().filter_by_position(
                    Axis.X,
                    minimum=self._config.frame_bracket_exterior_radius
                    + self._config.frame_hanger_offset
                    - 1,
                    maximum=self._config.frame_bracket_exterior_radius
                    + self._config.frame_hanger_offset
                    + 1,
                )
                - bframe.edges().filter_by_position(
                    Axis.X,
                    minimum=-self._config.frame_bracket_exterior_radius
                    + self._config.frame_hanger_offset
                    - 1,
                    maximum=-self._config.frame_bracket_exterior_radius
                    + self._config.frame_hanger_offset
                    + 1,
                )
            )
            fillet(edge_set, self._config.fillet_radius)
            if FrameStyle.STANDING in frame_style:
                add(self._bottom_frame_stand(frame_style=frame_style))
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    add(
                        self._chamber_cut(
                            self._config.frame_bracket_exterior_diameter
                            + self._config.frame_base_depth * 4
                        )
                    )
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count + 1,
                ):
                    add(self._frame_arched_sidewall_cut())
                with BuildPart(
                    Location(
                        (
                            self._config.frame_hanger_offset,
                            0,
                            self._config.frame_base_depth,
                        )
                    )
                ):
                    Cylinder(
                        radius=self._config.wheel.radius,
                        height=self._config.frame_exterior_width,
                        rotation=(90, 0, 0),
                    )
                    Box(
                        self._config.wheel.diameter,
                        self._config.frame_exterior_width,
                        self._config.frame_base_depth,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )
                add(self.straight_wall_grooves().mirror(Plane.XY))
            if frame_style == FrameStyle.HYBRID:
                add(self._screw_fitting())
                with BuildPart(
                    Location(
                        (
                            -self._config.frame_exterior_length(
                                frame_style=frame_style
                            )
                            / 2
                            + self._config.minimum_structural_thickness * 2
                            + self._config.frame_hanger_offset,
                            0,
                            self._bottom_frame_stand_height
                            - self._config.minimum_structural_thickness,
                        ),
                        (0, 225, 0),
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(self._screw_cut())
            elif frame_style == FrameStyle.HANGING:
                tab_width = (
                    self._config.minimum_structural_thickness
                    + self._config.fillet_radius
                    + self._config.frame_hanger_offset
                )
                with BuildPart(
                    Location(
                        (
                            -self._config.frame_exterior_length(
                                frame_style=frame_style
                            )
                            / 2,
                            0,
                            self._config.fillet_radius,
                        )
                    )
                ) as tab:
                    Box(
                        tab_width,
                        self._config.bracket_depth,
                        self._config.bracket_depth
                        + self._config.frame_base_depth,
                        align=(Align.MIN, Align.CENTER, Align.MIN),
                    )
                    fillet(
                        (tab.edges() - tab.faces().sort_by(Axis.X)[0].edges()),
                        self._config.fillet_radius,
                    )
                with BuildPart(
                    Location(
                        (
                            -self._config.frame_exterior_length(
                                frame_style=frame_style
                            )
                            / 2
                            + tab_width / 2,
                            0,
                            self._config.frame_base_depth
                            + self._config.fillet_radius,
                        ),
                        (0, 225, 0),
                    ),
                    mode=Mode.SUBTRACT,
                ) as cutter:
                    add(self._screw_cut())
                    extrude(
                        cutter.faces().sort_by(Axis.Z)[-1],
                        amount=self._config.frame_chamber_depth,
                    )
        part = bframe.part
        part.label = "bottom stand with frame"
        return part

    def top_frame(self, frame_style=FrameStyle.HYBRID) -> Part:
        """
        the top frame for fitting the filament brackets and hanging the walls
        """
        with BuildPart() as tframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length(
                        frame_style=frame_style
                    ),
                    self._config.frame_exterior_width,
                    self._config.frame_base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Box(
                    self._config.frame_exterior_length(frame_style=frame_style)
                    / 2,
                    self._config.frame_exterior_width,
                    self._config.bracket_height,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location(
                    (
                        self._config.frame_hanger_offset,
                        0,
                        self._config.frame_base_depth,
                    )
                )
            ):
                Cylinder(
                    radius=self._config.frame_bracket_exterior_radius,
                    height=self._config.frame_exterior_width,
                    rotation=(90, 0, 0),
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                )
            edge_set = tframe.edges() - tframe.edges().filter_by_position(
                Axis.X,
                minimum=self._config.frame_bracket_exterior_radius
                + self._config.frame_hanger_offset
                - 1,
                maximum=self._config.frame_bracket_exterior_radius
                + self._config.frame_hanger_offset
                + 1,
            )
            fillet(edge_set, self._config.fillet_radius)
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    add(self.bracket_cutblock())

                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count + 1,
                ):
                    add(self._frame_arched_sidewall_cut())
                with BuildPart(
                    Location(
                        (
                            self._config.frame_hanger_offset,
                            0,
                            self._config.frame_base_depth,
                        )
                    )
                ):
                    Cylinder(
                        radius=self._config.wheel.radius,
                        height=self._config.frame_exterior_width,
                        rotation=(90, 0, 0),
                    )
                    Box(
                        self._config.wheel.diameter,
                        self._config.frame_exterior_width,
                        self._config.frame_base_depth,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )
                add(self.straight_wall_grooves().mirror(Plane.XY))

            with BuildPart(
                Location(
                    (
                        -self._config.frame_bracket_exterior_radius,
                        0,
                        self._config.bracket_depth
                        + self._config.frame_base_depth,
                    ),
                    (0, 90, 0),
                )
            ):
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    with GridLocations(
                        0,
                        self._config.bracket_depth
                        + self._config.tolerance * 2,
                        1,
                        2,
                    ):
                        add(
                            rounded_cylinder(
                                radius=self._config.wall_thickness
                                - self._config.tolerance,
                                height=self._config.bracket_depth,
                                align=(Align.CENTER, Align.CENTER, Align.MIN),
                            )
                        )

            with BuildPart(
                Location(
                    (
                        self._config.frame_click_sphere_point.x
                        + self._config.frame_hanger_offset,
                        0,
                        self._config.frame_click_sphere_point.y
                        + self._config.frame_base_depth,
                    )
                )
            ):
                with GridLocations(
                    0,
                    self._config.frame_bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    with GridLocations(
                        0,
                        self._config.bracket_depth
                        + self._config.tolerance * 2,
                        1,
                        2,
                    ):
                        Sphere(self._config.frame_click_sphere_radius * 0.75)

            if FrameStyle.HANGING in frame_style:
                with BuildPart(
                    Location(
                        (
                            -self._config.frame_exterior_length(
                                frame_style=frame_style
                            )
                            / 2,
                            0,
                            0,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        wall_hanger_cut_template(
                            self._config.minimum_structural_thickness * 1.5,
                            self._config.frame_exterior_width
                            - self._config.minimum_structural_thickness * 2,
                            self._config.bracket_height,
                            bottom=False,
                            post_count=self._config.wall_bracket_post_count,
                            tolerance=self._config.tolerance,
                        )
                    )

            if LockStyle.PIN in self._config.frame_lock_style:
                with BuildPart(
                    Location(
                        (
                            self._config.wheel.radius
                            + self._config.bracket_depth / 2
                            + self._config.frame_hanger_offset
                            + self._config.frame_lock_pin_tolerance,
                            0,
                            self._config.bracket_depth
                            + self._config.minimum_structural_thickness / 2
                            + self._config.frame_base_depth,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        self._lockpin.lock_pin(
                            inset=-self._config.frame_lock_pin_tolerance / 2,
                            tie_loop=False,
                        )
                    )
                with BuildPart(
                    Location(
                        (
                            self._config.frame_exterior_length(
                                frame_style=frame_style
                            )
                            / 2
                            - self._config.fillet_radius,
                            0,
                            0,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ) as stringcut:
                    Box(
                        self._config.minimum_thickness * 2,
                        self._config.minimum_structural_thickness * 2,
                        self._config.frame_base_depth,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    fillet(
                        stringcut.edges().filter_by(Axis.Z),
                        self._config.minimum_thickness * 0.9,
                    )
        part = tframe.part
        part.label = "Top Frame"
        return part

    def wall_bracket(self) -> Part:
        """
        the part for hanging the top bracket on the wall
        """
        with BuildPart() as bracket:
            Box(
                self._config.minimum_structural_thickness * 3,
                self._config.frame_exterior_width
                - self._config.minimum_structural_thickness
                - self._config.tolerance * 2,
                self._config.bracket_height,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            fillet(
                bracket.edges(),
                self._config.minimum_structural_thickness
                / self._config.fillet_ratio,
            )
            with BuildPart(mode=Mode.INTERSECT):
                add(
                    wall_hanger_cut_template(
                        self._config.minimum_structural_thickness * 1.5,
                        self._config.frame_exterior_width
                        - self._config.minimum_structural_thickness * 2,
                        self._config.bracket_height,
                        bottom=True,
                        post_count=self._config.wall_bracket_post_count,
                        tolerance=self._config.tolerance,
                    )
                )
            with BuildPart(
                Location(
                    (
                        self._config.minimum_structural_thickness + 0.33,
                        0,
                        self._config.bracket_height / 2,
                    ),
                    (0, -90, 0),
                ),
                mode=Mode.SUBTRACT,
            ):
                add(self._screw_cut())
        return bracket.part

    def _screw_cut(self) -> Part:
        """
        template for the cutout for a screwhead
        """
        with BuildPart() as head:
            with BuildSketch(Plane.XY.offset(-self._config.bracket_depth)):
                Circle(self._config.wall_bracket_screw_head_radius)
            with BuildSketch(
                Plane.XY.offset(self._config.wall_bracket_screw_head_sink)
            ):
                Circle(self._config.wall_bracket_screw_head_radius)
            with BuildSketch(
                Plane.XY.offset(
                    self._config.wall_bracket_screw_head_sink
                    + self._config.wall_bracket_screw_head_radius
                    - self._config.wall_bracket_screw_radius
                )
            ):
                Circle(self._config.wall_bracket_screw_radius)
            with BuildSketch(
                Plane.XY.offset(self._config.frame_chamber_depth)
            ):
                Circle(self._config.wall_bracket_screw_radius)
            loft(ruled=True)
        return head.part

    def _screw_fitting(self, frame_style=FrameStyle.HYBRID) -> Part:
        """
        a fitting for screwing the bracket to the wall
        """
        with BuildPart(
            Location(
                (
                    -self._config.frame_exterior_length(
                        frame_style=frame_style
                    )
                    / 2,
                    0,
                    self._config.frame_bracket_exterior_radius
                    + self._config.frame_base_depth
                    + self._config.minimum_structural_thickness
                    - self._config.fillet_radius,
                )
            )
        ) as fitting:
            Box(
                (
                    self._config.frame_exterior_length(frame_style=frame_style)
                    - (
                        self._config.frame_bracket_exterior_diameter
                        - self._config.minimum_structural_thickness * 2
                    )
                )
                / 2,
                self._config.frame_bracket_spacing,
                self._config.frame_bracket_exterior_radius / 2,
                align=(Align.MIN, Align.CENTER, Align.MAX),
            )
            with BuildPart(
                fitting.faces()
                .sort_by(Axis.Z)[0]
                .offset(-self._config.fillet_radius),
                mode=Mode.SUBTRACT,
            ) as cut:
                Box(
                    self._config.frame_exterior_length(
                        frame_style=frame_style
                    ),
                    self._config.bracket_depth,
                    self._config.fillet_radius * 3,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                fillet(
                    cut.edges().filter_by(Axis.X), self._config.fillet_radius
                )
            with BuildPart(mode=Mode.INTERSECT):
                add(self._bottom_frame_stand_sectioncut())
        screwfitting = fitting.part
        screwfitting.label = "Screw Fitting"
        return screwfitting

    def load_config(self, configuration_path: str):
        """
        loads the configuration file
         -------
        arguments:
            - configuration_path: the path to the configuration file
        """
        self._config.load_config(configuration_path)
        self._bracket.load_config(configuration_path)
        self._lockpin.load_config(configuration_path)

    def __init__(self, configuration_file: str):
        """
        initializes the Partomatic filament wheel
        -------
        arguments:
            - configuration_file: the path to the configuration file,
        set to None to use the default configuration
        """
        super(Partomatic, self).__init__()
        if configuration_file is not None:
            self.load_config(configuration_file)

    def compile(self):
        """
        Builds the relevant parts for the frame
        """
        self.bracketclip = self._bracket.bracket_clip(
            inset=self._config.tolerance / 2
        ).move(
            Location(
                (
                    self._config.bracket_depth,
                    0,
                    self._config.frame_clip_point.y
                    - self._config.minimum_structural_thickness / 2,
                )
            )
        )
        self.hangingtopframe = self.top_frame(frame_style=FrameStyle.HANGING)
        self.standingtopframe = self.top_frame(frame_style=FrameStyle.STANDING)
        self.hybridbottomframe = (
            self.bottom_frame(frame_style=FrameStyle.HYBRID)
            .rotate(Axis.X, 180)
            .move(Location((0, 0, -self._config.frame_base_depth)))
        )
        self.hangingbottomframe = self.bottom_frame(
            frame_style=FrameStyle.HANGING
        )
        self.standingbottomframe = (
            self.bottom_frame(frame_style=FrameStyle.STANDING)
            .rotate(Axis.X, 180)
            .move(Location((0, 0, -self._config.frame_base_depth)))
        )
        self.standingconnectorframe = self.connector_frame(
            frame_style=FrameStyle.STANDING
        )
        self.hangingconnectorframe = self.connector_frame(
            frame_style=FrameStyle.HANGING
        )
        self.wallbracket = self.wall_bracket()

    def display(self):
        """
        Shows the filament wheel in OCP CAD Viewer
        """
        show(
            self.hangingtopframe,
            self._bracket.bottom_bracket_block()
            .move(Location((0, 0, -self._config.bracket_depth / 2)))
            .rotate(Axis.X, 90)
            .move(
                Location(
                    (
                        self._config.frame_hanger_offset
                        + self._config.tolerance,
                        0,
                        self._config.frame_base_depth,
                    )
                )
            ),
            (
                self.bracketclip
                if LockStyle.CLIP in self._config.frame_lock_style
                else None
            ),
            self.hybridbottomframe.move(
                Location((0, 0, -self._config.frame_base_depth * 3))
            ),
            self.hangingconnectorframe.move(
                Location((0, 0, -self._config.frame_base_depth * 2))
            ),
            self.wallbracket.move(
                Location(
                    (
                        -self._config.frame_exterior_length(
                            frame_style=FrameStyle.HANGING
                        )
                        / 2
                        - self._config.minimum_structural_thickness * 3,
                        0,
                        0,
                    )
                )
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        """
        Generates the frame STLs in the configured
        folder
        """
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(
            self.hangingtopframe, str(output_directory / "frame-top.stl")
        )
        export_stl(
            self.standingtopframe,
            str(output_directory / "frame-top-alt-standing.stl"),
        )
        export_stl(
            self.hybridbottomframe, str(output_directory / "frame-bottom.stl")
        )
        export_stl(
            self.hangingbottomframe,
            str(output_directory / "frame-bottom-alt-hanging-no-stand.stl"),
        )
        export_stl(
            self.standingbottomframe,
            str(output_directory / "frame-bottom-alt-standing.stl"),
        )
        export_stl(
            self.hangingconnectorframe,
            str(output_directory / "frame-connector.stl"),
        )
        export_stl(
            self.standingconnectorframe,
            str(output_directory / "frame-connector-alt-standing.stl"),
        )
        export_stl(
            self.wallbracket, str(output_directory / "frame-wall-bracket.stl")
        )

    def render_2d(self):
        """
        not yet implemented
        """
        pass


if __name__ == "__main__":
    frameset = FrameSet(Path(__file__).parent / "../build-configs/debug.conf")
    frameset.compile()
    frameset.display()
    frameset.export_stls()
