#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication

from src.factory_creator.cli.argument_processor import ArgumentProcessor
from src.factory_creator.cli.cli import CLI
#TODO: setup pyproject.toml (and use pip install -e .   so it is not needed to write src.factory... but only factory...)

from src.factory_creator.gui.main_window import MainWindow


def main(no_browser: bool = False):
    """
    Main function which call the GUI.
    """
    app = QApplication(sys.argv)

    window = MainWindow(use_embedded_browser=not no_browser)
    window.show()

    return app.exec()

if __name__ == "__main__":
    args = ArgumentProcessor.process_arguments()

    if not args.cli:
        sys.exit(main(args.no_browser))
    else:
        CLI.run(args)
