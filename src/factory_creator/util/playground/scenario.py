from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    csv_path: Path


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    description: str
    run: Callable[[], ScenarioResult]
