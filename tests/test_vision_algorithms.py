"""Tests for vision algorithms module."""

import unittest
import numpy as np
from src.vision_algorithms import ObjectDetector, PathPlanner, calculate_centroid


class TestVisionAlgorithms(unittest.TestCase):
    """Test cases for vision algorithms."""
    
    def test_calculate_centroid(self):
        """Test centroid calculation."""
        # Create simple binary image with known centroid
        image = np.zeros((10, 10), dtype=np.uint8)
        image[4:6, 4:6] = 255  # 2x2 square centered at (4.5, 4.5)
        
        centroid = calculate_centroid(image)
        
        # Check centroid is approximately at center of square
        self.assertAlmostEqual(centroid[0], 4.5, places=1)
        self.assertAlmostEqual(centroid[1], 4.5, places=1)
    
    def test_centroid_empty_image(self):
        """Test centroid of empty image."""
        image = np.zeros((10, 10), dtype=np.uint8)
        
        centroid = calculate_centroid(image)
        
        self.assertEqual(centroid, (0.0, 0.0))
    
    def test_object_detector_initialization(self):
        """Test ObjectDetector initialization."""
        detector = ObjectDetector(min_area=50)
        
        self.assertEqual(detector.min_area, 50)

    def test_object_detector_detects_connected_components(self):
        """Object detection should report component geometry."""
        image = np.zeros((6, 6), dtype=np.uint8)
        image[1:3, 1:4] = 255
        image[5, 5] = 255

        detector = ObjectDetector(min_area=2)
        objects = detector.detect(image)

        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]["area"], 6)
        self.assertEqual(objects[0]["bbox"], (1, 1, 3, 2))
        self.assertEqual(objects[0]["centroid"], (2.0, 1.5))
        self.assertEqual(objects[0]["contour"], [(1, 1), (2, 1), (3, 1), (1, 2), (2, 2), (3, 2)])

    def test_object_detector_rejects_invalid_min_area(self):
        """Object detector should require a positive area threshold."""
        with self.assertRaises(ValueError):
            ObjectDetector(min_area=0)
    
    def test_path_planner_initialization(self):
        """Test PathPlanner initialization."""
        planner = PathPlanner(grid_size=(100, 200))
        
        self.assertEqual(planner.grid_size, (100, 200))
        self.assertEqual(planner.obstacle_map.shape, (100, 200))

    def test_path_planner_finds_path_around_obstacles(self):
        """A* path planning should route through available gaps."""
        planner = PathPlanner(grid_size=(5, 5))
        obstacles = np.zeros((5, 5), dtype=np.uint8)
        obstacles[2, :] = 255
        obstacles[2, 2] = 0
        planner.update_obstacles(obstacles)

        path = planner.find_path(start=(0, 0), goal=(4, 4))

        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))
        self.assertIn((2, 2), path)
        self.assertTrue(all(not planner.obstacle_map[x, y] for x, y in path))

    def test_path_planner_returns_none_when_blocked(self):
        """Path planning should fail when no route exists."""
        planner = PathPlanner(grid_size=(5, 5))
        obstacles = np.zeros((5, 5), dtype=np.uint8)
        obstacles[2, :] = 255
        planner.update_obstacles(obstacles)

        path = planner.find_path(start=(0, 0), goal=(4, 4))

        self.assertIsNone(path)

    def test_path_planner_rejects_invalid_grid(self):
        """Path planner should require positive grid dimensions."""
        with self.assertRaises(ValueError):
            PathPlanner(grid_size=(0, 5))


if __name__ == '__main__':
    unittest.main()
