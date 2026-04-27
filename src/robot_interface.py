"""Interface for robot control based on vision processing."""

from typing import Tuple, Optional
import numpy as np
from dataclasses import asdict, dataclass

from src.storage import RuntimeStorage


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
        # Analyze image and generate appropriate command
        # This is a placeholder - implement your logic here
        command = RobotCommand(
            direction='arrete',
            speed=0.0,
            duration=0.0
        )
        
        self.last_command = command

        if self.storage is not None:
            frame_record = self.storage.save_array(
                image,
                prefix="vision_frame",
                metadata={
                    "safety_distance": self.safety_distance,
                    "mean_pixel_value": float(np.mean(image)),
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
        # Implement obstacle detection logic
        return False
    
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
