from __future__ import annotations
import random
import math
from typing import List, Tuple

import config
from core.environment import Environment, Cell
from core.pheromone import PheromoneGrid


class Ant:
    def __init__(self,
                 env: Environment,
                 pher: PheromoneGrid):
        self.env = env
        self.pher = pher
        self.reset()

    def step(self) -> None:
        if self.state == "searching":
            self._search_step()
        else:
            self._return_step()

    def _search_step(self) -> None:
        # Timeout check
        self.steps_since_nest += 1
        if self.steps_since_nest > config.SEARCH_TIMEOUT:
            # Give up → return home WITHOUT laying pheromone / stats
            self.skip_deposit = True
            self.deposit_path = []  # nothing to record
            self.return_stack = self.path[-2::-1]  # retrace
            self.state = "returning"
            return

        # Candidate moves (4-neighbourhood) and exclude the tile we just came from so the ant does not oscillate back & forth
        neighbours = self.env.neighbours(self.pos)

        if len(self.path) > 1:
            prev = self.path[-2]
            if prev in neighbours:
                filtered = [n for n in neighbours if n != prev]
                # Only use the filtered list if at least one alternative exists
                if filtered:
                    neighbours = filtered

        if not neighbours:
            self.reset()
            return

        # Transition probabilities
        probs = [(self.pher.tau[n] ** config.ALPHA) *
                 (self._heuristic(n) ** config.BETA)
                 for n in neighbours]
        total = sum(probs)

        if total == 0 or random.random() < config.EPSILON:
            nxt = random.choice(neighbours)
        else:
            r, s = random.random() * total, 0.0
            for n, p in zip(neighbours, probs):
                s += p
                if r <= s:
                    nxt = n
                    break

        self._move_to(nxt)

        cell_here = self.env.grid[self.pos]

        # Fresh food
        if cell_here == Cell.FOOD:
            exhausted = self.env.consume_food(self.pos, self.pher)
            if exhausted:
                for x, y in self.path:
                    self.pher.tau[x, y] = config.TAU0
                self.skip_deposit = True

            self.state = "returning"
            self.deposit_path = list(self.path)
            self.return_stack = self.path[-2::-1]  # back home

        # Depleted food source
        elif cell_here == Cell.DEPLETED:
            # treat as failure: no stats, no deposit, clear the trail
            for x, y in self.path:
                self.pher.tau[x, y] = config.TAU0
            self.skip_deposit = True
            self.deposit_path = []  # nothing to record

            self.state = "returning"
            self.return_stack = self.path[-2::-1]

    def _return_step(self) -> None:
        nxt = self.return_stack.pop(
            0) if self.return_stack else config.NEST_POS
        self._move_to(nxt)

        if self.env.grid[self.pos] == Cell.NEST:
            # Only register / deposit when a real food tour exists
            if self.deposit_path:
                self.env.record_path(self.deposit_path[-1],
                                     self.deposit_path)
                if not self.skip_deposit:
                    L = max(1, len(self.deposit_path))
                    self.pher.deposit(self.deposit_path, config.Q / L)
            self.reset()

    # Helpers
    def _move_to(self, nxt: Tuple[int, int]) -> None:
        self.pos = nxt
        self.path.append(nxt)

    def _heuristic(self, nxt: Tuple[int, int]) -> float:
        if not self.env.food_positions:
            return 0.0
        x, y = nxt
        d_min = min(math.hypot(fx - x, fy - y)
                    for fx, fy in self.env.food_positions)
        return 1.0 / (d_min + 1e-6)

    def reset(self) -> None:
        self.pos = config.NEST_POS
        self.state = "searching"
        self.path: List[Tuple[int, int]] = [self.pos]
        self.return_stack: List[Tuple[int, int]] = []
        self.deposit_path: List[Tuple[int, int]] = []
        self.skip_deposit = False
        self.steps_since_nest = 0  # counter for timeout
