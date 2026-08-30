from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
)

from ..util.output import OutputLevel
from ..export.url_creator import URLCreator


class PreferencesDialog(QDialog):
    def __init__(
        self,
        output_level: OutputLevel,
        factory_url: str = URLCreator.BASE_URL,
        parent=None,
        evolution_caching: bool = True,
        mutation_plugins_path: str = "",
        fitness_plugins_path: str = "",
        retry_topological_ordering_resizes: bool = False,
        initial_grid_resize_retries: int = 3,
        mutation_grid_resize_retries: int = 3,
    ):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Report detail"))

        self.output_level_slider = QSlider(Qt.Horizontal)
        self.output_level_slider.setRange(OutputLevel.LOW, OutputLevel.HIGH)
        self.output_level_slider.setSingleStep(1)
        self.output_level_slider.setPageStep(1)
        self.output_level_slider.setTickInterval(1)
        self.output_level_slider.setTickPosition(QSlider.TicksBelow)
        self.output_level_slider.setValue(output_level)
        layout.addWidget(self.output_level_slider)

        labels_layout = QHBoxLayout()
        for level in OutputLevel:
            label = QLabel(level.name.title())
            label.setAlignment(Qt.AlignCenter)
            labels_layout.addWidget(label, 1)
        layout.addLayout(labels_layout)

        self.selected_level_label = QLabel()
        self.selected_level_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_level_label)
        self.output_level_slider.valueChanged.connect(self._update_selected_level)
        self._update_selected_level(self.output_level_slider.value())

        layout.addWidget(QLabel("Factory viewer URL"))
        self.factory_url_input = QLineEdit(factory_url)
        self.factory_url_input.setPlaceholderText(URLCreator.BASE_URL)
        layout.addWidget(self.factory_url_input)

        self.evolution_caching_checkbox = QCheckBox("Cache evolution fitness results")
        self.evolution_caching_checkbox.setChecked(evolution_caching)
        self.evolution_caching_checkbox.setToolTip(
            "Reuse fitness results for layouts already evaluated during an evolution run."
        )
        layout.addWidget(self.evolution_caching_checkbox)

        initial_resize_layout = QHBoxLayout()
        initial_resize_layout.addWidget(QLabel("Initial grid resize retries"))
        self.initial_grid_resize_retries_input = QSpinBox()
        self.initial_grid_resize_retries_input.setRange(0, 100)
        self.initial_grid_resize_retries_input.setValue(initial_grid_resize_retries)
        self.initial_grid_resize_retries_input.setToolTip(
            "Maximum number of larger-grid retries while building the initial grid."
        )
        initial_resize_layout.addWidget(self.initial_grid_resize_retries_input)
        layout.addLayout(initial_resize_layout)

        mutation_resize_layout = QHBoxLayout()
        self.retry_topological_ordering_resizes_checkbox = QCheckBox(
            "Retry mutation topological orderings"
        )
        self.retry_topological_ordering_resizes_checkbox.setChecked(
            retry_topological_ordering_resizes
        )
        self.retry_topological_ordering_resizes_checkbox.setToolTip(
            "Retry failed topological orderings on progressively larger grids "
            "during evolution."
        )
        mutation_resize_layout.addWidget(
            self.retry_topological_ordering_resizes_checkbox
        )
        mutation_resize_layout.addWidget(QLabel("Resize retries"))
        self.mutation_grid_resize_retries_input = QSpinBox()
        self.mutation_grid_resize_retries_input.setRange(0, 100)
        self.mutation_grid_resize_retries_input.setValue(
            mutation_grid_resize_retries
        )
        self.mutation_grid_resize_retries_input.setToolTip(
            "Maximum number of larger-grid retries for each topological mutation."
        )
        self.mutation_grid_resize_retries_input.setEnabled(
            retry_topological_ordering_resizes
        )
        self.retry_topological_ordering_resizes_checkbox.toggled.connect(
            self.mutation_grid_resize_retries_input.setEnabled
        )
        mutation_resize_layout.addWidget(self.mutation_grid_resize_retries_input)
        layout.addLayout(mutation_resize_layout)

        self.mutation_plugins_input = self._add_directory_input(
            layout, "User mutations directory", mutation_plugins_path
        )
        self.fitness_plugins_input = self._add_directory_input(
            layout, "User fitness aspects directory", fitness_plugins_path
        )
        warning = QLabel(
            "Plugin files will be executed as Python code without any sandboxing. Only use trusted plugins."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def output_level(self):
        return OutputLevel(self.output_level_slider.value())

    def factory_url(self):
        url = self.factory_url_input.text().strip()
        return url or URLCreator.BASE_URL

    def evolution_caching(self) -> bool:
        return self.evolution_caching_checkbox.isChecked()

    def retry_topological_ordering_resizes(self) -> bool:
        return self.retry_topological_ordering_resizes_checkbox.isChecked()

    def initial_grid_resize_retries(self) -> int:
        return self.initial_grid_resize_retries_input.value()

    def mutation_grid_resize_retries(self) -> int:
        return self.mutation_grid_resize_retries_input.value()

    def mutation_plugins_path(self) -> str:
        return self.mutation_plugins_input.text().strip()

    def fitness_plugins_path(self) -> str:
        return self.fitness_plugins_input.text().strip()

    def _add_directory_input(self, layout, label: str, value: str) -> QLineEdit:
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        path_input = QLineEdit(value)
        browse = QPushButton("Browse...")
        browse.clicked.connect(lambda: self._choose_directory(path_input))
        row.addWidget(path_input)
        row.addWidget(browse)
        layout.addLayout(row)
        return path_input

    def _choose_directory(self, path_input: QLineEdit) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select plugin directory")
        if directory:
            path_input.setText(directory)

    def _update_selected_level(self, value):
        level = OutputLevel(value)
        self.selected_level_label.setText(f"Selected: {level.name.title()}")
