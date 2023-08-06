import numpy as np
import matplotlib.pyplot as plt

def interp_color(iso_vals, pltmap = plt.cm.jet):
    
    vmax = iso_vals.max()
    vmin = iso_vals.min()
    
    xp = [vmin, vmax]
    fp = [0, 256]
    color = pltmap(np.interp(iso_vals, xp, fp))
    return