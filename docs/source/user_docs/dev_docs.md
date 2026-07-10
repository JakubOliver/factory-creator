# Development setup

This page describes the dependencies and tools needed for development, testing,
documentation generation, and mind map conversion.

## Python dependencies

Install the development requirements with:

```bash
pip install -r requirements_dev.txt
```

This installs the runtime dependencies together with packages used for:

- testing
- coverage reports
- documentation generation
- mind map conversion

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

It is used `xfail` for a known bug or functionality that is specified by a test
but has not been implemented yet.

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
```

On other Linux distributions, install the equivalent Graphviz system package
from the package manager.

## Notes

The runtime installation remains separate:

```bash
pip install -r requirements.txt
```
