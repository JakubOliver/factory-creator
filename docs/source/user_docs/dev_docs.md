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
- optional graph rendering

The optional graph rendering is enabled by the CLI `--show-graph` flag or the
GUI `Show graph (Graphviz)` option.

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
