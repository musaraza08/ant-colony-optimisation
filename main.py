import sys
import pygame as pg

import config
from simulation import Simulation
from visual.renderer import draw

pg.font.init()
FONT = pg.font.SysFont(None, 22)

# Main loop


def main() -> None:
    pg.init()
    screen = pg.display.set_mode((config.WINDOW_W, config.WINDOW_H))
    pg.display.set_caption("Ant Colony Optimisation – demo")
    clock = pg.time.Clock()

    sim = Simulation()

    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

        sim.tick()
        draw(sim, screen, FONT)

        pg.display.flip()
        clock.tick(config.FPS)


if __name__ == "__main__":
    main()
