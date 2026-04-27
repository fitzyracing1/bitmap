import numpy as np
from PIL import Image

class BitmapProcessor:
    """A class to process raw camera data into 1-bit bitmap images."""
    
    def __init__(self, raw_file_path, storage=None):
        """Initialize with the path to a raw camera file."""
        self.raw_file_path = raw_file_path
        self.storage = storage
    
    def process_to_1bit(self, output_file, dither=Image.Dither.FLOYDSTEINBERG):
        """Process raw camera data to a 1-bit bitmap and save as BMP.
        
        Args:
            output_file (str): Path to save the output BMP file.
            dither (Image.Dither): Dithering method for 1-bit conversion.
        """
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
