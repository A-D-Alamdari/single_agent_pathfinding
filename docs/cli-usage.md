# README snippet (CLI examples)

## CLI usage

Run an algorithm on a map (JSON or pickle auto-detected by extension):

```bash
python -m single_agent_pathfinding.cli --map examples/map.json --algo astar --diagonal false --step false
```

Run in step mode (consumes the step generator) and print per-expansion logs:

```bash
python -m single_agent_pathfinding.cli --map examples/map.json --algo dijkstra --diagonal false --step true --print-steps true
```

Save the resulting path to a JSON file:

```bash
python -m single_agent_pathfinding.cli --map examples/map.pkl --algo bfs --diagonal false --step false --save-path outputs/path.json
```

Exit codes:

* `0` if a path is found.
* `1` for argument / runtime errors (reported by argparse)
* `2` if no path exists

