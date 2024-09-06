"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""

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
    Sphere,
    add,
    export_stl,
    extrude,
    fillet,
    loft,
)
from ocp_vscode import Camera, show
from pathlib import Path
from partomatic import Partomatic
from bank_config import BankConfig, FrameStyle, LockStyle
from basic_shapes import (
    frame_arched_sidewall_cut,
    frame_flat_sidewall_cut,
    lock_pin,
    rounded_cylinder,
)
from filament_bracket import FilamentBracket
from wall_hanger_cut_template import wall_hanger_cut_template

class FrameSet(Partomatic):
    """The complete set of frames"""
    _config:BankConfig = BankConfig()
    topframe: Part
    bottomframe: Part
    connectorframe: Part
    wallbracket: Part
    lockpin: Part
    bracketclip: Part
    bracket: FilamentBracket

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
                with GridLocations(0, self._config.top_frame_interior_width-self._config.bracket_depth, 1, 2):
                    Sphere(radius=self._config.frame_click_sphere_radius)
            with BuildPart(groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
                with GridLocations(0, self._config.top_frame_interior_width-self._config.bracket_depth, 1, 2):
                    Sphere(radius=self._config.frame_click_sphere_radius * 0.75)
            with BuildPart(mode=Mode.SUBTRACT):
                Box(
                    self._config.wall_thickness + self._config.tolerance,
                    self._config.wall_thickness / 2,
                    self._config.frame_tongue_depth + self._config.tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                with BuildPart(Location((0, 0, self._config.wall_thickness * 0.75))):
                    Sphere(radius=self._config.wall_thickness * 0.5)

        with BuildPart() as grooves:
            with PolarLocations(
                -self._config.sidewall_width / 2 - self._config.wall_thickness / 2, 2
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
                    height=self._config.bracket_depth + self._config.tolerance * 2,
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                    rotation=(90, 0, 0),
                )
                fillet(curve.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((-self._config.wheel_radius - self._config.bracket_depth / 2, 0, 0))
            ) as top_block:
                Box(
                    self._config.frame_bracket_exterior_diameter,
                    self._config.bracket_depth + self._config.tolerance * 2,
                    self._config.bracket_width,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                )
                fillet(top_block.edges(), self._config.fillet_radius)
            add(self.chamber_cut(height=self._config.frame_base_depth * 2))
            if LockStyle.CLIP in self._config.frame_lock_style:
                add(self.bracket.bracket_clip_rail_block(inset=-self._config.tolerance / 2))

        part = cutblock.part.move(Location((0, 0, self._config.frame_base_depth)))
        part.label = "cut block"
        return part


    def chamber_cut(self, height=_config.bracket_height * 3) -> Part:
        """
        a filleted box for each chamber in the lower connectors
        """
        with BuildPart() as cut:
            Box(
                self._config.chamber_cut_length,
                self._config.bracket_depth + self._config.tolerance * 2,
                height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            fillet(cut.edges().filter_by(Axis.Z), radius=self._config.fillet_radius)
        return cut.part


    def connector_frame(self, ) -> Part:
        """
        the connecting frame for supporting the walls of the top and extension
        sections
        """
        with BuildPart() as cframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length,
                    self._config.frame_exterior_width,
                    self._config.frame_connector_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            fillet(cframe.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, 0)), mode=Mode.SUBTRACT
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
                        add(frame_flat_sidewall_cut())
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count
                ):
                    add(self.chamber_cut())
        return cframe.part


    def bottom_frame_stand(self) -> Part:
        """
        a stand for balancing the bottom bracket when sitting on a flat surface
        instead of hanging from a wall
        """
        with BuildPart(
            Location((0, 0, self._config.frame_base_depth)), mode=Mode.PRIVATE
        ) as sectioncut:
            Box(
                self._config.frame_bracket_exterior_diameter * 2,
                self._config.bracket_depth,
                self._config.frame_bracket_exterior_radius - self._config.fillet_radius,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            fillet(sectioncut.edges(), radius=self._config.fillet_radius)

        with BuildPart() as stand:
            Box(
                self._config.frame_exterior_length,
                self._config.frame_exterior_width,
                self._config.frame_bracket_exterior_radius
                + self._config.frame_base_depth
                + self._config.minimum_structural_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, self._config.frame_base_depth)),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.frame_bracket_exterior_diameter
                    - self._config.minimum_structural_thickness * 2,
                    self._config.frame_exterior_width,
                    self._config.frame_bracket_exterior_radius - self._config.fillet_radius,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            fillet(stand.edges(), self._config.fillet_radius)
            with GridLocations(
                0, self._config.frame_bracket_spacing, 1, self._config.filament_count
            ):
                add(sectioncut, mode=Mode.SUBTRACT)

        return stand.part


    def bottom_frame(self) -> Part:
        """
        the bottom frame for supporting the walls
        """

        with BuildPart() as bframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length,
                    self._config.frame_exterior_width,
                    self._config.frame_base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, self._config.frame_base_depth))
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
            if FrameStyle.STANDING in self._config.frame_style:
                add(self.bottom_frame_stand())
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, 0)), mode=Mode.SUBTRACT
            ):
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count
                ):
                    add(self.chamber_cut())
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count + 1
                ):
                    add(frame_arched_sidewall_cut())
                with BuildPart(
                    Location(
                        (self._config.frame_hanger_offset, 0, self._config.frame_base_depth)
                    )
                ):
                    Cylinder(
                        radius=self._config.wheel_radius,
                        height=self._config.frame_exterior_width,
                        rotation=(90, 0, 0),
                    )
                    Box(
                        self._config.wheel_diameter,
                        self._config.frame_exterior_width,
                        self._config.frame_base_depth,
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )
                add(self.straight_wall_grooves().mirror(Plane.XY))
        part = bframe.part
        part.label = "bottom stand with frame"
        return part


    def top_frame(self) -> Part:
        """
        the top frame for fitting the filament brackets and hanging the walls
        """
        with BuildPart() as tframe:
            with BuildPart():
                Box(
                    self._config.frame_exterior_length,
                    self._config.frame_exterior_width,
                    self._config.frame_base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Box(
                    self._config.frame_exterior_length / 2,
                    self._config.frame_exterior_width,
                    self._config.bracket_height,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location((self._config.frame_hanger_offset, 0, self._config.frame_base_depth))
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
                Location((self._config.frame_hanger_offset, 0, 0)), mode=Mode.SUBTRACT
            ):
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count
                ):
                    add(self.bracket_cutblock())

                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count + 1
                ):
                    add(frame_arched_sidewall_cut())
                with BuildPart(
                    Location(
                        (self._config.frame_hanger_offset, 0, self._config.frame_base_depth)
                    )
                ):
                    Cylinder(
                        radius=self._config.wheel_radius,
                        height=self._config.frame_exterior_width,
                        rotation=(90, 0, 0),
                    )
                    Box(
                        self._config.wheel_diameter,
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
                        self._config.bracket_depth + self._config.frame_base_depth,
                    ),
                    (0, 90, 0),
                )
            ):
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count
                ):
                    with GridLocations(
                        0, self._config.bracket_depth + self._config.tolerance * 2, 1, 2
                    ):
                        add(
                            rounded_cylinder(
                                radius=self._config.wall_thickness - self._config.tolerance,
                                height=self._config.bracket_depth,
                                align=(Align.CENTER, Align.CENTER, Align.MIN),
                            )
                        )

            with BuildPart(
                Location(
                    (
                        self._config.frame_click_sphere_point.x + self._config.frame_hanger_offset,
                        0,
                        self._config.frame_click_sphere_point.y
                        + self._config.frame_base_depth,
                    )
                )
            ):
                with GridLocations(
                    0, self._config.frame_bracket_spacing, 1, self._config.filament_count
                ):
                    with GridLocations(
                        0, self._config.bracket_depth + self._config.tolerance * 2, 1, 2
                    ):
                        Sphere(self._config.frame_click_sphere_radius * 0.75)

            if FrameStyle.HANGING in self._config.frame_style:
                with BuildPart(
                    Location((-self._config.frame_exterior_length / 2, 0, 0)),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        wall_hanger_cut_template(
                            self._config.minimum_structural_thickness * 1.5,
                            self._config.frame_exterior_width-self._config.minimum_structural_thickness*2,
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
                            self._config.wheel_radius
                            + self._config.bracket_depth / 2
                            + self._config.frame_hanger_offset,
                            0,
                            self._config.bracket_depth
                            + self._config.minimum_structural_thickness / 2
                            + self._config.frame_base_depth,
                        )
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        lock_pin(
                            tolerance=-self._config.frame_lock_pin_tolerance / 2,
                            tie_loop=False,
                        )
                    )
                with BuildPart(
                    Location(
                        (
                            self._config.frame_exterior_length / 2
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
                self._config.frame_exterior_width -self._config.minimum_structural_thickness - self._config.tolerance*2,
                self._config.bracket_height,
                align=(Align.MIN, Align.CENTER, Align.MIN),
            )
            fillet(
                bracket.edges(),
                self._config.minimum_structural_thickness / self._config.fillet_ratio,
            )
            with BuildPart(mode=Mode.INTERSECT):
                add(
                    wall_hanger_cut_template(
                        self._config.minimum_structural_thickness * 1.5,
                        self._config.frame_exterior_width-self._config.minimum_structural_thickness*2,
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
                add(self.screw_head())
        return bracket.part


    def screw_head(self) -> Part:
        """
        template for the cutout for a screwhead
        """
        with BuildPart() as head:
            with BuildSketch():
                Circle(self._config.wall_bracket_screw_head_radius)
            with BuildSketch(Plane.XY.offset(self._config.wall_bracket_screw_head_sink)):
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
                Plane.XY.offset(self._config.minimum_structural_thickness * 2)
            ):
                Circle(self._config.wall_bracket_screw_radius)
            loft(ruled=True)
        return head.part

    def load_config(self, configuration_path: str):
        self._config.load_config(configuration_path)
        self.bracket = FilamentBracket(configuration_path)

    def __init__(self, configuration_file:str):
        super(Partomatic, self).__init__()
        self.load_config(configuration_file)

    def compile(self):
        self.bracketclip = self.bracket.bracket_clip(inset=self._config.tolerance / 2).move(
            Location(
                (
                    self._config.bracket_depth,
                    0,
                    self._config.frame_clip_point.y
                    - self._config.minimum_structural_thickness / 2,
                )
            )
        )
        self.topframe = self.top_frame()
        self.bottomframe = self.bottom_frame()
        self.connectorframe = self.connector_frame()
        self.wallbracket = self.wall_bracket()
        self.lockpin = lock_pin(
            tolerance=self._config.frame_lock_pin_tolerance / 2, tie_loop=True
        )

    def display(self):
        show(
            self.topframe,
            # self.bracket.bottom_bracket_block()
            # .move(Location((0, 0, -self._config.bracket_depth / 2)))
            # .rotate(Axis.X, 90)
            # .move(
            #     Location(
            #         (
            #             self._config.frame_hanger_offset + self._config.tolerance,
            #             0,
            #             self._config.frame_base_depth,
            #         )
            #     )
            # ),
            # self.bracketclip if LockStyle.CLIP in self._config.frame_lock_style else None,
            # (
            #     self.lockpin.move(
            #         Location(
            #             (
            #                 self._config.wheel_radius
            #                 + self._config.bracket_depth / 2
            #                 + self._config.frame_hanger_offset,
            #                 self._config.frame_exterior_width / 2,
            #                 self._config.bracket_depth
            #                 + self._config.minimum_structural_thickness / 2
            #                 + self._config.frame_base_depth
            #                 + self._config.frame_lock_pin_tolerance / 2,
            #             )
            #         )
            #     )
            #     if LockStyle.PIN in self._config.frame_lock_style
            #     else None
            # ),
            # self.bottomframe.rotate(axis=Axis.X, angle=180).move(
            #     Location((0, 0, -self._config.frame_base_depth * 3))
            # ),
            # self.connectorframe.move(Location((0, 0, -self._config.frame_base_depth * 2))),
            # self.wallbracket.move(
            #     Location(
            #         (
            #             -self._config.frame_exterior_length / 2
            #             - self._config.minimum_structural_thickness * 3,
            #             0,
            #             0,
            #         )
            #     )
            # ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.topframe, str(output_directory / "frame-top.stl"))
        export_stl(self.bottomframe, str(output_directory / "frame-bottom.stl"))
        export_stl(self.connectorframe, str(output_directory / "frame-connector.stl"))
        export_stl(self.wallbracket, str(output_directory / "frame-wall-bracket.stl"))
        if LockStyle.PIN in self._config.frame_lock_style:
            export_stl(self.lockpin, str(output_directory / "frame-lock-pin.stl"))

    def render_2d(self):
        pass

if __name__ == "__main__":
    frameset = FrameSet(Path(__file__).parent / "../build-configs/debug.conf")
    frameset.compile()
    frameset.display()
    frameset.export_stls()
