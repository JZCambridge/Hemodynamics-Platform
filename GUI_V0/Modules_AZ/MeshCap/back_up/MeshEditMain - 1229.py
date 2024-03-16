# -*- coding: UTF-8 -*-
'''
@Project ：GUI
@File    ：MeshEditMain.py
@IDE     ：PyCharm
@Author  ：YangChen's Piggy
@Date    ：2021/12/26 21:26
'''
import os
import vtk
import numpy as np
from vtkmodules.vtkCommonCore import vtkIdList
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkIdList
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
    vtkStripper
)
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def extract_points(source, reverse_bool = False):
    """
            Dscription: extract points from cell

            Parameters
            ----------
            source: cell
                edge cell
            reverse_bool: bool
                whether reverse the points'order of the cell

            Examples
            --------
            #>>> extract_points(edge_cell, True)
            """
    # Travers the cells and add points while keeping their order.
    points = source.GetPoints()
    cells = source
    cells.GetPointIds().SetNumberOfIds(points.GetNumberOfPoints())
    idList = vtk.vtkIdList()
    pointIds = []
    for i in range(0, points.GetNumberOfPoints()):
        pId = i
        # Only add the point id if the previously added point does not
        # have the same id. Avoid p->p duplications which occur for example
        # if a poly-line is traversed. However, other types of point
        # duplication currently are not avoided: a->b->c->a->d
        if len(pointIds)==0 or pointIds[-1]!=pId:
            pointIds.append(pId)
    result = []
    for i in pointIds:
        if not reverse_bool:
            result.append(points.GetPoint(i))
        else:
            result.append(points.GetPoint(pointIds[len(pointIds)-1 - pointIds.index(i)] ))
    # print(len(result),result)
    return result

def reverse_lines(source):
    # # strip = vtk.vtkStripper()
    # # strip.SetInputData(source)
    # # strip.Update()
    # reversed = vtk.vtkReverseSense()
    # reversed.SetInputConnection(source)
    # reversed.Update()
    # return reversed.GetOutput()
    print("reversed", source)
    points2 = vtk.vtkPoints()
    points2.DeepCopy(source.GetPoints())

    # poly = vtk.vtkPolyData()
    # poly.SetPoints(source.GetPoints())
    # poly.SetPoints(source.Ge
    # # poly.Update()
    # # print("reverse_line",poly)
    strip = vtk.vtkStripper()
    strip.SetInputData(points2)
    strip.Update()
    reversed = vtk.vtkReverseSense()
    reversed.SetInputConnection(strip.GetOutputPort())
    reversed.Update()
    print("reversed", reversed.GetOutput())
    return reversed.GetOutput()
    # # reversed.SetInputConnection(source.GetOutputPort())
    # # print('source {}'.format(source))
    # print()
    #
    # poly = vtk.vtkPolyData()
    # poly.SetPoints(source.GetPoints())
    #
    # # print(source.GetPoints())
    # reversed.SetInputData(poly)
    # reversed.ReverseCellsOn()
    # # reversed.ReverseNormalsOn()
    # reversed.Update()
    # # print(source.GetPoints())
    # # print(reversed.GetOutput().GetPointData())
    # # print(reversed.GetOutput().GetPoints().GetData())
    #
    # # points1 = vtk.vtkPoints()
    # # points1.DeepCopy(reversed.GetOutput().GetPoints())
    # #
    # # for i in range(source.GetPoints().GetNumberOfPoints()):
    # #     # print(source.GetPoints().GetPoint(i))
    # #     print(points2.GetPoint(i))
    # #
    # #     # print(reversed.GetOutput().GetPoints().GetPoint(i))
    # #     # print(reversed.GetOutput().GetPoints())
    # #     print(points1.GetPoint(i))
    # #     # print(reversed.GetOutput().GetPoints().GetPoint(i))
    # #     print('\n')
    # #     # break
    # # # for i in range(reversed.GetOutput().GetPoints().GetNumberOfPoints()):
    # # #     print(reversed.GetOutput().GetPoints().GetPoint(i))
    # #     # break
    # # breakpoint()
    # return reversed.GetOutput()

def find_closest_point(points, samplePoint):
    points = np.asarray(points)
    assert(len(points.shape)==2 and points.shape[1]==3)
    nPoints = points.shape[0]
    diff = np.array(points) - np.tile(samplePoint, [nPoints, 1])
    pId = np.argmin(np.linalg.norm(diff, axis=1))
    return pId

