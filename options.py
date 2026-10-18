import argparse


class Options:
    """Handles command-line argument parsing for the solve_pips application.

    Attributes:
        parser (argparse.ArgumentParser): The argument parser instance.
        initialized (bool): Flag indicating if the parser has been configured.
    """
    def __init__(self) -> None:
        """Initializes the Options class with a default ArgumentParser."""
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.initialized = False

    def initialize(self) -> None:
        """Configures the command-line arguments for the puzzle solver.

        Adds arguments for TOML files, CSV files, and verbose logging.
        """
        self.parser.add_argument(
            "-t",
            "--toml",
            dest="toml_file",
            type=str,
            help="the puzzle information as a toml file",
        )
        self.parser.add_argument(
            "-c",
            "--csv",
            dest="csv_file",
            type=str,
            help="the puzzle information as a csv file",
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            help="set logging level to INFO",
            action="store_true",
        )
        self.initialized = True

    def getparse(self) -> argparse.Namespace:
        """Parses the command-line arguments.

        Returns:
            argparse.Namespace: An object containing the parsed argument values.
        """
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args()

        return self.opt
