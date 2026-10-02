"""Piper ROS boundary.

This module documents the only hardware ownership boundary. Fill in the
message/service types after inspecting the installed official piper_ros
version and a known-good single-grasp program. Never create a second CAN
connection here.
"""


class PiperROSBackend:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Configure this backend with the verified piper_ros topics/services; "
            "the current project intentionally makes no unverified hardware assumptions."
        )

