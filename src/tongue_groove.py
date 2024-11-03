from build123d import (
    Part,
    BuildPart,
    Align,
    Axis,
    Cylinder,
    GridLocations,
    Sphere,
    Mode,
    Box,
    Location,
    extrude,
    PolarLocations,
    add,
)

from ocp_vscode import show, Camera


def tongue(
    width, length, depth, tolerance, click_fit_distance, click_fit_radius
) -> Part:
    """
    creates a snap in tongue for fitting peieces together,
    companion to groove
    """
    with BuildPart() as single_tongue:
        Box(
            width - tolerance * 2,
            length - tolerance * 2,
            depth - tolerance - width / 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        extrude(
            single_tongue.faces().sort_by(Axis.Z)[-1],
            amount=width / 2,
            taper=44,
        )
        with BuildPart(
            single_tongue.faces().sort_by(Axis.X)[-1], mode=Mode.ADD
        ):
            with GridLocations(
                0,
                click_fit_distance,
                1,
                2,
            ):
                Sphere(radius=click_fit_radius * 0.75)
        with BuildPart(
            single_tongue.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT
        ):
            with GridLocations(
                0,
                click_fit_distance,
                1,
                2,
            ):
                Sphere(radius=click_fit_radius)

        # this center cut guides the alignment when assembling,
        # and provides additional stability to the hold
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                width - tolerance * 2,
                width / 2 + tolerance * 4,
                depth - tolerance,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(Location((0, 0, width * 0.75))):
                Sphere(radius=width * 0.75)
                Cylinder(
                    radius=width * 0.6,
                    height=depth,
                    rotation=(0, 0, 0),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    part = single_tongue.part
    part.label = "tongue"
    return part


def groove(
    width, length, depth, tolerance, click_fit_distance, click_fit_radius
) -> Part:
    """
    creates a groove for snap-fitting peieces together,
    companion to tongue
    """
    with BuildPart(mode=Mode.PRIVATE) as single_groove:
        Box(
            width + tolerance * 2,
            length + tolerance,
            depth - width / 2,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        extrude(
            single_groove.faces().sort_by(Axis.Z)[-1],
            amount=width / 2,
            taper=44,
        )
        with BuildPart(
            single_groove.faces().sort_by(Axis.X)[-1], mode=Mode.ADD
        ):
            with GridLocations(
                0,
                click_fit_distance,
                1,
                2,
            ):
                Sphere(radius=click_fit_radius)
        with BuildPart(
            single_groove.faces().sort_by(Axis.X)[0], mode=Mode.SUBTRACT
        ):
            with GridLocations(
                0,
                click_fit_distance,
                1,
                2,
            ):
                Sphere(radius=click_fit_radius * 0.75)
        with BuildPart(mode=Mode.SUBTRACT):
            Box(
                width + tolerance * 2,
                width / 2 + tolerance * 2,
                depth + tolerance,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(Location((0, 0, width * 0.75))):
                Sphere(radius=width / 2)
    return single_groove.part.mirror()


def groove_pair(
    groove_distance,
    width,
    length,
    depth,
    tolerance,
    click_fit_distance,
    click_fit_radius,
) -> Part:
    """
    creates two grooves facing each other,
    """

    with BuildPart() as grooves:
        with PolarLocations(
            -groove_distance / 2,
            2,
        ):
            add(
                groove(
                    width,
                    length,
                    depth,
                    tolerance,
                    click_fit_distance,
                    click_fit_radius,
                )
            )
    return grooves.part


def tongue_pair(
    tongue_distance,
    width,
    length,
    depth,
    tolerance,
    click_fit_distance,
    click_fit_radius,
) -> Part:
    """
    creates two tongues facing each other,
    """

    with BuildPart() as tongues:
        with PolarLocations(
            -tongue_distance / 2,
            2,
        ):
            add(
                tongue(
                    width,
                    length,
                    depth,
                    tolerance,
                    click_fit_distance,
                    click_fit_radius,
                )
            )
    return tongues.part


if __name__ == "__main__":
    show(
        groove(4, 20, 5, 0.1, 10, 1),
        tongue(4, 20, 5, 0.1, 10, 1),
        groove_pair(40, 4, 20, 5, 0.1, 10, 1),
        tongue_pair(40, 4, 20, 5, 0.1, 10, 1),
        reset_camera=Camera.KEEP,
    )
