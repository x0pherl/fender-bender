# FENDER BENDER FILAMENT BUFFER

## Overview

![FENDER BENDER logo](logo.svg){: width="25%"}

FENDER BENDER is an open-source filament buffering system. Filament buffers are necesarry for reliable operation of multi-material systems such as Prusa's MMU3 or earlier revisions of the ERCF.

The 3d modeling in this project is made possible by Build123d -- a python-based, parametric, boundary representation (BREP) modeling framework for 2D and 3D CAD. You can learn more by reading the [build123d documentation](https://build123d.readthedocs.io/en/latest/).

FENDER BENDER begins with an opinionated design for building the most effective buffering system that eliminates as much friction from the system as possible. This was done through careful measurement of resistance *all the way through the system* for hundreds of prototypes. The final reference design uses 6mm OD x 3mm ID PTFE tubing wherever possible in our internal filament passages to minimize any friction introduced by the buffering system. This attention to performance was matched by focus on creating a design that maintains a reasonable asthetic.

We believe the reference design represents the best choices for a buffering system. However, because FENDER BENDER was built using a flexible, parametric tool, the design can easily be modified to build buffering systems representing differing opinions on design; allowing for different tubes, connectors, and bearings to be built without having to modify the Python/Build123d source code.

This flexibility comes from having as many elements as possible calculated on a few critical elements. While this approach allows for tremendous flexibility without a lot of knowledge of Python, there's no guarantee that any combination of values will work. If you're struggling to get something to work, please reach out with enough details for us to assist.

## Components

### The "Filament Bracket"

This bracket is the component responsible for ensuring that the filament smoothly moves through the system when feeding the extruder, and is redirected to the buffer when retracting.

The system requires one filament bracket for each filament you need to buffer (on the Prusa MMU3, you'll need 5 filament brackets).

#### Bottom Bracket

This is the primary part of the filament bracket, supporting the PTFE tubes through the system. The filament bracket wheel mounts on top of this part

#### Bracket Wheel

The wheel will mount on a bearing and sit on the [bottom bracket](#bottom-bracket). When the [Filament Bracket](#the-filament-bracket) is fully assembled, the wheel should spin freely.

#### Bracket Top

The bracket top slides into the [bottom bracket](#bottom-bracket) and locks the wheel/bearing assemly into place.

#### Bracket Clip

If you've chosen a frame clip locking style, the bracket clips lock each filament bracket into place in the top frame to prevent it from coming out in the event of a printer jam.

### Walls

The walls form the sides of each buffering chamber. A fully assembled filament bracket will have two complete wall assemblies.

#### Guide Walls
The guide walls connect to the frame elements and hold the sidewalls in place

#### Reinforced Side Walls
Reinforced sidewalls are for the exterior of a wall assembly and provide some extra rigidity to the assembled frame.

#### Side Walls
Side walls separate each filament chamber.

### Frame
The frame holds everything together.

#### Frame Top
This is one of the most critical components of the system. Each filament bracket should snap into the frame with a satisfying click when properly assembled. One of the wall assemblies will click into the bottom of the frame. In wall mounted installations, the frame top will also connect to the wall hanger.

#### Frame Connector
This connects the two wall assemblies.

#### Frame Bottom
In hanging installations, this part is not strictly necesarry. In hybrid or standing installtions, this includes a flat bottom for a free-standing buffer.

## Code

The source file, `build.py` is used to generate the .stl files -- the 3d models. The other python files represent the shapes that are generated. The various parameters and tolerances are all stored in the .conf files in the build-config directory -- it's possible to generate new sets of parts by modifying those configurations and executing `python3 ./build.py`

## Resources for fittings and tubing

You'll need to purchase Tube Fittings, and potentially tubing. Here are some sources that I've found here in the states

| Description                             | Possible Source |
| -----------                             | --------------- |
| PC4-M10 Straight Pneumatic Tube Fitting (for 4mm OD tubing) | [BIQU via Amazon](https://www.amazon.com/gp/product/B01IB81IHG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) |
| 1/8th threaded PC6-01 Through fitting (for 6mm OD tubing)| [Robot Digg](https://www.robotdigg.com/product/755/Through-fitting-PC4-M6,-PC4-01,-PC6-M6-or-PC6-01-for-PTFE-Tubing) (be sure to select PC6-01) and print the -1-8th fitting parts|
| PTFE Teflon tubing (3mm Inner Diameter(ID) X 6mm Outer Diameter (OD)) | [uxcell via Amazon](https://www.amazon.com/gp/product/B09158R6LD)

## Recommended Print Settings
Other than where noted, the standard Prusa Slicer "structural" profiles will be fine. Some components will require supports to print properly, and we strongly recommend using organic supports. You'll get best results from hand painting areas for support and using PETG supports for PLA parts or vice-versa (although that's not strictly required)


## Modifying the Source

The included source file relies on the build123d library. I recommend following the [build123d installation instructions](https://build123d.readthedocs.io/en/latest/installation.html).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you're not a python developer but want to help, we can always use volunteers willing to print and test new prototypes :smile:

## License

This project is licensed under the terms of the MIT license [MIT](https://choosealicense.com/licenses/mit/)
