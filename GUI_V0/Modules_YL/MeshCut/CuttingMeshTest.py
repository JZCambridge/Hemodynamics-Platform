import sys
import os
import time

os.chdir(os.getcwd())
sys.path.insert(0, '../Functions_JZ')
sys.path.insert(0, '../Functions_AZ')
# Import functions
import pdfunction
import Save_Load_File

import vtk
import numpy as np
from Modules_YL.MeshCut import GeoTransform
# import GeoTransform
import copy
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *

class Interaction:
    def __init__(self,UI = None,Hedys = None):
        self.ui = None
        if UI:
            self.ui = UI
        self.modelui = None
        if Hedys:
            self.modelui = Hedys.ui
        
        self.ui.ChooseStlBtn_MC.clicked.connect(lambda: self.ChooseStlFile())
        self.ui.CuttingMethod_YL.buttonClicked.connect(lambda: self.SetCuttingMethod())
        self.ui.VTKVisualize_Btn_MC.clicked.connect(lambda: self.Excute())
        self.ui.CuttingDirectionGrp_YL.buttonClicked.connect(lambda: self.SetDirection())
        self.ui.CuttingBoxVisibilityCheck.clicked.connect(lambda: self.SetVisibility())
        self.ui.ResetSizeBtn_MC.clicked.connect(lambda: self.SetBoxSize())
        self.ui.ChooseSaveFileBtn_MC.clicked.connect(lambda: self.ChooseSaveStlFile())
        self.ui.SaveBtn_MC.clicked.connect(lambda: self.Save())
        self.ui.CappingBtn_MC.clicked.connect(lambda: self.Capping())
        self.ui.pushButton_BatchTable_MC.clicked.connect(lambda: self.batchcsv())
        self.ui.pushButton_BatchRun_MC.clicked.connect(lambda: self.batchrun())
        
        self.InitCuttingMesh()

    def InitCuttingMesh(self):
        self.stlPath = self.ui.StlPathTxt_MC.toPlainText()
        self.methodFlag = 'Plane'
        self.visFlag = False
        self.dirFlag = 'Forward'
        self.saveFileName = ''

        self.geo = GeoTransform.GeoTrans()
        self.style = None
        self.mapper = None
        self.actor = None
        self.renderer = None
        self.renderWindow = None
        self.iren = None
        self.CappingFlag = False
        self.extrude = None
        self.reader = None

    # used to select specific stl file using UI
    def ChooseStlFile(self):
        self.stlPath = Save_Load_File.OpenFilePathQt(
            dispMsg='Load Stl Path',
            fileTypes='All files (*.*);; stl files(*.stl)',
            fileObj=self.ui,
            qtObj=True

        )

        self.ui.StlPathTxt_MC.setText(self.stlPath)

    # use UI to select the saving name and path of generated stl file
    def ChooseSaveStlFile(self):
        self.saveFileName = Save_Load_File.SaveFilePathQT(
            dispMsg='Choose Save Stl name and Path',
            fileTypes='All files (*.*);; stl files(*.stl)',
            fileObj=self.ui,
            qtObj=True
        )

        self.ui.SaveNameTxt_MC_4.setText(self.saveFileName)

    # used to pass the direction from UI to vtk window
    def SetDirection(self):
        dirInfo = self.ui.CuttingDirectionGrp_YL.checkedButton().text()

        if dirInfo == 'Forward':
            self.dirFlag = 'Forward'
        else:
            self.dirFlag = 'Backward'

        print(self.dirFlag)
        self.style.SetDirection(self.dirFlag)

    # pass the cutting method to interactor style
    def SetCuttingMethod(self):
        buttonInfo = self.ui.CuttingMethod_YL.checkedButton().text()
        # print(buttonInfo)
        if buttonInfo == "Plane Method":
            self.methodFlag = 'Plane'
        else:
            self.methodFlag = 'Circle'
        print(self.methodFlag)
        self.style.SetMethod(self.methodFlag)

    # used to set the visibility of cutting box
    def SetVisibility(self):
        if not self.visFlag:
            self.visFlag = True
        else:
            self.visFlag = False
        print(self.visFlag)
        self.style.SetVisibilty(self.visFlag)

    #　used to set the size of cutting box
    def SetBoxSize(self):
        # length = self.ui.LengthTxt_MC_1.text()
        # width = self.ui.WidthTxt_MC_1.text()
        # height = self.ui.HeightTxt_MC_1.text()

        ExtRadius = self.ui.RadiusSetTxt_MC.text()
        height = self.ui.HeightSetTxt_MC.text()

        self.style.SetBoxSize(ExtRadius, height)



    # get the stl name and path from UI, then excute the saving function
    def Save(self):
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(self.ui.SaveNameTxt_MC_4.toPlainText())
        if self.CappingFlag:
            writer.SetInputData(self.CurrentMesh.GetOutput())
        else:
            writer.SetInputData(self.style.GetOutputData())
        writer.Write()
        print("Successfully saved")

    # this function is used to fill holes of mesh
    def Capping(self):
        if self.style.GetCurrentMesh():
            tmpFile = self.style.GetCurrentMesh()
        else:
            tmpFile = self.CurrentMesh
        self.extrude = vtk.vtkFillHolesFilter()
        self.extrude.SetInputData(tmpFile)
        self.extrude.SetHoleSize(1000)
        self.extrude.Update()


        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(self.extrude.GetOutputPort())
        normals.ConsistencyOn()
        normals.SplittingOff()
        normals.Update()
        normals.GetOutput().GetPointData().SetNormals(self.reader.GetOutput().GetPointData().GetNormals())


        # self.CurrentMesh = self.extrude
        self.CurrentMesh = normals
        # self.mapper.SetInputConnection(self.extrude.GetOutputPort())
        self.mapper.SetInputData(self.CurrentMesh.GetOutput())
        self.mapper.Update()
        self.renderWindow.Render()  # update pipeline

        print('Capping Done')
        self.CappingFlag = True

    # the entrance of main function, used to specify interactor style and color properties
    def Excute(self):
        # specify input source
        self.stlPath = self.ui.StlPathTxt_MC.toPlainText()
        source = self.read_data(self.stlPath)

        self.CurrentMesh = source

        surface = source.GetOutput()
        # Initialize color
        color = vtk.vtkNamedColors()

        # input mesh and output triangle mesh
        triangleFilter = vtk.vtkTriangleFilter()
        triangleFilter.SetInputData(surface)
        triangleFilter.Update()
        surface = triangleFilter.GetOutput()

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(surface)
        self.mapper.ScalarVisibilityOn()

        # Set Actor property and enable model edge
        self.actor = vtk.vtkActor()
        # self.actor.GetProperty().SetOpacity(0.5)
        self.actor.GetProperty().SetColor(color.GetColor3d("Tomato"))
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().EdgeVisibilityOn()
        self.actor.GetProperty().SetLineWidth(0.2)

        textactor = vtk.vtkTextActor()
        textactor.SetInput('Left button to rotate\nRight button to select point\n'
                           '\'g\' to get box or plane\n\'c\' to cut model\n'
                           '\'Ctrl+z\' to return previous')
        textactor.SetPosition2(20, 40)
        textactor.GetTextProperty().SetColor(1, 0, 0)
        textactor.GetTextProperty().SetFontSize(16)
        textactor.GetTextProperty().SetFontFamilyToArial()


        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(textactor)
        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(color.GetColor3d('Silver'))

        # Set specific Interactor style and pass the UI object to interactor style
        self.style = MyCellPickerInteractor(source=source,
                                            mapper=self.mapper,
                                            funcGeo=self.geo,
                                            UI=self.ui
                                            )

        self.style.SetDefaultRenderer(self.renderer)

        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)

        self.iren = vtk.vtkRenderWindowInteractor()

        self.iren.SetRenderWindow(self.renderWindow)
        # 　set cellpicker for RenderwindowInteractor
        cell_picker = vtk.vtkCellPicker()
        self.iren.SetPicker(cell_picker)

        self.iren.SetInteractorStyle(self.style)

        self.iren.Initialize()

        self.renderWindow.Render()

        self.iren.Start()

    # For reading stl file purpose
    def read_data(self, filename):
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(filename)
        self.reader.Update()
        return self.reader

    def batchcsv(self):
        # choose
        filename = Save_Load_File.OpenFilePathQt(dispMsg="Choose csv file",
                                                 fileTypes="All files (*.*);; CSV files(*.csv)",
                                                 fileObj=self.ui, qtObj=True)
        # set filename
        self.ui.plainTextEdit_BatchTable_MC.setPlainText('{}'.format(filename))

    def batchrun(self, CSVPath=None):
        if CSVPath:
            inpath = CSVPath
        else:
            inpath = self.ui.plainTextEdit_BatchTable_MC.toPlainText()
        DF = pdfunction.readexcel(inpath)
        for i in range(len(DF)):

            # get line of table
            print('get info in line', i)
            info = DF.iloc[i].fillna('')

            MeshCut = False

            try:
                if info["MeshCut"]:
                    MeshCut = info["MeshCut"]
            except:
                pass

            if MeshCut:
                InputFloder = ''
                OutputFloder = ''
                Capping = ''

                try:
                    if info["InputFolder"]:
                        InputFloder = info["InputFolder"]
                except:
                    pass
                try:
                    if info["InputStl(MeshCut)"]:
                        InputFloder = info["InputStl(MeshCut)"]
                except:
                    pass
                try:
                    if info["OutputFolder"]:
                        OutputFloder = info["OutputFolder"] + '/MeshCut'
                except:
                    pass
                try:
                    if info["OutputFolder(MeshCut)"]:
                        OutputFloder = info["OutputFolder(MeshCut)"]
                except:
                    pass
                try:
                    if isinstance(info["Capping(MeshCut)"], np.bool_):
                        Capping = info["Capping(MeshCut)"]
                except:
                    pass
                # make dir
                if not os.path.exists(OutputFloder):
                    os.mkdir(OutputFloder)
                # change tab
                if self.modelui:
                    self.modelui.QStackedWidget_Module.setCurrentWidget(self.ui.centralwidget)
                # set ui
                self.ui.StlPathTxt_MC.setPlainText('{}'.format(InputFloder))
                self.ui.SaveNameTxt_MC_4.setPlainText('{}'.format(OutputFloder + '/lumenCut.stl'))
                # Touched function
                self.Excute()
                if Capping:
                    self.Capping()
                self.Save()
                self.InitCuttingMesh()


class MyCellPickerInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,
                 source='',
                 mapper='',
                 funcGeo=None,
                 UI=None):

        # set trigger event right mouse button press and key press
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        # self.AddObserver("MouseWheelForwardEvent", self.OnMouseWheelForward)
        self.AddObserver("KeyPressEvent", self.keypressEvent)

        self.ui = UI

        self.mapper1 = None
        self.points = []    # used to store the x,y,z coordinates of points used to determine the normal
        self.count = 1     # this variable is used to count number of visible points created by user

        self.planes = None
        self.point_no = 0

        # convert the input vtkstl object to polydata
        self.source = vtk.vtkPolyData()
        self.source.DeepCopy(source.GetOutput())

        # store the polydata of current mesh working on
        self.CurrentMesh = vtk.vtkPolyData()
        self.CurrentMesh.DeepCopy(source.GetOutput())

        # self.source = source
        self.mapper = mapper        # store the polydata of main mesh
        self.clipper = None         # used to clip mesh
        self.writer = None          # used to write the final mesh

        self.PreviousMesh = None    # used to store the mesh before cut action

        self.funcGeo = funcGeo
        self.dirFlag = 'Forward'    # used to store the cut direction
        self.methodFlag = 'Plane'   # used to store the method of cutting
        self.visFlag = False        # used to represent if the cutting box visible
        self.plane_info = None      # used to store the information of generated plane
        self.BoxActors = []         # used to store the six actors to generate a box
        self.PointActors = []       # used to store the actor object picked by user

    # def OnMouseWheelForward(self, obj, event):
    #     print("mouse wheel triggered")

    # generate visible cutting box, mesh within the box will be removed
    def GenerateBox(self):
        print(self.point_no)
        plane_val = self.plane_info[0]
        self.planes = self.plane_info[1]

        tmp_points = self.plane_info[2]
        tmp_normal = self.plane_info[3]

        print(tmp_points)
        print(tmp_normal)

        plane1 = vtk.vtkPlaneSource()
        # print(plane_val[0])
        # print(plane_val[1])

        plane1.SetNormal(plane_val[0])
        plane1.SetOrigin(plane_val[1])
        plane1.SetPoint1(plane_val[2])
        plane1.SetPoint2(plane_val[3])
        plane1.Update()

        plane2 = vtk.vtkPlaneSource()

        plane2.SetNormal(tmp_normal[1])
        plane2.SetOrigin(tmp_points[4])
        plane2.SetPoint1(tmp_points[7])
        plane2.SetPoint2(tmp_points[6])
        plane2.Update()

        plane3 = vtk.vtkPlaneSource()

        plane3.SetNormal(tmp_normal[2])
        plane3.SetOrigin(tmp_points[0])
        plane3.SetPoint1(tmp_points[3])
        plane3.SetPoint2(tmp_points[4])
        plane3.Update()

        plane4 = vtk.vtkPlaneSource()

        plane4.SetNormal(tmp_normal[3])
        plane4.SetOrigin(tmp_points[2])
        plane4.SetPoint1(tmp_points[1])
        plane4.SetPoint2(tmp_points[6])
        plane4.Update()

        plane5 = vtk.vtkPlaneSource()

        plane5.SetNormal(tmp_normal[4])
        plane5.SetOrigin(tmp_points[3])
        plane5.SetPoint1(tmp_points[1])
        plane5.SetPoint2(tmp_points[7])
        plane5.Update()

        plane6 = vtk.vtkPlaneSource()

        plane6.SetNormal(tmp_normal[5])
        plane6.SetOrigin(tmp_points[0])
        plane6.SetPoint1(tmp_points[2])
        plane6.SetPoint2(tmp_points[4])
        plane6.Update()
        # mapper2 to store visible plane

        # create mapper and actor for 6 planes, then add the actor to the default renderer
        names = locals()
        for i in range(2, 8):
            names['mapper' + str(i)] = vtk.vtkPolyDataMapper()
            names['mapper' + str(i)].SetInputData(names['plane' + str(i-1)].GetOutput())
            names['actor' + str(i)] = vtk.vtkActor()
            names['actor' + str(i)].SetMapper(names['mapper' + str(i)])
            names['actor' + str(i)].GetProperty().SetColor(0.5, 0.5, 0.5)
            names['actor' + str(i)].GetProperty().SetOpacity(0.25)
            self.GetDefaultRenderer().AddActor(names['actor' + str(i)])
            self.BoxActors.append(names['actor' + str(i)])

        print("success")

    # generate a single plane, mesh below the plane will be removed
    def GeneratePlane(self):
        print(self.point_no)
        plane_val = self.plane_info[0]
        self.planes = self.plane_info[1]

        plane1 = vtk.vtkPlaneSource()
        # print(plane_val[0])
        # print(plane_val[1])

        plane1.SetNormal(plane_val[0])
        plane1.SetOrigin(plane_val[1])
        plane1.SetPoint1(plane_val[2])
        plane1.SetPoint2(plane_val[3])
        plane1.Update()

        # mapper2 to store visible plane
        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputData(plane1.GetOutput())

        actor2 = vtk.vtkActor()
        actor2.SetMapper(mapper2)
        actor2.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor2.GetProperty().SetOpacity(0.25)

        self.GetDefaultRenderer().AddActor(actor2)

        self.BoxActors.append(actor2)
        print("success")

    # def BoxCut(self):

    def keypressEvent(self, obj, event):
        # this key used for keypress, GetKeyCode() used for key down
        key = self.GetInteractor().GetKeySym()

        # print("keypress Event triggered")

        # calculate the plane that fits the chosen points, moreover, using the directional point to generate 6 planes
        # to form a rectangle
        if self.GetInteractor().GetKeyCode() == 'g' or self.GetInteractor().GetKeyCode() == 'G':
            # Initialize normal calculation class GeoTransform

            # calculate the normal of given points
            # print(list(self.points))

            # check box status every time before generating visible plane
            self.CheckBoxCheck()
            self.plane_info = self.funcGeo.calculate(list(self.points[self.point_no]),
                                                     list(self.points[self.point_no + 1]),
                                                     list(self.points[self.point_no + 2]),
                                                     list(self.points[self.point_no + 3]),
                                                     self.dirFlag)

            self.point_no += 4

            if not self.visFlag:
                self.GeneratePlane()
            else:
                self.GenerateBox()

        # used to input points coordainate and generate cuntting plane
        # if self.GetInteractor().GetKeyCode() == 'a':
        #
        #     # Initialize normal calculation class GeoTransform
        #     # a = GeoTransform.GeoTransform()
        #
        #     self.plane_info = self.funcGeo.calculate([105.340, 116.396, 65.983], [103.420, 118.585, 66.618], [102.578, 116.109, 64.615],
        #                              [105.186, 117.898, 59.998], 'Forward')
        #
        #     # D1
        #     # self.plane_info = a.calculate([109.868, 109.544, 66.456], [112.934, 108.631, 66.710], [112.757, 109.222, 65.247], [111.021, 107.771, 65.202], 'Forward')
        #
        #     self.point_no += 4
        #     print(self.point_no)
        #     plane_val = self.plane_info[0]
        #     self.planes = self.plane_info[1]
        #
        #     plane1 = vtk.vtkPlaneSource()
        #     # print(plane_val[0])
        #     # print(plane_val[1])
        #
        #     plane1.SetNormal(plane_val[0])
        #     plane1.SetOrigin(plane_val[1])
        #     plane1.SetPoint1(plane_val[2])
        #     plane1.SetPoint2(plane_val[3])
        #     plane1.Update()
        #
        #     # mapper2 to store visible plane
        #     mapper2 = vtk.vtkPolyDataMapper()
        #     mapper2.SetInputData(plane1.GetOutput())
        #
        #     actor2 = vtk.vtkActor()
        #     actor2.SetMapper(mapper2)
        #     actor2.GetProperty().SetColor(0.5, 0.5, 0.5)
        #     actor2.GetProperty().SetOpacity(0.25)
        #
        #     self.GetDefaultRenderer().AddActor(actor2)
        #     print("success")

        # press ctrl + z to cancel last cut
        elif self.GetInteractor().GetControlKey():
            if key == 'z':
                self.CurrentMesh = vtk.vtkPolyData()
                self.CurrentMesh.DeepCopy(self.PreviousMesh)
                self.mapper.SetInputData(self.CurrentMesh)
                self.mapper.Update()
                self.GetInteractor().GetRenderWindow().Render()
                print('Time Travel')

        # used to return maximum 2 steps of cutting backward
        elif self.GetInteractor().GetKeyCode() == 'r':

            self.CurrentMesh = vtk.vtkPolyData()
            self.CurrentMesh.DeepCopy(self.PreviousMesh)

            self.mapper.SetInputData(self.CurrentMesh)
            # self.mapper = vtk.vtkPolyDataMapper()
            # self.mapper.SetInputData(self.test)
            self.mapper.Update()
            self.GetInteractor().GetRenderWindow().Render()

        # excute cutting function when pressing 'c'
        elif self.GetInteractor().GetKeyCode() == 'c':
            # check the check box status before cut excuted

            self.clipper = vtk.vtkClipPolyData()

            # set current mesh polydata as clipper input
            self.clipper.SetInputData(self.CurrentMesh)

            # store the mesh status
            self.StorePreviousStatus()

            clipfunction = vtk.vtkImplicitBoolean()
            clipfunction.SetOperationTypeToUnion()

            if self.methodFlag == 'Circum':
                # get planes generated by 3 chosen points and 1 directional point
                # use 6 planes to generate a rectangle to cut mesh
                for plane in self.planes:
                    clipfunction.AddFunction(plane)
            # if cutting flag = p, use single plane to cut mesh
            else:
                clipfunction.AddFunction(self.planes[0])

            # for boxwidget generated planes set clipping function
            self.clipper.SetClipFunction(clipfunction)
            self.clipper.GenerateClippedOutputOff()
            self.clipper.GenerateClipScalarsOff()
            self.clipper.InsideOutOn()
            self.clipper.Update()

            # refresh the source data as clipped data
            self.source = vtk.vtkPolyData()
            self.source.DeepCopy(self.clipper.GetOutput())

            self.CurrentMesh = vtk.vtkPolyData()
            self.CurrentMesh.DeepCopy(self.clipper.GetOutput())

            self.mapper.SetInputData(self.CurrentMesh)
            self.mapper.Update()

            # used to update pipeline
            self.GetInteractor().GetRenderWindow().Render()
            self.count = 0
            print("cut done")

            # Remove visible points and cutting plane or box after cut is done
            for i in self.BoxActors:
                self.GetDefaultRenderer().RemoveActor(i)

            for j in self.PointActors:
                self.GetDefaultRenderer().RemoveActor(j)
            self.PointActors = []

        # used to delete the latest point actor
        elif self.GetInteractor().GetKeyCode() == 'd':
            self.GetDefaultRenderer().RemoveActor(self.PointActors[len(self.PointActors)-1])
            # remove point actor from the list that store the actors
            self.PointActors.pop(len(self.PointActors)-1)
            # remove the position of latest point
            self.points.pop(len(self.points)-1)

            self.count -= 1

        # output points coordinate
        elif self.GetInteractor().GetKeyCode() == 'w':
            with open(r"E:\\testPoints.txt", 'wt') as f:
                f.write(str(self.points))
            print("points coordinates successfully saved")

        # convert the string read from specified file to list
        elif self.GetInteractor().GetKeyCode() == 'o':
            with open(r"E:\\testPoints.txt", "r") as f:
                str = f.read()
                self.points = eval(str)
                print("Read Data Done")

        else:
            pass

    # define the right button press event to create a visible red points
    def RightButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        print("picking pixel:", clickPos)

        picker = self.GetInteractor().GetPicker()

        # picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

        if picker.GetCellId() != -1:
            print("pick position is", picker.GetPickPosition())
            print("cell id is", picker.GetCellId())
            print("Point id is", picker.GetPointId())

            point_postion = self.CurrentMesh.GetPoint(picker.GetPointId())

            sSource = vtk.vtkSphereSource()
            sSource.SetCenter(point_postion)
            sSource.SetRadius(0.25)

            self.mapper1 = vtk.vtkPolyDataMapper()
            self.mapper1.SetInputConnection(sSource.GetOutputPort())

            self.mapper1.Update()

            actor1 = vtk.vtkActor()
            actor1.SetMapper(self.mapper1)
            if self.count % 4 == 0:
                actor1.GetProperty().SetColor(0, 0, 1)
            else:
                actor1.GetProperty().SetColor(1, 0, 0)

            # append the point position to self.points
            self.points.append(picker.GetPickPosition())
            print(self.points)
            self.count += 1
            self.GetDefaultRenderer().AddActor(actor1)

            self.PointActors.append(actor1)

        self.OnRightButtonDown()

    def GetPoints(self):
        return self.points

    # return data to be saved
    def GetOutputData(self):
        return self.clipper.GetOutput()

    def SetDirection(self, dir):
        self.dirFlag = dir

    def SetMethod(self, method):
        self.methodFlag = method

    def SetVisibilty(self, vis):
        self.visFlag = vis

    def SetBoxSize(self, ExtRadius, height):
        self.funcGeo.setSize(ExtRadius, height)
        # print('box size now is{}x{}x{} '.format(length, width, height))

    def GetCurrentMesh(self):
        return self.CurrentMesh

    # check the check box and radio button status everytime before the cut action
    def CheckBoxCheck(self):
        if not self.ui.CuttingBoxVisibilityCheck.isChecked():
            self.visFlag = False
        else:
            self.visFlag = True

        if self.ui.CuttingMethod_YL.checkedButton().text() == 'Plane Method':
            self.methodFlag = 'Plane'
        # elif self.ui.CuttingMethod_YL.checkedButton().text() == 'Box Method':
        #     self.methodFlag = 'Box'
        else:
            self.methodFlag = 'Circum'

        if self.ui.CuttingDirectionGrp_YL.checkedButton().text() == 'Forward':
            self.dirFlag = 'Forward'
        elif self.ui.CuttingDirectionGrp_YL.checkedButton().text() == 'Backward':
            self.dirFlag = 'Backward'
        else:
            self.dirFlag = 'Forward'

    # store the data of mesh from previous step
    def StorePreviousStatus(self):
        self.PreviousMesh = vtk.vtkPolyData()
        self.PreviousMesh.DeepCopy(self.CurrentMesh)

        print('previous status storage done')

if __name__ == '__main__':
    app = QApplication([])
    ui = QUiLoader().load(r"E:\GUI\Hedys\GUI_V0\ui\MeshCut.ui")
    stats = Interaction(UI=ui)
    stats.ui.show()
    app.exec_()