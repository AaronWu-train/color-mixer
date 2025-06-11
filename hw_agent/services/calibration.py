import numpy as np
from typing import Sequence, Union

# ——— 校正參考值 ———
BLACK_REF = np.array([0, 0, 0, 0], dtype=float)
WHITE_REF = np.array([5853, 7351, 6247, 20401], dtype=float)

# 定義一個通用的型別別名
ArrayLikeF = Union[Sequence[float], np.ndarray]


def normalize(
    raw: ArrayLikeF, white: ArrayLikeF = WHITE_REF, black: ArrayLikeF = BLACK_REF
) -> np.ndarray:
    """
    將 raw value 依校正值 remap 至 0-1 float ndarray。

    :param raw:     原始通道值，一維長度與 white/black 相同
    :param white:   白板參考值
    :param black:   黑板參考值
    :return:        uint8 ndarray，值域 [0,1]，長度與輸入相同
    """
    arr_raw = np.asarray(raw, dtype=float)
    arr_white = np.asarray(white, dtype=float)
    arr_black = np.asarray(black, dtype=float)

    if arr_raw.shape != arr_white.shape or arr_raw.shape != arr_black.shape:
        raise ValueError(
            f"raw, white, black 必須形狀一致，收到 {arr_raw.shape}, {arr_white.shape}, {arr_black.shape}"
        )

    norm = (arr_raw - arr_black) / (arr_white - arr_black)
    return np.clip(norm, 0, 10000).astype(np.float32)


def remove_clear_channel(rgbc: ArrayLikeF) -> np.ndarray:
    """
    移除 Clear channel，將 RGBC → RGB。

    :param rgbc: 一維長度 4 的序列或 ndarray
    :return:     一維長度 3 的 ndarray，dtype 與輸入相同（通常 uint16/int）
    """
    arr = np.asarray(rgbc)
    if arr.shape != (4,):
        raise ValueError(f"rgbc 形狀應為 (4,) ，但收到 {arr.shape}")
    r, g, b, c = arr
    r_c = r / c * 255 / 1.8 if c != 0 else 0
    g_c = g / c * 255 / 2 if c != 0 else 0
    b_c = b / c * 255 / 2 if c != 0 else 0
    new_arr = np.array([r_c, g_c, b_c])
    new_arr = np.clip(new_arr, 0, 255)  # 確保值在 0–255 範圍內
    return new_arr.astype(np.uint8)  # 回傳 uint8 ndarray


def calibrate_rgb(raw_rgb: ArrayLikeF) -> np.ndarray:
    """
    將感測器讀到的 RGB 校正到目標色域。
    回傳 float ndarray（線性 RGB，以 0–255 為範圍）。

    :param raw_rgb: 原始感測器讀值，一維長度 3
    :return:        校正後的線性 RGB，一維長度 3，dtype float
    """
    # 量測純色值 (V) 與理想純色值 (R)，各 shape=(6,3)
    V = np.array(
        [
            [255, 76, 141],  # magenta
            [255, 235, 99],  # yellow
            [63, 111, 235],  # cerulean blue
            [133, 165, 119],  # green
            [130, 94, 212],  # purple
            [255, 105, 89],  # orange
            #[89, 99, 208], # new purple
        ],
        dtype=float,
    )
    R = np.array(
        [
            [202, 20, 123],
            [240, 220, 100],
            [0, 134, 210],
            [60, 160, 65],
            [125, 75, 205],  # purple
            [237, 128, 60],
            #[170, 140, 250], 
        ],
        dtype=float,
    )

    # 計算 3×3 校正矩陣
    M = np.linalg.pinv(V) @ R

    arr = np.asarray(raw_rgb, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"raw_rgb 形狀應為 (3,) ，但收到 {arr.shape}")

    return arr @ M  # 回傳 float ndarray shape=(3,)


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


if __name__ == "__main__":
    raw = [65, 90, 84]
    rgb_lin255 = calibrate_rgb(raw)
    rgb_srgb8 = gamma_correction(rgb_lin255)
    print("校正後 RGB: ", rgb_srgb8)
