def iso_surface(mesh, **kwargs):
    from mayavi import mlab
    mlab_mesh = mlab.triangular_mesh(mesh.verts[:, 0], mesh.verts[:, 1], mesh.verts[:, 2], 
                                    mesh.faces, scalars = mesh.iso_vals, **kwargs)
    return mlab_mesh
    