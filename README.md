# Piper-VPG 无序连接器推抓协同分拣

本工程是面向 Ubuntu 20.04 + ROS Noetic 的第一版可运行实现。它把 RGB-D 高度图、推/抓动作选择、Piper 运动适配、YOLO 实例分割和分类投放串成一个安全状态机。

## 重要边界

工程内置 `SimPiperBackend` 和合成 RGB-D 场景，可以不接硬件验证完整闭环。真实 Piper 驱动由官方 `piper_ros` 节点独占 `can0`；本工程不会初始化 CAN，也不会直接调用 `piper_sdk`。由于实施说明没有提供现场 Piper 工程、Topic、Service、手眼标定和日志，真实后端的 Topic 名称必须在现场确认后写入配置，不能直接把示例参数用于机械臂。

## Ubuntu 安装

```bash
sudo apt update
sudo apt install -y python3-pip python3-numpy python3-yaml ros-noetic-rospy \
  ros-noetic-geometry-msgs ros-noetic-std-msgs ros-noetic-sensor-msgs
cd piper_vpg_sorting
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

如果使用真实相机，再安装并启动官方 RealSense ROS 驱动；如果使用真实分类模型，再安装与 CUDA/PyTorch 匹配的 `ultralytics`。VPG 原版权重应放在 `weights/vpg_pretrained.pth`，本工程的 `VPGPolicy` 留有权重推理接口；没有权重时使用可解释的安全启发式策略，便于联调，不能作为最终竞赛策略指标。

## 先验证软件闭环

```bash
source .venv/bin/activate
PYTHONPATH=src python3 scripts/run_demo.py --steps 20
```

预期看到每一步的 `push`/`grasp`、像素位置、执行结果和最后统计。单元测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## 接入 ROS

1. 单独启动官方 `piper_ros` 驱动，确认只有它连接 `can0`。
2. 启动 RealSense 官方 ROS 节点，确认彩色图和深度图已对齐。
3. 把真实 Topic/Service、观察位、工作区标定和料盒位置填入 `config/*.yaml`。
4. 先运行 `scripts/single_action_test.py` 的人工安全动作测试，再启动分拣节点。

```bash
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch piper_vpg_ros piper_vpg_sorting.launch use_sim:=false
```

真实适配层只向 ROS 发布末端位姿和夹爪命令，动作完成状态由 `/arm_status` 读取。不同版本的 Piper 官方驱动消息接口可能不同，需在 `piper_ros_backend.py` 中按已验证的现场消息类型完成最后映射；该文件不包含未经确认的 CAN 协议假设。高度图转换函数位于 `src/piper_vpg_core/heightmap.py`，现场应使用标定的托盘平面深度生成它。

## 数据和模型

YOLO 数据集建议使用 `dataset.yaml` 的三类名称 `connector_a`、`connector_b`、`connector_c`，并覆盖方向、遮挡和光照变化。推理节点只负责实例分割；VPG 负责动作，不把分类结果混入动作网络。模型放置：

```text
weights/connector_seg.pt
weights/vpg_pretrained.pth
```

第一版真机只加载预训练策略，记录数据，不做高随机探索。安全保护触发或连续失败达到上限时，状态机停止而不是继续发新动作。
