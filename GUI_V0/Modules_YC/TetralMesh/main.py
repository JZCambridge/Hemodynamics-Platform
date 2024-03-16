#!/usr/bin/env python3
'''
    File: main.py
    License: MIT
    Author: Aidan Kurtz, Sebastien Dery
    Created: 09/07/2016
    Python Version: 3.5
    ========================
    For now, this is the main script.
'''

import sys
import math
import numpy as np
import trimesh

from extraction import *
from machina import HexMachina
from optimization import *
from parametrization import *
from singularity import *
from utils import *

def main():

    print('Reading triangle mesh...', end=" ")
    sys.stdout.flush()
    #tri_mesh = trimesh.load_mesh('../data/bunny.stl')
    tri_mesh = trimesh.load_mesh(r'E:\B_Develop\tst\AllHexMesh\test\HexMc\data\coronary_face.stl')
    say_ok()

    # Instantiate tetrahedral mesh
    print('Generating tetrahedral mesh...', end=" ")
    sys.stdout.flush()
    machina = HexMachina(tri_mesh, max_vol = 2)
    # Output tetrahedral mesh
    vtk_tetmesh(machina.tet_mesh, 'tet_mesh')
    say_ok()

    # Construct boundary surface of tetrahedral mesh.
    print('Computing surface curvatures/normals...', end=" ")
    sys.stdout.flush()
    # Compute face and vertex normals.
    machina.surf_mesh.compute_normals()
    # Compute principal curvatures and directions.
    machina.surf_mesh.compute_curvatures()
    # Output curvature crossfield to .vtk file.
    vtk_curvature(machina.surf_mesh, 'curvature')
    say_ok()

    # Compute the tetrahedral one-rings of the mesh.
    print('Extracting dual voronoi...', end=" ")
    sys.stdout.flush()
    machina.compute_dual()
    say_ok()

    # Construct 3D frame field as an array of (U, V, W) frames.
    # This field is parallel to the tet list (i.e. each tet has a frame).
    print('Initializing framefield...', end=" ")
    sys.stdout.flush()
    # Construct frame field.
    machina.init_framefield()
    say_ok()

    # Optimize 3D frame field by L-BFGS minimization.
    print('Optimizing framefield...')
    machina.optimize_framefield()
    print("yang1")

    # Output frame field to .vtk file.
    vtk_framefield(machina.frames, 'field')
    print("yang2")

    # Determine the singular edges of the framefield.      
    print("Computing singular graph...", end=" ")
    sys.stdout.flush()
    print("yang3")
    singular_vertices = singular_graph(machina)[2]
    say_ok()

    print("Parametrizing volume...")
    uvw_map = parametrize_volume(machina, singular_vertices, 3.0)
    say_ok()

    print("Extracting hexahedrons...", end=" ")
    iso_pts = extract_isolines(machina, uvw_map)
    say_ok()

if __name__ == '__main__':
    main()



