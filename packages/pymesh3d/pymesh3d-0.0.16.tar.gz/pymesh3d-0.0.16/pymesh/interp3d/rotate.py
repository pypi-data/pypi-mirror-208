import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

@njit(parallel = True)
def interpolate_3d(ey, res):
    m, n = ey.shape[0], ey.shape[1]
    y0 = (n - 1)/2
    z0 = (n - 1)/2
    for i in prange(m):
        for j in range(n):
            for k in range(n):
                r = int(np.sqrt((j - y0)**2 + (k - y0)**2))
                if int(y0 + r) > n - 1 or int(y0 - r) < 0:
                    continue
                z = k - z0
                y = j - y0
                theta = np.arctan2(z, y)
                if np.abs(theta) <= 3.14/2:
                    res[i, j, k] = ey[i, int(y0 + r)]
                #else:
                #    res[i, j, k] = ey[i, int(y0 - r)]
            
    return

@njit(parallel = True)
def rotate_total(ey, res):
    m, n = ey.shape[0], ey.shape[1]
    y0 = (n - 1)/2
    z0 = (n - 1)/2
    for i in prange(m):
        for j in range(n):
            for k in range(n):
                r = int(np.sqrt((j - y0)**2 + (k - y0)**2))
                if int(r + y0) < n:
                    res[i, j, k] = ey[i, int(r + y0)]
    
    return

def rotate(ey, res, ifhalf = False):
    if ifhalf:
        interpolate_3d(ey, res)
    else:
        rotate_total(ey, res)
    return