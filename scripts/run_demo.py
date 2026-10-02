#!/usr/bin/env python3
import argparse
import time
import numpy as np
from piper_vpg_core import Observation, VPGPolicy, SafePiperVPGAdapter, SimPiperBackend, SortingManager
from piper_vpg_core.classifier import class_at_pixel
from piper_vpg_core.types import Detection


class SyntheticClassifier:
    def __init__(self, backend, width=640, height=480):
        self.backend, self.width, self.height = backend, width, height

    def detect(self, color):
        detections = []
        for x, y, z, name in self.backend.objects:
            px, py = int(320 + x * 615 / max(z, 0.05)), int(240 + y * 615 / max(z, 0.05))
            mask = np.zeros((self.height, self.width), dtype=bool)
            mask[max(0, py - 7):py + 8, max(0, px - 7):px + 8] = True
            detections.append(Detection(name, 0.99, mask, (px - 7, py - 7, px + 7, py + 7)))
        return detections


def make_camera(backend, width=640, height=480):
    def provider():
        depth = np.full((height, width), 20.0, dtype=np.float32)
        height_map = np.zeros((height, width), dtype=np.float32)
        color = np.zeros((height, width, 3), dtype=np.uint8)
        for x, y, z, _name in backend.objects:
            px, py = int(320 + x * 615 / max(z, 0.05)), int(240 + y * 615 / max(z, 0.05))
            if 4 <= px < width - 4 and 4 <= py < height - 4:
                depth[py - 4:py + 5, px - 4:px + 5] = z * 1000.0 + 12.0
                height_map[py - 4:py + 5, px - 4:px + 5] = z
                color[py - 4:py + 5, px - 4:px + 5] = (40, 180, 230)
        return Observation(color, depth, time.time(), height_map=height_map)
    return provider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()
    workspace = {"camera_fx": 615, "camera_fy": 615, "camera_cx": 320, "camera_cy": 240, "depth_scale": 0.001, "floor_z": 0.02, "min_object_height": 0.004, "max_push_length": 0.05, "max_action_seconds": 12, "max_consecutive_failures": 3, "workspace": {"x_min": -0.28, "x_max": 0.28, "y_min": -0.22, "y_max": 0.22, "z_min": 0.035, "z_max": 0.32}}
    # Keep synthetic objects inside the camera frustum while remaining inside the tray workspace.
    objects = [[-0.02, -0.02, 0.10, "connector_a"], [0.04, 0.03, 0.09, "connector_b"], [0.01, -0.03, 0.11, "connector_c"]]
    backend = SimPiperBackend(objects)
    adapter = SafePiperVPGAdapter(backend, workspace, {}, {"connector_a": {}, "connector_b": {}, "connector_c": {}}, make_camera(backend))
    stats = SortingManager(adapter, VPGPolicy(workspace), SyntheticClassifier(backend), args.steps).run()
    for item in stats.history:
        print(f"{item['action']:6s} pixel={item['pixel']} success={item['success']} reason={item['reason']}")
    print(f"actions={stats.actions} pushes={stats.pushes} grasps={stats.grasps} remaining={len(backend.objects)}")


if __name__ == "__main__":
    main()
