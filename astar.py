import heapq
import numpy as np
import time
from typing import List, Tuple, Dict, Set, Optional


class AStar:

    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.obstacles = set()  # Set of (x, y) tuples representing obstacle positions

    def set_obstacles(self, obstacles: List[Tuple[int, int]]):
        self.obstacles = set(obstacles)

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return (0 <= x < self.grid_width and
                0 <= y < self.grid_height and
                pos not in self.obstacles)

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        # Consider 8 neighbors (including diagonals)
        neighbors = [
            (x+1, y), (x-1, y), (x, y+1), (x, y-1),
            (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
        ]
        return [n for n in neighbors if self.is_valid_position(n)]

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        # Euclidean distance
        return np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        came_from = {}

        heapq.heappush(open_set, (f_score[start], start))

        while open_set:
            # Get node with lowest f_score
            _, current = heapq.heappop(open_set)

            # If we've reached the goal, reconstruct and return the path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            # Add current node to closed set
            closed_set.add(current)

            # Check all neighbors
            for neighbor in self.get_neighbors(current):
                # Skip if neighbor is in closed set
                if neighbor in closed_set:
                    continue

                # Calculate tentative g_score
                tentative_g_score = g_score[current] + \
                    self.heuristic(current, neighbor)

                # If neighbor not in open set or has better g_score
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Update path and scores
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + \
                        self.heuristic(neighbor, goal)

                    # Add to open set if not already there
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # No path found
        return None
