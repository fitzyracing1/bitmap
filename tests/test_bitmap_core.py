"""Tests for bitmap core processing module."""

import unittest
import os
import numpy as np
from src.core import BitmapProcessor


class TestBitmapProcessor(unittest.TestCase):
    """Test cases for BitmapProcessor class."""
    
    def test_initialization(self):
        """Test BitmapProcessor initialization."""
        processor = BitmapProcessor("test_image.nef")
        self.assertEqual(processor.raw_file_path, "test_image.nef")
    
    def test_process_to_1bit_with_sample(self):
        """Test processing to 1-bit BMP with a sample raw file."""
        # This test requires a valid raw file
        raw_file = "test_image.nef"
        output_file = "test_output.bmp"
        
        if os.path.exists(raw_file):
            processor = BitmapProcessor(raw_file)
            result = processor.process_to_1bit(output_file)
            
            self.assertTrue(os.path.exists(result))
            self.assertEqual(result, output_file)
            
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)
        else:
            self.skipTest("Test raw file not found")
    
    def test_process_nonexistent_file(self):
        """Test that processing nonexistent file raises error."""
        processor = BitmapProcessor("nonexistent_file.nef")
        
        with self.assertRaises((FileNotFoundError, ValueError)):
            processor.process_to_1bit("output.bmp")
    
    def test_process_to_array_with_sample(self):
        """Test processing to numpy array."""
        raw_file = "test_image.nef"
        
        if os.path.exists(raw_file):
            processor = BitmapProcessor(raw_file)
            result = processor.process_to_array()
            
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.dtype, np.uint8)
            # 1-bit image should only have 0 and 1 values
            self.assertTrue(np.all(np.isin(result, [0, 1])))
        else:
            self.skipTest("Test raw file not found")


if __name__ == '__main__':
    unittest.main()
