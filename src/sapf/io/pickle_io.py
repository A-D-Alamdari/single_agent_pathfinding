from __future__ import annotations

import pickle
from pathlib import Path
from typing import Union

from src.sapf.core.map import GridMap

PathLike = Union[str, Path]


def save_pickle(grid_map: GridMap, path: PathLike) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("wb") as f:
        pickle.dump(grid_map, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(path: PathLike) -> GridMap:
    p = Path(path)

    with p.open("rb") as f:
        obj = pickle.load(f)

    if not isinstance(obj, GridMap):
        raise TypeError(f"Pickle did not contain a GridMap; got: {type(obj).__name__}")

    # Ensure validation is enforced even if pickle was manipulated.
    # Reconstruct via JSON dict to re-validate invariants deterministically.
    return GridMap.from_json_dict(obj.to_json_dict())
