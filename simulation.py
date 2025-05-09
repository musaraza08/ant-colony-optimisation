import random
from typing import List, Tuple, Dict, Optional

import config
from core.environment import Environment
from core.pheromone import PheromoneGrid
from core.ant import Ant


class Simulation:

    def __init__(self):
        # Set random seed for reproducibility
        if config.RANDOM_SEED is None:
            self.seed = random.randint(0, 2**32 - 1)
        else:
            self.seed = config.RANDOM_SEED
        random.seed(self.seed)

        # Initialize core components
        self.env = Environment(config.GRID_W, config.GRID_H)
        self.pher = PheromoneGrid(config.GRID_W, config.GRID_H, config.TAU0)
        self.ants = [Ant(self.env, self.pher)
                     for _ in range(config.N_ANTS)]

        # Metrics
        self.tick_count = 0
        self.first_food_tick = None
        self.all_food_tick = None
        self.food_collected = 0
        self.collection_history = []
        self.best_paths = None

    def tick(self) -> None:
        # Increment tick count
        self.tick_count += 1
        before = self.env.remaining_food()

        # Update all ants
        for ant in self.ants:
            ant.step()

        # Evaporate pheromones
        self.pher.evaporate(config.RHO)

        # Update metrics
        after = self.env.remaining_food()
        delta = before - after

        if delta > 0:
            self.food_collected += delta
            self.collection_history.append(
                (self.tick_count, self.food_collected))
            if self.first_food_tick is None:
                self.first_food_tick = self.tick_count

        if after == 0 and self.all_food_tick is None:
            self.all_food_tick = self.tick_count

        # Calculate best paths when all food is collected
        if (self.best_paths is None and
                self.env.remaining_food() == 0 and
                self.env.paths_by_food):
            self.best_paths = {
                food: self._best_path(paths)
                for food, paths in self.env.paths_by_food.items()
                if paths
            }

    @staticmethod
    def _best_path(paths: List[List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
        # Return the shortest recorded forward tour
        return min(paths, key=len)

    def seconds(self, ticks: Optional[int]) -> str:
        # Convert ticks to seconds string representation
        if ticks is None:
            return "—"
        return f"{ticks / config.FPS:.2f}s"

    @property
    def throughput(self) -> float:
        # Calculate food collection rate (items per second)
        if self.first_food_tick is None:
            return 0.0
        end = (self.all_food_tick or self.tick_count)
        secs = (end - self.first_food_tick) / config.FPS
        return 0.0 if secs == 0 else self.food_collected / secs
