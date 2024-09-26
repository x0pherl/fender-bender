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



.. highlight:: python

.. image:: ./assets/logo.svg
  :align: right
  :alt: fender-bender logo


########
Summary
########

FENDER BENDER is an open-source filament buffering system. Filament buffers are necessary for reliable operation of multi-material systems such as Prusa's MMU3 or earlier revisions of the ERCF.

The 3d modeling in this project is made possible by Build123d -- a python-based, parametric, boundary representation (BREP) modeling framework for 2D and 3D CAD. You can learn more by reading the build123d documentation.

FENDER BENDER begins with an opinionated design for building the most effective buffering system that eliminates as much friction from the system as possible. This was done through careful measurement of resistance all the way through the system for hundreds of prototypes. The final reference design uses 6mm OD x 3mm ID PTFE tubing wherever possible in our internal filament passages to minimize any friction introduced by the buffering system. This attention to performance was matched by focus on creating a design that maintains a reasonable aesthetic.

We believe the reference design represents the best choices for a buffering system. However, because FENDER BENDER was built using a flexible, parametric tool, the design can easily be modified to build buffering systems representing differing opinions on design; allowing for different tubes, connectors, and bearings to be built without having to modify the Python/Build123d source code.

This flexibility comes from having as many elements as possible calculated on a few critical elements. While this approach allows for tremendous flexibility without a lot of knowledge of Python, there's no guarantee that any combination of values will work. If you're struggling to get something to work, please reach out with enough details for us to assist.


#################
Table Of Contents
#################

.. toctree::
    :maxdepth: 2

    introduction.rst
    assembly.rst
    usage.rst

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`