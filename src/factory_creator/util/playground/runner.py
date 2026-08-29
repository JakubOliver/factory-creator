from .scenario import Scenario, ScenarioResult


def run_scenario(scenario: Scenario) -> ScenarioResult:
    result = scenario.run()

    expected_name = f"{scenario.name}.csv"

    return result
