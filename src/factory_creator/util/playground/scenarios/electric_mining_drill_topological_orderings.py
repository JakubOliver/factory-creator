import csv
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from networkx import DiGraph, all_topological_sorts
from prettytable import PrettyTable

from ....export import URLCreator
from ....graph_processing import GraphToMatrix
from ....loading import FactoryLoader
from ..scenario import Scenario


RECIPE_NAME = "electric-mining-drill"
RECIPE_PATH = Path(__file__).resolve().parents[5] / "data" / "recipe.json"
OUTPUT_DIRECTORY = Path("output")
RESULT_CSV_PATH = OUTPUT_DIRECTORY / "electric-mining-drill-topological-orderings.csv"
TOPOLOGICAL_ORDERING_SAMPLE_SIZE = 25
PROGRESS_INTERVAL = 1


@dataclass(frozen=True, slots=True)
class OrderingBenchmarkResult:
    ordering: tuple
    duration_seconds: float
    url: str | None
    error: str | None = None


def create_dependency_graph(recipe_path: Path = RECIPE_PATH) -> DiGraph:
    factories = FactoryLoader.load(str(recipe_path))
    root = FactoryLoader.get_dependency_tree(factories, RECIPE_NAME)

    return root.get_dependency_graph(
        show_amounts=True,
        show_simplified=False,
    )


def count_topological_orderings(graph: DiGraph) -> int:
    ordering_count = 0
    for _ordering in all_topological_sorts(graph):
        ordering_count += 1

    return ordering_count


def generate_evenly_spaced_topological_orderings(
    graph,
    sample_size=TOPOLOGICAL_ORDERING_SAMPLE_SIZE,
):
    if sample_size < 1:
        raise ValueError("Topological ordering sample size must be positive.")

    total_orderings = count_topological_orderings(graph)
    sample_size = min(sample_size, total_orderings)

    if sample_size == 1:
        sampled_indices = {0}
    else:
        distance_between_samples = (total_orderings - 1) / (sample_size - 1)
        sampled_indices = set()
        for sample_index in range(sample_size):
            ordering_index = round(sample_index * distance_between_samples)
            sampled_indices.add(ordering_index)

    last_sampled_index = max(sampled_indices)
    for ordering_index, ordering in enumerate(all_topological_sorts(graph)):
        if ordering_index in sampled_indices:
            yield tuple(ordering)

        # There is no reason to enumerate results after the final sample.
        if ordering_index == last_sampled_index:
            return


def benchmark_topological_orderings(
    graph,
    topological_orderings=None,
    report_method=print,
    progress_interval=PROGRESS_INTERVAL,
):
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    if topological_orderings is None:
        topological_orderings = generate_evenly_spaced_topological_orderings(
            graph,
        )

    results = []
    for index, ordering in enumerate(topological_orderings, start=1):
        ordering = tuple(ordering)
        started_at = perf_counter()

        try:
            grid = GraphToMatrix.convert_via_heuristics(
                graph,
                topological_ordering=ordering,
                report_method=_ignore_message,
                error_report_method=_ignore_message,
            )
        except Exception as error:
            duration_seconds = perf_counter() - started_at
            result = OrderingBenchmarkResult(
                ordering=ordering,
                duration_seconds=duration_seconds,
                url=None,
                error=f"{type(error).__name__}: {error}",
            )
        else:
            duration_seconds = perf_counter() - started_at
            result = OrderingBenchmarkResult(
                ordering=ordering,
                duration_seconds=duration_seconds,
                url=URLCreator.create_factory_url_from_grid(grid),
            )

        results.append(result)

        if progress_interval is not None and index % progress_interval == 0:
            report_method(f"Processed {index} topological orderings.")

    return results


def create_result_table(graph, results):
    table = PrettyTable(
        ["#", "Topological ordering", "Time [s]", "Grid URL"],
    )
    table.align["Topological ordering"] = "l"
    table.align["Grid URL"] = "l"

    for index, result in enumerate(results, start=1):
        table.add_row(
            [
                index,
                _format_ordering(graph, result.ordering),
                f"{result.duration_seconds:.6f}",
                result.url or f"ERROR: {result.error}",
            ]
        )

    return table


def write_results_csv(
    graph,
    results,
    output_path=RESULT_CSV_PATH,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "index",
                "topological_ordering",
                "duration_seconds",
                "grid_url",
                "error",
            ],
        )
        writer.writeheader()

        for index, result in enumerate(results, start=1):
            writer.writerow(
                {
                    "index": index,
                    "topological_ordering": _format_ordering(
                        graph,
                        result.ordering,
                    ),
                    "duration_seconds": f"{result.duration_seconds:.9f}",
                    "grid_url": result.url or "",
                    "error": result.error or "",
                }
            )

    return output_path


def run():
    graph = create_dependency_graph()
    print(
        f"Benchmarking {TOPOLOGICAL_ORDERING_SAMPLE_SIZE} evenly spaced "
        f"topological orderings for {RECIPE_NAME} "
        f"({len(graph)} nodes, {len(graph.edges)} edges)."
    )

    results = benchmark_topological_orderings(graph)
    result_csv_path = write_results_csv(graph, results)

    successful_results = sum(result.error is None for result in results)
    total_duration = sum(result.duration_seconds for result in results)

    print(create_result_table(graph, results))
    print(
        f"Completed {len(results)} orderings in {total_duration:.6f} s: "
        f"{successful_results} succeeded and "
        f"{len(results) - successful_results} failed."
    )
    print(f"CSV saved to {result_csv_path.resolve()}.")


def _format_ordering(graph, ordering):
    nodes = []
    for node in ordering:
        node_text = str(node)
        label = str(graph.nodes[node].get("label", node))
        nodes.append(node_text if node_text == label else f"{node_text} ({label})")

    return " -> ".join(nodes)


def _ignore_message(_message):
    pass


SCENARIO = Scenario(
    name="electric-mining-drill-topological-orderings",
    description=(
        "Benchmark 1,000 evenly spaced orderings of the full dependency graph "
        "for an electric mining drill."
    ),
    run=run,
)
