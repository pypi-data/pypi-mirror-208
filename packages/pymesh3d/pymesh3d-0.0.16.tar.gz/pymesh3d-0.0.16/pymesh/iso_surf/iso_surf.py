import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .marching_cubes import ger_iso_meshs, mesh_concatenate
from ..colormap import Colormap
from ..mesh import Mesh

def get_iso_surf(res, **kwargs):
    
    if res.min() < 0:
        cmap = kwargs.pop("cmap", 'seismic')
        vmax = kwargs.pop("vmax", min(np.abs(res.max()), np.abs(res.min())) * 1.0)
        vmin = kwargs.pop("vmin", -vmax)
    else:
        cmap = kwargs.pop("cmap", 'jet')
        vmax = kwargs.pop("vmax", res.max() * 0.85)
        vmin = kwargs.pop("vmin", res.max() * 0.15)
    
    colormap = Colormap(mpl.colormaps[cmap], vmin, vmax)
    contours_number = kwargs.pop("contours_number", 4)
    contours = kwargs.pop("contours", np.linspace(vmin, vmax, contours_number))
    
    tri_verts, tri_faces, tri_norms, tri_color, iso_vals = ger_iso_meshs(res, contours, colormap)
    verts, faces, normals, colors = mesh_concatenate(tri_verts, tri_faces, tri_norms, tri_color)
    return Mesh(verts, faces, normals, colors, iso_vals)
