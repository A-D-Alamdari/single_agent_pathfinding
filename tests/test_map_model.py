from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.sapf.core.map import GridMap
from src.sapf.core.exceptions import MapValidationError
from src.sapf.generator.generate import generate_map, generate_random_obstacles


def test_valid_map_construction() -> None:
    m = GridMap(width=5, height=4, obstacles={(1, 1), (2, 2)}, start=(0, 0), goal=(4, 3))

    assert m.width == 5
    assert m.height == 4
    assert m.in_bound((4, 3))
    assert m.is_blocked((1, 1))
    assert not m.is_blocked((0, 0))


@pytest.mark.parametrize(
    "width,height",
    [(0, 5), (-1, 5), (5, 0), (5, -2)]
)
def test_invalid_map_construction(width: int, height: int) -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=width, height=height)


def test_start_out_of_bounds() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, start=(3, 0))


def test_goal_out_of_bounds() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, goal=(0, 3))


def test_obstacle_out_of_bounds() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, obstacles={(2, 2), (3, 1)})


def test_start_on_obstacle() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, obstacles={(1, 1)}, start=(1, 1))


def test_goal_on_obstacle() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, obstacles={(2, 2)}, goal=(2, 2))


def test_start_equals_goal_invalid() -> None:
    with pytest.raises(MapValidationError):
        GridMap(width=3, height=3, start=(1, 1), goal=(1, 1))


def test_to_json_dict_roundtrip() -> None:
    m1 = GridMap(width=5, height=5, obstacles={(2, 2), (1, 3)}, start=(0, 0), goal=(4, 4))
    d = m1.to_json_dict()
    m2 = GridMap.from_json_dict(d)
    assert m2 == m1


def test_from_json_dict_rejects_bad_schema() -> None:
    with pytest.raises(MapValidationError):
        GridMap.from_json_dict("not-a-dict")  # type: ignore[arg-type]

    with pytest.raises(MapValidationError):
        GridMap.from_json_dict({"width": 5})  # missing height

    with pytest.raises(MapValidationError):
        GridMap.from_json_dict({"width": 5, "height": 5, "start": [0, "y"]})  # type: ignore[list-item]


def test_save_load_json(tmp_path: Path) -> None:
    m1 = GridMap(width=4, height=3, obstacles={(1, 1)}, start=(0, 0), goal=(3, 2))
    p = tmp_path / "map.json"

    # via io module (through convenience wrapper is also fine)
    m1.save_json(p)
    assert p.exists()

    m2 = GridMap.load_json(p)
    assert m2 == m1

    # Ensure JSON is valid and human-readable
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded["width"] == 4
    assert loaded["height"] == 3


def test_save_load_pickle(tmp_path: Path) -> None:
    m1 = GridMap(width=6, height=6, obstacles={(2, 2), (2, 3)}, start=(0, 0), goal=(5, 5))
    p = tmp_path / "map.pkl"

    m1.save_pickle(p)
    assert p.exists()

    m2 = GridMap.load_pickle(p)
    assert m2 == m1


def test_generate_map_helper() -> None:
    m = generate_map(5, 5, start=(0, 0), goal=(4, 4), obstacles=[(1, 1), (2, 2)])
    assert isinstance(m, GridMap)
    assert m.start == (0, 0)
    assert m.goal == (4, 4)
    assert (2, 2) in m.obstacles


def test_random_obstacles_seed_reproducible() -> None:
    obs1 = generate_random_obstacles(10, 10, start=(0, 0), goal=(9, 9), obstacle_ratio=0.25, seed=123)
    obs2 = generate_random_obstacles(10, 10, start=(0, 0), goal=(9, 9), obstacle_ratio=0.25, seed=123)
    assert obs1 == obs2
    assert (0, 0) not in obs1
    assert (9, 9) not in obs1


def test_random_obstacles_ratio_bounds() -> None:
    with pytest.raises(ValueError):
        generate_random_obstacles(5, 5, obstacle_ratio=-0.1)
    with pytest.raises(ValueError):
        generate_random_obstacles(5, 5, obstacle_ratio=1.1)
