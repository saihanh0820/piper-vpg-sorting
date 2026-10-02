#!/usr/bin/env python3
"""Manual safety test scaffold. Replace the backend only after interface audit."""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from piper_vpg_core import SafePiperVPGAdapter, SimPiperBackend


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("push", "grasp"), required=True)
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=0.08)
    args = parser.parse_args()
    config = {"max_push_length": .05, "max_action_seconds": 12, "workspace": {"x_min": -.28, "x_max": .28, "y_min": -.22, "y_max": .22, "z_min": .035, "z_max": .32}}
    adapter = SafePiperVPGAdapter(SimPiperBackend([[args.x, args.y, args.z, "test"]]), config, {}, {"test": {}})
    result = adapter.push((args.x, args.y, args.z), 0.0, .03) if args.action == "push" else adapter.grasp((args.x, args.y, args.z), 0.0)
    print(result)


if __name__ == "__main__":
    main()

