from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class RecipeOptionsWidget(QWidget):
    """
    Collapsible widget containing graph display and evolution algorithm options.
    """

    MIN_ITERATIONS = 1
    MAX_ITERATIONS = 1_000_000
    DEFAULT_ITERATIONS = 10

    MIN_STAGNATION = 1
    MAX_STAGNATION = 1_000_000
    DEFAULT_STAGNATION = 10

    def __init__(self) -> None:
        """
        Build the options controls and connect local widget signals.
        """
        super().__init__()

        layout = QVBoxLayout(self)

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
        self.evolution_iterations_input.setRange(self.MIN_ITERATIONS, self.MAX_ITERATIONS)
        self.evolution_iterations_input.setValue(self.DEFAULT_ITERATIONS)

        self.evolution_stagnation_input = QSpinBox()
        self.evolution_stagnation_input.setRange(self.MIN_STAGNATION, self.MAX_STAGNATION)
        self.evolution_stagnation_input.setValue(self.DEFAULT_STAGNATION)

        evolution_parameters_layout.addWidget(QLabel("Iterations"))
        evolution_parameters_layout.addWidget(self.evolution_iterations_input)
        evolution_parameters_layout.addWidget(QLabel("Stagnation threshold"))
        evolution_parameters_layout.addWidget(self.evolution_stagnation_input)

        options_layout.addLayout(graph_characteristic_vector_layout)
        options_layout.addLayout(evolution_parameters_layout)

        layout.addWidget(self.options_toggle_button)
        layout.addWidget(self.options_container)

        self.options_toggle_button.toggled.connect(self._toggle_options)
        self.show_simplified_structure.toggled.connect(self._show_simplified_structure_info)

    def show_amounts(self) -> bool:
        """
        Return whether graph edges should include ingredient amounts.

        :return: Whether amounts should be shown on graph edges.
        """
        return self.show_amounts_on_edges_check_box.isChecked()

    def simplified_structure(self) -> bool:
        """
        Return whether the backend should use simplified dependency structure.

        :return: Whether simplified graph structure is enabled.
        """
        return self.show_simplified_structure.isChecked()

    def show_graph(self) -> bool:
        """
        Return whether the dependency graph should be shown after computation.

        :return: Whether the graph should be rendered after computation.
        """
        return self.show_graph_check_box.isChecked()

    def evolution_iterations(self) -> int:
        """
        Return the configured maximum evolution iteration count.

        :return: Maximum number of evolution iterations.
        """
        return self.evolution_iterations_input.value()

    def evolution_stagnation(self) -> int:
        """
        Return the configured stagnation threshold for evolution.

        :return: Number of stagnant generations allowed before stopping.
        """
        return self.evolution_stagnation_input.value()

    def _toggle_options(self, checked: bool) -> None:
        """
        Show or hide the options container and update the disclosure arrow.

        :param checked: Whether the options panel should be expanded.
        """
        self.options_container.setVisible(checked)
        self.options_toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

    def _show_simplified_structure_info(self, checked: bool) -> None:
        """
        Warn users that simplified structure changes backend computation.

        :param checked: Whether simplified structure has just been enabled.
        """
        if checked:
            QMessageBox.information(
                self,
                "Simplified structure",
                "Simplified structure changes the backend dependency graph. "
                "That also changes the generated grid, matrix, and evolution result."
            )
