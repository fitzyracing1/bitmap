"""Image processing utilities for robot vision using bitmap operations."""

from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError


def load_bitmap(filepath: str) -> np.ndarray:
    """Load a bitmap image from file.
    
    Args:
        filepath: Path to the bitmap file
        
    Returns:
        numpy array containing the image data
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the file format is not supported
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Bitmap file not found: {filepath}")

    try:
        with Image.open(path) as image:
            if image.mode == "1":
                return np.array(image, dtype=np.uint8) * 255
            return np.array(image.convert("L"), dtype=np.uint8)
    except UnidentifiedImageError as exc:
        raise ValueError(f"Unsupported bitmap format: {filepath}") from exc
    except OSError as exc:
        raise ValueError(f"Failed to load bitmap: {exc}") from exc


def apply_threshold(image: np.ndarray, threshold: int = 128) -> np.ndarray:
    """Apply binary threshold to an image.
    
    Args:
        image: Input image array
        threshold: Threshold value (0-255)
        
    Returns:
        Thresholded binary image
    """
    if threshold < 0 or threshold > 255:
        raise ValueError("Threshold must be between 0 and 255")

    grayscale = _to_grayscale(image)
    return (grayscale > threshold).astype(np.uint8) * 255


def detect_edges(image: np.ndarray) -> np.ndarray:
    """Detect edges in an image for robot navigation.
    
    Args:
        image: Input grayscale image
        
    Returns:
        Edge-detected image
    """
    grayscale = _to_grayscale(image).astype(np.float32)
    if grayscale.size == 0:
        return np.zeros_like(grayscale, dtype=np.uint8)

    padded = np.pad(grayscale, ((1, 1), (1, 1)), mode="edge")

    gx = (
        -padded[:-2, :-2]
        + padded[:-2, 2:]
        - 2 * padded[1:-1, :-2]
        + 2 * padded[1:-1, 2:]
        - padded[2:, :-2]
        + padded[2:, 2:]
    )
    gy = (
        padded[:-2, :-2]
        + 2 * padded[:-2, 1:-1]
        + padded[:-2, 2:]
        - padded[2:, :-2]
        - 2 * padded[2:, 1:-1]
        - padded[2:, 2:]
    )

    magnitude = np.hypot(gx, gy)
    max_value = float(np.max(magnitude))
    if max_value == 0.0:
        return np.zeros_like(grayscale, dtype=np.uint8)

    return np.clip((magnitude / max_value) * 255, 0, 255).astype(np.uint8)


def find_contours(binary_image: np.ndarray) -> List[List[Tuple[int, int]]]:
    """Find contours in a binary image.
    
    Args:
        binary_image: Binary input image
        
    Returns:
        List of contours found in the image
    """
    mask = _to_binary_mask(binary_image)
    visited = np.zeros(mask.shape, dtype=bool)
    contours: List[List[Tuple[int, int]]] = []

    for y_start, x_start in np.argwhere(mask):
        if visited[y_start, x_start]:
            continue

        stack = [(int(y_start), int(x_start))]
        visited[y_start, x_start] = True
        boundary_points = set()

        while stack:
            y, x = stack.pop()
            is_boundary = False

            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if ny < 0 or ny >= mask.shape[0] or nx < 0 or nx >= mask.shape[1]:
                    is_boundary = True
                    continue
                if not mask[ny, nx]:
                    is_boundary = True
                    continue
                if not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))

            if is_boundary:
                boundary_points.add((x, y))

        contours.append(sorted(boundary_points, key=lambda point: (point[1], point[0])))

    return contours


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    """Return a 2D grayscale view of a grayscale or RGB-like image."""
    array = np.asarray(image)
    if array.ndim == 2:
        return array
    if array.ndim == 3:
        if array.shape[2] == 1:
            return array[:, :, 0]
        if array.shape[2] >= 3:
            return np.dot(array[:, :, :3], [0.2989, 0.5870, 0.1140])
    raise ValueError("Image must be a 2D grayscale or 3D RGB-like array")


def _to_binary_mask(image: np.ndarray) -> np.ndarray:
    """Convert an image to a boolean foreground mask."""
    grayscale = _to_grayscale(image)
    return grayscale > 0
