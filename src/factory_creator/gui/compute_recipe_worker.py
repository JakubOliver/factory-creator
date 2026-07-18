from PySide6.QtCore import QObject, Signal, Slot

from ..factory_processor import FactoryProcessor
from ..util.file_util import FileUtil
from ..util.output import OutputLevel


class ComputeRecipeWorker(QObject):
    """
    Runs factory computation in a worker thread and reports progress through Qt signals.
    """

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
        output_level: OutputLevel = OutputLevel.MEDIUM,
        evolution_caching: bool = True,
    ) -> None:
        """
        Store the recipe path, selected recipe, graph options, and evolution limits.

        :param path: Path to the JSON recipe file.
        :param recipe_type: Name of the recipe to compute.
        :param show_amounts: Whether dependency graph edges should include amounts.
        :param simplified_structure: Whether to use the simplified dependency graph.
        :param evolution_iterations: Maximum number of evolution iterations.
        :param evolution_stagnation: Stagnation threshold for stopping evolution.
        """
        super().__init__()
        self.path = path
        self.recipe_type = recipe_type
        self.show_amounts = show_amounts
        self.simplified_structure = simplified_structure
        self.evolution_iterations = evolution_iterations
        self.evolution_stagnation = evolution_stagnation
        self.output_level = output_level
        self.evolution_caching = evolution_caching

    @Slot()
    def run(self) -> None:
        """
        Execute the factory processing workflow and emit result or error signals.
        """
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
                report_method=self.message.emit,
                output_level=self.output_level,
                evolution_caching=self.evolution_caching,
            ))
            self.message.emit("Factory computation finished.")
        except Exception as e:
            self.message.emit("Factory computation failed.")
            self.error.emit(str(e))
        finally:
            self.finished.emit()
