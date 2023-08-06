import trimesh
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt

def marching_cubes(res, iso_value, colormap):
    verts, faces, normals, values = measure.marching_cubes(res, iso_value, spacing = [1.0, 1.0, 1.0])

    pltmap = colormap.cmap
    vmax = colormap.vmax
    vmin = colormap.vmin

    xp = [vmin, vmax]
    fp = [0, 256]

    color = pltmap(int(np.interp(iso_value, xp, fp)))
    colors = np.asarray([color for _ in range(verts.shape[0])])

    return verts, faces, normals, colors

def ger_iso_meshs(res, iso_value_range, colormap):

    tri_verts = []
    tri_faces = []
    tri_norms = []
    tri_color = []

    iso_vals = np.zeros([0])

    for iso_value in iso_value_range:
        verts, faces, normals, colors = marching_cubes(res, iso_value, colormap)

        tri_verts.append(verts)
        tri_faces.append(faces)
        tri_norms.append(normals)
        tri_color.append(colors)

        #color.append(colors[0])
        iso_vals = np.hstack((iso_vals, np.ones_like(verts[:, 0]) * iso_value))
        
    return tri_verts, tri_faces, tri_norms, tri_color, np.asarray(iso_vals)

def mesh_concatenate(tri_verts, tri_faces, tri_norms, tri_color):
    v_old = np.zeros([0, 3])
    f_old = np.zeros([0, 3], dtype = "int")
    n_old = np.zeros([0, 3])
    c_old = np.zeros([0, 4], dtype = "int")

    for i, verts in enumerate(tri_verts):

        #matching
        f_new = np.array(tri_faces[i]) + np.shape(v_old)[0]
        v_old = np.concatenate((v_old,tri_verts[i]),axis=0)
        f_old = np.concatenate((f_old,f_new),axis=0)
        n_old = np.concatenate((n_old,tri_norms[i]),axis=0)
        c_old = np.concatenate((c_old,tri_color[i]),axis=0)
        
    return v_old, f_old, n_old, c_old