def stitch(edge1, edge2, reverse_bool1 = False, reverse_bool2 = True):
    # Extract points along the edge line (in correct order).
    # The following further assumes that the polyline has the
    # same orientation (clockwise or counterclockwise).
    points1 = extract_points(edge1, reverse_bool1)
    points2 = extract_points(edge2, reverse_bool2)
    # points2 = points2.reverse()
    n1 = len(points1)
    n2 = len(points2)

    # Prepare result containers.
    # Variable points concatenates points1 and points2.
    # Note: all indices refer to this targert container!
    points = vtk.vtkPoints()
    cells = vtk.vtkCellArray()
    points.SetNumberOfPoints(n1+n2)
    for i, p1 in enumerate(points1):
        points.SetPoint(i, p1)
    for i, p2 in enumerate(points2):
        # points.SetPoint(i+n1, p2)
        points.SetPoint(n1 +i, p2)

    # The following code stitches the curves edge1 with (points1) and
    # edge2 (with points2) together based on a simple growing scheme.

    # Pick a first stitch between points1[0] and its closest neighbor
    # of points2.
    i1Start = 0
    i2Start = find_closest_point(points2, points1[i1Start])
    # i2Start += n1 # offset to reach the points2
    i2Start += n1 # offset to reach the points2

    # Initialize
    i1 = i1Start
    i2 = i2Start
    p1 = np.asarray(points.GetPoint(i1))
    p2 = np.asarray(points.GetPoint(i2))
    # mask = np.zeros(n1+n2, dtype=bool)
    mask = np.zeros(n1 + n2, dtype=bool)
    count = 0
    while not np.all(mask):
        count += 1
        i1Candidate = (i1+1)%n1
        i2Candidate = (i2+1-n1)%n2+n1
        p1Candidate = np.asarray(points.GetPoint(i1Candidate))
        p2Candidate = np.asarray(points.GetPoint(i2Candidate))
        diffEdge12C = np.linalg.norm(p1-p2Candidate)
        diffEdge21C = np.linalg.norm(p2-p1Candidate)

        mask[i1] = True
        mask[i2] = True
        if diffEdge12C < diffEdge21C:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0,i1)
            triangle.GetPointIds().SetId(1,i2)
            triangle.GetPointIds().SetId(2,i2Candidate)
            cells.InsertNextCell(triangle)
            i2 = i2Candidate
            p2 = p2Candidate
        else:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0,i1)
            triangle.GetPointIds().SetId(1,i2)
            triangle.GetPointIds().SetId(2,i1Candidate)
            cells.InsertNextCell(triangle)
            i1 = i1Candidate
            p1 = p1Candidate

    # Add the last triangle.
    i1Candidate = (i1+1)%n1
    i2Candidate = (i2+1-n1)%n2+n1
    if (i1Candidate <= i1Start) or (i2Candidate <= i2Start):
        if i1Candidate <= i1Start:
            iC = i1Candidate
        else:
            iC = i2Candidate
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0,i1)
        triangle.GetPointIds().SetId(1,i2)
        triangle.GetPointIds().SetId(2,iC)
        cells.InsertNextCell(triangle)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    poly.BuildLinks()

    return poly

def add_to_renderer(renderer, item, color, opacity=1., linewidth=None):
    colors = vtk.vtkNamedColors()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetScalarVisibility(False)
    if hasattr(item, 'GetOutputPort'):
        mapper.SetInputConnection(item.GetOutputPort())
    elif isinstance(item, vtk.vtkPolyData):
        mapper.SetInputData(item)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d(color))
    actor.GetProperty().SetOpacity(opacity)
    if linewidth:
        actor.GetProperty().SetLineWidth(linewidth)
    renderer.AddActor(actor)
    return mapper, actor

