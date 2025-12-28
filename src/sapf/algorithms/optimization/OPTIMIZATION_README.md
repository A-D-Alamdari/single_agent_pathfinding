# Genetic Algorithm

## Implementation Strategy

To make GA fit to `PathfindingAlgorithm` structure:

1. **Chromosome**: A path is represented as a list of moves (e.g., Up, Down, Left, Right).

2. **Population**: We maintain, say, 50 random paths.

3. **Step Mode**: Each "step" in the GUI corresponds to one generation of evolution.

4. **Visualization**:

    * **Open Set**: We can use this to render the current position of every individual in the population (creating a swarm effect). 
    * **Best Path**: The fittest individual of the current generation.


## How it Looks in GUI

When you run this:

1. **Blue Squares (Open Set)**: You will see a cloud of blue squares expanding from the start. These are the "heads" of the 100 agents in the population.

2. **Yellow Line (Path)**: This is the path of the single fittest agent in that generation.

3. **Behavior**: You will watch the path flail around randomly at first, then "learn" to avoid obstacles, and eventually snap to the goal. It might wiggle a lot—that's the nature of GA!


-------