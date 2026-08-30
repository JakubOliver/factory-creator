from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from ..factory_processor import FactoryProcessor
from ..util.file_util import FileUtil
from ..util.output import OutputLevel
from ..evolution.fitness_aspects import FitnessAspect
from ..evolution.mutations.mutation import Mutation
from ..util.cancellation import ComputationCancelled


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
        mutations: list[Mutation],
        fitness_aspects: list[FitnessAspect],
        output_level: OutputLevel = OutputLevel.MEDIUM,
        evolution_caching: bool = True,
        output_efficiency: float = 1.0,
        initial_grid_resize_retries: int = 3,
    ) -> None:
        """
        Store the recipe path, selected recipe, graph options, and evolution limits.

        :param path: Path to the JSON recipe file.
        :param recipe_type: Name of the recipe to compute.
        :param show_amounts: Whether dependency graph edges should include amounts.
        :param simplified_structure: Whether to use the simplified dependency graph.
        :param evolution_iterations: Maximum number of evolution iterations.
        :param evolution_stagnation: Stagnation threshold for stopping evolution.
        :param output_efficiency: Requested utilization of the root factory.
        :param initial_grid_resize_retries: Maximum number of larger-grid retries
            while building the initial grid.
        """
        super().__init__()
        self.path = path
        self.recipe_type = recipe_type
        self.show_amounts = show_amounts
        self.simplified_structure = simplified_structure
        self.output_efficiency = output_efficiency
        self.evolution_iterations = evolution_iterations
        self.evolution_stagnation = evolution_stagnation
        self.output_level = output_level
        self.evolution_caching = evolution_caching
        self.initial_grid_resize_retries = initial_grid_resize_retries
        self.mutations = mutations
        self.fitness_aspects = fitness_aspects
        self._stop_event = Event()

    def request_stop(self) -> None:
        self._stop_event.set()

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
                show_amounts = self.show_amounts,
                simplified_structure = self.simplified_structure,
                output_efficiency = self.output_efficiency,
                evolution_iteration = self.evolution_iterations,
                evolution_stagnation = self.evolution_stagnation,
                report_method = self.message.emit,
                output_level = self.output_level,
                evolution_caching = self.evolution_caching,
                mutations = self.mutations,
                fitness_aspects = self.fitness_aspects,
                initial_grid_resize_retries=self.initial_grid_resize_retries,
                stop_requested=self._stop_event.is_set,
            ))
            
            self.message.emit("Factory computation finished.")
        except ComputationCancelled:
            self.message.emit("Factory computation cancelled.")
        except Exception as e:
            self.message.emit("Factory computation failed.")
            self.error.emit(str(e))
        finally:
            self.finished.emit()
