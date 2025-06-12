import numpy as np
from typing import Sequence, Union

# 定義一個通用的型別別名
ArrayLikeF = Union[Sequence[float], np.ndarray]


def gamma_correction(linear_rgb: ArrayLikeF) -> np.ndarray:
    """
    sRGB Gamma 校正：將 0–255 的線性 RGB → 0–255 的 sRGB uint8。

    :param linear_rgb: 長度 3 的序列或 ndarray，各通道值應在 0–255
    :return:           uint8 ndarray，shape=(3,)
    """
    arr = np.asarray(linear_rgb, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"linear_rgb 形狀應為 (3,) ，但收到 {arr.shape}")

    def _srgb_comp(c: np.ndarray) -> np.ndarray:
        a = 0.055
        c = c / 255.0
        return np.where(c <= 0.0031308, 12.92 * c, (1 + a) * np.power(c, 1 / 2.4) - a)

    srgb = _srgb_comp(arr)
    srgb_255 = np.clip(srgb * 255.0, 0, 255)
    return np.round(srgb_255).astype(np.uint8)
