import numpy as np

def raw_to_rgb(r_raw, g_raw, b_raw, c_raw):
    r = float(r_raw) / c_raw
    g = float(g_raw) / c_raw
    b = float(b_raw) / c_raw
    
    cal_sensor = np.array("magenta")
    cal_ref_lin = np.array([1, 0, 0])
    A = cal_sensor.T
    B = cal_ref_lin.T
    M = (B@np.linalg.pinv(A)).T
