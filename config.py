# ----------------------------
# Global simulation constants
# ----------------------------

# Grid / window
TILE_SIZE = 12                 # pixels
# Slightly smaller arena
GRID_W, GRID_H = 50, 50         # tiles
WINDOW_W, WINDOW_H = GRID_W * TILE_SIZE, GRID_H * TILE_SIZE

# Colony
N_ANTS = 50               # more agents
NEST_POS = (GRID_W // 2, GRID_H // 2)

# How many random food sources should be scattered on the grid?
# If you still want fixed positions, comment this out and restore
# a FOOD_POSITIONS list instead.


# ACO parameters
ALPHA = 1.0              # influence of pheromone 1.0
BETA = 3.0               # influence of heuristic 3.0
RHO = 0.05           # evaporation rate 0.05
Q = 100           # pheromone laid per tour 100
TAU0 = 0.1             # initial trail 0.1

# Exploration probability (ants ignore pheromone with this chance)
EPSILON = 0.3

# -------- NEW ----------
SEARCH_TIMEOUT = 100      # steps before the ant gives up and goes home

# Runtime
FPS = 120
RANDOM_SEED = None

NUM_FOOD_SOURCES = 1
# How many items can be taken from a single food tile
FOOD_CAPACITY = 300

# Obstacles -------------------------------------------------------------
NUM_WALLS = 15   # how many independent wall segments 20
WALL_MIN_LEN = 5     # in tiles
WALL_MAX_LEN = 15
