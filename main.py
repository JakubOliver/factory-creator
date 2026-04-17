#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication

from src.factory_creator.GUI.main_window import MainWindow

recipe_file_path = "data/recipe.json"

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
