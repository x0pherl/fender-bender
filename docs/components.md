# Components Overview
<!---
..
    fender-bender readthedocs documentation

    by:   x0pherl
    date: September 25th 2024

    desc: This is the documentation for the fender-bender filament buffering solution on readthedocs

    license:

        Copyright 2024 x0pherl

        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->

![Fender-Bender Logo](assets/logo.svg){ align=right loading=lazy width=33%}

## Sourced Parts

### Resources for fittings and tubing
You'll need to purchase Tube Fittings, and potentially tubing. Here are some sources that I've found here in the states

| Description                             | Possible Source |
| -----------                             | --------------- |
| 5x bearings (or however many filament brackets you plan to install) | [uxcell via amazon](https://www.amazon.com/gp/product/B082PQ8DVT) |
| PC4-M10 Straight Pneumatic Tube Fitting (:asterisk: for 4mm OD tubing when fittings are desired) | [BIQU via Amazon](https://www.amazon.com/gp/product/B01IB81IHG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) |
| 1/8th threaded PC6-01 Through fitting (:asterisk: for 6mm OD tubing when fittings are desired)| [Robot Digg](https://www.robotdigg.com/product/755/Through-fitting-PC4-M6,-PC4-01,-PC6-M6-or-PC6-01-for-PTFE-Tubing) (:warning: be sure to select PC6-01) and print the -1-8th fitting parts |
| PTFE Teflon tubing (3mm Inner Diameter(ID) X 6mm Outer Diameter (OD)) | [uxcell via Amazon](https://www.amazon.com/gp/product/B09158R6LD) |


## Printed Parts

Of course, most of the fender-bender project is intended to be 3D printed. This guide doesn't need to build the project, it's here as a reference in case you need a reminder of what the vocabulary in the printing & assembly instructions is referring to :slight_smile:.

### The "Filament Bracket"

This bracket is the component responsible for ensuring that the filament smoothly moves through the system when feeding the extruder, and is redirected to the buffer when retracting.
The system requires one filament bracket for each filament you need to buffer (on the Prusa MMU3, you'll need 5 filament brackets).

#### Bottom Bracket
This is the primary part of the filament bracket, supporting the PTFE tubes through the system. The filament bracket wheel mounts on top of this part.
Several alternative parts exist for different tube and connector configurations. The default part is for 3mm inner diameter / 6mm outer diameter PTFE tubing without a connector. See Resources for fittings and tubing for part sources

#### Bracket Wheel
The wheel will mount on a bearing and sit on the bottom bracket. When the Filament Bracket is fully assembled, the wheel should spin freely.

#### Bracket Top
The bracket top slides into the bottom bracket and locks the wheel/bearing assembly into place.

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
The default part includes the cut for the wall hanger; if you prefer to print the self-standing version it will have a smoother exterior profile, but you'll have to choose alternative parts for the connector and bottom as well.

#### Frame Connector
This connects the two wall assemblies.
The default part includes a thicker wall to the wall side for wall mounted installations. The alternative "standing" file will provide a straight back line when coupled with the standing top and bottom components.

#### Frame Bottom
In hanging installations, this part is not strictly necessary. In hybrid or standing installations, this includes a flat bottom for a free-standing buffer.
The default part includes the stand but also has extra spacing for wall mounted installations. The "hanging-no-stand" alternative has a round bottom profile which uses less filament and a different appearance in hanging installations. The "standing" alternative eliminates the extra spacing for the wall hanging bracket, as well as the screw guide along the back.
