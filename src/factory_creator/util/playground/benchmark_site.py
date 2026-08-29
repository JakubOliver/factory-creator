import argparse
import html
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .scenarios import SCENARIOS


@dataclass(frozen=True, slots=True)
class BenchmarkRunMetadata:
    run_key: str
    created_at: str
    commit_sha: str
    ref_name: str
    run_url: str

    @staticmethod
    def from_environment() -> "BenchmarkRunMetadata":
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        run_id = os.environ.get("GITHUB_RUN_ID")
        run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        if run_id:
            run_key = f"{run_id}-{run_attempt}"
        else:
            run_key = f"local-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}"

        repository = os.environ.get("GITHUB_REPOSITORY", "")
        server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        run_url = (
            f"{server_url}/{repository}/actions/runs/{run_id}"
            if repository and run_id
            else ""
        )

        return BenchmarkRunMetadata(
            run_key=_safe_path_component(run_key),
            created_at=created_at,
            commit_sha=os.environ.get("GITHUB_SHA", ""),
            ref_name=os.environ.get("GITHUB_REF_NAME", ""),
            run_url=run_url,
        )


def publish_benchmark_results(
    results_directory: Path,
    history_directory: Path,
    metadata: BenchmarkRunMetadata,
) -> Path:
    csv_paths = _get_scenario_csv_paths(results_directory)
    run_directory = history_directory / "runs" / metadata.run_key
    run_directory.mkdir(parents=True, exist_ok=True)

    scenarios = []
    for scenario_name, csv_path in csv_paths.items():
        destination = run_directory / csv_path.name
        shutil.copy2(csv_path, destination)
        scenarios.append(
            {
                "name": scenario_name,
                "csv_file": destination.name,
                "size_bytes": destination.stat().st_size,
            }
        )

    manifest = asdict(metadata) | {"scenarios": scenarios}
    manifest_path = run_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (run_directory / "index.html").write_text(
        _create_run_page(manifest),
        encoding="utf-8",
    )

    manifests = _load_manifests(history_directory)
    history_directory.mkdir(parents=True, exist_ok=True)
    (history_directory / "index.html").write_text(
        _create_history_page(manifests),
        encoding="utf-8",
    )

    return history_directory / "index.html"


def _get_scenario_csv_paths(results_directory: Path) -> dict[str, Path]:
    csv_paths = {name: results_directory / f"{name}.csv" for name in SCENARIOS}
    missing = [str(path) for path in csv_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing scenario CSV results: " + ", ".join(missing))

    return csv_paths


def _load_manifests(history_directory: Path) -> list[dict]:
    manifests = []
    for manifest_path in (history_directory / "runs").glob("*/manifest.json"):
        manifests.append(json.loads(manifest_path.read_text(encoding="utf-8")))

    return sorted(
        manifests,
        key=lambda manifest: (
            manifest.get("created_at", ""),
            manifest.get("run_key", ""),
        ),
        reverse=True,
    )


def _create_history_page(manifests: list[dict]) -> str:
    rows = []
    for manifest in manifests:
        run_key = html.escape(str(manifest["run_key"]))
        commit_sha = str(manifest.get("commit_sha", ""))
        commit_text = html.escape(commit_sha[:8] or "local")
        run_url = str(manifest.get("run_url", ""))
        run_link = (
            f'<a href="{html.escape(run_url, quote=True)}">Actions run</a>'
            if run_url
            else "local run"
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(manifest.get('created_at', '')))}</td>"
            f"<td><code>{commit_text}</code></td>"
            f"<td>{html.escape(str(manifest.get('ref_name', '')))}</td>"
            f"<td>{len(manifest.get('scenarios', []))}</td>"
            f'<td><a href="runs/{run_key}/">Details</a></td>'
            f"<td>{run_link}</td>"
            "</tr>"
        )

    rows_html = "\n".join(rows) or (
        '<tr><td colspan="6">No benchmark runs have been published yet.</td></tr>'
    )
    return _html_document(
        "Benchmark history",
        """
<h1>Benchmark history</h1>
<table>
  <thead>
    <tr><th>Created</th><th>Commit</th><th>Ref</th><th>CSVs</th><th>Results</th><th>Workflow</th></tr>
  </thead>
  <tbody>
"""
        + rows_html
        + """
  </tbody>
</table>
""",
    )


def _create_run_page(manifest: dict) -> str:
    rows = []
    for scenario in manifest["scenarios"]:
        csv_file = html.escape(str(scenario["csv_file"]), quote=True)
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(scenario['name']))}</td>"
            f"<td>{scenario['size_bytes']}</td>"
            f'<td><a href="{csv_file}">Open CSV</a></td>'
            "</tr>"
        )

    run_url = str(manifest.get("run_url", ""))
    workflow_link = (
        f'<p><a href="{html.escape(run_url, quote=True)}">Open GitHub Actions run</a></p>'
        if run_url
        else ""
    )
    body = f"""
<p><a href="../../">Back to benchmark history</a></p>
<h1>Benchmark run {html.escape(str(manifest["run_key"]))}</h1>
<dl>
  <dt>Created</dt><dd>{html.escape(str(manifest["created_at"]))}</dd>
  <dt>Commit</dt><dd><code>{html.escape(str(manifest.get("commit_sha", "")))}</code></dd>
  <dt>Ref</dt><dd>{html.escape(str(manifest.get("ref_name", "")))}</dd>
</dl>
{workflow_link}
<table>
  <thead><tr><th>Scenario</th><th>Size [bytes]</th><th>CSV</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
"""
    return _html_document(
        f"Benchmark run {manifest['run_key']}",
        body,
    )


def _html_document(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem auto; max-width: 70rem; padding: 0 1rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #bbb; padding: .5rem; text-align: left; }}
    th {{ background: #eee; }}
    dt {{ font-weight: bold; }}
    dd {{ margin-bottom: .5rem; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def _safe_path_component(value: str) -> str:
    safe_value = re.sub(r"[^A-Za-z0-9._-]", "-", value)
    if not safe_value or safe_value in {".", ".."}:
        raise ValueError("Benchmark run key is empty or unsafe.")
    return safe_value


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add scenario CSV files to the static benchmark history.",
    )
    parser.add_argument(
        "--results-directory",
        type=Path,
        default=Path("output"),
    )
    parser.add_argument(
        "--history-directory",
        type=Path,
        default=Path("benchmark-history") / "benchmarks",
    )
    return parser


def main() -> int:
    args = create_argument_parser().parse_args()
    index_path = publish_benchmark_results(
        args.results_directory,
        args.history_directory,
        BenchmarkRunMetadata.from_environment(),
    )
    print(f"Benchmark history generated at {index_path.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
