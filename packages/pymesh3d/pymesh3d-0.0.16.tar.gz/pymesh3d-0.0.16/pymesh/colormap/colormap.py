import matplotlib.pyplot as plt

class Colormap(object):
    def __init__(self, cmap, vmin, vmax):
        self.cmap, self.vmin, self.vmax = cmap, vmin, vmax
        