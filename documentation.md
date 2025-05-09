# Ant Colony Optimization Simulation Documentation

## Overview

This project implements an Ant Colony Optimization (ACO) simulation that demonstrates how simple agents following basic rules can collectively solve complex pathfinding problems. The simulation also includes a comparison with the A* pathfinding algorithm to benchmark performance.

The ACO algorithm is inspired by the foraging behavior of real ants, which use pheromone trails to communicate and find efficient paths between their nest and food sources. In this simulation, virtual ants explore a grid-based environment, deposit pheromones when they find food, and use these pheromone trails to guide their future exploration.

This project serves both as a demonstration of emergent collective intelligence and as a framework for experimenting with different ACO parameters to understand their effects on pathfinding efficiency.

## Project Structure

The project is organized into several modules:

```
ant-colony-simulation/
├── core/                     # Core simulation components
│   ├── ant.py                # Ant agent implementation
│   ├── environment.py        # Environment representation
│   └── pheromone.py          # Pheromone grid management
├── visual/                   # Visualization components
│   └── renderer.py           # Pygame rendering
├── astar.py                  # A* pathfinding implementation
├── batch.py                  # Batch experiment runner
├── config.py                 # Global configuration
├── a_star_comparison.py      # A* vs Ant Colony comparison
├── experiment.py             # Headless experiment runner
├── main.py                   # Main simulation with visualization
└── simulation.py             # Simulation coordinator
```


## Core Components

### `config.py`

Contains all global configuration parameters for the simulation:

- **Grid/Window Parameters**: Defines the size of the simulation environment (50x50 grid)
- **Colony Parameters**: Number of ants (50) and nest position (center of grid)
- **ACO Parameters**: Controls the behavior of the ant colony algorithm
  - `ALPHA = 1.0`: Influence of pheromone on ant decisions
  - `BETA = 3.0`: Influence of heuristic (distance) on ant decisions
  - `RHO = 0.05`: Pheromone evaporation rate
  - `Q = 100`: Amount of pheromone deposited per tour
  - `TAU0 = 0.1`: Initial pheromone trail value
  - `EPSILON = 0.3`: Probability of random exploration
- **Environment Parameters**: Food sources, obstacles, and their properties

### `core/environment.py`

Represents the environment where ants operate:

- `Environment` class: Manages the grid-based world with different cell types
  - `Cell` enum: Defines cell types (EMPTY, WALL, NEST, FOOD, DEPLETED)
  - Handles food sources and obstacles
  - Provides methods for querying neighbors and consuming food
  - Tracks successful paths found by ants

Key methods:
- `neighbours(pos)`: Returns valid neighboring positions (4-neighborhood)
- `consume_food(pos, pher)`: Removes one unit of food from a position
- `record_path(food_pos, path)`: Records a successful path to food
- `_generate_walls()`: Creates random wall obstacles

### `core/pheromone.py`

Manages the pheromone levels across the grid:

- `PheromoneGrid` class: Stores and updates pheromone values
  - Uses a 2D NumPy array to efficiently store pheromone levels
  - Provides methods for evaporation and deposition

Key methods:
- `evaporate(rho)`: Reduces all pheromone levels by a factor of (1-rho)
- `deposit(path, amount)`: Adds pheromone along a path

### `core/ant.py`

Implements the individual ant agents:

- `Ant` class: Represents a single ant with its own state and behavior
  - Maintains state (searching/returning)
  - Implements the ACO decision rule for choosing next moves
  - Handles food collection and pheromone deposition

Key methods:
- `step()`: Updates the ant's state for one time step
- `_search_step()`: Handles behavior when searching for food
- `_return_step()`: Handles behavior when returning to nest
- `_heuristic(pos)`: Calculates the heuristic value (inverse distance to nearest food)

## Simulation Coordination

### `simulation.py`

Coordinates the environment, pheromone grid, and ants:

- `Simulation` class: Main coordinator for the simulation
  - Initializes all components (environment, pheromone grid, ants)
  - Updates the simulation state
  - Tracks metrics (food collected, time to find food, etc.)

Key methods:
- `tick()`: Advances the simulation by one time step
- `throughput`: Property that calculates food collection rate

## Visualization

### `visual/renderer.py`

Handles the visualization of the simulation:

- `draw()`: Renders the current simulation state using Pygame
  - Draws the pheromone heat map
  - Renders cells (nest, food, walls)
  - Displays ants
  - Shows metrics and best paths

### `main.py`

Entry point for the interactive simulation:

- Initializes Pygame
- Creates the simulation
- Runs the main loop (handling events, updating simulation, rendering)

## Experimentation Framework

### `experiment.py`

Provides a framework for running controlled experiments:

- `run_experiment()`: Runs a simulation with specific parameters
  - Takes parameter overrides as input
  - Collects performance metrics over time
  - Returns data points for analysis

- `save_results()`: Saves experiment results to a CSV file

### `batch.py`

Enables batch processing of multiple experiments:

- `parameter_grid()`: Generates combinations of parameters to test
- `run_batch()`: Runs multiple experiments in parallel
  - Uses ProcessPoolExecutor for parallelization
  - Collects and aggregates results

## Algorithm Comparison

### `astar.py`

Implements the A* pathfinding algorithm for comparison:

- `AStar` class: A* pathfinding implementation
  - Uses a priority queue to explore paths efficiently
  - Calculates paths using f(n) = g(n) + h(n)
    - g(n): Cost from start to current node
    - h(n): Heuristic estimate from current node to goal

Key methods:
- `find_path(start, goal)`: Finds the shortest path between two points
- `heuristic(a, b)`: Calculates the Euclidean distance between points

### `a_star_comparison.py`

Provides a direct comparison between A* and Ant Colony algorithms:

- Runs both algorithms on identical scenarios
- Measures performance metrics (time to find path, path length)
- Generates comparison data for visualization

## Ant Colony Optimization Algorithm

The ACO algorithm is implemented through the collective behavior of individual ants:

1. **Initialization**:
   - Ants start at the nest
   - Initial pheromone levels are set to TAU0

2. **Ant Decision Rule**:
   - Ants choose their next move based on:
     ```
     P(i,j) = [τ(i,j)]^α * [η(i,j)]^β / Σ [τ(i,k)]^α * [η(i,k)]^β
     ```
     Where:
     - τ(i,j) is the pheromone level
     - η(i,j) is the heuristic value (1/distance to nearest food)
     - α and β control the relative influence of pheromone vs. heuristic

   - With probability EPSILON, ants make a random move (exploration)

3. **Pheromone Update**:
   - Pheromone evaporates at rate RHO:
     ```
     τ(i,j) = (1-ρ) * τ(i,j)
     ```
   
   - Ants deposit pheromone along successful paths:
     ```
     τ(i,j) = τ(i,j) + Q/L
     ```
     Where:
     - Q is a constant
     - L is the path length

4. **Convergence**:
   - Over time, shorter paths receive more pheromone
   - Ants increasingly follow these stronger trails
   - The colony converges on optimal or near-optimal paths

## Performance Metrics

The simulation tracks several key performance metrics:

1. **Time to First Food**: How quickly the first ant finds food
2. **Time to All Food**: How long it takes to collect all food
3. **Throughput**: Rate of food collection (items per second)
4. **Path Length**: Length of paths found by ants

These metrics allow for quantitative comparison between different parameter settings and between the Ant Colony and A* algorithms.