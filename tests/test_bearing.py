import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from build123d import Part

from bearing import (
    _bowed_cylinder,
    _rolling_element,
    print_in_place_bearing,
    _guide_ring,
)


class TestBearing:
    def test_bowed_cylinder(self):
        part = _bowed_cylinder(3, 10, 1)
        assert isinstance(part, Part)
        assert part.is_valid()
        assert part.bounding_box().size.Z == pytest.approx(10)
        assert part.bounding_box().size.X == pytest.approx(6)
        assert part.bounding_box().size.Y == pytest.approx(6)

    def test_rolling_element(self):
        part = _rolling_element(4)
        assert isinstance(part, Part)
        assert part.is_valid()
        assert part.bounding_box().size.Z == pytest.approx(4)
        assert part.bounding_box().size.X == pytest.approx(4)
        assert part.bounding_box().size.Y == pytest.approx(4)

    def test_guide_ring(self):
        part = _guide_ring(20, 4, 8)
        assert isinstance(part, Part)
        assert part.is_valid()
        assert part.bounding_box().size.Z == pytest.approx(4)
        assert part.bounding_box().size.X == pytest.approx(43.474)
        assert part.bounding_box().size.Y == pytest.approx(43.474)

    def test_print_in_place_bearing(self):
        part = print_in_place_bearing(12, 3, 4)
        assert isinstance(part, Part)
        assert part.is_valid()
        assert part.bounding_box().size.Z == pytest.approx(4)
        assert part.bounding_box().size.X == pytest.approx(24)
        assert part.bounding_box().size.Y == pytest.approx(24)

    def test_print_in_place_bearing_invald(self):
        with pytest.raises(ValueError):
            part = print_in_place_bearing(1, 2, 3)

    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/bearing.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
