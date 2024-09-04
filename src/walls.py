"""
Generates the part for the chamber walls of the filament bank
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    GridLocations,
    Location,
    Mode,
    Part,
    Plane,
    Rectangle,
    Sphere,
    add,
    export_stl,
    extrude,
    fillet,
    loft,
)
from ocp_vscode import Camera, show
from partomatic import Partomatic
from pathlib import Path
from bank_config import BankConfig
from basic_shapes import sidewall_shape
from hexwall import HexWall

class Walls(Partomatic):
    _config = BankConfig('../build-configs/default.conf')

    gwall:Part
    sidewall: Part
    reinforcedsidewall:Part


    def wall_channel(self, length: float) -> Part:
        """
        creates a channel with tapered sides and
        snap-click points for locking in side walls
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
                Rectangle(self._config.wall_thickness + self._config.tolerance * 2, length)
            loft()
            with BuildPart(
                Plane.XY.offset(self._config.wall_thickness), mode=Mode.SUBTRACT
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
                    Sphere(self._config.frame_click_sphere_radius * 0.75)
        part = channel.part
        part.label = "wall channel guide"
        return part


    def straight_wall_tongue(self) -> Part:
        """
        creates a tongue for locking in wall parts,
        companion to straight_wall_groove
        """
        with BuildPart() as tongue:
            Box(
                self._config.wall_thickness,
                self._config.top_frame_interior_width - self._config.tolerance * 2,
                self._config.frame_tongue_depth - self._config.wall_thickness / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            extrude(
                tongue.faces().sort_by(Axis.Z)[-1],
                amount=self._config.wall_thickness / 2,
                taper=44,
            )
            with BuildPart(tongue.faces().sort_by(Axis.X)[-1], mode=Mode.ADD):
                with GridLocations(0, self._config.top_frame_interior_width-self._config.bracket_depth, 1, 2):
                    Sphere(radius=self._config.frame_click_sphere_radius * 0.75)
            with BuildPart(tongue.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT):
                with GridLocations(0, self._config.top_frame_interior_width-self._config.bracket_depth, 1, 2):
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
                with BuildPart(Location((0, 0, self._config.wall_thickness * 0.75))):
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


    def guide_side(self, length: float) -> Part:
        """
        defines the outer sides of the sidewall with appropriate structural
        reinforcements
        """
        with BuildPart() as side:
            Box(
                self._config.minimum_structural_thickness - self._config.tolerance,
                length,
                self._config.wall_thickness * 3,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        return side.part


    def side_wall_divots(self, length: float = _config.sidewall_straight_depth):
        """
        positions the holes that get punched along a sidewall to connect to
        the front and back walls
        arguments:
        length: the length of the sidewall
        """
        with BuildPart() as divots:
            with BuildPart(Location((0, 0, self._config.wall_thickness))):
                with GridLocations(
                    self._config.sidewall_width - self._config.wall_thickness * 2,
                    length / 2,
                    2,
                    2,
                ):
                    Sphere(radius=self._config.frame_click_sphere_radius)
            with GridLocations(
                self._config.sidewall_width - self._config.wall_thickness * 2, length / 2, 2, 2
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
        """
        with BuildPart() as wall:
            with BuildSketch(Plane.XY):
                add(sidewall_shape(inset=self._config.wall_thickness / 2, length=length))
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness / 2)):
                add(sidewall_shape(length=length))
            with BuildSketch(Plane.XY.offset(self._config.wall_thickness)):
                add(sidewall_shape(inset=self._config.wall_thickness / 2, length=length))
            loft(ruled=True)
            if reinforce:
                with BuildPart():
                    with BuildSketch():
                        add(
                            sidewall_shape(
                                inset=self._config.wall_thickness / 2,
                                length=length,
                                straignt_inset=self._config.minimum_structural_thickness
                                + self._config.tolerance,
                            )
                        )
                        add(
                            sidewall_shape(
                                inset=self._config.wall_thickness / 2
                                + self._config.minimum_structural_thickness,
                                length=length,
                                straignt_inset=self._config.minimum_structural_thickness,
                            ),
                            mode=Mode.SUBTRACT,
                        )
                    extrude(
                        amount=self._config.minimum_structural_thickness
                        + self._config.wall_thickness
                    )
            if not self._config.solid_walls:
                multiplier = 1 if reinforce else 0
                with BuildPart(mode=Mode.SUBTRACT):
                    with BuildSketch():
                        add(
                            sidewall_shape(
                                inset=self._config.wall_thickness / 2
                                + self._config.minimum_structural_thickness,
                                length=length,
                                straignt_inset=self._config.minimum_structural_thickness
                                * multiplier,
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
                add(self.side_wall_divots(self._config.sidewall_straight_depth))

        return wall.part


    def guide_wall(self, length: float, flipped=False) -> Part:
        """
        builds a wall with guides for each sidewall
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
                        base_length - self._config.minimum_structural_thickness * 2,
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
                add(self.straight_wall_tongue())
            with BuildPart(wall.faces().sort_by(Axis.Y)[0]):
                add(self.straight_wall_tongue())
            with GridLocations(
                self._config.frame_bracket_spacing, 0, self._config.filament_count + 1, 1
            ):
                add(self.wall_channel(base_length))
            with GridLocations(
                self._config.frame_exterior_width
                - self._config.minimum_structural_thickness
                + self._config.tolerance,
                0,
                2,
                1,
            ):
                add(self.guide_side(base_length))
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


    def load_config(self, configuration_path: str):
        self._config.load_config(configuration_path)

    def __init__(self, configuration_file:str='../build-configs/default.conf'):
        super(Partomatic, self).__init__()
        self.load_config(configuration_file)

    def compile(self):
        self.gwall = self.guide_wall(self._config.sidewall_straight_depth)
        self.sidewall = self.side_wall(length=self._config.sidewall_section_depth)
        self.reinforcedsidewall = self.side_wall(
            length=self._config.sidewall_section_depth, reinforce=True
        )

    def display(self):
        show(
            self.gwall.move(Location((0, -self._config.sidewall_straight_depth / 2, 0))),
            self.sidewall.move(
                Location(
                    (
                        -self._config.frame_exterior_width / 2
                        - self._config.sidewall_width / 2
                        -1,
                        0,
                        0,
                    )
                )
            ),
            self.reinforcedsidewall.move(
                Location(
                    (
                        self._config.frame_exterior_width / 2
                        + self._config.sidewall_width / 2
                        + 1,
                        0,
                        0,
                    )
                )
            ),
            reset_camera=Camera.KEEP,
        )

    def export_stls(self):
        output_directory = Path(__file__).parent / self._config.stl_folder
        output_directory.mkdir(parents=True, exist_ok=True)
        export_stl(self.sidewall, str(output_directory / "wall-side.stl"))
        export_stl(self.reinforcedsidewall, str(output_directory / "wall-side-reinforced.stl"))
        export_stl(self.gwall, str(output_directory / "wall-guide.stl"))

    def render_2d(self):
        pass

if __name__ == "__main__":
    walls = Walls(Path(__file__).parent / "../build-configs/default.conf")
    walls.compile()
    walls.display()
    walls.export_stls()
