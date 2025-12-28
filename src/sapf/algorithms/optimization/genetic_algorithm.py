from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...core.map import GridMap
from ...core.types import Coord

# Directions: (dx, dy)
MOVES = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # U, D, L, R


@dataclass
class Individual:
    genes: List[int]  # List of indices into MOVES
    fitness: float = 0.0
    path: List[Coord] = None
    reached_goal: bool = False
    hit_obstacle: bool = False


class GeneticPathfindingAlgorithm(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "Genetic Algorithm (Evolutionary)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("GA requires start and goal.")

        start = grid_map.start
        goal = grid_map.goal

        # --- Parameters ---
        POPULATION_SIZE = 100
        MUTATION_RATE = 0.05
        # Max path length (chromosome length).
        # Heuristic: Manhatten distance * 2 usually gives enough wiggle room.
        min_dist = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        GENE_LENGTH = max(20, min_dist * 3)
        MAX_GENERATIONS = 500

        # --- Helper: Decode Genes to Path ---
        def decode(ind: Individual) -> None:
            """Translate genes (moves) into actual coordinates on the map."""
            curr = start
            path = [curr]
            ind.reached_goal = False
            ind.hit_obstacle = False

            for gene_idx in ind.genes:
                dx, dy = MOVES[gene_idx]
                next_pos = (curr[0] + dx, curr[1] + dy)

                # Check bounds/obstacles
                if not grid_map.in_bound(next_pos) or grid_map.is_blocked(next_pos):
                    ind.hit_obstacle = True
                    break  # Stop moving if hit wall

                curr = next_pos
                path.append(curr)
                if curr == goal:
                    ind.reached_goal = True
                    break

            ind.path = path

        # --- Helper: Calculate Fitness ---
        def evaluate(ind: Individual) -> None:
            """
            Fitness logic:
            1. Reward getting close to goal.
            2. Huge reward for reaching goal.
            3. Penalty for length (to encourage shorter paths).
            """
            last_pos = ind.path[-1]
            dist = abs(last_pos[0] - goal[0]) + abs(last_pos[1] - goal[1])

            if ind.reached_goal:
                # Score = 1000 - path_length (Shorter is better)
                ind.fitness = 1000.0 - len(ind.path)
            else:
                # Score = 1 / (distance + 1)
                # We square distance to punish being far away more severely
                ind.fitness = 1.0 / (dist ** 2 + 1)

                if ind.hit_obstacle:
                    ind.fitness *= 0.1  # Penalty for crashing

        # --- Initialization ---
        population = []
        for _ in range(POPULATION_SIZE):
            genes = [random.choice(range(4)) for _ in range(GENE_LENGTH)]
            ind = Individual(genes=genes)
            decode(ind)
            evaluate(ind)
            population.append(ind)

        def _run_steps() -> Iterator[SearchStep]:
            generation = 0
            best_ever_path = []

            while generation < MAX_GENERATIONS:
                # Sort by fitness descending
                population.sort(key=lambda x: x.fitness, reverse=True)
                best_ind = population[0]

                # Visualization:
                # open_set = the head positions of the entire population (The Swarm)
                # best_path = the path of the best individual so far
                current_heads = [ind.path[-1] for ind in population]

                status = SearchStatus.RUNNING
                log_msg = f"Gen {generation}: Best Fitness={best_ind.fitness:.4f}"

                if best_ind.reached_goal:
                    status = SearchStatus.FOUND
                    log_msg = f"Gen {generation}: Goal Reached! Optimizing..."
                    best_ever_path = best_ind.path

                yield SearchStep(
                    current=start,
                    open_set=current_heads,  # Show the swarm
                    closed_set=[],  # Not used in GA
                    open_added=[],
                    best_path=best_ind.path,
                    log=log_msg,
                    status=status
                )

                # If we found a perfect path (short and reaches goal), we could stop,
                # but GA usually runs longer to optimize.
                # Let's stop if we have a stable solution for a while or hit max gens.
                # For this demo, just run until user stops or max gens.

                # --- Selection (Elitism + Roulette/Tournament) ---
                new_pop = []

                # Elitism: Keep top 10%
                elite_count = int(POPULATION_SIZE * 0.1)
                new_pop.extend(population[:elite_count])

                # Mating pool (top 50%)
                pool = population[: int(POPULATION_SIZE * 0.5)]

                while len(new_pop) < POPULATION_SIZE:
                    parent1 = random.choice(pool)
                    parent2 = random.choice(pool)

                    # Crossover (Single Point)
                    cut = random.randint(0, GENE_LENGTH - 1)
                    child_genes = parent1.genes[:cut] + parent2.genes[cut:]

                    # Mutation
                    for i in range(len(child_genes)):
                        if random.random() < MUTATION_RATE:
                            child_genes[i] = random.choice(range(4))

                    child = Individual(genes=child_genes)
                    decode(child)
                    evaluate(child)
                    new_pop.append(child)

                population[:] = new_pop
                generation += 1

            # End
            yield SearchStep(
                current=start,
                open_set=[],
                closed_set=[],
                open_added=[],
                best_path=best_ever_path,
                log="Max generations reached.",
                status=SearchStatus.FOUND if best_ever_path else SearchStatus.NO_PATH
            )

        if step_mode:
            return _run_steps()

        # Non-step mode (not really recommended for GA, but supported)
        final_path = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                final_path = step.best_path
        return final_path