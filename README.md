# FENDER BENDER FILAMENT BUFFER

## Overview

<img src="docs/assets/logo.svg" align="right" width=33%>

FENDER BENDER is an open-source filament buffering system. Filament buffers are necessary for reliable operation of multi-material systems such as Prusa's MMU3 or earlier revisions of the ERCF.

The 3d modeling in this project is made possible by Build123d -- a python-based, parametric, boundary representation (BREP) modeling framework for 2D and 3D CAD. You can learn more by reading the [build123d documentation](https://build123d.readthedocs.io/en/latest/).

FENDER BENDER begins with an opinionated design for building the most effective buffering system that eliminates as much friction from the system as possible. This was done through careful measurement of resistance *all the way through the system* for hundreds of prototypes. The final reference design uses 6mm OD x 3mm ID PTFE tubing wherever possible in our internal filament passages to minimize any friction introduced by the buffering system. This attention to performance was matched by focus on creating a design that maintains a reasonable aesthetic.

We believe the reference design represents the best choices for a buffering system. However, because FENDER BENDER was built using a flexible, parametric tool, the design can easily be modified to build buffering systems representing differing opinions on design; allowing for different tubes, connectors, and bearings to be built without having to modify the Python/Build123d source code.

This flexibility comes from having as many elements as possible calculated on a few critical elements. While this approach allows for tremendous flexibility without a lot of knowledge of Python, there's no guarantee that any combination of values will work. If you're struggling to get something to work, please reach out with enough details for us to assist.

## Documentation
Complete documentation for the Fender-Bender project is maintained in the docs folder and on the [fender-bender documentation](https://fender-bender.readthedocs.io/en/latest/) site.

## Modifying the Source

The included source file relies on the build123d library. I recommend following the [build123d installation instructions](https://build123d.readthedocs.io/en/latest/installation.html).

[Fender-bender developer documentation](https://fender-bender.readthedocs.io/en/latest/developers/) will walk you through the general philosophy of the fender-bender project.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you're not a python developer but want to help, we can always use volunteers willing to print and test new prototypes :smile:

## License

This project is licensed under the terms of the MIT license [MIT](https://choosealicense.com/licenses/mit/)