################################################################################
def run():
    # Retrieve the original stl file.
    reader = vtk.vtkSTLReader()
    reader.SetFileName(r"E:\tst\wallOnlyNoSmooth.stl")
    reader.Update()

    # Extract the boundary edge in a continuous order.
    fedges = vtk.vtkFeatureEdges()
    fedges.BoundaryEdgesOn()
    fedges.FeatureEdgesOff()
    fedges.ManifoldEdgesOff()
    fedges.SetInputData(reader.GetOutput())
    fedges.Update()
    # print(fedges.GetOutput().GetNumberOfCells(), fedges.GetOutput())

    Bstripper = vtk.vtkStripper()
    Bstripper.SetInputConnection(fedges.GetOutputPort())
    Bstripper.JoinContiguousSegmentsOn()
    Bstripper.Update()
    # print(Bstripper)

    # stripper_source = Bstripper.GetOutput()
    cleanPolyData = vtk.vtkCleanPolyData()
    cleanPolyData.SetInputConnection(Bstripper.GetOutputPort())
    cleanPolyData.Update()
    cleanPolyData.GetOutput().GetNumberOfCells()
    # print(Bstripper.GetOutput())

    source_edge1 = vtk.vtkPolyLine()
    source_edge1.DeepCopy(cleanPolyData.GetOutput().GetCell(2))

    tmpsource_edge2 = vtk.vtkPolyLine()
    tmpsource_edge2.DeepCopy(cleanPolyData.GetOutput().GetCell(3))

    # reversed = vtk.vtkReverseSense()
    # reversed.SetInputConnection(poly)
    # reversed.Update()
    # print("tst",source_edge1.GetPoints(), tmpsource_edge2.GetPoints())

    # Requirement: edge1 and edge2 must be oriented the same way!
    # source_edge2 = reverse_lines(tmpsource_edge2)

    # Perform the stitching.
    stitching = stitch(source_edge1, tmpsource_edge2, False, True)

    # Combine everything into one polydata object.
    combo = vtk.vtkAppendPolyData()
    combo.AddInputData(reader.GetOutput())
    combo.AddInputData(stitching)
    combo.AddInputData(fedges.GetOutput())
    combo.Update()

    writerFinal = vtk.vtkSTLWriter()
    writerFinal.SetFileTypeToBinary()
    writerFinal.SetInputData(combo.GetOutput())
    writerFinal.SetFileName(R"E:\tst\wallOnlyNoSmoothyes.stl")
    writerFinal.Update()
    writerFinal.Write()

    # Visualize.
    renderer = vtk.vtkRenderer()
    opacity=1.0
    add_to_renderer(renderer=renderer, item=stitching, color='blue', opacity=1.)
    add_to_renderer(renderer=renderer, item=fedges, color='red', opacity=1.)
    add_to_renderer(renderer=renderer, item=reader, color='white')

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName("Overlapping cylinders example")
    render_window.SetSize(1000,1000)
    renderer.SetBackground([0.5]*3)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    render_window.Render()
    render_window_interactor.Start()

if __name__ == '__main__':
    run()


######################



