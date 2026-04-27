# Package Build and Distribution Guide

## Project Structure

```
bitmap/
├── .github/
│   └── copilot-instructions.md    # AI coding assistant instructions
├── src/
│   ├── __init__.py                 # Package initialization, exposes BitmapProcessor
│   ├── core.py                     # Raw camera to 1-bit bitmap processing
│   ├── image_processing.py         # Image processing utilities
│   ├── vision_algorithms.py        # Computer vision algorithms
│   └── robot_interface.py          # Robot control interface
├── tests/
│   ├── __init__.py
│   ├── test_bitmap_core.py         # Tests for BitmapProcessor
│   ├── test_image_processing.py
│   └── test_vision_algorithms.py
├── main.py                          # Demo application
├── example.py                       # Usage examples
├── setup.py                         # Package configuration
├── requirements.txt                 # Dependencies
├── MANIFEST.in                      # Distribution manifest
├── LICENSE                          # MIT License
├── README.md                        # Documentation
└── .gitignore                       # Git ignore rules
```

## Building the Package

### 1. Install Build Tools
```bash
pip install --upgrade pip setuptools wheel build twine
```

### 2. Build Distribution
```bash
python -m build
```

This creates:
- `dist/bitmap-robot-vision-0.1.0.tar.gz` (source)
- `dist/bitmap-robot-vision-0.1.0-py3-none-any.whl` (wheel)

### 3. Test Local Installation
```bash
pip install dist/bitmap-robot-vision-0.1.0-py3-none-any.whl
```

### 4. Verify Installation
```python
from src.core import BitmapProcessor
processor = BitmapProcessor('test.nef')
```

## Publishing to PyPI

### First-time Setup
1. Create account at https://pypi.org/
2. Create API token at https://pypi.org/manage/account/token/
3. Configure credentials:
```bash
# Create/edit ~/.pypirc
[pypi]
  username = __token__
  password = pypi-YOUR-TOKEN-HERE
```

### Upload to PyPI
```bash
# Test upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Production upload
twine upload dist/*
```

### Verify Publication
```bash
pip install bitmap-robot-vision
```

## Usage After Installation

```python
# From anywhere in your system
from src.core import BitmapProcessor
from src.vision_algorithms import ObjectDetector

# Process raw camera file
processor = BitmapProcessor('camera_image.nef')
bitmap = processor.process_to_1bit('output.bmp')

# Use with vision algorithms
detector = ObjectDetector(min_area=100)
objects = detector.detect(bitmap)
```

## Development Workflow

### Running Tests
```bash
# All tests
python -m unittest discover tests

# Specific test file
python -m unittest tests.test_bitmap_core

# With verbose output
python -m unittest discover tests -v
```

### Installing in Development Mode
```bash
pip install -e .
```

This allows you to edit code and test changes without reinstalling.

## Version Updates

To release a new version:

1. Update version in:
   - `src/__init__.py` (`__version__`)
   - `setup.py` (`version`)

2. Rebuild and upload:
```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine upload dist/*
```

## Dependencies

### Runtime
- `rawpy>=0.17.0` - Raw camera file processing
- `pillow>=9.0.0` - Image operations
- `numpy>=1.21.0` - Array processing

### Development
- `pytest>=7.0.0` - Testing framework
- `setuptools` - Package building
- `wheel` - Wheel distribution
- `build` - Build frontend
- `twine` - PyPI upload

## Support

For raw camera files, supported formats include:
- Nikon RAW (.nef)
- Canon RAW (.cr2, .cr3)
- Sony RAW (.arw)
- Adobe DNG (.dng)
- Fujifilm RAW (.raf)
- And many others via rawpy/LibRaw
