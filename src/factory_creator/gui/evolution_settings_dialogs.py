from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..evolution.plugin_configuration import (
    FitnessAspectConfiguration,
    MutationConfiguration,
)
from ..util.reflection import DiscoveredClass


# Maximum value supported by QSpinBox's signed integer.
MAX_GENERATION = 2_147_483_647


class _SettingsListDialog(QDialog):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 420)
        self.layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        scroll.setWidget(self.content)
        self.layout.addWidget(scroll)

    def _add_buttons(self) -> None:
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)


class MutationsDialog(_SettingsListDialog):
    def __init__(self, discovered, saved, parent=None) -> None:
        super().__init__("Mutations", parent)
        self.rows = {}
        for column, title in enumerate(("Enabled", "Mutation", "Lower bound", "Upper bound")):
            self.grid.addWidget(QLabel(title), 0, column)

        for row, item in enumerate(discovered, 1):
            instance = item.create()

            config = saved.get(item.identifier)

            enabled = QCheckBox()
            enabled.setChecked(config.enabled if config else True)

            start = QSpinBox()
            start.setRange(0, MAX_GENERATION)
            start.setValue(config.start_generation if config else int(instance.start_generation))

            finite_end = config.end_generation if config else instance.end_generation

            end = QSpinBox()
            end.setRange(0, MAX_GENERATION)

            unlimited = QCheckBox("∞")
            is_unlimited = finite_end == float("inf")
            unlimited.setChecked(is_unlimited)

            end.setEnabled(not is_unlimited)

            if not is_unlimited:
                end.setValue(int(finite_end))

            unlimited.toggled.connect(lambda checked, widget=end: widget.setEnabled(not checked))

            end_container = QWidget()
            end_layout = QHBoxLayout(end_container)
            end_layout.setContentsMargins(0, 0, 0, 0)
            end_layout.addWidget(end)
            end_layout.addWidget(unlimited)

            self.grid.addWidget(enabled, row, 0)
            self.grid.addWidget(QLabel(item.display_name), row, 1)
            self.grid.addWidget(start, row, 2)
            self.grid.addWidget(end_container, row, 3)

            self.rows[item.identifier] = (enabled, start, end, unlimited)

        self.grid.setRowStretch(len(discovered) + 1, 1)
        self._add_buttons()

    def configurations(self) -> dict[str, MutationConfiguration]:
        result = {}

        for identifier, (enabled, start, end, unlimited) in self.rows.items():
            result[identifier] = MutationConfiguration(
                identifier,
                enabled.isChecked(),
                start.value(),
                float("inf") if unlimited.isChecked() else end.value(),
            )

        return result


class FitnessesDialog(_SettingsListDialog):
    def __init__(self, discovered, saved, parent=None) -> None:
        super().__init__("Fitness aspects", parent)
        self.rows = {}

        for column, title in enumerate(("Enabled", "Fitness aspect", "Weight")):
            self.grid.addWidget(QLabel(title), 0, column)

        for row, item in enumerate(discovered, 1):
            instance = item.create()

            config = saved.get(item.identifier)

            enabled = QCheckBox()
            enabled.setChecked(config.enabled if config else True)

            weight = QDoubleSpinBox()
            weight.setDecimals(6)
            weight.setRange(-1_000_000_000, 1_000_000_000)
            weight.setValue(float(config.weight if config else instance.weight))

            self.grid.addWidget(enabled, row, 0)
            self.grid.addWidget(QLabel(item.display_name), row, 1)
            self.grid.addWidget(weight, row, 2)

            self.rows[item.identifier] = (enabled, weight)

        self.grid.setRowStretch(len(discovered) + 1, 1)
        self._add_buttons()

    def configurations(self) -> dict[str, FitnessAspectConfiguration]:
        return {
            identifier: FitnessAspectConfiguration(
                identifier, enabled.isChecked(), weight.value()
            )
            for identifier, (enabled, weight) in self.rows.items()
        }
