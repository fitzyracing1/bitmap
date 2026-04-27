"""Lightweight file-backed storage for runtime artifacts and state."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import numpy as np


class RuntimeStorage:
    """Persist runtime artifacts and state inside the project."""

    def __init__(self, base_dir: str = "storage", robot_id: str = "robot_default"):
        self.root_dir = Path(base_dir)
        self.robot_id = self._sanitize_robot_id(robot_id)
        self.base_dir = self.root_dir / self.robot_id
        self.arrays_dir = self.base_dir / "arrays"
        self.state_dir = self.base_dir / "state"
        self.metadata_dir = self.base_dir / "metadata"
        self.events_file = self.base_dir / "events.jsonl"

        self.arrays_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.events_file.touch(exist_ok=True)

    def save_array(
        self,
        array: np.ndarray,
        *,
        prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save an array to disk and record metadata for later lookup."""
        timestamp = self._timestamp()
        identifier = f"{prefix}_{timestamp}_{uuid4().hex[:8]}"
        array_path = self.arrays_dir / f"{identifier}.npy"
        metadata_path = self.metadata_dir / f"{identifier}.json"

        np.save(array_path, array)

        record = {
            "id": identifier,
            "timestamp": timestamp,
            "path": str(array_path),
            "shape": list(array.shape),
            "dtype": str(array.dtype),
            "metadata": metadata or {},
        }

        metadata_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        self.append_event("array_saved", record)
        return record

    def save_state(self, name: str, payload: Any) -> Path:
        """Save JSON-serializable runtime state."""
        state_path = self.state_dir / f"{name}.json"
        serialized = self._serialize(payload)
        state_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        return state_path

    def load_state(self, name: str, default: Optional[Any] = None) -> Any:
        """Load previously saved runtime state."""
        state_path = self.state_dir / f"{name}.json"
        if not state_path.exists():
            return default

        return json.loads(state_path.read_text(encoding="utf-8"))

    def append_event(self, event_type: str, payload: Any) -> None:
        """Append a runtime event to the session log."""
        event = {
            "timestamp": self._timestamp(),
            "event_type": event_type,
            "payload": self._serialize(payload),
        }
        with self.events_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    def load_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load runtime events from disk."""
        lines = [
            json.loads(line)
            for line in self.events_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if limit is None:
            return lines
        return lines[-limit:]

    def robot_path(self) -> Path:
        """Return the storage path for the active robot."""
        return self.base_dir

    def _serialize(self, payload: Any) -> Any:
        if is_dataclass(payload):
            return asdict(payload)
        if isinstance(payload, np.ndarray):
            return payload.tolist()
        if isinstance(payload, Path):
            return str(payload)
        if isinstance(payload, dict):
            return {key: self._serialize(value) for key, value in payload.items()}
        if isinstance(payload, (list, tuple)):
            return [self._serialize(item) for item in payload]
        return payload

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _sanitize_robot_id(self, robot_id: str) -> str:
        normalized = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_"
            for char in robot_id.strip()
        )
        return normalized or "robot_default"
