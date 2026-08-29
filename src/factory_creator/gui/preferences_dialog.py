from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
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
    ):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(320)

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

        self.retry_topological_ordering_resizes_checkbox = QCheckBox(
            "Retry topological orderings with larger grids"
        )
        self.retry_topological_ordering_resizes_checkbox.setChecked(
            retry_topological_ordering_resizes
        )
        self.retry_topological_ordering_resizes_checkbox.setToolTip(
            "Retry failed topological orderings on progressively larger grids "
            "during evolution."
        )
        layout.addWidget(self.retry_topological_ordering_resizes_checkbox)

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
