import unittest
from bitmap.core import BitmapProcessor
import os

class TestBitmapProcessor(unittest.TestCase):
    def test_process_to_1bit(self):
        # Replace with a valid raw file path for testing
        raw_file = "test_image.nef"
        output_file = "test_output.bmp"
        
        if os.path.exists(raw_file):
            processor = BitmapProcessor(raw_file)
            result = processor.process_to_1bit(output_file)
            self.assertTrue(os.path.exists(result))
            os.remove(result)  # Clean up
        else:
            self.skipTest("Test raw file not found")

if __name__ == '__main__':
    unittest.main()
