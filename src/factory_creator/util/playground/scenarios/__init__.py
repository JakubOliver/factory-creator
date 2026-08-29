from ..scenario import Scenario
from .electric_mining_drill_topological_orderings import (
    SCENARIO as ELECTRIC_MINING_DRILL_TOPOLOGICAL_ORDERINGS,
)
from .retry_or_not_retry import SCENARIO as RETRY_OR_NOT_RETRY


_REGISTERED_SCENARIOS = (
    ELECTRIC_MINING_DRILL_TOPOLOGICAL_ORDERINGS,
    RETRY_OR_NOT_RETRY,
)

SCENARIOS: dict[str, Scenario] = {
    scenario.name: scenario for scenario in _REGISTERED_SCENARIOS
}
DEFAULT_SCENARIO_NAME = ELECTRIC_MINING_DRILL_TOPOLOGICAL_ORDERINGS.name


def get_scenario(name: str) -> Scenario:
    try:
        return SCENARIOS[name]
    except KeyError as error:
        available = ", ".join(SCENARIOS)
        raise ValueError(
            f"Unknown playground scenario {name!r}. Available: {available}."
        ) from error


__all__ = ["DEFAULT_SCENARIO_NAME", "SCENARIOS", "get_scenario"]
