from .calibration import *
from ..drivers.colorsensor import readSensorRawRGB
from ..models import RGBColorArray
import numpy as np


async def getColor() -> RGBColorArray:

    r, g, b, c = await readSensorRawRGB()
    raw = np.array([r, g, b, c], dtype=float)

    normalized = normalize(raw)  # 0-255
    clear_removed = remove_clear_channel(normalized)  # 0-255
    rgb_calibrated = calibrate_rgb(clear_removed)  # 0-255
    r, g, b = rgb_calibrated

    return RGBColorArray(r=r, g=g, b=b)
