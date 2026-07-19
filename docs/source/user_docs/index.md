# User Documentation

## Installation

Create and activate a virtual environment, then install the project in editable
mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows, open PowerShell in the project folder and run:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

When using Command Prompt (`cmd.exe`), activate the virtual environment with:

```bat
.venv\Scripts\activate.bat
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

Development setup, including documentation generation and Graphviz installation,
is described in [Development setup](dev_docs.md).

- Some GPUs are not compatible with PySide6 and WebGL redenring. In this case
  can be the GUI mode be started with `--no-browser` flag to use external
  browser buttons instead of embedded browser tabs. Or can be used this comamnd
  `QTWEBENGINE_CHROMIUM_FLAGS="--enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader --use-angle=swiftshader" ./main.py`
  which set WebGL computing with swiftshader which uses CPU for rendering
  instead of GPU.

## Controls

### GUI

Before computation:
![Before computation GUI](../_static/images/GUI_before_computation.png)

After computation:
![After computation GUI](../_static/images/GUI_after_computation.png)

The GUI contains these controls:

| Control                 | Description                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `Recipes path...`       | Text field for the path to the JSON recipe file.                                                                  |
| `Browse...`             | Opens a file picker for selecting a JSON recipe file.                                                             |
| `Import recipes`        | Validates the selected file and loads available recipe names into the recipe dropdown.                            |
| `Recipe dropdown`       | Selects which recipe should be computed. It is shown after recipes are imported.                                  |
| `Compute recipe`        | Starts the factory computation in a background thread.                                                            |
| `Options`               | Expands or collapses additional graph and evolution settings.                                                     |
| `Show amounts`          | Shows ingredient amounts on dependency graph edges.                                                               |
| `Simplified structure`  | Uses a simplified backend dependency graph. This changes the generated graph, grid, matrix, and evolution result. |
| `Show graph (Graphviz)` | Opens the rendered dependency graph after computation if the optional Graphviz support is installed.              |
| `Iterations`            | Maximum number of evolution iterations.                                                                           |
| `Stagnation threshold`  | Stops evolution after this many generations without improvement.                                                  |
| `Worker messages`       | Displays progress and error messages from the computation.                                                        |

When computation finishes, the result area shows the generated factory layouts.
By default, they are loaded in two embedded tabs:

- `Factory` - the layout before evolution
- `Evolved factory` - the layout after evolution

If the application is started with `--no-browser`, the GUI uses buttons instead
of embedded browser tabs:

In this mode, `Show factory` and `Show evolved factory` open the generated links
in the system browser.

GUI contains a menu bar (settings) in top left corner with several other
options:

#### Preferences

In this menu user can set **how detailed the progress message should be**:

- Low - only the most important messages:
  - Info about computation status
  - Generation started
  - Fitness of the best individual in the current generation
- Medium - same as low, plus:
  - Info about failures and errors occured while computing the factory
- High - same as medium, plus:
  - Detailed info about the evolution process, placement of individual
    buildings, thier connections etc.

Other option is **what website should be used to open generated factory**. By
defauled is set to 'https://fbe.teoxoy.com/'. This website/project is open
source and can be run locally. So user can set the URL to ther own instance.

**User mutations directory** is a directory from where can be loaded
user-defined mutations via reflection.

**User fitness aspects directory** is a directory from where can be loaded
user-defined fitness aspects via reflection.

![Preferences menu](../_static/images/GUI_preferences_menu.png)

#### Mutations

In this menu can user select which mutations should be used in the evolution
process. Can also set at what generation will the mutation start to be applied
(same for end).

![Mutation menu](../_static/images/GUI_mutations_menu.png)

#### Fitness aspects

In this menu can user select which fitness aspects should be used in the
evolution process. Can also set what weight should be used for each fitness
aspect.

![Fitness aspects menu](../_static/images/GUI_fitness_aspects_menu.png)

### CLI

- CLI mode is not upto date with GUI mode. If not necessary, it is recommended
  to use GUI mode instead of CLI mode.

The CLI mode is started with the `--cli` flag. In this mode, the input recipe
file and target recipe/building name are required:

```bash
python3 main.py --cli --input data/recipe.json --building barrel
```

Short argument names can also be used:

```bash
python3 main.py -c -i data/recipe.json -b barrel
```

The command validates that the selected JSON file contains the requested recipe.
If the input is valid, it computes the factory and prints two URLs:

- the factory before evolution
- the factory after evolution

The evolution can be configured by two optional arguments:

```bash
python3 main.py -c -i data/recipe.json -b engine-unit --iteration 100 --stagnation 20
```

Available CLI arguments:

| Argument       | Short | Description                                                                 | Default  |
| -------------- | ----- | --------------------------------------------------------------------------- | -------- |
| `--cli`        | `-c`  | Run the application without the GUI.                                        | disabled |
| `--input`      | `-i`  | Path to the JSON recipe file. Required in CLI mode.                         | none     |
| `--building`   | `-b`  | Name of the recipe/building to compute. Required in CLI mode.               | none     |
| `--iteration`  | `-t`  | Maximum number of evolution iterations.                                     | `10`     |
| `--stagnation` | `-s`  | Stop evolution after this many generations without progress.                | `10`     |
| `--no-browser` | `-n`  | In GUI mode, use external browser buttons instead of embedded browser tabs. | disabled |
| `--show-graph` | none  | Render the dependency graph if the optional Graphviz support is installed.  | disabled |
