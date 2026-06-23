"""Vision algorithms for robot perception and navigation."""

from heapq import heappop, heappush
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.image_processing import _to_binary_mask


class ObjectDetector:
    """Detect objects in images for robot vision."""
    
    def __init__(self, min_area: int = 100):
        """Initialize object detector.
        
        Args:
            min_area: Minimum area for valid objects
        """
        if min_area < 1:
            raise ValueError("min_area must be at least 1")
        self.min_area = min_area
    
    def detect(self, image: np.ndarray) -> List[dict]:
        """Detect objects in the image.
        
        Args:
            image: Input image array
            
        Returns:
            List of detected objects with bounding boxes and properties
        """
        mask = _to_binary_mask(image)
        visited = np.zeros(mask.shape, dtype=bool)
        objects = []

        for y_start, x_start in np.argwhere(mask):
            if visited[y_start, x_start]:
                continue

            pixels = self._collect_component(mask, visited, int(x_start), int(y_start))
            area = len(pixels)
            if area < self.min_area:
                continue

            xs = np.array([pixel[0] for pixel in pixels], dtype=np.int32)
            ys = np.array([pixel[1] for pixel in pixels], dtype=np.int32)
            x_min = int(xs.min())
            y_min = int(ys.min())
            x_max = int(xs.max())
            y_max = int(ys.max())

            objects.append(
                {
                    "area": int(area),
                    "bbox": (x_min, y_min, x_max - x_min + 1, y_max - y_min + 1),
                    "centroid": (float(xs.mean()), float(ys.mean())),
                    "contour": self._component_boundary(mask, pixels),
                }
            )

        objects.sort(key=lambda item: (-item["area"], item["bbox"][1], item["bbox"][0]))
        return objects

    def _collect_component(
        self,
        mask: np.ndarray,
        visited: np.ndarray,
        x_start: int,
        y_start: int,
    ) -> List[Tuple[int, int]]:
        stack = [(x_start, y_start)]
        visited[y_start, x_start] = True
        pixels: List[Tuple[int, int]] = []

        while stack:
            x, y = stack.pop()
            pixels.append((x, y))
            for nx, ny in self._neighbors(x, y, mask.shape[1], mask.shape[0]):
                if mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((nx, ny))

        return pixels

    def _component_boundary(
        self,
        mask: np.ndarray,
        pixels: List[Tuple[int, int]],
    ) -> List[Tuple[int, int]]:
        boundary = []
        height, width = mask.shape
        for x, y in pixels:
            for nx, ny in self._neighbors_with_edges(x, y, width, height):
                if nx is None or ny is None or not mask[ny, nx]:
                    boundary.append((x, y))
                    break
        return sorted(boundary, key=lambda point: (point[1], point[0]))

    def _neighbors(self, x: int, y: int, width: int, height: int) -> List[Tuple[int, int]]:
        neighbors = []
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append((nx, ny))
        return neighbors

    def _neighbors_with_edges(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> List[Tuple[Optional[int], Optional[int]]]:
        neighbors: List[Tuple[Optional[int], Optional[int]]] = []
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append((nx, ny))
            else:
                neighbors.append((None, None))
        return neighbors


class PathPlanner:
    """Plan navigation paths based on visual input."""
    
    def __init__(self, grid_size: Tuple[int, int] = (640, 480)):
        """Initialize path planner.
        
        Args:
            grid_size: Size of the navigation grid (width, height)
        """
        if grid_size[0] < 1 or grid_size[1] < 1:
            raise ValueError("grid_size dimensions must be positive")
        self.grid_size = grid_size
        self.obstacle_map = np.zeros(grid_size, dtype=bool)
    
    def update_obstacles(self, image: np.ndarray) -> None:
        """Update obstacle map from image data.
        
        Args:
            image: Binary image where obstacles are marked
        """
        mask = _to_binary_mask(image)
        width, height = self.grid_size

        if mask.shape == (width, height):
            self.obstacle_map = mask.copy()
        elif mask.shape == (height, width):
            self.obstacle_map = mask.T.copy()
        else:
            self.obstacle_map = self._resize_mask(mask, width, height)
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find a path from start to goal avoiding obstacles.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            List of waypoints forming the path, or None if no path exists
        """
        if not self._is_open(start) or not self._is_open(goal):
            return None
        if start == goal:
            return [start]

        open_set = []
        heappush(open_set, (self._heuristic(start, goal), 0, start))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        best_cost = {start: 0}

        while open_set:
            _, cost, current = heappop(open_set)
            if current == goal:
                return self._reconstruct_path(came_from, current)
            if cost > best_cost[current]:
                continue

            for neighbor in self._grid_neighbors(current):
                new_cost = cost + 1
                if new_cost >= best_cost.get(neighbor, float("inf")):
                    continue

                came_from[neighbor] = current
                best_cost[neighbor] = new_cost
                priority = new_cost + self._heuristic(neighbor, goal)
                heappush(open_set, (priority, new_cost, neighbor))

        return None

    def _resize_mask(self, mask: np.ndarray, width: int, height: int) -> np.ndarray:
        y_indices = np.linspace(0, mask.shape[0] - 1, height).astype(np.int32)
        x_indices = np.linspace(0, mask.shape[1] - 1, width).astype(np.int32)
        return mask[np.ix_(y_indices, x_indices)].T.copy()

    def _is_open(self, point: Tuple[int, int]) -> bool:
        x, y = point
        width, height = self.grid_size
        return 0 <= x < width and 0 <= y < height and not self.obstacle_map[x, y]

    def _grid_neighbors(self, point: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = point
        candidates = ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1))
        return [candidate for candidate in candidates if self._is_open(candidate)]

    def _heuristic(self, point: Tuple[int, int], goal: Tuple[int, int]) -> int:
        return abs(point[0] - goal[0]) + abs(point[1] - goal[1])

    def _reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int], Tuple[int, int]],
        current: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


def calculate_centroid(binary_image: np.ndarray) -> Tuple[float, float]:
    """Calculate the centroid of objects in a binary image.
    
    Args:
        binary_image: Binary input image
        
    Returns:
        Centroid coordinates (x, y)
    """
    y_coords, x_coords = np.nonzero(_to_binary_mask(binary_image))
    if len(x_coords) == 0:
        return (0.0, 0.0)
    
    centroid_x = float(np.mean(x_coords))
    centroid_y = float(np.mean(y_coords))
    
    return (centroid_x, centroid_y)
