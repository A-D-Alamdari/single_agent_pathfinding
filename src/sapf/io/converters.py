from __future__ import annotations

from typing import Any, Dict

from ..core.map import GridMap


def normalize_map(grid_map: GridMap) -> GridMap:
    """
    Return a canonical, normalized GridMap instance.

    Normalization goals:
      - Ensure validation is applied
      - Ensure obstacles are canonicalized (set)
      - Ensure JSON representation is stable through round-trip

    Implementation uses GridMap.to_json_dict() then from_json_dict()
    to enforce canonical structure.
    """
    return GridMap.from_json_dict(grid_map.to_json_dict())


def convert_json_dict_to_gridmap(data: Dict[str, Any]) -> GridMap:
    """
    Convert a JSON dict (already validated or raw) into a GridMap.
    """
    return GridMap.from_json_dict(data)


def convert_gridmap_to_json_dict(grid_map: GridMap) -> Dict[str, Any]:
    """
    Convert a GridMap into a JSON-serializable dict.
    """
    return grid_map.to_json_dict()