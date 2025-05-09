import os
import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any

from astar import AStar
from experiment import run_experiment
from config import GRID_W, GRID_H


def generate_random_walls(num_walls: int, grid_width: int = 50, grid_height: int = 50) -> List[Tuple[int, int]]:
    obstacles = set()

    # Generate random walls
    for _ in range(num_walls):
        # Random starting position
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)

        # Random length between 5-15 tiles
        length = random.randint(5, 15)

        # Random direction (horizontal or vertical)
        direction = random.choice(["horizontal", "vertical"])

        # Create the wall
        for i in range(length):
            if direction == "horizontal":
                pos = (min(x + i, grid_width - 1), y)
            else:
                pos = (x, min(y + i, grid_height - 1))

            obstacles.add(pos)

    return list(obstacles)


def generate_random_food_sources(num_sources: int, obstacles: List[Tuple[int, int]],
                                 grid_width: int = 50, grid_height: int = 50) -> List[Tuple[int, int]]:
    food_positions = []
    obstacles_set = set(obstacles)
    nest_pos = (grid_width // 2, grid_height // 2)

    while len(food_positions) < num_sources:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)
        pos = (x, y)

        # Make sure it's not on an obstacle or the nest
        if pos not in obstacles_set and pos != nest_pos and pos not in food_positions:
            food_positions.append(pos)

    return food_positions


def run_direct_comparison(num_walls_list: List[int], num_trials: int = 5) -> pd.DataFrame:
    """
    Run a direct comparison between Ant Colony and A* on identical scenarios
    """
    results = []

    # Get nest position from config
    nest_pos = (GRID_W // 2, GRID_H // 2)

    for num_walls in num_walls_list:
        print(f"Testing with {num_walls} walls...")

        for trial in range(num_trials):
            print(f"  Trial {trial+1}/{num_trials}")

            # Set random seed for reproducibility within this trial
            random_seed = trial + 1 + 1
            random.seed(random_seed)
            np.random.seed(random_seed)

            # Generate obstacles
            obstacles = generate_random_walls(num_walls, GRID_W, GRID_H)

            # Generate a single food source
            food_positions = generate_random_food_sources(
                1, obstacles, GRID_W, GRID_H)

            if not food_positions:
                print("Error: Could not generate food position")
                continue

            food_pos = food_positions[0]

            # Run A* algorithm
            astar = AStar(GRID_W, GRID_H)
            astar.set_obstacles(obstacles)

            astar_start_time = time.time()
            astar_path = astar.find_path(nest_pos, food_pos)
            astar_end_time = time.time()

            astar_time = astar_end_time - astar_start_time
            # Subtract 1 because path includes start
            astar_path_length = len(astar_path) - 1 if astar_path else 0

            # Run ant colony simulation using experiment.py
            scenario = {
                'NUM_WALLS': num_walls,
                'NUM_FOOD_SOURCES': 1,
                'RANDOM_SEED': random_seed
            }

            # Run the experiment for a limited number of ticks
            max_ticks = 10000
            data_points = run_experiment(scenario, max_ticks)

            # Find when the first food was collected
            ant_ticks_to_find = None
            for point in data_points:
                if point['food_collected'] > 0:
                    ant_ticks_to_find = point['tick']
                    break

            # Estimate path length based on ticks (this is an approximation)
            # In a real implementation, we would track the actual path
            ant_path_length = ant_ticks_to_find if ant_ticks_to_find else max_ticks

            # Record results
            results.append({
                'num_walls': num_walls,
                'trial': trial,
                'seed': random_seed,
                'food_position': food_pos,
                'astar_time_seconds': astar_time,
                'astar_path_length': astar_path_length,
                'ant_ticks_to_find': ant_ticks_to_find,
                'ant_path_length': ant_path_length
            })

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Save results
    os.makedirs('results', exist_ok=True)
    results_df.to_csv('results/direct_comparison.csv', index=False)

    return results_df


def plot_comparison_charts(df: pd.DataFrame):
    """Generate comparison charts from the results"""
    # Create output directory
    os.makedirs('results/charts', exist_ok=True)

    # Group by number of walls and calculate averages
    grouped = df.groupby('num_walls').agg({
        'astar_time_seconds': 'mean',
        'astar_path_length': 'mean',
        'ant_ticks_to_find': 'mean',
        'ant_path_length': 'mean'
    }).reset_index()

    # Plot time comparison
    plt.figure(figsize=(12, 6))

    x = grouped['num_walls']
    width = 0.35

    # Convert ant ticks to seconds for fair comparison (assuming 60 ticks per second)
    ant_time_seconds = grouped['ant_ticks_to_find'] / 60

    plt.bar(x - width/2, grouped['astar_time_seconds'],
            width, label='A*', color='skyblue')
    plt.bar(x + width/2, ant_time_seconds, width,
            label='Ant Colony', color='salmon')

    plt.xlabel('Number of Walls')
    plt.ylabel('Time to Find Path (seconds)')
    plt.title('Time Comparison: A* vs Ant Colony')
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)

    plt.savefig('results/charts/direct_time_comparison.png')
    plt.close()

    # Plot path length comparison
    plt.figure(figsize=(12, 6))

    plt.bar(x - width/2, grouped['astar_path_length'],
            width, label='A*', color='lightblue')
    plt.bar(x + width/2, grouped['ant_path_length'],
            width, label='Ant Colony', color='lightcoral')

    plt.xlabel('Number of Walls')
    plt.ylabel('Path Length (grid cells)')
    plt.title('Path Length Comparison: A* vs Ant Colony')
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)

    plt.savefig('results/charts/direct_path_comparison.png')
    plt.close()


if __name__ == "__main__":
    # Run comparison with different numbers of walls
    wall_counts = [0, 5, 10, 15, 20, 30]
    results = run_direct_comparison(wall_counts, num_trials=3)

    # Generate charts
    plot_comparison_charts(results)

    print("Direct comparison complete. Results saved to results/direct_comparison.csv")
