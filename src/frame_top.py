"""
Generates the part for the frames connecting the walls and holding the
filament brackets in place
"""

from dataclasses import asdict
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    GridLocations,
    Location,
    Mode,
    Part,
    PolarLocations,
    Sphere,
    add,
    export_stl,
    fillet,
)
from ocp_vscode import Camera, show

from bender_config import BenderConfig
from basic_shapes import (
    rounded_cylinder,
    rail_block_template,
    distance_to_circle_edge,
)

from frame_config import FrameConfig, FrameStyle
from frame_common import core_cut, wallslots
from lock_pin import LockPin
from lock_pin_config import LockPinConfig
from partomatic import BuildablePart, Partomatic
from tongue_groove import groove_pair
from wall_hanger_cut_template import wall_hanger_cut_template


class TopFrame(Partomatic):
    """
    A Partomatic for the top frame
    """

    _config: FrameConfig = FrameConfig()

    def _lock_clip_cut(self) -> Part:
        """creates the cutout for the lock clip"""
        with BuildPart(
            Location(
                (
                    distance_to_circle_edge(
                        self._config.exterior_radius,
                        (0, self._config.base_depth),
                        0,
                    ),
                    0,
                    self._config.base_depth,
                )
            )
        ) as clip:
            add(
                rail_block_template(
                    width=self._config.bracket_depth
                    + self._config.wall_thickness * 0.6,
                    length=self._config.bracket_depth * 2,
                    depth=self._config.minimum_structural_thickness,
                    radius=self._config.click_fit_radius,
                    inset=-self._config.tolerance / 2,
                    rail_width=self._config.wall_thickness * 0.3,
                )
            )
        return clip.part

    def _sliderails(self) -> Part:
        with BuildPart(
            Location(
                (
                    -self._config.exterior_radius,
                    0,
                    self._config.bracket_depth,
                ),
                (0, 90, 0),
            )
        ) as rails:
            with PolarLocations(
                self._config.bracket_depth / 2 + self._config.tolerance,
                2,
                90,
            ):
                add(
                    rounded_cylinder(
                        radius=self._config.wall_thickness
                        - self._config.tolerance,
                        height=self._config.bracket_depth,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                )
        return rails.part

    def _click_spheres(self) -> Part:
        with BuildPart(
            Location(
                (
                    self._config.exterior_radius
                    - self._config.minimum_structural_thickness,
                    0,
                    self._config.fillet_radius + self._config.click_fit_radius,
                )
            )
        ) as spheres:
            with PolarLocations(
                self._config.bracket_depth / 2 + self._config.tolerance,
                2,
                90,
            ):
                Sphere(self._config.click_fit_radius * 0.75)
        return spheres.part

    def _bracket_cutblock(self) -> Part:
        """
        the block that needs to be cut for each filament bracket in the top frame
        """
        with BuildPart() as cutblock:
            with BuildPart(Location((0, 0, 0))):
                Cylinder(
                    radius=self._config.exterior_radius,
                    height=self._config.bracket_depth
                    + self._config.tolerance * 2,
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                    rotation=(90, 0, 0),
                )
            with BuildPart(
                Location((-self._config.exterior_radius / 2, 0, 0))
            ):
                Box(
                    self._config.exterior_radius,
                    self._config.bracket_depth + self._config.tolerance * 2,
                    self._config.exterior_radius + self._config.bracket_depth,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                    rotation=(0, -30, 0),
                )
            with BuildPart(
                Location(
                    (
                        -self._config.interior_radius
                        - self._config.bracket_depth / 2,
                        0,
                        0,
                    )
                )
            ):
                Box(
                    self._config.exterior_diameter,
                    self._config.bracket_depth + self._config.tolerance * 2,
                    self._config.bracket_width,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                )
            fillet(cutblock.edges(), self._config.fillet_radius)
            with BuildPart() as narrowcut:
                Box(
                    self._config.interior_length,
                    self._config.bracket_depth
                    - self._config.fillet_radius
                    + self._config.tolerance * 2,
                    self._config.base_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )
                fillet(
                    narrowcut.edges().filter_by(Axis.Z),
                    self._config.fillet_radius,
                )
            widecut_offset = (
                self._config.interior_length - self._config.interior_diameter
            ) / 2 - self._config.tube_radius
            with BuildPart(Location((widecut_offset / 2, 0, 0))) as widecut:
                Box(
                    self._config.interior_length - widecut_offset,
                    self._config.bracket_depth + self._config.tolerance * 2,
                    self._config.base_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )
                fillet(
                    widecut.edges().filter_by(Axis.Z),
                    self._config.fillet_radius,
                )
            if self._config.include_lock_clip:
                add(self._lock_clip_cut())
            add(self._click_spheres(), mode=Mode.SUBTRACT)
            add(self._sliderails(), mode=Mode.SUBTRACT)

        part = cutblock.part.move(Location((0, 0, self._config.base_depth)))
        part.label = "cut block"
        return part

    def _top_base_block(
        self, offset: float = 0, extra_length: float = 0
    ) -> Part:
        """the basic top shape of the frame before any cuts are made out"""
        with BuildPart() as base:
            with BuildPart():
                Box(
                    self._config.exterior_length + extra_length,
                    self._config.exterior_width,
                    self._config.base_depth,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Box(
                    (self._config.exterior_length + extra_length) / 2,
                    self._config.exterior_width,
                    self._config.bracket_height,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
            with BuildPart(
                Location(
                    (
                        offset,
                        0,
                        self._config.base_depth,
                    )
                )
            ):
                Cylinder(
                    radius=self._config.exterior_radius,
                    height=self._config.exterior_width,
                    rotation=(90, 0, 0),
                    arc_size=180,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                )
            edge_set = base.edges() - base.edges().filter_by_position(
                Axis.X,
                minimum=self._config.exterior_radius + offset - 1,
                maximum=self._config.exterior_radius + offset + 1,
            )
            fillet(edge_set, self._config.fillet_radius)
        return base.part

    def _hanger_cut(self) -> Part:
        """the cutout to fit into the wall plate for hanging the frame"""
        with BuildPart(
            Location(
                (
                    -self._config.exterior_length / 2
                    - self._config.interior_offset,
                    0,
                    0,
                )
            )
        ) as hanger_cut:
            add(
                wall_hanger_cut_template(
                    self._config.minimum_structural_thickness * 1.5,
                    self._config.exterior_width
                    - self._config.minimum_structural_thickness * 2,
                    self._config.bracket_height,
                    bottom=False,
                    post_count=self._config.wall_bracket_post_count,
                    tolerance=self._config.tolerance,
                )
            )
        return hanger_cut.part

    def _pin_cuts(self, offset=0) -> Part:
        """the necessary cuts for the lock pin to fit into the frame and allow for a string hanger"""
        with BuildPart(
            Location(
                (
                    self._config.lock_pin_point.x + offset,
                    0,
                    self._config.lock_pin_point.y + self._config.base_depth,
                )
            ),
        ) as cuts:
            add(
                LockPin(
                    LockPinConfig(
                        stl_folder=self._config.stl_folder,
                        pin_length=self._config.exterior_width,
                        tolerance=self._config.lock_pin_tolerance,
                        height=self._config.minimum_structural_thickness,
                    )
                ).lock_pin(
                    inset=-self._config.lock_pin_tolerance / 2,
                    tie_loop=False,
                )
            )
            with BuildPart(
                Location(
                    (
                        self._config.exterior_length / 2
                        - self._config.fillet_radius
                        + offset,
                        0,
                        0,
                    )
                ),
            ) as stringcut:
                Box(
                    self._config.minimum_structural_thickness / 2,
                    self._config.minimum_structural_thickness * 2,
                    self._config.base_depth,
                    align=(Align.MAX, Align.CENTER, Align.MIN),
                )
                fillet(
                    stringcut.edges().filter_by(Axis.Z),
                    self._config.minimum_structural_thickness / 8,
                )
        return cuts.part

    def top_frame(self) -> Part:
        """
        the top frame for fitting the filament brackets and hanging the walls
        """
        extra_length = (
            0
            if FrameStyle.STANDING in self._config.frame_style
            else self._config.interior_offset * 2
        )
        offset = (
            0
            if FrameStyle.STANDING in self._config.frame_style
            else self._config.interior_offset
        )
        with BuildPart() as tframe:
            add(self._top_base_block(offset, extra_length))
            with BuildPart(
                Location((offset, 0, 0)),
                mode=Mode.SUBTRACT,
            ):
                add(
                    core_cut(
                        self._config.interior_radius,
                        self._config.exterior_width,
                        self._config.base_depth,
                    )
                )
                with GridLocations(
                    0,
                    self._config.bracket_spacing,
                    1,
                    self._config.filament_count,
                ):
                    add(self._bracket_cutblock())
                add(
                    wallslots(
                        wall_distance=self._config.bracket_spacing,
                        count=self._config.filament_count + 1,
                        wall_thickness=self._config.wall_thickness,
                        length=self._config.interior_length
                        + self._config.wall_thickness * 2,
                        interior_radius=self._config.interior_radius,
                        base_depth=self._config.base_depth,
                    )
                )
                add(
                    groove_pair(
                        self._config.groove_distance,
                        self._config.wall_thickness,
                        self._config.interior_width,
                        self._config.groove_depth,
                        self._config.tolerance,
                        self._config.click_fit_distance,
                        self._config.click_fit_radius,
                    ).mirror()
                )

            if FrameStyle.HANGING in self._config.frame_style:
                add(self._hanger_cut(), mode=Mode.SUBTRACT)
            if self._config.include_lock_pin:
                add(self._pin_cuts(offset=offset), mode=Mode.SUBTRACT)
        part = tframe.part
        part.label = "Top Frame"
        return part

    def compile(self):
        self.parts.clear()
        self.parts.append(
            BuildablePart(
                self.top_frame(),
                "frame-top",
                stl_folder=self._config.stl_folder,
            )
        )


if __name__ == "__main__":
    config_path = Path(__file__).parent / "../build-configs/dev.conf"
    if not config_path.exists() or not config_path.is_file():
        config_path = Path(__file__).parent / "../build-configs/debug.conf"
    bender_config = BenderConfig(config_path)
    frame = TopFrame(bender_config.frame_config)
    # show(frame._bracket_cutblock(), reset_camera=Camera.KEEP)
    frame.compile()
    frame.display()
    frame.export_stls()
