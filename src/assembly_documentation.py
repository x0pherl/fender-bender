from dataclasses import asdict
from pathlib import Path
from bender_config import BenderConfig
from filament_bracket import FilamentBracket
from filament_wheel import FilamentWheel
from sidewall import Sidewall
from sidewall_config import SidewallConfig
from guidewall import Guidewall
from guidewall_config import GuidewallConfig

from build123d import (
    Part,
    Compound,
    Location,
    Axis,
    BuildPart,
    Align,
    Mode,
    Cylinder,
    Cone,
)
from ocp_vscode import Camera, show, save_screenshot


class wall_assembly:

    _config: BenderConfig

    def _guide_wall_assembly(self) -> Part:
        """
        Arranges the guide walls for display
        """
        bottom_guide = Guidewall(
            self._config.guidewall_config
        ).build_guidewall()
        top_guide = bottom_guide.rotate(Axis.Y, 180).moved(
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
            swall = (
                Sidewall(self._config.sidewall_config)
                ._sidewall()
                .rotate(Axis.Y, 90)
                .moved(
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
            )
            swall.label = f"internal side wall {i+1}"
            swall.parent = wallspart

        wallspart.color = "#8c93e9"
        return wallspart

    def _reinforced_side_wall_assembly(self) -> Part:
        """
        Arranges the reinforced side walls for display
        """
        right_side = (
            Sidewall(self._config.sidewall_config)
            ._sidewall(reinforced=True)
            .rotate(Axis.Y, 90)
            .moved(
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
        )
        left_side = (
            Sidewall(self._config.sidewall_config)
            ._sidewall(reinforced=True)
            .rotate(Axis.Y, -90)
            .moved(
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
        )
        left_side.label = "left reinforced side wall"
        right_side.label = "right reinforced side wall"
        outerwalls = Compound(
            label="Reinforced Side Walls", children=[left_side, right_side]
        )
        outerwalls.color = "#009eb0"
        return outerwalls

    def step_one_assembly(self) -> Part:
        """creates an assembly for documentation step one"""
        bottom_guide = Guidewall(
            self._config.guidewall_config
        ).build_guidewall()
        bottom_guide.label = "bottom guide wall"
        bottom_guide.color = "#168529"
        swall = (
            Sidewall(self._config.sidewall_config)
            ._sidewall()
            .rotate(Axis.Y, 90)
            .moved(
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
        )
        swall.label = f"internal side wall"
        swall.color = "#8c93e9"

        return Compound(
            label="Step One Assembly", children=[bottom_guide, swall]
        )

    def step_two_assembly(self) -> Part:
        """creates an assembly for documentation step two"""
        wall_assembly = self.step_one_assembly()
        wall_assembly.label = "Step Two Assembly"
        right_side = (
            Sidewall(self._config.sidewall_config)
            ._sidewall(reinforced=True)
            .rotate(Axis.Y, 90)
            .moved(
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
        )

        right_side.color = "#009eb0"
        right_side.parent = wall_assembly
        return wall_assembly

    def complete_assembly(self) -> Part:
        complete_assembly = Compound(
            label="Wall Assembly",
            children=[
                self._guide_wall_assembly(),
                self._side_wall_assembly(),
                self._reinforced_side_wall_assembly(),
            ],
        )
        return complete_assembly

    def __init__(self, config: BenderConfig = None):
        if config is None:
            self._config = BenderConfig()
        else:
            self._config = config


class BracketAssembly:
    bender_config: BenderConfig
    _filament_bracket: FilamentBracket = FilamentBracket()

    def _step_one_assembly(self) -> Compound:
        """"""
        bottom = self._filament_bracket.bottom_bracket()
        bottom.label = "bottom bracket"
        bottom.color = "#168529"
        with BuildPart() as bearing:
            Cylinder(
                radius=self._config.wheel.bearing.radius,
                height=self._config.wheel.bearing.depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=self._config.wheel.bearing.inner_radius,
                height=self._config.wheel.bearing.depth,
                mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        bearing = bearing.part.moved(
            Location(
                (
                    0,
                    0,
                    self._config.bearing_shelf_height,
                )
            )
        )
        bearing.label = "bearing"
        bearing.color = "#C0C0C0"

        wheel = (
            FilamentWheel(self._config.wheel)
            .filament_wheel()
            .moved(
                Location(
                    (
                        0,
                        0,
                        self._config.bearing_shelf_height,
                    )
                )
            )
        )
        wheel.label = "filament wheel"
        wheel.color = "#8c93e9"

        bracket_assembly = Compound(
            label="Filament Bracket Assembly",
            children=[
                bottom.moved(Location((0, 0, 0))),
                wheel,
                bearing,
            ],
        )
        return bracket_assembly

    def _step_two_assembly(self) -> Compound:
        """"""
        bracket_assembly = self._step_one_assembly()
        top = (
            self._filament_bracket.top_bracket()
            .rotate(Axis.Y, 180)
            .move(
                Location(
                    (
                        0,
                        -self._config.bracket_depth,
                        self._config.bracket_depth,
                    )
                )
            )
        )
        top.label = "top bracket"
        top.color = "#009eb0"
        top.parent = bracket_assembly
        with BuildPart() as arrow:
            Cylinder(
                radius=self._config.wheel.bearing.inner_radius,
                height=self._config.wheel.radius / 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(arrow.faces().sort_by(Axis.Z)[-1]):
                Cone(
                    bottom_radius=self._config.wheel.bearing.inner_diameter,
                    top_radius=0,
                    height=self._config.wheel.bearing.inner_diameter * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        up_arrow = arrow.part.move(
            Location(
                (
                    0,
                    -self._config.bracket_depth,
                    self._config.bracket_depth * 1.5,
                )
            )
        )
        up_arrow.color = "#ebd591"
        up_arrow.label = "up arrow"
        up_arrow.parent = bracket_assembly
        slide_arrow = arrow.part.rotate(Axis.X, -90).move(
            Location((0, self._config.wheel.radius / 2, 0))
        )
        slide_arrow.color = "#ebd591"
        slide_arrow.label = "slide arrow"
        slide_arrow.parent = bracket_assembly
        return bracket_assembly

    def complete_assembly(self) -> Compound:
        """"""
        bracket_assembly = self._step_one_assembly()
        top = (
            self._filament_bracket.top_bracket()
            .rotate(Axis.Y, 180)
            .move(Location((0, 0, self._config.bracket_depth)))
        )
        top.label = "top bracket"
        top.color = "#009eb0"
        top.parent = bracket_assembly
        return bracket_assembly

    def __init__(self, config: BenderConfig = None):
        if config is None:
            self._config = BenderConfig()
        else:
            self._config = config
        self._filament_bracket = FilamentBracket(
            self._config.filament_bracket_config(0)
        )
        self._filament_bracket.compile()


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/reference.conf"
    bender_config = BenderConfig(config_path)
    output_directory = Path(__file__).parent / "../docs/assets"
    output_directory.mkdir(parents=True, exist_ok=True)
    walls = wall_assembly(bender_config)
    show(walls.step_one_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-001-internal-walls.png")
    )

    show(walls.step_two_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-002-external-walls.png")
    )

    show(walls.complete_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-003-wall-assembly.png")
    )
    brackets = BracketAssembly(bender_config)
    show(brackets._step_one_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-001-wheel-bearing.png")
    )
    show(brackets._step_two_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-002-external-walls.png")
    )
    show(brackets.complete_assembly(), reset_camera=Camera.RESET)
    save_screenshot(
        filename=str(Path(output_directory) / "step-003-bracket-complete.png")
    )
