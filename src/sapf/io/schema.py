from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, ValidationError, field_validator

from ..core.exceptions import MapValidationError
from ..core.types import Coord


class MapJsonV1(BaseModel):
    """
    Versioned JSON schema for GridMap.

    Stored representation:
      - start/goal: [x, y] or null
      - obstacles: list of [x, y]
    """

    version: int = Field(default=1, description="Schema version")
    width: PositiveInt
    height: PositiveInt

    start: Optional[List[int]] = None
    goal: Optional[List[int]] = None
    obstacles: List[List[int]] = Field(default_factory=list)

    @field_validator("start", "goal")
    @classmethod
    def _validate_start_goal(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is None:
            return None
        if len(v) != 2:
            raise ValueError("must be [x, y]")
        if not all(isinstance(a, int) for a in v):
            raise ValueError("coordinates must be integers")
        return v

    @field_validator("obstacles")
    @classmethod
    def _validate_obstacles(cls, v: List[List[int]]) -> List[List[int]]:
        for item in v:
            if len(item) != 2:
                raise ValueError("each obstacle must be [x, y]")
            if not all(isinstance(a, int) for a in item):
                raise ValueError("obstacle coordinates must be integers")
        return v

    def to_core_dict(self) -> dict:
        """
        Convert to the dict format expected by GridMap.from_json_dict().
        """
        return {
            "width": int(self.width),
            "height": int(self.height),
            "start": self.start,
            "goal": self.goal,
            "obstacles": self.obstacles,
        }

    @staticmethod
    def from_core_dict(d: dict) -> "MapJsonV1":
        """
        Convert from GridMap.to_json_dict() output into a schema object.
        """
        payload = {
            "version": 1,
            "width": d.get("width"),
            "height": d.get("height"),
            "start": d.get("start"),
            "goal": d.get("goal"),
            "obstacles": d.get("obstacles", []),
        }
        return MapJsonV1.model_validate(payload)


def validate_map_json(data: dict) -> MapJsonV1:
    """
    Validate arbitrary JSON object and return a parsed schema model.

    Raises MapValidationError with readable message for CLI/GUI.
    """
    try:
        model = MapJsonV1.model_validate(data)
    except ValidationError as e:
        raise MapValidationError(f"Invalid map JSON schema: {e}") from e

    if model.version != 1:
        raise MapValidationError(f"Unsupported map JSON version: {model.version}. Expected 1.")
    return model