from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from ..core.map import GridMap
from ..io.schema import MapJsonV1, validate_map_json

PathLike = Union[str, Path]


def save_json(grid_map: GridMap, path: PathLike) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # add versioned schema wrapper
    schema_obj = MapJsonV1.from_core_dict(grid_map.to_json_dict())
    with p.open("w", encoding="utf-8") as f:
        json.dump(schema_obj.model_dump(), f, indent=2, sort_keys=True)


def load_json(path: PathLike) -> GridMap:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # validate schema
    schema_obj = validate_map_json(data)
    return GridMap.from_json_dict(schema_obj.to_core_dict())
