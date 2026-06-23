"""Interface for robot control based on vision processing."""

from typing import Tuple, Optional
import numpy as np
from dataclasses import asdict, dataclass

from src.image_processing import _to_grayscale
from src.storage import RuntimeStorage
from src.vision_algorithms import calculate_centroid


@dataclass
class RobotCommand:
    """Command structure for robot control."""
    direction: str  # 'avance', 'recule', 'gauche', 'droite', 'arrete'
    speed: float  # Speed value 0.0 to 1.0
    duration: float  # Duration in seconds


class RobotVisionController:
    """Controller that processes vision data and generates robot commands."""

    FRENCH_STATUS_MESSAGES = {
        "startup": "Systeme de vision du robot pret.",
        "processing": "J'analyse l'image en cours.",
        "idle": "Je suis en attente d'une nouvelle image.",
        "obstacle_detected": "Obstacle detecte, je m'arrete.",
        "path_clear": "La voie est libre, j'avance.",
    }
    
    def __init__(
        self,
        safety_distance: float = 0.5,
        storage: Optional[RuntimeStorage] = None,
        robot_id: str = "robot_default",
    ):
        """Initialize robot vision controller.
        
        Args:
            safety_distance: Minimum safe distance from obstacles (meters)
        """
        self.safety_distance = safety_distance
        self.storage = storage or RuntimeStorage(robot_id=robot_id)
        self.robot_id = self.storage.robot_id
        self.last_command: Optional[RobotCommand] = None

        saved_command = self.storage.load_state("last_command")
        if isinstance(saved_command, dict):
            self.last_command = RobotCommand(**saved_command)
    
    def process_frame(self, image: np.ndarray) -> RobotCommand:
        """Process a vision frame and generate robot command.
        
        Args:
            image: Input image from robot camera
            
        Returns:
            Robot command based on vision analysis
        """
        obstacle_detected = self.detect_obstacles(image)
        if obstacle_detected:
            command = RobotCommand(direction="arrete", speed=0.0, duration=0.5)
        else:
            command = self._command_for_clear_path(image)
        
        self.last_command = command

        if self.storage is not None:
            frame_record = self.storage.save_array(
                image,
                prefix="vision_frame",
                metadata={
                    "safety_distance": self.safety_distance,
                    "mean_pixel_value": float(np.mean(image)),
                    "obstacle_detected": obstacle_detected,
                },
            )
            self.storage.save_state("last_command", asdict(command))
            self.storage.append_event(
                "robot_command_generated",
                {
                    "command": command,
                    "frame_id": frame_record["id"],
                },
            )

        return command

    def speak(self, status: str = "idle") -> str:
        """Return a French status line for the robot."""
        return self.FRENCH_STATUS_MESSAGES.get(status, "Je communique en francais.")

    def storage_summary(self) -> str:
        """Return a French summary of the robot's internal database."""
        return f"Base de donnees interne active pour {self.robot_id} dans {self.storage.robot_path()}."
    
    def detect_obstacles(self, image: np.ndarray) -> bool:
        """Detect if there are obstacles in the path.
        
        Args:
            image: Input image
            
        Returns:
            True if obstacles detected, False otherwise
        """
        mask = self._foreground_mask(image)
        if not np.any(mask):
            return False

        height, width = mask.shape
        y_start = height // 2
        corridor_half_width = max(1, int(width * min(max(self.safety_distance, 0.1), 1.0) / 4))
        center_x = width // 2
        x_start = max(0, center_x - corridor_half_width)
        x_end = min(width, center_x + corridor_half_width + 1)
        corridor = mask[y_start:, x_start:x_end]

        return bool(corridor.size > 0 and np.mean(corridor) >= 0.1)
    
    def calculate_steering(self, target_position: Tuple[int, int], 
                          current_position: Tuple[int, int]) -> float:
        """Calculate steering angle to reach target.
        
        Args:
            target_position: Target (x, y) coordinates
            current_position: Current (x, y) coordinates
            
        Returns:
            Steering angle in radians
        """
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        
        angle = np.arctan2(dy, dx)
        return float(angle)

    def _command_for_clear_path(self, image: np.ndarray) -> RobotCommand:
        mask = self._foreground_mask(image)
        if not np.any(mask):
            return RobotCommand(direction="avance", speed=0.6, duration=0.5)

        centroid_x, _ = calculate_centroid(mask)
        width = mask.shape[1]
        center_x = (width - 1) / 2.0
        if center_x == 0:
            return RobotCommand(direction="avance", speed=0.4, duration=0.5)

        offset = (centroid_x - center_x) / center_x
        if offset < -0.2:
            return RobotCommand(direction="gauche", speed=0.35, duration=0.4)
        if offset > 0.2:
            return RobotCommand(direction="droite", speed=0.35, duration=0.4)
        return RobotCommand(direction="avance", speed=0.6, duration=0.5)

    def _foreground_mask(self, image: np.ndarray) -> np.ndarray:
        grayscale = _to_grayscale(image).astype(np.float32)
        if grayscale.size == 0:
            return np.zeros_like(grayscale, dtype=bool)

        max_value = float(np.max(grayscale))
        if max_value <= 0.0:
            return np.zeros(grayscale.shape, dtype=bool)
        if max_value <= 1.0:
            return grayscale > 0.0

        threshold = 127.0 if max_value > 127.0 else float(np.mean(grayscale))
        return grayscale > threshold
