from dataclasses import fields
import pytest
from unittest.mock import patch

from typing import List, get_origin
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

from filament_wheel_config import WheelConfig

from bender_config import (
    BenderConfig,
    FrameStyle,
)
from fb_library import Point


class TestBenderConfig:

    def test_benderconfig_defaults(self):
        cfg = BenderConfig()
        for field in fields(cfg):
            if (
                get_origin(field.type) is not list
                and field.type is not WheelConfig
            ):
                assert (
                    getattr(cfg, field.name)
                    == BenderConfig.__dataclass_fields__[field.name].default
                )

    def test_benderconfig_tube_dict(self, bender_config_yaml_tube_dict):
        cfg = BenderConfig(configuration=bender_config_yaml_tube_dict)
        assert cfg.default_connector.tube.outer_diameter == 4321

    def test_wheelconfig_load_yaml_str(self, wheel_config_yaml):
        cfg = WheelConfig(configuration=wheel_config_yaml)
        assert cfg.diameter == 12.3
        assert cfg.spoke_count == 25
        assert cfg.lateral_tolerance == 1.111
        assert cfg.radial_tolerance == 0.222
        assert cfg.bearing.diameter == 1.2
        assert cfg.bearing.inner_diameter == 0.1
        assert cfg.bearing.shelf_diameter == 0.2
        assert cfg.bearing.depth == 1

    def test_frame_clip_point(self, default_bender_config):
        assert default_bender_config.frame_clip_point.x == pytest.approx(
            51.24382889675596
        )
        assert default_bender_config.frame_clip_point.y == pytest.approx(8)

    def test_click_distance(self, default_bender_config):
        assert (
            default_bender_config.frame_config.click_fit_distance
            == default_bender_config.guidewall_config.click_fit_distance
        )

    def test_bare_execution(self):
        loader = SourceFileLoader("__main__", "src/bender_config.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )

    def test_bare_execution_missing_file(self):
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
        with pytest.raises(ValueError):
            with patch.object(
                Path, "exists", return_value=False
            ) as mock_exists:
                loader = SourceFileLoader("__main__", "src/bender_config.py")
                loader.exec_module(
                    module_from_spec(spec_from_loader(loader.name, loader))
                )

    def test_frame_bracket_exterior_x_distance(self, default_bender_config):
        assert (
            default_bender_config.frame_bracket_exterior_x_distance(10)
            == 50.8913548650456
        )

    def test_sidewall_section_depth(self, default_bender_config):
        assert (
            default_bender_config.sidewall_section_depth == 153.0677324554909
        )

    def test_frame_clip_inset(self, default_bender_config):
        assert default_bender_config.frame_clip_inset == 1.0

    def test_frame_clip_rail_width(self, default_bender_config):
        assert default_bender_config.frame_clip_rail_width == 1.414213562373095

    def test_frame_clip_width(self, default_bender_config):
        assert default_bender_config.frame_clip_width == 15.1

    def test_frame_base_depth(self, default_bender_config):
        assert default_bender_config.frame_base_depth == 8

    def test_sidewall_straight_depth(self, default_bender_config):
        assert (
            default_bender_config.sidewall_straight_depth == 110.0677324554909
        )

    def test_frame_connector_depth(self, default_bender_config):
        assert default_bender_config.frame_connector_depth == 9

    def test_frame_bracket_exterior_radius(self, default_bender_config):
        assert (
            default_bender_config.frame_bracket_exterior_radius
            == 51.864535089018204
        )

    def test_frame_bracket_exterior_diameter(self, default_bender_config):
        assert (
            default_bender_config.frame_bracket_exterior_diameter
            == 103.72907017803641
        )

    def test_frame_bracket_spacing(self, default_bender_config):
        assert default_bender_config.frame_bracket_spacing == 16

    def test_frame_click_sphere_point(self, default_bender_config):
        assert default_bender_config.frame_click_sphere_point == Point(
            47.864535089018204, 4.15
        )

    def test_top_frame_interior_width(self, default_bender_config):
        assert default_bender_config.top_frame_interior_width == 77

    def test_frame_hanger_offset(self, default_bender_config):
        assert default_bender_config.frame_hanger_offset == 2

    def test_frame_exterior_width(self, default_bender_config):
        assert default_bender_config.frame_exterior_width == 91.0

    def test_default_connector(self, default_bender_config):
        assert default_bender_config.default_connector.diameter == 10.1

    def test_sidewall_width(self, default_bender_config):
        assert default_bender_config.sidewall_width == 103.3

    def test_bearing_shelf_height(self, default_bender_config):
        assert default_bender_config.bearing_shelf_height == 4.3

    def test_bracket_width(self, default_bender_config):
        assert default_bender_config.bracket_width == 96.3

    def test_chamber_cut_length(self, default_bender_config):
        assert default_bender_config.chamber_cut_length == 97.3

    def test_bracket_height(self, default_bender_config):
        assert default_bender_config.bracket_height == 43.2

    def test_bracket_depth_default(self, default_bender_config):
        assert default_bender_config.bracket_depth == 12.6

    def test_bracket_depth_min_is_greater(self, default_bender_config):
        default_bender_config.minimum_bracket_depth = 1234567
        assert default_bender_config.bracket_depth == 1234567

    def test_bracket_depth_bearing_depth_is_greater(
        self, default_bender_config
    ):
        default_bender_config.wheel.bearing.depth = 1234567
        assert (
            default_bender_config.bracket_depth
            == 1234567
            + default_bender_config.wheel.lateral_tolerance
            + default_bender_config.minimum_structural_thickness * 2
        )

    def test_bracket_depth_connector_diameter_is_greater(
        self, default_bender_config
    ):
        default_bender_config.default_connector.diameter = 1234567
        assert (
            default_bender_config.bracket_depth
            == 1234567 + default_bender_config.minimum_thickness * 2
        )

    def test_bracket_depth_tube_diameter_is_greater(
        self, default_bender_config
    ):
        default_bender_config.default_connector.tube.outer_diameter = 1234567
        assert (
            default_bender_config.bracket_depth
            == 1234567 + default_bender_config.minimum_thickness * 2
        )

    def test_fillet_radius(self, default_bender_config):
        assert default_bender_config.fillet_radius == 3.15

    def test_wheel_support_height(self, default_bender_config):
        assert default_bender_config.wheel_support_height == 4

    def test_tube_radius(self, default_bender_config):
        assert (
            default_bender_config.default_connector.tube.outer_radius == 3.25
        )

    def test_tube_inner_radius(self, default_bender_config):
        assert (
            default_bender_config.default_connector.tube.inner_radius == 1.775
        )

    def test_connector_radius(self, default_bender_config):
        assert default_bender_config.default_connector.radius == 5.05

    def test_frame_length(self, default_bender_config):
        assert (
            default_bender_config.frame_exterior_length == 123.72907017803641
        )

    def test_frame_length_standing(self, default_bender_config):
        x = default_bender_config
        x.frame_style = FrameStyle.STANDING
        assert x.frame_exterior_length == 119.72907017803641

    def test_default_connector_config(self, bender_config_yaml_default_second):
        cfg = BenderConfig(bender_config_yaml_default_second)
        assert cfg.default_connector.tube.outer_diameter == 1234

    def test_bad_config(self):
        with pytest.raises(ValueError):
            BenderConfig("this should fail")

    def test_load_bender_config_file(self):
        config_path = Path(__file__).parent / "pytest_bender.conf"

        cfg = BenderConfig(configuration=config_path)
        assert cfg.default_connector.tube.outer_diameter == 1234
