import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from walls_config import WallsConfig
from walls import Walls
from ocp_vscode import show, save_screenshot
from bender_config import BenderConfig
from pathlib import Path


class TestWallConfig:
    def test_wall_config(self, wall_config):
        assert wall_config.top_diameter == 70
        assert wall_config.top_extension == 10
        assert wall_config.sidewall_width == 110
        assert wall_config.wall_thickness == 3
        assert wall_config.reinforcement_thickness == 7
        assert wall_config.section_depth == 170

    def test_top_radius(self, wall_config):
        assert wall_config.top_radius == wall_config.top_diameter / 2

    def test_straight_length(self, wall_config):
        assert (
            wall_config.sidewall_straight_length
            == wall_config.section_depth
            - wall_config.top_radius
            - wall_config.top_extension
        )

    def test_load_from_bender_config(self):
        bconfig = BenderConfig()
        wconfig = WallsConfig().load_from_bender_config(bconfig)
        assert (
            wconfig.top_diameter
            == bconfig.wheel.diameter - bconfig.wall_thickness
        )
        assert (
            wconfig.top_radius
            == bconfig.wheel.radius - bconfig.wall_thickness / 2
        )
        assert wconfig.top_extension == bconfig.frame_bracket_spacing
        assert wconfig.sidewall_width == bconfig.sidewall_width
        assert wconfig.wall_thickness == bconfig.sidewall_straight_depth
        assert wconfig.reinforcement_thickness == bconfig.frame_connector_depth
        assert wconfig.section_depth == bconfig.frame_bracket_exterior_radius


class TestWalls:
    def test_bare_execution(self):
        loader = SourceFileLoader("__main__", "src/walls.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )

    def test_flipped_sidewall(self):
        walls = Walls()
        sidewall = walls.side_wall(flipped=True)
        assert sidewall.volume > 0

    def test_flipped_guidewall(self):
        walls = Walls()
        guidewall = walls.guide_wall(flipped=True)
        assert guidewall.volume > 0

    def test__step_one_assembly(self):
        walls1 = Walls()
        walls1.compile()
        assembly = walls1._step_one_assembly()
        assert assembly.volume > 0

    def test__step_two_assembly(self):
        walls1 = Walls()
        walls1.compile()
        # todo make a compiled default walls as a fixture of the tests
        assembly = walls1._step_two_assembly()
        assert assembly.volume > 0

    def test_export_stls(self, compiled_walls):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.mkdir"):
                compiled_walls.export_stls()

    def test_export_stls(self, compiled_walls):
        with patch("build123d.export_stl"):
            with patch("pathlib.Path.exists", return_value=False):
                compiled_walls.export_stls()

    def test_export_stls_with_none_folder(self):
        walltest = Walls()
        walltest._config.stl_folder = "NONE"
        walltest.export_stls()

    def test_display(self, compiled_walls):
        with patch("ocp_vscode.show"):
            compiled_walls.display()

    def test_render_2d(self, compiled_walls):
        with patch("ocp_vscode.show"):
            with patch("ocp_vscode.save_screenshot"):
                compiled_walls.render_2d(save_to_disk=True)
