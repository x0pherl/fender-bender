import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from ocp_vscode import show, save_screenshot
from bender_config import BenderConfig
from pathlib import Path

from guidewall_config import GuidewallConfig
from guidewall import Guidewall


class TestConfig:
    def test_load(self):
        config_path = Path(__file__).parent / "../build-configs/dev.conf"
        if not config_path.exists() or not config_path.is_file():
            config_path = Path(__file__).parent / "../build-configs/debug.conf"

        bender_config = BenderConfig(config_path)
        gw_config = bender_config.guidewall_config
        assert isinstance(gw_config, GuidewallConfig)

        assert (
            gw_config.width
            == gw_config.section_width * gw_config.section_count
            + gw_config.reinforcement_thickness * 2
        )


class TestGuidewall:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            loader = SourceFileLoader("__main__", "src/guidewall.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_none_stl_folder(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("build123d.export_stl"),
        ):
            sidewall = Guidewall()
            sidewall._config.stl_folder = "NONE"
            sidewall.export_stls()

    def test_render_2d(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
            patch("build123d.export_stl"),
        ):
            sidewall = Guidewall()
            sidewall.render_2d()
