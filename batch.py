import os
import time
import itertools
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any, List, Tuple

from experiment import run_experiment, save_results


def parameter_grid(**param_ranges) -> List[Dict[str, Any]]:
    # Generate a grid of parameter combinations
    keys = param_ranges.keys()
    values = param_ranges.values()
    combinations = list(itertools.product(*values))
    return [dict(zip(keys, combo)) for combo in combinations]


def run_batch(param_sets: List[Dict[str, Any]],
              max_ticks: int = 10000,
              max_workers: int = None) -> List[Dict[str, Any]]:
    # Run multiple experiments in parallel
    start_time = time.time()
    total = len(param_sets)
    print(f"Starting batch run with {total} experiments...")

    all_data_points = []

    # Run experiments in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submiting all experiments
        future_to_params = {
            executor.submit(run_experiment, params, max_ticks): params
            for params in param_sets
        }

        # Collecting results as they complete
        completed = 0
        for future in future_to_params:
            data_points = future.result()
            all_data_points.extend(data_points)

            # Progress update
            completed += 1
            print(f"Completed {completed}/{total} experiments "
                  f"({completed/total*100:.1f}%)")

    elapsed = time.time() - start_time
    print(f"Batch completed in {elapsed:.2f} seconds")
    return all_data_points


if __name__ == "__main__":
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    # Define parameter ranges to explore
    param_grid = parameter_grid(
        # ALPHA=[0.5, 1.0, 2.0],
        # BETA=[1.0, 3.0, 5.0],
        RHO=[0.02, 0.05, 0.1, 0.2],
        # EPSILON=[0.1, 0.3, 0.5],
        # N_ANTS=[25, 50, 100],
        # NUM_WALLS=[0, 10, 20, 30],
        # NUM_FOOD_SOURCES=[1, 2, 3]
    )

    # Run the batch
    all_data_points = run_batch(param_grid, max_ticks=5000)

    # Save results to CSV
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    csv_file = f"{output_dir}/throughput_over_time_{timestamp}.csv"
    save_results(all_data_points, csv_file)
    print(f"Results saved to {csv_file}")

    # Print summary
    print(
        f"Recorded {len(all_data_points)} data points across {len(param_grid)} configurations")
