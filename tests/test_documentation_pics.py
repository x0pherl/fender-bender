from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest

from assembly_documentation import wall_assembly


class TestDocPics:
    def test_docs_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.show_all"),
            patch("ocp_vscode.show_object"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader(
                "__main__", "src/assembly_documentation.py"
            )
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_docs_wall_assembly(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("assembly_documentation.show"),
            patch("assembly_documentation.save_screenshot"),
        ):
            wall_assembly()
