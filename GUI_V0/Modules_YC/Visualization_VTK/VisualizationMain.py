# -*- coding: UTF-8 -*-
'''
@Project ：getpyfilepath.py
@File    ：VisualizationMain.py
@IDE     ：PyCharm
@Author  ：YangChen's Piggy
@Date    ：2022/3/21 15:34
'''
# -*- coding: utf-8 -*-
##############################################################################
import sys
import os
# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
# Import functions

import QT_GUI
from PySide2 import QtWidgets
import vtk
from vtk.util.misc import vtkGetDataRoot
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PySide2.QtCore import Qt
import numpy as np

import pyvista as pv
from pyvistaqt import QtInteractor,BackgroundPlotter


import pyvista as pv

# sphere = pv.Sphere()
# plotter = pv.Plotter(notebook=False)
# plotter.add_mesh(sphere)
# picked = []
# def overlay(selection):
#     picked.append(selection)
#     print(len(picked))
#     for sub_selection in picked:
#         plotter.add_mesh(sub_selection,  color='lightblue')
#     return
#
# plotter.enable_cell_picking(mesh=sphere, show=False,
#                      callback=overlay)
# # plotter.enable_cell_picking(through=False)
# plotter.show()


import matplotlib.pyplot as plt
import numpy as np

import pyvista as pv
from pyvista import examples

#
# model = examples.load_channels()
# def path(y):
#     """Equation: x = a(y-h)^2 + k"""
#     a = 110.0 / 160.0**2
#     x = a * y**2 + 0.0
#     return x, y
#
#
# x, y = path(np.arange(model.bounds[2], model.bounds[3], 15.0))
# zo = np.linspace(9.0, 11.0, num=len(y))
# points = np.c_[x, y, zo]
# spline = pv.Spline(points, 15)
# slc = model.slice_along_line(spline)
# p = pv.Plotter()
# p.add_mesh(slc, cmap="jet")
# p.add_mesh(model.outline())
# p.show(cpos=[1, -1, 1])

class Visualization_Pyvista:
    def __init__(self, UI):
        # init
        self.UI = UI
        self.ui = UI.ui
        self.ui.vtkWidgetInit = None
        # remove central widget!
        self.ui.takeCentralWidget()
        self.RenderingMethod = "All"
        self.SetQTVTKWidget()
        self.add_sources()
        self.picked = []
        self.pyvShow()

        # self.point_slected()

    def SetQTVTKWidget(self):
        # add dock and get frame/layout
        dock = QT_GUI.CreateDockWidget(
            parent=self.ui,
            name="Initial Display",
            position='Right'
        )
        frame = dock.GetFrame()
        layout = dock.GetLayout()

        # VTK widget implementation
        self.ui.vtkWidgetInit = QtInteractor(frame)
        self.Plotter = self.ui.vtkWidgetInit
        layout.addWidget(self.Plotter)

        # frame set layout
        frame.setLayout(layout)

        # # simple menu to demo functions
        # mainMenu = self.menuBar()
        # fileMenu = mainMenu.addMenu('File')
        # exitButton = QtWidgets.QAction('Exit', self)
        # exitButton.setShortcut('Ctrl+Q')
        # exitButton.triggered.connect(self.close)
        # fileMenu.addAction(exitButton)
        #
        # # allow adding a sphere
        # meshMenu = mainMenu.addMenu('Mesh')
        # self.add_sphere_action = QtWidgets.QAction('Add Sphere', self)
        # self.add_sphere_action.triggered.connect(self.add_sphere)
        # meshMenu.addAction(self.add_sphere_action)

    def add_sources(self):
        """ add a sphere to the pyqt frame """
        vtupath = os.path.join(os.getcwd(), "../Base/example/CFD_file_37.vtu")
        self.mesh = pv.read(vtupath)

        # mesh.plot(scalars='MAX_SHEAR_STRESS', cmap='jet')

        # mesh = pv.read(vtupath)
        # # 显示
        # mesh.plot(scalars='MAX_SHEAR_STRESS', cmap='jet')

    def pyvShow(self):
        def overlay(selection):
            self.picked.append(selection)
            print(len(self.picked))
            for sub_selection in self.picked:
                self.Plotter.add_mesh(sub_selection,
                                      scalars='MAX_SHEAR_STRESS',
                                      cmap='jet',
                                      style='surface')

        if self.RenderingMethod == "All":
            # all mesh
            temp_mensh = pv.read(r"E:\pyvistaTst\CFD_file.vtu")
            # self.mesh = temp_mensh.extract_surface().triangulate()
            self.mesh = temp_mensh.extract_surface().triangulate()
            self.surface = pv.read(r"E:\pyvistaTst\pRCAd1Stl.stl")
            # self.Plotter.add_mesh(self.surface, color='w', label='Surface', opacity=0.75)
            clipped = temp_mensh.clip_surface(self.surface, invert=True)
            self.Plotter.add_mesh(
                clipped,
                scalars="MAX_SHEAR_STRESS",

                cmap="jet",
            )

            # pyvista.Sphere()
            # sphere_b = pyvista.Sphere(center=(0.5, 0, 0))
            # self.mesh = pv.read(r"E:\pyvistaTst\pRCAd1Stl.stl")
            # self.branch = pv.read(r"E:\pyvistaTst\pRCAd1Stl.stl")
            # self.mesh = pv.Sphere()
            # self.branch = pv.Sphere(center=(0.5, 0, 0))
            # self.branch = pv.read(r"E:\pyvistaTst\pRCAd1Stl.stl")
            # result = self.mesh.boolean_difference(self.branch)
            # self.Plotter.add_mesh(result
            #                         )


        elif self.RenderingMethod == "Box":
            # box widget clip
            self.Plotter.add_mesh_clip_box(self.mesh,
                                           scalars='MAX_SHEAR_STRESS',
                                           cmap='jet',
                                           style='surface')
        elif self.RenderingMethod == "Pv_Slice":
            # plane widget clip
            self.Plotter.add_mesh_slice(self.mesh,
                                           scalars='MAX_SHEAR_STRESS',
                                           cmap='jet',
                                           style='surface')
        elif self.RenderingMethod == "Plane":
            # plane widget clip
            self.Plotter.add_mesh_clip_plane(self.mesh,
                                           scalars='MAX_SHEAR_STRESS',
                                           cmap='jet',
                                           style='surface')
        elif self.RenderingMethod == "CellPicking":
            self.Plotter.add_mesh(self.mesh, style='surface')

            self.Plotter.enable_cell_picking(mesh=self.mesh, show=False,
                                        callback=overlay)

##################################
# import pyvista as pv
# import numpy as np
# import vtk
# from pyvista import examples
#
# pv.set_plot_theme("document")
#
# camera = pv.Camera()
# bunny = pv.read(r"\\TENOKE-JSA061\e\Coronary\a7paperCT847447\Reviewer27Apr22\pic\mesh1.stl")
#
# pl = pv.Plotter()
# pl.background_color = 'w'
# pl.enable_anti_aliasing()
# pl.add_mesh(bunny, color='white', show_edges=True)
# # pl.add_text("Camera Position")
#
# pl.window_size = [800, 800]
# pl.camera.position = (103.78771209716797, 103.67298889160156, 147.4187600697767)
# pl.camera.focal_point = (103.78771209716797, 103.67298889160156, 115.83499145507812)
# pl.camera.up = (0.0, 1.0, 0.0)
# pl.camera.view_angle = 30
#
# # pl.camera = camera
# # pl.show()
# pl.show(screenshot='E:/airplane.png')