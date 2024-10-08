"""Part extended for CI/CD automation"""

from abc import ABC, abstractmethod

from build123d import Part


class Partomatic(Part, ABC):
    """
    Partomatic is an extension of the Part class from build123d
    that allows for automation within a continuous integration
    environment. Descendant classes must implement:
    load_config: for loading an external configuration from a file
        - arguments:
            - configuration_path: the path to the configuration file
    display: for displaying the part using OCP
    export_stls: for exporting the part to STL files
        -arguments:
            - target_directory: the directory to save the STL files
    """

    @abstractmethod
    def load_config(self, configuration_path: str):
        """
        loads the configuration file
         -------
        arguments:
            - configuration_path: the path to the configuration file
        """

    @abstractmethod
    def compile(self):
        """
        Builds the relevant parts for the partomatic part
        """

    @abstractmethod
    def display(self):
        """
        Shows the relevant parts in OCP CAD Viewer
        """

    @abstractmethod
    def export_stls(self):
        """
        Generates the relevant STLs in the configured
        folder
        """

    @abstractmethod
    def render_2d(self):
        """method to render the part to a png file"""

    def partomate(self):
        """automates the part generation, render a 2d snapshot, and export"""
        self.compile()
        self.render_2d()
        self.export_stls()
