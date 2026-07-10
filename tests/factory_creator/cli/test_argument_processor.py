import pytest

from factory_creator.cli.argument_processor import ArgumentProcessor


def test_process_arguments_requires_input_and_building_for_cli(monkeypatch):
    monkeypatch.setattr("sys.argv", ["./main.py", "--cli"])

    with pytest.raises(SystemExit):
        ArgumentProcessor.process_arguments()


def test_process_arguments_parses_cli_options(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "-c",
            "--input",
            "recipes.json",
            "--building",
            "engine-unit",
            "--iteration",
            "100",
            "-s",
            "20",
            "--no-browser",
        ],
    )

    args = ArgumentProcessor.process_arguments()

    assert args.cli
    assert args.input == "recipes.json"
    assert args.building == "engine-unit"
    assert args.iteration == 100
    assert args.stagnation == 20
    assert args.no_browser
