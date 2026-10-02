#!/usr/bin/env python3
"""ROS entry point; site-specific Piper message mappings stay in the backend."""
import os
import sys
import time
import yaml
import rospy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from piper_vpg_core import VPGPolicy, SafePiperVPGAdapter, SimPiperBackend, SortingManager
from piper_vpg_core.types import Observation


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main():
    rospy.init_node("sorting_manager")
    workspace = load_yaml(rospy.get_param("~workspace_config"))
    observe = load_yaml(rospy.get_param("~observe_config")).get("observe_pose", {})
    bins = load_yaml(rospy.get_param("~bins_config")).get("bins", {})
    if not rospy.get_param("~use_sim", True):
        rospy.logerr("Real Piper backend is intentionally not guessed. Implement verified Topic/Service mappings in piper_ros_backend.py before use.")
        return
    backend = SimPiperBackend([])
    adapter = SafePiperVPGAdapter(backend, workspace, observe, bins, camera_provider=lambda: Observation(None, None, time.time()))
    rospy.loginfo("piper_vpg_ros is configured for simulation; use scripts/run_demo.py for the no-ROS software loop")


if __name__ == "__main__":
    main()

