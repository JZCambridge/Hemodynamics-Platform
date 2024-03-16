# -*- coding: UTF-8 -*-
'''
@Project ：main.py 
@File    ：MeshFormatsConvert.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2021/7/8 18:03 
'''
import meshio
mesh = meshio.read(r'E:\B_Develop\tst\AllHexMesh\test\HexMc\data\vtk\tet_mesh.vtk', file_format="vtk")
meshio.write(r'E:\B_Develop\tst\AllHexMesh\test\HexMc\data\vtk\coronary.nas', mesh, file_format="nastran")