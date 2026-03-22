import sys

from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
)

from graphviz import Digraph

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

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.input_field)
        file_layout.addWidget(self.submit_button)

        self.main_layout.addLayout(file_layout)

        self.main_layout.addStretch()

    def _connect_signals(self) -> None:
        self.submit_button.clicked.connect(self._handle_submit)

    def _handle_submit(self) -> None:
        text = self.input_field.text()
        print(f"Used path: {text}")

        #TODO: whether file exists

        factories = FactoryLoader.load(text)
        #root = FactoryLoader.get_dependency_tree(factories, "steam-turbine")
        root = FactoryLoader.get_dependency_tree(factories, "nuclear-reactor")
        
        if root is not None:
            #root.dfs()

            dot = Digraph(comment="Tree")
            
            root.add_to_graph(dot, 0)
            print(dot.source)
            dot.render("tree", format="png", cleanup=True)

