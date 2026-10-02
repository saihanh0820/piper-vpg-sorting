import numpy as np


def depth_to_height_map(depth, floor_depth, depth_scale=0.001, min_height=0.004, max_height=0.30):
    """Convert aligned depth to a fixed-camera height map in metres.

    `floor_depth` may be a scalar for a flat calibrated tray or an image-sized
    plane model for a perspective camera. Invalid and over-range samples are
    masked to zero so the policy cannot select them.
    """
    depth_m = np.asarray(depth, dtype=np.float32)
    if np.nanmedian(depth_m) > 5.0:
        depth_m = depth_m * float(depth_scale)
    floor_m = np.asarray(floor_depth, dtype=np.float32)
    height = floor_m - depth_m
    valid = np.isfinite(depth_m) & np.isfinite(height) & (height >= float(min_height)) & (height <= float(max_height))
    return np.where(valid, height, 0.0).astype(np.float32)

