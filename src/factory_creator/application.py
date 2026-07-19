import sys

from .cli import ArgumentProcessor, CLI


def run_gui(no_browser: bool = False) -> int:
    from PySide6.QtWidgets import QApplication

    from . import MainWindow

    app = QApplication(sys.argv)

    window = MainWindow(use_embedded_browser=not no_browser)
    window.show()
    
    return app.exec()


def main() -> int:
    args = ArgumentProcessor.process_arguments()

    if args.cli:
        CLI.run(args)
        return 0

    return run_gui(args.no_browser)

