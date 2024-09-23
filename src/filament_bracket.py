"""
Generates the part for the filament bracket of our filament bank design
The filament bracket allows for filament to smoothly pass around the wheel
when feeding into the printer, and redirecting the filament downwards into
the frame when the filament backs out of the MMU.
"""

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    Cone,
    Cylinder,
    GeomType,
    GridLocations,
    Line,
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
    make_face,
    offset,
)
from ocp_vscode import Camera, show

from bank_config import BankConfig, LockStyle
from basic_shapes import rounded_cylinder
from filament_channels import FilamentChannels
from lock_pin import LockPin
from partomatic import Partomatic


class FilamentBracket(Partomatic):
    """The partomatic for the filament bracket of the filament bank"""

    _config = BankConfig()
    _filamentchannels = FilamentChannels(None)
    _lockpin = LockPin(None)

    bottom: Part
    top: Part
    bracketclip: Part

    @property
    def _wheel_guide_outer_radius(self) -> float:
        return (
            self._config.wheel_radius
            + self._config.wheel_radial_tolerance
            + self._config.wheel_support_height
        )

    @property
    def _wheel_guide_inner_radius(self) -> float:
        return self._wheel_guide_outer_radius - self._spoke_thickness

    @property
    def _spoke_thickness(self) -> float:
        return self._config.wheel_support_height * 1.5

    def _wheel_guide_cut(self) -> Part:
        """
        the cutout shape for a wheel guide
        """

        with BuildPart() as wheelcut:
            Cone(
                bottom_radius=self._wheel_guide_inner_radius,
                top_radius=self._wheel_guide_inner_radius
                - self._config.wheel_support_height,
                height=self._config.wheel_support_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        return wheelcut.part

    def _bracket_spoke(self) -> Part:
        """
        returns ts single spoke part for the filament wheel
        """
        spoke_outer_radius = (
            self._wheel_guide_inner_radius / 2 + self._spoke_thickness
        )
        spoke_shift = spoke_outer_radius - self._spoke_thickness
        with BuildPart() as spoke:
            with BuildPart(Location((spoke_shift, 0, 0))):
                Cylinder(
                    radius=spoke_outer_radius,
                    height=self._config.wheel_support_height,
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.MIN),
                )
                Cylinder(
                    radius=spoke_outer_radius - self._spoke_thickness,
                    height=self._config.wheel_support_height,
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
        return spoke.part

    def _spoke_assembly(self) -> Part:
        """
        adds the axle for the filament wall bearing, along with the spokes
        """
        with BuildPart() as constructed_brace:
            with BuildPart() as spokes:
                with PolarLocations(0, 3, start_angle=45):
                    add(self._bracket_spoke())
                with BuildPart(mode=Mode.INTERSECT):
                    add(self._wheel_guide_cut())
            Cylinder(
                radius=self._config.bearing_shelf_radius,
                height=self._config.bearing_shelf_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=self._config.bearing_inner_radius,
                height=self._config.bracket_depth / 2
                - self._config.wheel_lateral_tolerance,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=self._spoke_thickness,
                height=self._config.wheel_support_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        part = constructed_brace.part
        part.label = "spoke assembly"
        return part

    def _wheel_guide(self) -> Part:
        """
        The outer ring responsible for guiding the
        filament wheel and keeping it straight
        """
        with BuildPart() as wheel_brace:
            Cone(
                bottom_radius=self._wheel_guide_outer_radius,
                top_radius=self._wheel_guide_outer_radius
                - self._config.wheel_support_height,
                height=self._config.wheel_support_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(mode=Mode.SUBTRACT):
                add(self._wheel_guide_cut())
        part = wheel_brace.part
        part.label = "rim"
        return part

    def _top_cut_shape(self, inset: float = 0) -> Sketch:
        """
        returns a 2d scetch of the basic shape used for the top cutout
        of the filament bracket
        -------
        arguments:
            - inset: an inset amount allowing tolerance in the printed parts
        """
        base_outer_radius = self._wheel_guide_outer_radius - inset
        with BuildSketch(mode=Mode.PRIVATE) as base_template:
            Circle(base_outer_radius)
            Rectangle(
                base_outer_radius * 2,
                self._config.bracket_height * 2,
                align=(Align.CENTER, Align.MAX, Align.MIN),
            )
            Rectangle(
                base_outer_radius,
                self._config.bracket_height * 2,
                align=(Align.CENTER, Align.MIN, Align.MIN),
            )
        return base_template.sketch

    def _top_cut_template(self, tolerance: float = 0) -> Part:
        """
        returns the shape defining the top cut of the bracket
        (the part that slides into place to hold the filament wheel in place)
        -------
        arguments:
            - tolerance: an inset amount allowing tolerance in the printed parts
        """
        with BuildPart() as cut:
            with BuildSketch():
                add(self._top_cut_shape(-tolerance))
            with BuildSketch(
                Plane.XY.offset(self._config.wheel_support_height)
            ):
                add(
                    self._top_cut_shape(
                        -tolerance - self._config.wheel_support_height
                    )
                )
            loft()
        return cut.part

    def bracket_clip_rail_block(
        self, inset=0, frame_depth=_config.frame_clip_point.y
    ) -> Part:
        """
        the basic shape defining the clip rail profile including the
        clip points and the rails. This can be cut from the frame or
        modified to fit the shape of the filament bracket
        -------
        arguments:
            - inset: an inset amount allowing tolerance in the printed parts
            - frame_depth: how deep in the frame to place the clip
        """
        x_intersection = self._config.frame_bracket_exterior_x_distance(
            frame_depth
        )
        with BuildPart() as rail_block:
            with BuildPart(
                Location((x_intersection, 0, frame_depth)), mode=Mode.ADD
            ) as railbox:
                Box(
                    self._config.bracket_depth * 2 - inset,
                    self._config.frame_clip_width - inset,
                    self._config.minimum_structural_thickness - inset,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )
                with BuildPart(railbox.faces().sort_by(Axis.Z)[-1]):
                    with GridLocations(
                        0, self._config.frame_clip_width - inset, 1, 2
                    ):
                        Box(
                            self._config.bracket_depth * 2 - inset,
                            self._config.frame_clip_rail_width - inset,
                            self._config.frame_clip_rail_width - inset,
                            rotation=(45, 0, 0),
                            align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        )
                Box(
                    self._config.bracket_depth * 2 - inset,
                    self._config.frame_clip_width - inset,
                    self._config.minimum_structural_thickness * 2
                    + abs(inset * 2),
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.INTERSECT,
                )
            with BuildPart(railbox.faces().sort_by(Axis.X)[0]) as rounded:
                Cylinder(
                    radius=(self._config.minimum_structural_thickness - inset)
                    / 2,
                    height=self._config.frame_clip_width - inset,
                    rotation=(90, 0, 0),
                )
            top_height = frame_depth + (
                (self._config.minimum_structural_thickness - inset) / 2
            )
            radial_inset = inset if inset > 0 else inset * 4
            with BuildPart(
                Location(
                    (
                        self._config.frame_bracket_exterior_x_distance(
                            top_height
                        )
                        - (
                            self._config.frame_click_sphere_radius
                            + self._config.minimum_thickness
                        ),
                        0,
                        top_height,
                    )
                )
            ):
                with GridLocations(
                    0,
                    self._config.frame_clip_width
                    - inset
                    - self._config.wall_thickness,
                    1,
                    2,
                ):
                    Cylinder(
                        radius=self._config.frame_click_sphere_radius
                        - radial_inset,
                        height=self._config.wall_thickness,
                        rotation=(90, 0, 0),
                    )
            with BuildPart(
                rounded.faces().filter_by(Axis.Y)[-1], mode=Mode.SUBTRACT
            ):
                Sphere(self._config.frame_click_sphere_radius + radial_inset)
                if inset > 0:
                    Cylinder(
                        radius=max(
                            self._config.frame_click_sphere_radius / 2 + inset,
                            0,
                        ),
                        height=self._config.minimum_structural_thickness,
                        rotation=(90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
            with BuildPart(
                rounded.faces().filter_by(Axis.Y)[0], mode=Mode.SUBTRACT
            ):
                Sphere(self._config.frame_click_sphere_radius + radial_inset)
                if inset > 0:
                    Cylinder(
                        radius=max(
                            self._config.frame_click_sphere_radius / 2 + inset,
                            0,
                        ),
                        height=self._config.minimum_structural_thickness,
                        rotation=(90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MAX),
                    )
        return rail_block.part

    def bracket_clip(
        self, inset=0, frame_depth=_config.frame_clip_point.y
    ) -> Part:
        """
        the part for locking the frame bracket into the frame
        -------
        arguments:
            - inset: an inset amount allowing tolerance in the printed parts
            - frame_depth: how deep in the frame to place the clip
        """
        with BuildPart(mode=Mode.PRIVATE) as base_cylinder:
            Cylinder(
                radius=self._config.frame_bracket_exterior_radius,
                height=self._config.frame_clip_width - inset * 2,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                rotation=(90, 0, 0),
            )
            fillet(
                base_cylinder.edges().filter_by(GeomType.CIRCLE),
                self._config.fillet_radius,
            )
        with BuildPart(mode=Mode.PRIVATE) as inset_cylinder:
            Cylinder(
                radius=self._config.frame_bracket_exterior_radius
                - self._config.wall_thickness
                + inset,
                height=self._config.frame_clip_width
                - self._config.wall_thickness * 2
                + inset * 2,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                rotation=(90, 0, 0),
            )
            fillet(
                inset_cylinder.edges().filter_by(GeomType.CIRCLE),
                self._config.fillet_radius,
            )
        with BuildPart() as clip:
            add(
                self.bracket_clip_rail_block(
                    inset=inset, frame_depth=frame_depth
                )
            )
            add(base_cylinder, mode=Mode.INTERSECT)
            add(inset_cylinder, mode=Mode.SUBTRACT)

            extrude(
                clip.faces().sort_by(Axis.X)[-1],
                amount=self._config.bracket_depth,
                dir=(1, 0, 0),
            )
            edge_set = (
                clip.faces()
                .sort_by(Axis.X)[-1]
                .edges()
                .filter_by(GeomType.CIRCLE)
            )
            fillet(
                edge_set, clip.part.max_fillet(edge_set, max_iterations=100)
            )
            with BuildPart(
                Location(
                    (
                        self._config.frame_clip_point.x
                        + self._config.bracket_depth / 2,
                        0,
                        frame_depth,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                Cylinder(
                    radius=(
                        self._config.frame_clip_width
                        - self._config.fillet_radius * 2
                    )
                    / 3.5,
                    height=self._config.minimum_structural_thickness + inset,
                    align=(Align.MIN, Align.CENTER, Align.CENTER),
                )
        part = clip.part
        part.label = "Bracket Clip"
        return part

    def bottom_bracket_block(self) -> Part:
        """
        the basic block shape of the bottom bracket
        """
        with BuildPart() as arch:
            with BuildSketch():
                with BuildLine():
                    arc = CenterArc(
                        (0, 0),
                        self._config.frame_bracket_exterior_radius,
                        start_angle=0,
                        arc_size=180,
                    )
                    Line(arc @ 0, arc @ 1)
                make_face()
            extrude(amount=self._config.bracket_depth)
            fillet(arch.edges(), self._config.fillet_radius)
            with BuildPart(
                Location((self._config.wheel_radius, 0, 0)), mode=Mode.SUBTRACT
            ):
                add(
                    self._filamentchannels.curved_filament_path_solid(
                        top_exit_fillet=True
                    )
                )
            with BuildPart(
                Location((-self._config.wheel_radius, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                add(self._filamentchannels.straight_filament_path_solid())
            with BuildPart(Location((self._config.wheel_radius, 0, 0))):
                add(
                    self._filamentchannels.curved_filament_path_solid(
                        top_exit_fillet=True
                    )
                )
            with BuildPart(Location((-self._config.wheel_radius, 0, 0))):
                add(self._filamentchannels.straight_filament_path_solid())
            if LockStyle.CLIP in self._config.frame_lock_style:
                with BuildPart(
                    Location(
                        (0, 0, self._config.bracket_depth / 2), (-90, 0, 0)
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(self.bracket_clip(inset=-self._config.tolerance / 2))
            if LockStyle.PIN in self._config.frame_lock_style:
                with BuildPart(
                    Location(
                        (
                            self._config.wheel_radius
                            + self._config.bracket_depth / 2,
                            self._config.bracket_depth
                            + self._config.minimum_structural_thickness / 2,
                            0,
                        ),
                        (-90, 0, 0),
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        self._lockpin.lock_pin(
                            inset=-self._config.frame_lock_pin_tolerance / 2,
                            tie_loop=False,
                        )
                    )

        part = arch.part
        part.label = "solid bracket block"
        return part

    def _pin_channel(self) -> Part:
        """
        the channel to lock the filament bracket into the back of the top frame
        """
        base_unit = self._config.wall_thickness + self._config.tolerance
        with BuildPart() as channel:
            add(
                rounded_cylinder(
                    radius=base_unit,
                    height=self._config.bracket_depth + self._config.tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            )
            with BuildPart(
                Location((0, 0, -self._config.bracket_depth / 2))
            ) as guide:
                Cylinder(
                    radius=self._config.bracket_depth,
                    height=base_unit * 2,
                    rotation=(0, 90, 0),
                )
                fillet(guide.edges(), base_unit - self._config.tolerance / 2)
        return channel.part

    def bottom_bracket(self, draft: bool = False) -> Part:
        """
        returns the bottom (main) portion of the filament
        """
        with BuildPart() as constructed_bracket:
            add(self.bottom_bracket_block())

            with BuildPart(mode=Mode.SUBTRACT):
                with BuildPart(Location((self._config.wheel_radius, 0, 0))):
                    add(self._filamentchannels.curved_filament_path_cut())
                with BuildPart(Location((-self._config.wheel_radius, 0, 0))):
                    add(self._filamentchannels.straight_filament_path_cut())
                add(
                    self._top_cut_template(self._config.tolerance)
                    .mirror()
                    .move(Location((0, 0, self._config.bracket_depth)))
                )
                Cylinder(
                    radius=self._config.wheel_radius
                    + self._config.wheel_radial_tolerance,
                    height=self._config.bracket_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                with Locations(
                    Location(
                        (
                            self._config.frame_click_sphere_point.x,
                            self._config.frame_click_sphere_point.y,
                            self._config.bracket_depth,
                        )
                    ),
                    Location(
                        (
                            self._config.frame_click_sphere_point.x,
                            self._config.frame_click_sphere_point.y,
                            0,
                        )
                    ),
                ):
                    Sphere(self._config.frame_click_sphere_radius)
            add(self._wheel_guide())
            add(self._spoke_assembly())
            with BuildPart(
                Location(
                    (
                        -self._config.frame_bracket_exterior_radius,
                        self._config.bracket_depth,
                        self._config.bracket_depth / 2,
                    ),
                    (0, 90, 0),
                ),
                mode=Mode.SUBTRACT,
            ):
                with GridLocations(self._config.bracket_depth, 0, 2, 1):
                    add(self._pin_channel())
            if LockStyle.CLIP in self._config.frame_lock_style:
                with BuildPart(
                    Location(
                        (0, 0, self._config.bracket_depth / 2), (-90, 0, 0)
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(self.bracket_clip(inset=-self._config.tolerance / 2))
            if LockStyle.PIN in self._config.frame_lock_style:
                with BuildPart(
                    Location(
                        (
                            self._config.wheel_radius
                            + self._config.bracket_depth / 2,
                            self._config.bracket_depth
                            + self._config.minimum_structural_thickness / 2,
                            0,
                        ),
                        (-90, 0, 0),
                    ),
                    mode=Mode.SUBTRACT,
                ):
                    add(
                        self._lockpin.lock_pin(
                            inset=-self._config.frame_lock_pin_tolerance / 2,
                            tie_loop=False,
                        )
                    )
            if not draft and self._config.default_connector.threaded:
                add(
                    self._filamentchannels.straight_filament_connector_threads().move(
                        Location((-self._config.wheel_radius, 0, 0))
                    )
                )
                add(
                    self._filamentchannels.curved_filament_connector_threads().move(
                        Location((self._config.wheel_radius, 0, 0))
                    )
                )
        part = constructed_bracket.part
        part.label = "bottom bracket"
        return part

    def top_bracket(self, tolerance: float = 0) -> Part:
        """
        returns the top slide-in part for the filament bracket
        """
        with BuildPart() as frame:
            add(self.bottom_bracket(draft=True).mirror(Plane.YZ))
            with BuildPart(mode=Mode.INTERSECT):
                add(self._top_cut_template(tolerance))
                Cylinder(
                    radius=self._config.bearing_shelf_radius,
                    height=self._config.bracket_depth / 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        part = frame.part
        part.label = "top bracket"
        return part

    def load_config(self, configuration_path: str):
        """
        loads the configuration file
         -------
        arguments:
        configuration_path: the path to the configuration file
        """
        self._config.load_config(configuration_path)
        self._filamentchannels.load_config(configuration_path)
        self._lockpin.load_config(configuration_path)

    def __init__(self, configuration_path: str):
        """
        initializes the Partomatic filament bracket
        -------
        arguments:
        configuration_file: the path to the configuration file,
        set to None to use the default configuration
        """
        super(Partomatic, self).__init__()
        if configuration_path is not None:
            self.load_config(configuration_path)

    def compile(self):
        """
        Builds the relevant parts for the filament bracket
        """
        self.bottom = self.bottom_bracket(draft=False)
        self.top = self.top_bracket()
        if LockStyle.CLIP in self._config.frame_lock_style:
            self.bracketclip = self.bracket_clip(
                inset=self._config.tolerance / 2
            )

    def display(self):
        """
        Shows the filament wheel in OCP CAD Viewer
        """
        show(
            self.bottom.move(
                Location((self._config.bracket_width / 2 + 5, 0, 0))
            ),
            self.top.move(
                Location((-self._config.bracket_width / 2 + 5, 0, 0))
            ),
            (
                self.bracketclip.rotate(Axis.X, -90).move(
                    Location(
                        (
                            self._config.bracket_width / 2
                            + 5
                            + self._config.bracket_depth / 2,
                            0,
                            self._config.bracket_depth / 2,
                        )
                    )
                )
                if LockStyle.CLIP in self._config.frame_lock_style
                else None
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        """
        Generates the filament wheel STLs in the configured
        folder
        """
        if self._config.stl_folder == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        if LockStyle.CLIP in self._config.frame_lock_style:
            export_stl(
                self.bracketclip,
                str(output_directory / "filament-bracket-clip.stl"),
            )
        export_stl(
            self.bottom, str(output_directory / "filament-bracket-bottom.stl")
        )
        export_stl(
            self.top, str(output_directory / "filament-bracket-top.stl")
        )

    def render_2d(self):
        pass


if __name__ == "__main__":
    bracket = FilamentBracket(
        Path(__file__).parent / "../build-configs/debug.conf"
    )
    bracket.compile()
    bracket.display()
    bracket.export_stls()
