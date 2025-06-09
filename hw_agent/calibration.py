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

    return np.array([R, G, B], dtype=float)


def calibrate_rgb(raw_rgb: Sequence[float]) -> List[float]:
    """
    將感測器讀到的 RGB (長度 3) 校正到目標色域。

    :param raw_rgb: 原始感測器讀值 [R, G, B]
    :return: 校正後的 RGB (list of float)
    """
    # 感測器對多種純色的讀值 (4×3)
    V = np.array(
        [
            [128, 80, 111],  # magenta
            [239, 191, 104],  # yellow
            [73, 100, 126], # cerulean blue
            [90, 108, 74], # green
            [71, 71, 108], #purple
            [139, 78, 91], # orange
            #[255, 255, 255],  # white
        ],
        dtype=float,
    )
    # 理想值 (4×3)
    R = np.array(
        [
            [202, 20, 123], # magenta
            [240, 220, 100], # yellow
            [0, 134, 210], # cerulean blue
            [30, 195, 105], # green
            [80, 60, 155], # purple
            [135, 130, 20], # orange
            #[255, 255, 255], # white
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
        c /= 255.0
        # <= 0.0031308 部分: 線性放大；其他: 指數校正
        return np.where(c <= 0.0031308, 12.92 * c, (1 + a) * np.power(c, 1 / 2.4) - a)

    # 套用到每個通道
    srgb = _srgb_comp(arr)
    # 轉到 0–255 範圍並取整
    srgb_255 = np.clip(srgb * 255.0, 0, 255).round().astype(np.uint8)
    return srgb_255


if __name__ == "__main__":
    raw = [65, 90, 84]
    rgb_lin255 = calibrate_rgb(raw)
    rgb_srgb8 = gamma_correction(rgb_lin255)
    print("校正後 RGB: ", rgb_srgb8)
