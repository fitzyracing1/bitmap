"""Tests for image processing module."""

import tempfile
import unittest

import numpy as np
from PIL import Image

from src.image_processing import apply_threshold, detect_edges, find_contours, load_bitmap


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

    def test_load_bitmap_returns_grayscale_array(self):
        """Bitmap loading should return an 8-bit grayscale array."""
        image = Image.fromarray(np.array([[0, 128], [200, 255]], dtype=np.uint8), mode="L")

        with tempfile.NamedTemporaryFile(suffix=".bmp") as temp_file:
            image.save(temp_file.name)

            result = load_bitmap(temp_file.name)

        expected = np.array([[0, 128], [200, 255]], dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)

    def test_load_bitmap_missing_file(self):
        """Missing bitmap files should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_bitmap("missing_bitmap.bmp")

    def test_detect_edges_highlights_boundaries(self):
        """Sobel edge detection should identify intensity transitions."""
        image = np.zeros((5, 5), dtype=np.uint8)
        image[:, 3:] = 255

        edges = detect_edges(image)

        self.assertEqual(edges.dtype, np.uint8)
        self.assertGreater(edges[:, 2].max(), 0)
        self.assertGreater(edges[:, 3].max(), 0)
        self.assertEqual(edges[:, 0].max(), 0)

    def test_find_contours_returns_component_boundaries(self):
        """Contour detection should return one boundary per component."""
        image = np.zeros((6, 6), dtype=np.uint8)
        image[1:3, 1:3] = 255
        image[4, 4] = 255

        contours = find_contours(image)

        self.assertEqual(len(contours), 2)
        self.assertEqual(contours[0], [(1, 1), (2, 1), (1, 2), (2, 2)])
        self.assertEqual(contours[1], [(4, 4)])


if __name__ == '__main__':
    unittest.main()
