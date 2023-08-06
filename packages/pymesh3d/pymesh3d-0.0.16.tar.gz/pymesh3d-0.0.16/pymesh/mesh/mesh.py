import numpy as np
import trimesh
from trimesh import Trimesh
from ..show import plt_trisurf, Poly3D

class Mesh(object):
    
    def __init__(self, verts, faces, normals, colors, iso_vals):
        
        self.iso_vals = iso_vals
        self.mesh = trimesh.Trimesh(vertices = verts, faces = faces,
                           vertex_normals = normals, vertex_colors = colors)
        
        trimesh.repair.fix_normals(self.mesh, multibody = True)

        self.verts = self.mesh.vertices
        self.faces = self.mesh.faces
        self.normals = self.mesh.vertex_normals
        self.colors = self.mesh.visual.vertex_colors
        return
    
    def load(filename, ext = "obj"):
        mesh = trimesh.load(f"{filename}.{ext}", ext)
        iso_vals = np.load(f"{filename}.npy")
        return Mesh(mesh.vertices, mesh.faces, mesh.vertex_normals, mesh.visual.vertex_colors, iso_vals)
    
    def export(self, filename, ext = "obj"):
        self.mesh.export(f"{filename}.{ext}", ext)
        np.save(f"{filename}.npy", self.iso_vals)
        return
    
    def plt_trisurf(self, **kwargs):
        verts, faces, iso_vals = self.verts, self.faces, self.iso_vals
        surf = plt_trisurf(verts, faces, array = iso_vals, **kwargs)
        return surf
    
    def Poly3D(self, **kwargs):
        verts, faces, iso_vals = self.verts, self.faces, self.iso_vals
        surf = Poly3D(verts, faces, array = iso_vals, **kwargs)
        return surf