# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：MeshDataTypeCovertMain.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/7/22 17:35 
'''
import meshio
#path = '/home/scarpma/Downloads/aorta46.msh'
#mesh = meshio.read(r'E:\A_Projects\meshtst\coronary_face.stl', file_format="stl")
# mesh = meshio.read(r'G:\Desktop\zhouao\CFD.inp', file_format="abaqus")
# meshio.write(r'G:\Desktop\zhouao\CFD.nas', mesh, file_format="nastran")

# mesh = meshio.read(r"E:\vmtk\coronary_uncapped1.msh",file_format='gmsh')
# meshio.write(r"E:\vmtk\coronary_uncapped1.inp", mesh, file_format="abaqus")

# mesh = meshio.read(r"E:\vmtk\convert\test.msh")
# meshio.write(r"E:\vmtk\convert\test1.nas", mesh)
# mesh = meshio.read(outfile, file_format="vtk-binary")

# mesh = meshio.read(r"E:\vmtk\coronary\RawData_ofextension05.vtu")
# meshio.write(r"E:\vmtk\coronary\RawData_ofextension05.nas", mesh, file_format="nastran")

# mesh = meshio.read(r"E:\paraview\tst\tiantan.nas")
# meshio.write(r"E:\paraview\tst\tiantan.vtu", mesh, file_format = "vtk-binary"
#              )
mesh = meshio.read(r"E:\paraview\tst\file_40.vtu",file_format = "vtu")
meshio.write(r"E:\paraview\tst\file_40.nas", mesh, file_format="nastran")