# Example: Using BitmapProcessor with Robot Vision

from src.core import BitmapProcessor
from src.image_processing import apply_threshold
from src.vision_algorithms import calculate_centroid
from src.robot_interface import RobotVisionController

# Example 1: Process raw camera file to 1-bit bitmap
print("Example 1: Raw Camera Processing")
print("-" * 50)

# Replace 'image.nef' with your actual raw file
raw_file = 'image.nef'  # Can be .nef, .cr2, .arw, .dng, etc.

try:
    processor = BitmapProcessor(raw_file)
    
    # Save as 1-bit BMP file
    output_file = processor.process_to_1bit('output.bmp')
    print(f"✓ Saved 1-bit bitmap to: {output_file}")
    
    # Or get as numpy array for further processing
    bitmap_array = processor.process_to_array()
    print(f"✓ Loaded bitmap array: {bitmap_array.shape}")
    
    # Use with robot vision algorithms
    centroid = calculate_centroid(bitmap_array)
    print(f"✓ Calculated centroid: ({centroid[0]:.2f}, {centroid[1]:.2f})")
    
except (FileNotFoundError, ValueError) as e:
    print(f"⚠ Cannot process file: {e}")
    print("  Please provide a valid raw camera file (NEF, CR2, ARW, DNG, RAF)")
    print("  Continuing with other examples...")

# Example 2: Integrate with robot controller
print("\nExample 2: Robot Vision Integration")
print("-" * 50)

controller = RobotVisionController(safety_distance=0.5)

# Process bitmap and generate robot command
# bitmap_array would come from your camera
import numpy as np
sample_bitmap = np.random.randint(0, 2, (480, 640), dtype=np.uint8) * 255

command = controller.process_frame(sample_bitmap)
print(f"Robot command: {command.direction} at speed {command.speed}")

print("\n✓ Integration examples complete!")
print("\nTo use with your robot:")
print("1. Capture image from robot camera as raw file")
print("2. Process with BitmapProcessor to get 1-bit bitmap")
print("3. Feed bitmap to vision algorithms")
print("4. Generate robot control commands")
