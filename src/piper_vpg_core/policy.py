import math
from typing import Optional
import numpy as np
from .types import Action, Observation


class VPGPolicy:
    """VPG-compatible action interface.

    A supplied VPG checkpoint can replace `predict_q_maps`. The fallback is a
    deterministic height-map policy for hardware and integration bring-up.
    """

    def __init__(self, workspace: dict, rotations: int = 16):
        self.workspace = workspace
        self.rotations = rotations
        self.floor_z = float(workspace.get("floor_z", 0.02))
        self.min_height = float(workspace.get("min_object_height", 0.004))

    def predict_q_maps(self, height: np.ndarray):
        h = np.nan_to_num(height.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        occupancy = np.maximum(h - self.floor_z, 0.0)
        padded = np.pad(occupancy, 1, mode="edge")
        local = sum(padded[dy:dy + h.shape[0], dx:dx + h.shape[1]] for dy in range(3) for dx in range(3)) / 9.0
        gy, gx = np.gradient(occupancy)
        edge = np.hypot(gx, gy)
        valid = occupancy >= self.min_height
        # These maps have the same semantic contract as VPG's pixel Q maps.
        grasp = np.where(valid, 0.7 * occupancy + 0.3 * local, -1e6)
        push = np.where(valid, 0.5 * edge + 0.25 * occupancy + 0.25 * np.abs(occupancy - local), -1e6)
        return push, grasp, gx, gy

    def select_action(self, observation: Observation, pixel_to_position) -> Optional[Action]:
        height = observation.height_map if observation.height_map is not None else observation.depth
        push, grasp, gx, gy = self.predict_q_maps(height)
        p_i = np.unravel_index(int(np.argmax(push)), push.shape)
        g_i = np.unravel_index(int(np.argmax(grasp)), grasp.shape)
        p_score, g_score = float(push[p_i]), float(grasp[g_i])
        if max(p_score, g_score) <= -1e5:
            return None
        if p_score > g_score * 1.05:
            row, col = p_i
            # Push across the local image gradient. The angle is in radians.
            angle = math.atan2(float(gy[row, col]), float(gx[row, col])) + math.pi / 2.0
            primitive, chosen, score = "push", p_i, p_score
        else:
            row, col = g_i
            angle = 0.0
            primitive, chosen, score = "grasp", g_i, g_score
        position = pixel_to_position(int(chosen[1]), int(chosen[0]), float(height[chosen]))
        return Action(primitive, (int(chosen[1]), int(chosen[0])), angle, position, score, push, grasp)
