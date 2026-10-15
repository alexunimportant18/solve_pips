import argparse


class Options:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.initialized = False

    def initialize(self) -> None:
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
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args()

        return self.opt
