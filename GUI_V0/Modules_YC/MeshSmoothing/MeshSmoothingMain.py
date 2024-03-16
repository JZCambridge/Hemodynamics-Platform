# -*- coding: UTF-8 -*-
'''
@Project ：GUI 
@File    ：MeshSmoothingMain.py
@IDE     ：PyCharm 
@Author  ：YangChen's Piggy
@Date    ：2022/2/17 11:24 
'''
import vtk
# class smoothing:
#     def __init__(self):
#         self.Surface = None
#         self.NumberOfIterations =15
#         self.Method = 'laplace'
#
#     def stlReading(self):
#         readerSTL = vtk.vtkSTLReader()
#         readerSTL.SetFileName("E:\Test\stlSmoothing\Raw.stl")
#         # 'update' the reader i.e. read the .stl file
#         readerSTL.Update()
#         polydata = readerSTL.GetOutputPort()
#         # If there are no points in 'vtkPolyData' something went wrong
#         # if polydata.GetNumberOfPoints() == 0:
#         #     raise ValueError(
#         #         "No point data could be loaded from '" +
#         #         "E:\Test\stlSmoothing\Raw.stl")
#         self.Surface = polydata
#
#     def Execute(self):
#         if self.Surface == None:
#             self.PrintError('Error: No input surface.')
#         smoothingFilter = None
#         if self.Method is 'taubin':
#             smoothingFilter = vtk.vtkWindowedSincPolyDataFilter()
#             smoothingFilter.SetInput(self.Surface)
#             smoothingFilter.SetNumberOfIterations(self.NumberOfIterations)
#             smoothingFilter.SetPassBand(self.PassBand)
#             smoothingFilter.SetBoundarySmoothing(self.BoundarySmoothing)
#             ##            smoothingFilter.NormalizeCoordinatesOn()
#             smoothingFilter.Update()
#         elif self.Method is 'laplace':
#             smoothingFilter = vtk.vtkSmoothPolyDataFilter()
#
#             smoothingFilter.SetNumberOfIterations(self.NumberOfIterations)
#             # smoothingFilter.SetRelaxationFactor(self.RelaxationFactor)
#             smoothingFilter.SetInputConnection(self.Surface)
#             smoothingFilter.Update()
#             print("laplace")
#         else:
#             self.PrintError('Error: smoothing method not supported.')
#         # self.Surface = smoothingFilter.GetOutput()
#         # normals = vmtkscripts.vmtkSurfaceNormals()
#         # normals.Surface = self.Surface
#         # normals.Execute()
#         # self.Surface = normals.Surface
#         # if self.Surface.GetSource():
#         #     self.Surface.GetSource().UnRegisterAllOutputs()
# meshSmoothing = smoothing()
# meshSmoothing.stlReading()
# meshSmoothing.Execute()


##############################################################################

#
# ########################################################
# if state.smoothing:
#       if state.smoothingMethod == "Laplace":
#         smoothing = vtk.vtkSmoothPolyDataFilter()
#         smoothing.SetBoundarySmoothing(state.boundarySmoothing)
#         smoothing.SetNumberOfIterations(state.laplaceIterations)
#         smoothing.SetRelaxationFactor(state.laplaceRelaxation)
#         smoothing.SetInputConnection(surface)
#         surface = smoothing.GetOutputPort()
#       elif state.smoothingMethod == "Taubin":
#         smoothing = vtk.vtkWindowedSincPolyDataFilter()
#         smoothing.SetBoundarySmoothing(state.boundarySmoothing)
#         smoothing.SetNumberOfIterations(state.taubinIterations)
#         smoothing.SetPassBand(state.taubinPassBand)
#         smoothing.SetInputConnection(surface)
#         surface = smoothing.GetOutputPort()
#
#     if state.normals:
#       normals = vtk.vtkPolyDataNormals()
#       normals.AutoOrientNormalsOn()
#       normals.SetFlipNormals(state.flipNormals)
#       normals.SetSplitting(state.splitting)
#       normals.SetFeatureAngle(state.featureAngle)
#       normals.ConsistencyOn()
#       normals.SetInputConnection(surface)
#       surface = normals.GetOutputPort()
#
#     if state.cleaner:
#       cleaner = vtk.vtkCleanPolyData()
#       cleaner.SetInputConnection(surface)
#       surface = cleaner.GetOutputPort()
#
#     if state.connectivity:
#       connectivity = vtk.vtkPolyDataConnectivityFilter()
#       connectivity.SetExtractionModeToLargestRegion()
#       connectivity.SetInputConnection(surface)
#       surface = connectivity.GetOutputPort()
#
#     state.outputModelNode.SetPolyDataConnection(surface)
#     return True
#     #######################################################################

import vtk
#read file_one
stl1 = vtk.vtkSTLReader()
stl1.SetFileName("E:\Test\stlSmoothing\Cut.stl")
stl1.Update()

poly1 = stl1.GetOutput()

# Smooth the polyData
smoothFilter = vtk.vtkSmoothPolyDataFilter()
smoothFilter.SetNumberOfIterations(15)
smoothFilter.SetRelaxationFactor(0.5)
smoothFilter.FeatureEdgeSmoothingOff()
smoothFilter.BoundarySmoothingOn()
smoothFilter.SetInputData(poly1)
smoothFilter.Update()

# Remove Duplicate points/unused points/degenerate cells
cleanf1 = vtk.vtkCleanPolyData()
cleanf1.SetInputConnection(smoothFilter.GetOutputPort())
cleanf1.ConvertStripsToPolysOn()
cleanf1.ConvertPolysToLinesOn()
cleanf1.ConvertLinesToPointsOn()
cleanf1.Update()

# Conversion to Triangles
trif0 = vtk.vtkTriangleFilter()
trif0.SetInputConnection(cleanf1.GetOutputPort())
trif0.PassVertsOff()
trif0.PassLinesOff()
trif0.Update()

# Recompute Normals
normalf0 = vtk.vtkPolyDataNormals()
normalf0.SetInputConnection(trif0.GetOutputPort())
normalf0.ComputePointNormalsOn()
normalf0.ComputeCellNormalsOff()
normalf0.SplittingOff()
normalf0.ConsistencyOn()
normalf0.AutoOrientNormalsOff()
normalf0.Update()
stlWriter = vtk.vtkSTLWriter()
stlWriter.SetFileName("E:\Test\stlSmoothing\Rawsmoothed.stl")
stlWriter.SetInputConnection(normalf0.GetOutputPort())
stlWriter.Write()