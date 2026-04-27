"""Robot Vision with Bitmap Processing.

This package provides computer vision and image processing capabilities
for robotics applications using bitmap operations.
"""

from .core import BitmapProcessor
from .storage import RuntimeStorage

__version__ = "0.1.1"

__all__ = ["BitmapProcessor", "RuntimeStorage"]
