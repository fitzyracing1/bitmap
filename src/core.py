"""Core bitmap processing functionality for raw camera data.

This module provides the BitmapProcessor class for converting raw camera
data into 1-bit bitmap images suitable for robot vision applications.
"""

import numpy as np
from PIL import Image
from typing import Optional

from src.storage import RuntimeStorage


class BitmapProcessor:
    """A class to process raw camera data into 1-bit bitmap images."""
    
    def __init__(self, raw_file_path: str, storage: Optional[RuntimeStorage] = None):
        """Initialize with the path to a raw camera file.
        
        Args:
            raw_file_path: Path to the raw camera file (e.g., .nef, .cr2, .arw)
        """
        self.raw_file_path = raw_file_path
        self.storage = storage
    
    def process_to_1bit(self, output_file: str,
                       dither: Image.Dither = Image.Dither.FLOYDSTEINBERG) -> str:
        """Process raw camera data to a 1-bit bitmap and save as BMP.
        
        Args:
            output_file: Path to save the output BMP file
            dither: Dithering method for 1-bit conversion (default: Floyd-Steinberg)
                   Options: Image.Dither.NONE, Image.Dither.FLOYDSTEINBERG
        
        Returns:
            Path to the saved output file
            
        Raises:
            FileNotFoundError: If raw file doesn't exist
            ValueError: If file format is not supported
        """
        try:
            import rawpy

            # Read and process raw camera data
            with rawpy.imread(self.raw_file_path) as raw:
                rgb = raw.postprocess(output_bps=16, use_camera_wb=True)
            
            # Convert to grayscale
            grayscale = np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint16)
            
            # Normalize to 8-bit
            grayscale = (grayscale / grayscale.max() * 255).astype(np.uint8)
            
            # Convert to 1-bit bitmap
            image = Image.fromarray(grayscale, mode='L')
            image_1bit = image.convert('1', dither=dither)
            
            # Save as BMP
            image_1bit.save(output_file, format='BMP')

            if self.storage is not None:
                self.storage.append_event(
                    "bitmap_saved",
                    {
                        "raw_file_path": self.raw_file_path,
                        "output_file": output_file,
                        "dither": str(dither),
                        "size": list(image_1bit.size),
                    },
                )

            return output_file
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Raw file not found: {self.raw_file_path}")
        except Exception as e:
            raise ValueError(f"Failed to process raw file: {e}")
    
    def process_to_array(self, dither: Image.Dither = Image.Dither.FLOYDSTEINBERG) -> np.ndarray:
        """Process raw camera data to a 1-bit numpy array.
        
        Args:
            dither: Dithering method for 1-bit conversion
        
        Returns:
            Binary numpy array (0 or 1 values)
        """
        try:
            import rawpy

            # Read and process raw camera data
            with rawpy.imread(self.raw_file_path) as raw:
                rgb = raw.postprocess(output_bps=16, use_camera_wb=True)
            
            # Convert to grayscale
            grayscale = np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint16)
            
            # Normalize to 8-bit
            grayscale = (grayscale / grayscale.max() * 255).astype(np.uint8)
            
            # Convert to 1-bit bitmap
            image = Image.fromarray(grayscale, mode='L')
            image_1bit = image.convert('1', dither=dither)
            
            # Convert to numpy array
            bitmap_array = np.array(image_1bit, dtype=np.uint8)

            if self.storage is not None:
                self.storage.save_array(
                    bitmap_array,
                    prefix="bitmap_frame",
                    metadata={
                        "raw_file_path": self.raw_file_path,
                        "dither": str(dither),
                    },
                )

            return bitmap_array
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Raw file not found: {self.raw_file_path}")
        except Exception as e:
            raise ValueError(f"Failed to process raw file: {e}")
