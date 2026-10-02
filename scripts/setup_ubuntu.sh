#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sudo apt update
sudo apt install -y python3-pip python3-venv python3-numpy python3-yaml \
  ros-noetic-rospy ros-noetic-sensor-msgs ros-noetic-std-msgs ros-noetic-geometry-msgs
python3 -m venv "$PROJECT_DIR/.venv" --system-site-packages
# shellcheck disable=SC1091
source "$PROJECT_DIR/.venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$PROJECT_DIR/requirements.txt"
mkdir -p "$PROJECT_DIR/catkin_ws/src"
if [ ! -e "$PROJECT_DIR/catkin_ws/src/piper_vpg_ros" ]; then
  ln -s "$PROJECT_DIR/piper_vpg_ros" "$PROJECT_DIR/catkin_ws/src/piper_vpg_ros"
fi
echo "Environment prepared. Build with: cd $PROJECT_DIR/catkin_ws && catkin_make"

