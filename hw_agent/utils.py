import numpy as np


def sensor_to_mixbox(R_raw, G_raw, B_raw, C, M):
    r, g, b = R_raw / C, G_raw / C, B_raw / C
    r_lin, g_lin, b_lin = M.T @ np.array([r, g, b]).clip(0, 1)
    to8 = lambda x: int(round((x**1 / 2.2) * 255))
    return to8(r_lin), to8(g_lin), to8(b_lin)
