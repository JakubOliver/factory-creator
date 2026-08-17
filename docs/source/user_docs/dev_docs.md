# Development setup

This page describes the dependencies and tools needed for development, testing,
documentation generation, and mind map conversion.

## Python dependencies

Install the development requirements with:

Optional graph rendering and development tools can be installed with extras:

```bash
python -m pip install -e ".[graph]"
python -m pip install -e ".[dev]"
```

This installs the runtime dependencies together with packages used for:

- testing
- coverage reports
- documentation generation
- mind map conversion
- optional graph rendering

The optional graph rendering is enabled by the CLI `--show-graph` flag or the
GUI `Show graph (Graphviz)` option.

## Testing

Run the complete test suite from the project root with:

```bash
pytest
```

Tests can also be limited to a file, a single test, or tests whose names match
an expression:

```bash
pytest tests/factory_creator/test_graph_to_matrix.py
pytest tests/factory_creator/test_graph_to_matrix.py::test_distance_and_orientation_helpers
pytest -k underground
```

Useful pytest options include:

- `-ra` displays reasons for skipped and expected-to-fail (`xfail`) tests, as
  well as other non-passing results.
- `-vv` displays full test names and more detailed output.
- `-s` disables output capturing, making test `print()` calls immediately
  visible.
- `-x` stops after the first failure.

Options may be combined, for example:

```bash
pytest -ra -vv
pytest -x --lf
```

`xfail` is used for a known bug or functionality that is specified by a test but
has not been implemented yet.

## Development playground

Saved development scenarios live in
`src/factory_creator/util/playground/scenarios`. List and run them with:

```bash
python -m factory_creator.util.playground --list
python -m factory_creator.util.playground electric-mining-drill-topological-orderings
```

### Test coverage

The development requirements include `pytest-cov`. Display coverage and missing
line numbers in the terminal with:

```bash
pytest --cov=factory_creator --cov-report=term-missing
```

Generate a browsable HTML report with:

```bash
pytest --cov=factory_creator --cov-report=html
```

The report is written to `htmlcov/index.html`.

## Graphviz

The project uses the Graphviz system package for graph layout rendering and
PNG/SVG export in the application code.

On Debian/Ubuntu:

```bash
sudo apt install graphviz

sudo dnf install graphviz
```

On other Linux distributions, install the equivalent Graphviz system package
from the package manager.

### Windows

You can install Graphviz with `winget` or `choco`:

```bash
winget install Graphviz.Graphviz

choco install graphviz
```

Official Graphviz download and installation instructions:

- [Graphviz download page](https://graphviz.org/download/)

The page also contains the official Windows installers and additional
platform-specific installation notes.

## Notes

The runtime installation remains separate:

```bash
pip install -r requirements.txt
```
