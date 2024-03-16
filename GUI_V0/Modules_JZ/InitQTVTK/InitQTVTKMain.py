# -*- coding: utf-8 -*-
"""
#Ver. 0
#Must not be used without all authors' permissions
#Created by
Jin ZHENG JZ410 (29Mar21)
"""

##############################################################################
# Import functions from JZ410
import sys
import os

# Set current folder as working directory
# Get the current working directory: os.getcwd()
# Change the current working directory: os.chdir()
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Base')
# Import functions
import QT_GUI
##############################################################################

##############################################################################
# Standard library
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PySide2.QtCore import Qt


class InitQTVTK:
    def __init__(self, UI):
        # init
        self.ui = UI.ui

        self.ui.vtkWidgetInit = None
        self.ui.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.ui.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.ui.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.ui.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        # remove central widget!!
        self.ui.takeCentralWidget()

        # Disabled so no image show initially
        # self.ShowQTVTK()

    def ShowQTVTK(self):
        # set Qt VTK Widget
        self.SetQTVTKWidget()
        # VTK pipe line
        self.VTKPipeline()

    # def get_sources(self):
    #     sources = list()

    #     # Create a sphere
    #     sphere = vtk.vtkSphereSource()
    #     sphere.SetCenter(0.0, 0.0, 0.0)
    #     sphere.Update()
    #     sources.append(sphere)
    #     # Create a cone
    #     cone = vtk.vtkConeSource()
    #     cone.SetCenter(0.0, 0.0, 0.0)
    #     cone.SetDirection(0, 1, 0)
    #     cone.Update()
    #     sources.append(cone)
    #     # Create a cube
    #     cube = vtk.vtkCubeSource()
    #     cube.SetCenter(0.0, 0.0, 0.0)
    #     cube.Update()
    #     sources.append(cube)
    #     # Create a cylinder
    #     cylinder = vtk.vtkCylinderSource()
    #     cylinder.SetCenter(0.0, 0.0, 0.0)
    #     cylinder.Update()
    #     sources.append(cylinder)

    #     return sources

    # def SetQTVTKWidget(self):
    #     # add dock and get frame/layout
    #     dock = QT_GUI.CreateDockWidget(
    #         parent=self.ui,
    #         name="Initial Display",
    #         position='Right'
    #     )
    #     frame = dock.GetFrame()
    #     layout = dock.GetLayout()

    #     # VTK widget implementation
    #     self.ui.vtkWidgetInit = QVTKRenderWindowInteractor(frame)
    #     layout.addWidget(self.ui.vtkWidgetInit)

    #     # frame set layout
    #     frame.setLayout(layout)


    # def VTKPipeline(self):
    #     # colors
    #     colors = vtk.vtkNamedColors()
    #     ## set colors.
    #     ren_bkg = ['Black', 'Black', 'Black', 'Black']
    #     actor_color = ['White', 'Green', 'Red', 'Yellow']

    #     # Define viewport ranges.
    #     xmins = [0, .5, 0, .5]
    #     xmaxs = [0.5, 1, 0.5, 1]
    #     ymins = [0, 0, .5, .5]
    #     ymaxs = [0.5, 0.5, 1, 1]

    #     # actor sources
    #     sources = self.get_sources()

    #     # set all sources
    #     for i in range(4):
    #         # Create mapper and actor
    #         mapper = vtk.vtkPolyDataMapper()
    #         mapper.SetInputConnection(sources[i].GetOutputPort())

    #         # create actor
    #         actor = vtk.vtkActor()
    #         actor.GetProperty().SetColor(colors.GetColor3d(actor_color[i]))
    #         actor.SetMapper(mapper)

    #         # create renderer
    #         ren = vtk.vtkRenderer()

    #         # set renderer actor, background, , camera
    #         ren.AddActor(actor)
    #         ren.SetBackground(colors.GetColor3d(ren_bkg[i]))
    #         ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])
    #         ## Share the camera between viewports.
    #         if i == 0:
    #             camera = ren.GetActiveCamera()
    #             camera.Azimuth(30)
    #             camera.Elevation(30)
    #         else:
    #             ren.SetActiveCamera(camera)
    #         ren.ResetCamera()

    #         # render window add renderer
    #         self.ui.vtkWidgetInit.GetRenderWindow().AddRenderer(ren)

    #     # set interactor
    #     iren = self.ui.vtkWidgetInit.GetRenderWindow().GetInteractor()

    #     # initialise and show
    #     iren.Initialize()
    #     iren.Start()
    def get_sources(self):

        # file_name = "CFD_file_37.vtu"
        file_name = r"../Base/InitialDisplay/Coronary.stl"
        print(os. getcwd())
        # Read the source file.
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_name)
        reader.Update()  # Needed because of GetScalarRange
        sources = reader.GetOutput()

        return sources

    def SetQTVTKWidget(self):
        # add dock and get frame/layout
        dock = QT_GUI.CreateDockWidget(
            parent=self.ui,
            name="Initial Display",
            position='Right'
        )
        frame = dock.GetFrame()
        layout = dock.GetLayout()
        # window.addDockWidget(QtCore.Qt.RightDockWidgetArea, options_dock)

        # VTK widget implementation
        self.ui.vtkWidgetInit = QVTKRenderWindowInteractor(frame)
        layout.addWidget(self.ui.vtkWidgetInit)

        # frame set layout
        frame.setLayout(layout)

    def VTKPipeline(self):
        # colors
        colors = vtk.vtkNamedColors()

        ## set colors.
        ren_bkg = 'Black'
        actor_color = 'White'

        # Define viewport ranges.
        xmins = 0
        xmaxs = 1
        ymins = 0
        ymaxs = 1
        # actor sources
        sources = self.get_sources()

        # Create the mapper that corresponds the objects of the vtk.vtk file
        # into graphics elements
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(sources)

        # Create the Actor
        actor = vtk.vtkActor()
        actor.GetProperty().SetColor(colors.GetColor3d(actor_color))
        actor.SetMapper(mapper)

        # Create the Renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(colors.GetColor3d(ren_bkg))
        renderer.SetViewport(xmins, ymins, xmaxs, ymaxs)
        camera = renderer.GetActiveCamera()
        camera.Azimuth(30)
        camera.Elevation(30)
        renderer.ResetCamera()

        # render window add renderer
        self.ui.vtkWidgetInit.GetRenderWindow().AddRenderer(renderer)

        # set interactor
        interactor = self.ui.vtkWidgetInit.GetRenderWindow().GetInteractor()
        interactor.Initialize()
        interactor.Start()

