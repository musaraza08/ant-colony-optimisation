"""
Pure algorithmic part (no pygame).  Unit-testable!
"""
import math
import random
from enum import IntEnum
from typing import List, Tuple, Dict
from collections import defaultdict     # ← NEW

import numpy as np
import config
from core.environment import Environment
from core.pheromone import PheromoneGrid
from core.ant import Ant


# -------------------------------------------------
# Environment & pheromone representation
# -------------------------------------------------
class Cell(IntEnum):
    EMPTY = 0
    WALL = 1
    NEST = 2
    FOOD = 3


class Environment:
    """Holds the discrete grid with semantic cells."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.grid = np.full((w, h), Cell.EMPTY, dtype=np.uint8)
        self.grid[config.NEST_POS] = Cell.NEST

        # -----------------------------------------------
        # Determine where the food lives:
        #  • Use preset list if it exists and is non-empty
        #  • Otherwise create random, unique locations
        # -----------------------------------------------
        if hasattr(config, "FOOD_POSITIONS") and config.FOOD_POSITIONS:
            self.food_positions = set(config.FOOD_POSITIONS)
        else:
            n = getattr(config, "NUM_FOOD_SOURCES", 3)
            self.food_positions = set(self._random_food_positions(n))

        # ----- random obstacles ---------------------------------------
        self._generate_walls()             # ← place them before food tiles

        # ─── per-tile remaining capacity ───────────────────────────────
        self.food_left: dict[tuple[int, int], int] = {
            (fx, fy): config.FOOD_CAPACITY for fx, fy in self.food_positions
        }
        # remember the initial total so we can show progress later
        self.total_food = sum(self.food_left.values())

        # forward tours grouped by their destination food tile
        #   (coordinate → list of tours)
        self.paths_by_food: dict[tuple[int, int],
                                 list[list[tuple[int, int]]]] = defaultdict(list)

        for fx, fy in self.food_positions:
            self.grid[fx, fy] = Cell.FOOD

    # helper -------------------------------------------------------------
    def _random_food_positions(self, n: int) -> list[tuple[int, int]]:
        """Return `n` unique positions that are not the nest."""
        coords = set()
        while len(coords) < n:
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            if (x, y) == config.NEST_POS:
                continue
            coords.add((x, y))
        return list(coords)

    # add helper just after _random_food_positions
    def consume_food(self, pos: tuple[int, int],
                     pher: "PheromoneGrid") -> bool:
        """
        Remove ONE unit of food.
        Returns True only when the tile has just been exhausted.
        """
        if pos not in self.food_left:
            return False

        self.food_left[pos] -= 1
        exhausted = False
        if self.food_left[pos] <= 0:
            # food exhausted → remove marker and clear pheromone there
            self.grid[pos] = Cell.EMPTY
            del self.food_left[pos]
            self.food_positions.discard(pos)
            pher.tau[pos] = config.TAU0
            exhausted = True
        return exhausted

    # 4-neighbourhood (no diagonals)
    def neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        cand = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(i, j) for i, j in cand
                if 0 <= i < self.w and 0 <= j < self.h
                and self.grid[i, j] != Cell.WALL]

    # quick helper ------------------------------------------------------
    def remaining_food(self) -> int:
        """How many units are still on the map?"""
        return sum(self.food_left.values())

    # -------- record a successful tour --------------------------------
    def record_path(self, food_pos: tuple[int, int],
                    path: list[tuple[int, int]]) -> None:
        """Store one successful forward tour for *this* food source."""
        self.paths_by_food[food_pos].append(list(path))

    # ------------------------------------------------------------------
    def _generate_walls(self):
        """Scatter random vertical / horizontal wall segments."""
        num = getattr(config, "NUM_WALLS", 0)
        min_len = getattr(config, "WALL_MIN_LEN", 3)
        max_len = getattr(config, "WALL_MAX_LEN", 10)

        for _ in range(num):
            for _attempt in range(30):                 # try a few times
                length = random.randint(min_len, max_len)
                if random.random() < 0.5:              # horizontal
                    y = random.randint(0, self.h - 1)
                    x0 = random.randint(0, self.w - length)
                    cells = [(x0 + i, y) for i in range(length)]
                else:                                  # vertical
                    x = random.randint(0, self.w - 1)
                    y0 = random.randint(0, self.h - length)
                    cells = [(x, y0 + i) for i in range(length)]

                # validity test: must be empty & not overlap nest / food
                if any((c == config.NEST_POS) or (c in self.food_positions)
                       for c in cells):
                    continue
                if any(self.grid[c] != Cell.EMPTY for c in cells):
                    continue

                for c in cells:
                    self.grid[c] = Cell.WALL
                break


class PheromoneGrid:
    def __init__(self, w: int, h: int, tau0: float):
        self.tau = np.full((w, h), tau0, dtype=np.float32)

    def evaporate(self, rho: float):
        self.tau *= (1.0 - rho)

    def deposit(self, path: List[Tuple[int, int]], amount: float):
        for (x, y) in path:
            self.tau[x, y] += amount


# -------------------------------------------------
# Ant agent
# -------------------------------------------------
class Ant:
    def __init__(self, env: Environment, pher: PheromoneGrid):
        self.env = env
        self.pher = pher
        self.pos = config.NEST_POS
        self.state = "searching"          # or "returning"
        self.path: List[Tuple[int, int]] = [self.pos]   # forward tour
        self.return_stack: List[Tuple[int, int]] = []   # reversed path home
        self.deposit_path: List[Tuple[int, int]] = []   # saved copy for Q/L
        self.skip_deposit = False                       # ← new flag

    def reset(self):
        self.pos = config.NEST_POS
        self.state = "searching"
        self.path = [self.pos]
        self.return_stack = []
        self.deposit_path = []
        self.skip_deposit = False       # clear flag

    # --- private helpers ---------------------------------------------------
    def _heuristic(self, nxt: Tuple[int, int]) -> float:
        # Use distance to the NEAREST food source
        x, y = nxt
        if not self.env.food_positions:          # all food depleted
            return 0.0

        d_min = min(
            math.hypot(fx - x, fy - y) for fx, fy in self.env.food_positions
        )
        return 1.0 / (d_min + 1e-6)

    # --- public ------------------------------------------------------------
    def step(self):
        if self.state == "searching":
            neighbours = self.env.neighbours(self.pos)
            if not neighbours:
                self.reset()
                return

            # ---------- probability table ----------
            probs = [
                (self.pher.tau[n] ** config.ALPHA) *
                (self._heuristic(n) ** config.BETA)
                for n in neighbours
            ]
            total = sum(probs)

            nxt = None  # ensure it is always initialised

            # ---------- choose next -----------------
            if random.random() < config.EPSILON or total == 0:
                # exploration / no info
                nxt = random.choice(neighbours)
            else:
                r, s = random.random() * total, 0.0
                for n, p in zip(neighbours, probs):
                    s += p
                    if r <= s:
                        nxt = n
                        break
            if nxt is None:              # numeric safeguard
                nxt = random.choice(neighbours)

            # ---------- move & record ---------------
            self.pos = nxt
            self.path.append(nxt)

            # ---------- found food ------------------
            if self.env.grid[self.pos] == Cell.FOOD:
                exhausted = self.env.consume_food(self.pos, self.pher)
                if exhausted:
                    # last piece taken → wipe trail & disable deposit
                    for x, y in self.path:
                        self.pher.tau[x, y] = config.TAU0
                    self.skip_deposit = True

                self.state = "returning"
                self.deposit_path = list(self.path)
                self.return_stack = self.path[-2::-1]    # back to nest

        else:  # --------------------- returning --------------------------
            if self.return_stack:               # FIFO pop – follows original order
                nxt = self.return_stack.pop(0)
            else:
                nxt = config.NEST_POS

            self.pos = nxt
            if self.env.grid[self.pos] == Cell.NEST:
                dest = self.deposit_path[-1]          # food this tour reached
                # store the tour for statistics (always)
                self.env.record_path(dest, self.deposit_path)

                if not self.skip_deposit:             # optionally lay pheromone
                    L = max(1, len(self.deposit_path))
                    self.pher.deposit(self.deposit_path, config.Q / L)

                self.reset()


# -------------------------------------------------
# Simulation wrapper
# -------------------------------------------------
class Simulation:
    def __init__(self):
        # 1)  If the user provided a seed → use it.
        # 2)  Otherwise generate one so we can still report it later.
        if config.RANDOM_SEED is None:
            self.seed = random.randint(0, 2**32 - 1)
        else:
            self.seed = config.RANDOM_SEED
        random.seed(self.seed)

        # Build the world AFTER seeding RNG so that food/walls are reproducible
        self.env = Environment(config.GRID_W, config.GRID_H)

        self.pher = PheromoneGrid(config.GRID_W, config.GRID_H, config.TAU0)
        self.ants = [Ant(self.env, self.pher)
                     for _ in range(config.N_ANTS)]

        # --------------------  metrics  -----------------------------
        self.tick_count: int | float = 0
        self.first_food_tick: int | None = None
        self.all_food_tick:   int | None = None
        self.food_collected:  int = 0       # running total

        # food_pos -> BEST (shortest) forward tour
        self.best_paths: Dict[Tuple[int, int],
                              List[Tuple[int, int]]] | None = None

    # ------------------------------------------------------------------
    def tick(self) -> None:
        self.tick_count += 1
        before = self.env.remaining_food()

        for ant in self.ants:
            ant.step()

        self.pher.evaporate(config.RHO)

        # --------------------  metrics update  ----------------------
        after = self.env.remaining_food()
        delta = before - after        # food units taken this tick

        if delta > 0:
            self.food_collected += delta
            if self.first_food_tick is None:
                self.first_food_tick = self.tick_count

        if after == 0 and self.all_food_tick is None:
            self.all_food_tick = self.tick_count

        # final statistics – build once
        if (self.best_paths is None and
                self.env.remaining_food() == 0 and
                self.env.paths_by_food):
            self.best_paths = {
                food: self._best_path(paths)
                for food, paths in self.env.paths_by_food.items()
                if paths
            }

    # ------------------------------------------------------------------
    @staticmethod
    def _best_path(paths: List[List[Tuple[int, int]]]
                   ) -> List[Tuple[int, int]]:
        """Return the shortest recorded forward tour."""
        return min(paths, key=len)

    # --------------------  convenience accessors  ------------------
    def seconds(self, ticks: int | None) -> str:
        if ticks is None:
            return "—"
        return f"{ticks / config.FPS:.2f}s"

    @property
    def throughput(self) -> float:
        """Food per second since the first pickup."""
        if self.first_food_tick is None:
            return 0.0
        end = (self.all_food_tick or self.tick_count)
        secs = (end - self.first_food_tick) / config.FPS
        return 0.0 if secs == 0 else self.food_collected / secs
