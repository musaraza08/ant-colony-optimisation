import time
import random
import csv
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

import config
from simulation import Simulation


def run_experiment(params: Dict[str, Any], max_ticks: int = 10000) -> List[Dict[str, Any]]:
    # Headless mode experiment runner

    # Save original config values
    original_values = {}
    for key in params:
        if hasattr(config, key):
            original_values[key] = getattr(config, key)

    # Apply experiment parameters
    for key, value in params.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Config has no attribute '{key}'")

    sim = Simulation()

    # Data points to track throughput over time
    data_points = []
    last_collected = 0
    # Calculate throughput over 60 tick windows (0.5 sec at 120 FPS)
    window_size = 60

    for tick in range(max_ticks):
        sim.tick()

        # Record data point every window_size ticks
        if tick % window_size == 0 and tick > 0:
            current_collected = sim.food_collected
            food_in_window = current_collected - last_collected
            throughput = food_in_window / \
                (window_size / config.FPS)  # food per second

            data_point = {
                'tick': tick,
                'time_seconds': tick / config.FPS,
                'food_collected': current_collected,
                'throughput': throughput,
                'seed': sim.seed
            }

            for k, v in params.items():
                data_point[f'param_{k}'] = v

            data_points.append(data_point)
            last_collected = current_collected

        # Stop when all food is collected
        if sim.all_food_tick is not None:
            break

    # Added final data point if simulation ended
    if sim.all_food_tick is not None and data_points and data_points[-1]['tick'] < sim.all_food_tick:
        data_point = {
            'tick': sim.all_food_tick,
            'time_seconds': sim.all_food_tick / config.FPS,
            'food_collected': sim.food_collected,
            'throughput': sim.throughput,
            'seed': sim.seed
        }
        for k, v in params.items():
            data_point[f'param_{k}'] = v
        data_points.append(data_point)

    for key, value in original_values.items():
        setattr(config, key, value)

    return data_points


def save_results(all_data_points: List[Dict[str, Any]], filename: str) -> None:
    if not all_data_points:
        return

    fieldnames = list(all_data_points[0].keys())

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data_point in all_data_points:
            writer.writerow(data_point)
