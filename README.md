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

On Windows, run the following commands in PowerShell from the project folder:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

When using Command Prompt (`cmd.exe`), activate the environment with
`.venv\Scripts\activate.bat` instead.

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

On Windows (PowerShell):

```powershell
factory-creator
factory-creator --cli --input data\recipe.json --building <recipe-name>
# Alternatively:
python -m factory_creator
# Or:
python .\main.py
```

## Documentation

Instructions for generating the documentation can be found in the
[docs](docs/source/user_docs/docs_gen.md) folder.
