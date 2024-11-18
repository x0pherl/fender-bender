from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Part, Align

from hexwall import HexWall


class TestHexWall:

    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/hexwall.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
