# Development setup

This page describes the dependencies and tools needed for development,
testing, documentation generation, and mind map conversion.

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
