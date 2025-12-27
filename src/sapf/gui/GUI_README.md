# GUI Package (`src.sapf.gui`)

The **GUI** package provides a modern, interactive visualization interface for the Single-Agent Pathfinding repository. It is built using PySide6 (Qt for Python) and follows a Model-View-Controller (MVC) architecture to ensure separation between algorithmic logic and rendering.

----

## 📦 Package Structure

```bash
gui/
├── app.py                  # Application entry point
├── main_window.py          # Main application window and layout assembly
├── grid_view.py            # Custom QGraphicsView for efficient grid rendering
├── palette.py              # Color definitions (Themes)
├── run_controller.py       # Manages algorithm execution (Step/Run animation)
├── editor_controller.py    # Manages map editing logic (Start/Goal/Obstacles)
├── dialogs/
│   └── new_map_dialog.py   # Dialog for generating new maps (Empty, Maze, Random)
└── widgets/
    ├── algorithm_picker.py # Dropdown for algorithm selection
    ├── log_panel.py        # Scrollable text log with search and copy features
    └── stats_panel.py      # Live metrics display (Expansions, Runtime, etc.)
```

----

## 🏗 Architecture

The GUI is designed to be **algorithm-agnostic**. It does not know the internal details of A* or BFS; instead, it consumes the standard `SearchStep` protocol defined in `sapf.core`.

1. **The View Layer**
    * `GridView`: Renders the grid map, obstacles, and search overlays (open/closed sets). It handles coordinate translation (screen pixels $\leftrightarrow$ grid coordinates) and emits signals when cells are clicked.
    * `MainWindow`: Assembles the toolbar, grid view, and side panels. It manages the high-level application state (loading files, resizing layouts).

2. **The Controller Layer**
    * `RunController`: Connects the Algorithm to the UI.
        * It runs the algorithm in "Step Mode" (Python Generator).
        * Uses a `QTimer` to pull the next SearchStep without freezing the UI.
        * Updates the `GridView`, `LogPanel`, and `StatsPanel` in real-time.
    
    * `EditorController`: Handles user input for map modification.
      * Listens for key presses (`s`, `e`, `o`, `x`) and mouse clicks.
      * Enforces invariants (e.g., "Start cannot be an obstacle"). 
      * Generates new immutable `GridMap` instances upon edit.

-----

## 🎮 Features & Usage

### Launching the GUI

From the project root (src folder), run:

```bash
python -m sapf.gui.app
```

### Map Editing

The GUI includes a built-in map editor. Use keyboard shortcuts combined with mouse clicks on the grid:


| Key | Mode     | Description                                |
|:----|:---------|:-------------------------------------------|
| `s` | Start    | Click to set the Start (Green) position.   |
| `e` | Goal     | Click to set the End/Goal (Red) position.  |
| `o` | Obstacle | Click to place walls/obstacles (Black).    |
| `x` | Erase    | Click to remove walls or clear start/goal. |


### Map Generation & IO

* **New Map:** Generate maps using presets:
  * Empty Grid 
  * Random Obstacles (user-defined density)
  * Simple Maze

* **Load Map:** Supports standard formats:
  * JSON / Pickle (`.json`, `.pkl`)
  * MovingAI Benchmarks (`.map`)

* **Save Map:** Export your created maps to JSON or Pickle.

### Algorithm Control

The toolbar provides full control over the search execution:

* **Start:** begins the animation.
* **Step:** advances the algorithm by exactly one iteration.
* **Stop:** pauses/ends the current run.
* **Reset:** clears the search state (open/closed lists) but keeps the map.
* **Speed:** Adjust the delay (in ms) between steps for fast or slow motion.


----

## 📊 Components Detail

`widgets.LogPanel`

A robust logging widget that handles high-frequency updates without UI lag.

* **Features:** Auto-scroll, timestamps, "Find" text filter, and "Copy All" functionality.

`widgets.StatsPanel`

Displays real-time metrics provided by the running algorithm:

* **Visited:** Number of nodes in the Closed set.
* **Expansions:** Total iterations performed.
* **Distance:** Length of the optimal path found.
* **Runtime:** Execution time in milliseconds.

`generator.movingai` **Integration**

The GUI is fully integrated with the `sapf.generator` package, allowing it to parse and visualize standard benchmark maps from the [MovingAI repository](https://movingai.com/benchmarks/mapf.html).
