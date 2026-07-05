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
    QTextEdit,
    QSpinBox,
    QToolButton,
)

from PySide6.QtGui import QDesktopServices

from PySide6.QtCore import QUrl, QObject, QThread, Signal, Slot, Qt

from ..factory_loader import FactoryLoader
from ..factory_graph_renderer import FactoryGraphRenderer
from ..factory_processor import FactoryProcessor
from ..util.file_util import FileUtil


class ComputeRecipeWorker(QObject):
    result = Signal(object)
    error = Signal(str)
    message = Signal(str)
    finished = Signal()

    def __init__(
        self,
        path: str,
        recipe_type: str,
        show_amounts: bool,
        simplified_structure: bool,
        evolution_iterations: int,
        evolution_stagnation: int,
    ) -> None:
        super().__init__()
        self.path = path
        self.recipe_type = recipe_type
        self.show_amounts = show_amounts
        self.simplified_structure = simplified_structure
        self.evolution_iterations = evolution_iterations
        self.evolution_stagnation = evolution_stagnation

    @Slot()
    def run(self) -> None:
        try:
            FileUtil.create_output_dir()

            self.message.emit("Computing factory...")
            self.result.emit(FactoryProcessor.process_factory(
                self.path,
                self.recipe_type,
                show_amounts=self.show_amounts,
                simplified_structure=self.simplified_structure,
                evolution_iteration=self.evolution_iterations,
                evolution_stagnation=self.evolution_stagnation,
                report_method=self.message.emit
            ))
            self.message.emit("Factory computation finished.")
        except Exception as e:
            self.message.emit("Factory computation failed.")
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    COMBOBOX_ITEMS = 8

    """
    Main GUI windows of the GUI.

    Provides user with basic controls: imports factories, select which recipe wants to compute etc.
    """
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Factory layout creation")
        self.resize(500, 250)

        self.compute_thread = None
        self.compute_worker = None
        self.show_graph_after_compute = False

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
        self._setup_messages_layout()

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

        self.type_container = QWidget()

        self.type_input = QComboBox()
        # Does not work at Linux!!!
        self.type_input.setMaxVisibleItems(MainWindow.COMBOBOX_ITEMS)

        self.type_input_compute_button = QPushButton("Compute recipe")

        recipe_layout = QHBoxLayout(self.type_container)
        recipe_layout.addWidget(self.type_input)
        recipe_layout.addWidget(self.type_input_compute_button)

        self.type_container.hide()

        self.main_layout.addLayout(file_layout)
        self.main_layout.addWidget(self.type_container)

    def _setup_characteristic_vector_layout(self) -> None:
        self.options_toggle_button = QToolButton()
        self.options_toggle_button.setText("Options")
        self.options_toggle_button.setCheckable(True)
        self.options_toggle_button.setChecked(True)
        self.options_toggle_button.setArrowType(Qt.DownArrow)
        self.options_toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.options_toggle_button.setAutoRaise(True)

        self.options_container = QWidget()
        options_layout = QVBoxLayout(self.options_container)

        graph_characteristic_vector_layout = QHBoxLayout()

        self.show_amounts_on_edges_check_box = QCheckBox("Show amounts")

        self.show_simplified_structure = QCheckBox("Simplified structure")
        self.show_simplified_structure.setChecked(False)

        self.show_graph_check_box = QCheckBox("Show graph")

        graph_characteristic_vector_layout.addWidget(self.show_amounts_on_edges_check_box)
        graph_characteristic_vector_layout.addWidget(self.show_simplified_structure)
        graph_characteristic_vector_layout.addWidget(self.show_graph_check_box)

        evolution_parameters_layout = QHBoxLayout()

        self.evolution_iterations_input = QSpinBox()
        self.evolution_iterations_input.setRange(1, 1_000_000)
        self.evolution_iterations_input.setValue(1)

        self.evolution_stagnation_input = QSpinBox()
        self.evolution_stagnation_input.setRange(1, 1_000_000)
        self.evolution_stagnation_input.setValue(10)

        evolution_parameters_layout.addWidget(QLabel("Iterations"))
        evolution_parameters_layout.addWidget(self.evolution_iterations_input)
        evolution_parameters_layout.addWidget(QLabel("Stagnation threshold"))
        evolution_parameters_layout.addWidget(self.evolution_stagnation_input)

        options_layout.addLayout(graph_characteristic_vector_layout)
        options_layout.addLayout(evolution_parameters_layout)

        self.main_layout.addWidget(self.options_toggle_button)
        self.main_layout.addWidget(self.options_container)

    def _factory_link_layout(self) -> None:
        self.factory_link_container = QWidget()
        factory_link_layout = QHBoxLayout(self.factory_link_container)

        self.factory_link_button = QPushButton("Show factory")
        factory_link_layout.addWidget(self.factory_link_button)

        self.evolved_factory_link_button = QPushButton("Show evolved factory")
        factory_link_layout.addWidget(self.evolved_factory_link_button)

        self.factory_link = None
        self.evolved_factory_link = None

        self.factory_link_container.hide()

        self.main_layout.addWidget(self.factory_link_container)

    def _setup_messages_layout(self) -> None:
        self.worker_messages = QTextEdit()
        self.worker_messages.setReadOnly(True)
        self.worker_messages.setPlaceholderText("Worker messages...")
        self.worker_messages.setFixedHeight(180)

        self.main_layout.addWidget(self.worker_messages)

    def _open_factory_link(self) -> None:
        self._open_link(self.factory_link, "Factory link is empty")

    def _open_evolved_factory_link(self) -> None:
        self._open_link(self.evolved_factory_link, "Evolved factory link is empty")

    def _open_link(self, link: str | None, error_message: str) -> None:
        if link is None:
            self._show_error(error_message)
            return

        QDesktopServices.openUrl(QUrl(link))

    def _update_recipe_combobox(self, values: list[str]) -> None:
        self.type_input.clear()

        for value in values:
            self.type_input.addItem(value)

        self.type_container.show()

    def _hide_file_dependent_widgets(self) -> None:
        self.type_container.hide()
        self.factory_link = None
        self.evolved_factory_link = None
        self.factory_link_container.hide()

    def _connect_signals(self) -> None:
        self.input_path.textChanged.connect(self._hide_file_dependent_widgets)
        self.recipe_import_button.clicked.connect(self._import_recipes)
        self.type_input_compute_button.clicked.connect(self._compute_recipe)
        self.factory_link_button.clicked.connect(self._open_factory_link)
        self.evolved_factory_link_button.clicked.connect(self._open_evolved_factory_link)
        self.options_toggle_button.toggled.connect(self._toggle_options)
        self.show_simplified_structure.toggled.connect(self._show_simplified_structure_info)

    def _toggle_options(self, checked: bool) -> None:
        self.options_container.setVisible(checked)
        self.options_toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

    def _show_simplified_structure_info(self, checked: bool) -> None:
        if checked:
            QMessageBox.information(
                self,
                "Simplified structure",
                "Simplified structure changes the backend dependency graph. "
                "That also changes the generated grid, matrix, and evolution result."
            )

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
        path = self.input_path.text()
        recipe_type = self.type_input.currentText()

        self.type_input_compute_button.setEnabled(False)
        self.factory_link_button.setEnabled(False)
        self.evolved_factory_link_button.setEnabled(False)
        self.factory_link = None
        self.evolved_factory_link = None
        self.factory_link_container.hide()
        self.show_graph_after_compute = self.show_graph_check_box.isChecked()
        self.worker_messages.clear()

        self.compute_thread = QThread()
        self.compute_worker = ComputeRecipeWorker(
            path,
            recipe_type,
            self.show_amounts_on_edges_check_box.isChecked(),
            self.show_simplified_structure.isChecked(),
            self.evolution_iterations_input.value(),
            self.evolution_stagnation_input.value(),
        )
        self.compute_worker.moveToThread(self.compute_thread)

        self.compute_thread.started.connect(self.compute_worker.run)
        self.compute_worker.result.connect(self._handle_compute_result)
        self.compute_worker.error.connect(self._show_error)
        self.compute_worker.error.connect(self._append_worker_message)
        self.compute_worker.message.connect(self._append_worker_message)
        self.compute_worker.finished.connect(self.compute_thread.quit)
        self.compute_worker.finished.connect(self.compute_worker.deleteLater)
        self.compute_thread.finished.connect(self.compute_thread.deleteLater)
        self.compute_thread.finished.connect(self._cleanup_compute_thread)

        self.compute_thread.start()

    @Slot(object)
    def _handle_compute_result(self, result) -> None:
        if result is None:
            return

        if result.factory_seed is not None:
            self.factory_link = MainWindow.create_factory_url_link(result.factory_seed)
            self.evolved_factory_link = MainWindow.create_factory_url_link(result.evolution_seed)
            self.factory_link_container.show()
            self._append_worker_message("Factory links are ready.")

        if self.show_graph_after_compute:
            FactoryGraphRenderer.show_graph(result.dependency_graph)

    @Slot(str)
    def _append_worker_message(self, message: str) -> None:
        self.worker_messages.append(message)

    @Slot()
    def _cleanup_compute_thread(self) -> None:
        self.type_input_compute_button.setEnabled(True)
        self.factory_link_button.setEnabled(True)
        self.evolved_factory_link_button.setEnabled(True)
        self.compute_thread = None
        self.compute_worker = None

    @staticmethod
    def create_factory_url_link(seed: str) -> str:
        return f"https://fbe.teoxoy.com/?source={seed}"

    def _show_error(self, error_message: str) -> None:
        pop_up = QMessageBox.critical(
            self,
            "Error",
            error_message
        )
