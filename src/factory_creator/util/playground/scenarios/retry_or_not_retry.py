import csv
import random
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from ....evolution.plugin_configuration import PluginConfiguration
from ....export import URLCreator
from ....factory_processor import FactoryProcessor
from ....util.output import OutputLevel
from ..scenario import Scenario


RECIPE_NAME = "electric-mining-drill"
RECIPE_PATH = Path(__file__).resolve().parents[5] / "data" / "recipe.json"
OUTPUT_DIRECTORY = Path("output")
RESULT_CSV_PATH = OUTPUT_DIRECTORY / "retry-or-not-retry.csv"
EVOLUTION_ITERATIONS = 100
EVOLUTION_STAGNATION = EVOLUTION_ITERATIONS
RANDOM_SEED = 0
REPEATS = 5


@dataclass(frozen=True, slots=True)
class RetryBenchmarkResult:
    repeat: int
    seed: int
    retry_resizes: bool
    duration_seconds: float
    factory_url: str
    evolution_url: str
    error: str = ""


def process_electric_mining_drill(
    retry_topological_ordering_resizes: bool,
    repeat: int,
) -> RetryBenchmarkResult:
    seed = RANDOM_SEED + repeat
    random.seed(seed)
    label = "retry" if retry_topological_ordering_resizes else "no retry"

    mutations = PluginConfiguration.create_mutations(
        PluginConfiguration.discover_mutations(),
        retry_topological_ordering_resizes=(retry_topological_ordering_resizes),
    )
    fitness_aspects = PluginConfiguration.create_fitness_aspects(
        PluginConfiguration.discover_fitness_aspects()
    )

    started_at = perf_counter()
    try:
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
    except Exception as e:
        duration_seconds = perf_counter() - started_at
        print(f"[{label}] Failed after {duration_seconds:.6f} s: {e}")

        return RetryBenchmarkResult(
            repeat=repeat + 1,
            seed=seed,
            retry_resizes=retry_topological_ordering_resizes,
            duration_seconds=duration_seconds,
            factory_url="",
            evolution_url="",
            error=str(e),
        )
    
    duration_seconds = perf_counter() - started_at

    if result is None:
        raise RuntimeError(f"Recipe {RECIPE_NAME!r} was not found.")

    evolution_url = URLCreator.create_factory_url_link(result.evolution_seed)
    print(f"[{label}] Completed in {duration_seconds:.6f} s.")
    print(f"[{label}] Evolved factory: {evolution_url}")

    return RetryBenchmarkResult(
        repeat=repeat + 1,
        seed=seed,
        retry_resizes=retry_topological_ordering_resizes,
        duration_seconds=duration_seconds,
        factory_url=URLCreator.create_factory_url_link(result.factory_seed),
        evolution_url=evolution_url,
    )


def write_results_csv(
    results: list[RetryBenchmarkResult],
    output_path: Path = RESULT_CSV_PATH,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "repeat",
                "seed",
                "retry_resizes",
                "duration_seconds",
                "factory_url",
                "evolution_url",
                "error"
            ],
        )
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "repeat": result.repeat,
                    "seed": result.seed,
                    "retry_resizes": str(result.retry_resizes).lower(),
                    "duration_seconds": f"{result.duration_seconds:.9f}",
                    "factory_url": result.factory_url,
                    "evolution_url": result.evolution_url,
                    "error": result.error,
                }
            )

    return output_path


def run():
    results = []
    for repeat in range(REPEATS):
        for retry_resizes in (True, False):
            results.append(
                process_electric_mining_drill(
                    retry_topological_ordering_resizes=retry_resizes,
                    repeat=repeat,
                )
            )

    result_csv_path = write_results_csv(results, RESULT_CSV_PATH)
    print(f"CSV saved to {result_csv_path.resolve()}.")


SCENARIO = Scenario(
    name="retry-or-not-retry",
    description=(
        "Compare electric-mining-drill evolution with and without retrying "
        "failed topological orderings on larger grids."
    ),
    run=run,
)
