import csv
import random
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from ....evolution.plugin_configuration import PluginConfiguration
from ....export import URLCreator
from ....factory_processor import FactoryProcessor
from ....util.output import OutputLevel
from ..scenario import Scenario, ScenarioResult


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
    factory_url: str | None
    evolution_url: str | None
    error: str | None = None


def process_electric_mining_drill(
    retry_topological_ordering_resizes: bool,
    repeat: int,
    seed: int,
) -> RetryBenchmarkResult:
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
        if result is None:
            raise RuntimeError(f"Recipe {RECIPE_NAME!r} was not found.")
    except Exception as error:
        duration_seconds = perf_counter() - started_at
        print(f"[{label}] Failed after {duration_seconds:.6f} s: {error}")
        return RetryBenchmarkResult(
            repeat=repeat,
            seed=seed,
            retry_resizes=retry_topological_ordering_resizes,
            duration_seconds=duration_seconds,
            factory_url=None,
            evolution_url=None,
            error=f"{type(error).__name__}: {error}",
        )

    duration_seconds = perf_counter() - started_at
    print(f"[{label}] Completed in {duration_seconds:.6f} s.")

    return RetryBenchmarkResult(
        repeat=repeat,
        seed=seed,
        retry_resizes=retry_topological_ordering_resizes,
        duration_seconds=duration_seconds,
        factory_url=URLCreator.create_factory_url_link(result.factory_seed),
        evolution_url=URLCreator.create_factory_url_link(result.evolution_seed),
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
                "error",
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
                    "factory_url": result.factory_url or "",
                    "evolution_url": result.evolution_url or "",
                    "error": result.error or "",
                }
            )

    return output_path


def run() -> ScenarioResult:
    results = []

    for repeat in range(1, REPEATS + 1):
        seed = RANDOM_SEED + repeat - 1
        retry_values = (True, False) if repeat % 2 == 1 else (False, True)

        for retry_resizes in retry_values:
            results.append(
                process_electric_mining_drill(
                    retry_topological_ordering_resizes=retry_resizes,
                    repeat=repeat,
                    seed=seed,
                )
            )

    result_csv_path = write_results_csv(results, RESULT_CSV_PATH)
    successful_results = sum(result.error is None for result in results)
    print(
        f"Completed {len(results)} runs: {successful_results} succeeded and "
        f"{len(results) - successful_results} failed."
    )
    print(f"CSV saved to {result_csv_path.resolve()}.")

    return ScenarioResult(result_csv_path)


SCENARIO = Scenario(
    name="retry-or-not-retry",
    description=(
        "Compare electric-mining-drill evolution with and without retrying "
        "failed topological orderings on larger grids."
    ),
    run=run,
)
