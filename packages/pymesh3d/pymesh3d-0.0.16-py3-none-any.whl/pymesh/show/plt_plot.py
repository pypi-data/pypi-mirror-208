import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def plt_trisurf(verts, faces, **kwargs):

    # Display resulting triangular mesh using Matplotlib. This can also be done
    # with mayavi (see skimage.measure.marching_cubes docstring).
    figsize = kwargs.pop("figsize", [4, 3])
    cmap = kwargs.pop("cmap", plt.cm.jet)
    
    fig = plt.figure(figsize = figsize)
    # Plot the surface.  The triangles in parameter space determine which x, y, z
    # points are connected by an edge.
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    surf = ax.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2], 
                    triangles = faces,
                    #color = color,
                    shade = True, antialiased = True, **kwargs)
    
    surf.set_cmap(cmap)
    
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
   
    return surf

def Poly3D(verts, faces, **kwargs):

    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], **kwargs)#, fc = color)
    #mesh.set_edgecolor('k')
    ax.add_collection3d(mesh)

    ax.set_xlabel("x-axis")
    ax.set_ylabel("y-axis")
    ax.set_zlabel("z-axis")

    ax.set_xlim(verts[:,0].min(), verts[:,0].max())  # a = 6 (times two for 2nd ellipsoid)
    ax.set_ylim(verts[:,1].min(), verts[:,1].max())  # b = 10
    ax.set_zlim(verts[:,2].min(), verts[:,2].max())  # c = 16
    
    return mesh