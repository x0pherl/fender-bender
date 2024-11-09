from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Part, Align
from basic_shapes import (
    diamond_torus,
    distance_to_circle_edge,
    rounded_cylinder,
    diamond_cylinder,
    rail_block_template,
    screw_cut,
)


class TestTorus:
    def test_diamond_torus(self):
        torus = diamond_torus(major_radius=10, minor_radius=1)
        assert isinstance(torus, Part)
        assert torus.bounding_box().size.X == pytest.approx(22)
        assert torus.bounding_box().size.Y == pytest.approx(22)
        assert torus.bounding_box().size.Z == pytest.approx(2)


class TestDistanceToCircleEdge:
    def test_distance_to_circle_edge(self):
        assert distance_to_circle_edge(10, (0, 5), 45) == 5.818609561002116

    def test_distance_to_circle_edge_discriminant_error(self):
        with pytest.raises(ValueError):
            distance_to_circle_edge(10, (0, 25), 45) == 5.818609561002116


class TestRoundedCylinder:
    def test_short_cylinder_fail(self):
        with pytest.raises(ValueError):
            cyl = rounded_cylinder(2, 3)

    def test_rounded_cylinder(self):
        cyl = rounded_cylinder(5, 11)
        assert cyl.is_valid()
        assert isinstance(cyl, Part)
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(11)


class TestDiamondCylinder:
    def test_diamond_cylinder(self):
        cyl = diamond_cylinder(5, 10)
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_diamond_cylinder_zmax(self):
        cyl = diamond_cylinder(
            5, 10, align=(Align.CENTER, Align.CENTER, Align.MAX)
        )
        assert cyl.is_valid()
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)


class TestRailBlockTemplate:
    def test_rail_block_template(self):
        rail_block = rail_block_template(
            width=10, length=20, depth=10, radius=1, inset=0.2, rail_width=1
        )
        assert rail_block.is_valid()
        assert isinstance(rail_block, Part)
        assert rail_block.bounding_box().size.X == pytest.approx(24.8)
        assert rail_block.bounding_box().size.Y == pytest.approx(9.8)
        assert rail_block.bounding_box().size.Z == pytest.approx(10.8)


class TestScrewCut:
    def test_screw_cut(self):
        screw = screw_cut(5, 1, 2, 10, 10)
        assert screw.is_valid()
        assert screw.bounding_box().size.X == pytest.approx(10)
        assert screw.bounding_box().size.Y == pytest.approx(10)
        assert screw.bounding_box().size.Z == pytest.approx(20)

    def test_invalid_screw_cut(self):
        with pytest.raises(ValueError):
            screw_cut(head_radius=5, shaft_radius=6)


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/basic_shapes.py")
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )
