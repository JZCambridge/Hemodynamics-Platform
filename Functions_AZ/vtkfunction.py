import vtk
import random
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import QT_GUI
import Qtfunction
from PySide2.QtCore import Qt

class InteractorChangeActorName(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, ui, actor):
        self.ui = ui
        self.actor = actor
        self.LastPickedActor = vtk.vtkActor()
        self.branch = None

        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.keypressEvent)

    def keypressEvent(self, obj, event):
        if self.GetInteractor().GetKeyCode() == 'h':
            for key in self.actor:
                color=self.actor[key].GetProperty().GetColor()
                if not color==(1,1,1):
                    self.actor[key].VisibilityOff()

    def RightButtonPressEvent(self, obj, event):
        info = self.ui.spinBox_highlightcomp_SF.value()
        actor = self.actor.get(info,vtk.vtkActor())

        clickPos = self.GetInteractor().GetEventPosition()
        prop = vtk.vtkPropPicker()
        prop.PickProp(clickPos[0], clickPos[1], self.GetDefaultRenderer())
        pickactor = prop.GetActor()

        if pickactor:
            actor = pickactor

        if self.LastPickedActor!=actor:
            self.LastPickedActor.GetProperty().SetColor(1, 1, 1)
            self.LastPickedActor=actor
            self.LastPickedActor.GetProperty().SetColor(random.random(), random.random(),random.random())

        for key in self.actor:
            if self.actor[key]==actor:
                if self.branch!=key:
                    self.branch=key
                    cunt = 0
                    string = str(self.branch)
                    lineinfo = Qtfunction.chooselineinfo(self.ui.textEdit_inputcsv_SF)
                    Qtfunction.updatetableline(self.ui.tableWidget_SF,cunt, string, lineinfo)

def showface(OutputPath,InputDict,ui,modelui=None,BatchProcess='False'):
    ren = vtk.vtkRenderer()  # Create a renderer
    ren.GradientBackgroundOn()  # Set background color
    ren.SetBackground(.1, .1, .1)
    ren.SetBackground2(0.8, 0.8, 0.8)

    textactor = vtk.vtkTextActor()
    textactor.SetInput('Left button to rotate\nRight button to select and change color\n'
                       '\'f\' to hide the select face\n')
    textactor.SetPosition2(20, 40)
    textactor.GetTextProperty().SetColor(1, 1, 1)
    textactor.GetTextProperty().SetFontSize(16)
    textactor.GetTextProperty().SetFontFamilyToArial()
    ren.AddActor(textactor)

    global mesh
    actor = {}
    for key in InputDict:
        sphereSource = vtk.vtkSTLReader()
        sphereSource.SetFileName(OutputPath + '\\' + str(key) + '.stl')
        sphereSource.Update()

        mesh = sphereSource.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)  # maps polygonal data to graphics primitives

        # actor[key] = vtk.vtkLODActor()
        actor[key] = vtk.vtkActor()
        actor[key].SetMapper(mapper)
        actor[key].GetProperty().EdgeVisibilityOn()
        actor[key].GetProperty().SetLineWidth(0.3)
        actor[key].GetProperty().SetColor(1, 1, 1)

        ren.AddActor(actor[key])

    try:
        # BatchProcess = 'False'
        if BatchProcess == 'False':
            if modelui:
                dock = QT_GUI.CreateDockWidget(parent=modelui, name="Face", position='Right')
            else:
                dock = QT_GUI.CreateDockWidget(parent=ui, name="Face", position='Right')
            # dock.setWindowModality(Qt.ApplicationModal)
            frame = dock.GetFrame()
            layout = dock.GetLayout()
            vtkWidget = QVTKRenderWindowInteractor(frame)
            layout.addWidget(vtkWidget)
            frame.setLayout(layout)

            vtkWidget.GetRenderWindow().AddRenderer(ren)
            iren = vtkWidget.GetRenderWindow().GetInteractor()
        else:
            raise Exception

    except:
        renWin = vtk.vtkRenderWindow()  # Create a rendering window
        renWin.SetSize(1000, 1000)  # Set window size
        renWin.AddRenderer(ren)
        iren = vtk.vtkRenderWindowInteractor()  # Create a renderwindowinteractor
        iren.SetRenderWindow(renWin)

    style = InteractorChangeActorName(ui, actor)
    style.SetDefaultRenderer(ren)
    iren.SetInteractorStyle(style)

    iren.Initialize()  # Enable user interface interactor
    iren.Start()