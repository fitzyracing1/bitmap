"""Tests for the runtime storage layer."""

from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.robot_interface import RobotCommand, RobotVisionController
from src.storage import RuntimeStorage


class TestRuntimeStorage(unittest.TestCase):
    """Test cases for file-backed runtime storage."""

    def test_save_array_creates_files_and_event(self):
        """Saving an array should persist both data and metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = RuntimeStorage(base_dir=temp_dir, robot_id="robot_alpha")
            array = np.array([[0, 255], [255, 0]], dtype=np.uint8)

            record = storage.save_array(array, prefix="test_frame", metadata={"source": "unit"})

            self.assertTrue(Path(record["path"]).exists())
            self.assertIn("robot_alpha", record["path"])
            self.assertEqual(record["shape"], [2, 2])
            self.assertEqual(record["metadata"]["source"], "unit")
            self.assertEqual(storage.load_events(limit=1)[0]["event_type"], "array_saved")

    def test_controller_restores_last_command_from_storage(self):
        """Controller should recover its last command from persisted state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = RuntimeStorage(base_dir=temp_dir, robot_id="robot_beta")
            storage.save_state("last_command", {"direction": "gauche", "speed": 0.4, "duration": 1.2})

            controller = RobotVisionController(storage=storage)

            self.assertEqual(controller.last_command, RobotCommand("gauche", 0.4, 1.2))

    def test_controller_process_frame_persists_runtime_memory(self):
        """Processing a frame should save frame data and command state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = RuntimeStorage(base_dir=temp_dir, robot_id="robot_gamma")
            controller = RobotVisionController(storage=storage)
            image = np.arange(16, dtype=np.uint8).reshape(4, 4)

            command = controller.process_frame(image)

            self.assertEqual(command.direction, "arrete")
            self.assertTrue(any(storage.arrays_dir.iterdir()))
            saved_state = storage.load_state("last_command")
            self.assertEqual(saved_state["direction"], "arrete")
            self.assertEqual(storage.load_events(limit=1)[0]["event_type"], "robot_command_generated")

    def test_controller_speaks_french(self):
        """Robot controller should expose French status messages."""
        controller = RobotVisionController()

        self.assertEqual(controller.speak("startup"), "Systeme de vision du robot pret.")
        self.assertEqual(controller.speak("unknown"), "Je communique en francais.")

    def test_storage_uses_robot_specific_folder(self):
        """Each robot should have its own internal storage area."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = RuntimeStorage(base_dir=temp_dir, robot_id="robot 42/fr")

            self.assertEqual(storage.robot_id, "robot_42_fr")
            self.assertTrue(str(storage.robot_path()).endswith("robot_42_fr"))


if __name__ == "__main__":
    unittest.main()
