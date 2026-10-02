from typing import List
import numpy as np
from .types import Detection


class NullClassifier:
    def detect(self, color: np.ndarray) -> List[Detection]:
        return []


class UltralyticsClassifier:
    def __init__(self, weights: str, confidence: float = 0.45):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("ultralytics is required for YOLO inference") from exc
        self.model = YOLO(weights)
        self.confidence = confidence

    def detect(self, color: np.ndarray) -> List[Detection]:
        result = self.model.predict(color, conf=self.confidence, verbose=False)[0]
        names = result.names
        detections = []
        if result.masks is None:
            return detections
        masks = result.masks.data.cpu().numpy()
        for i, box in enumerate(result.boxes):
            cls = int(box.cls[0].item())
            xyxy = tuple(int(v) for v in box.xyxy[0].tolist())
            detections.append(Detection(str(names[cls]), float(box.conf[0].item()), masks[i].astype(bool), xyxy))
        return detections


def class_at_pixel(detections: List[Detection], x: int, y: int):
    for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
        if 0 <= y < detection.mask.shape[0] and 0 <= x < detection.mask.shape[1] and detection.mask[y, x]:
            return detection.class_name
    return None

