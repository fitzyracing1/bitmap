# Bitmap Robot Vision - Quick Reference

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individual packages
pip install rawpy pillow numpy
```

## Core Classes

### BitmapProcessor
```python
from src.core import BitmapProcessor

# Initialize with raw camera file
processor = BitmapProcessor('image.nef')

# Convert to 1-bit BMP file
processor.process_to_1bit('output.bmp')

# Get as numpy array
bitmap_array = processor.process_to_array()
```

### ObjectDetector
```python
from src.vision_algorithms import ObjectDetector

detector = ObjectDetector(min_area=100)
objects = detector.detect(image)
```

### PathPlanner
```python
from src.vision_algorithms import PathPlanner

planner = PathPlanner(grid_size=(640, 480))
planner.update_obstacles(binary_image)
path = planner.find_path(start=(0, 0), goal=(100, 100))
```

### RobotVisionController
```python
from src.robot_interface import RobotVisionController

controller = RobotVisionController(safety_distance=0.5)
command = controller.process_frame(image)
print(f"{command.direction} at {command.speed}")
```

## Image Processing Functions

```python
from src.image_processing import apply_threshold, detect_edges
from src.vision_algorithms import calculate_centroid

# Threshold image
binary = apply_threshold(image, threshold=128)

# Detect edges
edges = detect_edges(image)

# Calculate centroid
cx, cy = calculate_centroid(binary_image)
```

## Running Tests

```bash
# All tests
python -m unittest discover tests

# Specific module
python -m unittest tests.test_bitmap_core -v

# Run main demo
python main.py

# Run examples
python example.py
```

## Building Package

```bash
# Install build tools
pip install build wheel twine

# Build distributions
python -m build

# Test locally
pip install dist/bitmap-robot-vision-0.1.0-py3-none-any.whl

# Upload to PyPI
twine upload dist/*
```

## Supported Raw Formats

- Nikon: .nef
- Canon: .cr2, .cr3
- Sony: .arw
- Fujifilm: .raf
- Adobe: .dng
- Pentax: .pef
- Olympus: .orf

## Common Workflows

### 1. Process Camera Image for Robot Vision
```python
from src.core import BitmapProcessor
from src.vision_algorithms import calculate_centroid
from src.robot_interface import RobotVisionController

# Load and process
processor = BitmapProcessor('capture.nef')
bitmap = processor.process_to_array()

# Analyze
centroid = calculate_centroid(bitmap)

# Control robot
controller = RobotVisionController()
command = controller.process_frame(bitmap)
```

### 2. Batch Process Images
```python
import os
from src.core import BitmapProcessor

for filename in os.listdir('raw_images/'):
    if filename.endswith('.nef'):
        processor = BitmapProcessor(f'raw_images/{filename}')
        output = f'processed/{filename[:-4]}.bmp'
        processor.process_to_1bit(output)
```

### 3. Real-time Robot Vision Loop
```python
from src.core import BitmapProcessor
from src.robot_interface import RobotVisionController

controller = RobotVisionController(safety_distance=0.5)

while robot_active:
    # Capture from camera
    image = capture_from_robot_camera()
    
    # Process
    processor = BitmapProcessor(image)
    bitmap = processor.process_to_array()
    
    # Generate command
    command = controller.process_frame(bitmap)
    
    # Execute
    robot.execute(command)
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project directory
cd /Users/joshuafitzgerald/bitmap

# Activate virtual environment
source .venv/bin/activate
```

### Raw File Errors
- Verify file exists and is readable
- Check format is supported by rawpy
- Ensure rawpy is installed: `pip install rawpy`

### Memory Issues with Large Images
```python
# Process in smaller batches
# Or use lower resolution raw processing
with rawpy.imread(file) as raw:
    rgb = raw.postprocess(
        output_bps=8,  # Use 8-bit instead of 16
        half_size=True  # Half resolution
    )
```

## Project Structure
```
src/
  __init__.py         # Package exports
  core.py             # Raw camera processing
  image_processing.py # Image utilities
  vision_algorithms.py # CV algorithms
  robot_interface.py  # Robot control

tests/                # Unit tests
main.py               # Demo application
example.py            # Usage examples
```

## Links

- GitHub: https://github.com/fitzyracing1/bitmap
- PyPI: (after publishing) https://pypi.org/project/bitmap-robot-vision/
- rawpy docs: https://letmaik.github.io/rawpy/
