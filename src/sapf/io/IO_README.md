# IO Package (`sapf.io`)

The **io** package is responsible for **all input/output operations** related to map persistence and conversion.  
It provides a clean separation between:

- **Core logic** (`GridMap`, validation, invariants)
- **Storage formats** (JSON, pickle)
- **Schema validation and normalization**

No algorithm, GUI, or CLI logic should directly read/write files outside this package.

---

## Package Structure

```bash
io/
├─ init.py
├─ schema.py      # Pydantic-based JSON schema (versioned)
├─ json_io.py     # Load/save JSON maps
├─ pickle_io.py   # Load/save pickle maps
└─ converters.py  # Format conversion & normalization helpers
```

---

## Design Principles

1. **Single Responsibility**
   - File parsing, validation, and serialization live here
   - Core logic (`GridMap`) remains format-agnostic

2. **Safety First**
   - JSON files are validated against a schema
   - Pickle files are re-validated after loading
   - Clear, domain-specific errors are raised

3. **Forward Compatibility**
   - JSON schema is versioned
   - New formats or schema versions can be added without breaking old files

4. **Canonical Representation**
   - All loaded maps are normalized into a consistent internal form

---

## Module Descriptions

---

### `schema.py`
Defines **versioned JSON schemas** using **pydantic**.

**Purpose**
- Validate external JSON files before creating `GridMap`
- Provide precise and readable error messages
- Enable future schema evolution

**Current Schema**
- `MapJsonV1`

**Fields**
- `version`: schema version (currently `1`)
- `width`, `height`: positive integers
- `start`, `goal`: `[x, y]` or `null`
- `obstacles`: list of `[x, y]`

**Key Functions**
- `validate_map_json(data: dict) -> MapJsonV1`

**Why pydantic?**
- Strong validation
- Human-readable error reporting
- Easy versioning and extension

---

### `json_io.py`
Handles **JSON file persistence**.

**Purpose**
- Read and write maps in a human-readable format
- Enforce schema validation on load
- Ensure deterministic output

**Key Functions**
- `save_json(grid_map, path)`
- `load_json(path) -> GridMap`

**Behavior**
- Automatically embeds `version` into saved JSON
- Rejects invalid or unsupported schema versions
- Delegates structural validation to `schema.py`

**Typical Use**
```python
from single_agent_pathfinding.core.map import GridMap

grid_map = GridMap.load_json("map.json")
grid_map.save_json("out.json")

