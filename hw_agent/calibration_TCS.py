import numpy as np

V = np.array(
    [
        [0.6583, 0.13527, 0.20643],  # magenta
        [0.09125, 0.33225, 0.5765],  # cerulean blue
        [0.48436, 0.37671, 0.13893],  # yellow
        [0.31009, 0.36779, 0.32212],
    ]
)  # white
R = np.array(
    [
        [0.7422, 0.0088, 0.2490],  # magenta
        [0.0000, 0.2640, 0.7360],  # cerulean blue
        [0.6030, 0.3970, 0.0000],
        [0.3333, 0.3333, 0.3333],
    ]
)

M = np.linalg.pinv(V) @ R
print("M:", M)
