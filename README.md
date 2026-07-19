# Factory creation

The project focuses on creating an AI-based production line generator inspired
by Factorio. Given a target product and required output rate, the system would
generate an optimized production layout or graph.

## Installation

Create and activate a virtual environment, then install the project in editable
mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Optional graph rendering and development tools can be installed with extras:

```bash
python -m pip install -e ".[graph]"
python -m pip install -e ".[dev]"
```

## Usage

```bash
factory-creator
factory-creator --cli --input data/recipe.json --building <recipe-name>
# Alternatively:
python -m factory_creator
# Or
./main.py
```

## Documentation

Instruction how to generate documentation can be found in the
[docs](docs/source/user_docs/docs_gen.md) folder.
