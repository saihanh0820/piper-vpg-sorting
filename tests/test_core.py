import unittest
import numpy as np
from piper_vpg_core import Observation, VPGPolicy, SafePiperVPGAdapter, SimPiperBackend, SortingManager
from piper_vpg_core.types import Detection
from piper_vpg_core.classifier import class_at_pixel


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.workspace = {"camera_fx": 100, "camera_fy": 100, "camera_cx": 10, "camera_cy": 10, "depth_scale": .001, "floor_z": .02, "min_object_height": .004, "max_push_length": .05, "max_action_seconds": 1, "max_consecutive_failures": 3, "workspace": {"x_min": -.28, "x_max": .28, "y_min": -.22, "y_max": .22, "z_min": .035, "z_max": .32}}
    def test_policy_finds_object(self):
        depth = np.full((20, 20), 20., dtype=np.float32); depth[10, 10] = 100.
        action = VPGPolicy(self.workspace).select_action(Observation(np.zeros((20,20,3), dtype=np.uint8), depth, 0), lambda x,y,z: (0,0,.1))
        self.assertIsNotNone(action); self.assertIn(action.primitive, ("push", "grasp"))
    def test_push_limit(self):
        backend = SimPiperBackend([]); adapter = SafePiperVPGAdapter(backend, self.workspace, {}, {})
        self.assertFalse(adapter.push((0, 0, .1), 0, .051).success)
    def test_mask_class(self):
        mask = np.zeros((3,3), dtype=bool); mask[1,1] = True
        self.assertEqual(class_at_pixel([Detection("connector_a", .9, mask, (0,0,2,2))], 1, 1), "connector_a")


if __name__ == "__main__":
    unittest.main()

