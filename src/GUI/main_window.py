from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel, QCheckBox,
)

from graphviz import Digraph
from ..factory_loader import FactoryLoader

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

        self.title_label = QLabel("Factory layout creation")

        self._setup_file_layout()
        self._setup_characteristic_vector_layout()

        self.main_layout.addStretch()

    def _setup_file_layout(self) -> None:
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Recipes path...")

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Recipes")

        self.submit_button = QPushButton("Import recipes")

        self.main_layout.addWidget(self.title_label)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.type_input)
        file_layout.addWidget(self.submit_button)

        self.main_layout.addLayout(file_layout)

    def _setup_characteristic_vector_layout(self) -> None:
        graph_characteristic_vector_layout = QHBoxLayout()

        self.show_amounts_on_edges_check_box = QCheckBox("Show amounts")
        self.show_simplified_structure = QCheckBox("Simplified structure")
        self.show_simplified_structure.setChecked(True)

        graph_characteristic_vector_layout.addWidget(self.show_amounts_on_edges_check_box)
        graph_characteristic_vector_layout.addWidget(self.show_simplified_structure)

        self.main_layout.addLayout(graph_characteristic_vector_layout)

    def _connect_signals(self) -> None:
        self.submit_button.clicked.connect(self._handle_submit)

    def _handle_submit(self) -> None:
        #TODO: create now thread for this action so the GUI is still responsive

        path = self.input_path.text()
        type = self.type_input.text()
        print(f"Used path: {path} {type}")

        #TODO: whether file exists

        factories = FactoryLoader.load(path)

        root = FactoryLoader.get_dependency_tree(factories, type)

        if root is not None:
            #root.dfs()

            dot = Digraph(comment="Tree")
            
            root.dependency_graph(
                dot,
                0,
                1,
                show_amounts = self.show_amounts_on_edges_check_box.isChecked(),
                show_simplified= self.show_simplified_structure.isChecked()
            )

            print(dot.source)
            dot.render("tree", format="png", cleanup=True)
            dot.render("tree", format="svg", cleanup=True)