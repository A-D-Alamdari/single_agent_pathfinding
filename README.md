[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
![Status](https://img.shields.io/badge/status-educational-orange)

# Single Agent Pathfinding (SAPF) Visualizer

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


> This project requires Python 3.9+. It relies on PySide6 for the GUI and pydantic for data validation.


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

------

------

# 🧭 Single-Agent Pathfinding Algorithms – Taxonomy

This document provides a **comprehensive and structured taxonomy of algorithms** commonly used for **single-agent pathfinding**.  
It is suitable for both **academic reference** and **practical system design**, such as grid-world simulators and GUI-based visualizers.

---

## 1. Uninformed (Blind) Search Algorithms

These algorithms **do not use heuristics** and explore the state space systematically.

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Depth-Limited Search (DLS)
- Iterative Deepening DFS (IDDFS)
- Uniform Cost Search (UCS)

**Properties**
- **Completeness:** Yes (except DFS without limits)
- **Optimality:** Only UCS (with non-negative costs)
- **Scalability:** Poor in large state spaces

---

## 2. Informed (Heuristic) Search Algorithms

These algorithms leverage **heuristic functions** to guide the search toward the goal.

### Classical Heuristic Search
- Greedy Best-First Search
- A*
- Weighted A*
- Anytime Repairing A* (ARA*)
- Anytime Dynamic A* (AD*)
- Multi-Heuristic A* (MHA*)

### Memory-Efficient Variants
- Iterative Deepening A* (IDA*)
- Recursive Best-First Search (RBFS)
- Simplified Memory-Bounded A* (SMA*)

**Properties**
- **Completeness:** Yes (with admissible heuristics)
- **Optimality:** Yes (A*, IDA*)
- **Scalability:** Strong with good heuristics

---

## 3. Dynamic and Incremental Search Algorithms

Designed for environments where **edge costs or obstacles change over time**.

- D*
- D* Lite
- Focused D*
- Lifelong Planning A* (LPA*)

**Typical Use Cases**
- Robotics
- Online navigation
- Real-time replanning

---

## 4. Graph-Based Shortest Path Algorithms

These algorithms treat the environment as a **general graph**.

- Dijkstra’s Algorithm
- Bellman–Ford Algorithm
- Floyd–Warshall Algorithm
- Johnson’s Algorithm

**Notes**
- Often used as benchmarks or subroutines
- Floyd–Warshall computes all-pairs shortest paths and is impractical for large grids

---

## 5. Grid-Specific and Any-Angle Pathfinding

Designed to reduce **grid artifacts** and produce more realistic paths.

- Jump Point Search (JPS)
- JPS+
- Theta*
- Lazy Theta*
- Field D*
- ANYA

**Advantages**
- Shorter and smoother paths
- Fewer node expansions than classical grid-based A*

---

## 6. Sampling-Based Motion Planning

Primarily used in **continuous or high-dimensional spaces**.

- Rapidly-Exploring Random Tree (RRT)
- RRT*
- Probabilistic Roadmaps (PRM)
- PRM*

**Common Domains**
- Robotics
- Autonomous vehicles
- Continuous configuration spaces

---

## 7. Bio-Inspired and Meta-Heuristic Algorithms

Optimization-based approaches without strict guarantees.

- Genetic Algorithms (GA)
- Ant Colony Optimization (ACO)
- Particle Swarm Optimization (PSO)
- Simulated Annealing
- Bee Colony Optimization

**Properties**
- **Completeness:** No
- **Optimality:** No guarantees
- Useful for very complex or poorly modeled environments

---

## 8. Learning-Based Pathfinding

The agent learns a **policy or value function** instead of explicitly planning.

### Reinforcement Learning
- Q-Learning
- SARSA
- Deep Q-Networks (DQN)
- Policy Gradient Methods
- Actor–Critic Methods

### Imitation & Hybrid Learning
- Behavior Cloning
- Learned Heuristic Functions
- Neural A* / Differentiable A*

---

## 9. Visibility and Geometric Planning

Used when obstacles are **polygonal** rather than grid-based.

- Visibility Graphs
- Voronoi Diagrams
- Navigation Meshes (NavMesh)

---

## 10. Constraint-Based and Mathematical Approaches

Less common, but theoretically important.

- Linear Programming (LP)
- Mixed-Integer Linear Programming (MILP)
- SAT-Based Planning
- Answer Set Programming (ASP)

---

## 11. Hybrid and Practical Systems

Combinations of classical planning and learning-based control.

- Hierarchical Pathfinding (HPA*)
- Abstract Graph Search
- Learned Heuristics + A*
- Planning + Reinforcement Learning Controllers


---

## 📊 Algorithm Comparison Table

Legend:  
✅ = Yes ⚠️ = Partial / Conditional ❌ = No

| Algorithm | Uses Heuristic | Step-by-Step Visualizable | Optimal | Complete | Dynamic Replanning | Any-Angle | Typical Use Case |
|---------|----------------|---------------------------|---------|----------|--------------------|-----------|------------------|
| BFS | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | Shortest path in unweighted grids |
| DFS | ❌ | ✅ | ❌ | ⚠️ | ❌ | ❌ | Fast exploration, low memory |
| UCS | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | Optimal path with costs |
| Greedy Best-First | ✅ | ✅ | ❌ | ⚠️ | ❌ | ❌ | Fast but suboptimal paths |
| A* | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | Standard optimal grid pathfinding |
| Weighted A* | ✅ | ✅ | ⚠️ | ✅ | ❌ | ❌ | Faster bounded-suboptimal search |
| IDA* | ✅ | ⚠️ | ✅ | ✅ | ❌ | ❌ | Memory-constrained environments |
| RBFS | ✅ | ⚠️ | ✅ | ✅ | ❌ | ❌ | Recursive memory-efficient search |
| SMA* | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ | Limited-memory optimal search |
| ARA* | ✅ | ✅ | ⚠️ | ✅ | ❌ | ❌ | Anytime planning |
| D* Lite | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | Dynamic environments |
| LPA* | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | Incremental replanning |
| Theta* | ✅ | ⚠️ | ✅ | ✅ | ❌ | ✅ | Any-angle grid pathfinding |
| Lazy Theta* | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | ✅ | Faster any-angle planning |
| Jump Point Search | ✅ | ⚠️ | ✅ | ✅ | ❌ | ❌ | Fast uniform-cost grids |
| HPA* | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | Large-scale maps |
| RRT | ❌ | ⚠️ | ❌ | ⚠️ | ⚠️ | ✅ | Continuous motion planning |
| RRT* | ❌ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ | Asymptotically optimal planning |
| PRM | ❌ | ❌ | ⚠️ | ⚠️ | ❌ | ✅ | Multi-query planning |
| Genetic Algorithm | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Optimization-based search |
| Ant Colony Optimization | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Stochastic optimization |
| Q-Learning | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ | Learned navigation policy |
| DQN | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ | Deep RL-based navigation |

---

## 📝 Notes

- **Step-by-step visualization** is best supported by classical search algorithms (BFS, A*, D* Lite).
- **Any-angle algorithms** reduce grid artifacts but require more complex visualization logic.
- **Dynamic replanning** algorithms are critical for robotics and real-world navigation.
- **Learning-based methods** execute learned policies rather than explicit planning steps.


---

## 📌 Summary

This repository focuses primarily on **search-based and heuristic algorithms** that:
- Operate on grid-world environments
- Support step-by-step visualization
- Are suitable for education, debugging, and research

Advanced methods (sampling-based, learning-based, and optimization-based) are included for completeness and extensibility.


