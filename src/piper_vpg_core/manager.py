import time
from .classifier import class_at_pixel
from .types import ExecutionResult, SortStats


class SortingManager:
    def __init__(self, adapter, policy, classifier, max_steps=100):
        self.adapter = adapter
        self.policy = policy
        self.classifier = classifier
        self.max_steps = max_steps
        self.max_failures = int(adapter.config.get("max_consecutive_failures", 3))
        self.stats = SortStats()

    def run(self):
        consecutive_failures = 0
        for _ in range(self.max_steps):
            observe_result = self.adapter.return_to_observe()
            if not observe_result.success:
                self.stats.failures += 1
                self.stats.history.append({"action": "observe", "success": False, "reason": observe_result.reason})
                break
            observation = self.adapter.get_camera_data()
            action = self.policy.select_action(observation, self.adapter.pixel_to_position)
            if action is None:
                break
            self.stats.actions += 1
            started = time.time()
            if action.primitive == "push":
                self.stats.pushes += 1
                result = self.adapter.push(action.position, action.angle)
                target_class = None
            else:
                self.stats.grasps += 1
                detections = self.classifier.detect(observation.color)
                target_class = class_at_pixel(detections, *action.pixel)
                if target_class is None:
                    result = ExecutionResult(False, "no YOLO class at grasp pixel")
                else:
                    result = self.adapter.grasp(action.position, action.angle)
                    if result.success:
                        self.stats.successful_grasps += 1
                        placed = self.adapter.place(target_class)
                        result.success = result.success and placed.success
                        if placed.success:
                            self.stats.placed += 1
                            self.stats.by_class[target_class] = self.stats.by_class.get(target_class, 0) + 1
            if not result.success:
                consecutive_failures += 1
                self.stats.failures += 1
            else:
                consecutive_failures = 0
            self.stats.history.append({"action": action.primitive, "pixel": action.pixel, "score": action.score, "class": target_class, "success": result.success, "reason": result.reason, "elapsed": time.time() - started})
            if consecutive_failures >= self.max_failures:
                break
        return self.stats
