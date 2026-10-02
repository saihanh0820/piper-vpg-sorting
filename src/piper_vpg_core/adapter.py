import time
from typing import Callable, Dict, Optional
import numpy as np
from .types import ExecutionResult, Observation


class SimPiperBackend:
    """A tiny backend for end-to-end testing without CAN or a robot."""

    def __init__(self, objects=None):
        self.objects = list(objects or [])
        self.last_action = "observe"

    def return_to_observe(self, pose, settle_seconds):
        time.sleep(min(float(settle_seconds), 0.01))
        self.last_action = "observe"
        return ExecutionResult(True, "simulated observe")

    def push(self, position, angle, length, timeout):
        self.last_action = "push"
        moved = 0
        dx, dy = np.cos(angle) * length, np.sin(angle) * length
        for obj in self.objects:
            if abs(obj[0] - position[0]) < 0.07 and abs(obj[1] - position[1]) < 0.07:
                obj[0] += float(dx); obj[1] += float(dy); moved += 1
        return ExecutionResult(moved > 0, "simulated push" if moved else "no object moved", metadata={"moved": moved})

    def grasp(self, position, angle, timeout):
        self.last_action = "grasp"
        for index, obj in enumerate(self.objects):
            if abs(obj[0] - position[0]) < 0.07 and abs(obj[1] - position[1]) < 0.07:
                self.objects.pop(index)
                return ExecutionResult(True, "simulated grasp", metadata={"object": obj[2]})
        return ExecutionResult(False, "no object at grasp point")

    def place(self, bin_id, bins, timeout):
        return ExecutionResult(True, "simulated place", metadata={"bin": bin_id})


class SafePiperVPGAdapter:
    """Safety and coordinate boundary around one already-running Piper driver."""

    def __init__(self, backend, workspace: dict, observe_pose: dict, bins: dict, camera_provider: Optional[Callable] = None):
        self.backend = backend
        self.ws = workspace["workspace"]
        self.config = workspace
        self.observe_pose = observe_pose
        self.bins = bins
        self.camera_provider = camera_provider

    def get_camera_data(self) -> Observation:
        if self.camera_provider is None:
            raise RuntimeError("camera_provider is not configured")
        return self.camera_provider()

    def return_to_observe(self):
        return self.backend.return_to_observe(self.observe_pose, self.config.get("settle_seconds", 0.8))

    def pixel_to_position(self, x: int, y: int, depth_m: float):
        fx, fy = float(self.config["camera_fx"]), float(self.config["camera_fy"])
        cx, cy = float(self.config["camera_cx"]), float(self.config["camera_cy"])
        z = float(depth_m) * float(self.config.get("depth_scale", 0.001)) if depth_m > 1.0 else float(depth_m)
        # Camera-to-base extrinsics are identity by default for simulation.
        px, py = (x - cx) * z / fx, (y - cy) * z / fy
        return px, py, z

    def _inside(self, position):
        x, y, z = position
        return self.ws["x_min"] <= x <= self.ws["x_max"] and self.ws["y_min"] <= y <= self.ws["y_max"] and self.ws["z_min"] <= z <= self.ws["z_max"]

    def push(self, position, angle, length=0.05):
        if length <= 0 or length > float(self.config["max_push_length"]):
            return ExecutionResult(False, "push length exceeds safety limit")
        if not self._inside(position):
            return ExecutionResult(False, "push start is outside workspace")
        end = (position[0] + np.cos(angle) * length, position[1] + np.sin(angle) * length, position[2])
        if not self._inside(end):
            return ExecutionResult(False, "push end is outside workspace")
        return self.backend.push(position, angle, length, float(self.config["max_action_seconds"]))

    def grasp(self, position, angle):
        if not self._inside(position):
            return ExecutionResult(False, "grasp is outside workspace")
        return self.backend.grasp(position, angle, float(self.config["max_action_seconds"]))

    def place(self, bin_id):
        if bin_id not in self.bins:
            return ExecutionResult(False, "unknown sorting bin")
        return self.backend.place(bin_id, self.bins, float(self.config["max_action_seconds"]))

