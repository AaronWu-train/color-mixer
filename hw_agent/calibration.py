import numpy as np
from typing import Sequence, List


def calibrate_black_point(raw_rgbc: np.ndarray) -> np.ndarray:
    """
    校正黑點，將 RGBC 值調整為接近黑色。

    :param raw_rgbc: 原始感測器讀值 (長度 4)
    :return: 校正後的 RGBC (numpy.ndarray)
    """
    pass


def calibrate_white_point(raw_rgbc: np.ndarray) -> np.ndarray:
    """
    校正白點，將 RGB 值調整為接近白色。

    :param raw_rgb: 原始感測器讀值 (長度 4)
    :return: 校正後的 RGBC (numpy.ndarray)
    """
    pass


def remove_clear_channel(raw_rgbc: np.ndarray) -> np.ndarray:
    """
    移除清晰通道 (Clear Channel)，將 RGBC 轉為 RGB。
    將 RGB 值正規化到 0-1 範圍。

    :param raw_rgbc: 原始感測器讀值 (長度 4)
    :return: 校正後的 RGB (numpy.ndarray) (長度 3)
    """
    if raw_rgbc.shape != (4,):
        raise ValueError(f"raw_rgbc 形狀應為 (4,) ，但收到 {raw_rgbc.shape}")

    R, G, B, C = raw_rgbc

    return np.array([R / C, G / C, B / C], dtype=float)


def calibrate_rgb(raw_rgb: Sequence[float]) -> List[float]:
    """
    將感測器讀到的 RGB (長度 3) 校正到目標色域。

    :param raw_rgb: 原始感測器讀值 [R, G, B]
    :return: 校正後的 RGB (list of float)
    """
    # 感測器對 4 種純色的讀值 (4×3)
    V = np.array(
        [
            [0.6583, 0.13527, 0.20643],  # magenta
            [0.09125, 0.33225, 0.57650],  # cerulean blue
            [0.48436, 0.37671, 0.13893],  # yellow
            [0.31009, 0.36779, 0.32212],  # white
        ],
        dtype=float,
    )
    # 理想值 (4×3)
    R = np.array(
        [
            [0.7422, 0.0088, 0.2490],
            [0.0000, 0.2640, 0.7360],
            [0.6030, 0.3970, 0.0000],
            [0.3333, 0.3333, 0.3333],
        ],
        dtype=float,
    )
    # 計算校正矩陣 M (3×3)
    M = np.linalg.pinv(V) @ R

    # 轉為陣列並檢查
    raw = np.asarray(raw_rgb, dtype=float)
    if raw.shape != (3,):
        raise ValueError(f"raw_rgb 形狀應為 (3,) ，但收到 {raw.shape}")

    # 線性轉換並回傳 list
    calibrated = raw @ M
    # 確保校正後的值在 0-1 範圍內
    calibrated = np.clip(calibrated, 0, 1)

    return calibrated.tolist()


import numpy as np
from typing import Union, Sequence


def gamma_correction(linear_rgb: Union[Sequence[float], np.ndarray]) -> np.ndarray:
    """
    將 0–1 範圍的 linear RGB 轉換為 0–255 的 sRGB（以 uint8 表示）。

    :param linear_rgb: 長度 3 的序列或陣列，各通道值應在 0–1 之間
    :return: 對應的 sRGB 值，型態為 np.ndarray，元素為 0–255 的 uint8
    """
    # 轉為 numpy 陣列
    arr = np.asarray(linear_rgb, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"輸入必須為長度 3 的向量，但收到形狀 {arr.shape}")

    # sRGB Gamma 校正函式
    def _srgb_comp(c: np.ndarray) -> np.ndarray:
        a = 0.055
        # <= 0.0031308 部分: 線性放大；其他: 指數校正
        return np.where(c <= 0.0031308, 12.92 * c, (1 + a) * np.power(c, 1 / 2.4) - a)

    # 套用到每個通道
    srgb = _srgb_comp(arr)
    # 轉到 0–255 範圍並取整
    srgb_255 = np.clip(srgb * 255.0, 0, 255).round().astype(np.uint8)
    return srgb_255


if __name__ == "__main__":
    raw = [0.09125, 0.33225, 0.57650]
    corrected = calibrate_rgb(raw)
    print("校正後 RGB: ", corrected)
