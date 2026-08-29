import random
from pathlib import Path
from time import perf_counter

from ....evolution.plugin_configuration import PluginConfiguration
from ....export import URLCreator
from ....factory_processor import FactoryProcessor, FactoryProcessingResult
from ....util.output import OutputLevel
from ..scenario import Scenario


RECIPE_NAME = "electric-mining-drill"
RECIPE_PATH = Path(__file__).resolve().parents[5] / "data" / "recipe.json"
OUTPUT_DIRECTORY = Path("output")
EVOLUTION_ITERATIONS = 100
EVOLUTION_STAGNATION = 100 #we do not want to end early
RANDOM_SEED = 0
REPEATS = 5


def process_electric_mining_drill(
    retry_topological_ordering_resizes: bool,
) -> FactoryProcessingResult:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    #random.seed(RANDOM_SEED)
    label = "retry" if retry_topological_ordering_resizes else "no retry"

    mutations = PluginConfiguration.create_mutations(
        PluginConfiguration.discover_mutations(),
        retry_topological_ordering_resizes=(retry_topological_ordering_resizes),
    )
    fitness_aspects = PluginConfiguration.create_fitness_aspects(
        PluginConfiguration.discover_fitness_aspects()
    )

    started_at = perf_counter()
    result = FactoryProcessor.process_factory(
        str(RECIPE_PATH),
        RECIPE_NAME,
        mutations=mutations,
        fitness_aspects=fitness_aspects,
        evolution_iteration=EVOLUTION_ITERATIONS,
        evolution_stagnation=EVOLUTION_STAGNATION,
        output_level=OutputLevel.LOW,
        report_method=lambda message: print(f"[{label}] {message}"),
    )
    duration_seconds = perf_counter() - started_at

    if result is None:
        raise RuntimeError(f"Recipe {RECIPE_NAME!r} was not found.")

    print(f"[{label}] Completed in {duration_seconds:.6f} s.")
    print(
        f"[{label}] Evolved factory: "
        f"{URLCreator.create_factory_url_link(result.evolution_seed)}"
    )

    return result


def run():
    for _ in range(REPEATS):
        process_electric_mining_drill(
            retry_topological_ordering_resizes=True,
        )

    for _ in range(REPEATS):
        process_electric_mining_drill(
            retry_topological_ordering_resizes=False,
        )


SCENARIO = Scenario(
    name="retry-or-not-retry",
    description=(
        "Compare electric-mining-drill evolution with and without retrying "
        "failed topological orderings on larger grids."
    ),
    run=run,
)
