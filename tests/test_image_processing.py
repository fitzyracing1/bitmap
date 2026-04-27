"""Tests for image processing module."""

import unittest
import numpy as np
from src.image_processing import apply_threshold, find_contours


class TestImageProcessing(unittest.TestCase):
    """Test cases for image processing functions."""
    
    def test_apply_threshold(self):
        """Test binary threshold application."""
        # Create test image
        image = np.array([[100, 150], [200, 50]], dtype=np.uint8)
        
        # Apply threshold
        result = apply_threshold(image, threshold=128)
        
        # Verify results
        expected = np.array([[0, 255], [255, 0]], dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)
    
    def test_threshold_boundaries(self):
        """Test threshold with boundary values."""
        image = np.array([[0, 128, 255]], dtype=np.uint8)
        
        result = apply_threshold(image, threshold=128)
        
        # 128 > 128 is False, so should be 0
        expected = np.array([[0, 0, 255]], dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)
    
    def test_invalid_threshold(self):
        """Test that invalid threshold raises ValueError."""
        image = np.zeros((10, 10), dtype=np.uint8)
        
        with self.assertRaises(ValueError):
            apply_threshold(image, threshold=300)
        
        with self.assertRaises(ValueError):
            apply_threshold(image, threshold=-10)


if __name__ == '__main__':
    unittest.main()