# import os
# import vtk
# import numpy as np
#
# def extract_points(source):
#     # Travers the cells and add points while keeping their order.
#     points = source.GetPoints()
#     print(len(points))
#     # cells = source.GetLines()
#     cells = source
#     cells.InitTraversal()
#     idList = vtk.vtkIdList()
#     pointIds = []
#     while cells.GetNextCell(idList):
#         for i in range(0, idList.GetNumberOfIds()):
#             pId = idList.GetId(i)
#             # Only add the point id if the previously added point does not
#             # have the same id. Avoid p->p duplications which occur for example
#             # if a poly-line is traversed. However, other types of point
#             # duplication currently are not avoided: a->b->c->a->d
#             if len(pointIds)==0 or pointIds[-1]!=pId:
#                 pointIds.append(pId)
#     result = []
#     for i in pointIds:
#         result.append(points.GetPoint(i))
#     return result
#
# def reverse_lines(source):
#     strip = vtk.vtkStripper()
#     strip.SetInputData(source)
#     strip.Update()
#     reversed = vtk.vtkReverseSense()
#     reversed.SetInputConnection(strip.GetOutputPort())
#     reversed.Update()
#     return reversed.GetOutput()
#
# def find_closest_point(points, samplePoint):
#     points = np.asarray(points)
#     assert(len(points.shape)==2 and points.shape[1]==3)
#     nPoints = points.shape[0]
#     diff = np.array(points) - np.tile(samplePoint, [nPoints, 1])
#     pId = np.argmin(np.linalg.norm(diff, axis=1))
#     return pId
#
# def stitch(edge1, edge2):
#     # Extract points along the edge line (in correct order).
#     # The following further assumes that the polyline has the
#     # same orientation (clockwise or counterclockwise).
#     points1 = extract_points(edge1)
#     points2 = extract_points(edge2)
#
#     # points1 = edge1.GetPoints()
#     # points2 =edge2.GetPoints()
#     n1 = len(points1)
#     n2 = len(points2)
#
#     # Prepare result containers.
#     # Variable points concatenates points1 and points2.
#     # Note: all indices refer to this targert container!
#     points = vtk.vtkPoints()
#     cells = vtk.vtkCellArray()
#     points.SetNumberOfPoints(n1+n2)
#     for i, p1 in enumerate(points1):
#         points.SetPoint(i, p1)
#     for i, p2 in enumerate(points2):
#         points.SetPoint(i+n1, p2)
#
#     # The following code stitches the curves edge1 with (points1) and
#     # edge2 (with points2) together based on a simple growing scheme.
#
#     # Pick a first stitch between points1[0] and its closest neighbor
#     # of points2.
#     i1Start = 0
#     i2Start = find_closest_point(points2, points1[i1Start])
#     i2Start += n1 # offset to reach the points2
#
#     # Initialize
#     i1 = i1Start
#     i2 = i2Start
#     p1 = np.asarray(points.GetPoint(i1))
#     p2 = np.asarray(points.GetPoint(i2))
#     mask = np.zeros(n1+n2, dtype=bool)
#     count = 0
#     while not np.all(mask):
#         count += 1
#         i1Candidate = (i1+1)%n1
#         i2Candidate = (i2+1-n1)%n2+n1
#         p1Candidate = np.asarray(points.GetPoint(i1Candidate))
#         p2Candidate = np.asarray(points.GetPoint(i2Candidate))
#         diffEdge12C = np.linalg.norm(p1-p2Candidate)
#         diffEdge21C = np.linalg.norm(p2-p1Candidate)
#
#         mask[i1] = True
#         mask[i2] = True
#         if diffEdge12C < diffEdge21C:
#             triangle = vtk.vtkTriangle()
#             triangle.GetPointIds().SetId(0,i1)
#             triangle.GetPointIds().SetId(1,i2)
#             triangle.GetPointIds().SetId(2,i2Candidate)
#             cells.InsertNextCell(triangle)
#             i2 = i2Candidate
#             p2 = p2Candidate
#         else:
#             triangle = vtk.vtkTriangle()
#             triangle.GetPointIds().SetId(0,i1)
#             triangle.GetPointIds().SetId(1,i2)
#             triangle.GetPointIds().SetId(2,i1Candidate)
#             cells.InsertNextCell(triangle)
#             i1 = i1Candidate
#             p1 = p1Candidate
#
#     # Add the last triangle.
#     i1Candidate = (i1+1)%n1
#     i2Candidate = (i2+1-n1)%n2+n1
#     if (i1Candidate <= i1Start) or (i2Candidate <= i2Start):
#         if i1Candidate <= i1Start:
#             iC = i1Candidate
#         else:
#             iC = i2Candidate
#         triangle = vtk.vtkTriangle()
#         triangle.GetPointIds().SetId(0,i1)
#         triangle.GetPointIds().SetId(1,i2)
#         triangle.GetPointIds().SetId(2,iC)
#         cells.InsertNextCell(triangle)
#
#     poly = vtk.vtkPolyData()
#     poly.SetPoints(points)
#     poly.SetPolys(cells)
#     poly.BuildLinks()
#
#     return poly
#
# def add_to_renderer(renderer, item, color, opacity=1., linewidth=None):
#     colors = vtk.vtkNamedColors()
#     mapper = vtk.vtkPolyDataMapper()
#     mapper.SetScalarVisibility(False)
#     if hasattr(item, 'GetOutputPort'):
#         mapper.SetInputConnection(item.GetOutputPort())
#     elif isinstance(item, vtk.vtkPolyData):
#         mapper.SetInputData(item)
#     actor = vtk.vtkActor()
#     actor.SetMapper(mapper)
#     actor.GetProperty().SetColor(colors.GetColor3d(color))
#     actor.GetProperty().SetOpacity(opacity)
#     if linewidth:
#         actor.GetProperty().SetLineWidth(linewidth)
#     renderer.AddActor(actor)
#     return mapper, actor
#
# ################################################################################
# def run():
#     # Retrieve the original stl file.
#     reader = vtk.vtkSTLReader()
#     reader.SetFileName(r"E:\tst\wallOnlyNoSmooth.stl")
#     reader.Update()
#
#     # Extract the boundary edge in a continuous order.
#     # edge1 = vtk.vtkFeatureEdges()
#     # edge1.SetInputData(reader.GetOutput())
#     # edge1.SetBoundaryEdges(1)
#     # edge1.SetFeatureEdges(0)
#     # edge1.SetNonManifoldEdges(0)
#     # edge1.SetManifoldEdges(0)
#     # edge1.Update()
#     # boundaryStrips = vtk.vtkStripper()
#     # boundaryStrips.SetInputConnection(edge1.GetOutputPort())
#     # boundaryStrips.Update()
#     # edge1 = boundaryStrips.GetOutput()
#     # edge2 = boundaryStrips.GetOutput()
#
#     fedges = vtk.vtkFeatureEdges()
#     fedges.SetInputData(reader.GetOutput())
#     fedges.SetBoundaryEdges(1)
#     fedges.SetFeatureEdges(0)
#     fedges.SetNonManifoldEdges(0)
#     fedges.SetManifoldEdges(0)
#     fedges.Update()
#     # print(fedges)
#
#     stripper = vtk.vtkStripper()
#     stripper.SetInputConnection(fedges.GetOutputPort())
#     stripper.JoinContiguousSegmentsOn()
#
#     cleanPolyData = vtk.vtkCleanPolyData()
#     cleanPolyData.SetInputConnection(stripper.GetOutputPort())
#     cleanPolyData.Update()
#
#     # print(cleanPolyData.GetOutput().GetCell(1).GetPoints())
#     # print(cleanPolyData.GetOutput().GetCell(1))
#     # print(cleanPolyData.GetOutput().GetCell(1).GetLines())
#     # print(cleanPolyData.GetOutput().GetCell(1).GetCellType())
#
#
#
#     # cells = vtk.vtkCell()
#     # cells.InsertNextCell(cleanPolyData.GetOutput().GetCell(1))
#     # cells.DeepCopy(cleanPolyData.GetOutput().GetCell(1))
#     # print(cells.GetOutput())
#
#     # polydata = vtk.vtkPolyData()
#     # polydata.SetLines(cells)
#     # # polydata.Update()
#     # # print(polydata)
#     #
#     # cells1 = vtk.vtkCellArray()
#     # cells1.InsertNextCell(cleanPolyData.GetOutput().GetCell(2))
#     # # print(cells.GetOutput())
#     #
#     # polydata1 = vtk.vtkPolyData()
#     # polydata1.SetLines(cells1)
#
#     mapper1 = vtk.vtkPolyDataMapper()
#     # mapper1.SetInputData(fedges.GetOutput())
#     # mapper1.SetInputData(stripper.GetOutput())
#     # mapper1.SetInputData(cleanPolyData.GetOutput())
#     mapper1.SetInputData(cleanPolyData.GetOutput())
#     actor1 = vtk.vtkActor()
#     actor1.SetMapper(mapper1)
#     actor1.GetProperty().SetColor(1,0,0)
#
#
#
#
#     # print(cleanPolyData.GetPoints())
#
#     # print(polydata1.GetPoints())
#     # print(polydata1.GetLines())
#
#     # print('point '+ str(polydata1.GetLines()))
#     # print(polydata1.GetLines().GetPoints())
#     # print(polydata1.GetCell(0).GetPoints())
#
#
#
#
#     # edge1 = fedges.GetOutput()
#     # edge2 = fedges.GetOutput()
#     #
#     edge1 = cleanPolyData.GetOutput().GetCell(1)
#     edge2 = cleanPolyData.GetOutput().GetCell(2)
#     # edge2 = cells1
#
#     # edge1 = polydata
#     # edge2 = polydata1
#
#     # print('here')
#
#     # Perform the stitching.
#     # Requirement: edge1 and edge2 must be oriented the same way!
#     #edge2 = reverse_lines(edge2)
#     stitching = stitch(edge1, edge2)
#
#     # Combine everything into one polydata object.
#     combo = vtk.vtkAppendPolyData()
#     combo.AddInputData(reader.GetOutput())
#     combo.AddInputData(stitching)
#     combo.Update()
#
#     writerFinal = vtk.vtkSTLWriter()
#     writerFinal.SetFileTypeToBinary()
#     writerFinal.SetInputData(combo.GetOutput())
#     writerFinal.SetFileName(r"E:\tst\fixed.stl")
#     writerFinal.Update()
#     writerFinal.Write()
#
#     # Visualize.
#     renderer = vtk.vtkRenderer()
#     opacity=1.0
#     add_to_renderer(renderer=renderer, item=stitching, color='blue', opacity=1.)
#     add_to_renderer(renderer=renderer, item=reader, color='white')
#
#
#     renderer.AddActor(actor1)
#     render_window = vtk.vtkRenderWindow()
#     render_window.AddRenderer(renderer)
#     render_window.SetWindowName("Overlapping cylinders example")
#     render_window.SetSize(1000,1000)
#     renderer.SetBackground([0.5]*3)
#     render_window_interactor = vtk.vtkRenderWindowInteractor()
#     render_window_interactor.SetRenderWindow(render_window)
#     render_window.Render()
#     render_window_interactor.Start()
#
# if __name__ == '__main__':
#     run()