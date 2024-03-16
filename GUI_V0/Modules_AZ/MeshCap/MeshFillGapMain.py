import sys
import os
os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File
import QT_GUI

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
import pyvista as pv
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

class MeshFillGap:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui

        self.ui.ChooseStlBtn_MFG.clicked.connect(lambda: self.ChooseStlFile())
        self.ui.ChooseSaveFileBtn_MFG.clicked.connect(lambda: self.ChooseSaveStlFile())
        self.ui.VTKVisualize_Btn_MFG.clicked.connect(lambda: self.Visualize())
        self.ui.SaveBtn_MFG.clicked.connect(lambda: self.Save())
        self.ui.ChooseSaveFileBtnConnectivity_MFG.clicked.connect(lambda: self.ChooseSaveConnectivityStlFile())
        self.ui.SaveBtnConnectivity_MFG.clicked.connect(lambda: self.ConnectivityFilter())
        self.ui.pushButton_BatchTable_MFG.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_MFG.clicked.connect(lambda: self.batchrun())

        self.InitMeshFillGap()

    def InitMeshFillGap(self):
        self.style = None

    def ChooseStlFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Load Stl Path",
                                                 fileTypes="All files (*.*);; stl files(*.stl)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.StlPathTxt_MFG.setPlainText('{}'.format(filename))

    def ChooseSaveStlFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose Save Stl name and Path",
                                                 fileTypes="All files (*.*);; stl files(*.stl)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.SaveNameTxt_MFG.setPlainText('{}'.format(filename))

    def ChooseSaveConnectivityStlFile(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose Save Stl name and Path",
                                                 fileTypes="All files (*.*);; stl files(*.stl)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.SaveNameTxtConnectivity_MFG.setPlainText('{}'.format(filename))

    def Visualize(self,Batch = False):
        infail = self.ui.StlPathTxt_MFG.toPlainText()
        print('infail', infail)

        stlpv = pv.read(infail)
        edge = stlpv.extract_feature_edges(non_manifold_edges=False, feature_edges=False, manifold_edges=False)
        edgestrip = edge.strip()

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

        actor = {}
        edgecell = {}

        stlpoly = vtk.vtkAppendPolyData()
        stlpoly.AddInputData(stlpv)
        stlpoly.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(stlpoly.GetOutput())

        actor['cap_stl'] = vtk.vtkActor()
        actor['cap_stl'].SetMapper(mapper)
        actor['cap_stl'].GetProperty().SetOpacity(0.5)
        actor['cap_stl'].PickableOff()
        render.AddActor(actor['cap_stl'])

        for i in range(edgestrip.n_cells):
            edgecell['edge'+str(i)] = vtk.vtkPolyLine()
            edgecell['edge'+str(i)].DeepCopy(cleanedgestrippoly.GetOutput().GetCell(i))

            points = extract_points(source=edgecell['edge'+str(i)])
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

            actor['edge'+str(i)] = vtk.vtkActor()
            actor['edge'+str(i)].SetMapper(mapper)
            actor['edge'+str(i)].GetProperty().SetLineWidth(8)
            actor['edge'+str(i)].GetProperty().SetColor(0, 1, 0)

            render.AddActor(actor['edge'+str(i)])

        textactor = vtk.vtkTextActor()
        textactor.SetInput('Left button to rotate\nRight button to select and change color\n'
                           '\'f\' to fill gap, if fail, delete the gap, select revese and retry\n'
                           '\'d\' to delete select gap or last gap\n\'r\' to change reverse type')
        textactor.SetPosition2(20,40)
        textactor.GetTextProperty().SetColor(1, 1, 1)
        textactor.GetTextProperty().SetFontSize(16)
        textactor.GetTextProperty().SetFontFamilyToArial()
        render.AddActor(textactor)

        if self.modelui:
            ui = self.modelui
        elif self.ui:
            ui = self.ui
        else:
            ui = None
        if Batch:
            ui = None
        if ui:
            dock = QT_GUI.CreateDockWidget(parent=ui, name="FillGap", position='Right')
            frame = dock.GetFrame()
            layout = dock.GetLayout()
            vtkWidget = QVTKRenderWindowInteractor(frame)
            layout.addWidget(vtkWidget)
            frame.setLayout(layout)

            vtkWidget.GetRenderWindow().AddRenderer(render)
            render_window_interactor = vtkWidget.GetRenderWindow().GetInteractor()
        else:
            render_window = vtk.vtkRenderWindow()
            render_window.AddRenderer(render)
            render_window.SetSize(1000, 1000)
            render_window_interactor = vtk.vtkRenderWindowInteractor()
            render_window_interactor.SetRenderWindow(render_window)

        self.style = InteractorFillGap(actor, edgecell, render, self.ui)
        self.style.SetDefaultRenderer(render)
        render_window_interactor.SetInteractorStyle(self.style)

        render_window_interactor.Initialize()
        render_window_interactor.Start()

    def Save(self):
        outfail = self.ui.SaveNameTxt_MFG.toPlainText()
        print('outfail', outfail)

        actor = self.style.GetOutputData()
        combo = vtk.vtkAppendPolyData()
        for key in actor:
            if 'cap' in key:
                print('Save',key)
                combo.AddInputData(actor[key].GetMapper().GetInput())
        combo.Update()

        writerFinal = vtk.vtkSTLWriter()
        writerFinal.SetInputData(combo.GetOutput())
        writerFinal.SetFileName(self.ui.SaveNameTxt_MFG.toPlainText())
        writerFinal.Update()
        writerFinal.Write()

    def ConnectivityFilter(self):
        infail = self.ui.SaveNameTxt_MFG.toPlainText()
        outfail = self.ui.SaveNameTxtConnectivity_MFG.toPlainText()
        print('infail',infail)
        print('outfail',outfail)

        stlpv = pv.read(infail)
        stlpoly = vtk.vtkAppendPolyData()
        stlpoly.AddInputData(stlpv)
        stlpoly.Update()

        connectivity = vtk.vtkPolyDataConnectivityFilter()
        connectivity.SetExtractionModeToLargestRegion()
        connectivity.SetInputData(stlpoly.GetOutput())
        connectivity.Update()

        writerFinal = vtk.vtkSTLWriter()
        writerFinal.SetInputData(connectivity.GetOutput())
        writerFinal.SetFileName(outfail)
        writerFinal.Update()
        writerFinal.Write()

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_MFG.setPlainText('{}'.format(filename))

    def batchrun(self,CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_MFG.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):
            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            FillGap = False
            try:
                if info["MeshFillGap"]:
                    FillGap = info["MeshFillGap"]
            except:
                pass
            if FillGap:
                InputFloder = ''
                OutputFloder = ''
                ConnectivityFloder = ''
                Connectivity = False
                try:
                    if info["InputStl(MeshFillGap)"]:
                        InputFloder = info["InputStl(MeshFillGap)"]
                except:
                    pass
                try:
                    if info["OutputFolder(MeshFillGap)"]:
                        OutputFloder = info["OutputFolder(MeshFillGap)"]
                except:
                    pass
                try:
                    if isinstance(info["Connectivity(MeshFillGap)"], np.bool_):
                        Connectivity = info["Connectivity(MeshFillGap)"]
                except:
                    pass
                try:
                    if info["ConnectivityFloder(MeshFillGap)"]:
                        ConnectivityFloder = info["ConnectivityFloder(MeshFillGap)"]
                except:
                    pass
                print('MeshFillGap InputFloder=', InputFloder)
                print('MeshFillGap OutputFloder=', OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                self.ui.StlPathTxt_MFG.setPlainText('{}'.format(InputFloder))
                self.ui.SaveNameTxt_MFG.setPlainText('{}'.format(OutputFloder))
                self.ui.SaveNameTxtConnectivity_MFG.setPlainText('{}'.format(ConnectivityFloder))
                # Touched function
                self.Visualize('True')
                self.Save()
                if Connectivity:
                    self.ConnectivityFilter()

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

def stitch(edge1, edge2, reverse_bool1=False, reverse_bool2=True):
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
        points.SetPoint(n1 + i, p2)

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

class InteractorFillGap(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, actor, edgecell, render, ui = None):
        self.actor = actor
        self.edgecell = edgecell
        self.render = render
        self.ui = ui
        self.capactorid = []
        self.reverse = False

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
                if self.ui:
                    self.reverse = self.ui.checkBox_reverse_MFG.isChecked()
                stitching = stitch(self.edgecell[edge[0]],self.edgecell[edge[-1]],False,self.reverse)
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
                id = 'cap_' + str(edge[0]) + '_' + str(edge[-1])
                self.actor[id] = actor
                self.capactorid.append(id)

                self.render.AddActor(actor)

        if self.GetInteractor().GetKeyCode() == 'r':
            if self.ui:
                self.reverse = self.ui.checkBox_reverse_MFG.isChecked()
                if self.reverse:
                    self.ui.checkBox_reverse_MFG.setChecked(False)
                else:
                    self.ui.checkBox_reverse_MFG.setChecked(True)
                self.reverse = self.ui.checkBox_reverse_MFG.isChecked()
            else:
                if self.reverse:
                    self.reverse = False
                else:
                    self.reverse = True


        if self.GetInteractor().GetKeyCode() == 'd':
            deleteid = []
            for key in self.actor:
                color = self.actor[key].GetProperty().GetColor()
                if color == (0, 0, 1):
                    if 'cap' in key:
                        deleteid.append(key)
            if deleteid == []:
                if not self.capactorid == []:
                    deleteid.append(self.capactorid[-1])
            for id in deleteid:
                self.render.RemoveActor(self.actor[id])
                del self.actor[id]
                self.capactorid.remove(id)

        if self.GetInteractor().GetKeyCode() == 's':
            combo = vtk.vtkAppendPolyData()
            for key in self.actor:
                if 'cap' in key:
                    combo.AddInputData(self.actor[key].GetMapper().GetInput())
            combo.Update()

            writerFinal = vtk.vtkSTLWriter()
            writerFinal.SetFileTypeToBinary()
            writerFinal.SetInputData(combo.GetOutput())
            writerFinal.SetFileName(self.ui.SaveNameTxt_MFG.toPlainText())
            writerFinal.Update()
            writerFinal.Write()

    def RightButtonPressEvent(self, obj, event):
        if self.ui:
            select = self.ui.comboBox_select_MFG.currentText()
            edgewith = self.ui.doubleSpinBox_edgewith_MFG.value()

            print('select',select)
            print('edgewith',edgewith)
        else:
            select = 'edge'
            edgewith = 8
        if select == 'edge':
            for key in self.actor:
                if 'cap' in key:
                    self.actor[key].PickableOff()
                else:
                    self.actor[key].PickableOn()
                    self.actor[key].GetProperty().SetLineWidth(edgewith)
                if 'stl' in key:
                    self.actor[key].PickableOff()
        if select == 'cap':
            for key in self.actor:
                if 'cap' in key:
                    self.actor[key].PickableOn()
                else:
                    self.actor[key].PickableOff()
                    self.actor[key].GetProperty().SetLineWidth(edgewith)
                if 'stl' in key:
                    self.actor[key].PickableOff()

        clickPos = self.GetInteractor().GetEventPosition()
        prop = vtk.vtkPropPicker()
        prop.PickProp(clickPos[0], clickPos[1], self.GetDefaultRenderer())
        actor = prop.GetActor()
        if actor:
            if actor.GetProperty().GetColor() == (0, 0, 1):
                actor.GetProperty().SetColor(0, 1, 0)
            else:
                actor.GetProperty().SetColor(0, 0, 1)

    def GetOutputData(self):
        return self.actor

if __name__ == '__main__':
    # run()
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\MeshFillGap.ui")
    stats = MeshFillGap(UI=ui)
    stats.ui.show()
    app.exec_()