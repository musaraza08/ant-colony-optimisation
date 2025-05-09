# ----------------------------
# Global simulation constants
# ----------------------------

# Grid / window
TILE_SIZE = 12
GRID_W, GRID_H = 50, 50
WINDOW_W, WINDOW_H = GRID_W * TILE_SIZE, GRID_H * TILE_SIZE

# Colony
N_ANTS = 50
NEST_POS = (GRID_W // 2, GRID_H // 2)

# ACO parameters
ALPHA = 1.0  # influence of pheromone
BETA = 3.0  # influence of heuristic
RHO = 0.2  # evaporation rate
Q = 100  # pheromone laid per tour
TAU0 = 0.1  # initial trail

# Exploration probability (ants ignore pheromone with this chance)
EPSILON = 0.3

# Steps before the ant gives up and goes home
SEARCH_TIMEOUT = 100

# Food
NUM_FOOD_SOURCES = 2
FOOD_CAPACITY = 200

# Obstacles
NUM_WALLS = 20
WALL_MIN_LEN = 5
WALL_MAX_LEN = 15

# Runtime
FPS = 120
RANDOM_SEED = 1
