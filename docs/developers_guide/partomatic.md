# The Partomatic philosophy behind Fender-Bender

Build123d is a powerful library, but it leaves the creation of final parts up to the developer. For a project like fender-bender, with many related and interlocking parts, this can make releasing a new version a project in and of itself.

[Partomatic](https://github.com/x0pherl/fender-bender/blob/main/src/partomatic.py) is an attempt to standardize some of the build automation behind each part. Partomatic is an [abstract base class](https://docs.python.org/3/library/abc.html) for components within a larger project. It defines a series of abstract methods which must be defined within a descendent class. These elements are:

## `load_config`

`load_config(self, configuration: str):`

This method handles loading the configuration. In some cases this is loading a full BenderConfig configuration file by passing the file location; in other cases we simply pass along a valid yaml configuration of a component.

## `compile`

`def compile(self):`

This method is responsible for generating the 3d geometry for each component.

## `display`

`def display(self):`

Shows the relevant parts in OCP CAD Viewer

## `export_stls`

`def export_stls(self):`

This method is responsible for generating and saving the actual STL files that will be a
part of the release.

## `render_2d`

`def render_2d(self):`

This method is responsible for generating any images that may be required for documentation
or other publications. In many cases, this is implemented with a simple `pass`

## `partomate`

`def partomate(self, bypass_2d_render: bool = True):`

This method is _not_ an abstract baseclass and could be modified as needed. This method calls the
- compile
- render_2d (if `bypass_2d_render` is set to false)
- export_stls

methods in that order.
