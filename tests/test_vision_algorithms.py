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
    
    def test_path_planner_initialization(self):
        """Test PathPlanner initialization."""
        planner = PathPlanner(grid_size=(100, 200))
        
        self.assertEqual(planner.grid_size, (100, 200))
        self.assertEqual(planner.obstacle_map.shape, (100, 200))


if __name__ == '__main__':
    unittest.main()
