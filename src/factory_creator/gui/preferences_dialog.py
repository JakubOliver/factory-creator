from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
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

    def _update_selected_level(self, value):
        level = OutputLevel(value)
        self.selected_level_label.setText(f"Selected: {level.name.title()}")
