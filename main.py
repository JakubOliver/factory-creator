#!/usr/bin/env python3

import sys
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parent / "src"
if str(SRC_DIRECTORY) not in sys.path:
    # Use the canonical factory_creator package name in both the application
    # and external plugins.
    sys.path.insert(0, str(SRC_DIRECTORY))

from factory_creator.cli import ArgumentProcessor, CLI

# TODO: Add pyproject.toml and use ``pip install -e .`` so the package can be
# imported as ``factory_creator`` without modifying ``sys.path`` here.
#TODO: add option to set start and end of mutaiton in gui (and CLI)


def main(no_browser: bool = False):
    """
    Main function which call the GUI.
    """
    from PySide6.QtWidgets import QApplication
    from factory_creator import MainWindow

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
