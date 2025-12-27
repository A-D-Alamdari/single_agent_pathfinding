[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
![Status](https://img.shields.io/badge/status-educational-orange)

# Single Agent Pathfinding (SAPF)

A modular, visualization-focused Python library for single-agent pathfinding algorithms. This repository provides a robust core architecture, a modern Qt-based GUI for real-time visualization, and support for standard benchmark formats (MovingAI).

----

## ✨ Features

* **Algorithm Agnostic:** Comes with __A*__, **Dijkstra**, **BFS**, and **DFS** built-in. Easily extensible to support custom logic.

* **Interactive GUI:**
  * **Map Editor:** Paint obstacles, start, and goal nodes directly on the grid. 
  * **Real-time Visualization:** Watch algorithms explore the map step-by-step. 
  * **Metrics Panel:** Track expansions, visited nodes, path length, and runtime live.

* **Map Generation:**
  * Procedural generation (Random obstacles, Simple Maze). 
  * Benchmark support: Load MovingAI (`.map`) files.

* **Robust IO:** Save and load maps using JSON or Pickle.

* **Type-Safe Core:** Built on modern Python (3.9+) with strict typing and Pydantic validation.

----

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/A-D-Alamdari/single_agent_pathfinding.git
cd Single_agent_pathfinding
```

### 2. Install Dependencies

This project requires **Python 3.9+**. It relies on `PySide6` for the GUI and `pydantic` for data validation.

```bash
This project requires Python 3.9+. It relies on PySide6 for the GUI and pydantic for data validation.
```

----

## 🚀 Usage

### Running the GUI

To launch the main visualizer, execute the `sapf.gui.app` module from the src directory:

```bash
cd src
python -m sapf.gui.app
```

### GUI Controls

| Section      | Action      | Description                                       |
|:-------------|:------------|:--------------------------------------------------|
| **Editor**   | `s` + Click | Set **Start** node (Green).                       |
|              | `e` + Click | Set **Goal** node (Red).                          |
|              | `o` + Click | Place **Obstacle** (Black).                       |
|              | `x` + Click | **Erase** cell contents.                          |
| **Playback** | **Start**   | Begin the pathfinding animation.                  |
|              | **Step**    | Advance algorithm by exactly one step (pause mode |
|              | **Speed**   | Adjust animation delay (10ms - 2000ms).           |


----

## 📂 Project Structure

```bash
Single_agent_pathfinding/
├── src/
│   └── sapf/
│       ├── algorithms/    # A*, BFS, DFS, Dijkstra implementations
│       ├── core/          # Shared data structures (GridMap, SearchStep)
│       ├── generator/     # Map generators & MovingAI parser
│       ├── gui/           # PySide6 application & widgets
│       └── io/            # JSON/Pickle serialization logic
├── pyproject.toml
└── README.md
```

----

## 🧠 Implemented Algorithms

The repository currently includes the following algorithms in `src/sapf/algorithms/`:

1. __A* (Manhattan)__: Heuristic search using Manhattan distance (4-connected).
2. **Dijkstra**: Uniform cost search (guaranteed the shortest path). 
3. **Breadth-First Search (BFS)**: Explores equally in all directions (optimal for unweighted grids). 
4. **Depth-First Search (DFS)**: Explores deep branches first (not optimal, but memory efficient).

---- 

## 🆕 Adding a New Algorithm

To add a new algorithm (e.g., `Greedy Best-First`)`, simply:

1. Create a class inheriting from `PathfindingAlgorithm`.

2. Implement the `find_path` generator that yields `SearchStep` objects.

3. Register it in `src/sapf/algorithms/registry.py`.


----

## 🗺 Map Formats

### JSON Format
Maps can be saved/loaded as JSON for easy human editing:

```json
{
  "width": 10,
  "height": 10,
  "start": [0, 0],
  "goal": [9, 9],
  "obstacles": [[1, 1], [1, 2], [5, 5]]
}
```

### MovingAI Benchmarks

The generator package natively supports `.map` files from the [MovingAI 2D Pathfinding Benchmarks](https://movingai.com/benchmarks/mapf.html).

----

## 📄 License

[MIT License](LICENSE)