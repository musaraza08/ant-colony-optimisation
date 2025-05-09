# Ant Colony Optimization Simulation

## Required Python Packages

To run this simulation, you'll need the following Python packages:
- numpy
- matplotlib
- pygame
- pandas

You can install them using pip:
```
pip install numpy matplotlib pygame pandas
```

## Running the Simulation

### Basic Simulation

To run the basic ant colony simulation with visualization, you can set configurations for the simulation in the config.py file before running:

```
python main.py
```

This will open a window showing the ants searching for food and building pheromone trails.

### Parameter Experiments

To run batch experiments testing different parameter values, you can add the configurations you need to test in the param grid in batch.py and then run:

```
python batch.py
```

This will run a series of simulations with different parameter combinations and save the results to a CSV file.

### Algorithm Comparison

To compare the Ant Colony algorithm with A* pathfinding:

```
python a_star_comparison.py
```

This will run both algorithms on identical scenarios with varying numbers of obstacles and compare their performance.


## Configuration

You can modify the simulation parameters in `config.py`, including:
- Grid size
- Number of ants
- ACO parameters (ALPHA, BETA, RHO, etc.)
- Number of food sources and obstacles

## Key Files

- `main.py`: Main simulation with visualization
- `config.py`: Configuration parameters
- `simulation.py`: Core simulation logic
- `experiment.py`: Framework for running controlled experiments
- `batch.py`: Batch processing of multiple experiments
- `a_star_comparison.py`: Direct comparison between Ant Colony and A*