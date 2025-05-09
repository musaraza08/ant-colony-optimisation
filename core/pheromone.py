from typing import List, Tuple

import numpy as np


class PheromoneGrid:

    def __init__(self, w: int, h: int, tau0: float):
        self.tau = np.full((w, h), tau0, dtype=np.float32)

    def evaporate(self, rho: float) -> None:
        self.tau *= (1.0 - rho)

    def deposit(self,
                path: List[Tuple[int, int]],
                amount: float) -> None:
        for (x, y) in path:
            self.tau[x, y] += amount
