import argparse

from .runner import run_scenario
from .scenarios import DEFAULT_SCENARIO_NAME, SCENARIOS, get_scenario


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a saved development playground scenario.",
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        choices=SCENARIOS,
        default=DEFAULT_SCENARIO_NAME,
        help=f"scenario to run (default: {DEFAULT_SCENARIO_NAME})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_scenarios",
        help="list the available scenarios and exit",
    )

    return parser


def main():
    args = create_argument_parser().parse_args()

    if args.list_scenarios:
        for scenario in SCENARIOS.values():
            print(f"{scenario.name}: {scenario.description}")

        return 0

    run_scenario(get_scenario(args.scenario))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
