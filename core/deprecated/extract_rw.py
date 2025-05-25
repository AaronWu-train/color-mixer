import cv2, numpy as np, json

# 1. 讀兩張 TIFF
img_white = cv2.imread("IMG_6107.tiff", cv2.IMREAD_UNCHANGED).astype(np.float32)
img_black = cv2.imread("IMG_6111.tiff", cv2.IMREAD_UNCHANGED).astype(np.float32)

# 2. 在 White 圖擷取「白紙」與「油漆」ROI
#    (填上你量到的白底 ROI 座標)
roi_ref = img_white[150:600, 100:500]  # 白紙
roi_paint = img_white[1500:1800, 1100:1400]  # 油漆區（白底）

# 3. 在 Black 圖擷取「油漆」ROI
#    (填上你量到的黑底油漆 ROI 座標)
roi_paint_black = img_black[1500:1700, 1200:1500]

# 4. 計算 D 值
D_ref = roi_ref.mean(axis=(0, 1))  # 白底參考
D_paint_w = roi_paint.mean(axis=(0, 1))  # 油漆 （白底）
D_paint_b = roi_paint_black.mean(axis=(0, 1))  # 油漆 （黑底）

# 5. 算反射率與 K/S
Rw = D_paint_w / D_ref
R0 = D_paint_b / D_ref
KS = (1 - Rw) ** 2 / (2 * Rw)
opacity = 1 - R0 / Rw

print(
    json.dumps(
        {
            "Rw": Rw.tolist(),  # 在白底時的反射率(理想：0~1)
            "R0": R0.tolist(),  # 在黑底時的反射率(理想：0~1)
            "K/S": KS.tolist(),  # 吸收/散射比
            "opacity": opacity.tolist(),  # 不透明度
        },
        indent=2,
    )
)
