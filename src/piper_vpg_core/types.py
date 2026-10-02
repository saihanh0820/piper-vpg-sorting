from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class Observation:
    color: np.ndarray
    depth: np.ndarray
    timestamp: float
    frame_id: str = "camera_color_optical_frame"
    height_map: Optional[np.ndarray] = None


@dataclass
class Action:
    primitive: str
    pixel: Tuple[int, int]
    angle: float
    position: Tuple[float, float, float]
    score: float
    q_push: Optional[np.ndarray] = None
    q_grasp: Optional[np.ndarray] = None


@dataclass
class Detection:
    class_name: str
    confidence: float
    mask: np.ndarray
    bbox: Tuple[int, int, int, int]


@dataclass
class ExecutionResult:
    success: bool
    reason: str = ""
    elapsed: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class SortStats:
    actions: int = 0
    pushes: int = 0
    grasps: int = 0
    successful_grasps: int = 0
    placed: int = 0
    failures: int = 0
    by_class: Dict[str, int] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
