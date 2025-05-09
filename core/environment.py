from __future__ import annotations
import random
import math
from enum import IntEnum
from typing import List, Tuple, Dict, Set

import numpy as np
import config


class Cell(IntEnum):
    EMPTY = 0
    WALL = 1
    NEST = 2
    FOOD = 3
    DEPLETED = 4


class Environment:

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h

        # Static layers
        self.grid = np.full((w, h), Cell.EMPTY, dtype=np.uint8)
        self.grid[config.NEST_POS] = Cell.NEST

        # Food
        self.food_positions: Set[Tuple[int, int]]
        if getattr(config, "FOOD_POSITIONS", None):
            self.food_positions = set(config.FOOD_POSITIONS)
        else:
            self.food_positions = set(self._random_food_positions(
                getattr(config, "NUM_FOOD_SOURCES", 3))
            )

        # Walls
        self._generate_walls()

        # Food capacity bookkeeping
        self.food_left: Dict[Tuple[int, int], int] = {
            pos: config.FOOD_CAPACITY for pos in self.food_positions
        }
        self.total_food = sum(self.food_left.values())

        for fx, fy in self.food_positions:
            self.grid[fx, fy] = Cell.FOOD

        # successful forward tours grouped by destination food cell
        # (filled by Ant objects via `record_path`)
        self.paths_by_food: Dict[Tuple[int, int],
                                 List[List[Tuple[int, int]]]] = {}

    # Helper methods
    def neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """4-neighbourhood (no diagonals) that ignores walls."""
        x, y = pos
        cand = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(i, j) for i, j in cand
                if 0 <= i < self.w and 0 <= j < self.h
                and self.grid[i, j] != Cell.WALL]

    def remaining_food(self) -> int:
        return sum(self.food_left.values())

    def consume_food(self,
                     pos: Tuple[int, int],
                     pher) -> bool:
        if pos not in self.food_left:
            return False

        self.food_left[pos] -= 1
        if self.food_left[pos] > 0:
            return False

        # Exhaust = keep the tile, but in "greyed-out" state
        self.grid[pos] = Cell.DEPLETED
        del self.food_left[pos]
        self.food_positions.discard(pos)
        pher.tau[pos] = config.TAU0
        return True

    def record_path(self,
                    food_pos: Tuple[int, int],
                    path: List[Tuple[int, int]]) -> None:
        self.paths_by_food.setdefault(food_pos, []).append(list(path))

    # Internals
    def _random_food_positions(self, n: int) -> List[Tuple[int, int]]:
        coords = set()
        while len(coords) < n:
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            if (x, y) != config.NEST_POS:
                coords.add((x, y))
        return list(coords)

    def _generate_walls(self) -> None:
        num = getattr(config, "NUM_WALLS", 0)
        min_len = getattr(config, "WALL_MIN_LEN", 3)
        max_len = getattr(config, "WALL_MAX_LEN", 10)

        for _ in range(num):
            for _attempt in range(30):  # give up if cannot place
                length = random.randint(min_len, max_len)
                if random.random() < 0.5:  # horizontal
                    y = random.randint(0, self.h - 1)
                    x0 = random.randint(0, self.w - length)
                    cells = [(x0 + i, y) for i in range(length)]
                else:  # vertical
                    x = random.randint(0, self.w - 1)
                    y0 = random.randint(0, self.h - length)
                    cells = [(x, y0 + i) for i in range(length)]

                # Overlap check
                if any(c == config.NEST_POS or c in self.food_positions
                       or self.grid[c] != Cell.EMPTY for c in cells):
                    continue

                for c in cells:
                    self.grid[c] = Cell.WALL
                break
