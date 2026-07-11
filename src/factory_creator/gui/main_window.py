import os

from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..factory_loader import FactoryLoader
from ..export.url_creator import URLCreator
from ..util.file_util import FileUtil
from .compute_recipe_worker import ComputeRecipeWorker
from .factory_result_widget import FactoryResultWidget
from .recipe_options_widget import RecipeOptionsWidget


class MainWindow(QMainWindow):
    """
    Main GUI windows of the GUI.

    Provides user with basic controls: imports factories, select which recipe wants to compute etc.
    """
    COMBOBOX_ITEMS = 8

    def __init__(self, use_embedded_browser: bool = True) -> None:
        """
        Initialize the main window and choose embedded or external result display mode.

        :param use_embedded_browser: Whether result links should open in embedded tabs.
        """
        super().__init__()

        self.setWindowTitle("Factory layout creation")
        self.resize(500, 320)

        self.use_embedded_browser = use_embedded_browser
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

        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        self.menu_container = QWidget()
        self.menu_container.setMaximumWidth(430)
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.main_layout.addWidget(self.menu_container, 0)

        self.title_label = QLabel("Factory layout creation")

        self._setup_file_layout()
        self._setup_options_layout()
        self._setup_result_layout()
        self._setup_messages_layout()

        if not self.use_embedded_browser:
            self.menu_layout.addStretch()

    def _setup_file_layout(self) -> None:
        """
        Setups widgets for part of the main window where user provides
        files which will be imported.
        """
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Recipes path...")

        self.browse_recipes_button = QPushButton("Browse...")
        self.recipe_import_button = QPushButton("Import recipes")

        self.menu_layout.addWidget(self.title_label)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.browse_recipes_button)
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

        self.menu_layout.addLayout(file_layout)
        self.menu_layout.addWidget(self.type_container)

    def _setup_options_layout(self) -> None:
        """
        Create and add the collapsible recipe options widget.
        """
        self.options_widget = RecipeOptionsWidget()
        self.menu_layout.addWidget(self.options_widget)

    def _setup_result_layout(self) -> None:
        """
        Create and place the factory result display widget.
        """
        self.factory_result_widget = FactoryResultWidget(self.use_embedded_browser)

        if self.use_embedded_browser:
            self.main_layout.addWidget(self.factory_result_widget, 1)
        else:
            self.menu_layout.addWidget(self.factory_result_widget)

    def _setup_messages_layout(self) -> None:
        """
        Create the worker message log and size it for the selected layout mode.
        """
        self.worker_messages = QTextEdit()
        self.worker_messages.setReadOnly(True)
        self.worker_messages.setPlaceholderText("Worker messages...")

        if self.use_embedded_browser:
            self.worker_messages.setMinimumHeight(180)
            self.worker_messages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.menu_layout.addWidget(self.worker_messages, 1)
        else:
            self.worker_messages.setFixedHeight(180)
            self.menu_layout.addWidget(self.worker_messages)

    def _update_recipe_combobox(self, values: list[str]) -> None:
        """
        Populate recipe choices and show the recipe selection controls.

        :param values: Recipe names loaded from the selected input file.
        """
        self.type_input.clear()

        for value in values:
            self.type_input.addItem(value)

        self.type_container.show()

    def _hide_file_dependent_widgets(self) -> None:
        """
        Hide recipe-specific controls and clear previous results after the file path changes.
        """
        self.type_container.hide()
        self.factory_result_widget.clear()

    def _connect_signals(self) -> None:
        """
        Connect user-interface events to their handlers.
        """
        self.input_path.textChanged.connect(self._hide_file_dependent_widgets)
        self.browse_recipes_button.clicked.connect(self._choose_recipe_file)
        self.recipe_import_button.clicked.connect(self._import_recipes)
        self.type_input_compute_button.clicked.connect(self._compute_recipe)

    def _choose_recipe_file(self) -> None:
        """
        Open a file chooser and place the selected JSON path into the path field.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select recipes file",
            "",
            "JSON files (*.json);;All files (*)"
        )

        if path:
            self.input_path.setText(os.path.relpath(path))

    def _import_recipes(self) -> None:
        """
        Validate the selected file and load available recipe names into the dropdown.
        """
        path = self.input_path.text()

        try:
            FileUtil.validate_json_file(path)
        except Exception as e:
            self._show_error(str(e))
            return

        recipe_names = FactoryLoader.load_recipe_names(path)

        self._update_recipe_combobox(recipe_names)

    def _compute_recipe(self) -> None:
        """
        Start recipe computation in a background thread using the current options.
        """
        path = self.input_path.text()
        recipe_type = self.type_input.currentText()

        self.type_input_compute_button.setEnabled(False)
        self.factory_result_widget.set_controls_enabled(False)
        self.show_graph_after_compute = self.options_widget.show_graph()
        self.worker_messages.clear()

        self.compute_thread = QThread()
        self.compute_worker = ComputeRecipeWorker(
            path,
            recipe_type,
            self.options_widget.show_amounts(),
            self.options_widget.simplified_structure(),
            self.options_widget.evolution_iterations(),
            self.options_widget.evolution_stagnation(),
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
        """
        Display factory links and optionally render the dependency graph after computation.

        :param result: Factory processing result emitted by the worker.
        """
        if result is None:
            return

        if result.factory_seed is not None:
            self.factory_result_widget.show_results(
                URLCreator.create_factory_url_link(result.factory_seed),
                URLCreator.create_factory_url_link(result.evolution_seed)
            )
            self._append_worker_message("Factory results are ready.")

            if self.use_embedded_browser:
                self.resize(max(self.width(), 1300), max(self.height(), 760))

        if self.show_graph_after_compute:
            self._show_dependency_graph(result.dependency_graph)

    @Slot(str)
    def _append_worker_message(self, message: str) -> None:
        """
        Append a worker progress message to the GUI log.

        :param message: Message emitted by the compute worker.
        """
        self.worker_messages.append(message)

    @Slot()
    def _cleanup_compute_thread(self) -> None:
        """
        Restore controls and release worker references when the thread finishes.
        """
        self.type_input_compute_button.setEnabled(True)
        self.factory_result_widget.set_controls_enabled(True)
        self.compute_thread = None
        self.compute_worker = None

    def _show_dependency_graph(self, graph) -> None:
        """
        Render the dependency graph if the optional Graphviz renderer is available.

        :param graph: Dependency graph to display.
        """
        try:
            from ..export.factory_graph_renderer import FactoryGraphRenderer
        except ImportError:
            self._show_error(
                "Graph rendering is unavailable. Install the optional graph rendering "
                "dependencies and the Graphviz system package."
            )
            return

        FactoryGraphRenderer.show_graph(graph)

    def _show_error(self, error_message: str) -> None:
        """
        Show an error message in a modal popup.

        :param error_message: Error text displayed to the user.
        """
        QMessageBox.critical(
            self,
            "Error",
            error_message
        )
