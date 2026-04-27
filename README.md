# Robot Vision with Bitmap Processing

A Python project for robot vision using bitmap image processing operations. This project provides a foundation for implementing computer vision algorithms for robotics applications, including raw camera data processing into 1-bit bitmaps, per-robot internal storage, and French robot status output.

## Features

- **Raw Camera Processing**: Convert raw camera files (NEF, CR2, ARW, etc.) to 1-bit bitmaps
- **Image Processing**: Bitmap loading, thresholding, edge detection, and contour finding
- **Vision Algorithms**: Object detection, path planning, and centroid calculation
- **Robot Interface**: Vision-based control system with obstacle detection and steering
- **Per-Robot Internal Storage**: Runtime frames, metadata, and state are saved under `storage/<robot_id>/`
- **French Robot Voice**: Built-in French status messages for robot output
- **Modular Design**: Clean separation of concerns for easy extension and customization

## Project Structure

```
bitmap/
├── src/
│   ├── __init__.py
│   ├── image_processing.py    # Core image processing functions
│   ├── vision_algorithms.py   # Computer vision algorithms
│   └── robot_interface.py     # Robot control interface
├── tests/
│   ├── __init__.py
│   ├── test_image_processing.py
│   └── test_vision_algorithms.py
├── main.py                     # Main entry point
├── requirements.txt
└── README.md
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/joshuafitzgerald/bitmap
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the main demo:
```bash
python main.py
```

### Run tests:
```bash
python -m unittest discover tests
```

### Example Code:

#### Process Raw Camera Data to 1-bit Bitmap:
```python
from src.core import BitmapProcessor

# Initialize with a raw camera file
processor = BitmapProcessor('image.nef')

# Process to 1-bit bitmap and save
processor.process_to_1bit('output.bmp')

# Or get as numpy array
bitmap_array = processor.process_to_array()
```

#### Robot Vision Processing:
```python
from src.image_processing import apply_threshold
from src.robot_interface import RobotVisionController
from src.storage import RuntimeStorage

storage = RuntimeStorage(robot_id="robot_fr_001")
detector = ObjectDetector(min_area=100)
controller = RobotVisionController(safety_distance=0.5, storage=storage, robot_id="robot_fr_001")

# Process an image
binary_image = apply_threshold(image, threshold=128)
centroid = calculate_centroid(binary_image)
command = controller.process_frame(image)
message = controller.speak("startup")
```

### Requirements
- Python 3.8+
- rawpy for raw camera file processing
- pillow for image operations
- numpy for array processing
- pytest for testing (development)

## Development

### Internal Storage Layout

Each robot gets its own internal data folder:

```text
storage/
  robot_fr_001/
    arrays/
    metadata/
    state/
    events.jsonl
```

This allows each robot instance to retain its own runtime memory without mixing data across robots.

## Building for Distribution

### Build the Package:
```bash
pip install --upgrade pip setuptools wheel build
python -m build
```

This creates `dist/` directory with:
- `bitmap-robot-vision-0.1.0.tar.gz` (source distribution)
- `bitmap-robot-vision-0.1.0-py3-none-any.whl` (wheel distribution)

### Install Locally:
```bash
pip install dist/bitmap-robot-vision-0.1.0-py3-none-any.whl
```

### Publish to PyPI:
```bash
pip install twine
twine upload dist/*
```

## Next Steps

1. Add raw camera files for testing (NEF, CR2, ARW formats)
2. Integrate camera interface with your robot
3. Customize vision algorithms for your specific use case
4. Integrate with your robot's control system
5. Test with real robot hardware
- Use type hints in function signatures
- Document all functions with docstrings
- Keep functions focused and single-purpose

### Testing
Unit tests are located in the `tests/` directory. Run all tests with:
```bash
python -m unittest discover tests
```

## Next Steps

1. Implement bitmap loading in `src/image_processing.py`
2. Add your robot's camera interface
3. Customize vision algorithms for your specific use case
4. Integrate with your robot's control system
5. Test with real robot hardware

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to extend and customize this project for your specific robotics application.
