from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest

from assembly_documentation import wall_assembly


class TestDocPics:
    def test_docs_bare_execution(self):
        loader = SourceFileLoader("__main__", "src/assembly_documentation.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )

    def test_docs_wall_assembly(self):
        wall_assembly()
