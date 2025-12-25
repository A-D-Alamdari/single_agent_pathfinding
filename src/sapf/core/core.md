# Core Package (`sapf.core`)

The **core** package defines the foundational data structures and shared abstractions used across the entire *Single-Agent Pathfinding* repository.  
All algorithms, the CLI, and the GUI depend on this package.  

The guiding design principles are:

- **Single source of truth** for maps, coordinates, and invariants  
- **UI-agnostic**: no GUI or CLI logic in `core`  
- **Algorithm-agnostic**: no search-specific logic in `core`  
- **Stable interfaces** that allow future extensions (diagonal moves, weighted costs, continuous time, etc.)

---

## Package Structure

```bash
core/
├─ init.py
├─ types.py # Shared type aliases
├─ exceptions.py # Domain-specific exceptions
├─ map.py # GridMap definition and validation
├─ node.py # Visualization-friendly node projection
├─ events.py # Search step event definitions (shared protocol)
├─ result.py # Standardized search results and metrics
└─ config.py # Shared configuration (connectivity, options)
```

---

## Module Descriptions

### `types.py`
Defines common, shared type aliases used across the repository.

**Purpose**
- Avoid repeated tuple definitions
- Improve readability and type checking
- Provide a single coordinate convention

**Key Types**
- `Coord`: `(x, y)` integer grid coordinate

**Design Notes**
- Coordinates always follow `(x, y)` with `(0, 0)` at the top-left
- All grid bounds are enforced in `GridMap`, not here

---

### `exceptions.py`
Contains domain-specific exceptions.

**Purpose**
- Provide clear, semantic error types
- Separate user input / data errors from programming errors

**Key Exceptions**
- `MapValidationError`: raised when a `GridMap` violates invariants

**Design Notes**
- Algorithms and UI code should not raise raw `ValueError` for map issues
- Centralized exception types make CLI/GUI error handling cleaner

---

### `map.py`
Defines the **canonical grid-world representation**.

**Purpose**
- Represent the environment independently of any algorithm
- Enforce all map invariants in one place
- Support serialization (JSON / pickle)

**Main Class**
- `GridMap`

**Fields**
- `width`, `height`: grid dimensions
- `obstacles`: set of blocked cells
- `start`, `goal`: optional start and goal positions

**Key Invariants**
- Coordinates must be inside bounds
- Start and goal cannot be on obstacles
- Width and height must be positive integers

**Key Methods**
- `in_bounds(coord)`
- `is_blocked(coord)`
- `to_json_dict() / from_json_dict()`
- `save_json() / load_json()`
- `save_pickle() / load_pickle()`

**Design Notes**
- All validation happens during construction
- Algorithms can safely assume the map is valid
- Serialization logic is deterministic and stable

---

### `node.py`
Defines a lightweight, visualization-friendly node projection.

**Purpose**
- Provide a stable representation for GUI rendering and debugging
- Decouple algorithm internals from visualization needs

**Main Class**
- `Node`

**Fields**
- `pos`: coordinate
- `g`, `h`, `f`: cost values
- `parent`: parent coordinate (optional)

**Design Notes**
- Algorithms are not required to use this internally
- Useful when exporting states to GUI or logs
- Supports future extensions (weighted graphs, continuous costs)

---

### `events.py`
Defines the **shared step-event protocol** for algorithm execution.

**Purpose**
- Provide a common event type for step-by-step visualization
- Decouple algorithms from GUI implementation details

**Exports**
- `SearchStep`
- `SearchStatus`

**Design Notes**
- Algorithms yield `SearchStep` objects in step mode
- GUI and CLI consume these events uniformly
- This module allows future expansion into richer event types
  (e.g., separate OPEN/CLOSED updates, statistics events)

---

### `result.py`
Defines a standardized search result container.

**Purpose**
- Provide a consistent return type for non-step execution
- Centralize metrics and status reporting

**Main Class**
- `SearchResult`

**Fields**
- `status`: FOUND / NO_PATH / CANCELLED
- `path`: final path (if any)
- `expansions`: number of expanded nodes
- `runtime_ms`: execution time
- `cost`: optional path cost
- `extra`: extensible metadata dictionary

**Design Notes**
- Currently optional for algorithms
- Recommended for future CLI/benchmark integration
- Aligns with research-oriented evaluation pipelines

---

### `config.py`
Defines shared configuration and options.

**Purpose**
- Avoid duplicated flags across CLI, GUI, and algorithms
- Provide a forward-compatible configuration layer

**Key Components**
- `Connectivity` enum (`4` or `8`)
- `SearchConfig` dataclass

**Design Notes**
- Current built-in algorithms use 4-connectivity
- This module enables future diagonal and weighted extensions
- Keeps algorithm signatures clean and extensible

---

## Design Philosophy Summary

| Aspect | Decision |
|------|----------|
| Validation | Centralized in `GridMap` |
| Visualization | Driven by step events, not algorithm internals |
| Extensibility | Configuration and result containers provided |
| Coupling | Core is independent of GUI/CLI |
| Safety | Invariants enforced early |

---

## When to Modify Core

You should update the **core** package when:
- Adding new environment representations (e.g., continuous grids)
- Supporting weighted or time-dependent costs
- Extending event types for richer visualization
- Adding standardized benchmarking metrics

You **should not** add:
- GUI widgets
- Rendering logic
- Algorithm-specific heuristics

---

## Relation to the Rest of the Repository

- **Algorithms** consume `GridMap` and emit `SearchStep`
- **GUI** renders `SearchStep` events
- **CLI** loads maps and prints `SearchResult`
- **Tests** validate core invariants independently

This separation ensures correctness, maintainability, and research-grade extensibility.

---

*This core package is intentionally minimal, explicit, and strict — making it suitable for both educational visualization and serious algorithmic experimentation.*
