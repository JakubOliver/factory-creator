#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication

from src.GUI.main_window import MainWindow
from src.factory import FactoryLoader

recipe_file_path = "data/recipe.json"

def main():
    factories = FactoryLoader.load(recipe_file_path)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
