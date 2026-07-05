from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QCheckBox,
    QComboBox,
    QMessageBox,
)

from PySide6.QtGui import QDesktopServices

from PySide6.QtCore import QUrl

import networkx
import matplotlib.pyplot as plt

from ..evol import Evolution
from ..factory_loader import FactoryLoader
from ..graph_to_matrix import GraphToMatrix
from ..json_matrix_representation import MatrixJsonConvertor, BluePrintRepresentation
from ..util.file_util import FileUtil

#TODO: add hiding the recipe combobox (same for the link) selecting when the name of the input file changes (it could be done via signals)
#TODO: limit the vertical size of the combobox


class MainWindow(QMainWindow):
    """
    Main GUI windows of the GUI.

    Provides user with basic controls: imports factories, select which recipe wants to compute etc.
    """
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Factory layout creation")
        self.resize(500, 250)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """
        Setups the widgets of the main window.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.title_label = QLabel("Factory layout creation")

        self._setup_file_layout()
        self._setup_characteristic_vector_layout()
        self._factory_link_layout()

        self.main_layout.addStretch()

    def _setup_file_layout(self) -> None:
        """
        Setups widgets for part of the main window where user provides
        files which will be imported.
        """
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Recipes path...")

        self.recipe_import_button = QPushButton("Import recipes")

        self.main_layout.addWidget(self.title_label)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.recipe_import_button)

        #self.type_input = QLineEdit()
        #self.type_input.setPlaceholderText("Recipes")

        self.type_container = QWidget()

        self.type_input = QComboBox()
        self.type_input_compute_button = QPushButton("Compute recipe")

        recipe_layout = QHBoxLayout(self.type_container)
        recipe_layout.addWidget(self.type_input)
        recipe_layout.addWidget(self.type_input_compute_button)

        self.type_container.hide()

        self.main_layout.addLayout(file_layout)
        self.main_layout.addWidget(self.type_container)

    def _setup_characteristic_vector_layout(self) -> None:
        graph_characteristic_vector_layout = QHBoxLayout()

        self.show_amounts_on_edges_check_box = QCheckBox("Show amounts")

        self.show_simplified_structure = QCheckBox("Simplified structure")
        self.show_simplified_structure.setChecked(True)

        graph_characteristic_vector_layout.addWidget(self.show_amounts_on_edges_check_box)
        graph_characteristic_vector_layout.addWidget(self.show_simplified_structure)

        self.main_layout.addLayout(graph_characteristic_vector_layout)

    def _factory_link_layout(self) -> None:
        self.factory_link_container = QWidget()
        factory_link_layout = QHBoxLayout(self.factory_link_container)

        self.factory_link_button = QPushButton("Show factory")
        factory_link_layout.addWidget(self.factory_link_button)

        self.factory_link = None

        self.factory_link_container.hide()

        self.main_layout.addWidget(self.factory_link_container)

    def _open_factory_link(self) -> None:
        if self.factory_link is None:
            #TODO: better
            print("Factory link is empty")
            return

        QDesktopServices.openUrl(QUrl(self.factory_link))

    def _update_recipe_combobox(self, values: list[str]) -> None:
        self.type_input.clear()

        for value in values:
            self.type_input.addItem(value)

        self.type_container.show()

    def _connect_signals(self) -> None:
        self.recipe_import_button.clicked.connect(self._import_recipes)
        self.type_input_compute_button.clicked.connect(self._compute_recipe)
        self.factory_link_button.clicked.connect(self._open_factory_link)

    def _import_recipes(self) -> None:
        path = self.input_path.text()

        try:
            FileUtil.validate_json_file(path)
        except Exception as e:
            self._show_error(str(e))
            return

        recipe_names = FactoryLoader.load_recipe_names(path)

        self._update_recipe_combobox(recipe_names)

    def _compute_recipe(self) -> None:
        #TODO: create now thread for this action so the gui is still responsive

        path = self.input_path.text()
        recipe_type = self.type_input.currentText()

        FileUtil.create_output_dir()

        #TODO: whether file exists
        #TODO: resolve ignoring matrix after evolution
        factory_seed, _ = MainWindow.process_factory(
            path,
            recipe_type,
            show_amounts=self.show_amounts_on_edges_check_box.isChecked(),
            simplified_structure=self.show_simplified_structure.isChecked(),
            evolution_iteration=1,
            show_graph=True
        )

        if factory_seed is not None:
            self.factory_link = MainWindow.create_factory_url_link(factory_seed)

            self.factory_link_container.show()

    # TODO: find better place for this function than GUI
    @staticmethod
    def process_factory(
        path,
        recipe_type,
        show_amounts = True,
        simplified_structure = False,
        evolution_iteration = float("inf"),
        evolution_stagnation = 10,
        show_graph = False,
        create_presentation = False
    ):
        factories = FactoryLoader.load(path)

        root = FactoryLoader.get_dependency_tree(factories, recipe_type)

        if root is not None:
            graph = root.get_dependency_graph(
                show_amounts=show_amounts,
                show_simplified=simplified_structure
            )

            if show_graph:
                graph_layout = networkx.nx_pydot.graphviz_layout(graph, prog="dot")
                networkx.draw(graph, graph_layout, with_labels=False)

                node_labels = networkx.get_node_attributes(graph, "label")
                networkx.draw_networkx_labels(graph, graph_layout, node_labels)

                edge_labels = networkx.get_edge_attributes(graph, "label")
                networkx.draw_networkx_edge_labels(graph, graph_layout, edge_labels=edge_labels)

                plt.show()

                p = networkx.drawing.nx_pydot.to_pydot(graph)
                p.write_png("output/tree.png")
                p.write_svg("output/tree.svg")

            matrix = GraphToMatrix.convert_via_heuristics(graph, root)
            json_obj = MatrixJsonConvertor.encode(matrix)
            factory_seed = BluePrintRepresentation.encode(json_obj)

            #print(factory_seed)
            #print(Evolution.fitness(matrix))

            after_evolution = Evolution.evol(
                matrix,
                iteration=evolution_iteration,
                stagnation_break=evolution_stagnation,
                create_presentation=create_presentation
            )

            if create_presentation:
                return factory_seed, BluePrintRepresentation.encode(MatrixJsonConvertor.process_presentation(after_evolution))

            return factory_seed, BluePrintRepresentation.encode(MatrixJsonConvertor.encode(after_evolution))
        else:
            return None

    # TODO: find better place
    @staticmethod
    def create_factory_url_link(seed: str) -> str:
        return f"https://fbe.teoxoy.com/?source={seed}"

    def _show_error(self, error_message: str) -> None:
        pop_up = QMessageBox.critical(
            self,
            "Error",
            error_message
        )