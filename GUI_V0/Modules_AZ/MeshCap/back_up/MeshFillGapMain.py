import sys
import os
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File

import vtk
import numpy as np
import pyvista as pv

def extract_points(source, reverse_bool = False):
    points = source.GetPoints()
    cells = source
    cells.GetPointIds().SetNumberOfIds(points.GetNumberOfPoints())
    pointIds = []
    for i in range(0, points.GetNumberOfPoints()):
        pId = i
        if len(pointIds) == 0 or pointIds[-1] != pId:
            pointIds.append(pId)
    result = []
    for i in pointIds:
        if not reverse_bool:
            result.append(points.GetPoint(i))
        else:
            result.append(points.GetPoint(pointIds[len(pointIds) - 1 - pointIds.index(i)]))
    # print(len(result),result)
    return result

def find_closest_point(points, samplePoint):
    points = np.asarray(points)
    assert(len(points.shape)==2 and points.shape[1]==3)
    nPoints = points.shape[0]
    diff = np.array(points) - np.tile(samplePoint, [nPoints, 1])
    pId = np.argmin(np.linalg.norm(diff, axis=1))
    return pId

def stitch(edge1, edge2, reverse_bool1 = False, reverse_bool2 = True):
    points1 = extract_points(edge1, reverse_bool1)
    points2 = extract_points(edge2, reverse_bool2)

    n1 = len(points1)
    n2 = len(points2)
    points = vtk.vtkPoints()
    cells = vtk.vtkCellArray()
    points.SetNumberOfPoints(n1+n2)
    for i, p1 in enumerate(points1):
        points.SetPoint(i, p1)
    for i, p2 in enumerate(points2):
        # points.SetPoint(i+n1, p2)
        points.SetPoint(n1 +i, p2)

    i1Start = 0
    i2Start = find_closest_point(points2, points1[i1Start])
    i2Start += n1  # offset to reach the points2

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
        i1Candidate = (i1 + 1) % n1
        i2Candidate = (i2 + 1 - n1) % n2 + n1
        p1Candidate = np.asarray(points.GetPoint(i1Candidate))
        p2Candidate = np.asarray(points.GetPoint(i2Candidate))
        diffEdge12C = np.linalg.norm(p1 - p2Candidate)
        diffEdge21C = np.linalg.norm(p2 - p1Candidate)

        mask[i1] = True
        mask[i2] = True
        if diffEdge12C < diffEdge21C:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, i1)
            triangle.GetPointIds().SetId(1, i2)
            triangle.GetPointIds().SetId(2, i2Candidate)
            cells.InsertNextCell(triangle)
            i2 = i2Candidate
            p2 = p2Candidate
        else:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, i1)
            triangle.GetPointIds().SetId(1, i2)
            triangle.GetPointIds().SetId(2, i1Candidate)
            cells.InsertNextCell(triangle)
            i1 = i1Candidate
            p1 = p1Candidate

    # Add the last triangle.
    i1Candidate = (i1 + 1) % n1
    i2Candidate = (i2 + 1 - n1) % n2 + n1
    if (i1Candidate <= i1Start) or (i2Candidate <= i2Start):
        if i1Candidate <= i1Start:
            iC = i1Candidate
        else:
            iC = i2Candidate
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, i1)
        triangle.GetPointIds().SetId(1, i2)
        triangle.GetPointIds().SetId(2, iC)
        cells.InsertNextCell(triangle)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    poly.BuildLinks()

    return poly

