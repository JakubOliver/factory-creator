import sys

from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from ..factory import FactoryLoader    


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Factory layout creation")
        self.resize(500, 250)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.title_label = QLabel("Application")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Recipes path...")

        self.submit_button = QPushButton("Import recipes")

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.input_field)
        self.main_layout.addWidget(self.submit_button)

        self.main_layout.addStretch()

    def _connect_signals(self) -> None:
        self.submit_button.clicked.connect(self._handle_submit)

    def _handle_submit(self) -> None:
        text = self.input_field.text()
        print(f"Used path: {text}")

        factories = FactoryLoader.load(text)

        for factory in factories:
            print(factory)
