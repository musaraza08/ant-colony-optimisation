from __future__ import annotations
import pygame as pg
import numpy as np

import config
from core.environment import Cell
from simulation import Simulation

# ------------------------------------------------------------------ #
#                   Colours & tiny utility helpers                   #
# ------------------------------------------------------------------ #
C_BG = (30, 30, 30)
C_GRID = (50, 50, 50)
C_NEST = (0, 220, 0)
C_FOOD = (220, 0, 0)
C_WALL = (100, 100, 100)
C_ANT = (250, 250, 250)
C_AVG = (255, 255, 0)
C_DEP = (140, 140, 140)


def _pheromone_surface(pher_tau, tile):
    w, h = pher_tau.shape
    tau_norm = np.clip(pher_tau / 1.0, 0.0, 1.0).T
    heat = np.zeros((h, w, 3), dtype=np.uint8)
    heat[..., 1] = (180 * tau_norm).astype(np.uint8)
    heat[..., 2] = (255 * tau_norm).astype(np.uint8)
    surf = pg.surfarray.make_surface(np.transpose(heat, (1, 0, 2)))
    return pg.transform.scale(surf, (w * tile, h * tile))


# ------------------------------------------------------------------ #
#                               DRAW                                 #
# ------------------------------------------------------------------ #
def draw(sim: Simulation,
         screen: pg.Surface,
         font: pg.font.Font) -> None:
    tile = config.TILE_SIZE
    w, h = config.GRID_W, config.GRID_H
    screen.fill(C_BG)

    # pheromone heat-map
    screen.blit(_pheromone_surface(sim.pher.tau, tile), (0, 0))

    # cells
    for x in range(w):
        for y in range(h):
            cell = sim.env.grid[x, y]
            if cell == Cell.EMPTY:
                continue
            if cell == Cell.NEST:
                color = C_NEST
            elif cell == Cell.FOOD:
                color = C_FOOD
            elif cell == Cell.DEPLETED:
                color = C_DEP
            else:
                color = C_WALL
            pg.draw.rect(screen, color, (x*tile, y*tile, tile, tile))

    # ants
    for ant in sim.ants:
        ax, ay = ant.pos
        pg.draw.circle(screen, C_ANT,
                       (ax*tile + tile//2, ay*tile + tile//2),
                       tile//2)

    # grid lines
    for x in range(0, w * tile, tile):
        pg.draw.line(screen, C_GRID, (x, 0), (x, h * tile))
    for y in range(0, h * tile, tile):
        pg.draw.line(screen, C_GRID, (0, y), (w * tile, y))

    # best (shortest) paths
    if sim.best_paths:
        for path in sim.best_paths.values():
            if len(path) >= 2:
                pts = [(x*tile + tile//2, y*tile + tile//2) for x, y in path]
                pg.draw.lines(screen, C_AVG, False, pts, 2)

    # overlay
    collected = sim.env.total_food - sim.env.remaining_food()
    txt_surf = font.render(
        f"Food collected: {collected}/{sim.env.total_food}", True, (255,
                                                                    255, 255)
    )
    screen.blit(txt_surf, (10, 5))
