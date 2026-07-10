# Factory creation

The project focuses on creating an AI-based production line generator inspired
by Factorio. Given a target product and required output rate, the system would
generate an optimized production layout or graph.

## Installation

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

For development, testing, and documentation generation, install the extended
set:

```bash
pip install -r requirements_dev.txt
```

Note: the project also needs the Graphviz system package for graph layout
rendering. On Debian/Ubuntu this can be installed with:

```bash
sudo apt install graphviz
```

## Documentation

Instruction how to generate documentation can be found in the
[docs](docs/source/user_docs/docs_gen.md) folder.
