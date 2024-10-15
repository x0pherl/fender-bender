"""
Generates the part for the chamber walls of the filament bank
"""

from enum import Enum, auto
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    Cylinder,
    GridLocations,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Rectangle,
    Sketch,
    Sphere,
    add,
    export_stl,
    extrude,
    fillet,
    loft,
    offset,
)
from ocp_vscode import Camera, show, save_screenshot

from hexwall import HexWall
from partomatic import Partomatic
from bender_config import BenderConfig
from walls_config import SidewallShape, WallsConfig


class Walls(Partomatic):
    """partomatic for the chamber walls of the filament bank"""

    _config = BenderConfig()
    _sidewall_shape: SidewallShape

    gwall: Part
    sidewall: Part
    reinforcedsidewall: Part
    complete_assembly: Part

    def _sidewall_shape(
        self,
        shape: SidewallShape = SidewallShape.BASE,
    ) -> Sketch:
        """
        the 2d shape of the sidewall at the defined length
        """
        straight_width = (
            self._config.sidewall_width - self._config.wall_thickness
        )
        curve_radius = (
            self._config.wheel.radius - self._config.wall_thickness / 2
        )
        wall_length = (
            self._config.sidewall_section_depth
            - self._config.frame_base_depth
            - curve_radius
            - self._config.wall_thickness * 1.5
        )
        straight_offset = -self._config.wall_thickness / 2

        if shape == SidewallShape.REINFORCEMENT:
            straight_width -= self._config.minimum_structural_thickness * 2
        elif shape == SidewallShape.POINT:
            straight_width += self._config.wall_thickness
            curve_radius += self._config.wall_thickness * 0.75
            wall_length += self._config.wall_thickness * 1.25
            straight_offset += self._config.wall_thickness * 0.75

        with BuildSketch(mode=Mode.PRIVATE) as wall:
            with Locations(Location((0, straight_offset))):
                Rectangle(
                    straight_width,
                    wall_length,
                    align=(Align.CENTER, Align.MAX),
                )
            with BuildSketch():
                with Locations(Location((0, self._config.frame_base_depth))):
                    Circle(radius=curve_radius)
                    Rectangle(
                        curve_radius * 2,
                        curve_radius * 2,
                        align=(Align.CENTER, Align.MAX),
                        mode=Mode.SUBTRACT,
                    )
                    Rectangle(
                        curve_radius * 2,
                        self._config.frame_base_depth - straight_offset,
                        align=(Align.CENTER, Align.MAX),
                    )
        return wall.sketch

    def _wall_channel(self, length: float) -> Part:
        """
            creates a channel with tapered sides and
            snap-click points for locking in side walls
        -------
            arguments:
            length: the appropriate length of the channel
        """
        with BuildPart() as channel:
            with BuildPart():
                Box(
                    self._config.wall_thickness * 3,
                    length,
                    self._config.wall_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                Rectangle(self._config.wall_thickness * 3, length)
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness * 3)):
                Rectangle(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    length,
                )
            loft()
            with BuildPart(
                Plane.XY.offset(self._config.wall_thickness),
                mode=Mode.SUBTRACT,
            ):
                Box(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    length,
                    self._config.wall_thickness * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with BuildPart(Plane.XY.offset(self._config.wall_thickness * 2)):
                with GridLocations(
                    self._config.wall_thickness + self._config.tolerance * 2,
                    (length + self._config.wall_thickness / 2) / 2,
                    2,
                    2,
                ):
                    Sphere(self._config.frame_click_sphere_radius * 0.675)
        part = channel.part
        part.label = "wall channel guide"
        return part

    def _straight_wall_tongue(self) -> Part:
        """
        creates a tongue for locking in wall parts,
        companion to straight_wall_groove
        """
        with BuildPart() as tongue:
            Box(
                self._config.wall_thickness,
                self._config.top_frame_interior_width
                - self._config.tolerance * 2,
                self._config.frame_tongue_depth
                - self._config.wall_thickness / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            extrude(
                tongue.faces().sort_by(Axis.Z)[-1],
                amount=self._config.wall_thickness / 2,
                taper=44,
            )
            with BuildPart(tongue.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
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
            with BuildPart(
                tongue.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT
            ):
                with GridLocations(
                    0,
                    self._config.top_frame_interior_width
                    - self._config.bracket_depth,
                    1,
                    2,
                ):
                    Sphere(radius=self._config.frame_click_sphere_radius)

            # this center cut guides the alignment when assembling,
            # and provides additional stability to the hold
            with BuildPart(mode=Mode.SUBTRACT):
                Box(
                    self._config.wall_thickness,
                    self._config.wall_thickness / 2 + self._config.tolerance,
                    self._config.frame_tongue_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                with BuildPart(
                    Location((0, 0, self._config.wall_thickness * 0.75))
                ):
                    Sphere(radius=self._config.wall_thickness * 0.75)
                    Cylinder(
                        radius=self._config.wall_thickness * 0.6,
                        height=self._config.wall_thickness,
                        rotation=(0, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )

        part = tongue.part
        part.label = "tongue"
        return part

    def _guide_side(self, length: float) -> Part:
        """
        defines the outer sides of the sidewall with appropriate structural
        reinforcements
        -------
            arguments:
            length: the appropriate length of the guide
        """
        with BuildPart() as side:
            Box(
                self._config.minimum_structural_thickness
                - self._config.tolerance,
                length,
                self._config.wall_thickness * 3,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        return side.part

    def _side_wall_divots(
        self, length: float = _config.sidewall_straight_depth
    ):
        """
        positions the holes that get punched along a sidewall to connect to
        the front and back walls
        -------
        arguments:
        length: the length of the sidewall controls the spacing of the divots
        """
        with BuildPart() as divots:
            with BuildPart(Location((0, 0, self._config.wall_thickness))):
                with GridLocations(
                    self._config.sidewall_width
                    - self._config.wall_thickness * 2,
                    length / 2,
                    2,
                    2,
                ):
                    Sphere(radius=self._config.frame_click_sphere_radius)
            with GridLocations(
                self._config.sidewall_width - self._config.wall_thickness * 2,
                length / 2,
                2,
                2,
            ):
                Sphere(radius=self._config.frame_click_sphere_radius)
        return divots.part

    def side_wall(
        self,
        length: float = _config.sidewall_section_depth,
        reinforce=False,
        flipped=False,
    ) -> Part:
        """
        returns a sidewall
        -------
        arguments:
        length: the appropriate length of the sidewall
        reinforce: whether to add structural reinforcements
        flipped: mirrors the sidewall on the xy plane
            (this can be helpful for reinforced walls,
            especially if there is a patterned wall)
        """
        with BuildPart() as wall:
            with BuildSketch(Plane.XY):
                add(self._sidewall_shape(SidewallShape.BASE))
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness / 2)):
                add(self._sidewall_shape(SidewallShape.POINT))
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                add(self._sidewall_shape(SidewallShape.BASE))
            loft(ruled=True)
            if reinforce:
                with BuildPart():
                    with BuildSketch():
                        add(self._sidewall_shape(SidewallShape.REINFORCEMENT))
                        with BuildSketch(mode=Mode.SUBTRACT):
                            add(
                                offset(
                                    self._sidewall_shape(
                                        SidewallShape.REINFORCEMENT
                                    ),
                                    -self._config.minimum_structural_thickness,
                                )
                            )
                    extrude(
                        amount=self._config.minimum_structural_thickness
                        + self._config.wall_thickness
                    )
            if not self._config.solid_walls:
                shape = (
                    SidewallShape.REINFORCEMENT
                    if reinforce
                    else SidewallShape.BASE
                )
                with BuildPart(mode=Mode.SUBTRACT):
                    with BuildSketch() as sk:
                        add(
                            offset(
                                self._sidewall_shape(shape),
                                -self._config.minimum_structural_thickness,
                            )
                        )
                    extrude(amount=self._config.wall_thickness)
                    with BuildPart(mode=Mode.INTERSECT):
                        hw = HexWall(
                            width=length * 2,
                            length=self._config.sidewall_width,
                            height=self._config.wall_thickness,
                            apothem=self._config.wall_window_apothem,
                            wall_thickness=self._config.wall_window_bar_thickness,
                            inverse=True,
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                        )
                        if flipped:
                            hw = hw.mirror(Plane.YZ)
                        add(hw)
            with BuildPart(
                Location((0, -self._config.sidewall_straight_depth / 2, 0)),
                mode=Mode.SUBTRACT,
            ):
                add(
                    self._side_wall_divots(
                        self._config.sidewall_straight_depth
                    )
                )

        return wall.part

    def guide_wall(
        self, length: float = _config.sidewall_straight_depth, flipped=False
    ) -> Part:
        """
        builds a wall with guides for each sidewall
        -------
        arguments:
        length: the appropriate length of the channel
        flipped: mirrors the sidewall on the xy plane
            (this can be helpful for reinforced walls,
            especially if there is a patterned wall)
        """
        base_length = length - self._config.wall_thickness / 2
        with BuildPart() as wall:
            with BuildPart():
                Box(
                    self._config.frame_exterior_width,
                    base_length,
                    self._config.wall_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            if self._config.solid_walls is False:
                with BuildPart(mode=Mode.SUBTRACT):
                    hw = HexWall(
                        self._config.frame_exterior_width
                        - self._config.minimum_structural_thickness * 2,
                        base_length
                        - self._config.minimum_structural_thickness * 2,
                        self._config.wall_thickness,
                        apothem=self._config.wall_window_apothem,
                        wall_thickness=self._config.wall_window_bar_thickness,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        inverse=True,
                    )
                    if flipped:
                        hw = hw.mirror(Plane.YZ)
                    add(hw)
            with BuildPart(wall.faces().sort_by(Axis.Y)[-1]):
                add(self._straight_wall_tongue())
            with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
                add(self._straight_wall_tongue())
            with GridLocations(
                self._config.frame_bracket_spacing,
                0,
                self._config.filament_count + 1,
                1,
            ):
                add(self._wall_channel(base_length))
            with GridLocations(
                self._config.frame_exterior_width
                - self._config.minimum_structural_thickness
                + self._config.tolerance,
                0,
                2,
                1,
            ):
                add(self._guide_side(base_length))
            fillet(
                (
                    wall.faces().sort_by(Axis.X)[0]
                    + wall.faces().sort_by(Axis.X)[-1]
                )
                .edges()
                .filter_by(Axis.Y),
                self._config.wall_thickness / 4,
            )

        part = wall.part
        return part

    def _guide_wall_assembly(self) -> Part:
        """
        Arranges the guide walls for display
        """
        bottom_guide = self.gwall
        top_guide = self.gwall.rotate(Axis.Y, 180).moved(
            Location(
                (
                    0,
                    0,
                    self._config.sidewall_width
                    + self._config.wall_thickness * 2
                    + self._config.tolerance * 2,
                )
            )
        )
        bottom_guide.label = "bottom guide wall"
        top_guide.label = "top guide wall"
        guidespart = Compound(
            children=[bottom_guide, top_guide], label="Guide Walls"
        )
        guidespart.color = "#168529"
        return guidespart

    def _side_wall_assembly(self) -> Part:
        """
        Arranges the side walls for display
        """
        wallspart = Compound(children=[], label="Inernal Side Walls")
        for i in range(self._config.filament_count - 1):
            swall = self.sidewall.rotate(Axis.Y, 90).moved(
                Location(
                    (
                        -self._config.frame_bracket_spacing
                        * (self._config.filament_count)
                        / 2
                        + self._config.frame_bracket_spacing
                        - self._config.wall_thickness / 2
                        + (self._config.frame_bracket_spacing * i),
                        self._config.sidewall_straight_depth / 2,
                        self._config.sidewall_width / 2
                        + self._config.wall_thickness
                        + self._config.tolerance,
                    )
                )
            )
            swall.label = f"internal side wall {i+1}"
            swall.parent = wallspart

        wallspart.color = "#8c93e9"
        return wallspart

    def _reinforced_side_wall_assembly(self) -> Part:
        """
        Arranges the reinforced side walls for display
        """
        right_side = self.reinforcedsidewall.rotate(Axis.Y, 90).moved(
            Location(
                (
                    self._config.frame_exterior_width / 2
                    - self._config.minimum_structural_thickness
                    - self._config.wall_thickness,
                    self._config.sidewall_straight_depth / 2,
                    self._config.sidewall_width / 2
                    + self._config.wall_thickness
                    + self._config.tolerance,
                )
            )
        )
        left_side = self.reinforcedsidewall.rotate(Axis.Y, -90).moved(
            Location(
                (
                    -self._config.frame_exterior_width / 2
                    + self._config.minimum_structural_thickness
                    + self._config.wall_thickness,
                    self._config.sidewall_straight_depth / 2,
                    self._config.sidewall_width / 2
                    + self._config.wall_thickness
                    + self._config.tolerance,
                )
            )
        )
        left_side.label = "left reinforced side wall"
        right_side.label = "right reinforced side wall"
        outerwalls = Compound(
            label="Reinforced Side Walls", children=[left_side, right_side]
        )
        outerwalls.color = "#009eb0"
        return outerwalls

    def _step_one_assembly(self) -> Part:
        """creates an assembly for documentation step one"""
        bottom_guide = self.gwall
        bottom_guide.label = "bottom guide wall"
        bottom_guide.color = "#168529"
        swall = self.sidewall.rotate(Axis.Y, 90).moved(
            Location(
                (
                    -self._config.frame_bracket_spacing / 2
                    - self._config.wall_thickness / 2,
                    self._config.sidewall_straight_depth / 2,
                    self._config.sidewall_width / 2
                    + self._config.wall_thickness
                    + self._config.tolerance,
                )
            )
        )
        swall.label = f"internal side wall"
        swall.color = "#8c93e9"

        return Compound(
            label="Step One Assembly", children=[bottom_guide, swall]
        )

    def _step_two_assembly(self) -> Part:
        """creates an assembly for documentation step two"""
        wall_assembly = self._step_one_assembly()
        wall_assembly.label = "Step Two Assembly"
        right_side = self.reinforcedsidewall.rotate(Axis.Y, 90).moved(
            Location(
                (
                    self._config.frame_exterior_width / 2
                    - self._config.minimum_structural_thickness
                    - self._config.wall_thickness,
                    self._config.sidewall_straight_depth / 2,
                    self._config.sidewall_width / 2
                    + self._config.wall_thickness
                    + self._config.tolerance,
                )
            )
        )
        right_side.color = "#009eb0"
        right_side.parent = wall_assembly
        return wall_assembly

    def load_config(self, configuration_path: str = None):
        """
        loads the configuration file
        -------
        arguments:
        configuration_path: the path to the configuration file
        """
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file: str = None):
        """
        initializes the Partomatic walls
        -------
        arguments:
        configuration_file: the path to the configuration file,
        set to None to use the default configuration
        """
        super(Partomatic, self).__init__()
        if configuration_file is not None:
            self.load_config(configuration_file)

    def compile(self):
        """
        Builds the relevant parts for the walls
        """
        self.gwall = self.guide_wall(self._config.sidewall_straight_depth)
        self.sidewall = self.side_wall(
            length=self._config.sidewall_section_depth
        )
        self.reinforcedsidewall = self.side_wall(
            length=self._config.sidewall_section_depth, reinforce=True
        )
        self.complete_assembly = Compound(
            label="Wall Assembly",
            children=[
                self._guide_wall_assembly(),
                self._side_wall_assembly(),
                self._reinforced_side_wall_assembly(),
            ],
        )

    def display(self):
        """
        Shows the walls in OCP CAD Viewer
        """
        show(self.complete_assembly, reset_camera=Camera.KEEP)

    def export_stls(self):
        """
        Generates the wall STLs in the configured
        folder
        """
        if self._config.stl_folder.upper() == "NONE":
            return
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.sidewall, str(output_directory / "wall-side.stl"))
        export_stl(
            self.reinforcedsidewall,
            str(output_directory / "wall-side-reinforced.stl"),
        )
        export_stl(self.gwall, str(output_directory / "wall-guide.stl"))

    def render_2d(self, save_to_disk: bool = False):
        """
        renders docuemntation images to the renders folder
        """
        output_directory = Path(__file__).parent / "../docs/assets"
        output_directory.mkdir(parents=True, exist_ok=True)

        show(self.complete_assembly, reset_camera=Camera.RESET)
        if save_to_disk:
            save_screenshot(
                filename=str(
                    Path(output_directory) / "step-003-wall-assembly.png"
                )
            )
        show(self._step_one_assembly(), reset_camera=Camera.RESET)
        if save_to_disk:
            save_screenshot(
                filename=str(
                    Path(output_directory) / "step-001-internal-walls.png"
                )
            )
        show(self._step_two_assembly(), reset_camera=Camera.RESET)
        if save_to_disk:
            save_screenshot(
                filename=str(
                    Path(output_directory) / "step-002-external-walls.png"
                )
            )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    walls = Walls(config_path)
    walls.compile()
    walls._step_one_assembly()
    # walls.display()
    # walls.export_stls()
    # walls.render_2d(save_to_disk=False)
