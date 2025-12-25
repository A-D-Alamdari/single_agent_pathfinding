from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from ..core.map import GridMap

PathLike = Union[str, Path]


def save_json(grid_map: GridMap, path: PathLike) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        json.dump(grid_map.to_json_dict(), f, indent=2, sort_keys=True)

def load_json(path: PathLike) -> GridMap:
    p = Path(path)

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return GridMap.from_json_dict(data)