def run():
    # stlpv = pv.read(r"E:\Coronary\b7_junzong\49-6000010357-1\solidtest\WallMesh\6Cap\wallOnlyNoSmooth.stl")
    stlpv = pv.read(r"E:\Coronary\b7_junzong\49-6000010357-1\solidtest\WallMesh\5Remesh\Remesh2.stl")
    edge = stlpv.extract_feature_edges(non_manifold_edges=False, feature_edges=False, manifold_edges=False)
    edgestrip = edge.strip()

    stlpoly = vtk.vtkAppendPolyData()
    stlpoly.AddInputData(stlpv)
    stlpoly.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(stlpoly.GetOutput())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(0.5)
    actor.PickableOff()
    actorstl = actor

    edgestrippoly = vtk.vtkAppendPolyData()
    edgestrippoly.AddInputData(edgestrip)
    edgestrippoly.Update()

    cleanedgestrippoly = vtk.vtkCleanPolyData()
    cleanedgestrippoly.SetInputConnection(edgestrippoly.GetOutputPort())
    cleanedgestrippoly.Update()

    render = vtk.vtkRenderer()  # Create a renderer
    render.GradientBackgroundOn()  # Set background color
    render.SetBackground(.1, .1, .1)
    render.SetBackground2(0.8, 0.8, 0.8)
    render.AddActor(actor)

    edgecell = {}
    actor = {}
    actor['stl'] = actorstl
    for i in range(edgestrip.n_cells):
        print(i)
        edgecell[i] = vtk.vtkPolyLine()
        edgecell[i].DeepCopy(cleanedgestrippoly.GetOutput().GetCell(i))

        points = extract_points(edgecell[i])
        pointsVTK = vtk.vtkPoints()
        pointsVTK.SetNumberOfPoints(len(points))

        polyLine = vtk.vtkPolyLine()
        polyLine.GetPointIds().SetNumberOfIds(len(points))

        for j in range(len(points)):
            pointsVTK.SetPoint(j, points[j])
            polyLine.GetPointIds().SetId(j, j)

        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polyLine)

        poly = vtk.vtkPolyData()
        poly.SetPoints(pointsVTK)
        poly.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)

        actor[i] = vtk.vtkActor()
        actor[i].SetMapper(mapper)
        actor[i].GetProperty().SetLineWidth(10.6)
        actor[i].GetProperty().SetColor(0,1,0)

        render.AddActor(actor[i])

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(render)
    render_window.SetWindowName("Overlapping cylinders example")
    render_window.SetSize(1000, 1000)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    style = InteractorFillGap(actor, edgecell, render)
    style.SetDefaultRenderer(render)
    render_window_interactor.SetInteractorStyle(style)

    render_window_interactor.Initialize()
    render_window_interactor.Start()

class InteractorFillGap(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, actor, edgecell, render):
        self.actor = actor
        self.edgecell = edgecell
        self.render = render

        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.keypressEvent)

    def keypressEvent(self, obj, event):
        if self.GetInteractor().GetKeyCode() == 'f':
            edge = []
            stitching = None
            for key in self.actor:
                color = self.actor[key].GetProperty().GetColor()
                if color == (0, 0, 1):
                    self.actor[key].GetProperty().SetColor(0, 1, 0)
                    edge.append(key)
            print(edge)
            if len(edge)==1:
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetTolerance(0.001)
                delaunay.SetAlpha(18)
                delaunay.SetInputData(self.actor[edge[0]].GetMapper().GetInput())
                delaunay.Update()

                stitching = delaunay.GetOutput()
            elif len(edge)==2:
                stitching = stitch(self.edgecell[edge[0]], self.edgecell[edge[-1]], False, False)
            else:
                print('Please check the Number of select edges')

            if stitching:
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(stitching)

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetOpacity(1)
                actor.GetProperty().SetColor(0, 1, 1)
                actor.PickableOff()
                self.actor['cap'+str(edge[0])+str(edge[-1])] = actor

                self.render.AddActor(actor)

        if self.GetInteractor().GetKeyCode() == 's':
            combo = vtk.vtkAppendPolyData()
            for key in self.actor:
                combo.AddInputData(self.actor[key].GetMapper().GetInput())
            combo.Update()

            writerFinal = vtk.vtkSTLWriter()
            writerFinal.SetFileTypeToBinary()
            writerFinal.SetInputData(combo.GetOutput())
            writerFinal.SetFileName(r"E:\Coronary\b7_junzong\49-6000010357-1\solidtest\WallMesh\6Cap\00000000000000000000.stl")
            writerFinal.Update()
            writerFinal.Write()

    def RightButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        prop = vtk.vtkPropPicker()
        prop.PickProp(clickPos[0], clickPos[1], self.GetDefaultRenderer())
        actor = prop.GetActor()
        if actor:
            if actor.GetProperty().GetColor() == (0, 1, 0):
                actor.GetProperty().SetColor(0, 0, 1)
            else:
                actor.GetProperty().SetColor(0, 1, 0)

if __name__ == '__main__':
    run()